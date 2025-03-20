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

    Parameters:
        sql_query (str or dict): An SQL query string or a dictionary with key "sql_query".

        Example: 'SELECT dealer_name, address, phone FROM dealers_df'

    Returns:
        str: Query results as a string, or None if an error occurs.
    """
    load_dotenv()
   
    DB_USER_READ = os.getenv("DB_USER_READ")
    DB_PASSWORD_READ = os.getenv("DB_PASSWORD_READ")
    DB_HOST_READ = os.getenv("DB_HOST_READ")
    DB_PORT_READ = os.getenv("DB_PORT_READ")
    DB_NAME_READ = os.getenv("DB_NAME_READ")
    engine = create_engine(f"mysql+pymysql://{DB_USER_READ}:{DB_PASSWORD_READ}@{DB_HOST_READ}:{DB_PORT_READ}/{DB_NAME_READ}")
    
    if isinstance(sql_query, dict):
        sql_query = sql_query.get('sql_query', '')
    
    try:
        # Load dealer_id from JSON file
        variables = load_variables()
        dealer_id = variables["dealer_id"]
        dealers_df = pd.read_sql_query(f"SELECT * FROM dealers_info WHERE dealer_id = {dealer_id}", engine)
        env = {'dealers_df': dealers_df}
        result_df = ps.sqldf(sql_query, env)
        print("result_df",result_df)
        
        return result_df.to_string(index=False)
        
        
        
    except Exception as e:
        error_message = f"Error executing query: {str(e)}"
        return None

