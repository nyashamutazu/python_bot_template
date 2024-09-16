from dataclasses import dataclass

@dataclass
class RiskManagement:
    max_trade_percentage: float
    max_stop_loss_percentage: float
    take_profit_ratio: float
    max_concurrent_trades: int
    max_daily_loss_percentage: float