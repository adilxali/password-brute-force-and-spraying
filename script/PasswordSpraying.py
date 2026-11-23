import json
import time
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8000/login"

USERS = ("alice", "bob", "charlie", "dave")
PADDING_PASSWORDS = ["wrong1", "wrong2", "wrong3", "wrong4", "wrong5"]

for attempt in PADDING_PASSWORDS:
    for username in USERS:
        data = json.dumps({"username": username, "password": attempt}).encode("utf-8")
        req = urllib.request.Request(
            URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                body = resp.read().decode("utf-8")
                print(f"Attempt {attempt} for {username}: {resp.status} - {body}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            print(f"Attempt {attempt} for {username}: {e.code} - {body}")
        
        time.sleep(1)
