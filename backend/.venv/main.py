from typing import Union
from src.db.db import test_db_conn
from src.forex.data import Forex
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
#from sqlalchemy.ext.asyncio import AsyncSession
import asyncio



app = FastAPI()
fx_obj = Forex()
# Create the scheduler globally
scheduler = BackgroundScheduler(timezone=pytz.timezone("America/New_York"))

def run_scheduler():
       # Create a scheduler
       scheduler = BackgroundScheduler(timezone=pytz.timezone("America/New_York"))

       # Schedule the job to run at 1 AM New York time every day
       scheduler.add_job(fx_obj.get_data, "cron", hour=1, minute=0)

       # Start the scheduler
       scheduler.start()

@app.on_event("startup")
async def startup_event():
    """
    Function that runs when the server starts up.
    Tests the database connection and logs the result.
    """
    print("🚀 Starting up server...")
    try:
        result = await test_db_conn()
        run_scheduler()
        # await create_tables()
        if result["status"] == 200:
            print("✅ Database connection test successful!")
        else:
            print(f"❌ Database connection test failed: {result['message']}")
    except Exception as e:
        print(f"❌ Error testing database connection: {str(e)}")

@app.on_event("shutdown")
def shutdown_event():
    # Shut down the scheduler when the app stops
    scheduler.shutdown()



@app.get("/")
def read_root():
    
    return {"Hello": "World"}

@app.get('/forex/last_update')
async def get_forex_last_update():
    data = await  fx_obj.get_data()


 
    if data:
        return {"status":"Success", "data":data["data"]}
    else:
        return data
    

@app.get('forex/lastupload')
async def get_last_upload():
    data = await  fx_obj.last_upload_date()

    print(data["data"])
    if data:
        return {"status":"Success", "data":data["data"]}
    else:
        return data

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Forex Data API"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}



