# properties/management/commands/import_communes.py
import json
from django.core.management.base import BaseCommand
from properties.models_valuation import Wilaya, Commune


class Command(BaseCommand):
    help = 'Import communes from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **options):
        json_file = options['json_file']

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for item in data:
            wilaya_name_ar = item.get('wilaya_name', '').strip()
            wilaya = Wilaya.objects.filter(name_ar=wilaya_name_ar).first()

            if not wilaya:
                self.stdout.write(self.style.WARNING(f"⚠️ ولاية غير موجودة: {wilaya_name_ar}"))
                skipped_count += 1
                continue

            # استخدام update_or_create بدلاً من get_or_create
            commune, created = Commune.objects.update_or_create(
                id=item['id'],
                defaults={
                    'wilaya': wilaya,
                    'name_ar': item['commune_name'],
                    'name_fr': item['commune_name_ascii'],
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            if (created_count + updated_count) % 100 == 0:
                self.stdout.write(f"📊 تمت معالجة {created_count + updated_count} بلدية...")

        self.stdout.write(self.style.SUCCESS(
            f"✅ تم استيراد {created_count} بلدية جديدة، تحديث {updated_count} بلدية، تخطي {skipped_count}"
        ))