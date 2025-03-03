from bot.utils.load_variables import load_variables
from bot.utils.db import DataBase
DB_USER_READ="bot_v2_writer"
DB_PASSWORD_READ="SwnvBYkjpfoYTIz"
DB_HOST_READ="preproduction-db-1-instance-1.c7nkisio0atn.us-west-2.rds.amazonaws.com"
DB_PORT_READ=3306
DB_NAME_READ="bot_v2"
db = DataBase(host=DB_HOST_READ,user=DB_USER_READ,password=DB_PASSWORD_READ,database=DB_NAME_READ,port=DB_PORT_READ)
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



