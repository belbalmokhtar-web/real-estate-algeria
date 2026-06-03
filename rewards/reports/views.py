from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q
from .models import AffiliateLink, Click, PromoterProfile, AdvertiserProfile
from properties.models import Property


@staff_member_required
def dashboard_report(request):
    total_clicks = Click.objects.count()
    valid_clicks = Click.objects.filter(is_valid=True).count()
    total_points = PromoterProfile.objects.aggregate(Sum('points'))['points__sum'] or 0
    total_spent = AdvertiserProfile.objects.aggregate(Sum('total_spent'))['total_spent__sum'] or 0

    clicks_by_property = AffiliateLink.objects.values('property__title').annotate(
        clicks=Sum('clicks_count')
    ).order_by('-clicks')[:10]

    context = {
        'total_clicks': total_clicks,
        'valid_clicks': valid_clicks,
        'total_points': total_points,
        'total_spent': total_spent,
        'clicks_by_property': clicks_by_property,
    }
    return render(request, 'reports/dashboard.html', context)