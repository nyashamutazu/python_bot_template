from dataclasses import dataclass

from models.indicators import Indicators

@dataclass
class IndividualStrategy:
    granularity: str
    indicators: Indicators
    risk: float
    profit_ratio: float
    
    def __repr__(self):
        return (f"IndividualStrategy(granularity='{self.granularity}', "
                f"indicators={self.indicators}, risk={self.risk})")
