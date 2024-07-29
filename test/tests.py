from pathlib import Path
import subprocess
import os

import pytest
import requests

from run_query_servers import QueryServers


@pytest.fixture(scope='module')
def servers():
    query_servers = QueryServers()
    query_servers.start_processes()
    os.environ["FLASK_APP"] = str(Path(__file__).resolve().parents[1] / 'src/coalesce_server.py')
    coalesce_server = subprocess.Popen(f"flask run", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    yield 
    query_servers.stop_processes()
    coalesce_server.terminate()


default_call_data = [
    (1, {"oop_max": 20000, "remaining_oop_max": 9000, "copay": 9000}),
    (2, {"oop_max": 123123, "remaining_oop_max": 1000, "copay": 1000}),
    (3, {"oop_max": 1234567, "remaining_oop_max": 98765, "copay": 0}),
]

@pytest.mark.parametrize("member_id,expected", default_call_data)
def test_default_call(servers, member_id, expected):
    response = requests.get("http://localhost:5000/api/coalescence/default", params={"member_id": member_id})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == expected


max_call_data = [
    (1, {"oop_max": 20000, "remaining_oop_max": 9000, "copay": 50000}),
    (2, {"oop_max": 123123, "remaining_oop_max": 1000, "copay": 2222}),
    (3, {"oop_max": 1234567, "remaining_oop_max": 98765, "copay": 0}),
]

@pytest.mark.parametrize("member_id,expected", max_call_data)
def test_max_call(servers, member_id, expected):
    response = requests.get("http://localhost:5000/api/coalescence/max", params={"member_id": member_id})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == expected


min_call_data = [
    (1, {"oop_max": 10000, "remaining_oop_max": 8000, "copay": 1000}),
    (2, {"oop_max": 99999, "remaining_oop_max": 0, "copay": 1111}),
    (3, {"oop_max": 1234567, "remaining_oop_max": 98765, "copay": 0}),
]
@pytest.mark.parametrize("member_id,expected", min_call_data)
def test_min_call(servers, member_id, expected):
    response = requests.get("http://localhost:5000/api/coalescence/min", params={"member_id": member_id})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == expected


avg_call_data = [
    (1, {"oop_max": 13333, "remaining_oop_max": 8667, "copay": 17333}),
    (2, {"oop_max": 111411, "remaining_oop_max": 367, "copay": 1522}),
    (3, {"oop_max": 1234567, "remaining_oop_max": 98765, "copay": 0}),
]

@pytest.mark.parametrize("member_id,expected", avg_call_data)
def test_avg_call(servers, member_id, expected):
    response = requests.get("http://localhost:5000/api/coalescence/avg", params={"member_id": member_id})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == expected

def test_invalid_strategy(servers):
    response = requests.get("http://localhost:5000/api/coalescence/nonexistant", params={"member_id": 1})
    assert response.status_code == 400
    response_json = response.json()
    assert response_json == {"message": "Invalid strategy: nonexistant"}

def test_nonexistant_member(servers):
    response = requests.get("http://localhost:5000/api/coalescence/default", params={"member_id": 42})
    assert response.status_code == 404
    response_json = response.json()
    assert response_json == {"message": "No info found for member 42"}

def test_missing_member_id(servers):
    response = requests.get("http://localhost:5000/api/coalescence/default")
    assert response.status_code == 400
    response_json = response.json()
    assert response_json == {"message": "Missing member_id key"}