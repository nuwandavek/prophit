from fasthtml.common import *
from ..models.database import get_db, Market, Position
from ..components.market_card import market_card
from ..utils.lmsr import LMSRCalculator
from ..constants import (
    DEFAULT_USER_ID, 
    DEFAULT_TRADE_QUANTITY, 
    MARKET_TYPES, 
    MARKET_STATUSES,
    BINARY_OUTCOMES
)


def register_market_routes(app, rt):
    """Register market-related routes"""
    
    @rt("/")
    def get():
        """Home page with market list"""
        with get_db() as db:
            markets = db.query(Market).order_by(Market.created_at.desc()).all()
        
        return Titled("Prophit - Prediction Markets",
            Div(
                H1("Prophit"),
                
                # Market creation form
                Div(
                    H2("Create New Market"),
                    Form(
                        Input(type="text", 
                              name="question", 
                              placeholder="Will project X be completed by Q3?", 
                              required=True,
                              style="width: 100%; margin-bottom: 1rem;"),
                        Button("Create Market", type="submit"),
                        hx_post="/create-market",
                        hx_target="#markets-list",
                        hx_swap="afterbegin"
                    ),
                    cls="create-market-form"
                ),
                
                # Markets list
                Div(
                    H2("Active Markets"),
                    *[Div(market_card(m.id, m.question, m.status), id=f"market-{m.id}") for m in markets] if markets else [Div("No markets yet. Create one above!", cls="empty-state")],
                    id="markets-list",
                    cls="markets-section"
                ),
                
                cls="container"
            ),
            
            # JavaScript for outcome selection (global event delegation)
            Script("""
                document.addEventListener('click', function(event) {
                    if (event.target.classList.contains('outcome-btn')) {
                        const button = event.target;
                        const marketId = button.getAttribute('data-market-id');
                        const outcome = button.getAttribute('data-outcome');
                        
                        // Find the form for this market
                        const form = document.querySelector(`form[hx-post="/trade/${marketId}"]`);
                        if (!form) return;
                        
                        // Update button states
                        const buttons = form.querySelectorAll('.outcome-btn');
                        const hiddenInput = form.querySelector('input[name="outcome"]');
                        
                        buttons.forEach(btn => btn.classList.remove('selected'));
                        button.classList.add('selected');
                        hiddenInput.value = outcome;
                    }
                });
            """)
        )

    @rt("/create-market")
    def post(question: str):
        """Create a new market"""
        with get_db() as db:
            market = Market(
                question=question, 
                type=MARKET_TYPES["BINARY"], 
                status=MARKET_STATUSES["ACTIVE"]
            )
            db.add(market)
            db.commit()
            db.refresh(market)
        
        return Div(market_card(market.id, market.question, market.status), id=f"market-{market.id}")

    @rt("/trade/{market_id}")
    def post(market_id: int, outcome: int, quantity: float):
        """Execute a trade"""
        user_id = DEFAULT_USER_ID  # TODO: Replace with actual user authentication
        
        calculator = LMSRCalculator()
        cost = calculator.calculate_trade_cost(market_id, outcome, quantity)
        
        # Record the trade
        with get_db() as db:
            position = Position(
                user_id=user_id,
                market_id=market_id,
                outcome=outcome,
                shares=quantity,
                cost=cost
            )
            db.add(position)
            db.commit()
            
            # Get updated market data
            market = db.query(Market).filter(Market.id == market_id).first()
        
        # Return the market card wrapped with the proper ID
        return Div(market_card(market.id, market.question, market.status), id=f"market-{market.id}")