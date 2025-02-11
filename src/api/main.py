from fastapi import FastAPI, Query
import pandas as pd
from typing import Optional

app = FastAPI()

# Load CSV data into a Pandas DataFrame
df = pd.read_csv("/home/mohamed/bot/data/products.csv")

@app.get("/products")
def get_products(
    vin: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    make: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    isadded: Optional[bool] = Query(None),
    mileage: Optional[int] = Query(None),
    condition: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    price: Optional[float] = Query(None),
    price_type: Optional[str] = Query(None),
):
    # Start with full DataFrame
    filtered_df = df.copy()
    
    # Apply filters dynamically
    filters = {
        "vin": vin,
        "year": year,
        "make": make,
        "model": model,
        "isadded": isadded,
        "mileage": mileage,
        "condition": condition,
        "title": title,
        "price": price,
        "price_type": price_type,
    }
    
    for key, value in filters.items():
        if value is not None:
            filtered_df = filtered_df[filtered_df[key] == value]
    
    return filtered_df.to_dict(orient="records")
