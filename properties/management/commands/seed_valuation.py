# properties/management/commands/seed_valuation.py
# python manage.py seed_valuation

from django.core.management.base import BaseCommand
from properties.models_valuation import NatureImmeuble, Caracteristique, Zone


ZONES = [
    {"key": "residential", "name_fr": "Zone résidentielle",  "name_ar": "المنطقة السكنية"},
    {"key": "city_center",  "name_fr": "Centre-ville",        "name_ar": "وسط المدينة"},
    {"key": "peripheral",   "name_fr": "Zone périphérique",   "name_ar": "المنطقة المحيطية"},
    {"key": "remote",       "name_fr": "Zone d'éloignement",  "name_ar": "المنطقة النائية"},
]

# nature_key → [(carac_key, name_fr, name_ar), ...]
NATURE_DATA = {
    "individuels": {
        "name_fr": "Individuels",
        "name_ar": "أفراد (منازل فردية)",
        "caracs": [
            ("standing",   "Standing",   "ستاندينغ"),
            ("ameliore",   "Amélioré",   "محسّن"),
            ("economique", "Economique", "اقتصادي"),
            ("precaire",   "Précaire",   "هش"),
        ],
    },
    "collectifs": {
        "name_fr": "Collectifs et Semi-Collectifs",
        "name_ar": "جماعية وشبه جماعية",
        "caracs": [
            ("standing",   "Standing",   "ستاندينغ"),
            ("ameliore",   "Amélioré",   "محسّن"),
            ("economique", "Economique", "اقتصادي"),
            ("precaire",   "Précaire",   "هش"),
        ],
    },
    "locaux_commerciaux": {
        "name_fr": "Locaux Commerciaux et Locaux à Usage Professionnels",
        "name_ar": "محلات تجارية ومهنية",
        "caracs": [
            ("artere_haute",  "Artère hautement commerciale",   "شارع تجاري مرتفع"),
            ("artere_moyen",  "Artère moyennement commerciale", "شارع تجاري متوسط"),
            ("artere_faible", "Artère peu commerciale",         "شارع تجاري ضعيف"),
        ],
    },
    "hangars": {
        "name_fr": "Hangars",
        "name_ar": "مستودعات",
        "caracs": [
            ("zone_urbaine", "Situé en zone urbaine", "في منطقة حضرية"),
            ("zone_rurale",  "Situé en zone rurale",  "في منطقة ريفية"),
        ],
    },
    "terrains_nus": {
        "name_fr": "Terrains Nus",
        "name_ar": "أراضي عارية",
        "caracs": [
            ("pp_2f_avec", "Pleine propriété 2 façades avec raccordements",    "ملكية تامة 2 واجهة مع توصيلات"),
            ("pp_1f_avec", "Pleine propriété 1 façade avec raccordements",     "ملكية تامة 1 واجهة مع توصيلات"),
            ("pp_2f_sans", "Pleine propriété 2 façades sans raccordements",    "ملكية تامة 2 واجهة بدون توصيلات"),
            ("pp_1f_sans", "Pleine propriété 1 façade sans raccordements",     "ملكية تامة 1 واجهة بدون توصيلات"),
            ("indivision", "Dans l'indivision",                                "في الشياع"),
            ("industriel", "Industriel",                                        "صناعي"),
        ],
    },
    "terrains_plaine": {
        "name_fr": "Terrains Agricoles en Plaine",
        "name_ar": "أراضي زراعية سهلية",
        "caracs": [
            ("potentialite_elevee",  "Potentialité élevée",  "إمكانية عالية"),
            ("potentialite_moyenne", "Potentialité moyenne", "إمكانية متوسطة"),
            ("potentialite_faible",  "Potentialité faible",  "إمكانية ضعيفة"),
        ],
    },
    "terrains_pente": {
        "name_fr": "Terrains Agricoles en Pente",
        "name_ar": "أراضي زراعية منحدرة",
        "caracs": [
            ("potentialite_elevee",  "Potentialité élevée",  "إمكانية عالية"),
            ("potentialite_moyenne", "Potentialité moyenne", "إمكانية متوسطة"),
            ("potentialite_faible",  "Potentialité faible",  "إمكانية ضعيفة"),
        ],
    },
}


class Command(BaseCommand):
    help = "Seed Zones, NatureImmeuble and Caracteristique tables"

    def handle(self, *args, **options):
        # Zones
        for z in ZONES:
            obj, created = Zone.objects.update_or_create(
                key=z["key"],
                defaults={"name_fr": z["name_fr"], "name_ar": z["name_ar"]}
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} zone: {obj}")

        # Natures + Caracteristiques
        for nature_key, data in NATURE_DATA.items():
            nature, created = NatureImmeuble.objects.update_or_create(
                key=nature_key,
                defaults={"name_fr": data["name_fr"], "name_ar": data["name_ar"]}
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} nature: {nature}")

            for order, (carac_key, name_fr, name_ar) in enumerate(data["caracs"]):
                carac, c2 = Caracteristique.objects.update_or_create(
                    nature=nature,
                    key=carac_key,
                    defaults={"name_fr": name_fr, "name_ar": name_ar, "order": order}
                )
                self.stdout.write(f"  {'Created' if c2 else 'Updated'} carac: {carac}")

        self.stdout.write(self.style.SUCCESS("\n✅ Seed completed successfully!"))