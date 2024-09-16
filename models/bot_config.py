from dataclasses import dataclass
from models.logging import Logging
# from models.notifications import Notifications
from models.error_handling import ErrorHandling
from models.signal_managment import SiganlManagement
from models.trade_management import TradeManagement

@dataclass
class BotConfig:
    bot_name: str
    strategy_name: str
    active_status: bool
    timezone: str
    sleep_time: int
    start_time: str
    end_time: str
    logging: Logging
    error_handling: ErrorHandling
    trade_management: TradeManagement
    signal_management: SiganlManagement
    