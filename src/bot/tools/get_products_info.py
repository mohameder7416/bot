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
load_dotenv()
secret_key = os.getenv("secret_key")


def get_stored_arguments():
    """Load all stored arguments from the single JSON file."""
    file_path = "lead_arguments.json"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}


def save_arguments(lead_id, new_arguments):
    """
    Save arguments for a specific lead ID to the single JSON file.
    Updates existing arguments instead of overwriting them.
    """
    file_path = "lead_arguments.json"
    
    # Load existing data
    all_arguments = get_stored_arguments()
    
    # Get existing arguments for this lead (or empty dict if none exist)
    existing_args = all_arguments.get(str(lead_id), {})
    
    # Update existing arguments with new ones
    existing_args.update(new_arguments)
    
    # Save updated arguments for this lead
    all_arguments[str(lead_id)] = existing_args
    
    # Save all arguments back to file
    with open(file_path, 'w') as f:
        json.dump(all_arguments, f, indent=2)


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
    dealer_id=variables["dealer_id"]
    if not lead_id:
        raise ValueError("lead_id not found in variables")

    # Load all arguments and get specific lead's arguments
    all_arguments = get_stored_arguments()
    filters = all_arguments.get(str(lead_id), {})  # Get stored filters for this lead
    
    # Update with new arguments if provided
    if args and isinstance(args[0], dict):
        filters.update(args[0])
    filters.update(kwargs)
    
    # Save updated arguments
    save_arguments(lead_id, filters)

    api_url = os.getenv("base_url_products_invontaire")
    token = create_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

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