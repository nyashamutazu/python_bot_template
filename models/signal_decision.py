from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional


@dataclass
class SignalDecision:
    symbol: str
    order_type: Literal["SELL_STOP", "BUY_STOP"]
    current_price: float
    volume: float
    risk: int
    take_profit: float
    stop_loss: float
    signal_timestamp: datetime
    break_of_structure: Optional[bool] = None
    granularity_ctf_granularity: Optional[str] = None
    
    def __repr__(self):
        return f"SignalDecision(): symbol={self.symbol}, order_type={self.order_type}, signal_timestamp={self.signal_timestamp}"
