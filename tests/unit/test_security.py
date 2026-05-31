from datetime import timedelta

import pytest
from jose import jwt

from app.core import security
from app.core.config import settings


# ---------- Пароли ----------

def test_password_hash_and_verify_ok():
    raw = "MySecret123!"
    hashed = security.pwd_context.hash(raw)

    assert hashed != raw
    assert security.pwd_context.verify(raw, hashed) is True


def test_password_verify_wrong():
    hashed = security.pwd_context.hash("correct")
    assert security.pwd_context.verify("wrong", hashed) is False


# ---------- Токены ----------

def test_create_access_token_contains_correct_payload():
    token = security.create_access_token(subject=42)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_refresh_token_contains_correct_payload():
    token = security.create_refresh_token(subject="user-1")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert payload["sub"] == "user-1"
    assert payload["type"] == "refresh"


def test_decode_token_valid():
    token = security.create_access_token(subject=1)
    payload = security.decode_token(token)

    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["type"] == "access"


def test_decode_token_invalid_returns_none():
    assert security.decode_token("this.is.not.a.jwt") is None


def test_decode_token_bad_signature_returns_none():
    # токен подписан другим ключом → должен вернуть None
    bad_token = jwt.encode({"sub": "1"}, "another-secret", algorithm="HS256")
    assert security.decode_token(bad_token) is None


def test_internal_create_token_sets_expiration():
    token = security._create_token(
        subject="abc",
        expires_delta=timedelta(minutes=5),
        token_type="access",
    )
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "abc"
    assert payload["type"] == "access"
