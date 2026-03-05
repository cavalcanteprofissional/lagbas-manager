# Historico blueprint - Activity history
from flask import Blueprint, render_template

from utils.supabase_utils import get_supabase_client
from utils.supabase_utils import buscar_perfis_usuarios
from blueprints.helpers import get_user_id, is_admin

historico_bp = Blueprint('historico', __name__)


@historico_bp.route("/historico")
def list():
    user_id = get_user_id()
    admin = is_admin()
    
    limit = 20
    
    historico_log = get_supabase_client().table("historico_log").select("*").order("created_at", desc=True).limit(limit).execute().data or []
    
    all_user_ids = {h.get("user_id") for h in historico_log if h.get("user_id")}
    user_map = buscar_perfis_usuarios(all_user_ids)
    if not user_map:
        user_map = {uid: str(uid) for uid in all_user_ids}
    
    history = []
    
    for h in historico_log:
        history.append({
            "tipo": h.get("tipo"),
            "acao": h.get("acao"),
            "nome": h.get("nome"),
            "data": h.get("created_at"),
            "user_id": h.get("user_id"),
            "usuario_nome": user_map.get(h.get("user_id"), '-')
        })
    
    return render_template("historico.html", history=history)
