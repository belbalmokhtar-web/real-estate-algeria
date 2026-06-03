# properties/management/commands/import_promoteurs.py
import pandas as pd
from django.core.management.base import BaseCommand
from properties.models_valuation import Wilaya, Commune
from properties.models import PromoteurImmobilier, ProjetImmobilier
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'استيراد بيانات المطورين العقاريين من ملف Excel'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='مسار ملف Excel')

    def handle(self, *args, **options):
        excel_file = options['excel_file']

        self.stdout.write(f"📖 جاري قراءة ملف {excel_file}...")

        # قراءة البيانات
        df = pd.read_excel(excel_file, sheet_name='Promoteurs FGCMPI')

        # قاموس لتخزين أسماء الولايات وبياناتها
        wilaya_map = {w.name_ar: w for w in Wilaya.objects.all()}
        wilaya_map.update({w.name_fr: w for w in Wilaya.objects.all()})

        promoteurs_created = 0
        promoteurs_updated = 0

        for index, row in df.iterrows():
            wilaya_name = row.get('الولاية', '')
            wilaya = wilaya_map.get(wilaya_name)

            # إنشاء أو تحديث المطور
            promoteur, created = PromoteurImmobilier.objects.update_or_create(
                numero_affiliation=str(row.get('رقم الانتساب', '')).strip(),
                defaults={
                    'numero_agrement': str(row.get('رقم الاعتماد', '')).strip(),
                    'numero_tnpi': str(row.get('رقم التسجيل TNPI', '')).strip(),
                    'nom_entreprise': str(row.get('اسم الشركة', '')).strip(),
                    'nom_gerant': str(row.get('المسير', '')).strip(),
                    'adresse': str(row.get('العنوان التجاري', '')).strip(),
                    'telephone': str(row.get('الهاتف', '')).strip(),
                    'wilaya': wilaya,
                }
            )

            if created:
                promoteurs_created += 1
            else:
                promoteurs_updated += 1

            if (index + 1) % 20 == 0:
                self.stdout.write(f"📊 تمت معالجة {index + 1} مطور...")

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ اكتمل استيراد المطورين!\n"
            f"   - تم إنشاء: {promoteurs_created}\n"
            f"   - تم تحديث: {promoteurs_updated}\n"
            f"   - إجمالي المطورين: {PromoteurImmobilier.objects.count()}"
        ))