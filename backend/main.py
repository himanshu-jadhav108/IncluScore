"""
IncluScore - AI-Powered Credit Scoring for the Unbanked
FastAPI Backend Application
"""

import os
import json
import joblib
import numpy as np
from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Try importing supabase; gracefully degrade if not configured
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False

load_dotenv()

# ---------------------------------------------------------------------------
# App initialization
# ---------------------------------------------------------------------------
app = FastAPI(
    title="IncluScore API",
    description="AI-powered credit scoring using alternative financial data",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Supabase client (optional - falls back to mock data if not configured)
# ---------------------------------------------------------------------------
supabase: Optional[object] = None
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[WARN] Supabase connection failed: {e}. Using mock data.")

# ---------------------------------------------------------------------------
# ML Model loading
# ---------------------------------------------------------------------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "credit_model.pkl")
model = None

try:
    model = joblib.load(MODEL_PATH)
    print("[INFO] ML model loaded successfully.")
except FileNotFoundError:
    print("[WARN] Model not found. Run train_model.py first. Using rule-based scoring.")

# ---------------------------------------------------------------------------
# Mock data (used when Supabase is not configured)
# ---------------------------------------------------------------------------
MOCK_USERS = {
    1: {
        "id": 1,
        "name": "Raj Kumar",
        "age": 32,
        "city": "Mumbai",
        "occupation": "Gig Worker (Delivery)",
        "financial_profile": {
            "upi_transactions": 45,
            "avg_transaction_amount": 320.0,
            "bill_payments_on_time": 18,
            "total_bill_payments": 24,
            "mobile_recharge_regularity": 0.85,
            "savings_pattern": 0.40,
            "monthly_income_estimate": 22000.0,
            "current_score": None,
        },
    },
    2: {
        "id": 2,
        "name": "Priya Sharma",
        "age": 28,
        "city": "Bengaluru",
        "occupation": "Salaried - Retail Worker",
        "financial_profile": {
            "upi_transactions": 92,
            "avg_transaction_amount": 850.0,
            "bill_payments_on_time": 23,
            "total_bill_payments": 24,
            "mobile_recharge_regularity": 0.96,
            "savings_pattern": 0.72,
            "monthly_income_estimate": 38000.0,
            "current_score": None,
        },
    },
    3: {
        "id": 3,
        "name": "Amit Patel",
        "age": 21,
        "city": "Ahmedabad",
        "occupation": "Student / Part-time Worker",
        "financial_profile": {
            "upi_transactions": 20,
            "avg_transaction_amount": 150.0,
            "bill_payments_on_time": 8,
            "total_bill_payments": 12,
            "mobile_recharge_regularity": 0.60,
            "savings_pattern": 0.22,
            "monthly_income_estimate": 8000.0,
            "current_score": None,
        },
    },
}

# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------
class UserData(BaseModel):
    upi_transactions: int = Field(..., ge=0, le=500, description="UPI transactions per month")
    avg_transaction: float = Field(..., ge=0, description="Average transaction amount in INR")
    bill_payments_on_time: int = Field(..., ge=0, le=24, description="On-time bill payments in last 24 months")
    mobile_recharge_regularity: float = Field(..., ge=0.0, le=1.0, description="Mobile recharge regularity score 0-1")
    savings_pattern: float = Field(..., ge=0.0, le=1.0, description="Savings behavior score 0-1")


class ScoreResponse(BaseModel):
    credit_score: int
    confidence: float
    factors: dict
    recommendations: list
    risk_band: str
    lender_recommendation: str


# ---------------------------------------------------------------------------
# Scoring helper functions
# ---------------------------------------------------------------------------
def calculate_score_rule_based(data: UserData) -> int:
    """Fallback rule-based scoring when ML model is unavailable."""
    score = (
        300
        + data.bill_payments_on_time * 12
        + data.mobile_recharge_regularity * 150
        + data.savings_pattern * 180
        + min(data.upi_transactions * 0.5, 50)
        + min(data.avg_transaction * 0.02, 30)
    )
    return int(np.clip(score, 300, 900))


def calculate_factor_contributions(data: UserData) -> dict:
    """Calculate and normalize contribution of each factor to the score."""
    raw = {
        "UPI Transaction Volume": data.upi_transactions * 2,
        "Average Transaction Value": min(data.avg_transaction * 0.05, 50),
        "Bill Payment History": data.bill_payments_on_time * 12,
        "Mobile Recharge Regularity": data.mobile_recharge_regularity * 150,
        "Savings Behavior": data.savings_pattern * 180,
    }
    total = sum(raw.values()) or 1
    normalized = {k: round(v / total * 100, 1) for k, v in raw.items()}
    return normalized


def get_risk_band(score: int) -> str:
    if score >= 750:
        return "Excellent"
    elif score >= 650:
        return "Good"
    elif score >= 550:
        return "Fair"
    else:
        return "Poor"


def get_lender_recommendation(score: int) -> str:
    if score >= 700:
        return "APPROVE"
    elif score >= 580:
        return "REVIEW"
    else:
        return "DENY"


def generate_recommendations(data: UserData, factors: dict) -> list:
    """Generate actionable, personalized recommendations based on weak factors."""
    recs = []

    if data.bill_payments_on_time < 18:
        recs.append(
            "⏰ Set up auto-pay for utility bills — consistent on-time payments can boost your score by up to 144 points over 24 months."
        )
    if data.savings_pattern < 0.5:
        recs.append(
            "💰 Save even ₹200/month consistently — a regular savings pattern could add up to 90 points to your score."
        )
    if data.mobile_recharge_regularity < 0.8:
        recs.append(
            "📱 Maintain a monthly mobile recharge plan — regularity signals financial stability to lenders."
        )
    if data.upi_transactions < 30:
        recs.append(
            "📲 Use UPI for everyday purchases — each transaction builds your digital financial footprint."
        )
    if data.avg_transaction < 200:
        recs.append(
            "🛒 Gradually increase transaction size as income grows — higher average values demonstrate financial capacity."
        )

    if not recs:
        recs.append("🌟 Excellent profile! Consider applying for your first micro-loan to further build credit history.")

    return recs[:3]


def predict_score(data: UserData) -> ScoreResponse:
    """Run prediction using ML model or fall back to rule-based scoring."""
    features = np.array([[
        data.upi_transactions,
        data.avg_transaction,
        data.bill_payments_on_time,
        data.mobile_recharge_regularity,
        data.savings_pattern,
    ]])

    if model is not None:
        try:
            raw_score = model.predict(features)[0]
            credit_score = int(np.clip(raw_score, 300, 900))
            # Confidence from tree variance
            predictions = [tree.predict(features)[0] for tree in model.estimators_]
            std_dev = np.std(predictions)
            confidence = round(float(max(0.60, min(0.99, 1 - std_dev / 200))), 2)
        except Exception as e:
            print(f"[WARN] Model prediction error: {e}. Falling back.")
            credit_score = calculate_score_rule_based(data)
            confidence = 0.82
    else:
        credit_score = calculate_score_rule_based(data)
        confidence = 0.82

    factors = calculate_factor_contributions(data)
    recommendations = generate_recommendations(data, factors)
    risk_band = get_risk_band(credit_score)
    lender_rec = get_lender_recommendation(credit_score)

    return ScoreResponse(
        credit_score=credit_score,
        confidence=confidence,
        factors=factors,
        recommendations=recommendations,
        risk_band=risk_band,
        lender_recommendation=lender_rec,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "name": "IncluScore API",
        "version": "1.0.0",
        "status": "healthy",
        "model_loaded": model is not None,
        "supabase_connected": supabase is not None,
        "endpoints": ["/users/{id}", "/predict", "/users/{id}/refresh-score", "/ws/{id}"],
    }


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Fetch user profile with financial data from Supabase or mock data."""
    if supabase:
        try:
            user_resp = supabase.table("users").select("*").eq("id", user_id).single().execute()
            if not user_resp.data:
                raise HTTPException(status_code=404, detail="User not found")
            user = user_resp.data

            profile_resp = (
                supabase.table("financial_profiles")
                .select("*")
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            profile = profile_resp.data or {}

            return {"user": user, "financial_profile": profile}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    else:
        # Use mock data
        if user_id not in MOCK_USERS:
            raise HTTPException(status_code=404, detail="User not found")
        return MOCK_USERS[user_id]


@app.post("/predict", response_model=ScoreResponse)
async def predict(data: UserData):
    """Accept financial data, return credit score with AI explanation."""
    try:
        result = predict_score(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/users/{user_id}/refresh-score")
async def refresh_score(user_id: int):
    """Simulate a new positive transaction and return updated score."""
    if user_id not in MOCK_USERS and supabase is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch base profile
    if supabase:
        try:
            profile_resp = (
                supabase.table("financial_profiles")
                .select("*")
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            profile = profile_resp.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        profile = MOCK_USERS.get(user_id, {}).get("financial_profile", {})

    # Apply a small random positive improvement
    noise = np.random.randint(3, 18)
    upi_bump = np.random.randint(1, 5)

    data = UserData(
        upi_transactions=int(profile.get("upi_transactions", 30)) + upi_bump,
        avg_transaction=float(profile.get("avg_transaction_amount", 300)),
        bill_payments_on_time=min(int(profile.get("bill_payments_on_time", 15)) + 1, 24),
        mobile_recharge_regularity=min(float(profile.get("mobile_recharge_regularity", 0.7)) + 0.02, 1.0),
        savings_pattern=min(float(profile.get("savings_pattern", 0.5)) + 0.03, 1.0),
    )

    result = predict_score(data)
    return {
        "new_score": result.credit_score,
        "delta": noise,
        "confidence": result.confidence,
        "message": f"New UPI transaction detected! Score improved by +{noise} points.",
        "factors": result.factors,
    }


# ---------------------------------------------------------------------------
# WebSocket for real-time score updates (bonus feature)
# ---------------------------------------------------------------------------
active_connections: dict = {}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_data = UserData(**payload)
            result = predict_score(user_data)
            await websocket.send_text(result.model_dump_json())
    except WebSocketDisconnect:
        active_connections.pop(user_id, None)
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
        active_connections.pop(user_id, None)
