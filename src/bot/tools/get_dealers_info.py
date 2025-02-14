import sys
sys.path.append('..')
import pandasql as ps
import pandas as pd
from dotenv import load_dotenv
from bot.variables.variables import dealer_id
from sqlalchemy import create_engine
import os 
# Load the CSV file into a Pandas DataFrame

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
    if isinstance(sql_query,dict):
            sql_query=sql_query.get('sql_query','')
    try :
        dealers_df=pd.read_sql_query(f"SELECT * FROM dealers_info WHERE dealer_id = {dealer_id}", engine)
     
        
        env = {'dealers_df': dealers_df}
        result_df=ps.sqldf(sql_query,env)
        return result_df.to_string(index=False)
        
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return None    
    
def main():
    """
    Main function to test the get_dealers_info function.
    """
    # Load environment variables
    load_dotenv()
    
    # Define a sample SQL query
    sample_query = "SELECT dealer_name, address, phone FROM dealers_df "

    # Test the function
    print("Testing get_dealers_info function...\n")
    try:
        # Call the function
        result = get_dealers_info(sample_query)
        
        # Check and print the result
        if result:
            print("Query executed successfully. Results:\n")
            print(result)
        else:
            print("No results returned or an error occurred.")
    except Exception as e:
        print(f"An exception occurred while testing: {str(e)}")

if __name__ == "__main__":
    main()    
    
    
    
    
    




