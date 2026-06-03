# properties/models.py
import uuid
from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

# استيراد نماذج التقييم من ملف منفصل
from .models_valuation import (
    Wilaya, Commune, Zone, NatureImmeuble, Caracteristique, ValuationRange
)


# ========== الفئات (Categories) ==========
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم الفئة")
    slug = models.SlugField(unique=True, blank=True, verbose_name="الرابط")
    description = models.TextField(blank=True, verbose_name="الوصف")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "فئة"
        verbose_name_plural = "الفئات"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ========== الصور ==========
class PropertyImage(models.Model):
    property = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/images/%Y/%m/')
    is_main = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = "صورة عقار"
        verbose_name_plural = "صور العقارات"

    def __str__(self):
        return f"صورة {self.property.title} - {self.order}"


# ========== العقار ==========
class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'شقة'),
        ('house', 'منزل'),
        ('villa', 'فيلا'),
        ('land', 'أرض'),
        ('commercial', 'محل تجاري'),
        ('office', 'مكتب'),
        ('shop', 'متجر'),
        ('warehouse', 'مستودع'),
    ]

    LISTING_TYPE_CHOICES = [
        ('sale', 'للبيع'),
        ('rent', 'للإيجار'),
        ('exchange', 'للبدل'),
    ]

    # المعلومات الأساسية
    title = models.CharField(max_length=200, verbose_name="العنوان")
    slug = models.SlugField(unique=True, blank=True, verbose_name="الرابط")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # الموقع - استخدام النماذج المستوردة
    wilaya = models.ForeignKey(Wilaya, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الولاية")
    commune = models.ForeignKey(Commune, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="البلدية")
    address = models.CharField(max_length=255, blank=True, verbose_name="العنوان التفصيلي")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="خط العرض")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="خط الطول")

    # التفاصيل
    price = models.BigIntegerField(verbose_name="السعر", validators=[MinValueValidator(0)])
    area_sqm = models.IntegerField(verbose_name="المساحة (م²)", validators=[MinValueValidator(0)])
    bedrooms = models.IntegerField(null=True, blank=True, verbose_name="عدد الغرف", validators=[MinValueValidator(0)])
    bathrooms = models.IntegerField(null=True, blank=True, verbose_name="عدد الحمامات", validators=[MinValueValidator(0)])
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, verbose_name="نوع العقار")
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, verbose_name="نوع العملية")

    # الصور
    image = models.ImageField(upload_to='properties/%Y/%m/', blank=True, null=True, verbose_name="الصورة الرئيسية")

    # الحالة
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_featured = models.BooleanField(default=False, verbose_name="مميز")
    is_verified = models.BooleanField(default=False, verbose_name="موثق")

    # الإعلانات المدفوعة (CPC)
    cpc = models.DecimalField(max_digits=5, decimal_places=2, default=0.20, verbose_name="CPC", validators=[MinValueValidator(0)])
    is_cpc_active = models.BooleanField(default=False, verbose_name="CPC نشط")
    cpc_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="ميزانية CPC")
    cpc_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المصروف من CPC")

    # العلاقات
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties', verbose_name="المالك")
    agent = models.ForeignKey('accounts.AgentProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='properties', verbose_name="الوكيل")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties', verbose_name="الفئة")

    # التواريخ والإحصائيات
    transaction_date = models.DateField(null=True, blank=True, verbose_name="تاريخ المعاملة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    views_count = models.IntegerField(default=0, verbose_name="عدد المشاهدات")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "عقار"
        verbose_name_plural = "العقارات"
        indexes = [
            models.Index(fields=['wilaya', 'commune']),
            models.Index(fields=['property_type', 'listing_type']),
            models.Index(fields=['price', 'area_sqm']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Property.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        wilaya_name = self.wilaya.name_ar if self.wilaya else "بدون ولاية"
        return f"{self.title} - {wilaya_name}"

    def get_absolute_url(self):
        return reverse('properties:property_detail', args=[self.id])

    def increase_views(self):
        """زيادة عدد المشاهدات"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    @property
    def formatted_price(self):
        """تنسيق السعر"""
        if self.price >= 1000000:
            return f"{self.price / 1000000:.1f} مليون دج"
        return f"{self.price:,} دج"

    @property
    def price_per_sqm(self):
        """السعر لكل متر مربع"""
        if self.area_sqm > 0:
            return self.price / self.area_sqm
        return 0

    @property
    def main_image(self):
        """الحصول على الصورة الرئيسية"""
        if self.images.filter(is_main=True).exists():
            return self.images.filter(is_main=True).first()
        elif self.images.exists():
            return self.images.first()
        return self.image

    @property
    def average_rating(self):
        """متوسط التقييم"""
        reviews = self.reviews.all()
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return 0

    @property
    def review_count(self):
        """عدد التقييمات"""
        return self.reviews.count()


# ========== الدفعات ==========
class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'قيد الانتظار'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
        ('refunded', 'مسترجع'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments', verbose_name="المستخدم")
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, related_name='payments', verbose_name="العقار")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ", validators=[MinValueValidator(0)])
    stripe_payment_intent = models.CharField(max_length=255, blank=True, verbose_name="معرف الدفع")
    status = models.CharField(max_length=50, default='pending', choices=PAYMENT_STATUS, verbose_name="الحالة")
    payment_method = models.CharField(max_length=50, blank=True, verbose_name="طريقة الدفع")
    transaction_id = models.CharField(max_length=255, blank=True, verbose_name="رقم المعاملة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الإكمال")

    class Meta:
        verbose_name = "دفعة"
        verbose_name_plural = "الدفعات"
        ordering = ['-created_at']

    def __str__(self):
        return f"دفعة {self.amount} دج - {self.user.username}"


# ========== المفضلة ==========
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites', verbose_name="المستخدم")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by', verbose_name="العقار")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        unique_together = ('user', 'property')
        verbose_name = "مفضلة"
        verbose_name_plural = "المفضلات"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.property.title}"


# ========== التقييمات ==========
class Review(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews', verbose_name="العقار")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name="المستخدم")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="التقييم", validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(verbose_name="التعليق")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        unique_together = ('property', 'user')
        verbose_name = "تقييم"
        verbose_name_plural = "التقييمات"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.property.title} - {self.rating}/5"


# ============================================================================
# 11. نماذج المطورين العقاريين (Promoteurs Immobiliers) - النسخة الوحيدة
# ============================================================================

class PromoteurImmobilier(models.Model):
    """
    نموذج المطور العقاري (المرقي العقاري)
    """
    numero_affiliation = models.CharField(max_length=10, unique=True, verbose_name="رقم الانتساب")
    numero_agrement = models.CharField(max_length=20, blank=True, verbose_name="رقم الاعتماد")
    numero_tnpi = models.CharField(max_length=50, blank=True, verbose_name="رقم التسجيل TNPI")

    nom_entreprise = models.CharField(max_length=255, verbose_name="اسم الشركة")
    nom_gerant = models.CharField(max_length=255, blank=True, verbose_name="اسم المسير")

    adresse = models.TextField(blank=True, verbose_name="العنوان التجاري")
    telephone = models.CharField(max_length=50, blank=True, verbose_name="الهاتف")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")

    wilaya = models.ForeignKey(
        Wilaya, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="الولاية"
    )

    # ========== حقول الصور ==========
    logo = models.ImageField(
        upload_to='promoteurs/logos/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="شعار الشركة"
    )
    cover_image = models.ImageField(
        upload_to='promoteurs/covers/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="صورة الغلاف"
    )
    avatar = models.ImageField(
        upload_to='promoteurs/avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="الصورة الشخصية"
    )

    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "مطور عقاري"
        verbose_name_plural = "المطورين العقاريين"
        ordering = ['nom_entreprise']
        indexes = [
            models.Index(fields=['numero_affiliation']),
            models.Index(fields=['wilaya']),
        ]

    def __str__(self):
        return f"{self.numero_affiliation} - {self.nom_entreprise}"

    @property
    def projets_count(self):
        return self.projets.count()


class ProjetImmobilier(models.Model):
    """
    نموذج المشروع العقاري (مشروع سكني)
    """
    promoteur = models.ForeignKey(
        PromoteurImmobilier, on_delete=models.CASCADE,
        related_name='projets', verbose_name="المطور"
    )

    nom_projet = models.CharField(max_length=255, verbose_name="اسم المشروع")
    localisation = models.TextField(verbose_name="الموقع")

    wilaya = models.ForeignKey(
        Wilaya, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="الولاية"
    )
    commune = models.ForeignKey(
        Commune, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="البلدية"
    )
    daira = models.CharField(max_length=100, blank=True, verbose_name="الدائرة")

    date_garantie = models.DateField(null=True, blank=True, verbose_name="تاريخ منح الضمان")

    # إحصائيات المشروع
    total_logements = models.IntegerField(default=0, verbose_name="إجمالي الوحدات")

    # تفاصيل أنواع الوحدات
    f1_count = models.IntegerField(default=0, verbose_name="عدد F1")
    f2_count = models.IntegerField(default=0, verbose_name="عدد F2")
    f3_count = models.IntegerField(default=0, verbose_name="عدد F3")
    f4_count = models.IntegerField(default=0, verbose_name="عدد F4")
    f5_count = models.IntegerField(default=0, verbose_name="عدد F5")
    f6_count = models.IntegerField(default=0, verbose_name="عدد F6")
    duplex_count = models.IntegerField(default=0, verbose_name="عدد Duplex")
    triplex_count = models.IntegerField(default=0, verbose_name="عدد Triplex")
    villa_count = models.IntegerField(default=0, verbose_name="عدد Villas")
    cave_count = models.IntegerField(default=0, verbose_name="عدد Caves")
    garage_count = models.IntegerField(default=0, verbose_name="عدد Garages")
    parking_count = models.IntegerField(default=0, verbose_name="عدد Parkings")
    local_count = models.IntegerField(default=0, verbose_name="عدد Locaux commerciaux")

    description = models.TextField(blank=True, verbose_name="وصف المشروع")

    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "مشروع عقاري"
        verbose_name_plural = "المشاريع العقارية"
        ordering = ['-date_garantie', 'nom_projet']
        indexes = [
            models.Index(fields=['promoteur', 'wilaya']),
            models.Index(fields=['date_garantie']),
        ]

    def __str__(self):
        return f"{self.nom_projet} - {self.promoteur.nom_entreprise}"

    def update_total(self):
        """تحديث إجمالي الوحدات"""
        self.total_logements = (
                self.f1_count + self.f2_count + self.f3_count +
                self.f4_count + self.f5_count + self.f6_count +
                self.duplex_count + self.triplex_count + self.villa_count +
                self.cave_count + self.garage_count + self.parking_count +
                self.local_count
        )
        self.save(update_fields=['total_logements'])