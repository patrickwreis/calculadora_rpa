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
