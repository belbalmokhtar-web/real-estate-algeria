# properties/models_valuation.py
from django.db import models
from django.core.validators import MinValueValidator


class Wilaya(models.Model):
    """الولاية"""
    code = models.CharField(max_length=2, unique=True, verbose_name="الرمز")
    name_ar = models.CharField(max_length=100, verbose_name="الاسم بالعربية")
    name_fr = models.CharField(max_length=100, verbose_name="الاسم بالفرنسية")

    class Meta:
        verbose_name = "ولاية"
        verbose_name_plural = "الولايات"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name_ar}"


class Commune(models.Model):
    """البلدية"""
    wilaya = models.ForeignKey(
        Wilaya, on_delete=models.CASCADE,
        related_name="communes", verbose_name="الولاية"
    )
    name_ar = models.CharField(max_length=100, verbose_name="الاسم بالعربية")
    name_fr = models.CharField(max_length=100, verbose_name="الاسم بالفرنسية")

    class Meta:
        verbose_name = "بلدية"
        verbose_name_plural = "البلديات"
        ordering = ["wilaya__code", "name_fr"]

    def __str__(self):
        return f"{self.name_ar} ({self.wilaya.code})"


class Zone(models.Model):
    """منطقة التقييم"""
    ZONE_CHOICES = [
        ("residential", "Zone résidentielle | المنطقة السكنية"),
        ("city_center", "Centre-ville | وسط المدينة"),
        ("peripheral",  "Zone périphérique | المنطقة المحيطية"),
        ("remote",      "Zone d'éloignement | المنطقة النائية"),
    ]
    key = models.CharField(
        max_length=20, choices=ZONE_CHOICES, unique=True,
        verbose_name="المفتاح"
    )
    name_ar = models.CharField(max_length=100, verbose_name="الاسم بالعربية")
    name_fr = models.CharField(max_length=100, verbose_name="الاسم بالفرنسية")

    class Meta:
        verbose_name = "منطقة"
        verbose_name_plural = "المناطق"

    def __str__(self):
        return f"{self.name_fr} | {self.name_ar}"


class NatureImmeuble(models.Model):
    """طبيعة العقار"""
    NATURE_CHOICES = [
        ("individuels",          "Individuels | أفراد"),
        ("collectifs",           "Collectifs et Semi-Collectifs | جماعية وشبه جماعية"),
        ("locaux_commerciaux",   "Locaux Commerciaux & Usage Professionnel | محلات تجارية ومهنية"),
        ("hangars",              "Hangars | مستودعات"),
        ("terrains_nus",         "Terrains Nus | أراضي عارية"),
        ("terrains_plaine",      "Terrains Agricoles en Plaine | أراضي زراعية سهلية"),
        ("terrains_pente",       "Terrains Agricoles en Pente | أراضي زراعية منحدرة"),
    ]
    key = models.CharField(
        max_length=30, choices=NATURE_CHOICES, unique=True,
        verbose_name="المفتاح"
    )
    name_ar = models.CharField(max_length=150, verbose_name="الاسم بالعربية")
    name_fr = models.CharField(max_length=150, verbose_name="الاسم بالفرنسية")

    class Meta:
        verbose_name = "طبيعة العقار"
        verbose_name_plural = "طبائع العقارات"

    def __str__(self):
        return f"{self.name_fr} | {self.name_ar}"


class Caracteristique(models.Model):
    """
    خاصية / نوع العقار — مرتبطة بطبيعة محددة.
    كل طبيعة لها قائمة خصائصها الخاصة.
    """
    CARAC_CHOICES = [
        # Individuels & Collectifs & Semi-Collectifs
        ("standing",   "Standing | ستاندينغ"),
        ("ameliore",   "Amélioré | محسّن"),
        ("economique", "Economique | اقتصادي"),
        ("precaire",   "Précaire | هش"),
        # Locaux Commerciaux
        ("artere_haute",  "Artère hautement commerciale | شارع تجاري مرتفع"),
        ("artere_moyen",  "Artère moyennement commerciale | شارع تجاري متوسط"),
        ("artere_faible", "Artère peu commerciale | شارع تجاري ضعيف"),
        # Hangars
        ("zone_urbaine", "Situé en zone urbaine | في منطقة حضرية"),
        ("zone_rurale",  "Situé en zone rurale | في منطقة ريفية"),
        # Terrains Nus
        ("pp_2f_avec",  "Pleine propriété 2 façades avec raccordements | ملكية تامة 2 واجهة مع توصيلات"),
        ("pp_1f_avec",  "Pleine propriété 1 façade avec raccordements | ملكية تامة 1 واجهة مع توصيلات"),
        ("pp_2f_sans",  "Pleine propriété 2 façades sans raccordements | ملكية تامة 2 واجهة بدون توصيلات"),
        ("pp_1f_sans",  "Pleine propriété 1 façade sans raccordements | ملكية تامة 1 واجهة بدون توصيلات"),
        ("indivision",  "Dans l'indivision | في الشياع"),
        ("industriel",  "Industriel | صناعي"),
        # Terrains Agricoles
        ("potentialite_elevee",  "Potentialité élevée | إمكانية عالية"),
        ("potentialite_moyenne", "Potentialité moyenne | إمكانية متوسطة"),
        ("potentialite_faible",  "Potentialité faible | إمكانية ضعيفة"),
    ]

    nature = models.ForeignKey(
        NatureImmeuble, on_delete=models.CASCADE,
        related_name="caracteristiques", verbose_name="طبيعة العقار"
    )
    key = models.CharField(
        max_length=30, choices=CARAC_CHOICES,
        verbose_name="المفتاح"
    )
    name_ar = models.CharField(max_length=200, verbose_name="الاسم بالعربية")
    name_fr = models.CharField(max_length=200, verbose_name="الاسم بالفرنسية")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="الترتيب")

    class Meta:
        verbose_name = "خاصية"
        verbose_name_plural = "الخصائص"
        ordering = ["nature", "order"]
        unique_together = [("nature", "key")]

    def __str__(self):
        return f"{self.nature.name_fr} → {self.name_fr}"


# properties/models_valuation.py - جزء ValuationRange فقط

class ValuationRange(models.Model):
    """
    نطاق التقييم النهائي (Fourchette d'évaluation)
    يجمع بين جميع المعايير: الولاية + البلدية + المنطقة + طبيعة العقار + الخاصية
    """
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE, related_name='valuations', verbose_name="الولاية")
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, related_name='valuations', verbose_name="البلدية")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='valuations', verbose_name="المنطقة")
    nature = models.ForeignKey(NatureImmeuble, on_delete=models.CASCADE, related_name='valuations',
                               verbose_name="طبيعة العقار")
    caracteristique = models.ForeignKey(Caracteristique, on_delete=models.CASCADE, related_name='valuations',
                                        verbose_name="الخاصية")

    min_price_per_sqm = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)],
                                            verbose_name="الحد الأدنى (دج/م²)")
    max_price_per_sqm = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)],
                                            verbose_name="الحد الأقصى (دج/م²)")

    reference_year = models.IntegerField(default=2024, verbose_name="سنة المرجع")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "نطاق تقييم"
        verbose_name_plural = "نطاقات التقييم"
        unique_together = ['wilaya', 'commune', 'zone', 'nature', 'caracteristique']
        indexes = [
            models.Index(fields=['wilaya', 'commune']),
            models.Index(fields=['zone', 'nature']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.wilaya.name_ar} - {self.commune.name_ar} - {self.zone.name_ar} - {self.nature.name_ar}: {self.min_price_per_sqm} - {self.max_price_per_sqm} دج/م²"