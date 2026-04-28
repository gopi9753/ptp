from celery import shared_task
from django.db import transaction
from .models import Payout
from ledger.models import LedgerEntry
import random

@shared_task
def process_payout(payout_id):

    with transaction.atomic():
        payout = Payout.objects.select_for_update().get(id=payout_id)

        if payout.status != "pending":
            return

        payout.transition("processing")

    r = random.random()

    if r < 0.7:
        payout.transition("completed")

    elif r < 0.9:
        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(id=payout_id)

            payout.transition("failed")

            LedgerEntry.objects.create(
                merchant=payout.merchant,
                amount_paise=payout.amount_paise,
                entry_type="credit",
                reference=f"refund_{payout.id}"
            )