# accounts/views.py
# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Sum, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db import transaction
from django.urls import reverse

from .models import User, AgentProfile, DeveloperProfile, Message
from .forms import UserRegisterForm, UserProfileForm
from properties.models import Property, Favorite
from rewards.models import PromoterProfile, AdvertiserProfile, AffiliateLink, Click


# ============================================================================
# دوال المصادقة (Authentication)
# ============================================================================

def register(request):
    """تسجيل مستخدم جديد (دور عادي)"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'مرحباً {user.username}، تم تسجيلك بنجاح.')
            return redirect('home')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """تسجيل الدخول"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            messages.success(request, f'مرحباً {user.username}، تم تسجيل الدخول بنجاح.')
            return redirect(next_url)
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
    return render(request, 'accounts/login.html')


def user_logout(request):
    """تسجيل الخروج"""
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('home')


# ============================================================================
# الملف الشخصي (Profile)
# ============================================================================

@login_required
def profile_view(request):
    """عرض لوحة التحكم الشخصية (dashboard)"""
    user = request.user
    properties = Property.objects.filter(owner=user, is_active=True).order_by('-created_at')
    favorites = Favorite.objects.filter(user=user).select_related('property')[:6]
    total_properties = properties.count()
    total_views = properties.aggregate(Sum('views_count'))['views_count__sum'] or 0

    # بيانات المروج والمعلن والوكيل والمطور
    promoter = None
    advertiser = None
    affiliate_links_count = 0
    total_clicks = 0
    valid_clicks = 0
    points = 0

    try:
        if hasattr(user, 'promoter'):
            promoter = user.promoter
            points = promoter.points
            affiliate_links = AffiliateLink.objects.filter(promoter=promoter)
            affiliate_links_count = affiliate_links.count()
            total_clicks = affiliate_links.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0
            valid_clicks = Click.objects.filter(affiliate_link__in=affiliate_links, is_valid=True).count()
    except:
        pass

    try:
        if hasattr(user, 'advertiser'):
            advertiser = user.advertiser
    except:
        pass

    agent_profile = getattr(user, 'agent_profile', None)
    developer_profile = getattr(user, 'developer_profile', None)

    context = {
        'profile_user': user,
        'properties': properties,
        'favorites': favorites,
        'total_properties': total_properties,
        'total_views': total_views,
        'promoter': promoter,
        'advertiser': advertiser,
        'agent_profile': agent_profile,
        'developer_profile': developer_profile,
        'affiliate_links_count': affiliate_links_count,
        'total_clicks': total_clicks,
        'valid_clicks': valid_clicks,
        'points': points,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit(request):
    """تعديل الملف الشخصي"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()

            # تحديث ملف الوكيل إذا كان وكيلاً
            if user.role == 'agent' and hasattr(user, 'agent_profile'):
                agent = user.agent_profile
                agent.agency_name = request.POST.get('agency_name', '')
                agent.license_number = request.POST.get('license_number', '')
                agent.years_experience = request.POST.get('years_experience') or None
                agent.website = request.POST.get('website', '')
                agent.facebook = request.POST.get('facebook', '')
                agent.instagram = request.POST.get('instagram', '')
                agent.linkedin = request.POST.get('linkedin', '')
                agent.save()

            # تحديث ملف المطور إذا كان مطوراً
            elif user.role == 'developer' and hasattr(user, 'developer_profile'):
                dev = user.developer_profile
                dev.company_name = request.POST.get('company_name', '')
                dev.license_number = request.POST.get('license_number', '')
                dev.years_experience = request.POST.get('years_experience') or None
                dev.projects_completed = request.POST.get('projects_completed') or 0
                dev.website = request.POST.get('website', '')
                dev.facebook = request.POST.get('facebook', '')
                dev.instagram = request.POST.get('instagram', '')
                dev.linkedin = request.POST.get('linkedin', '')
                dev.save()

            messages.success(request, 'تم تحديث الملف الشخصي بنجاح.')
            return redirect('accounts:profile_view')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form})


# ============================================================================
# قائمة الوكلاء والمطورين
# ============================================================================

def agent_list(request):
    """عرض قائمة الوكلاء العقاريين"""
    agents = User.objects.filter(role='agent', is_active=True, is_blocked=False).annotate(
        property_count=Count('properties', filter=Q(properties__is_active=True))
    ).order_by('-property_count')

    # إضافة معلومات إضافية
    for agent in agents:
        if hasattr(agent, 'agent_profile'):
            agent.agency_name = agent.agent_profile.agency_name
            agent.years_experience = agent.agent_profile.years_experience

    context = {
        'agents': agents,
        'total_agents': agents.count(),
    }
    return render(request, 'accounts/agent_list.html', context)


def developer_list(request):
    """عرض قائمة المطورين العقاريين"""
    developers = User.objects.filter(role='developer', is_active=True, is_blocked=False).annotate(
        property_count=Count('properties', filter=Q(properties__is_active=True))
    ).order_by('-property_count')

    # إضافة معلومات إضافية
    for dev in developers:
        if hasattr(dev, 'developer_profile'):
            dev.projects_completed = dev.developer_profile.projects_completed
            dev.years_experience = dev.developer_profile.years_experience

    context = {
        'developers': developers,
        'total_developers': developers.count(),
    }
    return render(request, 'accounts/developer_list.html', context)


def agent_detail(request, agent_id):
    """صفحة تفاصيل وكيل عقاري"""
    agent = get_object_or_404(User, id=agent_id, role='agent', is_active=True)
    agent_profile = getattr(agent, 'agent_profile', None)
    properties = Property.objects.filter(owner=agent, is_active=True).order_by('-created_at')
    total_properties = properties.count()
    total_views = properties.aggregate(Sum('views_count'))['views_count__sum'] or 0

    # فلترة حسب نوع العملية
    listing_type = request.GET.get('listing_type')
    if listing_type in ['sale', 'rent']:
        properties = properties.filter(listing_type=listing_type)

    # ترقيم الصفحات
    paginator = Paginator(properties, 12)
    page = request.GET.get('page', 1)
    try:
        properties_page = paginator.page(page)
    except PageNotAnInteger:
        properties_page = paginator.page(1)
    except EmptyPage:
        properties_page = paginator.page(paginator.num_pages)

    context = {
        'agent': agent,
        'agent_profile': agent_profile,
        'properties': properties_page,
        'total_properties': total_properties,
        'total_views': total_views,
        'listing_type': listing_type,
        'is_paginated': properties_page.has_other_pages(),
        'page_obj': properties_page,
    }
    return render(request, 'accounts/agent_detail.html', context)


def developer_detail(request, username):
    """صفحة تفاصيل مطور عقاري"""
    developer = get_object_or_404(User, username=username, role='developer', is_active=True)
    developer_profile = getattr(developer, 'developer_profile', None)
    properties = Property.objects.filter(owner=developer, is_active=True).order_by('-created_at')
    total_properties = properties.count()

    # ترتيب حسب الطلب
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        properties = properties.order_by('price')
    elif sort == 'price_desc':
        properties = properties.order_by('-price')
    elif sort == 'newest':
        properties = properties.order_by('-created_at')
    else:
        properties = properties.order_by('-created_at')

    # ترقيم الصفحات
    paginator = Paginator(properties, 12)
    page = request.GET.get('page', 1)
    try:
        properties_page = paginator.page(page)
    except PageNotAnInteger:
        properties_page = paginator.page(1)
    except EmptyPage:
        properties_page = paginator.page(paginator.num_pages)

    context = {
        'developer': developer,
        'developer_profile': developer_profile,
        'properties': properties_page,
        'total_properties': total_properties,
        'sort': sort,
        'is_paginated': properties_page.has_other_pages(),
        'page_obj': properties_page,
    }
    return render(request, 'accounts/developer_detail.html', context)


# ============================================================================
# نظام الرسائل (Messaging)
# ============================================================================

@login_required
def inbox(request):
    """صندوق الوارد للرسائل"""
    received_messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')

    # تحديث حالة القراءة للرسائل غير المقروءة
    unread_count = received_messages.filter(is_read=False).count()

    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/inbox.html', context)


@login_required
def compose_message(request, recipient_id=None, property_id=None):
    """إنشاء رسالة جديدة"""
    recipient = None
    property_obj = None

    if recipient_id:
        recipient = get_object_or_404(User, id=recipient_id)
    if property_id:
        property_obj = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()
        recipient_id_post = request.POST.get('recipient_id')

        if recipient_id_post:
            recipient = get_object_or_404(User, id=recipient_id_post)

        if not recipient:
            messages.error(request, 'المستلم غير محدد.')
            return redirect('accounts:inbox')

        if not subject or not body:
            messages.error(request, 'الرجاء إدخال الموضوع ونص الرسالة.')
        else:
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                property=property_obj,
                subject=subject,
                body=body
            )
            messages.success(request, 'تم إرسال الرسالة بنجاح.')
            return redirect('accounts:inbox')

    context = {
        'recipient': recipient,
        'property': property_obj,
    }
    return render(request, 'accounts/compose.html', context)


@login_required
def view_message(request, message_id):
    """عرض رسالة محددة (يتم تعليمها كمقروءة)"""
    msg = get_object_or_404(Message, id=message_id)

    # التحقق من أن المستخدم هو المرسل أو المستلم
    if msg.sender != request.user and msg.recipient != request.user:
        messages.error(request, 'ليس لديك صلاحية لعرض هذه الرسالة.')
        return redirect('accounts:inbox')

    if not msg.is_read and msg.recipient == request.user:
        msg.is_read = True
        msg.read_at = timezone.now()
        msg.save()

    return render(request, 'accounts/message_detail.html', {'message': msg})


@login_required
def delete_message(request, message_id):
    """حذف رسالة"""
    msg = get_object_or_404(Message, id=message_id)

    if msg.sender == request.user:
        msg.is_deleted_by_sender = True
        msg.save()
    elif msg.recipient == request.user:
        msg.is_deleted_by_recipient = True
        msg.save()
    else:
        messages.error(request, 'ليس لديك صلاحية لحذف هذه الرسالة.')
        return redirect('accounts:inbox')

    messages.success(request, 'تم حذف الرسالة بنجاح.')
    return redirect('accounts:inbox')


# ============================================================================
# المفضلة (Favorites)
# ============================================================================

@login_required
def favorites_list(request):
    """قائمة العقارات المفضلة للمستخدم"""
    favorites = Favorite.objects.filter(user=request.user).select_related('property').order_by('-created_at')

    # ترقيم الصفحات
    paginator = Paginator(favorites, 12)
    page = request.GET.get('page', 1)
    try:
        favorites_page = paginator.page(page)
    except PageNotAnInteger:
        favorites_page = paginator.page(1)
    except EmptyPage:
        favorites_page = paginator.page(paginator.num_pages)

    context = {
        'favorites': favorites_page,
        'total_favorites': favorites.count(),
        'is_paginated': favorites_page.has_other_pages(),
        'page_obj': favorites_page,
    }
    return render(request, 'accounts/favorites.html', context)


@login_required
def toggle_favorite(request, property_id):
    """إضافة/إزالة عقار من المفضلة (AJAX أو عادي)"""
    property_obj = get_object_or_404(Property, id=property_id, is_active=True)
    favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)

    if not created:
        favorite.delete()
        is_favorited = False
        message = 'تم إزالة العقار من المفضلة'
    else:
        is_favorited = True
        message = 'تم إضافة العقار إلى المفضلة'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'is_favorited': is_favorited,
            'property_id': property_id,
            'message': message
        })

    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'properties:property_detail'))


# ============================================================================
# دوال إضافية
# ============================================================================

@login_required
def become_promoter(request):
    """تفعيل حساب المروج"""
    if request.user.role == 'developer':
        messages.error(request, 'المطورون لا يمكنهم أن يكونوا مروجين.')
        return redirect('accounts:profile_view')

    promoter, created = PromoterProfile.objects.get_or_create(user=request.user)
    if created:
        messages.success(request, 'تم تفعيل حساب المروج بنجاح! يمكنك الآن إنشاء روابط ترويجية.')
    else:
        messages.info(request, 'أنت بالفعل مروج نشط.')

    return redirect('accounts:profile_view')


@login_required
def become_advertiser(request):
    """تفعيل حساب المعلن"""
    advertiser, created = AdvertiserProfile.objects.get_or_create(user=request.user)
    if created:
        messages.success(request, 'تم تفعيل حساب المعلن بنجاح! يمكنك الآن إضافة عقاراتك بنظام النقاط.')
    else:
        messages.info(request, 'أنت بالفعل معلن نشط.')

    return redirect('accounts:profile_view')


# إضافة استيراد timezone
from django.utils import timezone