import requests

def get_products_info(base_url="http://0.0.0.0:8000/products", **filters):
    """
   get products informations from the  with optional filters.
    
    Parameters:
       .base_url="http://0.0.0.0:8000/products"
        filters (dict): A JSON object containing optional query string parameters for filtering products, including:
            {
                "vin": vin,
                "year": year,
                "make": make,
                "model": model,
                "isadded": isadded,
                "mileage": mileage,
                "condition": condition,
                "title": title,
                "price": price,
                "price_type": price_type
            }
    
    Returns:
        list: A list of products matching the filters.
    """
    response = requests.get(base_url, params=filters)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch products. Status code: {response.status_code}"}

# Example usage:
filters = {
    "year": 2020,
    }
products = get_products_info(**filters)
print(products)
