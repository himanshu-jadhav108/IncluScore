-- ============================================================
-- IncluScore - Supabase Database Schema
-- Run this in the Supabase SQL Editor to set up your database
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- USERS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    age        INTEGER CHECK (age > 0 AND age < 120),
    city       VARCHAR(50),
    occupation VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- FINANCIAL PROFILES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS financial_profiles (
    id                          SERIAL PRIMARY KEY,
    user_id                     INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    upi_transactions            INTEGER DEFAULT 0,
    avg_transaction_amount      DECIMAL(10, 2),
    bill_payments_on_time       INTEGER DEFAULT 0,
    total_bill_payments         INTEGER DEFAULT 24,
    mobile_recharge_regularity  DECIMAL(3, 2) CHECK (mobile_recharge_regularity BETWEEN 0 AND 1),
    savings_pattern             DECIMAL(3, 2) CHECK (savings_pattern BETWEEN 0 AND 1),
    monthly_income_estimate     DECIMAL(10, 2),
    current_score               INTEGER,
    updated_at                  TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- CONSENT LOGS TABLE (privacy-first design)
-- ============================================================
CREATE TABLE IF NOT EXISTS consent_logs (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER REFERENCES users(id) ON DELETE CASCADE,
    data_type     VARCHAR(50) NOT NULL,  -- e.g. 'upi_data', 'bill_data', 'savings_data'
    consent_given BOOLEAN NOT NULL,
    ip_address    VARCHAR(45),           -- Supports IPv6
    timestamp     TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SCORE HISTORY TABLE (for trend charts)
-- ============================================================
CREATE TABLE IF NOT EXISTS score_history (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
    score      INTEGER NOT NULL,
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_financial_profiles_user_id ON financial_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_score_history_user_id ON score_history(user_id);
CREATE INDEX IF NOT EXISTS idx_consent_logs_user_id ON consent_logs(user_id);

-- ============================================================
-- SAMPLE DATA — Three Personas
-- ============================================================

-- Persona 1: Raj Kumar - Gig Worker (Delivery)
INSERT INTO users (name, age, city, occupation) VALUES
    ('Raj Kumar', 32, 'Mumbai', 'Gig Worker (Delivery)');

INSERT INTO financial_profiles
    (user_id, upi_transactions, avg_transaction_amount, bill_payments_on_time,
     total_bill_payments, mobile_recharge_regularity, savings_pattern,
     monthly_income_estimate)
VALUES
    (1, 45, 320.00, 18, 24, 0.85, 0.40, 22000.00);

-- Persona 2: Priya Sharma - Salaried Retail Worker
INSERT INTO users (name, age, city, occupation) VALUES
    ('Priya Sharma', 28, 'Bengaluru', 'Salaried - Retail Worker');

INSERT INTO financial_profiles
    (user_id, upi_transactions, avg_transaction_amount, bill_payments_on_time,
     total_bill_payments, mobile_recharge_regularity, savings_pattern,
     monthly_income_estimate)
VALUES
    (2, 92, 850.00, 23, 24, 0.96, 0.72, 38000.00);

-- Persona 3: Amit Patel - Student / Part-time Worker
INSERT INTO users (name, age, city, occupation) VALUES
    ('Amit Patel', 21, 'Ahmedabad', 'Student / Part-time Worker');

INSERT INTO financial_profiles
    (user_id, upi_transactions, avg_transaction_amount, bill_payments_on_time,
     total_bill_payments, mobile_recharge_regularity, savings_pattern,
     monthly_income_estimate)
VALUES
    (3, 20, 150.00, 8, 12, 0.60, 0.22, 8000.00);

-- Seed consent logs
INSERT INTO consent_logs (user_id, data_type, consent_given, ip_address) VALUES
    (1, 'upi_data',     TRUE, '0.0.0.0'),
    (1, 'bill_data',    TRUE, '0.0.0.0'),
    (1, 'savings_data', TRUE, '0.0.0.0'),
    (2, 'upi_data',     TRUE, '0.0.0.0'),
    (2, 'bill_data',    TRUE, '0.0.0.0'),
    (2, 'savings_data', TRUE, '0.0.0.0'),
    (3, 'upi_data',     TRUE, '0.0.0.0'),
    (3, 'bill_data',    TRUE, '0.0.0.0'),
    (3, 'savings_data', FALSE,'0.0.0.0');  -- Amit hasn't consented to savings sharing

-- ============================================================
-- ROW LEVEL SECURITY (recommended for production)
-- ============================================================
ALTER TABLE users              ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE consent_logs       ENABLE ROW LEVEL SECURITY;

-- Allow read access for authenticated users (adjust to your auth strategy)
CREATE POLICY "Allow read" ON users              FOR SELECT USING (true);
CREATE POLICY "Allow read" ON financial_profiles FOR SELECT USING (true);
CREATE POLICY "Allow read" ON consent_logs       FOR SELECT USING (true);
