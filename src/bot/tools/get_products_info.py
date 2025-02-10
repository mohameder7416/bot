import pandasql as ps
import pandas as pd


products_df= pd.read_csv("/home/mohamed/bot/data/products.csv")

def get_products_info(sql_query:str, df:pd.DataFrame = products_df):
    
    
    env={'products_df':df}
    try :
        return ps.sqldf(sql_query,env)
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return None
    
    
