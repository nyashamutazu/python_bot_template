import datetime as dt
import pytz
import constants.defs as defs

class CandleTiming:
    def __init__(self, last_time, trade_settings):
        self.last_time = last_time
        self.trade_settings = trade_settings
        self.last_position_update = last_time
        self.is_ready = False

    def __repr__(self):
        current_timezone = pytz.timezone(self.trade_settings['timezone'])

        return f"last_candle:{dt.datetime.fromtimestamp(self.last_time, current_timezone)} is_ready:{self.is_ready}"