from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List, Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

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
    volume: Optional[float]
    vwap: Optional[float]

class ForexDataList(BaseModel):
    """
    Pydantic model for a list of forex price data.
    """
    # data: List[ForexData]
    data : dict = {}
    api_data: List[ForexData]

    @classmethod
    def from_query_result(cls, rows):
        return cls(data={
           row.symbol: ForexData(
                symbol=row.symbol,
                date=row.date,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
                volume=row.volume if hasattr(row, 'volume') else None
            )
            for row in rows
        }) 
        
    @classmethod
    def from_api_response(cls, symbol, api_response):
        """
        Create a ForexDataList from a Polygon.io API response.
        
        Args:
            symbol: The forex pair symbol (e.g., "GBPUSD")
            api_response: The JSON response from the Polygon.io API
        """
        forex_data = [
            ForexData(
                symbol=symbol,
                date=datetime.fromtimestamp(entry["t"] / 1000),  # Convert timestamp to datetime
                open=entry["open"],
                high=entry["high"],
                low=entry["low"],
                close=entry["close"],
                volume=entry["volume"],
                vwap= entry["vwap"]
            )
            for entry in api_response.get("results", [])
        ]
        return cls(api_data=forex_data)
        
class Base(DeclarativeBase):
    pass

class DayData(Base):
    __tablename__ = "day"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str]
    open: Mapped[float]
    close: Mapped[float]
    volume: Mapped[float]
    high: Mapped[float]
    low: Mapped[float]
    vwap: Mapped[float]
    date: Mapped[datetime]
    
    def __repr__(self) -> str:
        return f"DayData(id={self.id!r}, symbol={self.symbol!r} ,open={self.open!r}, close= {self.close!r}, high={self.high!r},low={self.low!r},date={self.date!r},volume={self.volume!r},vwap={self.vwap!r})"
    