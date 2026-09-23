import secrets


def new_id(prefix: str = "") -> str:
    token = secrets.token_hex(10)
    if not prefix:
        return token[:20]
    return f"{prefix}{token}"[:20]
