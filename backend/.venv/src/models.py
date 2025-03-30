from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class ForexData(BaseModel):
    """
    Pydantic model for forex price data.
    """
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[int]

class ForexDataList(BaseModel):
    """
    Pydantic model for a list of forex price data.
    """
    data: List[ForexData]

    @classmethod
    def from_query_result(cls, rows):
        return cls(data=[
            ForexData(
                symbol=row.symbol,
                date=row.date,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
                volume=row.volume if hasattr(row, 'volume') else None
            )
            for row in rows
        ]) 
        
