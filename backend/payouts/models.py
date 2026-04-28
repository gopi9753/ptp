from django.db import models

class Payout(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    merchant = models.ForeignKey("merchants.Merchant", on_delete=models.CASCADE)
    amount_paise = models.BigIntegerField()
    bank_account_id = models.CharField(max_length=255)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    retries = models.IntegerField(default=0)

    idempotency_key = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def transition(self, new_status):
        allowed = {
            "pending": ["processing"],
            "processing": ["completed", "failed"],
        }

        if self.status not in allowed or new_status not in allowed[self.status]:
            raise Exception("Invalid transition")

        self.status = new_status
        self.save()