import asyncio
from prisma import Prisma
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Prisma()


async def test_db_conn():
    try:
        # Connect to the database
        await db.connect()

        # Execute a simple query to verify the connection
        result = await db.query_raw("SELECT 1")
        if result == [{"?column?": 1}]:  # PostgreSQL returns this format
            return {"status": 200}
        else:
            return {"status": "error", "message": "Unexpected query result"}
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        # Disconnect from the database
        await db.disconnect()
   