from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AgentProfile, DeveloperProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('معلومات إضافية', {'fields': ('role', 'phone', 'avatar', 'bio', 'company')}),
    )

admin.site.register(User, CustomUserAdmin)

@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'agency_name', 'license_number', 'years_experience')
    search_fields = ('user__username', 'agency_name')

@admin.register(DeveloperProfile)
class DeveloperProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'projects_completed', 'license_number', 'years_experience')
    search_fields = ('user__username',)