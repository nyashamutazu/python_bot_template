from dataclasses import dataclass
from typing import Dict, List

from dataclasses import dataclass
from bot.strategy_manager import StrategyManager
from models.risk_management import RiskManagement

@dataclass
class StrategyConfiguration:
    risk_management: RiskManagement
    trading_symbols: Dict[str, List[StrategyManager]]

    def __repr__(self):
        return (f"StrategyConfig(risk_management={self.risk_management}, "
                f"trading_symbols={self.trading_symbols})")
    
    @classmethod
    def settings_to_str(cls, settings):
        return_str = "Trade Settings: \n"
        for _, v in settings.trading_symbols.items():
            return_str += f'{_}: \n'
            for t in v:
                return_str += f'\t{t}\n'

        return_str += f'\n'

        return return_str