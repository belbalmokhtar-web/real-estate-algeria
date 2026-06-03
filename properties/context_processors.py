# properties/context_processors.py
from django.conf import settings
from django.db.models import Avg, Count


def site_context(request):
    """
    Context processor لتوفير بيانات عامة لجميع قوالب الموقع
    """
    context = {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'عقاري'),
        'SITE_NAME_FULL': getattr(settings, 'SITE_NAME_FULL', 'عقاري — منصة العقارات الجزائرية'),
        'PROPERTIES_PER_PAGE': getattr(settings, 'PROPERTIES_PER_PAGE', 12),
        'FEATURED_PROPERTIES_COUNT': getattr(settings, 'FEATURED_PROPERTIES_COUNT', 6),
        'DEBUG': settings.DEBUG,
        'total_properties': 0,
        'avg_property_price': 0,
    }

    # محاولة جلب إحصائيات من قاعدة البيانات
    try:
        from properties.models import Property

        # عدد العقارات النشطة
        context['total_properties'] = Property.objects.filter(is_active=True).count()

        # متوسط السعر
        avg_price = Property.objects.filter(is_active=True).aggregate(
            avg_price=Avg('price')
        )['avg_price']
        context['avg_property_price'] = int(avg_price) if avg_price else 0

        # أحدث 5 عقارات (للعرض في التذييل مثلاً)
        context['latest_properties_global'] = Property.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]

    except Exception:
        # في حالة عدم وجود قاعدة بيانات أو نموذج بعد
        context['latest_properties_global'] = []

    return context