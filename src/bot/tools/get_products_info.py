import requests
import os
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
    base_url_products = os.getenv("base_url_products")
    
    # Handle both dictionary input and keyword arguments
    if args and isinstance(args[0], dict):
        filters = args[0]
    else:
        filters = kwargs
    
    # Convert year to integer if it's a string
    if 'year' in filters and isinstance(filters['year'], str):
        try:
            filters['year'] = int(filters['year'])
        except ValueError:
            return {"error": "Invalid year provided"}
    
    try:
        response = requests.get(base_url_products, params=filters)
        response.raise_for_status()  # Raise an exception for bad status codes
        products = response.json()
        if not products:
            return {"message": "No products found matching the criteria."}
        return {"products": products}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch products. Error: {str(e)}"}

