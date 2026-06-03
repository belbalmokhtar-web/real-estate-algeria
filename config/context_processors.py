from django.conf import settings

def site_settings(request):
    """إضافة إعدادات الموقع إلى جميع القوالب"""
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_DOMAIN': settings.SITE_DOMAIN,
        'DEBUG': settings.DEBUG,
    }