from typing import Dict
import base64
import json

SECRET_KEY = b"1e5898ccb8dfdd921f9beca848768"

def decode_nickname(encoded: str) -> str:
    try:
        raw = base64.b64decode(encoded)
        dec = bytearray()
        for i, b in enumerate(raw):
            dec.append(b ^ SECRET_KEY[i % len(SECRET_KEY)])
        return dec.decode('utf-8')
    except Exception:
        return encoded  # fallback to original if decode fails


def pad_base64(b64_str: str) -> str:
    return b64_str + "=" * (-len(b64_str) % 4)


def decode_token_payload(token: str) -> Dict:
    try:
        payload_b64 = token.split(".")[1]
        payload_json = base64.urlsafe_b64decode(pad_base64(payload_b64)).decode("utf-8")
        return json.loads(payload_json)
    except Exception:
        return {}


def decode(token: str) -> str:
    payload = decode_token_payload(token)
    account_id = payload.get("account_id", "N/A")
    raw_nickname = payload.get("nickname", "N/A")
    nickname = decode_nickname(raw_nickname) if raw_nickname != "N/A" else "N/A"
    ReleaseVersion = payload.get("release_version", "N/A")
    return account_id, nickname, ReleaseVersion
