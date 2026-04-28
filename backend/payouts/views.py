from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction

from merchants.models import Merchant
from idempotency.models import IdempotencyKey
from ledger.services import get_balance
from .services import create_payout

class BalanceView(APIView):
    def get(self, request):
        merchant = Merchant.objects.first()
        return Response({"balance": get_balance(merchant)})

class PayoutView(APIView):

    @transaction.atomic
    def post(self, request):
        merchant = Merchant.objects.first()
        key = request.headers.get("Idempotency-Key")

        idem, created = IdempotencyKey.objects.select_for_update().get_or_create(
            merchant=merchant,
            key=key
        )

        if not created and idem.response:
            return Response(idem.response)

        if not created and idem.in_progress:
            return Response({"message": "Request in progress"}, status=409)

        payout = create_payout(
            merchant.id,
            request.data["amount_paise"],
            request.data["bank_account_id"],
            key
        )

        response = {"payout_id": payout.id, "status": payout.status}

        idem.response = response
        idem.in_progress = False
        idem.save()

        return Response(response)