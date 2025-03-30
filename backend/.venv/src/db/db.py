import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import dotenv_values
from contextlib import asynccontextmanager


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
config = dotenv_values(".env")

def get_database_url() -> str:
    """
    Retrieve and validate the database URL from environment variables.

    :return: Database URL as a string.
    :raises ValueError: If DATABASE_URL is not set or is invalid.
    """
    database_url = config["DATABASE_URL"]
  
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set.")
        raise ValueError("DATABASE_URL environment variable is not set.")
    return database_url


def create_async_db_engine(database_url: str):
    """
    Create an asynchronous SQLAlchemy engine.

    :param database_url: The database connection URL.
    :return: An async SQLAlchemy engine.
    """
    return create_async_engine(
        database_url,
        pool_size=10,  # Adjust pool size based on your application's needs
        max_overflow=5,  # Allow some overflow connections
        echo=False,  # Set to True to log all SQL statements (useful for debugging)
        future=True,  # Enable SQLAlchemy 2.0 behavior
    )


# Create async engine
engine = create_async_db_engine(get_database_url())

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_db_session():
    """
    Async context manager for database sessions.
    Usage: async with get_db_session() as session:
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def test_db_connection() -> dict:
    """
    Test the database connection asynchronously.

    :return: A dictionary containing the status and result of the test.
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            await session.commit()
            return {"status": "success", "result": [row[0] for row in result]}
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return {"status": "error", "message": str(e)}


# Example usage
async def main():
    # Test database connection
    connection_test_result = await test_db_connection()
    logger.info(f"Database connection test result: {connection_test_result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())