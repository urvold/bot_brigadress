import hmac
import hashlib
import urllib.parse
import json
from typing import Optional
from .config import settings

class TelegramAuthError(Exception):
    pass

def _parse_init_data(init_data: str) -> dict:
    # init_data is querystring-like: key=value&key2=value2...
    parsed = urllib.parse.parse_qs(init_data, strict_parsing=True)
    data = {k: v[0] for k, v in parsed.items()}
    return data

def verify_init_data(init_data: str) -> dict:
    try:
        data = _parse_init_data(init_data)
    except Exception as e:
        raise TelegramAuthError("Bad initData format") from e

    if "hash" not in data:
        raise TelegramAuthError("No hash in initData")

    received_hash = data.pop("hash")
    # build data_check_string
    pairs = [f"{k}={data[k]}" for k in sorted(data.keys())]
    data_check_string = "\n".join(pairs)

    secret_key = hashlib.sha256(settings.bot_token.encode("utf-8")).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise TelegramAuthError("Invalid initData hash")

    if "user" in data:
        try:
            data["user"] = json.loads(data["user"])
        except Exception:
            pass

    return data

def get_user_from_init_data(init_data: str) -> Optional[dict]:
    data = verify_init_data(init_data)
    user = data.get("user")
    if isinstance(user, dict) and "id" in user:
        return user
    return None
