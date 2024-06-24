# import mt5_interface
from models.trade_settings import TradeSettings
import strategy.strategy as strategy

from datetime import datetime as dt

import numpy as np

from bot.trade_risk_calculator import calculate_lot_size
from utils.utils import get_trade_multipler, get_decimals_places


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
