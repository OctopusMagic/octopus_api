import time

from loguru import logger
import requests

from app.config.cfg import AUTH_URL, AUTH_PASSWORD, NIT


token_storage = {
    "token": None,
    "expires_at": None
}


def obtain_new_token():
    """Obtain new token from Ministerio de Hacienda."""
    data = {
        "user": NIT,
        "pwd": AUTH_PASSWORD
    }
    payload = "&".join(f"{k}={v}" for k, v in data.items())

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozzila/5.0"
    }
    response = requests.post(AUTH_URL, data=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        token_storage["token"] = data["body"]["token"]
        token_storage["expires_at"] = time.time() + 24 * 3600
        return response.text
    else:
        logger.error("Error:", response.text)
        return None


def get_token():
    """Get token from storage or obtain new one if expired."""
    if token_storage["expires_at"] is None \
            or token_storage["expires_at"] < time.time():
        obtain_new_token()
    return token_storage["token"]
