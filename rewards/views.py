# rewards/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count
import json

from .models import (
    PromoterProfile, AdvertiserProfile, AffiliateLink,
    Click, Reward, RewardRedemption  # تأكد من استيراد RewardRedemption
)
from properties.models import Property

# ========== دوال مساعدة ==========
def can_be_promoter(user):
    """التحقق مما إذا كان المستخدم يمكنه التسجيل كمروج"""
    # المطورون لا يمكنهم أن يكونوا مروجين
    return user.role != 'developer'


def get_or_create_promoter(user):
    """إنشاء بروفايل المروج فقط إذا كان مسموحاً له"""
    if not can_be_promoter(user):
        return None, False
    promoter, created = PromoterProfile.objects.get_or_create(user=user)
    return promoter, created


def get_or_create_advertiser(user):
    """إنشاء بروفايل المعلن (مسموح لجميع الأدوار)"""
    advertiser, created = AdvertiserProfile.objects.get_or_create(user=user)
    return advertiser, created


# ========== الدوال الرئيسية ==========
@login_required
def become_promoter(request):
    """تفعيل حساب المروج - يمنع للمطورين"""
    if not can_be_promoter(request.user):
        messages.error(request, 'حساب المطور لا يمكنه الاستفادة من نظام الإحالات.')
        return redirect('rewards:advertiser_dashboard')

    promoter, created = get_or_create_promoter(request.user)
    if created:
        messages.success(request, 'تم تفعيل حساب المروج بنجاح! يمكنك الآن إنشاء روابط ترويجية.')
    else:
        messages.info(request, 'أنت بالفعل مروج نشط.')
    return redirect('rewards:my_links')


@login_required
def become_advertiser(request):
    """تفعيل حساب المعلن - مسموح لجميع الأدوار"""
    advertiser, created = get_or_create_advertiser(request.user)
    if created:
        messages.success(request, 'تم تفعيل حساب المعلن بنجاح! يمكنك الآن إضافة عقاراتك بنظام النقاط.')
    else:
        messages.info(request, 'أنت بالفعل معلن نشط.')
    return redirect('rewards:advertiser_dashboard')


@login_required
def create_affiliate_link(request, property_id=0):
    # إذا كان property_id = 0 (يعني تم إرساله عبر GET)
    if property_id == 0:
        property_id = request.GET.get('property_id')
        if not property_id:
            messages.error(request, 'يرجى اختيار عقار صالح.')
            return redirect('rewards:my_links')

    property_obj = get_object_or_404(Property, id=property_id, is_cpc_active=True)

    # التحقق من أن المستخدم ليس مطوراً (لا يمكنه الترويج)
    if request.user.role == 'developer':
        messages.error(request, 'المطورون لا يمكنهم إنشاء روابط ترويجية.')
        return redirect('properties:property_detail', id=property_obj.id)

    promoter, _ = PromoterProfile.objects.get_or_create(user=request.user)
    link, created = AffiliateLink.objects.get_or_create(promoter=promoter, property=property_obj)

    if created:
        messages.success(request, 'تم إنشاء الرابط الترويجي بنجاح.')
    else:
        messages.info(request, 'لديك بالفعل رابط لهذا العقار.')

    return redirect('rewards:my_links')


@login_required
def my_links(request):
    """عرض روابط المروج - يظهر فقط للمروجين"""
    if not can_be_promoter(request.user):
        messages.error(request, 'هذه الصفحة مخصصة للمروجين فقط.')
        return redirect('rewards:advertiser_dashboard')

    promoter, _ = get_or_create_promoter(request.user)
    if not promoter:
        return redirect('rewards:become_promoter')

    links = AffiliateLink.objects.filter(promoter=promoter).select_related('property')
    available_properties = Property.objects.filter(is_cpc_active=True).exclude(
        id__in=links.values_list('property_id', flat=True)
    )
    context = {
        'links': links,
        'available_properties': available_properties,
        'promoter': promoter,
    }
    return render(request, 'rewards/my_links.html', context)


@login_required
def promoter_dashboard(request):
    """لوحة تحكم المروج - يظهر فقط للمروجين"""
    if not can_be_promoter(request.user):
        messages.error(request, 'هذه الصفحة مخصصة للمروجين فقط.')
        return redirect('rewards:advertiser_dashboard')

    promoter, _ = get_or_create_promoter(request.user)
    if not promoter:
        return redirect('rewards:become_promoter')

    links = AffiliateLink.objects.filter(promoter=promoter)
    total_clicks = links.aggregate(Sum('clicks_count'))['clicks_count__sum'] or 0
    valid_clicks = Click.objects.filter(affiliate_link__in=links, is_valid=True).count()
    points = promoter.points

    # إحصائيات آخر 7 أيام
    from datetime import timedelta
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)
    clicks_by_day = Click.objects.filter(
        affiliate_link__in=links,
        created_at__date__gte=start_date
    ).extra({'day': "date(created_at)"}).values('day').annotate(count=Count('id')).order_by('day')

    days_labels = []
    clicks_data = []
    for i in range(7):
        day = start_date + timedelta(days=i)
        days_labels.append(day.strftime('%a'))
        day_data = next((item['count'] for item in clicks_by_day if str(item['day']) == str(day)), 0)
        clicks_data.append(day_data)

    context = {
        'promoter': promoter,
        'links': links,
        'total_clicks': total_clicks,
        'valid_clicks': valid_clicks,
        'points': points,
        'days_labels': days_labels,
        'clicks_data': clicks_data,
    }
    return render(request, 'rewards/promoter_dashboard.html', context)


@login_required
def advertiser_dashboard(request):
    """لوحة تحكم المعلن - مسموح لجميع الأدوار"""
    advertiser, _ = get_or_create_advertiser(request.user)
    properties = Property.objects.filter(owner=request.user, is_cpc_active=True)

    property_stats = []
    total_clicks = 0
    total_cost = 0
    for prop in properties:
        links = AffiliateLink.objects.filter(property=prop)
        clicks = Click.objects.filter(affiliate_link__in=links)
        click_count = clicks.count()
        cost = click_count * float(prop.cpc) if prop.cpc else 0
        total_clicks += click_count
        total_cost += cost
        property_stats.append({
            'property': prop,
            'clicks': click_count,
            'cost': cost,
        })

    context = {
        'advertiser': advertiser,
        'balance': advertiser.balance,
        'total_clicks': total_clicks,
        'total_cost': total_cost,
        'property_stats': property_stats,
    }
    return render(request, 'rewards/advertiser_dashboard.html', context)
# rewards/views.py - أضف هذه الدوال في نهاية الملف (قبل السطر الأخير)

# rewards/views.py - تصحيح دالة track_click

def track_click(request, code):
    """تتبع النقرة على رابط ترويجي"""
    from django.shortcuts import redirect, get_object_or_404
    from django.urls import reverse
    from .models import AffiliateLink, Click
    import logging

    logger = logging.getLogger(__name__)

    link = get_object_or_404(AffiliateLink, unique_code=code)

    # التحقق من وجود العقار
    if not link.property:
        logger.error(f"الرابط {code} لا يرتبط بأي عقار")
        return redirect('home')

    # تسجيل النقرة
    try:
        click = Click.objects.create(
            affiliate_link=link,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            referer=request.META.get('HTTP_REFERER', ''),
        )
        link.clicks_count += 1
        link.save()

        # إضافة مدة التصفح لاحقاً عبر JavaScript
        response = redirect(link.property.get_absolute_url())
        response.set_cookie('click_id', click.id, max_age=3600)
        return response

    except Exception as e:
        logger.error(f"خطأ في تتبع النقرة: {e}")
        # في حالة الخطأ، نوجه إلى صفحة العقار مباشرة
        try:
            return redirect(link.property.get_absolute_url())
        except:
            return redirect('home')


@login_required
def click_duration_api(request):
    """API لتسجيل مدة بقاء المستخدم على صفحة العقار"""
    if request.method == 'POST':
        data = json.loads(request.body)
        click_id = data.get('click_id')
        duration = data.get('duration')
        try:
            click = Click.objects.get(id=click_id, is_valid=False)
            click.duration = duration
            # منطق التحقق من صحة النقرة: مدة لا تقل عن 30 ثانية
            if duration and duration >= 30:
                click.is_valid = True
                # إضافة نقاط للمروج
                link = click.affiliate_link
                points_earned = int(link.property.cpc * 100)  # تحويل السعر إلى نقاط
                link.promoter.points += points_earned
                link.promoter.valid_clicks += 1
                link.promoter.save()
                # هنا يمكن خصم من المعلن (اختياري)
            click.save()
            return JsonResponse({'status': 'ok'})
        except Click.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Click not found'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)


from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum

@staff_member_required
def dashboard_report(request):
    """تقرير عام للمشرف (اختياري)"""
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


# rewards/views.py - أضف هذه الدوال في نهاية الملف

@login_required
def redeem_points(request):
    """استبدال النقاط بمكافآت"""
    if request.method == 'POST':
        points = int(request.POST.get('points', 0))
        reward_type = request.POST.get('reward_type')
        notes = request.POST.get('notes', '')

        # التحقق من وجود ملف المروج
        if not hasattr(request.user, 'promoter'):
            messages.error(request, 'يجب أن تكون مروجاً لاستبدال النقاط.')
            return redirect('rewards:become_promoter')

        total_points = request.user.promoter.points

        if points <= 0:
            messages.error(request, 'الرجاء إدخال عدد نقاط صحيح')
        elif points > total_points:
            messages.error(request, 'ليس لديك نقاط كافية')
        else:
            # خصم النقاط
            request.user.promoter.points -= points
            request.user.promoter.save()

            # إنشاء طلب استبدال
            redemption = RewardRedemption.objects.create(
                user=request.user,
                points=points,
                reward_type=reward_type,
                notes=notes
            )
            messages.success(request, f'تم تقديم طلب استبدال {points} نقطة بنجاح. سيتم مراجعته قريباً.')

        return redirect('rewards:my_links')

    # عرض صفحة استبدال النقاط
    total_points = request.user.promoter.points if hasattr(request.user, 'promoter') else 0
    context = {
        'total_points': total_points,
        'reward_types': RewardRedemption.REWARD_TYPES,
    }
    return render(request, 'rewards/redeem_points.html', context)


# rewards/views.py - أضف هذه الدالة إذا لم تكن موجودة

@login_required
def leaderboard(request):
    """لوحة المتصدرين - أكثر المروجين نقاطاً"""
    from .models import PromoterProfile
    from django.db.models import Count, Q

    # جلب جميع المروجين الذين لديهم نقاط، مرتبة تنازلياً
    top_promoters = PromoterProfile.objects.filter(
        points__gt=0
    ).select_related('user').order_by('-points')[:20]

    # إضافة عدد الروابط لكل مروج
    for promoter in top_promoters:
        promoter.links_count = promoter.links.count()

    context = {
        'top_promoters': top_promoters,
        'total_promoters': PromoterProfile.objects.filter(points__gt=0).count(),
    }

    return render(request, 'rewards/leaderboard.html', context)


@login_required
def my_earnings(request):
    """عرض أرباحي - تفاصيل النقاط المكتسبة"""
    if not hasattr(request.user, 'promoter'):
        return redirect('rewards:become_promoter')

    # النقاط حسب الروابط
    links = AffiliateLink.objects.filter(promoter=request.user.promoter)

    # النقاط حسب الفترة
    from datetime import timedelta
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)

    rewards = Reward.objects.filter(
        user=request.user,
        created_at__gte=start_date
    ).order_by('-created_at')

    context = {
        'promoter': request.user.promoter,
        'links': links,
        'rewards': rewards,
        'total_points': request.user.promoter.points,
    }
    return render(request, 'rewards/my_earnings.html', context)


# إصلاح دالة dashboard_report (إذا كانت موجودة في reports/views.py)
# إذا لم تكن موجودة، قم بإنشائها
try:
    from reports.views import dashboard_report
except ImportError:
    # تعريف الدالة هنا إذا لم تكن موجودة
    @staff_member_required
    def dashboard_report(request):
        """تقرير عام للمشرف"""
        from django.db.models import Sum

        total_clicks = Click.objects.count()
        valid_clicks = Click.objects.filter(is_valid=True).count()
        total_points = PromoterProfile.objects.aggregate(Sum('points'))['points__sum'] or 0
        total_spent = AdvertiserProfile.objects.aggregate(Sum('total_spent'))['total_spent__sum'] or 0
        total_redemptions = RewardRedemption.objects.aggregate(Sum('points'))['points__sum'] or 0

        clicks_by_property = AffiliateLink.objects.values('property__title').annotate(
            clicks=Sum('clicks_count')
        ).order_by('-clicks')[:10]

        clicks_by_promoter = AffiliateLink.objects.values('promoter__user__username').annotate(
            clicks=Sum('clicks_count'),
            points=Sum('points_earned')
        ).order_by('-clicks')[:10]

        context = {
            'total_clicks': total_clicks,
            'valid_clicks': valid_clicks,
            'total_points': total_points,
            'total_spent': total_spent,
            'total_redemptions': total_redemptions,
            'clicks_by_property': clicks_by_property,
            'clicks_by_promoter': clicks_by_promoter,
        }
        return render(request, 'reports/dashboard.html', context)


    @login_required
    def redeem_points(request):
        """استبدال النقاط بمكافآت"""
        from .models import RewardRedemption  # استيراد داخل الدالة أيضاً

        # التحقق من وجود ملف المروج
        if not hasattr(request.user, 'promoter'):
            messages.error(request, 'يجب أن تكون مروجاً لاستبدال النقاط.')
            return redirect('rewards:become_promoter')

        total_points = request.user.promoter.points

        if request.method == 'POST':
            points = int(request.POST.get('points', 0))
            reward_type = request.POST.get('reward_type')
            notes = request.POST.get('notes', '')

            if points <= 0:
                messages.error(request, 'الرجاء إدخال عدد نقاط صحيح')
            elif points > total_points:
                messages.error(request, 'ليس لديك نقاط كافية')
            else:
                # خصم النقاط
                request.user.promoter.points -= points
                request.user.promoter.save()

                # إنشاء طلب استبدال
                redemption = RewardRedemption.objects.create(
                    user=request.user,
                    points=points,
                    reward_type=reward_type,
                    notes=notes
                )
                messages.success(request, f'تم تقديم طلب استبدال {points} نقطة بنجاح. سيتم مراجعته قريباً.')

            return redirect('rewards:my_links')

        # عرض صفحة استبدال النقاط (GET)
        reward_types = [
            ('cash', 'نقود - 100 نقطة = 100 دج'),
            ('discount', 'خصم - 200 نقطة = خصم 5% على عمولة'),
            ('gift', 'هدية - 500 نقطة = هدية قيمة'),
            ('voucher', 'قسيمة شراء - 1000 نقطة = قسيمة 1000 دج'),
        ]

        context = {
            'total_points': total_points,
            'reward_types': reward_types,
        }
        return render(request, 'rewards/redeem_points.html', context)
