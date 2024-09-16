import pandas as pd
from datetime import datetime
from typing import Optional

from models.individual_strategy import IndividualStrategy
from models.signal_decision import SignalDecision

# Function to articulate run_strategy
def run_strategy(
    candle_data: pd.DataFrame,
    symbol: str,
    strategy: IndividualStrategy,
    log_message,
    log_to_error,
) -> Optional[SignalDecision]:
    try:
        log_message(f"run_strategy: running strategy analysis", symbol)

        # Initialize variables
        signal = 0
        sl = 0  # Stop Loss
        tp = 0  # Take Profit

        """
        INSERT STRATEGY IN THIS AREA
        This example uses an SMA crossover strategy.
        """

        short_sma = candle_data['Close'].rolling(window=trade_settings['short_window']).mean()
        long_sma = candle_data['Close'].rolling(window=trade_settings['long_window']).mean()

        if short_sma.iloc[-1] > long_sma.iloc[-1]:
            signal = 1  # Buy signal
            order_type = "BUY_STOP"
            sl = candle_data['Low'].min()  # Example stop loss: the Lowest price in the current dataset
            tp = candle_data['Close'].iloc[-1] + (candle_data['Close'].iloc[-1] - sl) * trade_settings['profit_ratio']  # Example take profit
        elif short_sma.iloc[-1] < long_sma.iloc[-1]:
            signal = -1  # Sell signal
            order_type = "SELL_STOP"
            sl = candle_data['High'].max()  # Example stop loss: the Highest price in the current dataset
            tp = candle_data['Close'].iloc[-1] - (sl - candle_data['Close'].iloc[-1]) * trade_settings['profit_ratio']  # Example take profit

        # If a signal is generated, return a SignalDecision
        if signal != 0:
            signal_decision = SignalDecision(
                symbol=symbol,
                order_type=order_type,
                current_price=candle_data['Close'].iloc[-1],
                volume=volume,
                risk=trade_settings['risk'],
                take_profit=tp,
                stop_loss=sl,
                signal_timestamp=datetime.now()
            )
            log_message(f"run_strategy: Signal generated for {symbol}: {signal_decision}")
            return signal_decision

        log_message(f"run_strategy: completed strategy analysis, no signal generated", symbol)
        return None  # No trade signal generated

    except Exception as error:
        log_to_error(f"run_strategy: Failed running strategy for {symbol}")
        log_to_error(error)
        return None