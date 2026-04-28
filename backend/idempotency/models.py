from django.db import models

class IdempotencyKey(models.Model):
    merchant = models.ForeignKey("merchants.Merchant", on_delete=models.CASCADE)
    key = models.CharField(max_length=255)

    response = models.JSONField(null=True, blank=True)
    in_progress = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("merchant", "key")