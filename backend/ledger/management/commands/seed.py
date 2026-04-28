from django.core.management.base import BaseCommand
from merchants.models import Merchant
from ledger.models import LedgerEntry

class Command(BaseCommand):
    help = "Seed initial data"

    def handle(self, *args, **kwargs):
        if Merchant.objects.exists():
            self.stdout.write(self.style.WARNING("Already seeded"))
            return

        m = Merchant.objects.create(name="Live Merchant")

        LedgerEntry.objects.create(
            merchant=m,
            amount_paise=20000,
            entry_type="credit",
            reference="seed"
        )

        self.stdout.write(self.style.SUCCESS("Seed data created"))