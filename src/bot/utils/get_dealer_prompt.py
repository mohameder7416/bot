from utils.load_variables import load_variables
from utils.db import DataBase
db = DataBase()
conn=db.connexion()
def get_dealer_prompt():
    variables = load_variables()
    dealer_id = variables["dealer_id"]
    welcome_message = db.readQuery(conn=conn, query=f"SELECT welcome_message FROM dealers_info WHERE dealer_id = {dealer_id}")
    bot_behavior = db.readQuery(conn=conn, query=f"SELECT bot_behavior FROM dealers_info WHERE dealer_id = {dealer_id}")
    dealer_prompt = f"""
    Start the conversation with {welcome_message[0][0]}, and be {bot_behavior[0][0]}
    """
    
    return dealer_prompt



