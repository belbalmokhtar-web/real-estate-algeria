from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import PromoterProfile, AdvertiserProfile, AffiliateLink, Click

@admin.register(PromoterProfile)
class PromoterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'total_clicks', 'valid_clicks', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)

@admin.register(AdvertiserProfile)
class AdvertiserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'total_spent', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)

@admin.register(AffiliateLink)
class AffiliateLinkAdmin(admin.ModelAdmin):
    list_display = ('promoter', 'property', 'unique_code', 'clicks_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('promoter__user__username', 'property__title', 'unique_code')
    readonly_fields = ('unique_code', 'created_at')

@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ('affiliate_link', 'ip_address', 'duration', 'is_valid', 'created_at')
    list_filter = ('is_valid', 'created_at')
    search_fields = ('affiliate_link__unique_code', 'ip_address')
    readonly_fields = ('created_at',)