import jwt  # PyJWT library for handling JSON Web Tokens
import datetime as dt  # To work with date and time
import os
import json
import requests

secret_key=os.getenv("secret_key")
PWA_API_CRM=os.getenv("PWA_API_CRM")


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


def appointment_url(lead_id):
    url = f"{PWA_API_CRM}/appointment/link"
    payload = json.dumps({
    "lead_id": int(lead_id),
    "source": "AI Bot"
    })

    # headers = {
    #     "Authorization": f"Bearer {BToken}",
    #     "Content-Type": "application/json",
    # }
    headers=create_token()
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()['result']


