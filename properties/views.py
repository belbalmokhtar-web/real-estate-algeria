# properties/views.py
# -*- coding: utf-8 -*-

import csv
import logging
from typing import List, Optional, Union

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.images import get_image_dimensions
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Q, Avg, Count, Prefetch, Sum, Min, Max
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST, require_http_methods, require_GET
from django.views.decorators.vary import vary_on_headers

# نماذج وأشكال التطبيق
from .models import (
    Property, PropertyImage, Favorite, Review,
    Category, Payment, PromoteurImmobilier, ProjetImmobilier
)
from .models_valuation import (
    Wilaya, Commune, Zone, NatureImmeuble, Caracteristique, ValuationRange
)
from .forms import PropertyForm, ReviewForm, ContactForm, ValuationSearchForm

from accounts.models import User, AgentProfile

# إعدادات التسجيل
logger = logging.getLogger(__name__)


# ============================================================================
# 2. دوال مساعدة (Helper functions)
# ============================================================================

def validate_image_file(image) -> tuple[bool, str]:
    """التحقق من صحة الصورة"""
    max_size = 5 * 1024 * 1024
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

    if image.size > max_size:
        return False, "حجم الصورة يتجاوز 5 ميجابايت"
    if image.content_type not in allowed_types:
        return False, "نوع الملف غير مدعوم"
    try:
        width, height = get_image_dimensions(image)
        if width < 200 or height < 200:
            return False, "الصورة صغيرة جداً. الحد الأدنى 200x200 بكسل"
    except Exception:
        pass
    return True, ""


def get_filtered_properties(request: HttpRequest):
    """تطبيق جميع الفلاتر والترتيب على استعلام العقارات النشطة"""
    properties = Property.objects.filter(is_active=True).select_related(
        'owner', 'agent', 'wilaya', 'commune'
    ).prefetch_related(
        Prefetch('images', queryset=PropertyImage.objects.filter(is_main=True))
    )

    q = request.GET.get('q', '').strip()
    if q:
        properties = properties.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(address__icontains=q) |
            Q(wilaya__name_ar__icontains=q) |
            Q(commune__name_ar__icontains=q)
        )

    property_type = request.GET.get('property_type')
    if property_type and property_type in dict(Property.PROPERTY_TYPE_CHOICES):
        properties = properties.filter(property_type=property_type)

    listing_type = request.GET.get('listing_type')
    if listing_type and listing_type in dict(Property.LISTING_TYPE_CHOICES):
        properties = properties.filter(listing_type=listing_type)

    try:
        min_price = request.GET.get('min_price')
        if min_price and min_price.isdigit():
            properties = properties.filter(price__gte=int(min_price))
        max_price = request.GET.get('max_price')
        if max_price and max_price.isdigit():
            properties = properties.filter(price__lte=int(max_price))
    except ValueError:
        pass

    price_range = request.GET.get('price_range')
    if price_range:
        try:
            min_price, max_price = price_range.split('-')
            properties = properties.filter(price__gte=int(min_price))
            if max_price != '999999999':
                properties = properties.filter(price__lte=int(max_price))
        except (ValueError, TypeError):
            pass

    try:
        min_area = request.GET.get('min_area')
        if min_area and min_area.isdigit():
            properties = properties.filter(area_sqm__gte=int(min_area))
        max_area = request.GET.get('max_area')
        if max_area and max_area.isdigit():
            properties = properties.filter(area_sqm__lte=int(max_area))
    except ValueError:
        pass

    wilaya_id = request.GET.get('wilaya')
    if wilaya_id and wilaya_id.isdigit():
        properties = properties.filter(wilaya_id=wilaya_id)

    commune_id = request.GET.get('commune')
    if commune_id and commune_id.isdigit():
        properties = properties.filter(commune_id=commune_id)

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        properties = properties.order_by('price')
    elif sort == 'price_desc':
        properties = properties.order_by('-price')
    elif sort == 'date_asc':
        properties = properties.order_by('created_at')
    else:
        properties = properties.order_by('-created_at')

    return properties


def handle_property_images(property_obj: Property, files: List, delete_ids: Optional[List[str]] = None) -> None:
    """معالجة الصور المرفوعة"""
    if delete_ids:
        PropertyImage.objects.filter(id__in=delete_ids, property=property_obj).delete()

    existing_count = property_obj.images.count()
    for idx, img in enumerate(files):
        valid, error = validate_image_file(img)
        if not valid:
            messages.warning(property_obj.owner, f"الصورة {img.name} لم تُرفع: {error}")
            continue
        is_main = (idx == 0 and existing_count == 0 and not property_obj.image)
        PropertyImage.objects.create(
            property=property_obj,
            image=img,
            is_main=is_main,
            order=existing_count + idx
        )


# ============================================================================
# 3. الصفحات الرئيسية والعمومية
# ============================================================================

@cache_page(60 * 5)
@vary_on_headers('Cookie')
def home(request: HttpRequest) -> HttpResponse:
    """الصفحة الرئيسية للموقع"""
    wilayas = Wilaya.objects.all().order_by('name_ar')
    total_properties = Property.objects.filter(is_active=True).count()
    avg_price = Property.objects.filter(is_active=True).aggregate(Avg('price'))['price__avg'] or 0

    properties_with_area = Property.objects.filter(is_active=True, area_sqm__gt=0)
    if properties_with_area.exists():
        total_price_per_sqm = sum(p.price / p.area_sqm for p in properties_with_area)
        avg_price_per_sqm = total_price_per_sqm / properties_with_area.count()
    else:
        avg_price_per_sqm = 0

    total_cities = Property.objects.filter(is_active=True).values('wilaya').distinct().count() or 58

    featured_properties = Property.objects.filter(
        is_active=True, is_featured=True
    ).select_related('owner', 'wilaya')[:6]

    latest_properties = Property.objects.filter(
        is_active=True
    ).select_related('owner', 'wilaya').order_by('-created_at')[:8]

    wilayas_stats = []
    for wilaya in wilayas[:10]:
        count = Property.objects.filter(is_active=True, wilaya=wilaya).count()
        if count > 0:
            wilayas_stats.append({
                'id': wilaya.id,
                'name': wilaya.name_ar,
                'code': wilaya.code,
                'count': count
            })

    top_agents = AgentProfile.objects.filter(user__is_active=True).annotate(
        property_count=Count('properties')
    ).order_by('-property_count')[:4]

    context = {
        'total_properties': total_properties,
        'avg_price': avg_price,
        'avg_price_per_sqm': avg_price_per_sqm,
        'total_cities': total_cities,
        'featured_properties': featured_properties,
        'latest_properties': latest_properties,
        'wilayas': wilayas,
        'wilayas_stats': wilayas_stats,
        'property_types': Property.PROPERTY_TYPE_CHOICES,
        'listing_types': Property.LISTING_TYPE_CHOICES,
        'top_agents': top_agents,
    }
    return render(request, 'home.html', context)


def property_list(request: HttpRequest) -> HttpResponse:
    """عرض قائمة العقارات مع الفلاتر"""
    properties_qs = get_filtered_properties(request)
    paginator = Paginator(properties_qs, 12)
    page = request.GET.get('page', 1)
    try:
        properties_page = paginator.page(page)
    except PageNotAnInteger:
        properties_page = paginator.page(1)
    except EmptyPage:
        properties_page = paginator.page(paginator.num_pages)

    wilayas = Wilaya.objects.all().order_by('name_ar')
    selected_wilaya_id = request.GET.get('wilaya')
    communes = []
    if selected_wilaya_id and selected_wilaya_id.isdigit():
        communes = Commune.objects.filter(wilaya_id=selected_wilaya_id).order_by('name_ar')

    context = {
        'properties': properties_page,
        'property_types': Property.PROPERTY_TYPE_CHOICES,
        'listing_types': Property.LISTING_TYPE_CHOICES,
        'current_filters': request.GET,
        'wilayas': wilayas,
        'communes': communes,
    }
    return render(request, 'properties/list.html', context)


def property_detail(request: HttpRequest, id: int) -> HttpResponse:
    """صفحة تفاصيل العقار"""
    property_obj = get_object_or_404(
        Property.objects.select_related('owner', 'agent', 'wilaya', 'commune').prefetch_related('images',
                                                                                                'reviews__user'),
        id=id, is_active=True
    )
    property_obj.increase_views()

    reviews = property_obj.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    if request.method == 'POST' and 'submit_review' in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, 'يجب تسجيل الدخول لإضافة تقييم.')
            return redirect('accounts:login')
        if user_review:
            messages.error(request, 'لقد قمت بتقييم هذا العقار مسبقاً.')
        else:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.property = property_obj
                review.user = request.user
                review.save()
                messages.success(request, 'تم إضافة تقييمك بنجاح!')
                return redirect('properties:property_detail', id=property_obj.id)
            else:
                messages.error(request, 'يرجى تصحيح الأخطاء في النموذج.')

    similar_properties = Property.objects.filter(
        is_active=True, property_type=property_obj.property_type
    ).exclude(id=property_obj.id).select_related('owner', 'wilaya')[:4]

    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = Favorite.objects.filter(user=request.user).values_list('property_id', flat=True)

    context = {
        'property': property_obj,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_review': user_review,
        'review_form': ReviewForm(),
        'similar_properties': similar_properties,
        'user_favorites': user_favorites,
    }
    return render(request, 'properties/detail.html', context)


# ============================================================================
# 4. العمليات الخاصة بالمستخدم
# ============================================================================

@login_required
@require_http_methods(['GET', 'POST'])
def property_create(request: HttpRequest) -> HttpResponse:
    """إضافة عقار جديد"""
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                property_obj = form.save(commit=False)
                property_obj.owner = request.user
                property_obj.save()
                images = request.FILES.getlist('images')
                handle_property_images(property_obj, images)
            messages.success(request, 'تم إضافة العقار بنجاح.')
            return redirect('properties:property_detail', id=property_obj.id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء في النموذج.')
    else:
        form = PropertyForm()

    wilayas = Wilaya.objects.all().order_by('name_ar')
    return render(request, 'properties/form.html', {'form': form, 'is_edit': False, 'wilayas': wilayas})


@login_required
@require_http_methods(['GET', 'POST'])
def property_edit(request: HttpRequest, id: int) -> HttpResponse:
    """تعديل عقار قائم"""
    property_obj = get_object_or_404(Property, id=id)
    if property_obj.owner != request.user and not request.user.is_staff:
        raise PermissionDenied("ليس لديك صلاحية تعديل هذا العقار.")

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            with transaction.atomic():
                property_obj = form.save()
                delete_ids = request.POST.getlist('delete_images')
                new_images = request.FILES.getlist('images')
                handle_property_images(property_obj, new_images, delete_ids)
            messages.success(request, 'تم تحديث العقار بنجاح.')
            return redirect('properties:property_detail', id=property_obj.id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء في النموذج.')
    else:
        form = PropertyForm(instance=property_obj)

    wilayas = Wilaya.objects.all().order_by('name_ar')
    return render(request, 'properties/form.html',
                  {'form': form, 'property': property_obj, 'is_edit': True, 'wilayas': wilayas})


@login_required
@require_POST
def property_delete(request: HttpRequest, id: int) -> HttpResponse:
    """حذف عقار"""
    property_obj = get_object_or_404(Property, id=id, owner=request.user)
    property_obj.delete()
    messages.success(request, 'تم حذف العقار بنجاح.')
    return redirect('properties:property_list')


@login_required
@require_POST
def toggle_favorite(request: HttpRequest, property_id: int) -> Union[JsonResponse, HttpResponse]:
    """إضافة/إزالة عقار من المفضلة"""
    property_obj = get_object_or_404(Property, id=property_id, is_active=True)
    favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
    if not created:
        favorite.delete()
        is_favorited = False
    else:
        is_favorited = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'is_favorited': is_favorited, 'property_id': property_id})
    return redirect('properties:property_detail', id=property_id)


# ============================================================================
# 5. نظام التقييم العقاري (Valuation System)
# ============================================================================

def valuation_view(request: HttpRequest) -> HttpResponse:
    """الصفحة الرئيسية للتقييم العقاري"""
    wilayas = Wilaya.objects.all().order_by("code")
    zones = Zone.objects.all().order_by("key")
    natures = NatureImmeuble.objects.all().order_by("key")

    result = None
    zone_range = None
    communes = []
    characteristics = []

    if request.method == "POST" and "advanced_submit" in request.POST:
        wilaya_id = request.POST.get('wilaya')
        commune_id = request.POST.get('commune')
        zone_id = request.POST.get('zone')
        nature_id = request.POST.get('nature')
        characteristic_id = request.POST.get('characteristic')

        if all([wilaya_id, commune_id, zone_id, nature_id, characteristic_id]):
            try:
                result = ValuationRange.objects.select_related(
                    "wilaya", "commune", "zone", "nature", "caracteristique"
                ).get(
                    wilaya_id=wilaya_id,
                    commune_id=commune_id,
                    zone_id=zone_id,
                    nature_id=nature_id,
                    caracteristique_id=characteristic_id,
                )
            except ValuationRange.DoesNotExist:
                messages.warning(request, "لا توجد بيانات تقييم للمعايير المحددة.")

        if zone_id:
            try:
                zone_obj = Zone.objects.get(id=zone_id)
                zone_qs = ValuationRange.objects.filter(zone_id=zone_id)
                if wilaya_id:
                    zone_qs = zone_qs.filter(wilaya_id=wilaya_id)
                if commune_id:
                    zone_qs = zone_qs.filter(commune_id=commune_id)
                if nature_id:
                    zone_qs = zone_qs.filter(nature_id=nature_id)

                if zone_qs.exists():
                    agg = zone_qs.aggregate(
                        min_val=Min("min_price_per_sqm"),
                        max_val=Max("max_price_per_sqm"),
                    )
                    zone_range = {
                        "min": agg["min_val"],
                        "max": agg["max_val"],
                        "zone_name": zone_obj.name_fr,
                    }
            except Zone.DoesNotExist:
                pass

        if wilaya_id and wilaya_id.isdigit():
            communes = Commune.objects.filter(wilaya_id=wilaya_id).order_by('name_ar')
        if nature_id and nature_id.isdigit():
            characteristics = Caracteristique.objects.filter(nature_id=nature_id).order_by('order')

    context = {
        "wilayas": wilayas,
        "zones": zones,
        "natures": natures,
        "communes": communes,
        "characteristics": characteristics,
        "result": result,
        "zone_range": zone_range,
    }
    return render(request, "properties/valuation.html", context)


# ============================================================================
# 6. AJAX endpoints للتقييم العقاري
# ============================================================================

@require_GET
def get_communes(request: HttpRequest) -> JsonResponse:
    """إرجاع بلديات الولاية المحددة (AJAX)"""
    wilaya_id = request.GET.get("wilaya_id")
    if not wilaya_id or not wilaya_id.isdigit():
        return JsonResponse([], safe=False)
    communes = Commune.objects.filter(wilaya_id=wilaya_id).order_by("name_ar")
    data = [{"id": c.pk, "name_ar": c.name_ar, "name_fr": c.name_fr} for c in communes]
    return JsonResponse(data, safe=False)


@require_GET
def get_characteristics(request: HttpRequest) -> JsonResponse:
    """إرجاع خصائص طبيعة العقار المحددة (AJAX)"""
    nature_id = request.GET.get("nature_id")
    if not nature_id or not nature_id.isdigit():
        return JsonResponse([], safe=False)
    chars = Caracteristique.objects.filter(nature_id=nature_id).order_by("order")
    data = [{"id": c.pk, "name_ar": c.name_ar, "name_fr": c.name_fr} for c in chars]
    return JsonResponse(data, safe=False)


@require_GET
def get_zone_range(request: HttpRequest) -> JsonResponse:
    """إرجاع نطاق سعر منطقة معينة (AJAX)"""
    zone_id = request.GET.get("zone_id")
    if not zone_id or not zone_id.isdigit():
        return JsonResponse({}, safe=False)
    qs = ValuationRange.objects.filter(zone_id=zone_id)
    agg = qs.aggregate(mn=Min("min_price_per_sqm"), mx=Max("max_price_per_sqm"))
    try:
        zone = Zone.objects.get(pk=zone_id)
        name = zone.name_fr
    except Zone.DoesNotExist:
        name = ""
    return JsonResponse({"min": str(agg["mn"] or ""), "max": str(agg["mx"] or ""), "name": name})


@require_GET
def get_valuation_result(request: HttpRequest) -> JsonResponse:
    """API للحصول على نتيجة التقييم (AJAX)"""
    wilaya_id = request.GET.get("wilaya_id")
    commune_id = request.GET.get("commune_id")
    zone_id = request.GET.get("zone_id")
    nature_id = request.GET.get("nature_id")
    caracteristique_id = request.GET.get("caracteristique_id")

    if not all([wilaya_id, commune_id, zone_id, nature_id, caracteristique_id]):
        return JsonResponse({"error": "جميع الحقول مطلوبة"}, status=400)

    try:
        result = ValuationRange.objects.select_related(
            "wilaya", "commune", "zone", "nature", "caracteristique"
        ).get(
            wilaya_id=wilaya_id,
            commune_id=commune_id,
            zone_id=zone_id,
            nature_id=nature_id,
            caracteristique_id=caracteristique_id,
        )
        return JsonResponse({
            "success": True,
            "min_price": float(result.min_price_per_sqm),
            "max_price": float(result.max_price_per_sqm),
            "wilaya": result.wilaya.name_ar,
            "commune": result.commune.name_ar,
            "zone": result.zone.name_ar,
            "nature": result.nature.name_ar,
            "caracteristique": result.caracteristique.name_ar,
        })
    except ValuationRange.DoesNotExist:
        return JsonResponse({"success": False, "error": "لا توجد بيانات"}, status=404)


# properties/views.py - الجزء المعدل

# ============================================================================
# 7. دوال المطورين العقاريين (Promoteurs) - المتقدمة
# ============================================================================

def promoteur_list(request: HttpRequest) -> HttpResponse:
    """عرض قائمة المطورين العقاريين مع بحث وفلتر شامل"""
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Q

    # قاعدة البيانات الأساسية
    promoteurs = PromoteurImmobilier.objects.filter(is_active=True).select_related('wilaya')

    # ========== معالجة البحث ==========
    search_query = request.GET.get('q', '').strip()
    if search_query:
        promoteurs = promoteurs.filter(
            Q(nom_entreprise__icontains=search_query) |
            Q(nom_gerant__icontains=search_query) |
            Q(numero_affiliation__icontains=search_query) |
            Q(numero_agrement__icontains=search_query)
        )

    # ========== معالجة فلتر الولاية ==========
    selected_wilaya = request.GET.get('wilaya')
    if selected_wilaya and selected_wilaya.isdigit():
        promoteurs = promoteurs.filter(wilaya_id=selected_wilaya)

    # ========== معالجة الترتيب ==========
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'name':
        promoteurs = promoteurs.order_by('nom_entreprise')
    elif sort_by == 'name_desc':
        promoteurs = promoteurs.order_by('-nom_entreprise')
    elif sort_by == 'wilaya':
        promoteurs = promoteurs.order_by('wilaya__name_ar', 'nom_entreprise')
    elif sort_by == 'date':
        promoteurs = promoteurs.order_by('-created_at')
    else:
        promoteurs = promoteurs.order_by('nom_entreprise')

    # ========== إحصائيات الولايات ==========
    all_wilayas = []
    for wilaya in Wilaya.objects.all().order_by('name_ar'):
        count = PromoteurImmobilier.objects.filter(wilaya=wilaya, is_active=True).count()
        if count > 0:
            all_wilayas.append({
                'id': wilaya.id,
                'name': wilaya.name_ar,
                'count': count
            })

    # ========== معالجة عرض البطاقات/القائمة ==========
    view_mode = request.GET.get('view', 'cards')

    # ========== ترقيم الصفحات ==========
    paginator = Paginator(promoteurs, 12)
    page = request.GET.get('page', 1)
    try:
        promoteurs_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        promoteurs_page = paginator.page(1)

    context = {
        'promoteurs': promoteurs_page,
        'all_wilayas': all_wilayas,
        'total_promoteurs': PromoteurImmobilier.objects.filter(is_active=True).count(),
        'results_count': promoteurs.count(),
        'selected_wilaya': selected_wilaya,
        'search_query': search_query,
        'sort_by': sort_by,
        'view_mode': view_mode,
        'is_paginated': promoteurs_page.has_other_pages(),
        'page_obj': promoteurs_page,
    }
    return render(request, 'properties/promoteur_list.html', context)


def promoteur_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """عرض تفاصيل مطور عقاري مع مشاريعه"""
    promoteur = get_object_or_404(PromoteurImmobilier, pk=pk, is_active=True)
    projets = promoteur.projets.filter(is_active=True)
    total_logements = sum(p.total_logements for p in projets)

    context = {
        'promoteur': promoteur,
        'projets': projets,
        'total_projets': projets.count(),
        'total_logements': total_logements,
    }
    return render(request, 'properties/promoteur_detail.html', context)


def contact_promoteur(request: HttpRequest, pk: int) -> HttpResponse:
    """معالجة نموذج الاتصال بالمطور"""
    promoteur = get_object_or_404(PromoteurImmobilier, pk=pk)
    if request.method == 'POST':
        messages.success(request, f'تم إرسال رسالتك إلى {promoteur.nom_entreprise} بنجاح!')
    return redirect('properties:promoteur_detail', pk=pk)


def projet_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """عرض تفاصيل مشروع عقاري"""
    projet = get_object_or_404(ProjetImmobilier, pk=pk, is_active=True)
    type_counts = {
        'F1': projet.f1_count,
        'F2': projet.f2_count,
        'F3': projet.f3_count,
        'F4': projet.f4_count,
        'F5': projet.f5_count,
        'Duplex': projet.duplex_count,
        'Villa': projet.villa_count,
        'Cave': projet.cave_count,
        'Garage': projet.garage_count,
    }
    available_types = {k: v for k, v in type_counts.items() if v > 0}
    context = {
        'projet': projet,
        'type_counts': available_types,
        'total_logements': projet.total_logements,
        'promoteur': projet.promoteur,
    }
    return render(request, 'properties/projet_detail.html', context)


# ============================================================================
# 8. API المشاريع (Projets API)
# ============================================================================

@require_GET
def api_projet_detail(request: HttpRequest, pk: int) -> JsonResponse:
    """API لجلب تفاصيل مشروع (للمودال)"""
    try:
        projet = ProjetImmobilier.objects.select_related('promoteur').get(pk=pk, is_active=True)

        return JsonResponse({
            'success': True,
            'id': projet.id,
            'nom_projet': projet.nom_projet,
            'localisation': projet.localisation,
            'date_garantie': projet.date_garantie.strftime('%d/%m/%Y') if projet.date_garantie else None,
            'total_logements': projet.total_logements,
            'f2_count': projet.f2_count or 0,
            'f3_count': projet.f3_count or 0,
            'f4_count': projet.f4_count or 0,
            'f5_count': projet.f5_count or 0,
            'description': projet.description or '',
            'promoteur_url': reverse('properties:promoteur_detail', args=[projet.promoteur.id]),
            'promoteur_nom': projet.promoteur.nom_entreprise,
        })
    except ProjetImmobilier.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'المشروع غير موجود'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ... باقي الدوال ...

# ============================================================================
# دوال الاختبار (للتصحيح فقط - يمكن حذفها في الإنتاج)
# ============================================================================

def promoteur_list_simple(request: HttpRequest) -> HttpResponse:
    """عرض قائمة المطورين (نسخة مبسطة للاختبار)"""
    from django.http import HttpResponse
    promoteurs = PromoteurImmobilier.objects.filter(is_active=True).select_related('wilaya')

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>قائمة المطورين العقاريين</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; direction: rtl; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
            th { background-color: #4CAF50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>قائمة المطورين العقاريين المعتمدين</h1>
        <p>إجمالي المطورين: <strong>""" + str(promoteurs.count()) + """</strong></p>
        <table>
            <tr>
                <th>رقم الانتساب</th>
                <th>اسم الشركة</th>
                <th>المسير</th>
                <th>الولاية</th>
                <th>الهاتف</th>
            </tr>
    """

    for p in promoteurs[:50]:
        html += f"""
            <tr>
                <td>{p.numero_affiliation}</td>
                <td>{p.nom_entreprise}</td>
                <td>{p.nom_gerant or '-'}</td>
                <td>{p.wilaya.name_ar if p.wilaya else '-'}</td>
                <td>{p.telephone or '-'}</td>
            </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    return HttpResponse(html)


def promoteur_list_test(request: HttpRequest) -> HttpResponse:
    """نسخة اختبار مبسطة"""
    promoteurs = PromoteurImmobilier.objects.filter(is_active=True).select_related('wilaya')

    all_wilayas = []
    for wilaya in Wilaya.objects.all().order_by('name_ar'):
        count = PromoteurImmobilier.objects.filter(wilaya=wilaya, is_active=True).count()
        if count > 0:
            all_wilayas.append({'id': wilaya.id, 'name': wilaya.name_ar, 'count': count})

    context = {
        'promoteurs': promoteurs,
        'all_wilayas': all_wilayas,
        'total_promoteurs': promoteurs.count(),
    }
    return render(request, 'properties/promoteur_list_test.html', context)

# ============================================================================
# دوال إضافية للـ APIs
# ============================================================================

@require_GET
def load_communes(request: HttpRequest) -> JsonResponse:
    """تحميل البلديات بناءً على الولاية المختارة (AJAX)"""
    wilaya_id = request.GET.get('wilaya_id')
    if wilaya_id and wilaya_id.isdigit():
        communes = Commune.objects.filter(wilaya_id=wilaya_id).order_by('name_ar')
        communes_list = [{'id': c.id, 'name': c.name_ar} for c in communes]
        return JsonResponse({'communes': communes_list})
    return JsonResponse({'communes': []})


@require_GET
def get_communes_by_name(request: HttpRequest) -> JsonResponse:
    """جلب البلديات حسب اسم الولاية"""
    wilaya_name = request.GET.get('wilaya_name')
    if not wilaya_name:
        return JsonResponse([], safe=False)
    communes = Commune.objects.filter(wilaya__name_ar=wilaya_name).values('id', 'name_ar')
    return JsonResponse(list(communes), safe=False)

def property_map(request: HttpRequest) -> HttpResponse:
    """عرض خريطة العقارات"""
    properties = Property.objects.filter(is_active=True, latitude__isnull=False, longitude__isnull=False)
    properties_data = []
    for prop in properties:
        if prop.latitude and prop.longitude:
            properties_data.append({
                'id': prop.id,
                'title': prop.title,
                'price': float(prop.price),
                'wilaya': prop.wilaya.name_ar if prop.wilaya else "",
                'lat': float(prop.latitude),
                'lng': float(prop.longitude),
            })
    context = {'properties': properties, 'properties_json': properties_data}
    return render(request, 'properties/map.html', context)

@require_GET
def export_properties_csv(request: HttpRequest) -> HttpResponse:
    """تصدير قائمة العقارات المفعلة إلى ملف CSV"""
    import csv
    properties = Property.objects.filter(is_active=True).values(
        'title', 'price', 'area_sqm', 'address', 'wilaya__name_ar', 'commune__name_ar',
        'property_type', 'listing_type', 'created_at'
    )
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="properties.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ['العنوان', 'السعر', 'المساحة (م²)', 'العنوان التفصيلي', 'الولاية', 'البلدية', 'النوع', 'نوع الإعلان',
         'تاريخ الإضافة'])
    for prop in properties:
        writer.writerow([
            prop['title'], prop['price'], prop['area_sqm'], prop['address'],
            prop['wilaya__name_ar'], prop['commune__name_ar'], prop['property_type'],
            prop['listing_type'], prop['created_at']
        ])
    return response

@require_GET
def property_stats_api(request: HttpRequest) -> JsonResponse:
    """API لإحصائيات العقارات"""
    total = Property.objects.filter(is_active=True).count()
    by_type = Property.objects.filter(is_active=True).values('property_type').annotate(count=Count('id'))
    by_listing = Property.objects.filter(is_active=True).values('listing_type').annotate(count=Count('id'))
    by_wilaya = Property.objects.filter(is_active=True).values('wilaya__name_ar').annotate(count=Count('id')).order_by('-count')[:10]
    return JsonResponse({
        'total': total,
        'by_type': list(by_type),
        'by_listing': list(by_listing),
        'by_wilaya': list(by_wilaya)
    })


@require_GET
def advanced_search(request: HttpRequest) -> JsonResponse:
    """بحث متقدم يعيد نتائج على شكل JSON"""
    properties = get_filtered_properties(request)
    data = list(properties.values('id', 'title', 'price', 'area_sqm', 'wilaya__name_ar', 'commune__name_ar', 'image', 'slug'))
    return JsonResponse(data, safe=False)


@require_GET
def search_suggestions(request: HttpRequest) -> JsonResponse:
    """اقتراحات للبحث التلقائي"""
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse([], safe=False)
    properties = Property.objects.filter(is_active=True, title__icontains=q).values('id', 'title', 'wilaya__name_ar')[:10]
    wilayas = Wilaya.objects.filter(name_ar__icontains=q).values('id', 'name_ar')[:5]
    suggestions = []
    for p in properties:
        suggestions.append({'id': p['id'], 'label': f"🏠 {p['title']} - {p['wilaya__name_ar']}", 'value': p['title'], 'type': 'property'})
    for w in wilayas:
        suggestions.append({'id': w['id'], 'label': f"📍 {w['name_ar']} (ولاية)", 'value': w['name_ar'], 'type': 'wilaya'})
    return JsonResponse(suggestions, safe=False)


@require_GET
def export_properties_csv(request: HttpRequest) -> HttpResponse:
    """تصدير قائمة العقارات المفعلة إلى ملف CSV"""
    import csv
    properties = Property.objects.filter(is_active=True).values(
        'title', 'price', 'area_sqm', 'address', 'wilaya__name_ar', 'commune__name_ar',
        'property_type', 'listing_type', 'created_at'
    )
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="properties.csv"'
    writer = csv.writer(response)
    writer.writerow(['العنوان', 'السعر', 'المساحة (م²)', 'العنوان التفصيلي', 'الولاية', 'البلدية', 'النوع', 'نوع الإعلان', 'تاريخ الإضافة'])
    for prop in properties:
        writer.writerow([
            prop['title'], prop['price'], prop['area_sqm'], prop['address'],
            prop['wilaya__name_ar'], prop['commune__name_ar'], prop['property_type'],
            prop['listing_type'], prop['created_at']
        ])
    return response

# properties/views.py - أضف هذه الدالة في نهاية الملف

def property_map(request: HttpRequest) -> HttpResponse:
    """عرض خريطة العقارات"""
    properties = Property.objects.filter(is_active=True, latitude__isnull=False, longitude__isnull=False)
    properties_data = []
    for prop in properties:
        if prop.latitude and prop.longitude:
            properties_data.append({
                'id': prop.id,
                'title': prop.title,
                'price': float(prop.price),
                'wilaya': prop.wilaya.name_ar if prop.wilaya else "",
                'lat': float(prop.latitude),
                'lng': float(prop.longitude),
            })
    context = {
        'properties': properties,
        'properties_json': properties_data,
    }
    return render(request, 'properties/map.html', context)