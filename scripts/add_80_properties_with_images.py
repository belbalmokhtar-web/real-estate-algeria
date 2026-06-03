#!/usr/bin/env python
# scripts/add_80_properties_with_images.py
import os
import sys
import django
import random
import urllib.request
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

# إعداد Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from properties.models import Property
from django.core.files.base import ContentFile

User = get_user_model()

# ========== بيانات الولايات والبلديات ==========
LOCATIONS = [
    ('الجزائر', ['الجزائر الوسطى', 'سيدي امحمد', 'القبة', 'الحراش', 'براقي', 'باب الوادي', 'بوزريعة', 'بن عكنون']),
    ('وهران', ['وهران', 'بئر الجير', 'السانية', 'عين الترك', 'قديل', 'بوتليليس', 'مسرغين', 'أرزيو']),
    ('قسنطينة', ['قسنطينة', 'الخروب', 'عين السمارة', 'زيغود يوسف', 'ابن زياد', 'ديدوش مراد', 'حامة بوزيان']),
    ('عنابة', ['عنابة', 'البوني', 'الحجار', 'سرايدي', 'برحال', 'شطايبي', 'عين الباردة']),
    ('بجاية', ['بجاية', 'أوقاس', 'القل', 'برباشة', 'تيمزريت', 'أميزور', 'فرعون', 'تازملت']),
    ('تيزي وزو', ['تيزي وزو', 'عين الحمام', 'ذراع بن خدة', 'بوزقن', 'واقنون', 'أربعاء ناث إيراثن', 'عزازقة']),
    ('بسكرة', ['بسكرة', 'طولقة', 'سيدي عقبة', 'أورلال', 'الوطاية', 'جمورة', 'القنطرة']),
    ('باتنة', ['باتنة', 'بريكة', 'عين التوتة', 'مروانة', 'نقاوس', 'أريس', 'تازولت']),
    ('سطيف', ['سطيف', 'العلمة', 'عين آزال', 'بابور', 'بوعنداس', 'قجال', 'صالح باي']),
    ('البليدة', ['البليدة', 'بوفاريك', 'بوقرة', 'الأربعاء', 'موزاية', 'العفرون', 'مفتاح']),
    ('تيبازة', ['تيبازة', 'القليعة', 'حجوط', 'شرشال', 'دواودة', 'بوعمران', 'الداموس']),
    ('بومرداس', ['بومرداس', 'بودواو', 'برج منايل', 'دلس', 'يسر', 'الثنية', 'زموري']),
]

# ========== عناوين العقارات ==========
TITLES = {
    'apartment': [
        'شقة فاخرة مع إطلالة', 'شقة عصرية مفروشة', 'شقة سكنية هادئة',
        'شقة راقية بموقع مميز', 'شقة جديدة كلياً', 'شقة عائلية واسعة',
        'شقة استوديو عصرية', 'شقة بدوبلكس فاخرة', 'شقة مطلة على البحر',
        'شقة قريبة من الخدمات', 'شقة هادئة في وسط المدينة', 'شقة اقتصادية',
        'شقة سكنية مفروشة', 'شقة رائعة للإيجار', 'شقة فاخرة للبيع'
    ],
    'house': [
        'منزل مستقل مع حديقة', 'منزل عصري', 'منزل تقليدي',
        'منزل عائلي كبير', 'منزل ريفي جميل', 'منزل دورين فاخر',
        'منزل مع تراس', 'منزل هادئ في ضاحية', 'منزل مميز للبيع'
    ],
    'villa': [
        'فيلا فاخرة مع مسبح', 'فيلا ساحلية', 'فيلا عصرية',
        'فيلا خاصة مع حديقة', 'فيلا مطلة على البحر', 'فيلا راقية جداً',
        'فيلا فاخرة للبيع', 'فيلا سكنية مميزة', 'فيلا مع مرآب'
    ],
    'land': [
        'أرض سكنية مميزة', 'قطعة أرض تجارية', 'أرض زراعية واسعة',
        'أرض للبناء', 'أرض استثمارية', 'أرض في موقع حيوي',
        'أرض قرب الطريق', 'قطعة أرض فاخرة', 'أرض سكنية للبيع'
    ],
    'commercial': [
        'محل تجاري مميز', 'مكتب للإيجار', 'متجر في شارع رئيسي',
        'مستودع كبير', 'مركز تجاري صغير', 'محل تجاري للبيع',
        'مكتب مجهز بالكامل', 'مساحة تجارية مميزة', 'عقار تجاري استثماري'
    ]
}

# ========== الأوصاف ==========
DESCRIPTIONS = [
    """عقار مميز يقع في موقع حيوي، يتميز بتصميم عصري ومساحات واسعة. 
    يتمتع العقار بإطلالة رائعة وموقعه قريب من جميع المرافق والخدمات.""",

    """فرصة استثمارية لا تعوض. عقار بمواصفات عالية الجودة، تشطيبات فاخرة، 
    وموقع استراتيجي قريب من المدارس والمستشفيات والمراكز التجارية.""",

    """عقار مثالي للعائلات، يتميز بالهدوء والراحة، محاط بالمساحات الخضراء، 
    وقريب من جميع وسائل الراحة والترفيه.""",

    """عقار جديد بالكامل، تشطيبات فاخرة، تصميم عصري، 
    إضاءة طبيعية ممتازة، وتهوية جيدة.""",

    """موقع مميز وعقار استثماري، مناسب للشركات والمكاتب، 
    قريب من المواصلات والخدمات العامة.""",
]


# ========== دوال مساعدة ==========
def download_image(url):
    """تحميل صورة من رابط"""
    try:
        result = urllib.request.urlretrieve(url)
        return result[0]
    except:
        return None


def get_random_image(property_type):
    """الحصول على صورة عشوائية حسب نوع العقار"""
    # روابط صور وهمية (صور مجانية من loremflick)
    # ملاحظة: هذه روابط تجريبية، يمكن استبدالها بروابط حقيقية

    image_categories = {
        'apartment': ['apartment', 'flat', 'condo'],
        'house': ['house', 'home', 'residence'],
        'villa': ['villa', 'luxury', 'mansion'],
        'land': ['land', 'field', 'property'],
        'commercial': ['office', 'shop', 'building']
    }

    # أبعاد الصورة
    width = random.choice([800, 1024, 1200])
    height = random.choice([600, 768, 800])

    # استخدام placeholder image (للتجربة فقط)
    # في الإنتاج، استخدم صوراً حقيقية من مجلد media
    return None  # سنستخدم صور placeholder محلية


def get_placeholder_image(property_type, index):
    """إنشاء صورة placeholder محلية"""
    from PIL import Image, ImageDraw, ImageFont

    # أبعاد الصورة
    width, height = 800, 500

    # ألوان مختلفة حسب نوع العقار
    colors = {
        'apartment': (52, 152, 219),  # أزرق
        'house': (46, 204, 113),  # أخضر
        'villa': (155, 89, 182),  # بنفسجي
        'land': (241, 196, 15),  # أصفر
        'commercial': (230, 126, 34),  # برتقالي
    }

    color = colors.get(property_type, (52, 152, 219))

    # إنشاء صورة
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)

    # إضافة نص
    text = f"Image {index}"
    text_bbox = draw.textbbox((0, 0), text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text((x, y), text, fill='white')

    # حفظ الصورة
    temp_file = NamedTemporaryFile(delete=True, suffix='.png')
    img.save(temp_file, format='PNG')
    temp_file.flush()

    return temp_file


def get_price(property_type, listing_type):
    """حساب سعر عشوائي مناسب"""
    if listing_type == 'sale':
        prices = {
            'apartment': (5000000, 35000000),
            'house': (15000000, 70000000),
            'villa': (30000000, 150000000),
            'land': (2000000, 30000000),
            'commercial': (8000000, 60000000)
        }
    else:  # rent
        prices = {
            'apartment': (25000, 120000),
            'house': (50000, 180000),
            'villa': (80000, 300000),
            'land': (10000, 50000),
            'commercial': (30000, 150000)
        }

    min_price, max_price = prices.get(property_type, (1000000, 10000000))
    return random.randint(min_price, max_price)


def get_area(property_type):
    """حساب مساحة عشوائية"""
    areas = {
        'apartment': (60, 180),
        'house': (150, 350),
        'villa': (250, 500),
        'land': (200, 1000),
        'commercial': (50, 200)
    }
    min_area, max_area = areas.get(property_type, (50, 200))
    return random.randint(min_area, max_area)


def get_rooms(property_type):
    """عدد الغرف والحمامات"""
    if property_type == 'apartment':
        return random.randint(1, 4), random.randint(1, 2)
    elif property_type in ['house', 'villa']:
        return random.randint(3, 6), random.randint(2, 4)
    else:
        return 0, random.randint(0, 1)


def create_80_properties():
    """إنشاء 80 عقاراً مع صور"""
    print("=" * 60)
    print("🚀 بدء إنشاء 80 عقاراً متنوعاً مع صور")
    print("=" * 60)

    # إنشاء المستخدم التجريبي
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
        print("✅ تم إنشاء المستخدم: demo / demo123")

    # حذف العقارات القديمة (اختياري - علق إذا أردت الاحتفاظ بها)
    # Property.objects.filter(owner=user).delete()
    # print("🗑️ تم حذف العقارات القديمة")

    created_count = 0
    error_count = 0

    for i in range(80):
        # اختيار نوع العقار
        property_type = random.choice(list(TITLES.keys()))
        listing_type = random.choice(['sale', 'rent'])

        # اختيار موقع عشوائي
        wilaya, communes = random.choice(LOCATIONS)
        commune = random.choice(communes)

        # إنشاء عنوان فريد
        base_title = random.choice(TITLES[property_type])
        title = f"{base_title} في {commune}"

        # التأكد من عدم التكرار
        if Property.objects.filter(title=title).exists():
            title = f"{base_title} {i + 1} - {commune}"

        # حساب التفاصيل
        price = get_price(property_type, listing_type)
        area_sqm = get_area(property_type)
        bedrooms, bathrooms = get_rooms(property_type)

        # هل العقار مميز؟
        is_featured = (i % 5 == 0)  # كل 5 عقارات عقار مميز
        is_verified = (i % 4 != 0)  # 75% موثقة

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
                address=f"شارع {random.randint(1, 100)}، حي {random.choice(['السلام', 'النهضة', 'الفلاح', 'الأمل', 'الزهور', 'الشهداء', 'الرياض', 'النخيل', 'الأندلس', 'المروج'])}",
                is_active=True,
                is_featured=is_featured,
                is_verified=is_verified,
                owner=user,
                views_count=random.randint(0, 500),
            )

            # إضافة صورة وهمية
            try:
                from django.core.files import File

                # إنشاء صورة placeholder
                temp_file = get_placeholder_image(property_type, i + 1)
                property_obj.image.save(f'property_{property_obj.id}.png', File(temp_file))
                temp_file.close()
            except Exception as img_error:
                print(f"   ⚠️ لم نتمكن من إضافة صورة للعقار {i + 1}: {img_error}")

            created_count += 1

            # عرض التقدم
            type_ar = {'apartment': '🏢 شقة', 'house': '🏠 منزل', 'villa': '🏰 فيلا', 'land': '🗺️ أرض',
                       'commercial': '🏪 تجاري'}.get(property_type, 'عقار')
            listing_ar = '💰 للبيع' if listing_type == 'sale' else '📝 للإيجار'
            featured_star = '⭐' if is_featured else '  '

            print(f"   {created_count:2d}. {featured_star} {type_ar} | {listing_ar} | {title[:30]} | {price:,} دج")

        except Exception as e:
            error_count += 1
            print(f"   ❌ خطأ في العقار {i + 1}: {e}")

    # عرض الملخص
    print("\n" + "=" * 60)
    print("📊 ملخص العقارات المضافة:")
    print("=" * 60)
    print(f"   ✅ العقارات المضافة بنجاح: {created_count}")
    print(f"   ❌ العقارات التي فشلت: {error_count}")
    print(f"   📍 إجمالي العقارات في النظام: {Property.objects.filter(is_active=True).count()}")

    # إحصائيات حسب النوع
    print("\n📈 إحصائيات حسب نوع العقار:")
    type_stats = {}
    for p_type in TITLES.keys():
        count = Property.objects.filter(property_type=p_type).count()
        if count > 0:
            type_ar = {'apartment': 'شقة', 'house': 'منزل', 'villa': 'فيلا', 'land': 'أرض', 'commercial': 'تجاري'}.get(
                p_type, p_type)
            print(f"   - {type_ar}: {count} عقار")

    # إحصائيات حسب العملية
    print("\n📈 إحصائيات حسب نوع العملية:")
    sale_count = Property.objects.filter(listing_type='sale').count()
    rent_count = Property.objects.filter(listing_type='rent').count()
    print(f"   - للبيع: {sale_count} عقار")
    print(f"   - للإيجار: {rent_count} عقار")

    # إحصائيات حسب الولايات
    print("\n📈 الولايات الأكثر عقارات:")
    from django.db.models import Count
    top_wilayas = Property.objects.values('wilaya').annotate(total=Count('id')).order_by('-total')[:5]
    for w in top_wilayas:
        print(f"   - {w['wilaya']}: {w['total']} عقار")

    print("\n" + "=" * 60)
    print("🎉 تم إنشاء 80 عقاراً بنجاح!")
    print("\n🔑 بيانات الدخول:")
    print("-" * 40)
    print("المستخدم: demo  | كلمة المرور: demo123")
    print("-" * 40)


if __name__ == '__main__':
    create_80_properties()