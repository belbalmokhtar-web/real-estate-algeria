# rewards/models.py
import secrets
from django.db import models
from django.conf import settings
from properties.models import Property
from django.utils import timezone


class PromoterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='promoter')
    points = models.IntegerField(default=0)
    total_clicks = models.IntegerField(default=0)
    valid_clicks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Promoter: {self.user.username}"

    def add_points(self, points, reason=""):
        """إضافة نقاط للمروج"""
        self.points += points
        self.save()
        # تسجيل المكافأة
        Reward.objects.create(
            user=self.user,
            points=points,
            reason=reason or "نقاط إحالة"
        )

    class Meta:
        verbose_name = "ملف المروج"
        verbose_name_plural = "ملفات المروجين"


class AdvertiserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='advertiser')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Advertiser: {self.user.username}"

    def deduct_balance(self, amount):
        """خصم من رصيد المعلن"""
        if self.balance >= amount:
            self.balance -= amount
            self.total_spent += amount
            self.save()
            return True
        return False

    class Meta:
        verbose_name = "ملف المعلن"
        verbose_name_plural = "ملفات المعلنين"


class AffiliateLink(models.Model):
    promoter = models.ForeignKey(PromoterProfile, on_delete=models.CASCADE, related_name='links')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='affiliate_links')
    unique_code = models.CharField(max_length=100, unique=True, default=secrets.token_urlsafe(16))
    clicks_count = models.IntegerField(default=0)
    valid_clicks_count = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('rewards:track_click', args=[self.unique_code])

    def get_full_url(self, request=None):
        """الحصول على الرابط الكامل"""
        if request:
            return request.build_absolute_uri(self.get_absolute_url())
        return self.get_absolute_url()

    def __str__(self):
        return f"{self.promoter.user.username} - {self.property.title}"

    class Meta:
        verbose_name = "رابط ترويجي"
        verbose_name_plural = "روابط ترويجية"
        unique_together = ['promoter', 'property']


class Click(models.Model):
    affiliate_link = models.ForeignKey(AffiliateLink, on_delete=models.CASCADE, related_name='clicks')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    referer = models.URLField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # seconds spent on property page
    is_valid = models.BooleanField(default=False)
    points_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Click on {self.affiliate_link} at {self.created_at}"

    def validate_click(self, duration):
        """التحقق من صحة النقرة بناءً على المدة"""
        self.duration = duration
        # منطق التحقق: مدة لا تقل عن 30 ثانية
        if duration and duration >= 30:
            self.is_valid = True
            # حساب النقاط (نقطة لكل 10 ثوانٍ فوق 30)
            extra_points = (duration - 30) // 10
            self.points_earned = 10 + extra_points
            self.affiliate_link.valid_clicks_count += 1
            self.affiliate_link.points_earned += self.points_earned
            self.affiliate_link.save()
            # إضافة نقاط للمروج
            self.affiliate_link.promoter.add_points(
                self.points_earned,
                f"نقرة صالحة على عقار {self.affiliate_link.property.title}"
            )
        self.save()
        return self.is_valid

    class Meta:
        verbose_name = "نقرة"
        verbose_name_plural = "النقرات"
        ordering = ['-created_at']


class Reward(models.Model):
    """نموذج المكافآت"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rewards')
    points = models.IntegerField(default=0, verbose_name="عدد النقاط")
    reason = models.CharField(max_length=200, verbose_name="السبب")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.points} نقطة - {self.reason}"

    class Meta:
        verbose_name = "مكافأة"
        verbose_name_plural = "المكافآت"
        ordering = ['-created_at']


class RewardRedemption(models.Model):
    """نموذج استبدال النقاط"""
    REWARD_TYPES = (
        ('cash', 'نقود'),
        ('discount', 'خصم'),
        ('gift', 'هدية'),
        ('voucher', 'قسيمة شراء'),
    )

    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('approved', 'موافق عليه'),
        ('rejected', 'مرفوض'),
        ('completed', 'مكتمل'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='redemptions')
    points = models.IntegerField(verbose_name="النقاط المستبدلة")
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES, verbose_name="نوع المكافأة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.points} نقطة - {self.get_reward_type_display()}"

    def approve(self):
        """الموافقة على طلب الاستبدال"""
        self.status = 'approved'
        self.processed_at = timezone.now()
        self.save()

    def complete(self):
        """إكمال طلب الاستبدال"""
        self.status = 'completed'
        self.save()

    def reject(self, reason=""):
        """رفض طلب الاستبدال"""
        self.status = 'rejected'
        self.notes = reason
        self.save()
        # إعادة النقاط للمستخدم
        self.user.promoter.points += self.points
        self.user.promoter.save()

    class Meta:
        verbose_name = "استبدال مكافأة"
        verbose_name_plural = "استبدال المكافآت"
        ordering = ['-created_at']

    # models.py
    @property
    def get_all_images(self):
        """دمج الصور بدون تكرار"""
        images = []
        if self.image: images.append(self.image.url)
        for img in self.images.all():
            if img.image and img.image.url not in images:
                images.append(img.image.url)
        return images

    @property
    def favorited_count(self):
        """عدد المرات التي أُضيف فيها العقار للمفضلة"""
        return self.favorited_by.count()