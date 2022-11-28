import time
import os
from typing import Dict, Optional

import jwt

JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
JWT_SECRET = os.environ["JWT_ALGORITHM"]


def token_response(token: str) -> Dict[str, str]:
    """Format token repsonse.

    :param token: the token to return
    """
    return {"access_token": token}


def signJWT(user_id: str, valid_in_sec: int = 31556952) -> Dict[str, str]:
    """Create a JWT token from a user_id.

    :param user_id: base token
    :param valid_in_sec: token expiration time in seconds

    Note: Default expiration time is one year
    """
    payload = {"user_id": user_id, "expires": time.time() + valid_in_sec}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decodeJWT(token: str) -> Optional[Dict[str, str]]:
    """Decode a JWT token.

    :param token: the token to decode
    """
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return None
