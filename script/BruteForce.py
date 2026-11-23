import json
import urllib.request
import time

URL = "http://127.0.0.1:8000/login"
INITIAL_DELAY = 1  # Initial delay in seconds
for attempt in range(1, 100):
    # time.sleep(INITIAL_DELAY + (attempt - 1) * 15) 
    data = json.dumps({"username": "alice", "password": "wrong"}).encode("utf-8")
    req = urllib.request.Request(
        URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        print(f"Attempt {attempt}: {body}")