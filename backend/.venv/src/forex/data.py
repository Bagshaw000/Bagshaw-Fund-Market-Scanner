import asyncio
import time
from typing import List
from venv import logger
from ..asset import connect_Polygon
from ..db.db import db,test_db_conn
import pytz
import logging
from ..models import  ForexDataList, ForexData
from polygon import RESTClient
from dotenv import dotenv_values
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

forexPairs = [
  "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "NZDUSD", "AUDUSD", "USDCAD", 
  "EURGBP", "EURJPY", "EURCHF", "EURNZD", "EURAUD", "EURCAD",
  "GBPJPY", "GBPCHF", "GBPNZD", "GBPAUD", "GBPCAD",
  "NZDJPY", "NZDCHF", "NZDCAD", "NZDAUD",
  "AUDJPY", "AUDCHF", "AUDCAD",
  "CADJPY", "CADCHF",
  "CHFJPY", 
]

class Forex:
    
    def __init__(self):
        self.config = dotenv_values(".env")
        self.db = db

 
 

           
           

    async def get_data(self):
        try: 
            client = RESTClient(self.config["ASSET_API_KEY"])
            
            last_update = await self.last_upload_date()
            print (last_update)
            
            
            for pair in forexPairs:
                print("started")
                # Check if they are in the last updated
                
                # for  last in last_update:
                #     print(last)
                if pair in last_update['data']:
                    ''' 
                    Check the last updated date of that symbol
                    
                    1. Get the day of that update. Check if the date was the previous day
                    
                    2. If the date was not the previous day data then make an api call from the next day
                    to the current date data
                    
                    '''
                    print(last_update['data'][pair])
                    
                    #Specifying the timezone
                    ny_tz = pytz.timezone("America/New_York")
                    # Get the current date
                    current_date = datetime.now(ny_tz)
                    
                    '''
                    Improvement api calls to polygon will occur during the weekends aswell
                    '''

                    # Subtract one day to get the previous date
                    previous_date = current_date - timedelta(days=1)
                    
                    formatted_previous_date: datetime =datetime.strptime( previous_date.strftime("%Y-%m-%d"),"%Y-%m-%d" )
                    
                    last_update_date: datetime = datetime.strptime(last_update['data'][pair]['date'],"%Y-%m-%d")
                    next_update_date: datetime = last_update_date + timedelta(days=1)
                    
                    formatted_last_updated_date: datetime = datetime.strptime(next_update_date.strftime("%Y-%m-%d"),"%Y-%m-%d")
                    print(formatted_last_updated_date)
                    print(formatted_previous_date)
                    print(next_update_date)
                  

                
                    
                    # Check if the last date that the system was update is less than yesterday date(which is meant to be the last date updated)
                    if formatted_last_updated_date <  formatted_previous_date :
                        update_pro = await self.get_asset_data(pair,'day',formatted_last_updated_date, formatted_previous_date)
                        
                       
                       
                        
                        update_dicts=[{
                            "symbol": pair,
                            "open": agg.open,
                            "high": agg.high,
                            "low": agg.low,
                            "close": agg.close,
                            "volume": agg.volume,
                            "vwap": agg.vwap,
                            "date": datetime.fromtimestamp(agg.timestamp / 1000) 
                        }for agg in update_pro]
                        
                        print(update_pro)
                        await self.store_symbol_data(update_dicts)
                    
                        print(f"Done updating this pair {pair}")
                        
                        time.sleep(20)
                        
                        '''
                        Update the data in the database
                
                        '''
                else:
                    '''
                    For new pairs get two year worth of data starting from the current date
                    '''
                        # Get the current date
                    current_date = datetime.now()

                    # Subtract one day to get the previous date
                    previous_date_two_yrs = current_date - timedelta(days=730)
                    
                    previous_date_one_day = current_date - timedelta(days=1)
                    
                    
                    formatted_previous_date: datetime =  previous_date_one_day.strftime("%Y-%m-%d")
                    
                    formatted_last_updated_date: datetime = previous_date_two_yrs.strftime("%Y-%m-%d")
                    
                  

                    print("Previous date:", previous_date_two_yrs)
                    print("Previous date:", previous_date_one_day)
                    
                    api_response = await self.get_asset_data(pair,'day',formatted_last_updated_date, formatted_previous_date)
                    
                    #if api_response:
                        #Mapping the api response to a format that allows bulk addition to database
                        
                    update_dicts=[{
                            "symbol": pair,
                            "open": agg.open,
                            "high": agg.high,
                            "low": agg.low,
                            "close": agg.close,
                            "volume": agg.volume,
                            "vwap": agg.vwap,
                            "date": datetime.fromtimestamp(agg.timestamp / 1000) 
                        }for agg in api_response]
                         
                         
               
                    
                    await self.store_symbol_data(update_dicts)
                    
                    print(f"Done updating this pair {pair}")
                   
                    time.sleep(20)


        except Exception as e:
                    logger.error(f"Error getting data: {e}")
    async def get_asset_data(self, pair:str, timeframe: str, from_ : str, to:str):
        client = RESTClient(self.config["ASSET_API_KEY"])

        aggs = []
        for a in client.list_aggs(
            f"C:{pair}",
            1,
            timeframe,
            from_,
            to,
            adjusted="true",
            sort="desc",
            limit=50000,
        ):aggs.append(a)
        
        return aggs
          
            
            
    async def last_upload_date(self):
        try:
            
            test_db = await test_db_conn()
            result = {}
          #Check database connection
            if test_db["status"] == 200:
               
                await self.db.connect()
                
                #Sellect the most recent symbol data
                latest_dates = await self.db.query_raw("""
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
                        d.close,
                        d.volume,
                        d.vwap
                    FROM day d
                    INNER JOIN latest_dates ld 
                        ON d.symbol = ld.symbol 
                        AND d.date = ld.date;
                """)
                
                for row in latest_dates:
                    symbol = row["symbol"]
                    
                    result[symbol]= row
             
                await self.db.disconnect() 
                
            
                return {"status":200, "data":result}
                
              
            else:
                      
             return {"status":500, "msg":"Database connection was not successful"}   
                
        except Exception as e:      
            logger.error(f"Error retrieving last uploaded dates: {e}")
            
            
    async def store_symbol_data(self, data: []):
        try:
            test_db = await test_db_conn()
            if test_db["status"] == 200:
                 await self.db.connect()
                 
                 day_data = await db.day.create_many(
                     data= data,
                     skip_duplicates=True
                 )
                 
                 await self.db.disconnect() 
            
         
        except Exception as e:      
            logger.error(f"Error retrieving last uploaded dates: {e}")    