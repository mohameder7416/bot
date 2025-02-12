import pandasql as ps
import pandas as pd

# Load the CSV file into a Pandas DataFrame
dealers_df = pd.read_csv("/home/mohamed/bot/data/dealers.csv")


def get_dealers_info(sql_query: str):
    """
    Execute an SQL query on the dealers_df DataFrame , table for dealers information that offer buying service  that contains (dealer_name, address, phone, credit_app_link, 
    inventory_link, offers_test_drive, welcome_message, shipping, trade_ins, opening_hours) columns info
    and return the result as a string.

    Parameters:
        sql_query (str or dict): An SQL query string or a dictionary with key "sql_query"

        example  : 'SELECT dealer_name, address, phone from dealers_df'
       
    Returns:
        str: Query results as a string
    """
    dealers_df = pd.read_csv("/home/mohamed/bot/data/dealers.csv")
    env = {'dealers_df': dealers_df }
    # Create a dictionary with the DataFrame explicitly named
    if isinstance(sql_query, dict):
        sql_query = sql_query.get('sql_query', '')
        
    
    try:
        result_df = ps.sqldf(sql_query, env)
        return result_df.to_string(index=False)
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return None



query = "SELECT dealer_name, address, phone FROM dealers_df"
# Now you can call it without specifying the DataFrame
result = get_dealers_info(query)
print(result)