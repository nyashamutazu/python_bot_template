from dataclasses import dataclass

@dataclass
class TradeManagement:
    traling_stop: bool
    partial_close: bool