import datetime as dt
import jwt
import requests
from datetime import timezone

secret_key = "Qt2eSu9Rljopn7uv3m5ZlY74P5dZWTIYMMP7kJL4JYrKSeW6QgcoWlIXYy74IrTW"

def create_token():
    module_name = 'bot'
    now = dt.datetime.now(timezone.utc)
    payload = {
        "iss": module_name,
        "iat": now,
        "exp": now + dt.timedelta(minutes=60*2),
        "nbf": now,
        "jti": module_name,
        "sub": module_name
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

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
    api_url = "https://inventory.addstaging.com/api/v2/internal/vehicles/listing"
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
        if key in ['make', 'model', 'year', 'mileage', 'price']:
            api_filters.append([key, "=", value])
        elif key == 'vin':
            api_filters.append(["serial_number", "=", value])

    data = {
        "user_id": filters.get('dealer_id', 102262),  # Default dealer_id if not provided
        "status": "published",
        "filters": api_filters,
        "fields": ["year", "make", "model", "mileage", "price", "factory_color", "serial_number", "carfax_url"]
    }

    try:
        response = requests.get(api_url, json=data, headers=headers)
        response.raise_for_status()
        products = response.json().get("data", [])
        if not products:
            return {"message": "No products found matching the criteria."}
        return {"products": products}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch products. Error: {str(e)}"}

# Example usage
if __name__ == "__main__":
    make = "Audi"
    model = ""
    dealer_id = 102262
    result = get_products_info(make=make, model=model, dealer_id=dealer_id)
    print(result)