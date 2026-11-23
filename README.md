# Password brute force and spraying (Python learning example)

This repository contains a small, **offline-only** demonstration of two
password-testing concepts:

- **Brute force:** try candidate passwords until a match is found.
- **Password spraying:** try the same password across several users.

It is intended for learning and works only against values supplied by the
caller. It does not send requests to websites or authenticate against real
accounts.

## Usage

```bash
python3 password_tool.py brute-force --target "learning" --passwords "a" "learning" "other"
python3 password_tool.py spray --password "learning" --accounts alice learning --accounts bob different
```

For password spraying, repeat `--accounts USERNAME PASSWORD` to supply each
local username/password pair. For example, the command above finds Alice and
leaves Bob unmatched.

## Python API

```python
from password_tool import brute_force, password_spray

match = brute_force(["a", "b", "learning"], "learning")
matches = password_spray(
    {"alice": "learning", "bob": "different"},
    "learning",
)
```