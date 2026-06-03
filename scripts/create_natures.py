# scripts/create_natures.py
# !/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import BuildingNature


def create_natures():
    """إنشاء طبائع العقارات الأساسية"""

    natures_data = [
        {'id': 1, 'name_ar': 'فردي', 'name_fr': 'Individuels'},
        {'id': 2, 'name_ar': 'جماعي وشبه جماعي', 'name_fr': 'Collectifs et Semi-Collectifs'},
        {'id': 3, 'name_ar': 'محلات تجارية ومحلات مهنية',
         'name_fr': 'Locaux Commerciaux et Locaux à Usage Professionnels'},
        {'id': 4, 'name_ar': 'هنغارات', 'name_fr': 'Hangars'},
        {'id': 5, 'name_ar': 'أراضي فضاء', 'name_fr': 'Terrains Nus'},
        {'id': 6, 'name_ar': 'أراضي فلاحية (سهل)', 'name_fr': 'Terrains Agricoles en Plaine'},
        {'id': 7, 'name_ar': 'أراضي فلاحية (منحدر)', 'name_fr': 'Terrains Agricoles en Pente'},
    ]

    print("=" * 60)
    print("🚀 بدء إنشاء طبائع العقارات")
    print("=" * 60)

    created = 0
    for nature_data in natures_data:
        nature, created_flag = BuildingNature.objects.get_or_create(
            id=nature_data['id'],
            defaults={
                'name_ar': nature_data['name_ar'],
                'name_fr': nature_data['name_fr']
            }
        )
        if created_flag:
            created += 1
            print(f"✅ تم إنشاء: {nature.name_ar}")
        else:
            print(f"⚠️ موجود بالفعل: {nature.name_ar}")

    print(f"\n📊 إجمالي طبائع العقارات: {BuildingNature.objects.count()}")
    print("🎉 تم الانتهاء!")


if __name__ == '__main__':
    create_natures()