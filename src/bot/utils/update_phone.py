from bot.utils.create_token import create_token
from dotenv import load_dotenv
import requests
load_dotenv()
import os 
from bot.utils.load_variables import load_variables
variables=load_variables()
lead_id=variables["lead_id"]
dealer_id=variables["dealer_id"]
crm_new_lead_id=variables["lead_crm_id"]
PWA_CRM_API_URL=os.getenv("PWA_CRM_API_URL")
PWA_DB_HOST_V12CHAT_WRITE=os.getenv("PWA_DB_HOST_V12CHAT_WRITE=")
PWA_DB_USERNAME_V12CHAT_WRITE=os.getenv("PWA_DB_USERNAME_V12CHAT_WRITE")
PWA_DB_PASSWORD_V12CHAT_WRITE=os.getenv("PWA_DB_PASSWORD_V12CHAT_WRITE")
PWA_DB_DATABASE_V12CHAT_WRITE=os.getenv("PWA_DB_DATABASE_V12CHAT_WRITE")

def update_CRM_phone(dealer_id, lead_crm_id, phone):

    phone_url = f"{PWA_CRM_API_URL}/lead/{lead_crm_id}?user_id={dealer_id}&new_phone={phone}"

    #lead_id for logging 
    headers=create_token()
    r = requests.put(phone_url, headers=headers)
    return r.status_code


def update_Chat_Phone(message, lead_id,DB):
    query = "Update leads SET phone_number= %s WHERE id = %s"
    data = (message, lead_id)
    conn_DBC = DB.connexion(
        PWA_DB_HOST_V12CHAT_WRITE,
        PWA_DB_USERNAME_V12CHAT_WRITE,
        PWA_DB_PASSWORD_V12CHAT_WRITE,
        PWA_DB_DATABASE_V12CHAT_WRITE,
    )
    res_update = DB.updateQuery(conn_DBC, query, data)