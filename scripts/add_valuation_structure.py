# scripts/add_valuation_structure.py
# !/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import ZoneType, BuildingNature, BuildingCharacteristic


def create_zones():
    """إنشاء أنواع المناطق"""
    zones_data = [
        ('residential', 'منطقة سكنية', 'Zone résidentielle'),
        ('centre_ville', 'وسط المدينة', 'Centre-ville'),
        ('peripherique', 'منطقة محيطة', 'Zone périphérique'),
        ('eloignement', 'منطقة نائية', "Zone d'éloignement"),
    ]

    created = 0
    for code, name_ar, name_fr in zones_data:
        zone, created_flag = ZoneType.objects.get_or_create(
            zone_type=code,
            defaults={'name_ar': name_ar, 'name_fr': name_fr}
        )
        if created_flag:
            created += 1
            print(f"✅ تم إنشاء منطقة: {zone.name_ar}")
    print(f"📊 تم إنشاء {created} منطقة جديدة")
    return created


def create_building_natures():
    """إنشاء طبائع العقارات"""
    natures_data = [
        ('individuels', 'منازل فردية', 'Individuels'),
        ('collectifs', 'مجمعات سكنية', 'Collectifs et Semi-Collectifs'),
        ('commerciaux', 'محلات تجارية ومهنية', 'Locaux Commerciaux et Locaux à Usage Professionnels'),
        ('hangars', 'مستودعات', 'Hangars'),
        ('terrains_nus', 'أراضي فضاء', 'Terrains Nus'),
        ('agricoles_plaine', 'أراضي زراعية في السهل', 'Terrains Agricoles en Plaine'),
        ('agricoles_pente', 'أراضي زراعية في المنحدر', 'Terrains Agricoles en Pente'),
    ]

    created = 0
    natures_map = {}
    for code, name_ar, name_fr in natures_data:
        nature, created_flag = BuildingNature.objects.get_or_create(
            nature_code=code,
            defaults={'name_ar': name_ar, 'name_fr': name_fr}
        )
        natures_map[code] = nature
        if created_flag:
            created += 1
            print(f"✅ تم إنشاء طبيعة عقار: {nature.name_ar}")
    print(f"📊 تم إنشاء {created} طبيعة عقار جديدة")
    return natures_map


def create_characteristics(natures_map):
    """إنشاء خصائص العقارات حسب كل طبيعة"""
    characteristics_data = {
        'individuels': [
            ('standing', 'راقي (Standing)', 'Standing'),
            ('ameliore', 'محسن (Amélioré)', 'Amélioré'),
            ('economique', 'اقتصادي (Economique)', 'Economique'),
            ('precaire', 'متواضع (Précaire)', 'Précaire'),
        ],
        'collectifs': [
            ('standing', 'راقي (Standing)', 'Standing'),
            ('ameliore', 'محسن (Amélioré)', 'Amélioré'),
            ('economique', 'اقتصادي (Economique)', 'Economique'),
            ('precaire', 'متواضع (Précaire)', 'Précaire'),
        ],
        'commerciaux': [
            ('artere_haut', 'شارع تجاري حيوي', 'Artère hautement commerciale'),
            ('artere_moyen', 'شارع تجاري متوسط', 'Artère moyennement commerciale'),
            ('artere_faible', 'شارع تجاري هادئ', 'Artère peu commerciale'),
        ],
        'hangars': [
            ('zone_urbaine', 'في منطقة حضرية', 'Situé en zone urbaine'),
            ('zone_rurale', 'في منطقة ريفية', 'Situé en zone rurale'),
        ],
        'terrains_nus': [
            ('pleine_propriete_2_facades_avec', 'ملكية كاملة - واجهتان مع التوصيلات',
             'Pleine propriété deux façades avec raccordements'),
            ('pleine_propriete_1_facade_avec', 'ملكية كاملة - واجهة واحدة مع التوصيلات',
             'Pleine propriété une façade avec raccordements'),
            ('pleine_propriete_2_facades_sans', 'ملكية كاملة - واجهتان بدون توصيلات',
             'Pleine propriété deux façades sans raccordements'),
            ('pleine_propriete_1_facade_sans', 'ملكية كاملة - واجهة واحدة بدون توصيلات',
             'Pleine propriété une façade sans raccordements'),
            ('indivision', 'في حالة شراكة', "Dans l'indivision"),
            ('industriel', 'صناعي', 'Industriel'),
        ],
        'agricoles_plaine': [
            ('potentialite_elevee', 'إمكانية عالية', 'Potentialité élevée'),
            ('potentialite_moyenne', 'إمكانية متوسطة', 'Potentialité moyenne'),
            ('potentialite_faible', 'إمكانية ضعيفة', 'Potentialité faible'),
        ],
        'agricoles_pente': [
            ('potentialite_elevee', 'إمكانية عالية', 'Potentialité élevée'),
            ('potentialite_moyenne', 'إمكانية متوسطة', 'Potentialité moyenne'),
            ('potentialite_faible', 'إمكانية ضعيفة', 'Potentialité faible'),
        ],
    }

    created = 0
    for nature_code, chars in characteristics_data.items():
        nature = natures_map.get(nature_code)
        if nature:
            for char_code, name_ar, name_fr in chars:
                char, created_flag = BuildingCharacteristic.objects.get_or_create(
                    nature=nature,
                    characteristic_code=char_code,
                    defaults={'name_ar': name_ar, 'name_fr': name_fr}
                )
                if created_flag:
                    created += 1
                    print(f"✅ تم إنشاء خاصية: {char.name_ar} (لـ {nature.name_ar})")

    print(f"📊 تم إنشاء {created} خاصية جديدة")
    return created


def main():
    print("=" * 60)
    print("🚀 بدء إنشاء هيكل التقييم العقاري")
    print("=" * 60)

    print("\n📌 إنشاء أنواع المناطق...")
    create_zones()

    print("\n📌 إنشاء طبائع العقارات...")
    natures_map = create_building_natures()

    print("\n📌 إنشاء خصائص العقارات...")
    create_characteristics(natures_map)

    print("\n" + "=" * 60)
    print("🎉 تم إنشاء هيكل التقييم العقاري بنجاح!")
    print("=" * 60)

    print(f"\n📊 الإحصائيات النهائية:")
    print(f"   - أنواع المناطق: {ZoneType.objects.count()}")
    print(f"   - طبائع العقارات: {BuildingNature.objects.count()}")
    print(f"   - خصائص العقارات: {BuildingCharacteristic.objects.count()}")


if __name__ == '__main__':
    main()