import time
from typing import Dict

import jwt


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def token_response(token: str):
    return {
        'access_token': token
    }


def signJWT(user_id: str) -> Dict[str, str]:
    payload = {
        'user_id': user_id,
        'expires': time.time() + 600
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithm=ALGORITHM)
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
