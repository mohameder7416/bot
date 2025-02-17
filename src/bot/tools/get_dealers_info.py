import sys
sys.path.append('..')
import pandasql as ps
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os 
import json
from utils.load_variables import load_variables

def get_dealers_info(sql_query: str):
    """
    Execute an SQL query on the dealers_df DataFrame, a table for dealers informations that offers buying services. 
    This table contains columns: (dealer_name, address, phone, credit_app_link, inventory_link, 
    offers_test_drive, welcome_message, shipping, trade_ins, opening_hours offer_finance

    Parameters:
        sql_query (str or dict): An SQL query string or a dictionary with key "sql_query".

        Example: 'SELECT dealer_name, address, phone FROM dealers_df'

    Returns:
        str: Query results as a string, or None if an error occurs.
    """
    load_dotenv()
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    if isinstance(sql_query, dict):
        sql_query = sql_query.get('sql_query', '')
    
    try:
        # Load dealer_id from JSON file
        variables = load_variables()
        dealer_id = variables["dealer_id"]
        
        dealers_df = pd.read_sql_query(f"SELECT * FROM dealers_info WHERE dealer_id = {dealer_id}", engine)
        
        env = {'dealers_df': dealers_df}
        result_df = ps.sqldf(sql_query, env)
        return result_df.to_string(index=False)
        
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return None

