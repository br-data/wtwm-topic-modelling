import time
from typing import Dict, Optional

import jwt

from settings import JWT_ALGORITHM, JWT_SECRET, WTWM_API_USER, WTWM_API_PASS


def token_response(token: str) -> Dict[str, str]:
    """Format token repsonse.

    :param token: the token to return
    """
    return {"access_token": token}


def signJWT(
        payload: dict[str, str],
        valid_in_sec: int = 31556952
) -> Dict[str, str]:
    """Create a JWT token from a user_id.

    :param payload: token data
    :param valid_in_sec: token expiration time in seconds

    Note: Default expiration time is one year
    """
    payload.update({"expires": time.time() + valid_in_sec})
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decodeJWT(
        token: str,
        username: str = WTWM_API_USER,
        password: str = WTWM_API_PASS
) -> Optional[Dict[str, str]]:
    """Decode a JWT token.

    :param token: the token to decode
    :param username: api username
    :param password: api password
    """
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if all([
            decoded_token["expires"] >= time.time(),
            decoded_token["username"] == username,
            decoded_token["password"] == password]):
            return decoded_token

        return None

    except (TypeError, KeyError, ValueError):
        return None
