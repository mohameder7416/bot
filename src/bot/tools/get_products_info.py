import sys
sys.path.append('..')
import datetime as dt
import requests
from datetime import timezone
import os
import json 
from dotenv import load_dotenv
from bot.utils.create_token import create_token
from bot.variables.variables import load_variables
import redis
load_dotenv()
secret_key = os.getenv("secret_key")
REDIS_HOST=os.getenv("REDIS_HOST")
REDIS_PORT=os.getenv("REDIS_PORT")
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=12, decode_responses=True)

def get_stored_arguments(lead_id):
        """Load stored arguments for a specific lead from Redis."""
        stored_args = redis_client.get(f"lead_arguments:{lead_id}")
        return json.loads(stored_args) if stored_args else {}


def save_arguments(lead_id, new_arguments):
    """
    Save arguments for a specific lead ID to Redis.
    Updates existing arguments instead of overwriting them.
    """
    existing_args = get_stored_arguments(lead_id)
    existing_args.update(new_arguments)
    redis_client.set(f"lead_arguments:{lead_id}", json.dumps(existing_args))
    key = f"lead_arguments:{lead_id}"
    print(f"Filters saved for lead {lead_id}: {existing_args}")
    
    return key  # Return the key used to store the filters
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
    product_id= variables["product_id"]
    if not lead_id:
        raise ValueError("lead_id not found in variables")

    # Load filters for this lead from Redis
    filters = get_stored_arguments(lead_id)
    
    # Update with new arguments if provided
    if args and isinstance(args[0], dict):
        filters.update(args[0])
    filters.update(kwargs)
    
    # Save updated arguments to Redis
    save_arguments(lead_id, filters)

    api_url = os.getenv("base_url_products_invontaire")
    headers = create_token()
    product_data = {
        "user_id": dealer_id,
        "product_id": product_id,
        "fields": ["make"]
    }

    try:
        product_response = requests.get(api_url, json=product_data, headers=headers)
        product_response.raise_for_status()
        product_details = product_response.json().get("data", [])
        
        if not product_details:
            return {"error": "Product not found"}
        
        product_make = product_details[0].get("make")
    except requests.RequestException as e:
        return {"error": f"Failed to fetch product details. Error: {str(e)}"}

    # Compare the make from the API with the make from the arguments
    if 'make' in filters and product_make != filters['make']:
        # If they don't match, don't include product_id in the main query
        product_id = None
    # Build API filters using ALL stored filters
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
    make_filter = filters.get('make')
    # Process ALL filters from storage
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
    if product_id:
        data["product_id"] = product_id

    print(f"Debug - API request data: {data}")

    try:
        response = requests.get(api_url, json=data, headers=headers)
        response.raise_for_status()
        products = response.json().get("data", [])
        print(f"Debug - API response: {products}")
        
        if not products:
            return {"message": "No products found matching the criteria."}
        return {"products": products}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch products. Error: {str(e)}"}