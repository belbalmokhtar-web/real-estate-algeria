#!/usr/bin/env python
# scripts/simple_demo_data.py
import os
import sys
import django
import random

# إعداد Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from properties.models import Property, Category

User = get_user_model()


def create_simple_demo():
    print("=" * 60)
    print("🚀 بدء إنشاء البيانات التجريبية البسيطة")
    print("=" * 60)

    # 1. إنشاء المستخدمين
    print("\n📌 إنشاء المستخدمين...")

    users_data = [
        {'username': 'admin', 'password': 'admin123', 'is_staff': True, 'is_superuser': True},
        {'username': 'demo1', 'password': 'demo123', 'is_staff': False, 'is_superuser': False},
        {'username': 'demo2', 'password': 'demo123', 'is_staff': False, 'is_superuser': False},
    ]

    created_users = []
    for data in users_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': f"{data['username']}@example.com",
                'is_staff': data['is_staff'],
                'is_superuser': data['is_superuser'],
                'is_active': True,
            }
        )
        if created:
            user.set_password(data['password'])
            user.save()
            print(f"   ✅ تم إنشاء المستخدم: {user.username}")
        else:
            print(f"   ⚠️ المستخدم موجود: {user.username}")
        created_users.append(user)

    # 2. إنشاء الفئات
    print("\n📌 إنشاء الفئات...")

    categories_data = ['سكني', 'تجاري', 'استثماري', 'فاخر']
    categories = []

    for cat_name in categories_data:
        # حذف Slug مكرر عن طريق إضافة رقم عشوائي
        category, created = Category.objects.get_or_create(
            name=cat_name,
            defaults={'description': f'عقارات {cat_name}'}
        )
        if created:
            print(f"   ✅ تم إنشاء فئة: {category.name}")
        categories.append(category)

    # 3. إنشاء عقارات تجريبية
    print("\n📌 إنشاء العقارات التجريبية...")

    demo_user = User.objects.filter(username='demo1').first() or created_users[0]

    properties_data = [
        {
            'title': 'شقة فاخرة في الجزائر العاصمة',
            'price': 25000000,
            'area_sqm': 120,
            'property_type': 'apartment',
            'listing_type': 'sale',
            'wilaya': 'الجزائر',
            'commune': 'الجزائر الوسطى',
            'bedrooms': 3,
            'bathrooms': 2,
            'description': 'شقة فاخرة في قلب الجزائر العاصمة، قريبة من جميع الخدمات',
            'is_featured': True,
        },
        {
            'title': 'فيلا راقية في وهران',
            'price': 85000000,
            'area_sqm': 250,
            'property_type': 'villa',
            'listing_type': 'sale',
            'wilaya': 'وهران',
            'commune': 'بئر الجير',
            'bedrooms': 5,
            'bathrooms': 3,
            'description': 'فيلا فاخرة مع مسبح وحديقة، موقع مميز',
            'is_featured': True,
        },
        {
            'title': 'منزل عائلي في قسنطينة',
            'price': 35000000,
            'area_sqm': 180,
            'property_type': 'house',
            'listing_type': 'sale',
            'wilaya': 'قسنطينة',
            'commune': 'الخروب',
            'bedrooms': 4,
            'bathrooms': 2,
            'description': 'منزل واسع مناسب للعائلات',
            'is_featured': False,
        },
        {
            'title': 'شقة للإيجار في عنابة',
            'price': 80000,
            'area_sqm': 100,
            'property_type': 'apartment',
            'listing_type': 'rent',
            'wilaya': 'عنابة',
            'commune': 'عنابة',
            'bedrooms': 2,
            'bathrooms': 1,
            'description': 'شقة مفروشة للإيجار الشهري',
            'is_featured': False,
        },
        {
            'title': 'أرض سكنية في بجاية',
            'price': 15000000,
            'area_sqm': 400,
            'property_type': 'land',
            'listing_type': 'sale',
            'wilaya': 'بجاية',
            'commune': 'بجاية',
            'bedrooms': 0,
            'bathrooms': 0,
            'description': 'قطعة أرض للبناء',
            'is_featured': False,
        },
        {
            'title': 'فيلا للإيجار في تيزي وزو',
            'price': 120000,
            'area_sqm': 200,
            'property_type': 'villa',
            'listing_type': 'rent',
            'wilaya': 'تيزي وزو',
            'commune': 'تيزي وزو',
            'bedrooms': 4,
            'bathrooms': 3,
            'description': 'فيلا مؤثثة للإيجار السنوي',
            'is_featured': True,
        },
        {
            'title': 'محل تجاري في الجزائر',
            'price': 45000000,
            'area_sqm': 80,
            'property_type': 'commercial',
            'listing_type': 'sale',
            'wilaya': 'الجزائر',
            'commune': 'الحراش',
            'bedrooms': 0,
            'bathrooms': 1,
            'description': 'محل تجاري في شارع رئيسي',
            'is_featured': False,
        },
        {
            'title': 'مكتب للإيجار في وهران',
            'price': 50000,
            'area_sqm': 60,
            'property_type': 'commercial',
            'listing_type': 'rent',
            'wilaya': 'وهران',
            'commune': 'السانية',
            'bedrooms': 0,
            'bathrooms': 1,
            'description': 'مكتب مجهز للإيجار',
            'is_featured': False,
        },
        {
            'title': 'شقة سكنية في البليدة',
            'price': 18000000,
            'area_sqm': 90,
            'property_type': 'apartment',
            'listing_type': 'sale',
            'wilaya': 'البليدة',
            'commune': 'البليدة',
            'bedrooms': 2,
            'bathrooms': 1,
            'description': 'شقة هادئة قريبة من المنتزه',
            'is_featured': False,
        },
        {
            'title': 'فيلا فاخرة في الجزائر',
            'price': 120000000,
            'area_sqm': 350,
            'property_type': 'villa',
            'listing_type': 'sale',
            'wilaya': 'الجزائر',
            'commune': 'سيدي امحمد',
            'bedrooms': 6,
            'bathrooms': 4,
            'description': 'فيلا فاخرة مع إطلالة رائعة',
            'is_featured': True,
        },
    ]

    created_count = 0
    for data in properties_data:
        # التحقق من عدم وجود عقار بنفس العنوان
        if not Property.objects.filter(title=data['title']).exists():
            property_obj = Property.objects.create(
                title=data['title'],
                price=data['price'],
                area_sqm=data['area_sqm'],
                property_type=data['property_type'],
                listing_type=data['listing_type'],
                wilaya=data['wilaya'],
                commune=data['commune'],
                bedrooms=data['bedrooms'],
                bathrooms=data['bathrooms'],
                description=data['description'],
                is_active=True,
                is_featured=data['is_featured'],
                is_verified=True,
                owner=demo_user,
                views_count=random.randint(0, 100),
            )
            created_count += 1
            print(f"   ✅ تم إنشاء: {property_obj.title}")
        else:
            print(f"   ⚠️ موجود مسبقاً: {data['title']}")

    # 4. عرض الملخص
    print("\n" + "=" * 60)
    print("📊 ملخص البيانات التجريبية:")
    print("=" * 60)
    print(f"   ✅ المستخدمين: {User.objects.count()}")
    print(f"   ✅ الفئات: {Category.objects.count()}")
    print(f"   ✅ العقارات: {Property.objects.filter(is_active=True).count()}")
    print("=" * 60)
    print("🎉 تم إنشاء البيانات التجريبية بنجاح!")

    # عرض بيانات الدخول
    print("\n🔑 بيانات الدخول:")
    print("-" * 40)
    print("المستخدم: admin  | كلمة المرور: admin123 | مشرف")
    print("المستخدم: demo1  | كلمة المرور: demo123 | مستخدم عادي")
    print("المستخدم: demo2  | كلمة المرور: demo123 | مستخدم عادي")
    print("-" * 40)


if __name__ == '__main__':
    create_simple_demo()