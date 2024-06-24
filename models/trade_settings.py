class TradeSettings:

    def __init__(self, ob, pair):
        self.timeframes = ob['timeframes']
        self.settings = ob['settings']        

    def __repr__(self):
        return str(vars(self))

    @classmethod
    def settings_to_str(cls, settings):
        ret_str = "Trade Settings:\n"
        for _, v in settings.items():
            ret_str += f"{v}\n"

        return ret_str