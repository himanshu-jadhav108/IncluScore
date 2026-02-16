"""
IncluScore - ML Model Training Script
Generates synthetic training data and trains a Random Forest credit scoring model.
Run this before starting the backend: python train_model.py
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
N_SAMPLES = 10_000
RANDOM_STATE = 42
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "credit_model.pkl")


def generate_synthetic_data(n: int = N_SAMPLES) -> pd.DataFrame:
    """
    Generate realistic synthetic financial data for unbanked individuals.
    Features are drawn from distributions representative of informal/gig economy workers.
    """
    np.random.seed(RANDOM_STATE)

    # Feature generation with realistic distributions
    upi_transactions = np.random.randint(0, 200, size=n)  # 0-200 UPI transactions/month
    avg_transaction = np.random.exponential(scale=400, size=n).clip(10, 5000)  # INR 10-5000
    bill_payments_on_time = np.random.randint(0, 25, size=n)  # 0-24 months
    mobile_recharge_regularity = np.random.beta(a=3, b=1.5, size=n).clip(0, 1)  # 0-1 score
    savings_pattern = np.random.beta(a=2, b=2, size=n).clip(0, 1)  # 0-1 score

    # Credit score formula (realistic non-linear scoring)
    credit_score = (
        300
        + bill_payments_on_time * 12                       # Up to 288 pts  (biggest factor)
        + mobile_recharge_regularity * 150                  # Up to 150 pts
        + savings_pattern * 180                             # Up to 180 pts
        + np.clip(upi_transactions * 0.5, 0, 50)           # Up to 50 pts
        + np.clip(avg_transaction * 0.01, 0, 30)           # Up to 30 pts
        + np.random.normal(0, 25, size=n)                   # Noise ±25 pts
    ).clip(300, 900)

    return pd.DataFrame({
        "upi_transactions": upi_transactions,
        "avg_transaction": avg_transaction,
        "bill_payments_on_time": bill_payments_on_time,
        "mobile_recharge_regularity": mobile_recharge_regularity,
        "savings_pattern": savings_pattern,
        "credit_score": credit_score.astype(int),
    })


def train_model(df: pd.DataFrame) -> RandomForestRegressor:
    """Train a Random Forest regressor on the synthetic data."""
    feature_cols = [
        "upi_transactions",
        "avg_transaction",
        "bill_payments_on_time",
        "mobile_recharge_regularity",
        "savings_pattern",
    ]
    X = df[feature_cols]
    y = df["credit_score"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    rf = RandomForestRegressor(
        n_estimators=50,
        max_depth=10,
        min_samples_split=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)

    # Evaluate
    y_pred = rf.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("=" * 50)
    print("  IncluScore - Model Training Results")
    print("=" * 50)
    print(f"  Samples:          {len(df):,}")
    print(f"  Train / Test:     {len(X_train):,} / {len(X_test):,}")
    print(f"  Mean Abs Error:   {mae:.1f} pts")
    print(f"  R² Score:         {r2:.4f}")
    print("=" * 50)

    # Feature importance
    importances = dict(zip(feature_cols, rf.feature_importances_))
    print("\n  Feature Importances:")
    for feat, imp in sorted(importances.items(), key=lambda x: -x[1]):
        bar = "█" * int(imp * 40)
        print(f"    {feat:<36} {bar} {imp:.3f}")
    print()

    return rf


def main():
    print("\n🚀 IncluScore - Training ML Credit Scoring Model\n")

    # Generate data
    print("📊 Generating synthetic training data...")
    df = generate_synthetic_data()
    print(f"   ✓ {len(df):,} samples generated")
    print(f"   Score range: {df['credit_score'].min()} - {df['credit_score'].max()}")
    print(f"   Score mean:  {df['credit_score'].mean():.0f}\n")

    # Train
    print("🤖 Training Random Forest model...")
    rf_model = train_model(df)

    # Save
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(rf_model, MODEL_PATH)
    print(f"✅ Model saved to {MODEL_PATH}")

    # Quick sanity check
    print("\n🔍 Sanity check - sample predictions:")
    test_cases = [
        dict(upi_transactions=80, avg_transaction=500, bill_payments_on_time=22,
             mobile_recharge_regularity=0.95, savings_pattern=0.80, label="High Performer"),
        dict(upi_transactions=30, avg_transaction=250, bill_payments_on_time=15,
             mobile_recharge_regularity=0.75, savings_pattern=0.45, label="Average Earner"),
        dict(upi_transactions=10, avg_transaction=100, bill_payments_on_time=5,
             mobile_recharge_regularity=0.50, savings_pattern=0.15, label="New to Digital"),
    ]
    feature_cols = ["upi_transactions", "avg_transaction", "bill_payments_on_time",
                    "mobile_recharge_regularity", "savings_pattern"]
    for case in test_cases:
        label = case.pop("label")
        import pandas as pd
        pred = rf_model.predict(pd.DataFrame([case]))[0]
        pred = int(np.clip(pred, 300, 900))
        print(f"   {label:<25} → Score: {pred}")

    print("\n✨ Done! Start the backend with: uvicorn main:app --reload\n")


if __name__ == "__main__":
    main()
