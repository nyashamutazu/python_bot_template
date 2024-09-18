
import time
import pandas as pd
from api.metatrader_api import MT5
from bot.strategy_manager import StrategyManager
from models.signal_decision import SignalDecision
from utils.utils import granularity_to_minutes

def process_signal(is_running: bool, signal_decision: SignalDecision, mt5: MT5, strategy_manager: StrategyManager, log_message: callable, log_to_error: callable):
    print(1)
    interval = 1
    symbol = signal_decision.symbol
    granularity = strategy_manager.strategy.granularity

    # Fetch the initial candles
    timeframe_df = mt5.fetch_candles(symbol, granularity, log_to_error, count=2)
    if timeframe_df is None or timeframe_df.empty:
        log_to_error(f"Failed to fetch candles for {symbol}")
        return None

    last_timeframe_candle = timeframe_df.iloc[-1]
    last_timeframe_low = last_timeframe_candle.Low
    last_timeframe_high = last_timeframe_candle.High

    granularity_to_seconds = granularity_to_minutes(granularity) * 60
    print(12)

    while is_running:
        try:
            log_message(f"process_signal: Checking for entry signal for {symbol}", "trade_processor")
            tick_info = mt5.mt5.symbol_info_tick(symbol)
            if tick_info is None:
                log_to_error(f"Failed to get tick info for {symbol}")
                continue

            current_time = pd.to_datetime(tick_info.time, unit="s")

            if tick_info.time % granularity_to_seconds == 0:
                timeframe_df = mt5.fetch_candles(symbol, granularity, log_to_error, count=2)
                last_timeframe_candle = timeframe_df.iloc[-1]
                last_timeframe_low = last_timeframe_candle.Low
                last_timeframe_high = last_timeframe_candle.High

            if signal_decision.signal == 1 and last_timeframe_high < tick_info.ask:
                placed_trade = process_place_order(signal_decision, mt5, log_message, log_to_error)
                return placed_trade

            if signal_decision.signal == -1 and last_timeframe_low > tick_info.ask:
                placed_trade = process_place_order(signal_decision, mt5, log_message, log_to_error)
                return placed_trade

            if tick_info.time % 5 == 0:
                print(f"Symbol: {symbol}, Time: {tick_info.time}, Bid: {tick_info.bid}, Ask: {tick_info.ask}, Last: {tick_info.last}")

            time.sleep(interval)
        except Exception as error:
            print(f"process_signal:Error for {symbol}: {error}")
            log_to_error(f"process_signal: Error for {symbol}: {error}")
            raise error

def process_place_order(signal_decision: SignalDecision, mt5: MT5, log_message: callable, log_to_error: callable):
    placed_trade = mt5.place_order(
        signal_decision.order_type,
        signal_decision.symbol,
        signal_decision.volume,
        signal_decision.current_price,
        signal_decision.stop_loss,
        signal_decision.take_profit,
        'Comment',
        log_message=log_message,
        log_to_error=log_to_error
    )

    if placed_trade is None:
        raise ValueError(f"Failed to place order for {signal_decision.symbol}")

    log_message(f"run_signal_executor: Successfully placed {signal_decision.symbol}", signal_decision.symbol)
    log_message(f"run_signal_executor: Successfully placed {signal_decision.symbol} for {signal_decision.symbol}", "main")
    
    return placed_trade
