from django.db.models import Sum, Case, When, F, BigIntegerField
from .models import LedgerEntry

def get_balance(merchant):
    result = LedgerEntry.objects.filter(merchant=merchant).aggregate(
        balance=Sum(
            Case(
                When(entry_type="credit", then=F("amount_paise")),
                When(entry_type="debit", then=-F("amount_paise")),
                output_field=BigIntegerField()
            )
        )
    )
    return result["balance"] or 0