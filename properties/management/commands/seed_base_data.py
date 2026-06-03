# properties/management/commands/seed_base_data.py
from django.core.management.base import BaseCommand
from properties.models_valuation import Zone, NatureImmeuble, Caracteristique


class Command(BaseCommand):
    help = 'إضافة البيانات الأساسية: المناطق، طبائع العقار، والخصائص'

    def handle(self, *args, **options):
        self.stdout.write("🌱 جاري إضافة البيانات الأساسية...")

        # ========== 1. إضافة المناطق ==========
        zones_data = [
            {'key': 'residential', 'name_ar': 'منطقة سكنية', 'name_fr': 'Zone résidentielle'},
            {'key': 'city_center', 'name_ar': 'وسط المدينة', 'name_fr': 'Centre-ville'},
            {'key': 'peripheral', 'name_ar': 'منطقة نائية', 'name_fr': 'Zone périphérique'},
            {'key': 'remote', 'name_ar': 'منطقة نائية جداً', 'name_fr': "Zone d'éloignement"},
        ]

        zones_created = 0
        for zone_data in zones_data:
            zone, created = Zone.objects.get_or_create(
                key=zone_data['key'],
                defaults={
                    'name_ar': zone_data['name_ar'],
                    'name_fr': zone_data['name_fr']
                }
            )
            if created:
                zones_created += 1
                self.stdout.write(f"  ✅ تم إضافة المنطقة: {zone.name_ar}")

        # ========== 2. إضافة طبائع العقار ==========
        natures_data = [
            {'key': 'individuels', 'name_ar': 'فرادى', 'name_fr': 'Individuels'},
            {'key': 'collectifs', 'name_ar': 'جماعية وشبه جماعية', 'name_fr': 'Collectifs et Semi-Collectifs'},
            {'key': 'locaux_commerciaux', 'name_ar': 'محلات تجارية ومهنية',
             'name_fr': 'Locaux Commerciaux et à Usage Professionnels'},
            {'key': 'hangars', 'name_ar': 'هنغارات', 'name_fr': 'Hangars'},
            {'key': 'terrains_nus', 'name_ar': 'أراضي فضاء', 'name_fr': 'Terrains Nus'},
            {'key': 'terrains_plaine', 'name_ar': 'أراضي فلاحية في السهل', 'name_fr': 'Terrains Agricoles en Plaine'},
            {'key': 'terrains_pente', 'name_ar': 'أراضي فلاحية في المنحدر', 'name_fr': 'Terrains Agricoles en Pente'},
        ]

        natures_created = 0
        nature_objects = {}

        for nature_data in natures_data:
            nature, created = NatureImmeuble.objects.get_or_create(
                key=nature_data['key'],
                defaults={
                    'name_ar': nature_data['name_ar'],
                    'name_fr': nature_data['name_fr']
                }
            )
            nature_objects[nature_data['key']] = nature
            if created:
                natures_created += 1
                self.stdout.write(f"  ✅ تم إضافة طبيعة العقار: {nature.name_ar}")

        # ========== 3. إضافة الخصائص ==========
        caracteristiques_data = {
            'individuels': [
                {'key': 'standing', 'name_ar': 'رقي', 'name_fr': 'Standing', 'order': 1},
                {'key': 'ameliore', 'name_ar': 'محسن', 'name_fr': 'Amélioré', 'order': 2},
                {'key': 'economique', 'name_ar': 'اقتصادي', 'name_fr': 'Economique', 'order': 3},
                {'key': 'precaire', 'name_ar': 'هش', 'name_fr': 'Précaire', 'order': 4},
            ],
            'collectifs': [
                {'key': 'standing', 'name_ar': 'رقي', 'name_fr': 'Standing', 'order': 1},
                {'key': 'ameliore', 'name_ar': 'محسن', 'name_fr': 'Amélioré', 'order': 2},
                {'key': 'economique', 'name_ar': 'اقتصادي', 'name_fr': 'Economique', 'order': 3},
                {'key': 'precaire', 'name_ar': 'هش', 'name_fr': 'Précaire', 'order': 4},
            ],
            'locaux_commerciaux': [
                {'key': 'artere_haute', 'name_ar': 'شارع عالي التجارة', 'name_fr': 'Artère hautement commerciale',
                 'order': 1},
                {'key': 'artere_moyen', 'name_ar': 'شارع متوسط التجارة', 'name_fr': 'Artère moyennement commerciale',
                 'order': 2},
                {'key': 'artere_faible', 'name_ar': 'شارع قليل التجارة', 'name_fr': 'Artère peu commerciale',
                 'order': 3},
            ],
            'hangars': [
                {'key': 'zone_urbaine', 'name_ar': 'يقع في منطقة حضرية', 'name_fr': 'Situé en zone urbaine',
                 'order': 1},
                {'key': 'zone_rurale', 'name_ar': 'يقع في منطقة ريفية', 'name_fr': 'Situé en zone rurale', 'order': 2},
            ],
            'terrains_nus': [
                {'key': 'pp_2f_avec', 'name_ar': 'ملكية تامة واجهتين مع توصيلات',
                 'name_fr': 'Pleine propriété 2 façades avec raccordements', 'order': 1},
                {'key': 'pp_1f_avec', 'name_ar': 'ملكية تامة واجهة واحدة مع توصيلات',
                 'name_fr': 'Pleine propriété 1 façade avec raccordements', 'order': 2},
                {'key': 'pp_2f_sans', 'name_ar': 'ملكية تامة واجهتين بدون توصيلات',
                 'name_fr': 'Pleine propriété 2 façades sans raccordements', 'order': 3},
                {'key': 'pp_1f_sans', 'name_ar': 'ملكية تامة واجهة واحدة بدون توصيلات',
                 'name_fr': 'Pleine propriété 1 façade sans raccordements', 'order': 4},
                {'key': 'indivision', 'name_ar': 'في الشياع', 'name_fr': "Dans l'indivision", 'order': 5},
                {'key': 'industriel', 'name_ar': 'صناعي', 'name_fr': 'Industriel', 'order': 6},
            ],
            'terrains_plaine': [
                {'key': 'potentialite_elevee', 'name_ar': 'إمكانية عالية', 'name_fr': 'Potentialité élevée',
                 'order': 1},
                {'key': 'potentialite_moyenne', 'name_ar': 'إمكانية متوسطة', 'name_fr': 'Potentialité moyenne',
                 'order': 2},
                {'key': 'potentialite_faible', 'name_ar': 'إمكانية ضعيفة', 'name_fr': 'Potentialité faible',
                 'order': 3},
            ],
            'terrains_pente': [
                {'key': 'potentialite_elevee', 'name_ar': 'إمكانية عالية', 'name_fr': 'Potentialité élevée',
                 'order': 1},
                {'key': 'potentialite_moyenne', 'name_ar': 'إمكانية متوسطة', 'name_fr': 'Potentialité moyenne',
                 'order': 2},
                {'key': 'potentialite_faible', 'name_ar': 'إمكانية ضعيفة', 'name_fr': 'Potentialité faible',
                 'order': 3},
            ],
        }

        carac_created = 0
        for nature_key, carac_list in caracteristiques_data.items():
            nature = nature_objects.get(nature_key)
            if nature:
                for carac_data in carac_list:
                    carac, created = Caracteristique.objects.get_or_create(
                        nature=nature,
                        key=carac_data['key'],
                        defaults={
                            'name_ar': carac_data['name_ar'],
                            'name_fr': carac_data['name_fr'],
                            'order': carac_data['order']
                        }
                    )
                    if created:
                        carac_created += 1
                        self.stdout.write(f"  ✅ تم إضافة الخاصية: {nature.name_ar} → {carac.name_ar}")

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ اكتمل!\n"
            f"   - المناطق: {zones_created}\n"
            f"   - طبائع العقار: {natures_created}\n"
            f"   - الخصائص: {carac_created}"
        ))