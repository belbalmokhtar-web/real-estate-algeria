# properties/management/commands/import_projets.py
import re
from django.core.management.base import BaseCommand
from properties.models import PromoteurImmobilier, ProjetImmobilier
from properties.models_valuation import Wilaya, Commune


class Command(BaseCommand):
    help = 'استيراد بيانات المشاريع العقارية (بيانات تجريبية)'

    def handle(self, *args, **options):
        # هذه بيانات تجريبية من الموقع
        projets_data = [
            {
                'nom_projet': '131 LOGTS - KOLEA - TIPAZA',
                'promoteur_nom': 'TOUDERT HAYAT',
                'localisation': 'Section 005 Ilot 719, Route de Blida, Daira : Kolea',
                'wilaya': 'TIPAZA',
                'daira': 'Kolea',
                'f2': 19, 'f3': 37, 'f4': 74, 'f5': 1,
                'date_garantie': '2015-01-17',
            },
            {
                'nom_projet': '24/270 LOGTS - THENIA - BOUMERDES',
                'promoteur_nom': 'MERCHICHI SAID',
                'localisation': 'Beni Arab, Daira : Thenia',
                'wilaya': 'BOUMERDES',
                'daira': 'Thenia',
                'f4': 24,
                'date_garantie': '2014-03-23',
            },
            # أضف باقي المشاريع من الموقع هنا
        ]

        created = 0

        for data in projets_data:
            promoteur = PromoteurImmobilier.objects.filter(
                nom_entreprise__icontains=data['promoteur_nom']
            ).first()

            if not promoteur:
                self.stdout.write(self.style.WARNING(f"⚠️ لم يتم العثور على المطور: {data['promoteur_nom']}"))
                continue

            wilaya = Wilaya.objects.filter(name_fr=data['wilaya']).first()

            projet, is_new = ProjetImmobilier.objects.get_or_create(
                nom_projet=data['nom_projet'],
                promoteur=promoteur,
                defaults={
                    'localisation': data['localisation'],
                    'wilaya': wilaya,
                    'daira': data.get('daira', ''),
                    'f2_count': data.get('f2', 0),
                    'f3_count': data.get('f3', 0),
                    'f4_count': data.get('f4', 0),
                    'f5_count': data.get('f5', 0),
                    'date_garantie': data.get('date_garantie'),
                }
            )

            if is_new:
                projet.update_total()
                created += 1

        self.stdout.write(self.style.SUCCESS(f"✅ تم استيراد {created} مشروع"))