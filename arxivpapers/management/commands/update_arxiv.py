from django.core.management.base import BaseCommand
from services import sync_stellar_papers

class Command(BaseCommand):
    help = 'Syncs recent Solar and Stellar Astrophysics papers'

    def handle(self, *args, **options):
        result = sync_stellar_papers()
        self.stdout.write(self.style.SUCCESS(result))
