from typing import Dict, List
from api.metatrader_api import MT5
from bot.strategy_manager import StrategyManager
from models.candle_timing import CandleTiming
import constants.defs as defs
from models.individual_strategy import IndividualStrategy
import datetime as dt

class CandleManager:
    def __init__(self, mt5: MT5, trading_symbols: Dict[str, List[StrategyManager]], log_message):
        self.mt5 = mt5
        self.trading_symbols = trading_symbols
        self.log_message = log_message

        self.create_timings()
        
    def create_timings(self):
        self.timings: Dict[str, CandleTiming] = {}
        self.symbols_list: List[tuple[str, str]] = []
        
        for symbol, strategy_managers in self.trading_symbols.items():
            for strategy_manager in strategy_managers:
                strategy = strategy_manager.strategy
                granularity = strategy.granularity
                
                name = f'{symbol}_{granularity}'
                current_candle = self.mt5.query_historic_data(symbol, 1, granularity=granularity)
                timestamp = current_candle[0][0]
            
                datetime = dt.datetime.fromtimestamp(timestamp)
                
                self.timings[name] = CandleTiming(
                    last_time=datetime)

                timing_var = (symbol, granularity)
                self.symbols_list.append(timing_var)

        for pg, t in self.timings.items():
            symbol, granularity = pg.rsplit('_', 1)

            self.log_message(f"CandleManager() init last_candle:{t}", symbol)
            
    def update_timings(self):
        triggered: List[str] = []

        for symbol, granularity in self.symbols_list:
            current_candle = self.mt5.query_historic_data(symbol, 1, granularity=granularity)
            timestamp = current_candle[0][0] if current_candle else None
            current_time = dt.datetime.fromtimestamp(timestamp)
                                
            if current_time is None:
                self.log_message(f"Unable to get candle for {symbol}. Retrying...", symbol)
                self.timings[f'{symbol}_{granularity}'].tries += 1
                if self.timings[f'{symbol}_{granularity}'].tries > defs.MAX_RETRIES:
                    self.log_message(f"Max retries exceeded for {symbol}. Skipping update.", symbol)
                continue

            # Reset retries on success
            self.timings[f'{symbol}_{granularity}'].tries = 0
            symbol_granularity = f'{symbol}_{granularity}'
            self.timings[symbol_granularity].is_ready = False

            if current_time > self.timings[symbol_granularity].last_time:
                self.timings[symbol_granularity].is_ready = True
                self.timings[symbol_granularity].last_time = current_time
                self.log_message(
                    f"CandleManager() new candle:{self.timings[symbol_granularity]}", symbol)
                triggered.append(symbol)

        return triggered

