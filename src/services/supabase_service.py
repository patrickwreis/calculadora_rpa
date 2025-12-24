"""Supabase client wrapper service"""
import os
from typing import Any, Dict, Optional

from supabase import create_client

from config.settings import SUPABASE_URL, SUPABASE_KEY


def get_supabase_client():
    """Create and return a Supabase client using env/config settings."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment or config.settings"
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)


class SupabaseService:
    """Lightweight helper for common Supabase operations."""

    def __init__(self):
        self.client = get_supabase_client()

    def insert(self, table: str, payload: Dict[str, Any]) -> Any:
        return self.client.table(table).insert(payload).execute()

    def select_all(self, table: str) -> Any:
        return self.client.table(table).select("*").execute()

    def rpc(self, fn: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.client.rpc(fn, params or {}).execute()

    def send_password_reset(self, email: str) -> Dict[str, Any]:
        """Trigger Supabase password recovery email for `email`.

        Tries to call the client auth helper if available, otherwise falls
        back to the direct REST endpoint `/auth/v1/recover` using the
        service key.
        Returns a dict with `ok: bool` and optional `error` message.
        """
        # Try client auth methods first (depends on supabase-py version)
        try:
            auth = getattr(self.client, "auth", None)
            if auth is not None:
                # v0.x style: auth.api.reset_password_for_email
                api = getattr(auth, "api", None)
                if api and hasattr(api, "reset_password_for_email"):
                    res = api.reset_password_for_email(email)
                    return {"ok": True, "result": res}

                # newer style: auth.reset_password_for_email
                if hasattr(auth, "reset_password_for_email"):
                    res = auth.reset_password_for_email(email)
                    return {"ok": True, "result": res}
        except Exception as e:
            # fall through to REST fallback
            fallback_err = str(e)

        # Fallback: call Supabase REST recover endpoint
        try:
            import requests

            if not SUPABASE_URL or not SUPABASE_KEY:
                return {"ok": False, "error": "SUPABASE_URL or SUPABASE_KEY not configured"}

            url = SUPABASE_URL.rstrip("/") + "/auth/v1/recover"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
            }
            payload = {"email": email}
            r = requests.post(url, json=payload, headers=headers, timeout=10)
            if r.status_code in (200, 204):
                return {"ok": True, "result": r.text}
            return {"ok": False, "error": f"unexpected status {r.status_code}: {r.text}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
