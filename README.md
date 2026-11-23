# Password Brute-Force and Spraying Prevention

A small FastAPI lab for demonstrating basic defenses against brute-force and
password-spraying attacks. The API applies a per-IP, in-memory login attempt
limit and records login activity while the application is running.

> [!WARNING]
> This project is for authorized testing and learning purposes only. Do not
> deploy it as authentication code without a production-grade authentication,
> persistence, and abuse-prevention design.

## Features

- FastAPI login endpoint
- JSON request and response bodies
- Per-IP failed-login counting over a 60-second window
- Temporary blocking after more than three recent failed attempts
- In-memory login audit log

## Requirements

- Python 3.9 or later
- `fastapi`
- `uvicorn`
- `pydantic`

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/adilxali/password-brute-force-and-spraying.git
cd password-brute-force-and-spraying
python -m pip install fastapi uvicorn
```

## Running the API

Start the development server:

```bash
uvicorn app:app --reload
```

The API is then available at `http://127.0.0.1:8000`. Interactive
documentation is provided by Swagger UI at `/docs` and ReDoc at `/redoc`.

## Login endpoint

### `POST /login`

Send a username and password as JSON:

```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Pass@123"}'
```

#### Successful login

```json
{
  "status": "authenticated",
  "user": "alice"
}
```

#### Invalid credentials

```json
{
  "status": "invalid_credentials"
}
```

#### Rate limit response

After a source IP has accumulated more than three failed attempts in the
preceding 60 seconds, subsequent requests receive:

```json
{
  "status": "Too many attempts, please try after sometime."
}
```

## Lab users

| Username | Password |
| --- | --- |
| `alice` | `Pass@123` |
| `bob` | `India#2026` |

These credentials are intentionally public and are included only for this lab.

## How the protection works

Every login attempt is stored in `LOGIN_LOGS` with a timestamp, client IP,
username, and success state. An attempt from an IP is considered rate-limited
when more than three unsuccessful attempts from that IP are less than 60 seconds
old. Successful attempts do not contribute to the failed-attempt count.

## Limitations

This implementation is a demonstration, not a complete security control:

- Attempts and users are held only in memory and reset when the process restarts.
- The client IP is used for limits; it may be shared or spoofed by proxies.
- No user lockout, MFA, password hashing, session management, or token issuance
  is implemented.
- The limit is in-memory and is not shared across multiple application workers.
- Login responses do not include timing, CORS, logging, or monitoring controls
  suitable for production.

Use TLS, secure password hashing, persistent storage, centralized rate limiting,
MFA, and a reviewed authentication framework before using similar logic in a
real application.