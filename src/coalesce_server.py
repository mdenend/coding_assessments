from flask import Flask, jsonify, request
from pathlib import Path
import requests
import sys

ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_PATH))

from src.config import load_config
from src.strategies import min_all, max_all, avg_all, default_strategy, coalesce

CONFIG = load_config("src/config/config.yml")

# Further strategies can be added here after being added in strategies.py and imported here.
# Key is what the path variable must be for the API to call, and value is the actual function.
VALID_STRATEGIES = {
    'min': min_all,
    'max': max_all,
    'avg': avg_all,
    'default': default_strategy
}

app = Flask(__name__)

@app.route("/api/coalescence/<strategy>")
def coalesce_amounts(strategy):
    if strategy not in VALID_STRATEGIES:
        # Could reveal all strategies here, but this might be giving away too
        # much info, so going to not pass that back.
        return jsonify(message=f"Invalid strategy: {strategy}"), 400

    try:
        member_id = request.args["member_id"]
    except KeyError as e:
        return jsonify(message="Missing member_id key"), 400
    
    query_params = {'member_id': member_id}
    responses = []

    for address in CONFIG['query_servers']:
        #TODO: try except when an HTTP error happens. If a server fails to connect, we should log it
        # Not going to add this, but will leave a TODO that I would address down the road for a serious
        # backend
        response = requests.get(address, params=query_params)
        if response.status_code == 200:
            if response.json():
                responses.append(response.json())

    if not responses:
        return jsonify(message=f"No info found for member {member_id}"), 404

    return jsonify(coalesce(responses, VALID_STRATEGIES[strategy])), 200
