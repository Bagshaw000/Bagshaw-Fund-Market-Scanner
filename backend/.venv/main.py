from typing import Union
from src.db.db import test_db_connection
from src.forex.data import Forex
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession



app = FastAPI()
fx_obj = Forex()

@app.on_event("startup")
async def startup_event():
    """
    Function that runs when the server starts up.
    Tests the database connection and logs the result.
    """
    print("🚀 Starting up server...")
    try:
        result = await test_db_connection()
        if result["status"] == "success":
            print("✅ Database connection test successful!")
        else:
            print(f"❌ Database connection test failed: {result['message']}")
    except Exception as e:
        print(f"❌ Error testing database connection: {str(e)}")




# test = Forex()
# print( test.get_last_uploaded_date())

# print(db_test_result)  # Print the result of the database connection test

@app.get("/")
def read_root():
    
    return {"Hello": "World"}

@app.get('/forex/last_update')
async def get_forex_last_update():
    data = await fx_obj.get_last_uploaded_date()
    print(data)
    if data:
        return {"status":"Success", "data":data}
    else:
        return data
    
    

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Forex Data API"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

