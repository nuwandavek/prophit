from fasthtml.common import *
from ..utils.lmsr import LMSRCalculator
from ..constants import DEFAULT_TRADE_QUANTITY


def market_card(market_id: int, question: str, status: str = "active", show_plot: bool = False):
    """Display a market with current prices and trading interface"""
    calculator = LMSRCalculator()
    shares = calculator.get_current_shares(market_id)
    prices = calculator.calculate_prices(shares)
    
    # Create the question display - link if not showing plot, plain text if showing plot
    question_display = H3(question) if show_plot else H3(A(question, href=f"/market/{market_id}"))
    
    return Div(
        question_display,
        Div(
            Div(f"Yes: {prices[1]:.1%}", cls="price-display yes"),
            Div(f"No: {prices[0]:.1%}", cls="price-display no"),
            cls="prices-container"
        ),
        Div(
            Div(f"Yes Shares: {shares[1]:.1f}"),
            Div(f"No Shares: {shares[0]:.1f}"),
            cls="shares-info"
        ),
        # Show plot if requested
        Div(
            H3("Probability Over Time"),
            Div(
                Canvas(id=f"priceChart-{market_id}", style="max-height: 300px;"),
                cls="chart-container"
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
                  value=str(int(DEFAULT_TRADE_QUANTITY))),
            Input(type="hidden", name="outcome", value="1"),
            Button("Buy Shares", type="submit"),
            cls="trade-form"
        ),
        hx_post=f"/trade/{market_id}",
        hx_target=f"#market-{market_id}",
        hx_swap="outerHTML"
    )