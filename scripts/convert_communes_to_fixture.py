# scripts/convert_communes_to_fixture.py
import json
import os
import sys

# أضف مسار المشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

from properties.models_valuation import Wilaya


def convert_json_to_fixture(input_file, output_file):
    """تحويل ملف JSON للبلديات إلى Django Fixture"""

    # قراءة البيانات
    with open(input_file, 'r', encoding='utf-8') as f:
        communes_data = json.load(f)

    # إنشاء قاموس لربط اسم الولاية بالـ PK
    wilaya_map = {}
    for wilaya in Wilaya.objects.all():
        # إزالة المسافات الزائدة للمقارنة
        name_clean = wilaya.name_ar.strip()
        wilaya_map[name_clean] = wilaya.id
        wilaya_map[wilaya.name_fr.strip()] = wilaya.id

    # إنشاء الـ Fixture
    fixtures = []

    for commune in communes_data:
        wilaya_name_ar = commune.get('wilaya_name', '').strip()
        wilaya_name_fr = commune.get('wilaya_name_ascii', '').strip()

        # البحث عن معرف الولاية
        wilaya_id = wilaya_map.get(wilaya_name_ar) or wilaya_map.get(wilaya_name_fr)

        if wilaya_id:
            fixtures.append({
                "model": "properties.commune",
                "pk": commune['id'],
                "fields": {
                    "wilaya": wilaya_id,
                    "name_ar": commune['commune_name'],
                    "name_fr": commune['commune_name_ascii'],
                    "postal_code": ""  # يمكن إضافة الرمز البريدي لاحقاً
                }
            })
        else:
            print(f"⚠️ لم يتم العثور على الولاية: {wilaya_name_ar} / {wilaya_name_fr}")

    # حفظ الـ Fixture
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)

    print(f"✅ تم تحويل {len(fixtures)} بلدية إلى {output_file}")
    return fixtures


if __name__ == '__main__':
    input_file = 'properties/fixtures/communes_full.json'
    output_file = 'properties/fixtures/communes_fixture.json'

    # أولاً: تأكد من وجود الولايات في قاعدة البيانات
    if Wilaya.objects.count() == 0:
        print("❌ يرجى أولاً تحميل الولايات باستخدام الأمر:")
        print("   python manage.py loaddata properties/fixtures/wilayas_fixture.json")
    else:
        convert_json_to_fixture(input_file, output_file)