from fasthtml.common import *
from ..models.database import get_db, Market, Position, PriceHistory
from ..components.market_card import market_card
from ..utils.lmsr import LMSRCalculator
from ..constants import (
    DEFAULT_USER_ID, 
    DEFAULT_TRADE_QUANTITY, 
    MARKET_TYPES, 
    MARKET_STATUSES,
    BINARY_OUTCOMES
)
import json
from datetime import datetime


def register_market_routes(app, rt):
    """Register market-related routes"""
    
    @rt("/")
    def get():
        """Home page with market list"""
        with get_db() as db:
            markets = db.query(Market).order_by(Market.created_at.desc()).all()
        
        return Titled("Prophit - Prediction Markets",
            Div(
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
            
            # Add initial price history (50/50 probability)
            initial_history = PriceHistory(
                market_id=market.id,
                yes_price=0.5,
                no_price=0.5
            )
            db.add(initial_history)
            db.commit()
        
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
        
        # Save price history
        calculator = LMSRCalculator()
        shares = calculator.get_current_shares(market.id)
        prices = calculator.calculate_prices(shares)
        
        with get_db() as db:
            price_history = PriceHistory(
                market_id=market.id,
                yes_price=prices[1],
                no_price=prices[0]
            )
            db.add(price_history)
            db.commit()
        
        # Return the market card wrapped with the proper ID
        return Div(market_card(market.id, market.question, market.status), id=f"market-{market.id}")
    
    @rt("/market/{market_id}")
    def get_market_detail(market_id: int):
        """Market detail page with probability plot"""
        with get_db() as db:
            market = db.query(Market).filter(Market.id == market_id).first()
            if not market:
                return "Market not found", 404
            
            # Get price history
            history = db.query(PriceHistory).filter(
                PriceHistory.market_id == market_id
            ).order_by(PriceHistory.timestamp).all()
            
            # Get current prices
            calculator = LMSRCalculator()
            shares = calculator.get_current_shares(market_id)
            prices = calculator.calculate_prices(shares)
            
            # Prepare chart data
            chart_data = {
                "labels": [h.timestamp.strftime("%m/%d %H:%M") for h in history],
                "datasets": [{
                    "label": "Yes Probability",
                    "data": [h.yes_price for h in history],
                    "borderColor": "#56d364",
                    "backgroundColor": "rgba(86, 211, 100, 0.1)",
                    "tension": 0.1
                }, {
                    "label": "No Probability", 
                    "data": [h.no_price for h in history],
                    "borderColor": "#f85149",
                    "backgroundColor": "rgba(248, 81, 73, 0.1)",
                    "tension": 0.1
                }]
            }
            
            return Titled(f"Market: {market.question}",
                Div(
                    # Back link at the very top
                    A("← Back to Markets", href="/", cls="back-link"),
                    
                    # Market header
                    Div(
                        H1(market.question),
                        style="margin-bottom: 2rem;"
                    ),
                    
                    # Current prices section
                    Div(
                        H2("Current Prices"),
                        Div(
                            Div(f"Yes: {prices[1]:.1%}", cls="price-display yes"),
                            Div(f"No: {prices[0]:.1%}", cls="price-display no"),
                            cls="prices-container"
                        ),
                        style="margin-bottom: 2rem;"
                    ),
                    
                    # Market card with plot and trading
                    Div(market_card(market.id, market.question, market.status, show_plot=True), id=f"market-{market.id}"),
                    
                    cls="container"
                ),
                
                # Chart initialization script
                Script(f"""
                    // Wait for fonts to load before initializing chart
                    document.fonts.ready.then(function() {{
                        // Wait a bit more for the canvas to be fully rendered
                        setTimeout(function() {{
                            const canvas = document.getElementById('priceChart-{market_id}');
                            if (canvas) {{
                                const ctx = canvas.getContext('2d');
                                const chart = new Chart(ctx, {{
                                    type: 'line',
                                    data: {json.dumps(chart_data)},
                                    options: {{
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        plugins: {{
                                            legend: {{
                                                display: true,
                                                position: 'top',
                                                labels: {{
                                                    color: '#e0e0e0',
                                                    font: {{
                                                        family: 'JetBrains Mono'
                                                    }}
                                                }}
                                            }}
                                        }},
                                        scales: {{
                                            x: {{
                                                ticks: {{
                                                    color: '#888',
                                                    font: {{
                                                        family: 'JetBrains Mono'
                                                    }}
                                                }},
                                                grid: {{
                                                    color: '#444'
                                                }}
                                            }},
                                            y: {{
                                                beginAtZero: true,
                                                max: 1,
                                                ticks: {{
                                                    color: '#888',
                                                    font: {{
                                                        family: 'JetBrains Mono'
                                                    }},
                                                    callback: function(value) {{
                                                        return (value * 100).toFixed(0) + '%';
                                                    }}
                                                }},
                                                grid: {{
                                                    color: '#444'
                                                }}
                                            }}
                                        }}
                                    }}
                                }});
                            }} else {{
                                console.error('Canvas element not found: priceChart-{market_id}');
                            }}
                        }}, 100);
                    }});
                """)
            )