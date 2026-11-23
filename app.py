import time
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI(
    title="Brute force and Password Spraying Attack Prevention API",
    description="This API is designed to prevent brute force and password spraying attacks by implementing rate limiting and account lockout mechanisms.it is a lab for testing and learning purposes only.",
    version="1.0.0"
)

USERS = {
    "alice":"Pass@123",
    "bob":"India#2026"
}

LOGIN_LOGS:list[dict] = []

PASSWORD_SPRAYING_LOGS: dict[str, dict[str, list[dict]]] = {}

class LoginRequest(BaseModel):
    username: str
    password: str


SLOW_BRUTE_WINDOW = 900
SLOW_BRUTE_MAX_FAILURES = 6
MIN_PACED_GAP= 3.0
IP_BURST_WINDOW = 60
IP_MAX_FAILURES = 15            
USER_IP_WINDOW = 60
USER_IP_MAX_FAILURES = 4       

def is_ip_flooding(ip: str, now: float) -> bool:
    failures = sum(
        1
        for log in LOGIN_LOGS
        if log["ip"] == ip and not log["success"] and (now - log["timestamp"]) < IP_BURST_WINDOW
    )
    return failures >= IP_MAX_FAILURES


def is_user_targeted_from_ip(ip: str, username: str, now: float) -> bool:
    failures = sum(
        1
        for log in LOGIN_LOGS
        if log["ip"] == ip
        and log["username"] == username
        and not log["success"]
        and (now - log["timestamp"]) < USER_IP_WINDOW
    )
    return failures >= USER_IP_MAX_FAILURES

def is_paced_or_slow_brute_force(ip: str, now: float) -> bool:
    ip_failures = [
        log["timestamp"] for log in LOGIN_LOGS
        if log['ip'] == ip and not log["success"] and now - log["timestamp"] < SLOW_BRUTE_WINDOW
    ]
    if len(ip_failures) >= SLOW_BRUTE_MAX_FAILURES:
        return True

    if len(ip_failures) >= 3:
        ip_failures.sort()
        gaps = [ip_failures[i] - ip_failures[i - 1] for i in range(1, len(ip_failures))]

        if sum( 1 for g in gaps if g < MIN_PACED_GAP) >= 2:
            return True

    return False


def AppendLogs(logs: list[dict], ip: str, username: str, success: bool):
    logs.append({
        "timestamp": time.time(),
        "ip": ip,
        "username": username,
        "success": success
    })

def AppendPasswordSprayingLogs(
    logs: dict[str, dict[str, list[dict]]],
    ip: str,
    username: str,
    password: str,
    success: bool,
):
    if password not in logs:
        logs[password] = {}
    if username not in logs[password]:
        logs[password][username] = []
    logs[password][username].append({
        "timestamp": time.time(),
        "ip": ip,
        "success": success
    })

def password_spraying_protection(ip: str, password: str, rate_threshold: float = 1.0) -> bool:
    now = time.time()
    distinct_users: set[str] = set()
    recent_failed_attempts = 0

    user_map = PASSWORD_SPRAYING_LOGS.get(password, {})
    for username, password_attempts in user_map.items():
        for attempt in password_attempts:
            if (
                attempt.get("ip") == ip
                and now - attempt["timestamp"] < 300
                and not attempt["success"]
            ):
                recent_failed_attempts += 1
                distinct_users.add(username)

    per_minute_failure_rate = recent_failed_attempts / 5
    return len(distinct_users) >= 3 and per_minute_failure_rate >= rate_threshold

def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host

@app.post("/login")
async def login(payload: LoginRequest, request: Request):
    client_ip = get_client_ip(request)
    now = time.time()

    stored_password = USERS.get(payload.username)
    success = stored_password is not None and stored_password == payload.password

    if not success:
        AppendLogs(LOGIN_LOGS, client_ip, payload.username, success)
        AppendPasswordSprayingLogs(PASSWORD_SPRAYING_LOGS, client_ip, payload.username, payload.password, success)

    if is_user_targeted_from_ip(client_ip, payload.username, now):
        return {
            "status": "Too many attempts for this account, please try after sometime."
        }

    
    if is_ip_flooding(client_ip, now):
        return {
            "status": "Too many attempts from this network, please try after sometime."
        }

    is_password_spraying = password_spraying_protection(client_ip, payload.password)

    if success:
        AppendLogs(LOGIN_LOGS, client_ip, payload.username, success)
        AppendPasswordSprayingLogs(PASSWORD_SPRAYING_LOGS, client_ip, payload.username, payload.password, success)

    if is_password_spraying:
        return {
            "status": "Password spraying detected, please try after sometime."
        }

    if success:
        return {"status": "authenticated", "user": payload.username}

    return {"status": "invalid_credentials"}