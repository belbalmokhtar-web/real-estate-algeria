from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q
from properties.models import Property
from accounts.models import User
from rewards.models import Click, AffiliateLink, PromoterProfile, AdvertiserProfile

@staff_member_required
def dashboard(request):
    # إحصائيات عامة
    total_properties = Property.objects.filter(is_active=True).count()
    total_users = User.objects.count()
    total_clicks = Click.objects.count()
    valid_clicks = Click.objects.filter(is_valid=True).count()
    total_points = PromoterProfile.objects.aggregate(Sum('points'))['points__sum'] or 0
    total_ad_spent = AdvertiserProfile.objects.aggregate(Sum('total_spent'))['total_spent__sum'] or 0

    # النقرات حسب العقار (أعلى 5)
    clicks_by_property = AffiliateLink.objects.values('property__title').annotate(
        clicks=Sum('clicks_count')
    ).order_by('-clicks')[:5]

    # النقرات حسب الشهر (آخر 12 شهراً)
    from django.db.models.functions import TruncMonth
    clicks_by_month = Click.objects.filter(created_at__isnull=False).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(count=Count('id')).order_by('month')

    months = [item['month'].strftime('%b %Y') for item in clicks_by_month] if clicks_by_month else []
    clicks_data = [item['count'] for item in clicks_by_month] if clicks_by_month else []

    # أحدث 10 نقرات
    recent_clicks = Click.objects.select_related('affiliate_link__property', 'affiliate_link__promoter__user').order_by('-created_at')[:10]

    context = {
        'total_properties': total_properties,
        'total_users': total_users,
        'total_clicks': total_clicks,
        'valid_clicks': valid_clicks,
        'total_points': total_points,
        'total_ad_spent': total_ad_spent,
        'clicks_by_property': clicks_by_property,
        'months': months,
        'clicks_data': clicks_data,
        'recent_clicks': recent_clicks,
    }
    return render(request, 'reports/dashboard.html', context)