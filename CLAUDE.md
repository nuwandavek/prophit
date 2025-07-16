# Prophit - Internal Prediction Market

## Goal
Employees bet on project outcomes and deadlines using virtual currency. Creates knowledge sharing incentives and predictive insights.

## Tech Stack
- **FastHTML**: Python server-side rendering with HTMX
- **Database**: SQLite → PostgreSQL
- **Styling**: Pico CSS
- **Real-time**: WebSockets

## Pricing Algorithm
**LMSR (Logarithmic Market Scoring Rule)**
- Cost Function: C(q) = b * log(sum(exp(qi/b)))
- Price: P(i) = exp(qi/b) / sum(exp(qj/b))
- Bounded loss, instant liquidity, proper scoring

## Market Types
- Binary: Yes/No questions
- Categorical: Multiple outcomes
- Numerical: Predict values