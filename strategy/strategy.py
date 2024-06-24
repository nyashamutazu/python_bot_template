import pandas as pd

# Function to articulate run_startegy
def run_startegy(
    candle_data,
    symbol,
    trade_settings,
    trade_dir,
    pattern_nm,
    log_message,
    log_to_error,
):
    try:
        log_message(f"run_strategy: running strategy analysis", symbol)

        # TO::DO REMOVE, signal, sl and tp
        signal = 0
        sl = 0
        tp = 0

        """
        
        INSERT STRATEGY IN THIS AREA
        USING SIGNAL OR/AND STOP LOSS
        
        """

        if signal != 0:
            return signal, sl, tp

        log_message(f"run_strategy: completed strategy analysis", symbol)
        return 0, "No trade"
    except Exception as error:
        log_to_error(f"Failed running strategy for {symbol}")
        log_to_error(error)

        return None, error
