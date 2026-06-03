# properties/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Category, Property, PropertyImage, Payment, Favorite, Review,
    PromoteurImmobilier, ProjetImmobilier  # ✅ تم التصحيح
)
from .models_valuation import (
    Wilaya, Commune, Zone, NatureImmeuble, Caracteristique, ValuationRange
)
from django.utils.safestring import mark_safe
from django.conf import settings
from django.conf.urls.static import static

# ========== فلتر مخصص لنطاق السعر ==========
class PriceRangeFilter(admin.SimpleListFilter):
    title = 'نطاق السعر (دج/م²)'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return (
            ('low', 'أقل من 20,000 دج/م²'),
            ('medium', '20,000 - 50,000 دج/م²'),
            ('high', '50,000 - 100,000 دج/م²'),
            ('very_high', 'أكثر من 100,000 دج/م²'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(max_price_per_sqm__lt=20000)
        if self.value() == 'medium':
            return queryset.filter(min_price_per_sqm__gte=20000, max_price_per_sqm__lte=50000)
        if self.value() == 'high':
            return queryset.filter(min_price_per_sqm__gte=50000, max_price_per_sqm__lte=100000)
        if self.value() == 'very_high':
            return queryset.filter(min_price_per_sqm__gt=100000)
        return queryset


# ========== إدارة الولايات ==========
@admin.register(Wilaya)
class WilayaAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_ar', 'name_fr', 'communes_count']
    search_fields = ['code', 'name_ar', 'name_fr']
    ordering = ['code']

    def communes_count(self, obj):
        return obj.communes.count()

    communes_count.short_description = 'عدد البلديات'


# ========== إدارة البلديات ==========
@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name_fr', 'wilaya']
    list_filter = ['wilaya']
    search_fields = ['name_ar', 'name_fr']
    autocomplete_fields = ['wilaya']


# ========== إدارة المناطق ==========
@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['key', 'name_ar', 'name_fr']
    search_fields = ['name_ar', 'name_fr', 'key']


# ========== إدارة طبيعة العقار ==========
class CaracteristiqueInline(admin.TabularInline):
    model = Caracteristique
    extra = 1
    fields = ['key', 'name_ar', 'name_fr', 'order']


@admin.register(NatureImmeuble)
class NatureImmeubleAdmin(admin.ModelAdmin):
    list_display = ['key', 'name_ar', 'name_fr']
    search_fields = ['name_ar', 'name_fr', 'key']
    inlines = [CaracteristiqueInline]


# ========== إدارة الخصائص ==========
@admin.register(Caracteristique)
class CaracteristiqueAdmin(admin.ModelAdmin):
    list_display = ['name_fr', 'name_ar', 'nature', 'key', 'order']
    list_filter = ['nature']
    search_fields = ['name_fr', 'name_ar']
    list_editable = ['order']


# ========== إدارة نطاقات التقييم ==========
@admin.register(ValuationRange)
class ValuationRangeAdmin(admin.ModelAdmin):
    list_display = [
        'wilaya', 'commune', 'zone', 'nature',
        'caracteristique', 'min_price_per_sqm', 'max_price_per_sqm'
    ]
    list_filter = [PriceRangeFilter, 'wilaya', 'zone', 'nature']
    search_fields = [
        'wilaya__name_ar', 'commune__name_ar',
        'nature__name_fr', 'caracteristique__name_fr'
    ]
    autocomplete_fields = ['wilaya', 'commune', 'zone', 'nature', 'caracteristique']
    list_per_page = 50


# ========== إدارة الفئات ==========
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ['parent']


# ========== إدارة صور العقار ==========
class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 2
    fields = ['image', 'is_main', 'order']


# ========== إدارة العقارات ==========
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'wilaya', 'commune', 'property_type', 'listing_type',
        'price', 'area_sqm', 'is_active', 'is_featured', 'views_count'
    ]
    list_filter = [
        'property_type', 'listing_type', 'is_active', 'is_featured',
        'is_verified', 'wilaya', 'created_at'
    ]
    search_fields = [
        'title', 'description', 'address', 'wilaya__name_ar', 'commune__name_ar'
    ]
    readonly_fields = ['slug', 'views_count', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['wilaya', 'commune', 'owner', 'agent', 'category']
    inlines = [PropertyImageInline]
    list_per_page = 25


# ========== إدارة الصور ==========
@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'is_main', 'order', 'uploaded_at']
    list_filter = ['is_main', 'uploaded_at']
    search_fields = ['property__title']
    list_editable = ['is_main', 'order']


# ========== إدارة الدفعات ==========
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'user__email', 'property__title', 'transaction_id']
    readonly_fields = ['created_at', 'completed_at']


# ========== إدارة المفضلة ==========
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'property__title']


# ========== إدارة التقييمات ==========
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['property__title', 'user__username', 'comment']


# ============================================================================
# إدارة المطورين العقاريين والمشاريع
# ============================================================================

class ProjetImmobilierInline(admin.TabularInline):
    model = ProjetImmobilier
    extra = 0
    fields = ['nom_projet', 'wilaya', 'commune', 'total_logements', 'date_garantie']
    readonly_fields = ['total_logements']
    show_change_link = True


# properties/admin.py - أضف هذه التعديلات

@admin.register(PromoteurImmobilier)
class PromoteurImmobilierAdmin(admin.ModelAdmin):
    list_display = [
        'numero_affiliation', 'nom_entreprise', 'wilaya',
        'projets_count', 'telephone', 'is_active', 'logo_preview'
    ]
    list_filter = ['wilaya', 'is_active']
    search_fields = [
        'numero_affiliation', 'numero_agrement',
        'nom_entreprise', 'nom_gerant', 'telephone'
    ]
    list_editable = ['is_active']
    list_per_page = 50
    autocomplete_fields = ['wilaya']
    inlines = [ProjetImmobilierInline]

    fieldsets = (
        ('معلومات التسجيل', {
            'fields': ('numero_affiliation', 'numero_agrement', 'numero_tnpi')
        }),
        ('معلومات الشركة', {
            'fields': ('nom_entreprise', 'nom_gerant', 'wilaya', 'adresse')
        }),
        ('معلومات الاتصال', {
            'fields': ('telephone', 'email')
        }),
        ('الصور', {
            'fields': ('logo', 'cover_image', 'avatar'),
            'classes': ('wide',)
        }),
        ('الحالة', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" style="max-height: 50px; max-width: 100px;" />')
        return mark_safe('<span style="color: gray;">لا يوجد شعار</span>')


@admin.register(ProjetImmobilier)
class ProjetImmobilierAdmin(admin.ModelAdmin):
    list_display = [
        'nom_projet', 'promoteur_link', 'wilaya', 'commune',
        'total_logements', 'date_garantie'
    ]
    list_filter = ['wilaya', 'date_garantie', 'promoteur']
    search_fields = ['nom_projet', 'localisation', 'promoteur__nom_entreprise']
    list_select_related = ['promoteur', 'wilaya', 'commune']
    autocomplete_fields = ['promoteur', 'wilaya', 'commune']
    list_per_page = 50

    def promoteur_link(self, obj):
        url = reverse('admin:properties_promoteurimmobilier_change', args=[obj.promoteur.id])
        return format_html('<a href="{}">{}</a>', url, obj.promoteur.nom_entreprise)

    promoteur_link.short_description = 'المطور'

    fieldsets = (
        ('المطور والمشروع', {
            'fields': ('promoteur', 'nom_projet', 'description')
        }),
        ('الموقع', {
            'fields': ('wilaya', 'commune', 'daira', 'localisation')
        }),
        ('الضمان', {
            'fields': ('date_garantie',)
        }),
        ('تفاصيل الوحدات', {
            'fields': (
                ('f1_count', 'f2_count', 'f3_count', 'f4_count'),
                ('f5_count', 'f6_count', 'duplex_count', 'triplex_count'),
                ('villa_count', 'cave_count', 'garage_count', 'parking_count'),
                ('local_count', 'total_logements'),
            ),
            'classes': ('wide',)
        }),
        ('الحالة', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['total_logements']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.update_total()