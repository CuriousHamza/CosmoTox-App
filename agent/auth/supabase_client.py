"""
Supabase service-role client.

Uses the service role key, which bypasses Row Level Security (RLS).
Only used server-side — never exposed to the frontend.
"""

import os

from supabase import Client, create_client

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_KEY"]
        _client = create_client(url, key)
    return _client
