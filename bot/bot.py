import json
import time

from api.metatrader_api import MT5
from core.log_wrapper import LogWrapper
import constants.defs as defs

from bot.candle_manager import CandleManager

import strategy.strategy as strategy
import bot.trade_manager as trade_manager

from models.trade_settings import TradeSettings


class Bot:
    ERROR_LOG = "error"
    MAIN_LOG = "main"

    def __init__(self):
        self.load_settings()
        self.setup_logs()

        self.mt5 = MT5()
        self.candle_manager = CandleManager(self.mt5, self.log_message, self.pairs_data, self.bot_settings)

        self.log_to_main("Bot started")
        self.log_to_error("Bot started")

    def load_settings(self):
        with open("./bot/settings.json", "r") as f:
            data = json.loads(f.read())
            self.pairs_data = {
                k: TradeSettings(v, k) for k, v in data["tradable_pairs"].items()
            }
            
            self.bot_settings = data
            del self.bot_settings['tradable_pairs']

    def setup_logs(self):
        self.logs = {}

        for k in self.pairs_data.keys():
            self.logs[k] = LogWrapper(k)
            self.log_message(f"{self.pairs_data[k]}", k)

        self.logs[Bot.ERROR_LOG] = LogWrapper(Bot.ERROR_LOG)
        self.logs[Bot.MAIN_LOG] = LogWrapper(Bot.MAIN_LOG)
        self.log_to_main(
            f"Bot started with {TradeSettings.settings_to_str(self.pairs_data)}"
        )

    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)

    def log_to_main(self, msg):
        self.log_message(msg, Bot.MAIN_LOG)

    def log_to_error(self, msg):
        self.log_message(msg, Bot.ERROR_LOG)

    def process_candles(self, triggered):
        if len(triggered) > 0:
            self.log_message(f"process_candles triggered:{triggered}", Bot.MAIN_LOG)
            for symbol in triggered:
                print(f"{symbol} triggered")
                for timeframe in self.pairs_data[symbol].timeframes:
                    for pattern, list_dir in self.pairs_data[symbol].settings['patterns'].items():
                        for trade_dir in list_dir:
                            last_time = self.candle_manager.timings[symbol].last_time
                            trade_result = trade_manager.run(
                                self.mt5,
                                self.bot_settings,
                                self.pairs_data, 
                                symbol,
                                timeframe,
                                pattern,
                                trade_dir,
                                last_time,
                                self.log_message,
                                self.log_to_error,
                            )


    def run(self):
        self.mt5.run()

        while True:

            self.process_candles(self.candle_manager.update_timings())
            time.sleep(self.bot_settings["sleep_time"])
