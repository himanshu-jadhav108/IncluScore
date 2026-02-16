# IncluScore — 2-Minute Demo Script

> **Time target:** Exactly 2:00 minutes
> **Speaker notes in** *italics*

---

## 🎬 INTRO — [0:00 – 0:15]

**"Hi everyone. 1.7 billion adults worldwide are credit invisible — not because they're risky borrowers, but because they've never had a bank account.**

**IncluScore changes that."**

*[Open the browser to the IncluScore dashboard. Make sure Raj Kumar is selected.]*

---

## 💔 THE PROBLEM — [0:15 – 0:30]

**"Traditional credit scoring requires a loan history, a credit card, or a bank account. But gig workers, street vendors, and rural earners don't have these.**

**They have something else — digital breadcrumbs. UPI payments, mobile recharges, utility bills. IncluScore reads those signals."**

---

## 🖥 LIVE DEMO — [0:30 – 1:30]

### Step 1 — Show Raj Kumar [0:30 – 0:50]

*[Point at the dashboard — Raj's score is visible: ~680]*

**"Meet Raj, a delivery worker in Mumbai. He has zero bank credit history. But IncluScore sees that he makes 45 UPI transactions a month, paid 18 of 24 bills on time, and recharges his phone every month without fail."**

**"His score? 680. Good band. Loan eligible."**

### Step 2 — Explain the AI [0:50 – 1:05]

*[Point to the 'Why This Score?' panel on the right]*

**"Unlike a black-box algorithm, IncluScore explains every decision. Bill payment history is his biggest strength at 37%. Savings behavior needs improvement — and the system tells him exactly how to fix it."**

### Step 3 — Switch to Priya [1:05 – 1:15]

*[Change dropdown to Priya Sharma]*

**"Priya is salaried with consistent savings. Her score jumps to 810 — Excellent. Instant approval."**

### Step 4 — Simulate a transaction [1:15 – 1:25]

*[Switch back to Raj. Click the 'Simulate New UPI Transaction' button]*

**"Now watch — Raj just made a new payment. His score updates in real-time, up by 8 points. Every responsible financial action is rewarded."**

### Step 5 — Lender View [1:25 – 1:30]

*[Click to expand the Lender View]*

**"From a lender's perspective: score, confidence rating, and an instant APPROVE/REVIEW/DENY decision — with full explainability for compliance."**

---

## 🚀 WHY WE WIN — [1:30 – 1:50]

**"Three things set IncluScore apart:**

**One — Alternative data. We score people traditional systems ignore.**

**Two — Explainable AI. Not a black box. Every factor is visible, in plain language.**

**Three — Privacy first. Data never leaves the device. Consent is baked in from day one."**

---

## 🎯 CLOSE — [1:50 – 2:00]

**"IncluScore isn't just a hackathon demo. It's a blueprint for bringing 1.7 billion people into the financial system — fairly, transparently, and on their terms.**

**Thank you."**

---

## ⚡ Backup Q&A Answers

**"How is this different from just estimating income?"**
> We score *behavioral reliability*, not just income. A low-income earner who pays every bill on time scores higher than a high earner who doesn't.

**"Could this be gamed?"**
> Scores are based on 24 months of consistent behavior. Short-term manipulation doesn't move the needle significantly.

**"How do you get the data?"**
> Via consented Open Banking APIs (NBFC/AA framework in India), or from BHIM/UPI apps with user permission. Our schema includes consent logs for every data type.

**"What's your accuracy?"**
> Our Random Forest model achieves R² ~0.98 on synthetic data, with mean absolute error under 20 points. We'd tune this further on real-world labeled datasets.
