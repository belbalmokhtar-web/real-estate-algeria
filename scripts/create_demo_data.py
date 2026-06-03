#!/usr/bin/env python
# scripts/create_demo_data.py
import os
import sys
import django
from datetime import datetime, timedelta
import random

# إعداد Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from properties.models import Property, Wilaya, Commune, Category, PropertyImage
from accounts.models import AgentProfile, DeveloperProfile

User = get_user_model()

# ========== بيانات وهمية ==========

# أنواع العقارات
PROPERTY_TYPES = ['apartment', 'house', 'villa', 'land', 'commercial']
PROPERTY_TYPES_AR = ['شقة', 'منزل', 'فيلا', 'أرض', 'محل تجاري']

# أنواع العمليات
LISTING_TYPES = ['sale', 'rent']
LISTING_TYPES_AR = ['للبيع', 'للإيجار']

# عناوين وهمية للعقارات
TITLES = {
    'apartment': [
        'شقة فاخرة مع إطلالة', 'شقة عصرية مفروشة', 'شقة سكنية هادئة',
        'شقة راقية بموقع مميز', 'شقة جديدة كلياً', 'شقة عائلية واسعة'
    ],
    'house': [
        'منزل مستقل مع حديقة', 'فيلا راقية', 'منزل تقليدي',
        'منزل عصري', 'منزل عائلي كبير', 'فيلا مع مسبح'
    ],
    'villa': [
        'فيلا فاخرة مع مسبح', 'فيلا ساحلية', 'فيلا عصرية',
        'فيلا خاصة', 'فيلا مع حديقة واسعة', 'فيلا مطلة على البحر'
    ],
    'land': [
        'أرض سكنية', 'قطعة أرض تجارية', 'أرض زراعية',
        'أرض للبناء', 'أرض استثمارية', 'أرض في موقع مميز'
    ],
    'commercial': [
        'محل تجاري', 'مكتب للإيجار', 'متجر في شارع رئيسي',
        'مستودع', 'مركز تجاري', 'عقار تجاري'
    ]
}

# أوصاف وهمية
DESCRIPTIONS = [
    """عقار مميز يقع في موقع حيوي، يتميز بتصميم عصري ومساحات واسعة. 
    يتمتع العقار بإطلالة رائعة وموقعه قريب من جميع المرافق والخدمات.""",

    """فرصة لا تعوض للاستثمار. عقار بمواصفات عالية الجودة، تشطيبات فاخرة، 
    وموقع استراتيجي قريب من المدارس والمستشفيات والمراكز التجارية.""",

    """عقار مثالي للعائلات، يتميز بالهدوء والراحة، محاط بالمساحات الخضراء، 
    وقريب من جميع وسائل الراحة والترفيه.""",
]


def create_demo_users():
    """إنشاء مستخدمين تجريبيين"""
    print("📌 إنشاء المستخدمين التجريبيين...")

    users_data = [
        {'username': 'admin', 'email': 'admin@example.com', 'password': 'admin123', 'is_staff': True,
         'is_superuser': True, 'role': 'user', 'first_name': 'مدير', 'last_name': 'النظام'},
        {'username': 'agent1', 'email': 'agent1@example.com', 'password': 'agent123', 'role': 'agent',
         'first_name': 'أحمد', 'last_name': 'محمد', 'company': 'وكالة الأمان العقارية'},
        {'username': 'agent2', 'email': 'agent2@example.com', 'password': 'agent123', 'role': 'agent',
         'first_name': 'سارة', 'last_name': 'بن عمر', 'company': 'وكالة النخبة العقارية'},
        {'username': 'developer1', 'email': 'developer1@example.com', 'password': 'dev123', 'role': 'developer',
         'first_name': 'كريم', 'last_name': 'حموش', 'company': 'شركة الأبراج العقارية'},
        {'username': 'user1', 'email': 'user1@example.com', 'password': 'user123', 'role': 'user', 'first_name': 'محمد',
         'last_name': 'خالد'},
        {'username': 'user2', 'email': 'user2@example.com', 'password': 'user123', 'role': 'user',
         'first_name': 'فاطمة', 'last_name': 'زهرة'},
        {'username': 'user3', 'email': 'user3@example.com', 'password': 'user123', 'role': 'user', 'first_name': 'علي',
         'last_name': 'بن أحمد'},
        {'username': 'user4', 'email': 'user4@example.com', 'password': 'user123', 'role': 'user', 'first_name': 'نورا',
         'last_name': 'سالم'},
        {'username': 'agent3', 'email': 'agent3@example.com', 'password': 'agent123', 'role': 'agent',
         'first_name': 'سمير', 'last_name': 'رابح', 'company': 'وكالة المستقبل العقارية'},
    ]

    created_users = []

    with transaction.atomic():
        for user_data in users_data:
            try:
                # حذف المستخدم إذا كان موجوداً مسبقاً
                User.objects.filter(username=user_data['username']).delete()

                # إنشاء المستخدم
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    is_staff=user_data.get('is_staff', False),
                    is_superuser=user_data.get('is_superuser', False),
                    role=user_data.get('role', 'user'),
                    company=user_data.get('company', ''),
                    is_active=True,
                )
                created_users.append(user)
                print(f"   ✅ تم إنشاء المستخدم: {user.username} ({user.role})")
            except Exception as e:
                print(f"   ⚠️ خطأ في إنشاء {user_data['username']}: {e}")

    return created_users


def create_agent_profiles(users):
    """إنشاء ملفات تعريف للوكلاء"""
    print("\n📌 إنشاء ملفات تعريف الوكلاء...")

    agents = [u for u in users if u.role == 'agent']
    created_count = 0

    for agent in agents:
        try:
            # حذف الملف القديم إذا وجد
            AgentProfile.objects.filter(user=agent).delete()

            # إنشاء ملف جديد
            profile = AgentProfile.objects.create(
                user=agent,
                license_number=f'LIC-{random.randint(10000, 99999)}',
                years_experience=random.randint(1, 15),
                agency_name=agent.company or f'وكالة {agent.first_name} العقارية',
                website=f'https://www.{agent.username}-agency.dz',
                facebook=f'https://facebook.com/{agent.username}',
                instagram=f'https://instagram.com/{agent.username}',
                properties_count=0,
            )
            created_count += 1
            print(f"   ✅ تم إنشاء ملف وكيل: {agent.username}")
        except Exception as e:
            print(f"   ⚠️ خطأ في إنشاء ملف الوكيل {agent.username}: {e}")

    return agents


def create_developer_profiles(users):
    """إنشاء ملفات تعريف للمطورين"""
    print("\n📌 إنشاء ملفات تعريف المطورين...")

    developers = [u for u in users if u.role == 'developer']
    created_count = 0

    for developer in developers:
        try:
            # حذف الملف القديم إذا وجد
            DeveloperProfile.objects.filter(user=developer).delete()

            # إنشاء ملف جديد
            profile = DeveloperProfile.objects.create(
                user=developer,
                projects_completed=random.randint(1, 30),
                projects_in_progress=random.randint(0, 5),
                license_number=f'DEV-{random.randint(10000, 99999)}',
                years_experience=random.randint(5, 20),
                website=f'https://www.{developer.username}-dev.dz',
                facebook=f'https://facebook.com/{developer.username}',
                instagram=f'https://instagram.com/{developer.username}',
            )
            created_count += 1
            print(f"   ✅ تم إنشاء ملف مطور: {developer.username}")
        except Exception as e:
            print(f"   ⚠️ خطأ في إنشاء ملف المطور {developer.username}: {e}")

    return developers


def create_categories():
    """إنشاء فئات للعقارات"""
    print("\n📌 إنشاء فئات العقارات...")

    categories_data = [
        {'name': 'سكني', 'description': 'عقارات سكنية للعائلات'},
        {'name': 'تجاري', 'description': 'محلات ومكاتب تجارية'},
        {'name': 'استثماري', 'description': 'فرص استثمارية عقارية'},
        {'name': 'فاخر', 'description': 'عقارات فاخرة وفيلات'},
        {'name': 'اقتصادي', 'description': 'عقارات بأسعار مناسبة'},
    ]

    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"   ✅ تم إنشاء فئة: {category.name}")
        categories.append(category)

    return categories


def get_wilayas_list():
    """الحصول على قائمة الولايات"""
    wilayas = list(Wilaya.objects.all())
    if not wilayas:
        # ولايات افتراضية
        wilayas_data = [
            {'code': '16', 'name_ar': 'الجزائر', 'name_fr': 'Alger'},
            {'code': '31', 'name_ar': 'وهران', 'name_fr': 'Oran'},
            {'code': '25', 'name_ar': 'قسنطينة', 'name_fr': 'Constantine'},
            {'code': '23', 'name_ar': 'عنابة', 'name_fr': 'Annaba'},
            {'code': '06', 'name_ar': 'بجاية', 'name_fr': 'Bejaia'},
            {'code': '15', 'name_ar': 'تيزي وزو', 'name_fr': 'Tizi Ouzou'},
            {'code': '07', 'name_ar': 'بسكرة', 'name_fr': 'Biskra'},
            {'code': '05', 'name_ar': 'باتنة', 'name_fr': 'Batna'},
            {'code': '19', 'name_ar': 'سطيف', 'name_fr': 'Setif'},
            {'code': '09', 'name_ar': 'البليدة', 'name_fr': 'Blida'},
        ]
        for w_data in wilayas_data:
            wilaya, _ = Wilaya.objects.get_or_create(
                code=w_data['code'],
                defaults={
                    'name_ar': w_data['name_ar'],
                    'name_fr': w_data['name_fr'],
                    'slug': f"wilaya-{w_data['code']}-{w_data['name_ar']}"
                }
            )
            wilayas.append(wilaya)

    return wilayas


def create_properties(users, categories):
    """إنشاء عقارات وهمية"""
    print("\n📌 إنشاء العقارات التجريبية...")

    properties = []
    normal_users = [u for u in users if u.role == 'user']
    agents = [u for u in users if u.role == 'agent']
    all_owners = normal_users + agents

    if not all_owners:
        print("   ⚠️ لا يوجد مستخدمين لإنشاء عقارات لهم!")
        return properties

    # الحصول على الولايات
    wilayas = get_wilayas_list()

    for i in range(25):  # إنشاء 25 عقار تجريبي
        property_type = random.choice(PROPERTY_TYPES)
        listing_type = random.choice(LISTING_TYPES)

        # اختيار عنوان مناسب
        title = f"{random.choice(TITLES[property_type])}"

        # تحديد السعر حسب النوع
        if listing_type == 'sale':
            if property_type == 'apartment':
                price = random.randint(5000000, 50000000)
            elif property_type == 'house':
                price = random.randint(10000000, 80000000)
            elif property_type == 'villa':
                price = random.randint(30000000, 150000000)
            elif property_type == 'land':
                price = random.randint(2000000, 30000000)
            else:
                price = random.randint(5000000, 60000000)
        else:  # rent
            if property_type == 'apartment':
                price = random.randint(30000, 120000)
            elif property_type == 'house':
                price = random.randint(50000, 200000)
            elif property_type == 'villa':
                price = random.randint(80000, 300000)
            elif property_type == 'land':
                price = random.randint(10000, 50000)
            else:
                price = random.randint(40000, 150000)

        # اختيار المالك
        owner = random.choice(all_owners)

        # اختيار الوكيل (اختياري)
        agent = random.choice(agents) if agents and random.choice([True, False]) else None

        # اختيار الفئة
        category = random.choice(categories) if random.choice([True, False]) else None

        # اختيار الولاية والبلدية
        wilaya = random.choice(wilayas)
        wilaya_name = wilaya.name_ar
        commune_name = ''
        try:
            communes = Commune.objects.filter(wilaya=wilaya)
            if communes.exists():
                commune_name = random.choice(communes).name_ar
        except:
            pass

        try:
            property_obj = Property.objects.create(
                title=title,
                description=random.choice(DESCRIPTIONS),
                property_type=property_type,
                listing_type=listing_type,
                price=price,
                area_sqm=random.randint(50, 300),
                bedrooms=random.randint(1, 5),
                bathrooms=random.randint(1, 3),
                wilaya=wilaya_name,
                commune=commune_name,
                address=f"شارع {random.randint(1, 100)}، حي {random.choice(['السلام', 'النهضة', 'الفلاح', 'الأمل', 'الزهور'])}",
                is_active=True,
                is_featured=random.choice([True, False]),
                is_verified=random.choice([True, True, False]),
                owner=owner,
                agent=agent,
                category=category,
                views_count=random.randint(0, 500),
            )
            properties.append(property_obj)
            print(f"   ✅ تم إنشاء عقار: {property_obj.title} ({property_obj.price:,} دج)")
        except Exception as e:
            print(f"   ⚠️ خطأ في إنشاء العقار: {e}")

    return properties


def main():
    print("=" * 60)
    print("🚀 بدء إنشاء البيانات التجريبية")
    print("=" * 60)

    # 1. إنشاء المستخدمين
    users = create_demo_users()

    # 2. إنشاء ملفات الوكلاء
    agents = create_agent_profiles(users)

    # 3. إنشاء ملفات المطورين
    developers = create_developer_profiles(users)

    # 4. إنشاء الفئات
    categories = create_categories()

    # 5. إنشاء العقارات
    properties = create_properties(users, categories)

    print("\n" + "=" * 60)
    print("📊 ملخص البيانات التجريبية:")
    print("=" * 60)
    print(f"   ✅ المستخدمين: {User.objects.count()}")
    print(f"   ✅ الوكلاء: {len(agents)}")
    print(f"   ✅ المطورين: {len(developers)}")
    print(f"   ✅ الفئات: {Category.objects.count()}")
    print(f"   ✅ العقارات: {Property.objects.filter(is_active=True).count()}")
    print("=" * 60)
    print("🎉 تم إنشاء البيانات التجريبية بنجاح!")

    # عرض بيانات الدخول
    print("\n🔑 بيانات الدخول للمستخدمين التجريبيين:")
    print("-" * 40)
    print("المستخدم: admin     | كلمة المرور: admin123 | مشرف")
    print("المستخدم: agent1    | كلمة المرور: agent123 | وكيل عقاري")
    print("المستخدم: agent2    | كلمة المرور: agent123 | وكيل عقاري")
    print("المستخدم: developer1| كلمة المرور: dev123  | مطور عقاري")
    print("المستخدم: user1     | كلمة المرور: user123 | مستخدم عادي")
    print("المستخدم: user2     | كلمة المرور: user123 | مستخدم عادي")
    print("-" * 40)


if __name__ == '__main__':
    main()