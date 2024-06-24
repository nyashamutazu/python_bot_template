class TradeManagerSettings:

    def __init__(self, ob, tradable_pairs):
        self.trade_risk = ob['trade_risk']
        self.timezone = ob['timezone']
        self.trailing_stop = ob['trailing_stop']
        self.sleep_time = ob['sleep_time']
        
    def __repr__(self):
        return str(vars(self))

    @classmethod
    def settings_to_str(cls, settings):
        ret_str = "Trade Settings:\n"
        for _, v in settings.items():
            ret_str += f"{v}\n"

        return ret_str