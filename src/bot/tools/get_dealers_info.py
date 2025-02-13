import pandasql as ps
import pandas as pd
# Load the CSV file into a Pandas DataFrame
dealers_df = pd.read_csv("/home/mohamed/bot/data/dealers.csv")

def get_dealers_info(sql_query: str):
    """
    Execute an SQL query on the dealers_df DataFrame, a table for dealer information that offers buying services. 
    This table contains columns: (dealer_name, address, phone, credit_app_link, inventory_link, 
    offers_test_drive, welcome_message, shipping, trade_ins, opening_hours) 
    and returns the result as a string.

    Parameters:
        sql_query (str or dict): An SQL query string or a dictionary with key "sql_query".

        Example: 'SELECT dealer_name, address, phone FROM dealers_df'

    Returns:
        str: Query results as a string, or None if an error occurs.
    """
    dealers_df = pd.read_csv("/home/mohamed/bot/data/dealers.csv")
    env = {'dealers_df': dealers_df}

    if isinstance(sql_query, dict):
        sql_query = sql_query.get('sql_query', '')

    # Fetch the latest dealer_id
    latest_dealer_id = 1

    # Append the WHERE clause to filter by dealer_id if not already present
  

    try:
        result_df = ps.sqldf(sql_query, env)
        return result_df.to_string(index=False)
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return None



