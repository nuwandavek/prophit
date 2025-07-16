import math
from typing import List
from sqlalchemy import func
from ..models.database import get_db, Position
from ..constants import DEFAULT_LIQUIDITY_PARAM, BINARY_OUTCOMES


class LMSRCalculator:
    """LMSR (Logarithmic Market Scoring Rule) calculator"""
    
    def __init__(self, liquidity_param: float = DEFAULT_LIQUIDITY_PARAM):
        self.b = liquidity_param
    
    def get_current_shares(self, market_id: int) -> List[float]:
        """Get current share quantities for each outcome"""
        with get_db() as db:
            result = db.query(
                Position.outcome, 
                func.sum(Position.shares).label('total_shares')
            ).filter(
                Position.market_id == market_id
            ).group_by(Position.outcome).order_by(Position.outcome).all()
        
        # For binary markets, ensure we have both outcomes
        shares = [0.0, 0.0]
        for outcome, total in result:
            if outcome < len(shares):
                shares[outcome] = total
        return shares
    
    def calculate_cost(self, shares: List[float]) -> float:
        """Calculate cost function C(q) = b * log(sum(exp(qi/b)))"""
        exp_sum = sum(math.exp(q / self.b) for q in shares)
        return self.b * math.log(exp_sum)
    
    def calculate_prices(self, shares: List[float]) -> List[float]:
        """Calculate prices P(i) = exp(qi/b) / sum(exp(qj/b))"""
        exp_values = [math.exp(q / self.b) for q in shares]
        exp_sum = sum(exp_values)
        return [exp_val / exp_sum for exp_val in exp_values]
    
    def calculate_trade_cost(self, market_id: int, outcome: int, quantity: float) -> float:
        """Calculate cost to buy quantity shares of outcome"""
        current_shares = self.get_current_shares(market_id)
        
        # Cost before trade
        cost_before = self.calculate_cost(current_shares)
        
        # Cost after trade
        new_shares = current_shares[:]
        new_shares[outcome] += quantity
        cost_after = self.calculate_cost(new_shares)
        
        return cost_after - cost_before