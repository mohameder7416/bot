from datetime import datetime
from bot.utils.load_variables import load_variables
variables = load_variables()
lead_id = variables["lead_id"]


def load_chat_history(DB, lead_id=lead_id):
    """
    Retrieve the last 7 messages for a conversation associated with the given lead_id.
    
    Args:
        DB: An instance of the DataBase class
        lead_id: The ID of the lead to get messages for
        
    Returns:
        A formatted string containing the last messages
    """
    conv_id_query = "SELECT id FROM `conversations` WHERE lead_id = %s"
    messages_query = "SELECT content, is_bot, is_bdc FROM `messages` WHERE conversation_id = %s ORDER BY id DESC LIMIT 7"
    
    conn = DB.connexion()
    if not conn:
        return ""
    
    try:
        conv_res = DB.readQuery(conn, conv_id_query, lead_id)
        if not conv_res:
            return ""
        
        con_id = conv_res[0][0]
        
        msg_res = DB.readQuery(conn, messages_query, con_id)
        
        messages = msg_res[::-1]
        
        last_mesg = ""
        for msg in messages:
            if msg[1] is not None or msg[2] is not None:
                last_mesg += "Bot:" + str(msg[0]) + "\n"
            else:
                last_mesg += "client:" + str(msg[0]) + "\n"
        
        return last_mesg
    except Exception as e:
        print(f"Error in last_messages: {str(e)}")
        return ""
    finally:
        if conn:
            conn.close()



