
import sys
sys.path.append('..')
from bot.utils.load_variables import load_variables
import os 
import datetime as dt
import jwt
import json
import requests
from dotenv import load_dotenv
load_dotenv()
secret_key = str(os.getenv("secret_key", ""))
print("secret_key",secret_key)
PWA_API_CRM=os.getenv("PWA_API_CRM")
print("PWA_API_CRM",PWA_API_CRM)

variables=load_variables()
lead_id_crm=variables["lead_crm_id"]
def create_token():
    module_name='bot'
    payload = {
        "iss": module_name,  # Issuer
        "iat": dt.datetime.utcnow(),  # Issued At
        "exp": dt.datetime.utcnow() + dt.timedelta(minutes=2),  # Expiration
        "nbf": dt.datetime.utcnow(),  # Not Before
        "jti": module_name,  # JWT ID
        "sub": module_name  # Subject
    }

    # Encode the JWT
    token = jwt.encode(payload, secret_key, algorithm="HS256")

    # Set up headers with the JWT token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    return headers






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

    
    
 