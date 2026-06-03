from django.core.management.base import BaseCommand
from properties.models import ZoneType, BuildingNature, BuildingCharacteristic

class Command(BaseCommand):
    help = 'إضافة خيارات المناطق وطبائع العقار وخصائصها'

    def handle(self, *args, **options):
        # --- إضافة أنواع المناطق ---
        zones = [
            "Zone résidentielle", "Centre-ville", "Zone périphérique", "Zone d’éloignement"
        ]
        for zone in zones:
            obj, created = ZoneType.objects.get_or_create(name_ar=zone, defaults={"name_fr": zone})
            self.stdout.write(f"{'أضيف' if created else 'موجود'}: {zone}")

        # --- إضافة طبائع العقار (BuildingNature) ---
        natures = [
            "Individuels", "Collectifs et Semi-Collectifs",
            "Locaux Commerciaux et Locaux à Usage Professionnels",
            "Hangars", "Terrains Nus", "Terrains Agricoles en Plaine",
            "Terrains Agricoles en Pente"
        ]
        nature_objects = {}
        for nature in natures:
            obj, created = BuildingNature.objects.get_or_create(name_ar=nature, defaults={"name_fr": nature})
            nature_objects[nature] = obj
            self.stdout.write(f"{'أضيف' if created else 'موجود'}: {nature}")

        # --- إضافة الخصائص (BuildingCharacteristic) حسب كل طبيعة ---
        characteristics_data = {
            "Individuels": ["Standing", "Amélioré", "Economique", "Précaire"],
            "Collectifs et Semi-Collectifs": ["Standing", "Amélioré", "Economique", "Précaire"],
            "Locaux Commerciaux et Locaux à Usage Professionnels": [
                "Artère hautement commerciale", "Artère moyennement commerciale", "Artère peu commerciale"
            ],
            "Hangars": ["Situé en zone urbaine", "Situé en zone rurale"],
            "Terrains Nus": [
                "Pleine propriété deux (02) façades avec raccordements",
                "Pleine propriété une (01) façade avec raccordements",
                "Pleine propriété deux (02) façades sans raccordements",
                "Pleine propriété une (01) façade sans raccordements",
                "Dans l'indivision",
                "Industriel"
            ],
            "Terrains Agricoles en Plaine": ["Potentialité élevée", "Potentialité moyenne", "Potentialité faible"],
            "Terrains Agricoles en Pente": ["Potentialité élevée", "Potentialité moyenne", "Potentialité faible"],
        }

        for nature_name, chars in characteristics_data.items():
            nature = nature_objects[nature_name]
            for char in chars:
                obj, created = BuildingCharacteristic.objects.get_or_create(
                    nature=nature, name_ar=char, defaults={"name_fr": char}
                )
                self.stdout.write(f"{'أضيف' if created else 'موجود'}: {nature_name} -> {char}")

        self.stdout.write(self.style.SUCCESS("تمت إضافة جميع الخيارات بنجاح."))