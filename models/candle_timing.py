from dataclasses import dataclass, field
import datetime as dt

@dataclass
class CandleTiming:
    last_time: dt.datetime
    tries: int = 0
    is_ready: bool = False

    def __repr__(self):
        return f'last_candle: {dt.datetime.strftime(self.last_time, "%Y-%m-%d %H:%M")}, is_ready: {self.is_ready}'
