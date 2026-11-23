from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import threading
import time
import urllib.request

URL = "http://127.0.0.1:8000/login"
IPS = [f"10.0.0.{i}" for i in range(1, 101)]  # 100 simulated IPs
TOTAL_REQUESTS = 300000
CONCURRENCY = 30
BARRIER = threading.Barrier(CONCURRENCY)


def send_login(attempt_num: int, ip: str, username: str = "alice", password: str = "wrong") -> str:
    payload = json.dumps({"username": username, "password": password}).encode("utf-8")
    req = urllib.request.Request(
        URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Forwarded-For": ip,
        },
        method="POST",
    )
    BARRIER.wait()
    start = time.perf_counter()
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
    elapsed = (time.perf_counter() - start) * 1000
    return f"Attempt {attempt_num:02d} [{ip}] ({elapsed:6.1f} ms): {body}"


def main():
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [
            executor.submit(send_login, i, IPS[(i - 1) % len(IPS)])
            for i in range(1, TOTAL_REQUESTS + 1)
        ]
        for fut in as_completed(futures):
            print(fut.result())


if __name__ == "__main__":
    main()