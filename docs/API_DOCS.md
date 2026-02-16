# IncluScore API Documentation

**Base URL:** `http://localhost:8000` (dev) · `https://incluscore-api.onrender.com` (prod)

---

## Authentication

Currently open (no auth). For production, add bearer token:

```http
Authorization: Bearer <your-api-key>
```

---

## Endpoints

### `GET /`
**Health check**

Returns API status, model availability, and list of endpoints.

**Response 200:**
```json
{
  "name": "IncluScore API",
  "version": "1.0.0",
  "status": "healthy",
  "model_loaded": true,
  "supabase_connected": false,
  "endpoints": ["/users/{id}", "/predict", "/users/{id}/refresh-score", "/ws/{id}"]
}
```

---

### `GET /users/{user_id}`
**Fetch user profile and financial data**

**Path params:**
- `user_id` (int): 1 = Raj Kumar, 2 = Priya Sharma, 3 = Amit Patel

**Response 200:**
```json
{
  "user": {
    "id": 1,
    "name": "Raj Kumar",
    "age": 32,
    "city": "Mumbai",
    "occupation": "Gig Worker (Delivery)"
  },
  "financial_profile": {
    "upi_transactions": 45,
    "avg_transaction_amount": 320.0,
    "bill_payments_on_time": 18,
    "total_bill_payments": 24,
    "mobile_recharge_regularity": 0.85,
    "savings_pattern": 0.40,
    "monthly_income_estimate": 22000.0,
    "current_score": null
  }
}
```

**Error 404:**
```json
{ "detail": "User not found" }
```

---

### `POST /predict`
**Generate credit score from financial data**

**Request body:**
```json
{
  "upi_transactions": 45,
  "avg_transaction": 320.0,
  "bill_payments_on_time": 18,
  "mobile_recharge_regularity": 0.85,
  "savings_pattern": 0.40
}
```

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `upi_transactions` | int | 0–500 | UPI transactions per month |
| `avg_transaction` | float | ≥0 | Average transaction amount (INR) |
| `bill_payments_on_time` | int | 0–24 | On-time bill payments in last 24 months |
| `mobile_recharge_regularity` | float | 0–1 | Regularity score (1 = every month) |
| `savings_pattern` | float | 0–1 | Savings behavior score (1 = consistent saver) |

**Response 200:**
```json
{
  "credit_score": 712,
  "confidence": 0.89,
  "risk_band": "Good",
  "lender_recommendation": "APPROVE",
  "factors": {
    "Bill Payment History": 37.2,
    "Savings Behavior": 28.1,
    "Mobile Recharge Regularity": 18.4,
    "UPI Transaction Volume": 11.3,
    "Average Transaction Value": 5.0
  },
  "recommendations": [
    "💰 Save even ₹200/month consistently — a regular savings pattern could add up to 90 points.",
    "📱 Maintain a monthly mobile recharge plan — regularity signals financial stability.",
    "📲 Use UPI for everyday purchases — each transaction builds your digital footprint."
  ]
}
```

**Score bands:**
| Band | Range | Lender Decision |
|------|-------|----------------|
| Excellent | 750–900 | APPROVE |
| Good | 650–749 | APPROVE |
| Fair | 550–649 | REVIEW |
| Poor | 300–549 | DENY |

**Error 422 (validation):**
```json
{
  "detail": [
    {
      "loc": ["body", "mobile_recharge_regularity"],
      "msg": "ensure this value is less than or equal to 1",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

### `POST /users/{user_id}/refresh-score`
**Simulate a new positive transaction and recalculate score**

Adds a small positive behavioral event (new UPI transaction, bill payment, etc.) and returns the updated score with the delta.

**Response 200:**
```json
{
  "new_score": 720,
  "delta": 8,
  "confidence": 0.89,
  "message": "New UPI transaction detected! Score improved by +8 points.",
  "factors": { ... }
}
```

---

### `WebSocket /ws/{user_id}`
**Real-time credit scoring stream**

Connect and send UserData JSON to receive ScoreResponse in real-time.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/1');

ws.onopen = () => {
  ws.send(JSON.stringify({
    upi_transactions: 45,
    avg_transaction: 320.0,
    bill_payments_on_time: 18,
    mobile_recharge_regularity: 0.85,
    savings_pattern: 0.40
  }));
};

ws.onmessage = (e) => {
  const result = JSON.parse(e.data);
  console.log('Score:', result.credit_score);
};
```

**Close codes:**
- `1000`: Normal closure
- `1011`: Internal server error during prediction

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 200 | Success |
| 404 | User not found |
| 422 | Validation error (check field ranges) |
| 500 | Internal server error (model or database) |

---

## Interactive Docs

When the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
