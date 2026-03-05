# Elemento blueprint - CRUD operations
from flask import Blueprint, render_template, request, redirect, url_for, flash

from utils.supabase_utils import get_supabase_client, get_admin_client
from utils.validators import safe_float
from utils.constants import ITEMS_PER_PAGE
from blueprints.helpers import get_user_id, is_admin, registrar_historico

elemento_bp = Blueprint('elemento', __name__)


@elemento_bp.route("/elementos", methods=["GET", "POST"])
def list():
    user_id = get_user_id()
    admin = is_admin()
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "create":
            nome = request.form.get("nome").strip().title()
            consumo_lpm = request.form.get("consumo_lpm")
            
            if not nome or not consumo_lpm:
                flash("Nome e consumo são obrigatórios", "danger")
                return redirect(url_for("elemento.list"))
            
            existing = get_supabase_client().table("elemento").select("id").eq("nome", nome).execute()
            if existing.data:
                if admin:
                    flash(f"Elemento '{nome}' já existe no sistema", "danger")
                else:
                    flash("Elemento com este nome já existe para este usuário", "danger")
                return redirect(url_for("elemento.list"))
            
            data = {
                "nome": nome,
                "consumo_lpm": safe_float(consumo_lpm, 0),
                "user_id": user_id
            }
            
            if admin:
                client = get_admin_client()
            else:
                client = get_supabase_client()
            
            client.table("elemento").insert(data).execute()
            registrar_historico("elemento", "criado", nome, user_id)
            flash("Elemento criado com sucesso!", "success")
            
        elif action == "update":
            elemento_id = request.form.get("elemento_id")
            nome = request.form.get("nome").strip().title()
            consumo_lpm = request.form.get("consumo_lpm")
            
            if not elemento_id or not nome or not consumo_lpm:
                flash("ID do elemento, nome e consumo são obrigatórios", "danger")
                return redirect(url_for("elemento.list"))
            
            if not admin:
                existing = get_supabase_client().table("elemento").select("id").eq("user_id", user_id).eq("nome", nome).neq("id", elemento_id).execute()
                if existing.data:
                    flash("Elemento com este nome já existe para este usuário", "danger")
                    return redirect(url_for("elemento.list"))
            
            data = {
                "nome": nome,
                "consumo_lpm": float(consumo_lpm) if consumo_lpm else 0
            }
            
            if not admin:
                get_supabase_client().table("elemento").update(data).eq("id", elemento_id).eq("user_id", user_id).execute()
            else:
                get_supabase_client().table("elemento").update(data).eq("id", elemento_id).execute()
            
            registrar_historico("elemento", "atualizado", nome, user_id)
            flash("Elemento atualizado com sucesso!", "success")
            
        elif action == "delete":
            elemento_id = request.form.get("elemento_id")
            
            if not elemento_id:
                flash("ID do elemento é obrigatório", "danger")
                return redirect(url_for("elemento.list"))
            
            amostra_count = get_supabase_client().table("amostra").select("id", count="exact").eq("elemento_id", elemento_id).execute()
            if amostra_count.count and amostra_count.count > 0:
                flash("Não é possível excluir este elemento pois existem amostras vinculadas a ele", "danger")
                return redirect(url_for("elemento.list"))
            
            try:
                elemento_info = get_supabase_client().table("elemento").select("nome").eq("id", elemento_id).execute().data
                elemento_nome = elemento_info[0].get("nome") if elemento_info else "N/A"
                
                if not admin:
                    get_supabase_client().table("elemento").delete().eq("id", elemento_id).eq("user_id", user_id).execute()
                else:
                    get_supabase_client().table("elemento").delete().eq("id", elemento_id).execute()
                
                registrar_historico("elemento", "excluido", elemento_nome, user_id)
                flash("Elemento excluído com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao excluir elemento: {str(e)}", "danger")
    
    response = get_supabase_client().table("elemento").select("*").order("created_at", desc=True).execute()
    elementos = response.data or []
    
    total = len(elementos)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = elementos[start:end]
    
    elementos = paginated_data
    
    pages = (total + per_page - 1) // per_page
    
    return render_template("elemento.html", elementos=elementos, page=page, per_page=per_page, total=total if 'pages' in locals() else None, pages=pages if 'pages' in locals() else None)
