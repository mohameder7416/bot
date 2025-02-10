import pandasql as ps
import pandas as pd

# Load the CSV file into a Pandas DataFrame
dealers = pd.read_csv("/home/mohamed/bot/data/dealers.csv")


def get_dealers_info(sql_query: str):
    """
    Execute an SQL query on the dealers_df DataFrame that contains (dealer_name, address, phone, credit_app_link, 
    inventory_link, offers_test_drive, welcome_message, shipping, trade_ins, opening_hours) columns info
    and return the result as a string.

    Parameters:
        sql_query (str): SQL query to execute on the DataFrame dealers
       
        dealers_id for api that consume delaers_id
        delaers_name for api that consume delaers_id
    Returns:
        str: Query results as a string
    """
    dealers = pd.read_csv("/home/mohamed/bot/data/dealers.csv")
    # Create a dictionary with the DataFrame explicitly named
    env = {'dealers': dealers }
    
    try:
        # Execute the query and get the DataFrame result
        result_df = ps.sqldf(sql_query, env)
        
        # Return the result as a string (convert DataFrame to string)
        return result_df.to_string(index=False)
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return None


query = "SELECT * FROM dealers WHERE dealer_name = 'ABC Motors'"
# Now you can call it without specifying the DataFrame
result = get_dealers_info(query)
print(result)