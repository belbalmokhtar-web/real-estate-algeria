#!/usr/bin/env python
# scripts/import_communes_direct.py
import os
import sys
import django

# إعداد Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import Wilaya, Commune

# بيانات الولايات والبلديات (جزء من البيانات للاختبار)
data = [
    # ولاية أدرار (01)
    {"id": 1, "commune_name": "أدرار", "commune_name_ascii": "Adrar", "daira_name": "أدرار",
     "daira_name_ascii": "Adrar", "wilaya_code": "01", "wilaya_name": "أدرار", "wilaya_name_ascii": "Adrar"},
    {"id": 2, "commune_name": "تامنطيط", "commune_name_ascii": "Tamantit", "daira_name": "فنوغيل",
     "daira_name_ascii": "Fenoughil", "wilaya_code": "01", "wilaya_name": "أدرار", "wilaya_name_ascii": "Adrar"},
    {"id": 3, "commune_name": "تامست", "commune_name_ascii": "Tamest", "daira_name": "فنوغيل",
     "daira_name_ascii": "Fenoughil", "wilaya_code": "01", "wilaya_name": "أدرار", "wilaya_name_ascii": "Adrar"},
    {"id": 4, "commune_name": "أولف", "commune_name_ascii": "Aoulef", "daira_name": "أولف",
     "daira_name_ascii": "Aoulef", "wilaya_code": "01", "wilaya_name": "أدرار", "wilaya_name_ascii": "Adrar"},
    {"id": 5, "commune_name": "تيمقتن", "commune_name_ascii": "Timekten", "daira_name": "أولف",
     "daira_name_ascii": "Aoulef", "wilaya_code": "01", "wilaya_name": "أدرار", "wilaya_name_ascii": "Adrar"},

    # ولاية الجزائر (16)
    {"id": 6, "commune_name": "الجزائر الوسطى", "commune_name_ascii": "Alger Centre", "daira_name": "سيدي امحمد",
     "daira_name_ascii": "Sidi M'hamed", "wilaya_code": "16", "wilaya_name": "الجزائر", "wilaya_name_ascii": "Alger"},
    {"id": 7, "commune_name": "سيدي امحمد", "commune_name_ascii": "Sidi M'hamed", "daira_name": "سيدي امحمد",
     "daira_name_ascii": "Sidi M'hamed", "wilaya_code": "16", "wilaya_name": "الجزائر", "wilaya_name_ascii": "Alger"},
    {"id": 8, "commune_name": "القبة", "commune_name_ascii": "Kouba", "daira_name": "حسين داي",
     "daira_name_ascii": "Hussein Dey", "wilaya_code": "16", "wilaya_name": "الجزائر", "wilaya_name_ascii": "Alger"},
    {"id": 9, "commune_name": "الحراش", "commune_name_ascii": "El Harrach", "daira_name": "الحراش",
     "daira_name_ascii": "El Harrach", "wilaya_code": "16", "wilaya_name": "الجزائر", "wilaya_name_ascii": "Alger"},
    {"id": 10, "commune_name": "براقي", "commune_name_ascii": "Baraki", "daira_name": "براقي",
     "daira_name_ascii": "Baraki", "wilaya_code": "16", "wilaya_name": "الجزائر", "wilaya_name_ascii": "Alger"},

    # ولاية وهران (31)
    {"id": 11, "commune_name": "وهران", "commune_name_ascii": "Oran", "daira_name": "وهران", "daira_name_ascii": "Oran",
     "wilaya_code": "31", "wilaya_name": "وهران", "wilaya_name_ascii": "Oran"},
    {"id": 12, "commune_name": "بئر الجير", "commune_name_ascii": "Bir El Djir", "daira_name": "بئر الجير",
     "daira_name_ascii": "Bir El Djir", "wilaya_code": "31", "wilaya_name": "وهران", "wilaya_name_ascii": "Oran"},
    {"id": 13, "commune_name": "السانية", "commune_name_ascii": "Es Senia", "daira_name": "السانية",
     "daira_name_ascii": "Es Senia", "wilaya_code": "31", "wilaya_name": "وهران", "wilaya_name_ascii": "Oran"},

    # ولاية قسنطينة (25)
    {"id": 14, "commune_name": "قسنطينة", "commune_name_ascii": "Constantine", "daira_name": "قسنطينة",
     "daira_name_ascii": "Constantine", "wilaya_code": "25", "wilaya_name": "قسنطينة",
     "wilaya_name_ascii": "Constantine"},
    {"id": 15, "commune_name": "الخروب", "commune_name_ascii": "El Khroub", "daira_name": "الخروب",
     "daira_name_ascii": "El Khroub", "wilaya_code": "25", "wilaya_name": "قسنطينة",
     "wilaya_name_ascii": "Constantine"},
    {"id": 16, "commune_name": "عين السمارة", "commune_name_ascii": "Ain Smara", "daira_name": "الخروب",
     "daira_name_ascii": "El Khroub", "wilaya_code": "25", "wilaya_name": "قسنطينة",
     "wilaya_name_ascii": "Constantine"},
]


def import_data():
    print("=" * 60)
    print("🚀 بدء استيراد الولايات والبلديات...")
    print("=" * 60)

    wilayas_created = 0
    communes_created = 0

    # استيراد الولايات
    wilayas_map = {}
    for item in data:
        code = item['wilaya_code']
        name_ar = item['wilaya_name']
        name_fr = item['wilaya_name_ascii']

        if code not in wilayas_map:
            wilaya, created = Wilaya.objects.get_or_create(
                code=code,
                defaults={
                    'name_ar': name_ar,
                    'name_fr': name_fr,
                    'slug': f"wilaya-{code}-{name_ar}"
                }
            )
            wilayas_map[code] = wilaya
            if created:
                wilayas_created += 1
                print(f"   ✅ تم إنشاء ولاية: {name_ar} ({code})")

    # استيراد البلديات
    for item in data:
        wilaya = wilayas_map.get(item['wilaya_code'])
        if wilaya:
            commune_code = f"{item['wilaya_code']}{str(item['id']).zfill(3)}"
            commune, created = Commune.objects.get_or_create(
                code=commune_code,
                defaults={
                    'wilaya': wilaya,
                    'name_ar': item['commune_name'],
                    'name_fr': item['commune_name_ascii'],
                    'daira_name': item.get('daira_name', ''),
                    'daira_name_ascii': item.get('daira_name_ascii', ''),
                    'slug': f"{item['wilaya_code']}-{commune_code}-{item['commune_name']}"
                }
            )
            if created:
                communes_created += 1

    print("\n" + "=" * 60)
    print("📊 ملخص الاستيراد:")
    print("=" * 60)
    print(f"   ✅ الولايات المستوردة: {wilayas_created}")
    print(f"   ✅ البلديات المستوردة: {communes_created}")
    print(f"   📍 إجمالي الولايات في النظام: {Wilaya.objects.count()}")
    print(f"   📍 إجمالي البلديات في النظام: {Commune.objects.count()}")
    print("=" * 60)
    print("🎉 انتهى الاستيراد بنجاح!")


if __name__ == '__main__':
    import_data()