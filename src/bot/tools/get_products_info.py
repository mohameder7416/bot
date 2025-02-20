import sys
sys.path.append('..')
import datetime as dt
import jwt
import requests
from datetime import timezone
import os
from dotenv import load_dotenv
from bot.utils.create_token import create_token
load_dotenv()
secret_key = os.getenv("secret_key")


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
    api_url = os.getenv("base_url_products_invontaire")
    token = create_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Handle both dictionary input and keyword arguments
    if args and isinstance(args[0], dict):
        filters = args[0]
    else:
        filters = kwargs

    api_filters = []
    for key, value in filters.items():
        if key == 'vin':
            api_filters.append(["serial_number", "=", value])
        elif key in ['year', 'make', 'model', 'mileage', 'price', 'condition', 'title']:
            api_filters.append([key, "=", value])
        elif key == 'isadded':
            api_filters.append(["is_added", "=", value])
        elif key == 'price_type':
            api_filters.append(["price_type", "=", value])

    data = {
        "user_id": filters.get('dealer_id', 102262),  # Default dealer_id if not provided
        "status": "published",
        "filters": api_filters,
        "fields": ["year", "make", "model", "mileage", "price", "factory_color", "serial_number", "carfax_url", "condition", "title", "is_added", "price_type"]
    }

    print(f"Debug - API request data: {data}")  # Debug print

    try:
        response = requests.get(api_url, json=data, headers=headers)
        response.raise_for_status()
        products = response.json().get("data", [])

        print(f"Debug - API response: {products}")  # Debug print

        if not products:
            return {"message": "No products found matching the criteria."}
        return {"products": products}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch products. Error: {str(e)}"}
