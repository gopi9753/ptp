# EXPLAINER.md

## 1. Ledger Design

Balance is NOT stored directly.

It is derived using:

```sql
SELECT COALESCE(SUM(
  CASE 
    WHEN entry_type = 'credit' THEN amount_paise
    ELSE -amount_paise
  END
), 0)
FROM ledger_entry
WHERE merchant_id = %s;
```

### Why this design?

* Prevents inconsistency
* Fully auditable
* Supports reconciliation
* Avoids race conditions

---

## 2. Concurrency Handling (Critical)

Code:

```python
with transaction.atomic():
    merchant = Merchant.objects.select_for_update().get(id=merchant_id)
```

### Explanation:

* Uses DB-level row locking
* Prevents simultaneous balance deductions
* Ensures only one payout succeeds when balance is insufficient

---

## 3. Idempotency

Stored in `IdempotencyKey` table.

Flow:

1. Check if key exists
2. If yes → return stored response
3. If no → process request + save response

### Edge case handled:

If two requests come simultaneously:

* One succeeds
* Second reads stored response

---

## 4. State Machine

Valid transitions:

* pending → processing → completed
* pending → processing → failed

Invalid transitions are blocked in model/service layer.

Example:

```python
if payout.status == "completed":
    raise Exception("Invalid transition")
```

---

## 5. Retry Logic

* Processing > 30 seconds → retry
* Exponential backoff
* Max retries = 3
* After that → mark failed + refund

---

## 6. Money Integrity

* Stored as BigInteger (paise)
* No float/decimal rounding errors
* All updates done via DB transactions

---

## 7. AI Audit (Important)

### ❌ AI-generated issue:

Initial code used:

```python
balance = sum(entries)
```

Problem:

* Not atomic
* Race condition risk

### ✅ Fix:

Replaced with DB aggregation:

```python
LedgerEntry.objects.aggregate(...)
```

### Result:

* Safe
* Accurate
* Scalable

---

## 8. Deployment Notes

* Hosted on Render
* PostgreSQL + Redis configured
* Migrations handled at startup
