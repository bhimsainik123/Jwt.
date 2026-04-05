from flask import Flask, jsonify, request
from flask_caching import Cache
from app.utils.response import process_token, process_token_direct
from colorama import init
import warnings
from urllib3.exceptions import InsecureRequestWarning
import time
import base64
import json
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore", category=InsecureRequestWarning)
init(autoreset=True)

app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple"})

# ─────────────────────────────────────────
#  HOME
# ─────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({"message": "JWT Token Generator & Decoder API is running!"})


# ─────────────────────────────────────────
#  /token  →  uid + password se FF JWT
# ─────────────────────────────────────────
@app.route("/token", methods=["GET"])
async def get_responses():
    uid = request.args.get("uid")
    password = request.args.get("password")

    if uid and password:
        cache_key = f"token_{uid}_{password}_{int(time.time())}"
        response = process_token(uid, password)
        status_code = int(response.get("status_code", 500))
        cache.set(cache_key, response, timeout=3600)
        return jsonify(response), status_code

    return jsonify({"error": "uid and password are required"}), 400


# ─────────────────────────────────────────
#  /jwt  →  access_token se FF JWT
# ─────────────────────────────────────────
@app.route("/jwt", methods=["GET"])
async def get_jwt_from_token():
    access_token = request.args.get("access_token")

    if not access_token:
        return jsonify({"error": True, "message": "access_token is required"}), 400

    response = process_token_direct(access_token)
    status_code = int(response.get("status_code", 500))
    return jsonify(response), status_code


# ─────────────────────────────────────────
#  /decode  →  Koi bhi JWT decode karo
# ─────────────────────────────────────────
def pad_base64(s):
    return s + "=" * (-len(s) % 4)

@app.route("/decode", methods=["GET"])
def decode_jwt():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "token parameter is required"}), 400

    if token.startswith("Bearer "):
        token = token[7:]

    try:
        parts = token.split(".")
        if len(parts) != 3:
            return jsonify({"error": "Invalid JWT format"}), 400

        header_json = base64.urlsafe_b64decode(pad_base64(parts[0])).decode("utf-8")
        header = json.loads(header_json)

        payload_json = base64.urlsafe_b64decode(pad_base64(parts[1])).decode("utf-8")
        payload = json.loads(payload_json)

        signature = parts[2]

        now = int(time.time())
        exp = payload.get("exp")
        iat = payload.get("iat")
        is_expired = exp is not None and now > exp

        time_remaining = None
        if exp is not None and not is_expired:
            time_remaining = exp - now

        issued_at = None
        if iat is not None:
            issued_at = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(iat))

        expires_at = None
        if exp is not None:
            expires_at = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(exp))

        return jsonify({
            "valid": not is_expired,
            "expired": is_expired,
            "issued_at": issued_at,
            "expires_at": expires_at,
            "time_remaining_seconds": time_remaining,
            "header": header,
            "payload": payload,
            "signature": signature
        })

    except Exception as e:
        return jsonify({"error": f"Failed to decode token: {str(e)}"}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)
