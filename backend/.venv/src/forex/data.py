from venv import logger
from ..asset import connect_Polygon
from ..db.db import get_db_session
from sqlalchemy import text, select  # Ensure you import text from SQLAlchemy
from sqlalchemy.orm import Session
import logging
from ..models import  ForexDataList

logger = logging.getLogger(__name__)

forexPairs = [
  "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "NZDUSD", "AUDUSD", "USDCAD",
  "EURGBP", "EURJPY", "EURCHF", "EURNZD", "EURAUD", "EURCAD",
  "GBPJPY", "GBPCHF", "GBPNZD", "GBPAUD", "GBPCAD",
  "NZDJPY", "NZDCHF", "NZDCAD", "NZDAUD",
  "AUDJPY", "AUDCHF", "AUDCAD",
  "CADJPY", "CADCHF",
  "CHFJPY"
]

class Forex:
    async def get_last_uploaded_date(self) -> ForexDataList:
        """
        Retrieve the last uploaded date for all unique symbols from the database.
        
        :return: ForexUpdateList containing symbols and their last update dates.
        """
        try:
            async with get_db_session() as session:
                query = text("""
                    WITH latest_dates AS (
                    SELECT 
                        symbol,
                        MAX(date) as date
                    FROM day
                    GROUP BY symbol
                    )
                    SELECT 
                        d.symbol,
                        d.date as date,
                        d.open,
                        d.high,
                        d.low,
                        d.close
                    FROM day d
                    INNER JOIN latest_dates ld 
                        ON d.symbol = ld.symbol 
                        AND d.date = ld.date;
                """)
                
                result = await session.execute(query)
                rows = result.fetchall()
                print(rows)
                return ForexDataList.from_query_result(rows)
        except Exception as e:
            logger.error(f"Error retrieving last uploaded dates: {e}")
            return ForexDataList(data=[])
        

   
         