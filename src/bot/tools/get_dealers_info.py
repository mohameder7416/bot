import sys
sys.path.append('..')
import pandasql as ps
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os 
import json
from bot.utils.load_variables import load_variables
from bot.utils.db import DataBase
def get_dealers_info(sql_query: str):
    """
    Execute an SQL query on the dealers_df DataFrame, a table for dealers informations that offers buying services. 
    This table contains columns: (dealer_name, address, phone, credit_app_link, inventory_link, 
    offers_test_drive, welcome_message, shipping, trade_ins, opening_hours offer_finance)
    dealer_name: The name of the dealership. It is typically the brand or business name that customers associate with the dealership, such as "XYZ Motors."

address: The physical location of the dealership. This includes the street address, city, state, and zip code. It helps customers find the dealership.

phone: The contact number of the dealership, allowing customers to call for inquiries, appointments, or other services.

credit_app_link: A link to the dealership's online credit application form. This allows customers to apply for financing or credit pre-approval for vehicle purchases.

inventory_link: A link to the dealership's inventory page, where customers can view available vehicles, their specifications, prices, and other relevant details.

offers_test_drive: Indicates whether the dealership offers test drives for customers interested in trying out a vehicle before making a purchase.

welcome_message: A greeting or introductory message displayed on the dealership’s website or sent to customers when they interact with the dealership. It could be something like, "Welcome to XYZ Motors, where we find the perfect vehicle for you!"

shipping: Information regarding shipping options available for purchasing vehicles. This could include delivery to a customer’s home or specific areas, and details on shipping fees and timelines.

trade_ins: Describes whether the dealership accepts trade-in vehicles from customers. If so, it might include information on how the trade-in process works, such as valuation or appraisal details.

opening_hours: The hours during which the dealership is open to the public. This typically includes specific opening and closing times for each day of the week.

offer_finance: Indicates whether the dealership provides financing options for customers. It could include details about loan terms, interest rates, and how customers can apply for financing.
    Parameters:
        sql_query (str or dict): An SQL query string or a dictionary with key "sql_query".

        Example: 'SELECT dealer_name, address, phone FROM dealers_df'

    Returns:
        str: Query results as a string, or None if an error occurs.
    """
    load_dotenv()
    db = DataBase()
    
    if isinstance(sql_query, dict):
        sql_query = sql_query.get('sql_query', '')
    
    try:
        # Load dealer_id from JSON file
        variables = load_variables()
        dealer_id = variables["dealer_id"]
        conn = db.connexion()
        if conn is None:
            raise Exception("Failed to connect to the database")
        
        
        dealers_query = f"SELECT * FROM dealers_info WHERE dealer_id = %s"
        dealers_data = db.readQuery(conn, dealers_query, (dealer_id,))
        
        dealers_df = pd.DataFrame(dealers_data, columns=[
            'dealer_id', 'dealer_name', 'address', 'phone', 'credit_app_link', 'inventory_link',
            'offers_test_drive', 'welcome_message', 'shipping', 'trade_ins', 'opening_hours', 'offer_finance'
        ])
        
        result_df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return result_df.to_string(index=False)
        
        
        
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return None

