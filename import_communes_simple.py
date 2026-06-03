# import_communes_simple.py
import json
import os
import sys

# إعداد Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

from properties.models_valuation import Wilaya, Commune


def import_communes():
    json_file = 'properties/fixtures/communes_full.json'

    print("📖 جاري قراءة ملف البلديات...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📊 تم العثور على {len(data)} بلدية")

    # إنشاء قاموس للولايات
    wilayas_dict = {w.name_ar: w for w in Wilaya.objects.all()}
    print(f"📊 الولايات المتاحة: {len(wilayas_dict)}")

    created_count = 0
    updated_count = 0
    skipped_count = 0

    for item in data:
        wilaya_name = item.get('wilaya_name', '').strip()
        wilaya = wilayas_dict.get(wilaya_name)

        if not wilaya:
            skipped_count += 1
            if skipped_count <= 10:  # عرض أول 10 أخطاء فقط
                print(f"⚠️ ولاية غير موجودة: '{wilaya_name}'")
            continue

        try:
            commune, created = Commune.objects.update_or_create(
                id=item['id'],
                defaults={
                    'wilaya': wilaya,
                    'name_ar': item['commune_name'],
                    'name_fr': item['commune_name_ascii'],
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        except Exception as e:
            print(f"❌ خطأ في البلدية {item.get('commune_name', 'غير معروف')}: {e}")
            skipped_count += 1

        # عرض التقدم
        total_processed = created_count + updated_count + skipped_count
        if total_processed % 200 == 0:
            print(f"📊 التقدم: {total_processed}/{len(data)} بلدية...")

    print("\n" + "=" * 50)
    print(f"✅ تم استيراد {created_count} بلدية جديدة")
    print(f"🔄 تم تحديث {updated_count} بلدية")
    print(f"⚠️ تم تخطي {skipped_count} بلدية")
    print(f"📊 إجمالي البلديات في قاعدة البيانات: {Commune.objects.count()}")
    print("=" * 50)


if __name__ == '__main__':
    import_communes()