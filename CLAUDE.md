# Prophit - Internal Prediction Market

## Goal
Employees bet on project outcomes and deadlines using virtual currency. Creates knowledge sharing incentives and predictive insights.

## Tech Stack
- **FastHTML**: Python server-side rendering with HTMX
- **Database**: SQLite (prophit.db)
- **Project**: UV managed Python project
- **Styling**: Modern CSS with flat colors and gradients
- **Real-time**: WebSockets (planned)

## Architecture
```
src/prophit/
├── app.py              # Main app setup and styling
├── models/
│   ├── database.py     # SQLite connection & schema
│   └── market.py       # Pydantic models
├── routes/
│   └── market_routes.py # Market CRUD endpoints
├── components/
│   └── market_card.py  # UI components
└── utils/
    └── lmsr.py         # LMSR pricing algorithm
```

## Pricing Algorithm
**LMSR (Logarithmic Market Scoring Rule)**
- Cost Function: C(q) = b * log(sum(exp(qi/b)))
- Price: P(i) = exp(qi/b) / sum(exp(qj/b))
- Bounded loss, instant liquidity, proper scoring
- Default liquidity parameter: 100.0

## Market Types
- **Binary**: Yes/No questions (currently implemented)
- **Categorical**: Multiple outcomes (planned)
- **Numerical**: Predict values (planned)

## Database Schema
```sql
-- Markets table
CREATE TABLE markets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'binary',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolution_date TIMESTAMP,
    outcome INTEGER DEFAULT NULL,
    liquidity_param REAL DEFAULT 100.0
);

-- Positions table
CREATE TABLE positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    market_id INTEGER NOT NULL,
    outcome INTEGER NOT NULL,
    shares REAL NOT NULL,
    cost REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (market_id) REFERENCES markets(id)
);
```

## UI Features
- **Modern design**: Gradient backgrounds, flat colors, smooth animations
- **Responsive**: Mobile-friendly with proper breakpoints
- **Real-time updates**: HTMX for seamless trading experience
- **Event delegation**: JavaScript that persists across HTMX updates
- **Color-coded outcomes**: Green for Yes, Red for No

## Development Notes
- **NEVER run the app** - User will run and report any issues
- **Entry point**: `python main.py`
- **Database**: Auto-created as prophit.db
- **Current user**: Hardcoded as "user123" (TODO: Add authentication)