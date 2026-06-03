# scripts/import_characteristics.py
# !/usr/bin/env python
import os
import sys
import json
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import BuildingCharacteristic, BuildingNature


def import_characteristics():
    """استيراد خصائص العقارات"""

    json_file = 'properties/fixtures/characteristics.json'

    if not os.path.exists(json_file):
        print(f"❌ الملف {json_file} غير موجود!")
        return

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("=" * 60)
    print("🚀 بدء استيراد خصائص العقارات")
    print("=" * 60)

    created = 0
    skipped = 0

    for item in data:
        nature_id = item['fields']['nature']
        name_ar = item['fields']['name_ar']
        name_fr = item['fields']['name_fr']

        # البحث عن طبيعة العقار
        try:
            nature = BuildingNature.objects.get(id=nature_id)
        except BuildingNature.DoesNotExist:
            print(f"⚠️ طبيعة العقار برقم {nature_id} غير موجودة، تخطي: {name_ar}")
            skipped += 1
            continue

        # إنشاء الخاصية
        char, created_flag = BuildingCharacteristic.objects.get_or_create(
            nature=nature,
            name_ar=name_ar,
            defaults={'name_fr': name_fr}
        )

        if created_flag:
            created += 1
            print(f"✅ تم إنشاء: {char.name_ar} (لـ {nature.name_ar})")
        else:
            print(f"⚠️ موجود بالفعل: {char.name_ar}")

    print("\n" + "=" * 60)
    print("📊 ملخص الاستيراد:")
    print("=" * 60)
    print(f"   ✅ تم إنشاء: {created} خاصية جديدة")
    print(f"   ⏭️ تم تخطي: {skipped} خاصية")
    print(f"   📍 إجمالي الخصائص: {BuildingCharacteristic.objects.count()}")
    print("=" * 60)
    print("🎉 تم استيراد خصائص العقارات بنجاح!")


if __name__ == '__main__':
    import_characteristics()