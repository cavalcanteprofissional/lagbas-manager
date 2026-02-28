from supabase import create_client, Client
from utils.config import SUPABASE_URL, SUPABASE_KEY

_supabase_client: Client = None


def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


def get_user_cilindros(user_id: str):
    supabase = get_supabase()
    response = supabase.table("cilindros").select("*").eq("user_id", user_id).execute()
    return response.data


def get_user_elementos(user_id: str):
    supabase = get_supabase()
    response = supabase.table("elementos").select("*").eq("user_id", user_id).execute()
    return response.data


def get_user_amostras(user_id: str):
    supabase = get_supabase()
    response = supabase.table("amostras").select("*").eq("user_id", user_id).execute()
    return response.data


def get_user_tempo_chama(user_id: str):
    supabase = get_supabase()
    response = supabase.table("tempo_chama").select("*").eq("user_id", user_id).execute()
    return response.data


def get_all_cilindros():
    supabase = get_supabase()
    response = supabase.table("cilindros").select("*").execute()
    return response.data


def get_all_elementos():
    supabase = get_supabase()
    response = supabase.table("elementos").select("*").execute()
    return response.data


def get_cilindro_by_id(cilindro_id: int):
    supabase = get_supabase()
    response = supabase.table("cilindros").select("*").eq("id", cilindro_id).execute()
    return response.data[0] if response.data else None


def get_elemento_by_id(elemento_id: int):
    supabase = get_supabase()
    response = supabase.table("elementos").select("*").eq("id", elemento_id).execute()
    return response.data[0] if response.data else None


def check_codigo_exists(codigo: str, user_id: str, exclude_id: int = None):
    supabase = get_supabase()
    query = supabase.table("cilindros").select("id").eq("codigo", codigo).eq("user_id", user_id)
    if exclude_id:
        query = query.neq("id", exclude_id)
    response = query.execute()
    return len(response.data) > 0


def check_elemento_nome_exists(nome: str, user_id: str, exclude_id: int = None):
    supabase = get_supabase()
    query = supabase.table("elementos").select("id").eq("nome", nome).eq("user_id", user_id)
    if exclude_id:
        query = query.neq("id", exclude_id)
    response = query.execute()
    return len(response.data) > 0


def initialize_default_elementos(user_id: str):
    from utils.config import ELEMENTOS_PADRAO
    supabase = get_supabase()
    for elemento in ELEMENTOS_PADRAO:
        existing = supabase.table("elementos").select("id").eq("nome", elemento["nome"]).eq("user_id", user_id).execute()
        if not existing.data:
            supabase.table("elementos").insert({
                "nome": elemento["nome"],
                "consumo_lpm": elemento["consumo_lpm"],
                "user_id": user_id
            }).execute()
