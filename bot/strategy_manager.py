from typing import Optional
from api.metatrader_api import MT5
from models.individual_strategy import IndividualStrategy
from models.risk_management import RiskManagement
from models.signal_decision import SignalDecision
from strategy.strategy import run_strategy


class StrategyManager:
    def __init__(self, symbol, strategy: IndividualStrategy, mt5: MT5 , log_message, log_to_error):
        self.symbol = symbol
        self.strategy = strategy
        self.mt5 = mt5
        self.log_message = log_message
        self.log_to_error = log_to_error
        
    def generate_signal(self)-> Optional[SignalDecision]: 
        # Get candle data from the MT5 API (assuming the API provides this method)
        candle_data = self.mt5.fetch_candles(self.symbol, self.strategy.granularity, self.log_to_error)

        if candle_data == None:
            return None
        
        # Call run_strategy to get the signal decision
        signal_decision = run_strategy(
            candle_data,
            self.symbol,
            strategy=self.strategy,
            log_message=self.log_message,
            log_to_error=self.log_message,
        )

        if signal_decision:
            self.log_message(f"StrategyManager: Signal generated: {signal_decision}", self.symbol)
            self.current_signal = signal_decision
        else:
            self.log_message(f"StrategyManager: No valid signal generated", self.symbol)
            return None