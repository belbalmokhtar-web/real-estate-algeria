from django.core.management.base import BaseCommand
from properties.models import BuildingNature, BuildingCharacteristic

class Command(BaseCommand):
    help = 'تحميل بيانات طبيعة المباني وخصائصها'

    def handle(self, *args, **options):
        data = {
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

        for nature_ar, characteristics in data.items():
            nature, created = BuildingNature.objects.get_or_create(name_ar=nature_ar)
            for char_ar in characteristics:
                BuildingCharacteristic.objects.get_or_create(nature=nature, name_ar=char_ar)
                self.stdout.write(f"Added: {nature_ar} -> {char_ar}")
        self.stdout.write(self.style.SUCCESS("Data loaded successfully"))