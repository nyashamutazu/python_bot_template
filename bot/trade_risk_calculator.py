import constants.defs as defs
import decimal

def calculate_lot_size(mt5, symbol, trade_decision, price_entry, stop_loss, trade_risk, log_message):
    log_message('calculate_lot_size:', symbol)
    
    symbol_info = mt5.mt5.symbol_info(symbol)
    
    pip_value = symbol_info.trade_tick_value
    volume_step = symbol_info.volume_step
    
    if trade_decision == 1:
        price = symbol_info.ask
    elif trade_decision == -1:
        price = symbol_info.bid
    
    trade_multiper = symbol_info.trade_tick_size
    num_pips = (abs(price_entry - stop_loss) / trade_multiper)

    balance = mt5.mt5.account_info().balance
    risk_amt = (trade_risk/100) * balance
    
    # Volume 
    d_v = decimal.Decimal(str(volume_step))
    d_v = abs(d_v.as_tuple().exponent)
    
    # Multiplier
    d_p = decimal.Decimal(str(trade_multiper))
    d_p = abs(d_p.as_tuple().exponent)
    
    units = round(risk_amt / (num_pips * pip_value), d_v)

    return units, trade_multiper, d_p