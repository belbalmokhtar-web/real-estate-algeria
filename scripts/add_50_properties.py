#!/usr/bin/env python
# scripts/add_50_properties.py
import os
import sys
import django
import random

# إعداد Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from properties.models import Property

User = get_user_model()

# بيانات الولايات والبلديات
LOCATIONS = [
    ('الجزائر',
     ['الجزائر الوسطى', 'سيدي امحمد', 'القبة', 'الحراش', 'براقي', 'باب الوادي', 'بوزريعة', 'بن عكنون', 'الرويبة',
      'عين طاية']),
    ('وهران',
     ['وهران', 'بئر الجير', 'السانية', 'عين الترك', 'قديل', 'بوتليليس', 'مسرغين', 'أرزيو', 'الكرمة', 'سيدي الشحمي']),
    ('قسنطينة',
     ['قسنطينة', 'الخروب', 'عين السمارة', 'زيغود يوسف', 'ابن زياد', 'ديدوش مراد', 'حامة بوزيان', 'بني حميدان']),
    ('عنابة', ['عنابة', 'البوني', 'الحجار', 'سرايدي', 'برحال', 'شطايبي', 'عين الباردة', 'تريعات']),
    ('بجاية', ['بجاية', 'أوقاس', 'القل', 'برباشة', 'تيمزريت', 'أميزور', 'فرعون', 'تازملت', 'صدوق', 'تيتشي']),
    ('تيزي وزو',
     ['تيزي وزو', 'عين الحمام', 'ذراع بن خدة', 'بوزقن', 'واقنون', 'أربعاء ناث إيراثن', 'عزازقة', 'بوغني', 'مقلع',
      'تيزي راشد']),
    ('بسكرة', ['بسكرة', 'طولقة', 'سيدي عقبة', 'أورلال', 'الوطاية', 'جمورة', 'القنطرة', 'ليشانة', 'فوغالة', 'أوماش']),
    ('باتنة', ['باتنة', 'بريكة', 'عين التوتة', 'مروانة', 'نقاوس', 'أريس', 'تازولت', 'المعذر', 'سريانة', 'قصر بلزمة']),
    ('سطيف',
     ['سطيف', 'العلمة', 'عين آزال', 'بابور', 'بوعنداس', 'قجال', 'صالح باي', 'حمام قرقور', 'بن عزيز', 'بئر العرش']),
    ('البليدة',
     ['البليدة', 'بوفاريك', 'بوقرة', 'الأربعاء', 'موزاية', 'العفرون', 'مفتاح', 'بن خليل', 'الشبلي', 'الصومعة']),
]

# عناوين العقارات حسب النوع
APARTMENT_TITLES = [
    'شقة عصرية', 'شقة فاخرة', 'شقة مفروشة', 'شقة سكنية', 'شقة عائلية', 'شقة استوديو',
    'شقة بدوبلكس', 'شقة مطلة على البحر', 'شقة قريبة من الخدمات', 'شقة هادئة',
    'شقة جديدة', 'شقة راقية', 'شقة اقتصادية', 'شقة واسعة', 'شقة مميزة'
]

HOUSE_TITLES = [
    'منزل مستقل', 'فيلا منفردة', 'منزل تقليدي', 'منزل عصري', 'فيلا راقية',
    'منزل عائلي', 'فيلا مع مسبح', 'منزل مع حديقة', 'فيلا فاخرة', 'منزل ريفي',
    'فيلا مطلة', 'منزل دورين', 'فيلا عصرية', 'منزل كبير', 'فيلا سكنية'
]

LAND_TITLES = [
    'أرض سكنية', 'قطعة أرض', 'أرض تجارية', 'أرض زراعية', 'أرض استثمارية',
    'أرض للبناء', 'أرض مميزة', 'أرض في موقع حيوي', 'أرض قريبة من الطريق'
]

COMMERCIAL_TITLES = [
    'محل تجاري', 'مكتب للإيجار', 'متجر', 'مستودع', 'مركز تجاري صغير',
    'محل في شارع رئيسي', 'مكتب مجهز', 'مساحة تجارية', 'محل تجاري مميز'
]

# أنواع العقارات
PROPERTY_TYPES = ['apartment', 'house', 'villa', 'land', 'commercial']

# الأوصاف
DESCRIPTIONS = [
    "عقار مميز في موقع رائع، قريب من جميع المرافق والخدمات.",
    "فرصة استثمارية لا تعوض، عقار بمواصفات عالية الجودة.",
    "منزل الأحلام بمساحات واسعة وتصميم عصري.",
    "موقع هادئ ومريح، مناسب للعائلات.",
    "عقار جديد بالكامل، تشطيبات فاخرة.",
    "إطلالة رائعة وتهوية ممتازة.",
    "قريب من المدارس والمستشفيات والمواصلات.",
]


def get_random_title(property_type):
    """الحصول على عنوان عشوائي حسب نوع العقار"""
    if property_type in ['apartment']:
        return random.choice(APARTMENT_TITLES)
    elif property_type in ['house', 'villa']:
        return random.choice(HOUSE_TITLES)
    elif property_type == 'land':
        return random.choice(LAND_TITLES)
    else:
        return random.choice(COMMERCIAL_TITLES)


def get_price(property_type, listing_type):
    """حساب سعر عشوائي مناسب"""
    if listing_type == 'sale':
        if property_type == 'apartment':
            return random.randint(8000000, 45000000)
        elif property_type in ['house', 'villa']:
            return random.randint(25000000, 120000000)
        elif property_type == 'land':
            return random.randint(5000000, 35000000)
        else:
            return random.randint(15000000, 60000000)
    else:  # rent
        if property_type == 'apartment':
            return random.randint(30000, 150000)
        elif property_type in ['house', 'villa']:
            return random.randint(60000, 250000)
        elif property_type == 'land':
            return random.randint(10000, 50000)
        else:
            return random.randint(40000, 120000)


def create_50_properties():
    """إنشاء 50 عقاراً متنوعاً"""
    print("=" * 60)
    print("🚀 بدء إنشاء 50 عقاراً متنوعاً")
    print("=" * 60)

    # الحصول على مستخدم (إنشاؤه إذا لم يوجد)
    user, created = User.objects.get_or_create(
        username='demo',
        defaults={
            'email': 'demo@example.com',
            'is_active': True,
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
        print("✅ تم إنشاء المستخدم التجريبي: demo / demo123")

    # حذف العقارات القديمة (اختياري)
    # Property.objects.filter(owner=user).delete()

    created_count = 0
    skipped_count = 0

    for i in range(50):
        # اختيار نوع العقار
        property_type = random.choice(PROPERTY_TYPES)
        listing_type = random.choice(['sale', 'rent'])

        # اختيار موقع عشوائي
        wilaya, communes = random.choice(LOCATIONS)
        commune = random.choice(communes)

        # إنشاء عنوان فريد
        title = f"{get_random_title(property_type)} في {commune}"

        # التأكد من عدم وجود عنوان مكرر
        if Property.objects.filter(title=title).exists():
            title = f"{title} {i + 1}"

        # حساب المساحة
        if property_type in ['apartment', 'commercial']:
            area_sqm = random.randint(60, 200)
        elif property_type in ['house', 'villa']:
            area_sqm = random.randint(150, 400)
        else:  # land
            area_sqm = random.randint(200, 800)

        # عدد الغرف
        if property_type == 'apartment':
            bedrooms = random.randint(1, 4)
            bathrooms = random.randint(1, 2)
        elif property_type in ['house', 'villa']:
            bedrooms = random.randint(3, 6)
            bathrooms = random.randint(2, 4)
        else:
            bedrooms = 0
            bathrooms = random.randint(0, 1)

        # السعر
        price = get_price(property_type, listing_type)

        # هل العقار مميز؟
        is_featured = random.choice([True, False, False, False])  # 25% مميز

        try:
            property_obj = Property.objects.create(
                title=title,
                description=random.choice(DESCRIPTIONS),
                property_type=property_type,
                listing_type=listing_type,
                price=price,
                area_sqm=area_sqm,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                wilaya=wilaya,
                commune=commune,
                address=f"شارع {random.randint(1, 100)}، حي {random.choice(['السلام', 'النهضة', 'الفلاح', 'الأمل', 'الزهور', 'الشهداء', 'الرياض', 'النخيل'])}",
                is_active=True,
                is_featured=is_featured,
                is_verified=random.choice([True, True, True, False]),  # 75% موثقة
                owner=user,
                views_count=random.randint(0, 300),
            )
            created_count += 1

            # عرض التقدم
            type_ar = {'apartment': 'شقة', 'house': 'منزل', 'villa': 'فيلا', 'land': 'أرض', 'commercial': 'تجاري'}.get(
                property_type, 'عقار')
            listing_ar = 'للبيع' if listing_type == 'sale' else 'للإيجار'
            print(f"   {created_count:2d}. {type_ar} | {listing_ar} | {title[:35]} | {price:,} دج")

        except Exception as e:
            skipped_count += 1
            print(f"   ❌ خطأ في العقار {i + 1}: {e}")

    # عرض الملخص
    print("\n" + "=" * 60)
    print("📊 ملخص العقارات المضافة:")
    print("=" * 60)
    print(f"   ✅ العقارات المضافة: {created_count}")
    print(f"   ⚠️ العقارات المتخطية: {skipped_count}")
    print(f"   📍 إجمالي العقارات في النظام: {Property.objects.filter(is_active=True).count()}")

    # إحصائيات حسب النوع
    print("\n📈 إحصائيات حسب نوع العقار:")
    for p_type in PROPERTY_TYPES:
        count = Property.objects.filter(property_type=p_type).count()
        type_ar = {'apartment': 'شقة', 'house': 'منزل', 'villa': 'فيلا', 'land': 'أرض', 'commercial': 'تجاري'}.get(
            p_type, p_type)
        if count > 0:
            print(f"   - {type_ar}: {count} عقار")

    print("\n" + "=" * 60)
    print("🎉 تم إنشاء 50 عقاراً متنوعاً بنجاح!")
    print("\n🔑 بيانات الدخول:")
    print("-" * 40)
    print("المستخدم: demo  | كلمة المرور: demo123")
    print("-" * 40)


if __name__ == '__main__':
    create_50_properties()