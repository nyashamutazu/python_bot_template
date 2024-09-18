import pandas as pd
from datetime import datetime
from typing import Optional

from bot.risk_management import calculate_lot_size
from models.individual_strategy import IndividualStrategy
from models.signal_decision import SignalDecision

# Function to articulate run_strategy
def run_strategy(
    candle_data: pd.DataFrame,
    symbol: str,
    strategy: IndividualStrategy,
    log_message: callable,
    log_to_error: callable,
) -> Optional[SignalDecision]:
    try:
        log_message(f"run_strategy: running strategy analysis", symbol)

        # Initialize variables
        signal = 0
        sl = 0  # Stop Loss
        tp = 0  # Take Profit

        # Calculate short and long SMAs based on the trade settings
        short_sma = candle_data['Close'].rolling(window=5).mean()
        long_sma = candle_data['Close'].rolling(window=20).mean()

        # Check for buy or sell signals
        if short_sma.iloc[-1] > long_sma.iloc[-1]:
            signal = 1  # Buy signal
            order_type = "BUY_STOP"
            sl = candle_data['Low'].min()  # Example stop loss: Lowest price in the dataset
            tp = candle_data['Close'].iloc[-1] + (candle_data['Close'].iloc[-1] - sl) * strategy.profit_ratio  # Take profit calculation
        elif short_sma.iloc[-1] < long_sma.iloc[-1]:
            signal = -1  # Sell signal
            order_type = "SELL_STOP"
            sl = candle_data['High'].max()  # Example stop loss: Highest price in the dataset
            tp = candle_data['Close'].iloc[-1] - (sl - candle_data['Close'].iloc[-1]) * strategy.profit_ratio  # Take profit calculation

        # If a signal is generated, return a SignalDecision object
        if signal != 0:
            signal_decision = SignalDecision(
                signal=signal,
                symbol=symbol,
                order_type=order_type,
                current_price=candle_data['Close'].iloc[-1],
                volume=None,
                risk=strategy.risk,
                take_profit=tp,
                stop_loss=sl,
                signal_timestamp=datetime.now()
            )
            
            log_message(f"run_strategy: Signal generated for {symbol}: {signal_decision}", symbol)
            return signal_decision

        log_message(f"run_strategy: completed strategy analysis, no signal generated", symbol)
        return None  # No trade signal generated

    except Exception as error:
        log_to_error(f"run_strategy: Failed running strategy for {symbol}")
        log_to_error(error)
        raise error