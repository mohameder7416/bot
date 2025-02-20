
import sys
sys.path.append('..')
from bot.utils.load_variables import load_variables
import os 
import datetime as dt
import jwt
import json
import requests
from dotenv import load_dotenv
from bot.utils.create_token import create_token
load_dotenv()

PWA_API_CRM=os.getenv("PWA_API_CRM")
print("PWA_API_CRM",PWA_API_CRM)

variables=load_variables()
lead_id_crm=variables["lead_crm_id"]







def make_appointment():
    """
   Generate a link to make an appointment between the customer and the dealer. 
   The link  contain available time slots when the dealer is available
    
    
    Returns:
        string: A link to book the appointement.
    
    
    """
    url = f"{PWA_API_CRM}/appointment/link"
    payload = json.dumps({
    "lead_id": int(lead_id_crm),
    "source": "AI Bot"
    })

    # headers = {
    #     "Authorization": f"Bearer {BToken}",
    #     "Content-Type": "application/json",
    # }
    headers=create_token()
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()['result']

    
    
if __name__=="__main__":
    make_appointment()     