# -*- coding: utf-8 -*-
"""Unit tests for src.ui.auth helper functions (non-UI paths)."""
import os
from unittest.mock import MagicMock, patch

import pytest

import src.ui.auth as auth


def test_truncate_for_bcrypt_limits_to_72_bytes():
    long_password = "x" * 200
    truncated = auth._truncate_for_bcrypt(long_password)
    assert len(truncated) == 72


def test_hash_and_verify_password_roundtrip():
    pwd = "Abc12345"
    hashed = auth.hash_password(pwd)
    assert auth.verify_password(pwd, hashed)
    assert not auth.verify_password("wrong", hashed)


def test_auth_required_respects_env(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "false")
    assert auth.auth_required() is False
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    assert auth.auth_required() is True


def test_load_credentials_builds_lookup_and_credentials():
    user = MagicMock(username="alice", password_hash="hash", id=1, is_admin=True)
    db = MagicMock()
    db.list_active_users.return_value = [user]

    credentials, lookup = auth._load_credentials(db)
    assert credentials["usernames"]["alice"]["password"] == "hash"
    assert lookup["alice"]["is_admin"] is True


def test_ensure_default_admin_creates_when_missing(monkeypatch):
    """Test that default admin is created only when env vars are set."""
    db = MagicMock()
    db.get_user_by_username.return_value = None
    
    # Set env vars for admin creation
    monkeypatch.setenv("AUTH_USERNAME", "testadmin")
    monkeypatch.setenv("AUTH_PASSWORD", "testpass123")
    
    auth._ensure_default_admin(db)
    db.create_user.assert_called_once()


def test_ensure_default_admin_skips_without_env_vars(monkeypatch):
    """Test that default admin is NOT created when env vars are missing."""
    db = MagicMock()
    
    # Remove env vars
    monkeypatch.delenv("AUTH_USERNAME", raising=False)
    monkeypatch.delenv("AUTH_PASSWORD", raising=False)
    
    auth._ensure_default_admin(db)
    db.create_user.assert_not_called()


def test_ensure_default_admin_skips_when_exists():
    db = MagicMock()
    db.get_user_by_username.return_value = MagicMock()
    auth._ensure_default_admin(db)
    db.create_user.assert_not_called()


def test_send_password_reset_email_returns_false_without_sender(monkeypatch):
    monkeypatch.delenv("EMAIL_SENDER", raising=False)
    monkeypatch.delenv("EMAIL_PASSWORD", raising=False)
    with patch("streamlit.warning") as mock_warn:
        assert auth.send_password_reset_email("u@e.com", "user", "temp") is False
        mock_warn.assert_called_once()


def test_send_password_reset_email_success(monkeypatch):
    monkeypatch.setenv("EMAIL_SENDER", "sender@example.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "secret")
    monkeypatch.setenv("SMTP_SERVER", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")

    fake_server = MagicMock()
    fake_context = MagicMock()
    fake_context.__enter__.return_value = fake_server
    fake_context.__exit__.return_value = False

    with patch("smtplib.SMTP", return_value=fake_context):
        result = auth.send_password_reset_email("u@e.com", "user", "temp")
        assert result is True
        fake_server.starttls.assert_called_once()
        fake_server.login.assert_called_once()
        fake_server.send_message.assert_called_once()


def test_logout_clears_auth_session(monkeypatch):
    class FakeState(dict):
        def __getattr__(self, item):
            return self.get(item)

    state = FakeState(auth_user="u", auth_user_id=1, auth_is_admin=True)
    monkeypatch.setattr(auth.st, "session_state", state, raising=False)

    auth.logout()
    assert "auth_user" not in state
    assert "auth_user_id" not in state
    assert "auth_is_admin" not in state
