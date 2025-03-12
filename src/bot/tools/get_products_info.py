import sys
sys.path.append('..')
import datetime as dt
import requests
from datetime import timezone, timedelta
import os
import json 
import redis
from dotenv import load_dotenv
from bot.utils.create_token import create_token
from bot.variables.variables import load_variables

# Load environment variables
load_dotenv()
secret_key = os.getenv("secret_key")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))  # Convert to integer with default
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Initialize Redis client with proper configuration
# Only include password if it's actually set
redis_kwargs = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "decode_responses": True  # Automatically decode responses to strings
}

# Only add password if it's actually set and not empty
if REDIS_PASSWORD:
    redis_kwargs["password"] = REDIS_PASSWORD

try:
    # Print connection details for debugging (without password)
    debug_info = redis_kwargs.copy()
    if "password" in debug_info:
        debug_info["password"] = "***" if debug_info["password"] else "None"
    print(f"Connecting to Redis with: {debug_info}")
    
    redis_client = redis.Redis(**redis_kwargs)
    
    # Test the connection
    redis_client.ping()
    print("Successfully connected to Redis")
except redis.exceptions.AuthenticationError as e:
    print(f"Redis authentication error: {e}")
    print("Check if REDIS_PASSWORD is correctly set in your environment variables")
    # Fallback to non-authenticated connection if that's what your Redis server expects
    try:
        redis_kwargs.pop("password", None)
        redis_client = redis.Redis(**redis_kwargs)
        redis_client.ping()
        print("Successfully connected to Redis without authentication")
    except Exception as e:
        print(f"Failed to connect to Redis without authentication: {e}")
        # Create a dummy Redis client that uses in-memory storage as fallback
        class DummyRedis:
            def __init__(self):
                self.storage = {}
                print("Using in-memory storage instead of Redis")
            
            def get(self, key):
                return self.storage.get(key)
            
            def set(self, key, value, **kwargs):
                self.storage[key] = value
                return True
            
            def delete(self, key):
                if key in self.storage:
                    del self.storage[key]
                return True
            
            def expire(self, key, time):
                return True
            
            def scan_iter(self, match):
                return [k for k in self.storage.keys() if k.startswith(match.replace("*", ""))]
            
            def ping(self):
                return True
        
        redis_client = DummyRedis()
except Exception as e:
    print(f"Redis connection error: {e}")
    print("Check your Redis connection settings")
    # Create a dummy Redis client that uses in-memory storage as fallback
    class DummyRedis:
        def __init__(self):
            self.storage = {}
            print("Using in-memory storage instead of Redis")
        
        def get(self, key):
            return self.storage.get(key)
        
        def set(self, key, value, **kwargs):
            self.storage[key] = value
            return True
        
        def delete(self, key):
            if key in self.storage:
                del self.storage[key]
            return True
        
        def expire(self, key, time):
            return True
        
        def scan_iter(self, match):
            return [k for k in self.storage.keys() if k.startswith(match.replace("*", ""))]
        
        def ping(self):
            return True
    
    redis_client = DummyRedis()

def get_stored_arguments(lead_id=None):
    """
    Load stored arguments from Redis.
    If lead_id is provided, returns arguments for that lead only.
    Otherwise, returns all arguments for all leads.
    """
    try:
        if lead_id:
            # Get arguments for specific lead
            stored_args = redis_client.get(f"lead_arguments:{lead_id}")
            try:
                return json.loads(stored_args) if stored_args else {}
            except (TypeError, json.JSONDecodeError):
                print(f"Error decoding stored arguments for lead {lead_id}")
                return {}
        else:
            # Get arguments for all leads
            all_arguments = {}
            for key in redis_client.scan_iter("lead_arguments:*"):
                lead_id = key.split(":")[-1]
                stored_args = redis_client.get(key)
                try:
                    if stored_args:
                        all_arguments[lead_id] = json.loads(stored_args)
                except (TypeError, json.JSONDecodeError):
                    print(f"Error decoding stored arguments for lead {lead_id}")
            return all_arguments
    except Exception as e:
        print(f"Error retrieving from Redis: {e}")
        return {} if lead_id else {}

def save_arguments(lead_id, new_arguments):
    """
    Save arguments for a specific lead ID to Redis.
    Updates existing arguments instead of overwriting them.
    """
    try:
        # Get existing arguments for this lead
        existing_args = get_stored_arguments(lead_id)
        
        # Update existing arguments with new ones
        existing_args.update(new_arguments)
        
        # Save updated arguments for this lead
        key = f"lead_arguments:{lead_id}"
        redis_client.set(key, json.dumps(existing_args))
        
        # Set expiration for 1 week
        redis_client.expire(key, timedelta(weeks=1).total_seconds())
        
        print(f"Updated filters for lead {lead_id}: {existing_args}, expires in 1 week")
        return key
    except Exception as e:
        print(f"Error saving to Redis: {e}")
        return None

def get_products_info(*args, **kwargs):
    """
    Get products information from the API with optional filters.

    Parameters:
        args: A single dictionary of filters (optional)
        kwargs: Keyword arguments for filters

    Filters can include:
        vin (str): Vehicle Identification Number
        year (int): Year of manufacture
        make (str): Make of the vehicle
        model (str): Model of the vehicle
        isadded (bool): Whether the product is added
        mileage (int): Mileage of the vehicle
        condition (str): Condition of the vehicle
        title (str): Title of the product
        price (float): Price of the product
        price_type (str): Type of price

    Returns:
        dict: A dictionary containing either a list of products or an error message.
    """
    variables = load_variables()
    lead_id = variables["lead_id"]
    dealer_id = variables["dealer_id"]
    
    if not lead_id:
        raise ValueError("lead_id not found in variables")

    # Load stored filters from Redis for this lead
    filters = get_stored_arguments(lead_id)
    
    # Update with new arguments if provided
    if args and isinstance(args[0], dict):
        filters.update(args[0])
    filters.update(kwargs)
    
    # Save updated arguments to Redis
    save_arguments(lead_id, filters)

    api_url = os.getenv("base_url_products_invontaire")
    headers = create_token()

    # Build API filters using stored filters
    api_filters = []
    filter_mapping = {
        'vin': ['serial_number', '='],
        'year': ['year', '='],
        'make': ['make', '='],
        'model': ['model', '='],
        'mileage': ['mileage', '='],
        'price': ['price', '='],
        'condition': ['condition', '='],
        'title': ['title', '='],
        'isadded': ['is_added', '='],
        'price_type': ['price_type', '=']
    }

    # Debug print to see what filters we're working with
    print(f"Debug - Current filters: {filters}")

    # Process filters
    for key, value in filters.items():
        if key in filter_mapping:
            field, operator = filter_mapping[key]
            api_filters.append([field, operator, value])

    data = {
        "user_id": dealer_id,
        "status": "published",
        "filters": api_filters,
        "fields": [
            "year", "make", "model", "mileage", "price", 
            "factory_color", "serial_number", "carfax_url", 
            "condition", "title", "is_added", "price_type"
        ]
    }

    print(f"Debug - API request data: {data}")

    try:
        response = requests.get(api_url, json=data, headers=headers)
        response.raise_for_status()
        products = response.json().get("data", [])
        print(f"Debug - API response: {products}")
        
        # Save the result to Redis with lead_id as key
        result = {"products": products} if products else {"message": "No products found matching the criteria."}
        try:
            redis_client.set(f"products_info:{lead_id}", json.dumps(result))
            redis_client.expire(f"products_info:{lead_id}", timedelta(weeks=1).total_seconds())
        except Exception as e:
            print(f"Error saving products info to Redis: {e}")
        
        return result
    except requests.RequestException as e:
        error_result = {"error": f"Failed to fetch products. Error: {str(e)}"}
        try:
            redis_client.set(f"products_info:{lead_id}", json.dumps(error_result))
            redis_client.expire(f"products_info:{lead_id}", timedelta(weeks=1).total_seconds())
        except Exception as redis_e:
            print(f"Error saving error info to Redis: {redis_e}")
        return error_result