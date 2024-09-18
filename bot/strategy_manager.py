from typing import Optional
from api.metatrader_api import MT5
from bot.risk_management import calculate_lot_size
from models.individual_strategy import IndividualStrategy
from models.signal_decision import SignalDecision
from strategy.strategy import run_strategy


class StrategyManager:
    def __init__(self, symbol, strategy: IndividualStrategy, mt5: MT5 , log_message, log_to_error):
        self.symbol = symbol
        self.strategy = strategy
        self.mt5 = mt5
        self.log_message = log_message
        self.log_to_error = log_to_error
        
    def generate_signal(self) -> Optional[SignalDecision]: 
        print(f"StrategyManager.generate_signal: starting for {self.symbol}, {self.strategy.granularity}")
        
        # Fetch candle data from MT5 API
        candle_data = self.mt5.fetch_candles(self.symbol, self.strategy.granularity, self.log_to_error)
        
        # Check if we received valid candle data
        if candle_data.empty:
            self.log_to_error(f"StrategyManager.generate_signal: No candle data received for {self.symbol}")
            return None

        print(f"StrategyManager.generate_signal: Running run_strategy with data size {len(candle_data)}")

        # Call run_strategy to get the signal decision
        signal_decision = run_strategy(
            candle_data=candle_data,
            symbol=self.symbol,
            strategy=self.strategy,
            log_message=self.log_message,
            log_to_error=self.log_to_error,
        )

        print(f"StrategyManager.generate_signal: Received strategy decision: {signal_decision}")
        
        if not signal_decision or signal_decision.signal == 0:
            self.log_message(f"StrategyManager: No valid signal generated for {self.symbol}", self.symbol)
            return None

        # Calculate lot size based on the signal decision
        volume, _, decimal_places = calculate_lot_size(
            self.mt5, signal_decision, self.log_message, self.log_to_error
        )
        
        signal_decision.volume = volume
        signal_decision.take_profit = round(signal_decision.take_profit, decimal_places)
        signal_decision.stop_loss = round(signal_decision.stop_loss, decimal_places)
    
        # Log the successful signal generation
        self.log_message(f"StrategyManager: Signal generated for {self.symbol}: {signal_decision}", self.symbol)
        
        return signal_decision
        