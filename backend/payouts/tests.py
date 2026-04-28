from django.test import TransactionTestCase, TestCase
import threading
from merchants.models import Merchant
from ledger.models import LedgerEntry

class ConcurrencyTest(TransactionTestCase):

    def setUp(self):
        self.merchant = Merchant.objects.create(name="Test")
        LedgerEntry.objects.create(
            merchant=self.merchant,
            amount_paise=10000,
            entry_type="credit",
            reference="seed"
        )

    def test_double_payout(self):
        from payouts.services import create_payout

        def run():
            try:
                create_payout(self.merchant.id, 6000, "123", "k")
            except:
                pass

        t1 = threading.Thread(target=run)
        t2 = threading.Thread(target=run)

        t1.start(); t2.start()
        t1.join(); t2.join()

        from payouts.models import Payout
        assert Payout.objects.count() == 1


class IdempotencyTest(TestCase):

    def test_same_key(self):
        key = "abc"

        r1 = self.client.post("/api/v1/payouts",
            {"amount_paise": 1000, "bank_account_id": "1"},
            HTTP_IDEMPOTENCY_KEY=key
        )

        r2 = self.client.post("/api/v1/payouts",
            {"amount_paise": 1000, "bank_account_id": "1"},
            HTTP_IDEMPOTENCY_KEY=key
        )

        assert r1.json() == r2.json()