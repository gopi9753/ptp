from django.db import transaction
from merchants.models import Merchant
from ledger.models import LedgerEntry
from ledger.services import get_balance
from .models import Payout

@transaction.atomic
def create_payout(merchant_id, amount, bank_account_id, key):

    merchant = Merchant.objects.select_for_update().get(id=merchant_id)

    balance = get_balance(merchant)

    if balance < amount:
        raise Exception("Insufficient balance")

    payout = Payout.objects.create(
        merchant=merchant,
        amount_paise=amount,
        bank_account_id=bank_account_id,
        idempotency_key=key,
        status="pending"
    )

    LedgerEntry.objects.create(
        merchant=merchant,
        amount_paise=amount,
        entry_type="debit",
        reference=f"payout_{payout.id}"
    )

    return payout