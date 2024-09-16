# import mt5_interface
from models.trade_management import TradeSettings
import strategy.strategy as strategy

from datetime import datetime as dt

import numpy as np

from bot.risk_management import calculate_lot_size
from utils.utils import get_trade_multipler, get_decimals_places

import time
import datetime as dt
from typing import List

import time
import datetime as dt
from typing import List

class TradeManager:
    def __init__(self, mt5, risk_management, log_message, log_to_error):
        """Initializes the TradeManager with MT5 instance, risk management rules, and logging functions."""
        self.mt5 = mt5  # MT5 instance for trading operations
        self.risk_management = risk_management  # Risk management settings
        self.log_message = log_message  # Function for logging general messages
        self.log_to_error = log_to_error  # Function for logging error messages
        self.is_running = True  # Flag to control the trade monitoring loop
        self.daily_loss = 0  # Track daily loss to stop trading if threshold is met
        
    def close_open_trades(self):
        """Closes all open trades before stopping the bot."""
        self.log_message("close_open_trades: Closing all open trades before stopping...")

        open_trades = self.mt5.get_open_trades()
        for trade in open_trades:
            try:
                # Attempt to close the trade
                self.mt5.close_order(trade.order_id)
                self.log_message(f"close_open_trades: Successfully closed trade for {trade.symbol}")

            except Exception as e:
                self.log_to_error(f"close_open_trades: Failed to close trade for {trade.symbol}: {e}")


    def monitor_open_trades(self):
        """Monitors open trades and adjusts stop-loss or take-profit if necessary."""
        self.log_message("monitor_open_trades: Monitoring open trades...")

        try:
            open_trades = self.mt5.get_open_trades()  # Fetch open trades
            for trade in open_trades:
                # Get the current market price for the traded pair
                current_price = self.mt5.get_current_price(trade.symbol)
                # Adjust stop-loss or take-profit based on your strategy
                self.manage_trade(trade, current_price)

        except Exception as e:
            self.log_to_error(f"monitor_open_trades: Critical error while monitoring trades: {e}")

    def manage_trade(self, trade, current_price):
        """Manages an open trade by adjusting stop-loss or take-profit if conditions are met."""
        if trade.order_type == "BUY_ORDER":
            # Check if the current price has moved favorably for a BUY order
            if current_price > trade.price_open + self.risk_management["max_stop_loss_percentage"] * trade.price_open:
                new_stop_loss = current_price - self.risk_management["max_stop_loss_percentage"] * trade.price_open
                if new_stop_loss > trade.stop_loss:
                    self.mt5.modify_order(trade.order_id, stop_loss=new_stop_loss)
                    self.log_message(f"manage_trade: Adjusted stop-loss for {trade.symbol} to {new_stop_loss}")

        elif trade.order_type == "SELL_ORDER":
            # Check if the current price has moved favorably for a SELL order
            if current_price < trade.price_open - self.risk_management["max_stop_loss_percentage"] * trade.price_open:
                new_stop_loss = current_price + self.risk_management["max_stop_loss_percentage"] * trade.price_open
                if new_stop_loss < trade.stop_loss:
                    self.mt5.modify_order(trade.order_id, stop_loss=new_stop_loss)
                    self.log_message(f"manage_trade: Adjusted stop-loss for {trade.symbol} to {new_stop_loss}")

    def close_trade_early(self, trade, current_price):
        """Closes a trade early if it meets specific conditions (e.g., profit threshold)."""
        current_profit = self.mt5.calculate_profit(trade)

        # Example: Close the trade early if it reaches the take-profit ratio
        take_profit_target = self.risk_management["take_profit_ratio"] * (trade.price_open - trade.stop_loss)
        if current_profit >= take_profit_target:
            self.mt5.close_order(trade.order_id)
            self.log_message(f"close_trade_early: Closed trade {trade.symbol} early with profit {current_profit}")

    def check_risk_limits(self, signal_decision):
        """Ensures that the trade meets risk management limits."""
        account_balance = self.mt5.get_account_balance()
        open_trades = self.mt5.get_open_trades()

        # Check the number of concurrent trades
        if len(open_trades) >= self.risk_management["max_concurrent_trades"]:
            self.log_to_error(f"check_risk_limits: Maximum concurrent trades reached. Ignoring new trade for {signal_decision.pair}.")
            return False

        # Calculate potential risk for this trade
        stop_loss_distance = signal_decision.current_price - signal_decision.stop_loss
        risk_per_trade = stop_loss_distance * signal_decision.volume
        max_risk_per_trade = self.risk_management["max_trade_percentage"] * account_balance

        if risk_per_trade > max_risk_per_trade:
            self.log_to_error(f"check_risk_limits: Risk for {signal_decision.pair} exceeds allowed maximum. Ignoring trade.")
            return False

        return True

    def track_daily_loss(self):
        """Tracks the bot's daily losses and stops trading if the max daily loss limit is reached."""
        total_loss = sum([trade.loss for trade in self.mt5.get_closed_trades_today()])
        account_balance = self.mt5.get_account_balance()
        max_daily_loss = self.risk_management["max_daily_loss_percentage"] * account_balance

        if total_loss >= max_daily_loss:
            self.log_to_error(f"track_daily_loss: Max daily loss reached. No further trades today.")
            return False  # Stop trading for the day

        return True

    def run_trade_manager(self):
        """Main loop to monitor and manage open trades."""
        self.log_message("run_trade_manager: Running trade manager...")

        while self.is_running:
            try:
                if self.track_daily_loss():  # Stop trading if daily loss limit is hit
                    self.monitor_open_trades()  # Continuously monitor and manage open trades
            except Exception as e:
                self.log_to_error(f"run_trade_manager: Critical error in trade management: {e}")
            finally:
                time.sleep(5)  # Adjust sleep time as needed to control trade management frequency

    def stop_trade_manager(self):
        """Stops the trade manager process."""
        self.is_running = False
        self.log_message("stop_trade_manager: Trade manager stopped.")



# Function to articulate strategy_one
def run(
    mt5,
    bot_settings,
    pairs_data,
    symbol,
    mt5_timeframe,
    pattern,
    trade_dir,
    candle_time,
    log_message,
    log_to_error,
):
    try:
        log_message(f"trade_manager.run(): candle_time:{candle_time}", symbol)

        candle_data = mt5.fetch_candles(
            symbol=symbol,
            mt5_timeframe=mt5_timeframe,
            log_message=log_message,
            log_to_error=log_to_error,
        )
        current_candle = candle_data.iloc[-1]
        current_candle_time = current_candle.Time
        # Get open open_positions
        positions = mt5.get_open_positions()

        # Pass positions to update_trailing_stop given trailing stop requirement
        if len(positions) and bot_settings["trailing_stop"]:
            for position in positions:
                if position.symbol == symbol:
                    modify_position_response = update_trailing_stop(
                        mt5=mt5,
                        symbol=symbol,
                        order=position,
                        log_message=log_message,
                        log_to_error=log_to_error,
                    )
                    return 200, "Updated Trail"

        trade_settings = pairs_data[symbol].settings

        print(1)
        # Run Strategy and get trade decision and the sl
        strategy_analysis = strategy.run_startegy(
            candle_data,
            symbol,
            trade_settings,
            trade_dir,
            pattern,
            log_message,
            log_to_error,
        )

        print("ANALYSIS", strategy_analysis)

        if strategy_analysis[0] == None:
            log_to_error(f"Error: failed running trade_manager.run(): symbol: {symbol}")
            log_to_error(strategy_analysis[1])
            return 500, strategy_analysis[1]

        if strategy_analysis[0] == 0:
            return 200, strategy_analysis[1]

        trade_decision = strategy_analysis[0]

        if strategy_analysis[1] != None:
            sl = strategy_analysis[1]

        if strategy_analysis[2] != None:
            entry = strategy_analysis[2]

        if strategy_analysis[3] != None:
            tp = strategy_analysis[3]

        if trade_decision != 0:
            # Creating a new order
            order = create_new_order(
                mt5=mt5,
                trade_decision=trade_decision,
                stop_loss=sl,
                entry=entry,
                take_profit=tp,
                candle_data=candle_data,
                symbol=symbol,
                trade_risk=bot_settings["trade_risk"],
                log_message=log_message,
                log_to_error=log_to_error,
            )

            if len(order):
                (
                    order_type,
                    symbol,
                    unit,
                    entry_price,
                    stop_loss,
                    take_profit,
                    comment,
                ) = order

                order_result = mt5.place_order(
                    order_type,
                    symbol,
                    unit,
                    entry_price,
                    stop_loss,
                    take_profit,
                    comment,
                    log_message,
                    log_to_error,
                )
                return 200, order_result
            return 200, "No order"
        else:
            return 500, None
    except Exception as e:
        log_to_error(f"Error: trade_manager.run(): symbol: {symbol}")
        log_to_error(e)
        return 500, e


# Function to create a new order based upon previous analysis
def create_new_order(
    mt5,
    trade_decision,
    stop_loss,
    entry,
    take_profit,
    candle_dataframe,
    symbol,
    trade_risk,
    log_message,
    log_to_error,
):
    # Extract the first row of the dataframe
    log_message(
        f"trade_manager.create_new_order(): trade_decision: {trade_decision}", symbol
    )
    last_row = candle_dataframe.iloc[-1]

    # Do nothing if outcome is "DoNothing
    if trade_decision == 0:
        return []
    elif trade_decision == 1:
        trade_multiper = get_trade_multipler(last_row.Close)

        # stop_loss = stop_loss - trade_multiper
        buy_stop = last_row.High + trade_multiper

        if entry:
            buy_stop = entry

        units, _, decimal_places = calculate_lot_size(
            mt5, symbol, trade_decision, buy_stop, stop_loss, trade_risk, log_message
        )

        # pip_distance = abs(buy_stop - stop_loss) / trade_multiper
        # num_pips = pip_distance * trade_multiper  # Convert pip_distance back into pips

        # buy_stop = round(buy_stop, decimal_places)
        # stop_loss = round(stop_loss, decimal_places)

        # if not take_profit:
        #     take_profit = buy_stop + num_pips
        #     take_profit = round(take_profit, decimal_places)

        comment = f"isl={stop_loss}"

        log_message(
            f"trade_manager.create_new_order(): trade_decision: BUY ORDER CREATED",
            symbol,
        )
        return ["BUY_STOP", symbol, units, buy_stop, stop_loss, take_profit, comment]

    elif trade_decision == -1:

        trade_multiper = get_trade_multipler(last_row.Close)
        # stop_loss = stop_loss + trade_multiper
        sell_stop = last_row.Low - trade_multiper

        if entry:
            sell_stop = entry

        units, _, decimal_places = calculate_lot_size(
            mt5, symbol, trade_decision, sell_stop, stop_loss, trade_risk, log_message
        )
        # # Calculate the order take_profit (2 times the pip distance, subtracted from the buy_stop)
        # pip_distance = abs(sell_stop - stop_loss) / trade_multiper
        # num_pips = pip_distance * 2 * trade_multiper

        # sell_stop = round(sell_stop, decimal_places)
        # stop_loss = round(stop_loss, decimal_places)

        # if not take_profit:
        #     take_profit = sell_stop - num_pips
        #     take_profit = round(take_profit, decimal_places)

        # Add in an order comment
        log_message(
            f"trade_manager.create_new_order(): trade_decision: SELL ORDER CREATED",
            symbol,
        )
        comment = f"isl={stop_loss}"

        return ["SELL_STOP", symbol, units, sell_stop, stop_loss, take_profit, comment]


# Function to update trailing stop if needed
def update_trailing_stop(mt5, symbol, order, log_message, log_to_error):

    order_number = order.ticket
    order_comment = order.comment
    order_open_price = order.price_open
    order_profit = order.profit
    order_sl = order.sl
    order_current_price = order.price_current
    order_decimal_places = get_decimals_places(order_open_price)

    # print('DP', order_decimal_places)
    initial_stop_loss = round(float(order_comment.split("=")[1]), order_decimal_places)

    # print('initial_stop_loss', initial_stop_loss)
    initial_price_difference = round(
        abs(order_open_price - initial_stop_loss), order_decimal_places
    )
    current_price_difference = round(
        abs(order_current_price - order_sl), order_decimal_places
    )

    if order_profit > 0 and current_price_difference >= initial_price_difference:

        # A BUY Position will have a take_profit > stop_loss
        if order_current_price > order_sl:

            new_stop_loss = round(
                order_current_price - initial_price_difference, order_decimal_places
            )
            # Test to see if new_stop_loss > current_stop_loss
            if new_stop_loss > order_sl:

                # New take_profit will be the difference between new_stop_loss and old_stop_loss added to take profit
                new_take_profit = order[12] + new_stop_loss - order_sl
                log_message(
                    "trade_manager.update_trailing_stops(): Attemping to update stop loss",
                    symbol,
                )

                # Send order to modify_position
                return mt5.modify_position(
                    order_number=order_number,
                    symbol=symbol,
                    new_stop_loss=new_stop_loss,
                    new_take_profit=new_take_profit,
                )

        elif order_current_price < order_sl:
            # If SELL, new_stop_loss = current_price - trailing_stop_pips
            new_stop_loss = round(
                order_current_price + initial_price_difference, order_decimal_places
            )

            # Test to see if new_stop_loss < current_stop_loss
            if new_stop_loss < order_sl:

                # New take_profit will be the difference between new_stop_loss and old_stop_loss subtracted from old take_profit
                new_take_profit = order[12] - new_stop_loss + order_sl
                log_message(
                    "trade_manager.update_trailing_stops(): Attemping to update stop loss",
                    symbol,
                )

                # Send order to modify_position
                return mt5.modify_position(
                    order_number=order_number,
                    symbol=symbol,
                    new_stop_loss=new_stop_loss,
                    new_take_profit=new_take_profit,
                )
