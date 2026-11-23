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

PASSWORD_SPRAYING_LOGS:dict[str, list[dict]] = {}

class LoginRequest(BaseModel):
    username: str
    password: str




def AppendLogs(logs: list[dict], ip: str, username: str, success: bool):
    logs.append({
        "timestamp": time.time(),
        "ip": ip,
        "username": username,
        "success": success
    })

def AppendPasswordSprayingLogs(logs: dict[str, list[dict]], ip: str,username:str, password: str, success: bool):
    if password not in logs:
        logs[password] = {}
    if username not in logs[password]:
        logs[password][username] = []
    logs[password][username].append({
        "timestamp": time.time(),
        "ip": ip,
        "success": success
    })

def password_spraying_protection(ip: str, password: str) -> bool:
    now = time.time()
    distinct_users: set[str] = set()
    recent_failed_attempts = 0

    user_map = PASSWORD_SPRAYING_LOGS.get(password, {})
    for username, password_attempts in user_map.items():
        for attempt in password_attempts:
            if (
                attempt.get("ip") == ip
                and now - attempt["timestamp"] < 60
                and not attempt["success"]
            ):
                recent_failed_attempts += 1
                distinct_users.add(username)

    return len(distinct_users) >= 3

@app.post("/login")
async def login(payload: LoginRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    logins_attempts_from_ip = 0
    for log in LOGIN_LOGS:
        if log["ip"] == client_ip and now - log["timestamp"] < 60 and not log["success"]:
            logins_attempts_from_ip += 1

    if logins_attempts_from_ip > 3:
        return {
            "status":"Too many attempts, please try after sometime."
        }

    stored_password = USERS.get(payload.username)
    success = stored_password is not None and stored_password == payload.password

    is_password_spraying = password_spraying_protection(client_ip, payload.password)
    AppendLogs(LOGIN_LOGS, client_ip if request.client else "unknown", payload.username, success)
    AppendPasswordSprayingLogs(PASSWORD_SPRAYING_LOGS, client_ip if request.client else "unknown", payload.username, payload.password, success)

    if is_password_spraying:
        return {
            "status":"Password spraying detected, please try after sometime."
        }

    if success:
        return {"status":"authenticated", "user":payload.username}
    
    return {"status":"invalid_credentials"}