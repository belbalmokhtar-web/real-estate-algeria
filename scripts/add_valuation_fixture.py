# scripts/add_valuation_fixture.py
# !/usr/bin/env python
import os
import sys
import django
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import ZoneType, BuildingNature, BuildingCharacteristic
from django.utils import timezone


def add_valuation_data():
    print("=" * 50)
    print("🚀 بدء إضافة بيانات التقييم العقاري")
    print("=" * 50)

    # ========== إضافة المناطق ==========
    print("\n📌 إضافة المناطق...")

    zones_data = [
        ('منطقة سكنية', 'Zone résidentielle'),
        ('وسط المدينة', 'Centre-ville'),
        ('منطقة محيطة', 'Zone périphérique'),
        ('منطقة نائية', "Zone d'éloignement"),
    ]

    zones_created = 0
    for name_ar, name_fr in zones_data:
        zone, created = ZoneType.objects.get_or_create(
            name_ar=name_ar,
            defaults={'name_fr': name_fr}
        )
        if created:
            zones_created += 1
            print(f"   ✅ تم إنشاء منطقة: {zone.name_ar}")
        else:
            print(f"   ⚠️ المنطقة موجودة: {zone.name_ar}")

    print(f"📊 إجمالي المناطق: {ZoneType.objects.count()} (جديد: {zones_created})")

    # ========== إضافة طبائع العقارات ==========
    print("\n📌 إضافة طبائع العقارات...")

    natures_data = [
        ('فردي', 'Individuels'),
        ('جماعي وشبه جماعي', 'Collectifs et Semi-Collectifs'),
        ('محلات تجارية ومحلات مهنية', 'Locaux Commerciaux et Locaux à Usage Professionnels'),
        ('هنغارات', 'Hangars'),
        ('أراضي فضاء', 'Terrains Nus'),
        ('أراضي فلاحية (سهل)', 'Terrains Agricoles en Plaine'),
        ('أراضي فلاحية (منحدر)', 'Terrains Agricoles en Pente'),
    ]

    natures_created = 0
    natures_map = {}
    for name_ar, name_fr in natures_data:
        nature, created = BuildingNature.objects.get_or_create(
            name_ar=name_ar,
            defaults={'name_fr': name_fr}
        )
        natures_map[name_ar] = nature
        if created:
            natures_created += 1
            print(f"   ✅ تم إنشاء طبيعة عقار: {nature.name_ar}")
        else:
            print(f"   ⚠️ طبيعة العقار موجودة: {nature.name_ar}")

    print(f"📊 إجمالي طبائع العقارات: {BuildingNature.objects.count()} (جديد: {natures_created})")

    # ========== إضافة خصائص العقارات ==========
    print("\n📌 إضافة خصائص العقارات...")

    characteristics_data = [
        # فردي
        ('فردي', 'Standing', 'Standing'),
        ('فردي', 'Amélioré', 'Amélioré'),
        ('فردي', 'Economique', 'Economique'),
        ('فردي', 'Précaire', 'Précaire'),

        # جماعي وشبه جماعي
        ('جماعي وشبه جماعي', 'Standing', 'Standing'),
        ('جماعي وشبه جماعي', 'Amélioré', 'Amélioré'),
        ('جماعي وشبه جماعي', 'Economique', 'Economique'),
        ('جماعي وشبه جماعي', 'Précaire', 'Précaire'),

        # محلات تجارية
        ('محلات تجارية ومحلات مهنية', 'Artère hautement commerciale', 'Artère hautement commerciale'),
        ('محلات تجارية ومحلات مهنية', 'Artère moyennement commerciale', 'Artère moyennement commerciale'),
        ('محلات تجارية ومحلات مهنية', 'Artère peu commerciale', 'Artère peu commerciale'),

        # هنغارات
        ('هنغارات', 'Situé en zone urbaine', 'Situé en zone urbaine'),
        ('هنغارات', 'Situé en zone rurale', 'Situé en zone rurale'),

        # أراضي فضاء
        ('أراضي فضاء', 'Pleine propriété deux façades avec raccordements',
         'Pleine propriété deux façades avec raccordements'),
        ('أراضي فضاء', 'Pleine propriété une façade avec raccordements',
         'Pleine propriété une façade avec raccordements'),
        ('أراضي فضاء', 'Pleine propriété deux façades sans raccordements',
         'Pleine propriété deux façades sans raccordements'),
        ('أراضي فضاء', 'Pleine propriété une façade sans raccordements',
         'Pleine propriété une façade sans raccordements'),
        ('أراضي فضاء', "Dans l'indivision", "Dans l'indivision"),
        ('أراضي فضاء', 'Industriel', 'Industriel'),

        # أراضي فلاحية (سهل)
        ('أراضي فلاحية (سهل)', 'Potentialité élevée', 'Potentialité élevée'),
        ('أراضي فلاحية (سهل)', 'Potentialité moyenne', 'Potentialité moyenne'),
        ('أراضي فلاحية (سهل)', 'Potentialité faible', 'Potentialité faible'),

        # أراضي فلاحية (منحدر)
        ('أراضي فلاحية (منحدر)', 'Potentialité élevée', 'Potentialité élevée'),
        ('أراضي فلاحية (منحدر)', 'Potentialité moyenne', 'Potentialité moyenne'),
        ('أراضي فلاحية (منحدر)', 'Potentialité faible', 'Potentialité faible'),
    ]

    chars_created = 0
    for nature_name, char_ar, char_fr in characteristics_data:
        nature = natures_map.get(nature_name)
        if nature:
            char, created = BuildingCharacteristic.objects.get_or_create(
                nature=nature,
                name_ar=char_ar,
                defaults={'name_fr': char_fr}
            )
            if created:
                chars_created += 1
                print(f"   ✅ تم إنشاء خاصية: {char.name_ar} (لـ {nature_name})")

    print(f"📊 إجمالي الخصائص: {BuildingCharacteristic.objects.count()} (جديد: {chars_created})")

    # ========== الملخص النهائي ==========
    print("\n" + "=" * 50)
    print("📊 الملخص النهائي:")
    print("=" * 50)
    print(f"   ✅ المناطق: {ZoneType.objects.count()}")
    print(f"   ✅ طبائع العقارات: {BuildingNature.objects.count()}")
    print(f"   ✅ خصائص العقارات: {BuildingCharacteristic.objects.count()}")
    print("=" * 50)
    print("🎉 تم إضافة بيانات التقييم العقاري بنجاح!")


if __name__ == '__main__':
    add_valuation_data()