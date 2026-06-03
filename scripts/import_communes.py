#!/usr/bin/env python
# scripts/import_communes.py
import os
import sys
import json
import django

# إعداد Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import Wilaya, Commune


def import_communes(json_file_path):
    """استيراد جميع البلديات من ملف JSON"""

    print("=" * 70)
    print("🚀 بدء استيراد البلديات الجزائرية...")
    print("=" * 70)

    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # إحصائيات
    wilayas_created = 0
    communes_created = 0
    communes_updated = 0
    communes_skipped = 0

    # أولاً: جمع كل الولايات من البيانات
    wilayas_data = {}
    for item in data:
        wilaya_code = item.get('wilaya_code')
        wilaya_name = item.get('wilaya_name', '').strip()
        wilaya_name_ascii = item.get('wilaya_name_ascii', wilaya_name)

        if wilaya_code and wilaya_name:
            if wilaya_code not in wilayas_data:
                wilayas_data[wilaya_code] = {
                    'name_ar': wilaya_name,
                    'name_fr': wilaya_name_ascii
                }

    # إنشاء أو تحديث الولايات
    print("\n📌 معالجة الولايات...")
    wilayas_map = {}

    for code, info in wilayas_data.items():
        wilaya, created = Wilaya.objects.update_or_create(
            code=code,
            defaults={
                'name_ar': info['name_ar'].strip(),
                'name_fr': info['name_fr'].strip(),
                'slug': f"wilaya-{code}-{info['name_ar']}"
            }
        )
        wilayas_map[code] = wilaya
        if created:
            wilayas_created += 1
            print(f"   ✅ تم إنشاء ولاية: {wilaya.name_ar} ({code})")
        else:
            print(f"   🔄 ولاية موجودة: {wilaya.name_ar} ({code})")

    print(f"\n📊 إحصائيات الولايات:")
    print(f"   - إجمالي الولايات في الملف: {len(wilayas_data)}")
    print(f"   - ولايات جديدة: {wilayas_created}")
    print(f"   - ولايات موجودة: {len(wilayas_data) - wilayas_created}")

    # ثانياً: معالجة البلديات
    print("\n📌 معالجة البلديات...")

    # تتبع الرموز المستخدمة
    used_codes = set()

    for idx, item in enumerate(data, 1):
        wilaya_code = item.get('wilaya_code')
        commune_name = item.get('commune_name', '').strip()
        commune_name_ascii = item.get('commune_name_ascii', commune_name)
        daira_name = item.get('daira_name', '').strip()
        daira_name_ascii = item.get('daira_name_ascii', daira_name)

        if not commune_name or not wilaya_code:
            continue

        # الحصول على كائن الولاية
        wilaya = wilayas_map.get(wilaya_code)
        if not wilaya:
            print(f"   ⚠️ ولاية غير موجودة للبلدية: {commune_name} (رمز: {wilaya_code})")
            communes_skipped += 1
            continue

        # إنشاء رمز فريد للبلدية
        commune_code = f"{wilaya_code}{str(item.get('id', idx)).zfill(3)}"

        # تجنب التكرار
        if commune_code in used_codes:
            communes_skipped += 1
            continue
        used_codes.add(commune_code)

        # إنشاء أو تحديث البلدية
        commune, created = Commune.objects.update_or_create(
            code=commune_code,
            defaults={
                'wilaya': wilaya,
                'name_ar': commune_name,
                'name_fr': commune_name_ascii,
                'daira_name': daira_name,
                'daira_name_ascii': daira_name_ascii,
                'slug': f"{wilaya_code}-{commune_code}-{slugify(commune_name)}"
            }
        )

        if created:
            communes_created += 1
        else:
            communes_updated += 1

        # عرض التقدم
        if (communes_created + communes_updated) % 200 == 0:
            print(f"   📍 تم معالجة {(communes_created + communes_updated)} بلدية...")

    # عرض الإحصائيات النهائية
    print("\n" + "=" * 70)
    print("📊 ملخص الاستيراد النهائي:")
    print("=" * 70)
    print(f"   ✅ الولايات المستوردة: {wilayas_created}")
    print(f"   ✅ البلديات المستوردة: {communes_created}")
    print(f"   🔄 البلديات المحدثة: {communes_updated}")
    print(f"   ⏭️  البلديات المتخطية: {communes_skipped}")
    print(f"\n   📍 إجمالي الولايات في النظام: {Wilaya.objects.count()}")
    print(f"   📍 إجمالي البلديات في النظام: {Commune.objects.count()}")
    print("=" * 70)
    print("🎉 انتهى استيراد البلديات بنجاح!")


def slugify(text):
    """تحويل النص إلى slug"""
    import re
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-').lower()


if __name__ == '__main__':
    import sys
    import os

    # تحديد مسار ملف JSON
    json_path = 'properties/fixtures/communes_full.json'

    if len(sys.argv) > 1:
        json_path = sys.argv[1]

    if not os.path.exists(json_path):
        print(f"❌ خطأ: الملف {json_path} غير موجود!")
        print(f"الرجاء التأكد من وجود الملف في المسار الصحيح.")
        sys.exit(1)

    import_communes(json_path)