import pandas as pd
import MetaTrader5 as mt5
import pytz
import logging
import time

import datetime as dt

import constants.credentials as credentials
import constants.defs as defs

class MT5:
    MAX_LOGIN_ATTEMPTS = 3  # Define the max number of login attempts
    RETRY_DELAY = 5  # Delay in seconds before retrying the login

    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO) 
        self.mt5 = mt5
        
    def attempt_login(self) -> bool:
        """Attempts to log in to the MT5 account with retry logic."""
        for attempt in range(1, self.MAX_LOGIN_ATTEMPTS + 1):
            if self.login():
                logging.info(f"Connected to account #{credentials.ACCOUNT_ID}")
                return True
            else:
                error_code = self.mt5.last_error()
                logging.error(f"Login attempt {attempt} failed for account #{credentials.ACCOUNT_ID}, error code: {error_code}")
                
                if attempt < self.MAX_LOGIN_ATTEMPTS:
                    logging.info(f"Retrying login in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logging.error(f"Max login attempts reached. Unable to connect to account #{credentials.ACCOUNT_ID}.")
                    return False
        
        return False
    
    def login(self) -> bool:
        """Logs in to the MetaTrader 5 account."""
        if not self.mt5.initialize(path=defs.METATRADER_PATH):
            logging.error(f"Failed to initialize MetaTrader 5, error: {self.mt5.last_error()}")
            return False

        authorized = self.mt5.login(
            credentials.ACCOUNT_ID,
            password=credentials.ACCOUNT_PASSWORD,
            server=credentials.ACCOUNT_SERVER
        )
        
        if authorized:
            return True
        else:
            logging.error(f"Login failed for account #{credentials.ACCOUNT_ID}, error code: {self.mt5.last_error()}")
            return False

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
            
            print(f"palce_order: {request}")

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

            raise error

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
        symbol: str,
        mt5_timeframe: str,
        log_to_error: callable,
        count: int = 200,
    ) -> pd.DataFrame:
        try:
            # Set the correct timeframe for MT5 query
            mt5_timeframe = self.set_query_timeframe(mt5_timeframe)
            hist_data = self.mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            if hist_data is None or len(hist_data) == 0:
                raise ValueError(f"No data returned for {symbol} in {mt5_timeframe}")
            
            # Convert to DataFrame and configure it
            hist_data_df = self.configure_df(hist_data)
            return hist_data_df
        except Exception as error:
            # Log detailed error message
            log_to_error(f"Error: fetch_candles failed for {symbol} in {mt5_timeframe}. Error: {error}")
            return pd.DataFrame()  # Return an empty DataFrame on failure


    # Function to query previous candlestick data from MT5
    def query_historic_data(self, symbol, number_of_candles, granularity):
        # Convert the timeframe into an MT5 friendly format
        mt5_timeframe = self.set_query_timeframe(granularity)
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
