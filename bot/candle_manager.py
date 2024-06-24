from api.metatrader_api import MT5
from models.candle_timing import CandleTiming
import constants.defs as defs


class CandleManager:
    def __init__(self, mt5: MT5, log_message, pairs, trade_settings):
        self.mt5 = mt5
        self.log_message = log_message
        self.pairs_list = pairs.keys()
        self.trade_settings = trade_settings
        self.timings = {
            p: CandleTiming(0, trade_settings) for p in self.pairs_list
        }
        for p, t in self.timings.items():
            self.log_message(f"CandleManager() init last_candle:{t}", p)

    def update_timings(self):
        triggered = []

        for pair in self.pairs_list:
            current_candle = self.mt5.query_historic_data(pair, 1)
            current_time = current_candle[0][0]
   
            if current_time is None:
                self.log_message("Unable to get candle", pair)
                continue
            
            self.timings[pair].is_ready = False

            if current_time > self.timings[pair].last_time:
                self.timings[pair].is_ready = True
                self.timings[pair].last_time = current_time
                self.log_message(
                    f"CandleManager() new candle:{self.timings[pair]}", pair
                )
                triggered.append(pair)

        return triggered
