import sys
import hashlib
import datetime as dt
import requests
import os
import json
import redis
from datetime import timezone, timedelta
from dotenv import load_dotenv
from bot.utils.create_token import create_token
from bot.variables.variables import load_variables

sys.path.append('..')

# Load environment variables
load_dotenv()
secret_key = os.getenv("secret_key")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

# Initialize Redis client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=12, decode_responses=True)

async def delete(lead_id, redis_client):
    """Delete a specific lead call record from Redis."""
    await redis_client.delete(f"lead_arguments:{lead_id}")
    return True

async def delete_cache(redis_client):
    """Delete all lead call records from Redis."""
    async for key in redis_client.scan_iter("lead_arguments:*"):
        await redis_client.delete(key)
    return "Success"

async def update_cache(lead_id, new_arguments, redis_client):
    """Update stored lead arguments in Redis and set expiration time."""
    existing_args = await get_stored_arguments(lead_id, redis_client)
    existing_args.update(new_arguments)
    key = f"lead_arguments:{lead_id}"
    await redis_client.set(key, json.dumps(existing_args))
    await redis_client.expire(key, timedelta(weeks=1).total_seconds())  # Set expiration for 1 week
    print(f"Updated filters for lead {lead_id}: {existing_args}, expires in 1 week")
    return key

async def get_stored_arguments(lead_id, redis_client):
    """Retrieve stored lead arguments from Redis."""
    stored_args = await redis_client.get(f"lead_arguments:{lead_id}")
    return json.loads(stored_args) if stored_args else {}

def get_products_info(*args, **kwargs):
    """Retrieve product information from an external API with optional filters."""
    variables = load_variables()
    lead_id = variables["lead_id"]
    dealer_id = variables["dealer_id"]
    product_id = variables["product_id"]
    
    if not lead_id:
        raise ValueError("lead_id not found in variables")
    
    # Load stored filters from Redis
    filters = get_stored_arguments(lead_id, redis_client)
    
    if args and isinstance(args[0], dict):
        filters.update(args[0])
    filters.update(kwargs)
    
    # Save updated arguments to Redis and set expiration
    update_cache(lead_id, filters, redis_client)
    
    api_url = os.getenv("base_url_products_invontaire")
    headers = create_token()
    product_data = {"user_id": dealer_id, "product_id": product_id, "fields": ["make"]}
    
    try:
        product_response = requests.get(api_url, json=product_data, headers=headers)
        product_response.raise_for_status()
        product_details = product_response.json().get("data", [])
        
        if not product_details:
            return {"error": "Product not found"}
        
        product_make = product_details[0].get("make")
    except requests.RequestException as e:
        return {"error": f"Failed to fetch product details. Error: {str(e)}"}
    
    if 'make' in filters and product_make != filters['make']:
        product_id = None
    
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
    
    api_filters = [[field, operator, filters[key]] for key, (field, operator) in filter_mapping.items() if key in filters]
    
    data = {
        "user_id": dealer_id,
        "status": "published",
        "filters": api_filters,
        "fields": ["year", "make", "model", "mileage", "price", "factory_color", "serial_number", "carfax_url", "condition", "title", "is_added", "price_type"]
    }
    if product_id:
        data["product_id"] = product_id
    
    try:
        response = requests.get(api_url, json=data, headers=headers)
        response.raise_for_status()
        products = response.json().get("data", [])
        
        if not products:
            return {"message": "No products found matching the criteria."}
        return {"products": products}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch products. Error: {str(e)}"}
