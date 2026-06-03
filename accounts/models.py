from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
import uuid


# ========== دوال مساعدة للتحقق ==========
def validate_phone_number(value):
    """التحقق من صحة رقم الهاتف الجزائري"""
    import re
    pattern = r'^(05|06|07)\d{8}$'
    if value and not re.match(pattern, value):
        raise ValidationError('رقم الهاتف يجب أن يكون 10 أرقام ويبدأ بـ 05، 06، أو 07')


# ========== نموذج المستخدم الرئيسي ==========
class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'مستخدم عادي'),
        ('agent', 'وكيل عقاري'),
        ('developer', 'مطور عقاري'),
        ('advertiser', 'معلن'),
        ('promoter', 'مروج'),
    )

    # الحقول الأساسية
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=20, blank=True, validators=[validate_phone_number])
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True)
    bio = models.TextField(blank=True)
    company = models.CharField(max_length=100, blank=True)

    # حقول إضافية
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # التواريخ والإحصائيات
    last_activity = models.DateTimeField(auto_now=True)
    login_count = models.IntegerField(default=0)

    # الحقول المحجوزة
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    block_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def can_be_promoter(self):
        return self.role != 'developer'

    @property
    def is_verified(self):
        return self.email_verified and self.is_active and not self.is_blocked

    def get_profile(self):
        if self.role == 'agent' and hasattr(self, 'agent_profile'):
            return self.agent_profile
        elif self.role == 'developer' and hasattr(self, 'developer_profile'):
            return self.developer_profile
        return None

    def increment_login_count(self):
        self.login_count += 1
        self.last_activity = timezone.now()
        self.save(update_fields=['login_count', 'last_activity'])


# ========== نماذج الملفات الشخصية ==========
class BaseProfile(models.Model):
    """نموذج أساسي للملفات الشخصية"""
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AgentProfile(BaseProfile):
    """ملف تعريف إضافي للوكيل العقاري"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    license_number = models.CharField(max_length=50, blank=True)
    years_experience = models.PositiveIntegerField(null=True, blank=True)
    agency_name = models.CharField(max_length=150, blank=True)
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    properties_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "ملف الوكيل العقاري"
        verbose_name_plural = "ملفات الوكيل العقاري"

    def __str__(self):
        return f"Agent: {self.user.username}"


class DeveloperProfile(BaseProfile):
    """ملف تعريف إضافي للمطور العقاري"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='developer_profile')
    projects_completed = models.IntegerField(default=0)
    projects_in_progress = models.IntegerField(default=0)
    license_number = models.CharField(max_length=50, blank=True)
    years_experience = models.PositiveIntegerField(null=True, blank=True)
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    class Meta:
        verbose_name = "ملف المطور العقاري"
        verbose_name_plural = "ملفات المطور العقاري"

    def __str__(self):
        return f"Developer: {self.user.username}"


class Message(models.Model):
    MESSAGE_TYPES = (
        ('general', 'عام'),
        ('inquiry', 'استفسار عن عقار'),
        ('offer', 'عرض سعر'),
        ('complaint', 'شكوى'),
        ('support', 'دعم فني'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, null=True, blank=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='general')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"من {self.sender.username} إلى {self.recipient.username}: {self.subject[:50]}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


# ========== إشارات (Signals) لإنشاء الملفات الشخصية ==========
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """إنشاء الملف الشخصي المناسب تلقائياً"""
    if created:
        if instance.role == 'agent':
            AgentProfile.objects.create(user=instance)
        elif instance.role == 'developer':
            DeveloperProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """حفظ الملف الشخصي"""
    if instance.role == 'agent' and hasattr(instance, 'agent_profile'):
        instance.agent_profile.save()
    elif instance.role == 'developer' and hasattr(instance, 'developer_profile'):
        instance.developer_profile.save()