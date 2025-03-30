import logging
from polygon import RESTClient
from dotenv import dotenv_values

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = dotenv_values(".env")

def connect_Polygon():
    """
    Establishes a connection to the Polygon API using the provided API key.

    :return: An instance of RESTClient if the connection is successful, None otherwise.
    """
    try:
        asset_key = config["ASSET_API_KEY"]
        client = RESTClient(api_key=asset_key, trace=True)
        logger.info("Successfully connected to the Polygon API.")
        return client
    except KeyError as e:
        logger.error(f"Missing configuration key: {e}")
    except Exception as e:
        logger.error(f"Cannot connect to the Polygon API: {e}")
    
    return None  # Return None if the connection fails

def get_Data( pair: str, start_date: str, end_date: str, period:str, adjusted:bool, sort:str, limit:int  ):
    """
    Fetches  data for a given forex pair between specified dates.
    
    :param pair: The forex pair to fetch data for (e.g., "EURUSD").
    :param start_date: The start date for the data in 'YYYY-MM-DD' format.
    :param end_date: The end date for the data in 'YYYY-MM-DD' format.
    :return: The response from the API.
    """
    try:
        # Assuming self.conn_Poly has a method called 'get_monthly_data'
        client = connect_Polygon()
        
        if client is None:
            logger.error("Failed to connect to the Polygon API.")
        else:
            response = client.list_aggs(ticker=pair, timespan=period, from_=start_date, to= end_date, limit = 50000)
            return response  # Return the API response
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return {"status": "error", "message": str(e)}

