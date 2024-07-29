import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

with Path(os.getenv("DATA_FILE")).open() as f:
    data = json.load(f)

app = Flask(__name__)


@app.route("/")
def get_member_data():
    try:
        member_id = request.args['member_id']
    except KeyError as e:
        return jsonify(message="Missing argument member_id"), 400
        
    return jsonify(data.get(member_id, {}))
