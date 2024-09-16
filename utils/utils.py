import decimal

def granularity_to_minutes(granularity: str) -> int:

    granularity_map = {
        'M1': 1,
        'M5': 5,
        'M15': 15,
        'M30': 30,
        'H1': 60,
        'H4': 240,
        'D': 1440,  # 24 hours * 60 minutes
        'W': 10080, # 7 days * 24 hours * 60 minutes
        'M': 43200  # 30 days * 24 hours * 60 minutes (approximation)
    }

    if granularity not in granularity_map:
        raise ValueError(f"Unsupported granularity: {granularity}")
    
    return granularity_map[granularity]

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