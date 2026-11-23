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

@app.post("/login")
async def login(payload: LoginRequest, request: Request):

    logins_attempts_from_ip = 0
    for log in LOGIN_LOGS:
        if log["ip"] == request.client.host and time.time() - log["timestamp"] < 60 and not log["success"]:
            logins_attempts_from_ip += 1

    if logins_attempts_from_ip > 3:
        AppendLogs(LOGIN_LOGS, request.client.host if request.client else "unknown", payload.username, False)
        return {
            "status":"Too many attempts, please try after sometime."
        }

    stored_password = USERS.get(payload.username)
    success = stored_password is not None and stored_password == payload.password

    AppendLogs(LOGIN_LOGS, request.client.host if request.client else "unknown", payload.username, success)


    if success:
        return {"status":"authenticated", "user":payload.username}
    
    return {"status":"invalid_credentials"}