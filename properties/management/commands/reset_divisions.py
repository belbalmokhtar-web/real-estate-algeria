from django.core.management.base import BaseCommand
from django.db import transaction
from properties.models import Wilaya, Commune

class Command(BaseCommand):
    help = 'Delete all wilayas and communes (reset divisions).'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force deletion without confirmation')

    def handle(self, *args, **options):
        if not options['force']:
            confirm = input('This will delete ALL wilayas and communes. Are you sure? (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write('Operation cancelled.')
                return

        with transaction.atomic():
            Commune.objects.all().delete()
            Wilaya.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All divisions have been deleted.'))