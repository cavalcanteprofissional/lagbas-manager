# Admin blueprint - Administrative functions
import jwt
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from utils.supabase_utils import get_admin_client
from blueprints.helpers import get_user_id, is_admin, get_user_role, get_habilitar_abas

admin_bp = Blueprint('admin', __name__)


def validate_admin_token():
    """Valida o token JWT para operações admin"""
    user_id = get_user_id()
    token = session.get("jwt_token")
    
    if not token:
        flash("Sessão inválida. Faça login novamente.", "danger")
        return None, redirect(url_for("auth.login"))
    
    try:
        from flask import current_app
        decoded = jwt.decode(token, current_app.secret_key, algorithms=["HS256"])
        if decoded.get("user_id") != user_id:
            flash("Acesso não autorizado.", "danger")
            return None, redirect(url_for("dashboard"))
    except:
        flash("Token inválido.", "danger")
        return None, redirect(url_for("auth.login"))
    
    return user_id, None


@admin_bp.route("/admin")
def panel():
    if not is_admin():
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for("dashboard"))
    
    user_id, error = validate_admin_token()
    if error:
        return error
    
    client = get_admin_client()
    users_response = client.table("perfil").select("*").execute()
    users = users_response.data or []
    
    for user in users:
        user_id = user.get("id")
        
        cilindro_count = client.table("cilindro").select("id", count="exact").eq("user_id", user_id).execute()
        elemento_count = client.table("elemento").select("id", count="exact").eq("user_id", user_id).execute()
        amostra_count = client.table("amostra").select("id", count="exact").eq("user_id", user_id).execute()
        
        user["nome"] = user.get("nome") or user.get("email") or user_id
        user["cilindros"] = cilindro_count.count or 0
        user["elementos"] = elemento_count.count or 0
        user["amostras"] = amostra_count.count or 0
        user["habilitar_abas"] = get_habilitar_abas(user["id"])
    
    return render_template("admin.html", users=users)


@admin_bp.route("/admin/toggle-user", methods=["POST"])
def toggle_user():
    if not is_admin():
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for("dashboard"))
    
    user_id, error = validate_admin_token()
    if error:
        return error
    
    target_user_id = request.form.get("user_id")
    ativo = request.form.get("ativo") == "true"
    
    if target_user_id == get_user_id():
        flash("Você não pode desativar seu próprio usuário.", "warning")
        return redirect(url_for("admin.panel"))
    
    client = get_admin_client()
    client.table("perfil").update({"ativo": ativo}).eq("id", target_user_id).execute()
    flash(f"Usuário {'ativado' if ativo else 'desativado'} com sucesso!", "success")
    
    return redirect(url_for("admin.panel"))


@admin_bp.route("/admin/set-role", methods=["POST"])
def set_role():
    if not is_admin():
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for("dashboard"))
    
    user_id, error = validate_admin_token()
    if error:
        return error
    
    target_user_id = request.form.get("user_id")
    role = request.form.get("role")
    
    if role not in ["admin", "usuario"]:
        flash("Função inválida.", "danger")
        return redirect(url_for("admin.panel"))
    
    if target_user_id == get_user_id():
        flash("Você não pode alterar sua própria função.", "warning")
        return redirect(url_for("admin.panel"))
    
    client = get_admin_client()
    client.table("perfil").update({"role": role}).eq("id", target_user_id).execute()
    flash(f"Função do usuário alterada para {role}!", "success")
    
    return redirect(url_for("admin.panel"))


@admin_bp.route("/admin/delete-user", methods=["POST"])
def delete_user():
    if not is_admin():
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for("dashboard"))
    
    user_id, error = validate_admin_token()
    if error:
        return error
    
    target_user_id = request.form.get("user_id")
    
    if target_user_id == get_user_id():
        flash("Você não pode excluir seu próprio usuário.", "warning")
        return redirect(url_for("admin.panel"))
    
    client = get_admin_client()
    client.table("cilindro").delete().eq("user_id", target_user_id).execute()
    client.table("elemento").delete().eq("user_id", target_user_id).execute()
    client.table("amostra").delete().eq("user_id", target_user_id).execute()
    client.table("perfil").delete().eq("id", target_user_id).execute()
    
    flash("Usuário e todos os seus dados foram excluídos!", "success")
    
    return redirect(url_for("admin.panel"))


@admin_bp.route("/admin/update-habilitar-abas", methods=["POST"])
def update_habilitar_abas():
    if not is_admin():
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for("dashboard"))
    
    user_id, error = validate_admin_token()
    if error:
        return error
    
    target_user_id = request.form.get("user_id")
    aba = request.form.get("aba")
    habilitar = request.form.get("habilitar") == "true"
    
    if not target_user_id or not aba:
        flash("Parâmetros inválidos.", "danger")
        return redirect(url_for("admin.panel"))
    
    if aba not in ["cilindro", "elemento", "amostra", "historico"]:
        flash("Aba inválida.", "danger")
        return redirect(url_for("admin.panel"))
    
    client = get_admin_client()
    
    perfil = client.table("perfil").select("habilitar_abas").eq("id", target_user_id).execute()
    
    habilitar_abas = {"cilindro": False, "elemento": False, "amostra": False, "historico": False}
    if perfil.data and perfil.data[0].get("habilitar_abas"):
        habilitar_abas = perfil.data[0].get("habilitar_abas")
    
    habilitar_abas[aba] = habilitar
    
    client.table("perfil").update({"habilitar_abas": habilitar_abas}).eq("id", target_user_id).execute()
    
    acao = "habilitada" if habilitar else "desabilitada"
    nome_aba = {"cilindro": "Cilindros", "elemento": "Elementos", "amostra": "Amostras", "historico": "Histórico"}.get(aba, aba)
    flash(f"Aba {nome_aba} {acao} com sucesso!", "success")
    
    client = get_admin_client()
    client.table("perfil").update({"habilitar_abas": habilitar_abas}).eq("id", target_user_id).execute()
    
    flash("Permissões de acesso atualizadas!", "success")
    
    return redirect(url_for("admin.panel"))


@admin_bp.route("/admin/user-data/<target_user_id>")
def user_data(target_user_id):
    if not is_admin():
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for("dashboard"))
    
    user_id, error = validate_admin_token()
    if error:
        return error
    
    client = get_admin_client()
    cilindro = client.table("cilindro").select("*").eq("user_id", target_user_id).execute().data or []
    elementos = client.table("elemento").select("*").eq("user_id", target_user_id).execute().data or []
    amostras = client.table("amostra").select("*").eq("user_id", target_user_id).execute().data or []
    
    perfil = client.table("perfil").select("*").eq("id", target_user_id).execute().data
    target_user = perfil[0] if perfil else {"id": target_user_id, "role": "unknown"}
    
    return render_template(
        "admin_user_data.html",
        target_user=target_user,
        cilindro=cilindro,
        elementos=elementos,
        amostras=amostras
    )
