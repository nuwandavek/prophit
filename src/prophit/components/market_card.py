from fasthtml.common import *
from ..utils.lmsr import LMSRCalculator
from ..constants import DEFAULT_TRADE_QUANTITY
from ..models.database import get_db, Position


def market_card(market_id: int, question: str, status: str = "active", show_plot: bool = False):
    """Display a market with current prices and trading interface"""
    calculator = LMSRCalculator()
    shares = calculator.get_current_shares(market_id)
    prices = calculator.calculate_prices(shares)
    
    # Calculate total trade volume and total shares
    with get_db() as db:
        total_volume = db.query(Position).filter(Position.market_id == market_id).count()
        if total_volume == 0:
            total_volume = 0
        
        # Calculate total shares (sum of all shares across all positions)
        total_shares_result = db.query(Position).filter(Position.market_id == market_id).all()
        total_shares = sum(pos.shares for pos in total_shares_result) if total_shares_result else 0
    
    # Create the question display - always make it a clickable link
    question_display = H3(A(question, href=f"/market/{market_id}"))
    
    return Div(
        question_display,
        Div(
            Div(f"Yes: {prices[1]:.1%}", cls="price-display yes"),
            Div(f"No: {prices[0]:.1%}", cls="price-display no"),
            cls="prices-container"
        ),
        Div(
            Div(f"Total Trades: {total_volume} ({total_shares:.1f} shares)"),
            cls="volume-info"
        ),
        # Show plot if requested
        Div(
            H3("Probability Over Time"),
            Div(
                Canvas(id=f"priceChart-{market_id}", style="width: 100%; height: 250px;"),
                cls="chart-container",
                style="height: 250px; width: 100%;"
            ),
            style="margin: 20px 0;"
        ) if show_plot else None,
        trade_form(market_id) if status == "active" else None,
        cls="market-card"
    )


def trade_form(market_id: int):
    """Trading form for a market"""
    return Form(
        Div(
            Button("Yes", 
                   type="button", 
                   cls="outcome-btn yes",
                   **{"data-market-id": str(market_id), "data-outcome": "1"}),
            Button("No", 
                   type="button", 
                   cls="outcome-btn no",
                   **{"data-market-id": str(market_id), "data-outcome": "0"}),
            Input(type="number", 
                  name="quantity", 
                  placeholder="Shares", 
                  min="1", 
                  step="1", 
                  value=str(int(DEFAULT_TRADE_QUANTITY)),
                  cls="quantity-input"),
            Button("Buy Shares", type="submit", cls="buy-btn"),
            Input(type="hidden", name="outcome", value="1"),
            cls="trade-form"
        ),
        hx_post=f"/trade/{market_id}",
        hx_target=f"#market-{market_id}",
        hx_swap="outerHTML"
    )