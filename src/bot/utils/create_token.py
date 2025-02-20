import os
from dotenv import load_dotenv
load_dotenv()
secret_key = os.getenv("secret_key")
import jwt
import datetime as dt
from datetime import timezone


def create_token():
    module_name = 'bot'
    now = dt.datetime.now(timezone.utc)
    payload = {
        "iss": module_name,
        "iat": now,
        "exp": now + dt.timedelta(minutes=60*2),
        "nbf": now,
        "jti": module_name,
        "sub": module_name
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token
