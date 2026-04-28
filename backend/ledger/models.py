from django.db import models

class LedgerEntry(models.Model):
    merchant = models.ForeignKey("merchants.Merchant", on_delete=models.CASCADE)
    amount_paise = models.BigIntegerField()
    entry_type = models.CharField(max_length=10)
    reference = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)