# Helper functions for the application
import logging
from flask import session

logger = logging.getLogger(__name__)


def get_user_id():
    """Retorna o ID do usuário atual"""
    return session.get("user_id")


def is_admin():
    """Verifica se o usuário atual é admin"""
    user_id = get_user_id()
    if not user_id:
        logger.warning("is_admin: user_id não encontrado na sessão")
        return False
    
    try:
        from utils.supabase_utils import get_supabase_client
        supabase = get_authenticated_client()
        response = supabase.table("perfil").select("role").eq("id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            role = response.data[0].get("role", "usuario")
            logger.info(f"is_admin: user_id={user_id}, role={role}")
            return role == "admin"
        else:
            logger.warning(f"is_admin: perfil não encontrado para user_id={user_id}")
    except Exception as e:
        logger.error(f"is_admin: erro ao buscar perfil: {str(e)}")
    
    return False


def is_user_active(user_id):
    """Verifica se o usuário está ativo"""
    try:
        from utils.supabase_utils import get_supabase_client
        supabase = get_authenticated_client()
        response = supabase.table("perfil").select("ativo").eq("id", user_id).execute()
        if response.data:
            return response.data[0].get("ativo", True)
    except Exception as e:
        logger.error(f"is_user_active: erro: {str(e)}")
    return True


def get_user_role():
    """Retorna o role do usuário atual"""
    user_id = get_user_id()
    if not user_id:
        return "usuario"
    try:
        from utils.supabase_utils import get_supabase_client
        supabase = get_authenticated_client()
        response = supabase.table("perfil").select("role").eq("id", user_id).execute()
        if response.data:
            return response.data[0].get("role", "usuario")
    except Exception as e:
        logger.error(f"get_user_role: erro: {str(e)}")
    return "usuario"


def get_user_name():
    """Retorna o nome do usuário atual"""
    user_id = get_user_id()
    if not user_id:
        return ""
    try:
        supabase = get_authenticated_client()
        response = supabase.table("perfil").select("nome").eq("id", user_id).execute()
        if response.data:
            return response.data[0].get("nome", "")
    except Exception as e:
        logger.error(f"get_user_name: erro: {str(e)}")
    return ""


def get_authenticated_client():
    """Retorna cliente Supabase autenticado com token JWT do usuário"""
    from utils.supabase_utils import get_supabase_client
    token = session.get("supabase_token")
    if token:
        client = get_supabase_client()
        client.auth.set_session(token, "")
        return client
    return get_supabase_client()


def get_admin_client():
    """Retorna cliente Supabase com service_role (bypass RLS)"""
    from utils.supabase_utils import get_admin_client as supabase_admin
    return supabase_admin()


def registrar_historico(tipo, acao, nome, user_id):
    """Registra uma ação no histórico"""
    from utils.supabase_utils import get_admin_client
    try:
        client = get_admin_client()
        client.table("historico_log").insert({
            "tipo": tipo,
            "acao": acao,
            "nome": nome,
            "user_id": user_id
        }).execute()
        logger.info(f"Histórico registrado: {tipo} | {acao} | {nome} | User: {user_id}")
    except Exception as e:
        logger.error(f"Erro ao registrar histórico: {str(e)}")
