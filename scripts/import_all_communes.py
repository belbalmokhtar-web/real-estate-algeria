# scripts/import_all_communes.py
# !/usr/bin/env python
import os
import sys
import json
import django
from django.utils.text import slugify

# إعداد Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import Wilaya, Commune


def import_all_communes(json_file_path):
    """
    استيراد جميع البلديات من ملف JSON
    """
    print("=" * 60)
    print("🚀 بدء استيراد جميع البلديات الجزائرية")
    print("=" * 60)

    # قراءة الملف
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # إحصائيات
    wilayas_created = 0
    communes_created = 0
    communes_skipped = 0

    # تخزين الولايات التي تم إنشاؤها
    wilayas_map = {}

    # الخطوة 1: إنشاء الولايات (من البيانات)
    print("\n📌 الخطوة 1: إنشاء الولايات...")

    # جمع الولايات الفريدة
    unique_wilayas = {}
    for item in data:
        code = item.get('wilaya_code')
        if code and code not in unique_wilayas:
            unique_wilayas[code] = {
                'code': code,
                'name_ar': item.get('wilaya_name', '').strip(),
                'name_fr': item.get('wilaya_name_ascii', item.get('wilaya_name', '')).strip()
            }

    # إنشاء الولايات
    for code, info in unique_wilayas.items():
        if code and info['name_ar']:
            wilaya, created = Wilaya.objects.get_or_create(
                code=code,
                defaults={
                    'name_ar': info['name_ar'],
                    'name_fr': info['name_fr'],
                    'slug': slugify(f"wilaya-{code}-{info['name_ar']}")
                }
            )
            wilayas_map[code] = wilaya
            if created:
                wilayas_created += 1
                print(f"   ✅ تم إنشاء ولاية: {wilaya.name_ar} ({code})")

    print(f"\n📊 إحصائيات الولايات:")
    print(f"   - إجمالي الولايات في الملف: {len(unique_wilayas)}")
    print(f"   - ولايات جديدة: {wilayas_created}")
    print(f"   - إجمالي الولايات في النظام: {Wilaya.objects.count()}")

    # الخطوة 2: إنشاء البلديات
    print("\n📌 الخطوة 2: إنشاء البلديات...")

    # تتبع البلديات المكررة
    seen_codes = set()

    for idx, item in enumerate(data, 1):
        wilaya_code = item.get('wilaya_code')
        commune_name = item.get('commune_name', '').strip()
        commune_name_ascii = item.get('commune_name_ascii', commune_name)
        daira_name = item.get('daira_name', '').strip()
        daira_name_ascii = item.get('daira_name_ascii', daira_name)

        if not commune_name or not wilaya_code:
            continue

        # الحصول على الولاية
        wilaya = wilayas_map.get(wilaya_code)
        if not wilaya:
            print(f"   ⚠️ ولاية غير موجودة للبلدية: {commune_name}")
            communes_skipped += 1
            continue

        # إنشاء رمز فريد للبلدية
        original_id = item.get('id', idx)
        commune_code = f"{wilaya_code}{str(original_id).zfill(4)}"

        # تجنب التكرار
        if commune_code in seen_codes:
            communes_skipped += 1
            continue
        seen_codes.add(commune_code)

        # إنشاء البلدية
        try:
            commune, created = Commune.objects.get_or_create(
                code=commune_code,
                defaults={
                    'wilaya': wilaya,
                    'name_ar': commune_name,
                    'name_fr': commune_name_ascii,
                    'daira_name': daira_name,
                    'daira_name_ascii': daira_name_ascii,
                    'slug': slugify(f"{wilaya_code}-{commune_code}-{commune_name}")[:50]
                }
            )

            if created:
                communes_created += 1
                # عرض التقدم
                if communes_created % 100 == 0:
                    print(f"   📍 تم استيراد {communes_created} بلدية...")
        except Exception as e:
            print(f"   ❌ خطأ في استيراد {commune_name}: {e}")
            communes_skipped += 1

    # الخطوة 3: عرض الملخص
    print("\n" + "=" * 60)
    print("📊 ملخص الاستيراد النهائي:")
    print("=" * 60)
    print(f"   ✅ الولايات المستوردة: {wilayas_created}")
    print(f"   ✅ البلديات المستوردة: {communes_created}")
    print(f"   ⏭️  البلديات المتخطية: {communes_skipped}")
    print(f"\n   📍 إجمالي الولايات في النظام: {Wilaya.objects.count()}")
    print(f"   📍 إجمالي البلديات في النظام: {Commune.objects.count()}")
    print("=" * 60)
    print("🎉 تم استيراد البلديات بنجاح!")


if __name__ == '__main__':
    # تحديد مسار ملف JSON
    json_file = 'properties/fixtures/communes_full.json'

    if len(sys.argv) > 1:
        json_file = sys.argv[1]

    if not os.path.exists(json_file):
        print(f"❌ خطأ: الملف {json_file} غير موجود!")
        print(f"الرجاء التأكد من وجود الملف في المسار الصحيح.")
        print(f"\nالاستخدام: python scripts/import_all_communes.py [path/to/file.json]")
        sys.exit(1)

    import_all_communes(json_file)