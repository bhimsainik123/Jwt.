from typing import Dict
import base64
import json


def pad_base64(b64_str: str) -> str:
    """Ajoute le padding nécessaire pour une chaîne base64."""
    return b64_str + "=" * (-len(b64_str) % 4)


def decode_token_payload(token: str) -> Dict:
    """Décode le payload JWT et retourne un dict. Renvoie {} en cas d'échec."""
    try:
        payload_b64 = token.split(".")[1]
        payload_json = base64.urlsafe_b64decode(pad_base64(payload_b64)).decode("utf-8")
        return json.loads(payload_json)
    except Exception:
        return {}


def decode(token: str) -> str:
    """Retourne uniquement la valeur du champ 'lock_region' du token."""
    payload = decode_token_payload(token)
    account_id = payload.get("account_id", "N/A")
    nickname = payload.get("nickname", "N/A")
    ReleaseVersion =payload.get("release_version", "N/A")
    return account_id ,nickname ,ReleaseVersion

