# EXPLAINER.md

## 1. System Overview

This system implements a payout engine where:

* Merchants receive credits (international payments)
* Merchants request payouts (bank transfers)
* System ensures correctness under concurrency and retries

---

## 2. Ledger-Based Accounting (Core Design)

Balance is NOT stored as a column.

Instead, it is derived from ledger entries:

* credit → adds balance
* debit → reduces balance

### Why this approach?

* Prevents data inconsistency
* Fully auditable (every transaction stored)
* Easy rollback via compensating entries
* Eliminates race conditions from direct balance updates

### Tradeoff

* Slightly slower reads (aggregation)
* Solved using DB aggregation + indexing

---

## 3. Balance Calculation

Balance is computed using DB aggregation:

```sql
SUM(CASE 
  WHEN entry_type='credit' THEN amount_paise
  ELSE -amount_paise
END)
```

### Why DB-level aggregation?

* Atomic and consistent
* Avoids stale application-level calculations
* Scales with DB optimization

---

## 4. Concurrency Handling (Critical Section)

When creating a payout:

```python
with transaction.atomic():
    merchant = Merchant.objects.select_for_update().get(id=merchant_id)
```

### Why this works

* Locks the merchant row
* Prevents concurrent updates
* Ensures only one payout can deduct balance at a time

### Example scenario

Two requests with ₹100 balance:

* Request A → locks row → succeeds
* Request B → waits → fails if balance insufficient

---

## 5. Idempotency (Production Requirement)

Each payout request uses:

```
Idempotency-Key header
```

### Flow

1. Check if key exists
2. If yes → return stored response
3. If no → process + store result

### Why this is important

* Prevents duplicate payouts
* Handles client retries safely
* Guarantees exactly-once semantics

---

## 6. State Machine Design

Payout states:

* pending
* processing
* completed
* failed

### Valid transitions

* pending → processing
* processing → completed
* processing → failed

Invalid transitions are blocked.

### Why this matters

* Prevents inconsistent states
* Makes system predictable
* Enables retry logic safely

---

## 7. Retry & Failure Handling

If payout processing fails:

* Retry with exponential backoff
* Max retries = 3
* If still failing:

  * mark payout as failed
  * reverse ledger entry (refund)

### Why this design

* Ensures money is never lost
* Handles transient failures (network/bank API)

---

## 8. Money Precision

* All amounts stored as **paise (integer)**
* No floating point operations

### Why

* Avoids rounding errors
* Industry-standard approach for financial systems

---

## 9. Data Integrity Guarantees

System guarantees:

* No double spending
* No negative balance (checked before debit)
* All operations wrapped in DB transactions

---

## 10. Scalability Considerations

* DB row-level locking ensures correctness
* Can be extended with:

  * sharding merchants
  * read replicas for balance queries
  * async payout processing (Celery)

---

## 11. AI Usage & Corrections

AI was used for scaffolding but had issues:

### Issue:

Used application-level sum → race condition

### Fix:

Moved to DB-level aggregation + locking

### Result:

Production-safe logic

---

## 12. Deployment

* Hosted on Render
* PostgreSQL for persistence
* Redis for background jobs
* Gunicorn for production serving

---

## 13. Key Design Decisions Summary

| Problem             | Solution         |
| ------------------- | ---------------- |
| Double spending     | Row locking      |
| Duplicate API calls | Idempotency keys |
| Money accuracy      | Integer (paise)  |
| Auditability        | Ledger system    |
| Failures            | Retry + refund   |

---

## 14. What I Would Improve Next

* Add API authentication
* Add rate limiting
* Add monitoring (Prometheus)
* Add distributed locking for multi-node scaling
* Introduce event-driven architecture (Kafka)

---

## Conclusion

This system prioritizes:

* correctness over convenience
* consistency over speed
* auditability over simplicity

It is designed to behave predictably under real-world failures and concurrency.
