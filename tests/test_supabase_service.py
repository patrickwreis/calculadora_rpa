import types

import pytest

from src.services import supabase_service as svc


class _FakeResp:
    def __init__(self, status_code=200, text="OK"):
        self.status_code = status_code
        self.text = text


def test_send_password_reset_via_auth_api(monkeypatch):
    class FakeAPI:
        def reset_password_for_email(self, email):
            return {"status": "sent", "email": email}

    class FakeAuth:
        api = FakeAPI()

    class FakeClient:
        auth = FakeAuth()

    monkeypatch.setattr(svc, "get_supabase_client", lambda: FakeClient())

    s = svc.SupabaseService()
    res = s.send_password_reset("user@example.com")
    assert res.get("ok") is True


def test_send_password_reset_via_auth_reset(monkeypatch):
    class FakeAuth:
        @staticmethod
        def reset_password_for_email(email):
            return {"status": "sent2", "email": email}

    class FakeClient:
        auth = FakeAuth()

    monkeypatch.setattr(svc, "get_supabase_client", lambda: FakeClient())

    s = svc.SupabaseService()
    res = s.send_password_reset("user2@example.com")
    assert res.get("ok") is True


def test_send_password_reset_rest_fallback_success(monkeypatch):
    # client without auth -> force REST fallback
    monkeypatch.setattr(svc, "get_supabase_client", lambda: object())
    monkeypatch.setattr(svc, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(svc, "SUPABASE_KEY", "testkey")

    import requests

    monkeypatch.setattr(requests, "post", lambda url, json, headers, timeout: _FakeResp(200, "OK"))

    s = svc.SupabaseService()
    res = s.send_password_reset("fallback@example.com")
    assert res.get("ok") is True


def test_send_password_reset_rest_fallback_error(monkeypatch):
    monkeypatch.setattr(svc, "get_supabase_client", lambda: object())
    monkeypatch.setattr(svc, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(svc, "SUPABASE_KEY", "testkey")

    import requests

    monkeypatch.setattr(requests, "post", lambda url, json, headers, timeout: _FakeResp(400, "Bad Request"))

    s = svc.SupabaseService()
    res = s.send_password_reset("fallback2@example.com")
    assert res.get("ok") is False


def test_send_password_reset_missing_config(monkeypatch):
    # Ensure missing config returns error
    monkeypatch.setattr(svc, "get_supabase_client", lambda: object())
    monkeypatch.setattr(svc, "SUPABASE_URL", "")
    monkeypatch.setattr(svc, "SUPABASE_KEY", "")

    s = svc.SupabaseService()
    res = s.send_password_reset("no-config@example.com")
    assert res.get("ok") is False
