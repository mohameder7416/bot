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
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Initialize Redis client
redis_kwargs = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "decode_responses": True
}

if REDIS_PASSWORD:
    redis_kwargs["password"] = REDIS_PASSWORD

try:
    redis_client = redis.Redis(**redis_kwargs)
    redis_client.ping()
    print("Successfully connected to Redis")
except Exception as e:
    print(f"Redis connection error: {e}")
    class DummyRedis:
        def __init__(self):
            self.storage = {}

        def hset(self, name, key, value):
            if name not in self.storage:
                self.storage[name] = {}
            self.storage[name][key] = value

        def hgetall(self, name):
            return self.storage.get(name, {})

        def exists(self, name):
            return name in self.storage

        def expire(self, name, time):
            return True

    redis_client = DummyRedis()
    print("Using in-memory storage instead of Redis")

# Function to save lead arguments in Redis hash
def save_arguments(lead_id, new_arguments):
    try:
        key = f"lead_arguments:{lead_id}"
        for arg_key, arg_value in new_arguments.items():
            redis_client.hset(key, arg_key, json.dumps(arg_value))
        redis_client.expire(key, timedelta(weeks=1).total_seconds())
        print(f"Updated filters for lead {lead_id} in Redis hash")
        return key
    except Exception as e:
        print(f"Error saving arguments to Redis hash: {e}")
        return None

# Function to get stored lead arguments from Redis
def get_stored_arguments(lead_id=None):
    try:
        if lead_id:
            key = f"lead_arguments:{lead_id}"
            if redis_client.exists(key):
                stored_args = redis_client.hgetall(key)
                return {k: json.loads(v) for k, v in stored_args.items()}
            return {}
        else:
            all_arguments = {}
            for key in redis_client.scan_iter("lead_arguments:*"):
                lead_id = key.split(":")[-1]
                stored_args = redis_client.hgetall(key)
                all_arguments[lead_id] = {k: json.loads(v) for k, v in stored_args.items()}
            return all_arguments
    except Exception as e:
        print(f"Error retrieving arguments from Redis hash: {e}")
        return {}

# Function to save product information in Redis hash
def save_products_info(lead_id, products):
    try:
        key = f"products_info:{lead_id}"
        for index, product in enumerate(products):
            redis_client.hset(key, str(index), json.dumps(product))
        redis_client.expire(key, timedelta(weeks=1).total_seconds())
        print(f"Saved products info for lead {lead_id} in Redis hash")
    except Exception as e:
        print(f"Error saving products info to Redis hash: {e}")

# Function to retrieve product information from Redis
def get_products_info_from_redis(lead_id):
    try:
        key = f"products_info:{lead_id}"
        if redis_client.exists(key):
            stored_products = redis_client.hgetall(key)
            return [json.loads(v) for v in stored_products.values()]
        return {"message": "No products found for this lead."}
    except Exception as e:
        print(f"Error retrieving products from Redis hash: {e}")
        return {"error": "Failed to retrieve products from Redis."}

# Function to fetch products from API with Redis caching
def get_products_info(*args, **kwargs):
    variables = load_variables()
    lead_id = variables.get("lead_id")
    dealer_id = variables.get("dealer_id")
    
    if not lead_id:
        raise ValueError("lead_id not found in variables")

    filters = get_stored_arguments(lead_id)
    
    if args and isinstance(args[0], dict):
        filters.update(args[0])
    filters.update(kwargs)
    
    save_arguments(lead_id, filters)

    api_url = os.getenv("base_url_products_invontaire")
    headers = create_token()

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
        
        result = {"products": products} if products else {"message": "No products found matching the criteria."}
        
        save_products_info(lead_id, products)

        return result
    except requests.RequestException as e:
        error_result = {"error": f"Failed to fetch products. Error: {str(e)}"}
        save_products_info(lead_id, [])
        return error_result
