from concurrent.futures import ThreadPoolExecutor
import json
from queue import Queue
import time
from typing import Dict, List
import datetime as dt 
import threading
import logging

from api.metatrader_api import MT5
from bot.signal_management import process_signal
from bot.strategy_manager import StrategyManager
from core.log_wrapper import LogWrapper

from bot.candle_manager import CandleManager

from models.bot_config import BotConfig
from models.error_handling import ErrorHandling
from models.indicators import Indicators
from models.logging import Logging
from models.risk_management import RiskManagement
from models.individual_strategy import IndividualStrategy
from models.signal_decision import SignalDecision
from models.signal_managment import SignalManagement
from models.strategy_configuration import StrategyConfiguration
import bot.trade_manager as trade_manager

from models.trade_management import TradeManagement

from utils.utils import granularity_to_minutes

class Bot:
    ERROR_LOG = "error"
    MAIN_LOG = "main"

    def __init__(self):
        self.mt5 = MT5()

        # Attempt login
        if not self.mt5.attempt_login():
            logging.error("Failed to login to MetaTrader. Bot will not start.")
            return  # Exit the constructor if login fails

        logging.info("Login successful, proceeding with bot initialization.")
        
        self.load_settings()
        self.set_bot_configuration()
        self.set_bot_variables()
        self.setup_logs()

        self.candle_manager = CandleManager(self.mt5, self.trading_symbols, self.log_message)
        self.trade_manager = trade_manager.TradeManager(self.mt5, self.risk_management, self.log_to_main, self.log_message, self.log_to_error)

        self.log_to_main("Bot started")
        self.log_to_error("Bot started")

    def load_settings(self):
        with open("./bot/configuration.json", "r") as f:
            data = json.loads(f.read())
            self.risk_management = RiskManagement(**data["risk_management"])
            self.error_handling = ErrorHandling(**data["error_handling"])
            
            self.logging: Dict[str, Logging] = {}
            for logging_name, logging_config in data["logging"].items():
                self.logging[logging_name] = Logging(**logging_config)
                
            self.trade_management = TradeManagement(**data["trade_management"])
            self.signal_management = SignalManagement(**data["signal_management"])
            
            self.trading_symbols: Dict[str, List[StrategyManager]] = {}
            self.trading_times = set()
            
            for symbol, strategy_configurations in data["tradable_symbols"].items():
                self.trading_symbols[symbol] = []
                
                for strategy_configuration in strategy_configurations:
                    granularities_in_minutes = granularity_to_minutes(strategy_configuration["granularity"])
                    self.trading_times.add(granularities_in_minutes)
                    
                    indicators = Indicators(**strategy_configuration["indicators"])
                    strategy = IndividualStrategy(indicators=indicators, granularity=strategy_configuration["granularity"], risk=strategy_configuration["risk"], profit_ratio=strategy_configuration["profit_ratio"])

                    strategy_manager = StrategyManager(
                        symbol=symbol,
                        strategy=strategy,
                        mt5=self.mt5,
                        log_message=self.log_message,
                        log_to_error=self.log_to_error
                    )
                    
                    self.trading_symbols[symbol].append(strategy_manager)
                    
            
            self.bot_config = BotConfig(
                bot_name=data["bot_name"],
                strategy_name=data["strategy_name"],
                active_status=data["active_status"],
                timezone=data["timezone"],
                start_time=data["start_time"],
                end_time=data["end_time"],
                sleep_time=data["sleep_time"],
                logging=self.logging,
                error_handling=self.error_handling,
                trade_management=self.trade_management,
                signal_management=self.signal_management
            )
            
            self.strategy_configuration = StrategyConfiguration(
                risk_management=self.risk_management,
                trading_symbols=self.trading_symbols
            )

    def setup_logs(self):
        self.logs: Dict[str, LogWrapper] = {}
        
        for symbol in self.trading_symbols.keys():
            self.logs[symbol] = LogWrapper(symbol)
            for symbol_candle in self.trading_symbols[symbol]:
                self.log_message(f"{symbol_candle}", symbol)
        
        for logging_name, loging_attributes in self.logging.items():
            _name = loging_attributes.name
            self.logs[_name] = LogWrapper(_name)
            
        if self.bot_config.signal_management.trade_processor:
            self.logs["trade_processor"] = LogWrapper("trade_processor")
        
        self.log_to_main(
            f"Bot started with {StrategyConfiguration.settings_to_str(self.strategy_configuration)}"
        )
        
    def set_bot_configuration(self):
        self.is_running = True
        self.lock = threading.Lock()
        self.error_count = 0
        
    def set_bot_variables(self):
        self.current_signals = Queue()

    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)

    def log_to_main(self, msg):
        self.log_message(msg, 'main')

    def log_to_error(self, msg):
        self.log_message(msg, 'error')
        
    def get_next_interval(self):
        now = dt.datetime.now()
        minimum_duration = min(self.trading_times)
        minutes_to_add = minimum_duration - (now.minute % minimum_duration)
        next_interval = now + dt.timedelta(minutes=minutes_to_add)
        # Set seconds and microseconds to zero
        next_interval = next_interval.replace(second=0, microsecond=0)
        
        return next_interval

    def process_candles(self, triggered):
        try:
            if len(triggered) > 0:
                self.log_to_main(f"process_candles: triggered {triggered}")
                
                while len(triggered) > 0:
                    print(triggered)
                    symbol = triggered.pop(0)
                    
                    print(self.trading_symbols[symbol])
                    
                    for strategy_manager in self.trading_symbols[symbol]:
                        print(f'process_candles: strategy_manager {strategy_manager}')
                        signal_decision = strategy_manager.generate_signal()
                        
                        if signal_decision == None or signal_decision.signal == 0:
                            continue
                        
                        print(f'process_candles: signal_decision {signal_decision}')
                        signal_container = (signal_decision, strategy_manager)
                        
                        self.current_signals.put(signal_container)
        except Exception as error:
            self.log_to_error(f'process_candles: Error {error}')
            raise error

                            
    def run_signal_executor(self):
        self.log_to_main("run_signal_executor: Running signal executor...")
        while self.is_running:
            try:
                if not self.current_signals.empty():
                    time.sleep(0.1)  # Prevent tight loop when no signals are present                        
                    signal_container = self.current_signals.get()
                    signal_decision, strategy_manager = signal_container
                    
                    self.log_to_main("run_signal_executor: Attempting entry of signal")

                    try:
                        placed_trade = self.mt5.place_order(
                            signal_decision.order_type,
                            signal_decision.symbol,
                            signal_decision.volume,
                            signal_decision.current_price,
                            signal_decision.stop_loss,
                            signal_decision.take_profit,
                            'Comment',
                            log_message=self.log_message,
                            log_to_error=self.log_to_error
                        )
                        
                        if placed_trade is None:
                            raise ValueError(f"Failed to place order for {signal_decision.symbol}")

                        self.log_message(f"run_signal_executor: Successfully placed {signal_decision.symbol}", signal_decision.symbol)
                        self.log_to_main(f"run_signal_executor: Successfully placed {signal_decision.symbol} for {signal_decision.symbol}")

                    except ConnectionError as ce:
                        self.log_to_error(f"run_signal_executor: Connection error while placing order for {signal_decision.symbol}: {ce}")

                    except ValueError as ve:
                        self.log_to_error(f"run_signal_executor: Value error (order issue) for {signal_decision.symbol}: {ve}")

                    except Exception as e:
                        self.log_to_error(f"run_signal_executor: Unexpected error while processing signal for {signal_decision.symbol}: {e}")
                        self.error_count += 1
                        raise e
                        
            except Exception as e:
                self.log_to_error(f"run_signal_executor: Critical error in run_signal_executor thread: {e}")
                self.error_count += 1
            finally:            
                time.sleep(self.bot_config.sleep_time)
    
    def run_signal_processor(self):
        self.log_message("run_signal_processor: Running trade processor...", "trade_processor")

        with ThreadPoolExecutor() as executor:
            while self.is_running:
                try:
                    if not self.current_signals.empty():
                        time.sleep(0.1)  # Prevent tight loop when no signals are present
                        
                        while not self.current_signals.empty():
                            signal_container = self.current_signals.get()
                            signal_decision, strategy_manager = signal_container

                            self.log_to_main(f"run_signal_executor: Submitting entry of signal for {signal_decision.symbol}")

                            # Submit the task to the thread pool with unpacked parameters
                            executor.submit(
                                process_signal,
                                self.is_running,
                                signal_decision,
                                self.mt5,
                                strategy_manager,
                                self.log_message,
                                self.log_to_error
                            )

                except Exception as e:
                    self.log_to_error(f"Error in run_signal_processor loop: {e}")

    def run_bot(self):
        self.log_to_main("run_bot: Running bot...")
        while self.is_running:
            try:
                print("run_bot: executing process_candles()")
                self.process_candles(self.candle_manager.update_timings())
                next_interval = self.get_next_interval()
                sleep_duration = (next_interval - dt.datetime.now()).total_seconds()
                print(f"run_bot: complete process_candles(), time_duration {sleep_duration}")
                
                time.sleep(sleep_duration)
            except Exception as e:
                self.log_to_error(f"run_bot: Critical error in run_bot thread: {e}")
                self.error_count += 1

                    
    def stop(self):
        self.log_to_main("stop: Gracefully stop the threads")
        
        # self.trade_manager.close_open_trades()

        # for thread in threading.enumerate():
        #     if thread != threading.main_thread():
        #         thread.join()
                
        self.is_running = False
        
        self.log_to_main("stop: Bot has been stopped.")

    def run(self):
        try: 
            run_bot_thread = threading.Thread(target=self.run_bot, name="run_bot_thread")
            run_bot_thread.start()
            
            if self.bot_config.signal_management.trade_processor:
                run_signal_executor = threading.Thread(target=self.run_signal_processor, name="run_trade_processor_thread")
            else:
                run_signal_executor = threading.Thread(target=self.run_signal_executor, name="run_signal_executor_thread")
                
            run_signal_executor.start()
            
            while self.is_running:
                if not run_bot_thread.is_alive():
                    self.log_to_error("run: Bot thread has unexpectedly stopped.")
                    break 
                
                if not run_signal_executor.is_alive():
                    self.log_to_error("run: Signal executor thread has unexpectedly stopped.")
                    break 
                
                time.sleep(1)
        except KeyboardInterrupt:
            self.log_to_main("run: KeyboardInterrupt received, stopping the bot...")
            self.stop()  # Gracefully stop the bot on Ctrl+C
        except Exception as e:
            self.log_to_error(f"run: Critical error in main thread: {e}")
            self.stop()
        finally:
            self.stop()
            run_bot_thread.join()
            run_signal_executor.join()
            self.log_to_main("run: Bot has been stopped.")
