from flask import Flask, jsonify, request
from flask_caching import Cache
from app.utils.response import process_token, process_token_direct
from colorama import init
import warnings
from urllib3.exceptions import InsecureRequestWarning
import time
from dotenv import load_dotenv
import os
import logging

load_dotenv()



logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ignore SSL warnings
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

# Initialize colorama
init(autoreset=True)

# Initialize Flask app
app = Flask(__name__)



cache = Cache(app, config={"CACHE_TYPE": "simple"})  # In-memory cache

@app.route("/")
def home():
    return "JWT Token Generator API is running!"

@app.route("/token", methods=["GET"])
async def get_responses():
    uid = request.args.get("uid")
    password = request.args.get("password")

    if uid and password:
        # Generate a unique cache key per request using a timestamp
        cache_key = f"token_{uid}_{password}_{int(time.time())}"

        response = process_token(uid, password)
        status_code=int(response.get("status_code", 500))
        region =response.get("server","NONE")

        cache.set(
            cache_key, response, timeout=3600
        )  
        return jsonify(response),status_code
    

    return jsonify({"message": "Bulk retrieval logic has been removed."})

@app.route("/jwt", methods=["GET"])
async def get_jwt_from_token():
    access_token = request.args.get("access_token")

    if not access_token:
        return jsonify({"error": True, "message": "access_token is required"}), 400

    response = process_token_direct(access_token)
    status_code = int(response.get("status_code", 500))
    return jsonify(response), status_code

if __name__ == "__main__":
    print("dorrkf")
    port =5002
    app.run(host="0.0.0.0", port=port,debug=True )
