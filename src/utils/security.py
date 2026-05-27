import base64
import hashlib
import os
import secrets
import uuid


def generate_uuid():
    return str(uuid.uuid4())


def generate_token():
    return str(uuid.uuid4())


def generate_auth_token():
    return secrets.token_urlsafe(32)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return base64.b64encode(salt + hashed).decode("utf-8")


def verify_password(password: str, stored_hash: str) -> bool:
    decoded = base64.b64decode(stored_hash.encode("utf-8"))
    salt = decoded[:16]
    stored = decoded[16:]
    computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return secrets.compare_digest(computed, stored)
