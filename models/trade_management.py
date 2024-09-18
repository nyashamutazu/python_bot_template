from dataclasses import dataclass

@dataclass
class TradeManagement:
    trailing_stop: bool
    partial_close: bool