from flask import Flask
from flask_assets import Environment, Bundle
from datetime import datetime, timedelta, timezone
import uuid
import hashlib
import jwt
from jwt.algorithms import NoneAlgorithm, HMACAlgorithm
from typing import Any


def setup_assets(app : Flask) -> None:
    """Setup the assets pipeline."""
    assets = Environment(app)
    css = Bundle("dist/main.css")
    assets.register("css", css)


def valid_user(username: str, password: str) -> bool:
    """Check if the user credentials are valid."""
    # Sample user credentials (in a real application, use a database)
    valid_users = {"user1": "password1", "user2": "password2"}
    return username in valid_users and valid_users[username] == password


def create_access_token(
    identity: str,
    key: str,
    expires_delta: timedelta = timedelta(minutes=15),
    algorithm: str = "HS256",
    kid: str | None = None,
) -> str:
    """Create an access token."""

    now = datetime.now(timezone.utc)

    token_data = {
        "iat": now,
        "nbf": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
        "type": "access",
        "username": identity,
    }

    headers = None
    if kid:
        headers = {"kid": kid}

    return jwt.encode(
        token_data,
        key,
        algorithm,
        headers=headers,
    )


class DemoNoneAlgorithm(NoneAlgorithm):
    """An implementation of the None algorithm that always returns True."""

    def prepare_key(self, key: str | None) -> None:
        return None

    def verify(self, msg: bytes, key: None, sig: bytes) -> bool:
        return True


class DemoHMACAlgorithm(HMACAlgorithm):
    """An implementation of the HMAC algorithm that allows PEM keys."""

    def prepare_key(self, key: str | bytes) -> bytes:
        if isinstance(key, str):
            return key.encode("utf-8")
        return key


# Replace the default algorithms with the demo algorithms
jwt.unregister_algorithm("none")
jwt.register_algorithm("none", DemoNoneAlgorithm())
jwt.unregister_algorithm("HS256")
jwt.register_algorithm("HS256", DemoHMACAlgorithm(hashlib.sha256))


def get_user(token: str, key: str, algs: list[str]) -> str:
    """Get the user from a token."""

    if not token:
        raise ValueError("invalid token")
    payload = jwt.decode(token, key, algorithms=algs)
    return str(payload["username"])
