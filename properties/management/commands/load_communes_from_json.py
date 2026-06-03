import json
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from properties.models import Wilaya, Commune

class Command(BaseCommand):
    help = 'Load wilayas and communes from a JSON list of communes (fields: wilaya_code, wilaya_name, wilaya_name_ascii, commune_name, commune_name_ascii, id)'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='Path to JSON file')
        parser.add_argument('--clear', action='store_true', help='Clear existing data')

    def handle(self, *args, **options):
        file_path = Path(options['file'])
        clear = options['clear']

        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        # قراءة الملف وإصلاح الفواصل الزائدة
        content = file_path.read_text(encoding='utf-8')
        fixed_content = re.sub(r',\s*([}\]])', r'\1', content)
        try:
            data = json.loads(fixed_content)
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f'JSON error: {e}'))
            return

        if not isinstance(data, list):
            self.stderr.write(self.style.ERROR('JSON root must be a list of communes'))
            return

        with transaction.atomic():
            if clear:
                Commune.objects.all().delete()
                Wilaya.objects.all().delete()
                self.stdout.write('Cleared existing data.')

            wilayas_cache = {}
            communes_created = 0
            total = len(data)

            for idx, item in enumerate(data, 1):
                wilaya_code = str(item.get('wilaya_code', '')).strip()
                wilaya_name_ar = item.get('wilaya_name', '').strip()
                wilaya_name_fr = item.get('wilaya_name_ascii', '').strip()

                if not wilaya_code or not wilaya_name_ar:
                    self.stdout.write(self.style.WARNING(f'Skipping item {idx}: missing wilaya info'))
                    continue

                # إنشاء أو استرجاع الولاية
                if wilaya_code not in wilayas_cache:
                    wilaya, created = Wilaya.objects.get_or_create(
                        code=wilaya_code,
                        defaults={'name_ar': wilaya_name_ar, 'name_fr': wilaya_name_fr or wilaya_name_ar}
                    )
                    wilayas_cache[wilaya_code] = wilaya
                    if created:
                        self.stdout.write(f"Added wilaya: {wilaya_code} - {wilaya_name_ar}")

                wilaya = wilayas_cache[wilaya_code]

                # استخراج بيانات البلدية
                commune_name_ar = item.get('commune_name', '').strip()
                if not commune_name_ar:
                    continue

                commune_name_fr = item.get('commune_name_ascii', '').strip() or commune_name_ar
                commune_code = str(item.get('id', ''))

                if not commune_code:
                    self.stdout.write(self.style.WARNING(f'Skipping commune without id for wilaya {wilaya_code}'))
                    continue

                # إنشاء البلدية
                commune, created = Commune.objects.get_or_create(
                    code=commune_code,
                    wilaya=wilaya,
                    defaults={'name_ar': commune_name_ar, 'name_fr': commune_name_fr}
                )
                if created:
                    communes_created += 1

                # عرض التقدم كل 500 عنصر
                if idx % 500 == 0:
                    self.stdout.write(f'Processed {idx}/{total} items...')

            self.stdout.write(self.style.SUCCESS(
                f'Successfully loaded {len(wilayas_cache)} wilayas and {communes_created} communes.'
            ))