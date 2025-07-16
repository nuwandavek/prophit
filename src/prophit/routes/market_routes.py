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


def generate_homepage_charts(markets):
    """Generate JavaScript code to initialize charts for all markets on the homepage"""
    chart_code = []
    
    for market in markets:
        with get_db() as db:
            # Get price history for this market
            history = db.query(PriceHistory).filter(
                PriceHistory.market_id == market.id
            ).order_by(PriceHistory.timestamp).all()
            
            print(f"DEBUG: Found {len(history)} price history entries for market {market.id}")
            for i, h in enumerate(history):
                print(f"  Entry {i}: {h.timestamp} - yes={h.yes_price}, no={h.no_price}")
            
            # If no history exists, create initial history based on current prices
            if not history:
                print(f"DEBUG: No price history found for market {market.id}, creating initial entry")
                from ..utils.lmsr import LMSRCalculator
                calculator = LMSRCalculator()
                shares = calculator.get_current_shares(market.id)
                prices = calculator.calculate_prices(shares)
                
                initial_history = PriceHistory(
                    market_id=market.id,
                    yes_price=prices[1],
                    no_price=prices[0]
                )
                db.add(initial_history)
                db.commit()
                
                # Re-fetch history after creating initial entry
                history = db.query(PriceHistory).filter(
                    PriceHistory.market_id == market.id
                ).order_by(PriceHistory.timestamp).all()
                print(f"DEBUG: Created initial price history, now have {len(history)} entries")
            
            # Prepare chart data
            if history:
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
            else:
                # No history data, show empty chart
                chart_data = {
                    "labels": [],
                    "datasets": [{
                        "label": "Yes Probability",
                        "data": [],
                        "borderColor": "#56d364",
                        "backgroundColor": "rgba(86, 211, 100, 0.1)",
                        "tension": 0.1
                    }, {
                        "label": "No Probability", 
                        "data": [],
                        "borderColor": "#f85149",
                        "backgroundColor": "rgba(248, 81, 73, 0.1)",
                        "tension": 0.1
                    }]
                }
            
            # Add chart initialization code for this market
            chart_code.append(f"""
                const canvas{market.id} = document.getElementById('priceChart-{market.id}');
                console.log('DEBUG: Homepage canvas {market.id} found:', canvas{market.id});
                console.log('DEBUG: Homepage chart data {market.id}:', {json.dumps(chart_data)});
                if (canvas{market.id}) {{
                    const ctx{market.id} = canvas{market.id}.getContext('2d');
                    console.log('DEBUG: Homepage canvas context {market.id}:', ctx{market.id});
                    const chart{market.id} = new Chart(ctx{market.id}, {{
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
                                    display: true,
                                    ticks: {{
                                        display: true,
                                        color: '#888',
                                        font: {{
                                            family: 'JetBrains Mono'
                                        }},
                                        maxTicksLimit: 10
                                    }},
                                    grid: {{
                                        color: '#444'
                                    }},
                                    title: {{
                                        display: true,
                                        text: 'Time',
                                        color: '#888',
                                        font: {{
                                            family: 'JetBrains Mono'
                                        }}
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
                    console.error('Homepage canvas element not found: priceChart-{market.id}');
                }}
            """)
    
    return '\n'.join(chart_code)


def register_market_routes(app, rt):
    """Register market-related routes"""
    
    @rt("/")
    def get():
        """Home page with market list"""
        with get_db() as db:
            markets = db.query(Market).order_by(Market.created_at.desc()).all()
            print(f"DEBUG: Homepage found {len(markets)} markets")
            for market in markets:
                print(f"  Market {market.id}: {market.question}")
        
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
                    *[Div(market_card(m.id, m.question, m.status, show_plot=True), id=f"market-{m.id}") for m in markets] if markets else [Div("No markets yet. Create one above!", cls="empty-state")],
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
            """),
            
            # Chart initialization for homepage
            Script(f"""
                // Initialize charts for all markets on homepage
                document.fonts.ready.then(function() {{
                    setTimeout(function() {{
                        // Initialize charts for each market
                        {generate_homepage_charts(markets)}
                    }}, 100);
                }});
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
            print(f"DEBUG: Created initial price history for market {market.id}: yes={initial_history.yes_price}, no={initial_history.no_price}")
        
        # Get initial price history for chart
        with get_db() as db:
            history = db.query(PriceHistory).filter(
                PriceHistory.market_id == market.id
            ).order_by(PriceHistory.timestamp).all()
            
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
        
        return Div(
            market_card(market.id, market.question, market.status, show_plot=True),
            # Chart initialization script for newly created market
            Script(f"""
                // Initialize chart for new market
                setTimeout(function() {{
                    const canvas = document.getElementById('priceChart-{market.id}');
                    console.log('DEBUG: New market - Canvas element found:', canvas);
                    console.log('DEBUG: New market - Chart data:', {json.dumps(chart_data)});
                    if (canvas) {{
                        const ctx = canvas.getContext('2d');
                        console.log('DEBUG: New market - Canvas context:', ctx);
                        
                        // Create new chart
                        window.chart{market.id} = new Chart(ctx, {{
                            type: 'line',
                            data: {json.dumps(chart_data)},
                            options: {{
                                responsive: true,
                                maintainAspectRatio: false,
                                layout: {{
                                    padding: 0
                                }},
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
                                        display: true,
                                        ticks: {{
                                            display: true,
                                            color: '#888',
                                            font: {{
                                                family: 'JetBrains Mono'
                                            }},
                                            maxTicksLimit: 10
                                        }},
                                        grid: {{
                                            color: '#444'
                                        }},
                                        title: {{
                                            display: true,
                                            text: 'Time',
                                            color: '#888',
                                            font: {{
                                                family: 'JetBrains Mono'
                                            }}
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
                        console.error('New market - Canvas element not found: priceChart-{market.id}');
                    }}
                }}, 100);
            """),
            id=f"market-{market.id}"
        )

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
            print(f"DEBUG: Created new price history for market {market.id} after trade: yes={prices[1]}, no={prices[0]}")
        
        # Get updated price history for chart
        with get_db() as db:
            history = db.query(PriceHistory).filter(
                PriceHistory.market_id == market.id
            ).order_by(PriceHistory.timestamp).all()
            
            # Prepare chart data
            if history:
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
            else:
                chart_data = {
                    "labels": [],
                    "datasets": [{
                        "label": "Yes Probability",
                        "data": [],
                        "borderColor": "#56d364",
                        "backgroundColor": "rgba(86, 211, 100, 0.1)",
                        "tension": 0.1
                    }, {
                        "label": "No Probability", 
                        "data": [],
                        "borderColor": "#f85149",
                        "backgroundColor": "rgba(248, 81, 73, 0.1)",
                        "tension": 0.1
                    }]
                }
        
        # Return the market card wrapped with the proper ID (with plot for homepage) plus chart initialization
        return Div(
            market_card(market.id, market.question, market.status, show_plot=True),
            # Chart initialization script for this specific market after HTMX update
            Script(f"""
                // Re-initialize chart after HTMX update
                setTimeout(function() {{
                    const canvas = document.getElementById('priceChart-{market.id}');
                    console.log('DEBUG: HTMX update - Canvas element found:', canvas);
                    console.log('DEBUG: HTMX update - Chart data:', {json.dumps(chart_data)});
                    if (canvas) {{
                        const ctx = canvas.getContext('2d');
                        console.log('DEBUG: HTMX update - Canvas context:', ctx);
                        
                        // Destroy existing chart if it exists
                        if (window.chart{market.id}) {{
                            window.chart{market.id}.destroy();
                        }}
                        
                        // Create new chart
                        window.chart{market.id} = new Chart(ctx, {{
                            type: 'line',
                            data: {json.dumps(chart_data)},
                            options: {{
                                responsive: true,
                                maintainAspectRatio: false,
                                layout: {{
                                    padding: 0
                                }},
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
                                        display: true,
                                        ticks: {{
                                            display: true,
                                            color: '#888',
                                            font: {{
                                                family: 'JetBrains Mono'
                                            }},
                                            maxTicksLimit: 10
                                        }},
                                        grid: {{
                                            color: '#444'
                                        }},
                                        title: {{
                                            display: true,
                                            text: 'Time',
                                            color: '#888',
                                            font: {{
                                                family: 'JetBrains Mono'
                                            }}
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
                        console.error('HTMX update - Canvas element not found: priceChart-{market.id}');
                    }}
                }}, 100);
            """),
            id=f"market-{market.id}"
        )
    
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
            
            print(f"DEBUG: Market detail page - Found {len(history)} price history entries for market {market_id}")
            for i, h in enumerate(history):
                print(f"  Entry {i}: {h.timestamp} - yes={h.yes_price}, no={h.no_price}")
            
            # If no history exists, create initial history based on current prices
            if not history:
                print(f"DEBUG: No price history found for market {market_id}, creating initial entry")
                calculator = LMSRCalculator()
                shares = calculator.get_current_shares(market_id)
                prices = calculator.calculate_prices(shares)
                
                initial_history = PriceHistory(
                    market_id=market_id,
                    yes_price=prices[1],
                    no_price=prices[0]
                )
                db.add(initial_history)
                db.commit()
                
                # Re-fetch history after creating initial entry
                history = db.query(PriceHistory).filter(
                    PriceHistory.market_id == market_id
                ).order_by(PriceHistory.timestamp).all()
                print(f"DEBUG: Created initial price history, now have {len(history)} entries")
            
            # Get current prices
            calculator = LMSRCalculator()
            shares = calculator.get_current_shares(market_id)
            prices = calculator.calculate_prices(shares)
            
            # Prepare chart data
            if history:
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
            else:
                # No history data, show empty chart
                chart_data = {
                    "labels": [],
                    "datasets": [{
                        "label": "Yes Probability",
                        "data": [],
                        "borderColor": "#56d364",
                        "backgroundColor": "rgba(86, 211, 100, 0.1)",
                        "tension": 0.1
                    }, {
                        "label": "No Probability", 
                        "data": [],
                        "borderColor": "#f85149",
                        "backgroundColor": "rgba(248, 81, 73, 0.1)",
                        "tension": 0.1
                    }]
                }
            
            # Debug data - print chart values
            print(f"DEBUG: Chart data for market {market_id}:")
            print(f"  Number of history entries: {len(history)}")
            print(f"  Labels: {chart_data['labels']}")
            print(f"  Yes prices: {chart_data['datasets'][0]['data']}")
            print(f"  No prices: {chart_data['datasets'][1]['data']}")
            
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
                            console.log('DEBUG: Canvas element found:', canvas);
                            console.log('DEBUG: Chart data:', {json.dumps(chart_data)});
                            if (canvas) {{
                                const ctx = canvas.getContext('2d');
                                console.log('DEBUG: Canvas context:', ctx);
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
                                                display: true,
                                                ticks: {{
                                                    display: true,
                                                    color: '#888',
                                                    font: {{
                                                        family: 'JetBrains Mono'
                                                    }},
                                                    maxTicksLimit: 10
                                                }},
                                                grid: {{
                                                    color: '#444'
                                                }},
                                                title: {{
                                                    display: true,
                                                    text: 'Time',
                                                    color: '#888',
                                                    font: {{
                                                        family: 'JetBrains Mono'
                                                    }}
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