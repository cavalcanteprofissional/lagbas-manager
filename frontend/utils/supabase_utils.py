# Supabase utility functions
import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

_supabase_client = None
_admin_client = None


def get_supabase_client():
    """Retorna cliente Supabase常规 (anon key)."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


def get_admin_client():
    """Retorna cliente Supabase com service_role (bypass RLS)."""
    global _admin_client
    if _admin_client is None:
        _admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _admin_client


def buscar_perfis_usuarios(user_ids):
    """Busca perfis de múltiplos usuários em uma única consulta (otimização N+1)."""
    from flask import current_app
    
    supabase = get_supabase_client()
    if not user_ids:
        return {}
    try:
        perfis = supabase.table("perfil").select("id,nome").in_("id", list(user_ids)).execute().data
        return {p["id"]: p.get("nome", str(p["id"])) for p in (perfis or [])}
    except Exception:
        return {uid: str(uid) for uid in user_ids}


# Aliases for backwards compatibility
supabase_client = get_supabase_client
