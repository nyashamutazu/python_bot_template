import decimal

def get_trade_multipler(price_1):
    if str(price_1).index('.') >= 3:  # JPY pair
        multiplier = 0.01
    else:
        multiplier = 0.0001
    
    return multiplier

def get_decimals_places(value):
    d_p = decimal.Decimal(str(value))
    d_p = abs(d_p.as_tuple().exponent)
    
    # Decimals places
    return d_p