import pandas as pd
import MetaTrader5 as mt5
import pytz

import datetime as dt
import constants.credentials as credentials

import constants.defs as defs


class MT5:
    def __init__(self) -> None:
        pass

    def run(self):
        self.mt5 = self.attempt_login()
        
    def get_mt5(self):
        return self.mt5

    def attempt_login(self):
        authorized=mt5.login(account=credentials.ACCOUNT_ID,
            password=credentials.ACCOUNT_PASSWORD,
            server=credentials.ACCOUNT_SERVER)  # the terminal database password is applied if connection data is set to be remembered
        if authorized:
            print("connected to account #{}".format(credentials.ACCOUNT_ID))
        else:
            print("failed to connect at account #{}, error code: {}".format(credentials.ACCOUNT_ID, mt5.last_error()))
            print("retrying login attempt")
            
            if mt5.initialize(
                path=defs.METATRADER_PATH,
                login=credentials.ACCOUNT_ID,
                password=credentials.ACCOUNT_PASSWORD,
                server=credentials.ACCOUNT_SERVER,
            ):
                print("connection established")
            
        return mt5
        

    def configure_df(self, hist_data):
        hist_data_df = pd.DataFrame(hist_data)
        hist_data_df.time = pd.to_datetime(hist_data_df.time, unit="s")
        hist_data_df.rename(
            columns={
                "time": "Time",
                "open": "Open",
                "high": "High",
                "close": "Close",
                "low": "Low",
                "tick_volume": "Volume",
                "real_volume": "_Volume",
                "spread": "Spread",
            },
            inplace=True,
        )

        return hist_data_df

    # Function to place a trade on MT5
    def place_order(
        self,
        order_type,
        symbol,
        volume,
        price,
        stop_loss,
        take_profit,
        comment,
        log_message,
        log_to_error,
    ):
        try:
            # If order type SELL_STOP
            if order_type == "SELL_STOP":
                order_type = self.mt5.ORDER_TYPE_SELL_STOP
            elif order_type == "BUY_STOP":
                order_type = self.mt5.ORDER_TYPE_BUY_STOP

            # Create the request
            request = {
                "action": self.mt5.TRADE_ACTION_PENDING,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "sl": stop_loss,
                "tp": take_profit,
                "type_filling": self.mt5.ORDER_FILLING_RETURN,
                "type_time": self.mt5.ORDER_TIME_GTC,
                "comment": f"{comment}",
            }

            # Send the order to MT5
            order_result = self.mt5.order_send(request)

            # Notify based on return outcomes
            if order_result[0] == 10009:
                log_message(
                    f"metatrader_api.place_order(): Order for {symbol} successful",
                    symbol,
                )
            else:
                log_message(
                    f"Error placing order. ErrorCode {order_result[0]}, Error Details: {order_result}",
                    symbol,
                )
                log_to_error(
                    f"Error placing order. {symbol} ErrorCode {order_result[0]}, Error Details: {order_result}"
                )

            return order_result
        except Exception as error:
            log_message(f"Error placing order {error}", symbol)
            log_to_error(
                f"metatrader_api.place_order(): Error placing order symbol: {error}"
            )

            return None

    # Function to convert a timeframe string in MetaTrader 5 friendly format
    def set_query_timeframe(self, timeframe):
        # Implement a Pseudo Switch statement. Note that Python 3.10 implements match / case but have kept it this way for
        # backwards integration
        if timeframe == "M1":
            return mt5.TIMEFRAME_M1
        elif timeframe == "M2":
            return mt5.TIMEFRAME_M2
        elif timeframe == "M3":
            return mt5.TIMEFRAME_M3
        elif timeframe == "M4":
            return mt5.TIMEFRAME_M4
        elif timeframe == "M5":
            return mt5.TIMEFRAME_M5
        elif timeframe == "M6":
            return mt5.TIMEFRAME_M6
        elif timeframe == "M10":
            return mt5.TIMEFRAME_M10
        elif timeframe == "M12":
            return mt5.TIMEFRAME_M12
        elif timeframe == "M15":
            return mt5.TIMEFRAME_M15
        elif timeframe == "M20":
            return mt5.TIMEFRAME_M20
        elif timeframe == "M30":
            return mt5.TIMEFRAME_M30
        elif timeframe == "H1":
            return mt5.TIMEFRAME_H1
        elif timeframe == "H2":
            return mt5.TIMEFRAME_H2
        elif timeframe == "H3":
            return mt5.TIMEFRAME_H3
        elif timeframe == "H4":
            return mt5.TIMEFRAME_H4
        elif timeframe == "H6":
            return mt5.TIMEFRAME_H6
        elif timeframe == "H8":
            return mt5.TIMEFRAME_H8
        elif timeframe == "H12":
            return mt5.TIMEFRAME_H12
        elif timeframe == "D1":
            return mt5.TIMEFRAME_D1
        elif timeframe == "W1":
            return mt5.TIMEFRAME_W1
        elif timeframe == "MN1":
            return mt5.TIMEFRAME_MN1
    
    # Function to cancel an order
    def cancel_order(self, order_number):
        # Create the request
        request = {
            "action": self.mt5.TRADE_ACTION_REMOVE,
            "order": order_number,
            "comment": "Order Removed",
        }
        # Send order to MT5
        order_result = self.mt5.order_send(request)
        return order_result

    # Function to modify an open position
    def modify_position(self, order_number, symbol, new_stop_loss, new_take_profit):
        # Create the request
        request = {
            "action": self.mt5.TRADE_ACTION_SLTP,
            "symbol": symbol,
            "sl": new_stop_loss,
            # "tp": new_take_profit,
            "position": order_number,
        }
        # Send order to MT5
        order_result = self.mt5.order_send(request)

        if order_result[0] == 10009:
            return True
        else:
            return False

    def fetch_candles(
        self,
        symbol,
        log_message,
        log_to_error,
        count=100,
        mt5_timeframe="M30",
    ):
        try:
            mt5_timeframe = self.set_query_timeframe(mt5_timeframe)
            hist_data = self.mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            hist_data_df = self.configure_df(hist_data)

            return hist_data_df
        except Exception as error:
            log_to_error(
                f"Error: mt5.fetch_candles: Failed to fetch candles for {symbol}"
            )
            log_to_error(error)

            return pd.DataFrame()

    # Function to query previous candlestick data from MT5
    def query_historic_data(self, symbol, number_of_candles):
        # Convert the timeframe into an MT5 friendly format
        mt5_timeframe = mt5.TIMEFRAME_M5
        # Retrieve data from MT5
        rates = self.mt5.copy_rates_from_pos(
            symbol, mt5_timeframe, 0, number_of_candles
        )

        return rates

    # Function to retrieve all open orders from MT5
    def get_open_orders(self):
        orders = self.mt5.orders_get()
        order_array = []
        for order in orders:
            order_array.append(order[0])
        return order_array

    # Function to retrieve all open positions
    def get_open_positions(self):
        # Get position objects
        positions = self.mt5.positions_get()
        # Return position objects
        return positions
