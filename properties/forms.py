# properties/forms.py
# -*- coding: utf-8 -*-
"""
نماذج تطبيق العقارات - مصممة بطريقة عصرية واحترافية.
تشمل نماذج إدارة العقارات، التقييم العقاري، التواصل، والصور.
"""

from django import forms
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from .models import (
    Property, PropertyImage, Review, Category
)
from .models_valuation import (
    Wilaya, Commune, Zone, NatureImmeuble, Caracteristique, ValuationRange
)


class PropertyForm(forms.ModelForm):
    """
    نموذج إضافة / تعديل عقار.
    يحتوي على تحسينات في ربط البلديات، والتحقق من صحة البيانات، وتنسيق عصري.
    """

    class Meta:
        model = Property
        fields = [
            'title', 'description', 'price', 'area_sqm',
            'property_type', 'listing_type', 'bedrooms', 'bathrooms',
            'wilaya', 'commune', 'address', 'latitude', 'longitude',
            'category', 'cpc', 'is_cpc_active',
            'is_active', 'is_featured', 'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'latitude': forms.NumberInput(
                attrs={'step': 'any', 'class': 'form-control', 'placeholder': 'مثال: 36.7538'}),
            'longitude': forms.NumberInput(
                attrs={'step': 'any', 'class': 'form-control', 'placeholder': 'مثال: 3.0588'}),
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'مثال: شقة فاخرة في الجزائر العاصمة'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'السعر بالدينار الجزائري'}),
            'area_sqm': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'المساحة بالمتر المربع'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'عدد غرف النوم'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'عدد الحمامات'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'العنوان الكامل'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'listing_type': forms.Select(attrs={'class': 'form-select'}),
            'wilaya': forms.Select(attrs={'class': 'form-select', 'id': 'id_wilaya'}),
            'commune': forms.Select(attrs={'class': 'form-select', 'id': 'id_commune'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'cpc': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'سعر النقرة'}),
            'is_cpc_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'title': _('عنوان العقار'),
            'description': _('الوصف'),
            'price': _('السعر (دج)'),
            'area_sqm': _('المساحة (م²)'),
            'property_type': _('نوع العقار'),
            'listing_type': _('نوع العملية'),
            'bedrooms': _('غرف النوم'),
            'bathrooms': _('الحمامات'),
            'wilaya': _('الولاية'),
            'commune': _('البلدية'),
            'address': _('العنوان التفصيلي'),
            'latitude': _('خط العرض'),
            'longitude': _('خط الطول'),
            'category': _('الفئة'),
            'cpc': _('سعر النقرة (دج)'),
            'is_cpc_active': _('تفعيل الإعلان المدفوع (CPC)'),
            'is_active': _('نشط'),
            'is_featured': _('مميز'),
            'image': _('الصورة الرئيسية'),
        }
        help_texts = {
            'cpc': _('تكلفة النقرة الواحدة على إعلان العقار (تُستخدم فقط مع تفعيل الإعلان المدفوع).'),
            'latitude': _('يمكنك الحصول على الإحداثيات من خرائط Google.'),
            'longitude': _('يمكنك الحصول على الإحداثيات من خرائط Google.'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ربط البلديات بالولاية المختارة
        if 'wilaya' in self.data and self.data.get('wilaya'):
            try:
                wilaya_id = int(self.data.get('wilaya'))
                self.fields['commune'].queryset = Commune.objects.filter(wilaya_id=wilaya_id).order_by('name_ar')
            except (ValueError, TypeError):
                self.fields['commune'].queryset = Commune.objects.none()
        elif self.instance and self.instance.pk and self.instance.wilaya:
            self.fields['commune'].queryset = Commune.objects.filter(wilaya=self.instance.wilaya).order_by('name_ar')
        else:
            self.fields['commune'].queryset = Commune.objects.none()

        # جعل بعض الحقول اختيارية
        self.fields['bedrooms'].required = False
        self.fields['bathrooms'].required = False
        self.fields['category'].required = False
        self.fields['cpc'].required = False
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['image'].required = False

        # إضافة فئة الـ CSS للتحقق من صحة الحقول (للتكامل مع Bootstrap)
        for field_name, field in self.fields.items():
            if 'form-control' not in field.widget.attrs.get('class', ''):
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' form-control'
                else:
                    field.widget.attrs['class'] = 'form-control'

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError(_('السعر يجب أن يكون أكبر من صفر.'))
        return price

    def clean_area_sqm(self):
        area = self.cleaned_data.get('area_sqm')
        if area is not None and area <= 0:
            raise forms.ValidationError(_('المساحة يجب أن تكون أكبر من صفر.'))
        return area

    def clean(self):
        cleaned_data = super().clean()
        is_cpc_active = cleaned_data.get('is_cpc_active')
        cpc = cleaned_data.get('cpc')
        if is_cpc_active and (cpc is None or cpc <= 0):
            self.add_error('cpc', _('عند تفعيل الإعلان المدفوع، يجب أن يكون سعر النقرة أكبر من صفر.'))
        return cleaned_data


class PropertyImageForm(forms.ModelForm):
    """نموذج رفع الصور الإضافية للعقار"""

    class Meta:
        model = PropertyImage
        fields = ['image', 'is_main', 'order']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'ترتيب الصورة'}),
        }
        labels = {
            'image': _('الصورة'),
            'is_main': _('صورة رئيسية'),
            'order': _('ترتيب العرض'),
        }


class ReviewForm(forms.ModelForm):
    """نموذج إضافة تقييم لعقار"""

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}, choices=[(i, f"{i} نجوم") for i in range(1, 6)]),
            'comment': forms.Textarea(
                attrs={'rows': 4, 'class': 'form-control', 'placeholder': _('شارك تجربتك مع هذا العقار...')}),
        }
        labels = {
            'rating': _('التقييم'),
            'comment': _('التعليق'),
        }


class ContactForm(forms.Form):
    """نموذج التواصل مع وكيل العقار"""
    name = forms.CharField(
        max_length=100,
        label=_("الاسم الكامل"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('أدخل اسمك الكامل')})
    )
    email = forms.EmailField(
        label=_("البريد الإلكتروني"),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@domain.com'})
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        label=_("رقم الهاتف (اختياري)"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('05xxxxxxxx')})
    )
    message = forms.CharField(
        label=_("الرسالة"),
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': _('اكتب رسالتك هنا...')})
    )


# ============================================================================
# نماذج التقييم العقاري المتقدمة
# ============================================================================

class ValuationSearchForm(forms.Form):
    """
    نموذج البحث عن التقييم العقاري.
    يدعم التقسيم الكامل: Wilaya + Commune + Zone + Nature + Caractéristique
    """
    wilaya = forms.ModelChoiceField(
        queryset=Wilaya.objects.all(),
        required=True,
        label=_("الولاية / Wilaya"),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'valuation_wilaya'})
    )
    commune = forms.ModelChoiceField(
        queryset=Commune.objects.none(),
        required=True,
        label=_("البلدية / Commune"),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'valuation_commune'})
    )
    zone = forms.ModelChoiceField(
        queryset=Zone.objects.all(),
        required=True,
        label=_("المنطقة / Zone"),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'valuation_zone'})
    )
    nature = forms.ModelChoiceField(
        queryset=NatureImmeuble.objects.all(),
        required=True,
        label=_("طبيعة العقار / Nature du bien"),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'valuation_nature'})
    )
    characteristic = forms.ModelChoiceField(
        queryset=Caracteristique.objects.none(),
        required=True,
        label=_("الخاصية / Caractéristique"),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'valuation_characteristic'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ترتيب الخيارات - تعديل: إزالة order_by('order') لأن Zone لا يحتوي على order
        self.fields['wilaya'].queryset = Wilaya.objects.all().order_by('code')
        self.fields['zone'].queryset = Zone.objects.all().order_by('key')  # استخدم key بدلاً من order
        self.fields['nature'].queryset = NatureImmeuble.objects.all().order_by('key')  # استخدم key بدلاً من order

        # في البداية، اجعل حقول commune و characteristic فارغة
        self.fields['commune'].queryset = Commune.objects.none()
        self.fields['characteristic'].queryset = Caracteristique.objects.none()

        # إذا كان هناك بيانات مرسلة (POST)
        if self.is_bound:
            wilaya_id = self.data.get('wilaya')
            if wilaya_id and str(wilaya_id).isdigit():
                self.fields['commune'].queryset = Commune.objects.filter(
                    wilaya_id=int(wilaya_id)
                ).order_by('name_ar')

            nature_id = self.data.get('nature')
            if nature_id and str(nature_id).isdigit():
                self.fields['characteristic'].queryset = Caracteristique.objects.filter(
                    nature_id=int(nature_id)
                ).order_by('order')  # Caracteristique لديه حقل order


# اسم مستعار للتوافق
ValuationForm = ValuationSearchForm