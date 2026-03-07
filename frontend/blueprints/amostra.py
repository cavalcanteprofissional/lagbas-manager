# Amostra blueprint - CRUD operations
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from utils.supabase_utils import get_supabase_client, get_admin_client
from utils.validators import safe_int, formatar_tempo_chama
from utils.constants import ITEMS_PER_PAGE
from blueprints.helpers import get_user_id, is_admin, registrar_historico, pode_acessar_aba

amostra_bp = Blueprint('amostra', __name__)


@amostra_bp.route("/amostras", methods=["GET", "POST"])
def list():
    if not pode_acessar_aba("amostra"):
        flash("Você não tem permissão para acessar esta aba.", "warning")
        from flask import current_app
        return redirect(current_app.config.get("LOGIN_VIEW", "/dashboard"))
    
    user_id = get_user_id()
    admin = is_admin()
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)
    
    cilindro_response = get_supabase_client().table("cilindro").select("id,codigo").order("codigo").execute()
    elementos_response = get_supabase_client().table("elemento").select("id,nome").order("nome").execute()
    
    cilindro = cilindro_response.data or []
    elementos = elementos_response.data or []
    
    elementos_unicos = []
    nomes_vistos = set()
    for e in elementos:
        nome = e.get("nome", "").lower()
        if nome not in nomes_vistos:
            nomes_vistos.add(nome)
            elementos_unicos.append(e)
    elementos = elementos_unicos
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "create":
            data_amostra = request.form.get("data")
            hora = request.form.get("hora", "00")
            minuto = request.form.get("minuto", "00")
            segundo = request.form.get("segundo", "00")
            cilindro_id = request.form.get("cilindro_id")
            elemento_id = request.form.get("elemento_id")
            quantidade = request.form.get("quantidade_amostras", 1)
            
            if not data_amostra or not cilindro_id or not elemento_id:
                flash("Data, cilindro e elemento são obrigatórios", "danger")
                return redirect(url_for("amostra.list"))
            
            tempo_chama = formatar_tempo_chama(hora, minuto, segundo)
            
            cilindro_id_val = safe_int(cilindro_id)
            elemento_id_val = safe_int(elemento_id)
            quantidade_val = safe_int(quantidade, 1)
            
            if cilindro_id_val is None or elemento_id_val is None:
                flash("Cilindro e elemento são obrigatórios", "danger")
                return redirect(url_for("amostra.list"))
            
            data = {
                "data": data_amostra,
                "tempo_chama": tempo_chama,
                "cilindro_id": cilindro_id_val,
                "elemento_id": elemento_id_val,
                "quantidade_amostras": quantidade_val,
                "user_id": user_id
            }
            
            if admin:
                client = get_admin_client()
            else:
                client = get_supabase_client()
            
            try:
                client.table("amostra").insert(data).execute()
                
                cilindro_nome = get_supabase_client().table("cilindro").select("codigo").eq("id", cilindro_id).execute().data
                elemento_nome = get_supabase_client().table("elemento").select("nome").eq("id", elemento_id).execute().data
                nome_amostra = f"{cilindro_nome[0]['codigo'] if cilindro_nome else 'N/A'} - {elemento_nome[0]['nome'] if elemento_nome else 'N/A'}"
                registrar_historico("amostra", "criado", nome_amostra, user_id)
                flash("Amostra criada com sucesso!", "success")
            except Exception as e:
                error_str = str(e)
                if "23505" in error_str or "duplicate key" in error_str.lower():
                    flash("Amostra duplicada. Os dados informados já existem.", "danger")
                else:
                    flash(f"Erro ao criar amostra: {error_str}", "danger")
            
        elif action == "update":
            amostra_id = request.form.get("amostra_id")
            data_amostra = request.form.get("data")
            hora = request.form.get("hora", "00")
            minuto = request.form.get("minuto", "00")
            segundo = request.form.get("segundo", "00")
            cilindro_id = request.form.get("cilindro_id")
            elemento_id = request.form.get("elemento_id")
            quantidade = request.form.get("quantidade_amostras", 1)
            
            if not amostra_id or not data_amostra or not cilindro_id or not elemento_id:
                flash("ID da amostra, data, cilindro e elemento são obrigatórios", "danger")
                return redirect(url_for("amostra.list"))
            
            tempo_chama = formatar_tempo_chama(hora, minuto, segundo)
            cilindro_id_val = safe_int(cilindro_id)
            elemento_id_val = safe_int(elemento_id)
            quantidade_val = safe_int(quantidade, 1)
            
            data = {
                "data": data_amostra,
                "tempo_chama": tempo_chama,
                "cilindro_id": cilindro_id_val,
                "elemento_id": elemento_id_val,
                "quantidade_amostras": quantidade_val
            }
            
            if not admin:
                get_supabase_client().table("amostra").update(data).eq("id", amostra_id).eq("user_id", user_id).execute()
            else:
                get_supabase_client().table("amostra").update(data).eq("id", amostra_id).execute()
            
            amostra_info = get_supabase_client().table("amostra").select("cilindro_id,elemento_id").eq("id", amostra_id).execute().data
            nome_amostra = "N/A"
            if amostra_info:
                cilindro_nome = get_supabase_client().table("cilindro").select("codigo").eq("id", amostra_info[0]["cilindro_id"]).execute().data
                elemento_nome = get_supabase_client().table("elemento").select("nome").eq("id", amostra_info[0]["elemento_id"]).execute().data
                nome_amostra = f"{cilindro_nome[0]['codigo'] if cilindro_nome else 'N/A'} - {elemento_nome[0]['nome'] if elemento_nome else 'N/A'}"
            
            registrar_historico("amostra", "atualizado", nome_amostra, user_id)
            flash("Amostra atualizada com sucesso!", "success")
            
        elif action == "delete":
            amostra_id = request.form.get("amostra_id")
            
            if not amostra_id:
                flash("ID da amostra é obrigatório", "danger")
                return redirect(url_for("amostra.list"))
            
            try:
                amostra_info = get_supabase_client().table("amostra").select("cilindro_id,elemento_id,user_id").eq("id", amostra_id).execute().data
                if not amostra_info:
                    flash("Amostra não encontrada", "danger")
                    return redirect(url_for("amostra.list"))
                
                if amostra_info[0].get("user_id") != user_id:
                    flash("Você não tem permissão para excluir esta amostra.", "danger")
                    return redirect(url_for("amostra.list"))
                
                nome_amostra = "N/A"
                cilindro_nome = get_supabase_client().table("cilindro").select("codigo").eq("id", amostra_info[0]["cilindro_id"]).execute().data
                elemento_nome = get_supabase_client().table("elemento").select("nome").eq("id", amostra_info[0]["elemento_id"]).execute().data
                nome_amostra = f"{cilindro_nome[0]['codigo'] if cilindro_nome else 'N/A'} - {elemento_nome[0]['nome'] if elemento_nome else 'N/A'}"
                
                get_admin_client().table("amostra").delete().eq("id", amostra_id).execute()
                
                registrar_historico("amostra", "excluido", nome_amostra, user_id)
                flash("Amostra excluída com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao excluir amostra: {str(e)}", "danger")
            
            return redirect(url_for("amostra.list"))
        
        elif action == "delete_multiple":
            amostra_ids = request.form.getlist("amostra_ids")
            
            if not amostra_ids:
                flash("Nenhuma amostra selecionada", "danger")
                return redirect(url_for("amostra.list"))
            
            try:
                deleted_count = 0
                not_owned = []
                
                for amostra_id in amostra_ids:
                    try:
                        amostra_info = get_supabase_client().table("amostra").select("cilindro_id,elemento_id,user_id").eq("id", amostra_id).execute().data
                        if not amostra_info:
                            continue
                        
                        if amostra_info[0].get("user_id") != user_id:
                            not_owned.append(amostra_id)
                            continue
                        
                        nome_amostra = "N/A"
                        cilindro_nome = get_supabase_client().table("cilindro").select("codigo").eq("id", amostra_info[0]["cilindro_id"]).execute().data
                        elemento_nome = get_supabase_client().table("elemento").select("nome").eq("id", amostra_info[0]["elemento_id"]).execute().data
                        nome_amostra = f"{cilindro_nome[0]['codigo'] if cilindro_nome else 'N/A'} - {elemento_nome[0]['nome'] if elemento_nome else 'N/A'}"
                        
                        get_admin_client().table("amostra").delete().eq("id", amostra_id).execute()
                        
                        registrar_historico("amostra", "excluido", nome_amostra, user_id)
                        deleted_count += 1
                    except Exception:
                        continue
                
                if deleted_count > 0:
                    flash(f"{deleted_count} amostra(s) excluída(s) com sucesso!", "success")
                if not_owned:
                    flash(f"{len(not_owned)} amostra(s) não foram excluídas (não pertencem a você)", "warning")
            except Exception as e:
                flash(f"Erro ao excluir amostras: {str(e)}", "danger")
            
            return redirect(url_for("amostra.list"))
    
    response = get_supabase_client().table("amostra").select("*").order("data", desc=True).execute()
    amostras = response.data or []
    
    total = len(amostras)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = amostras[start:end]
    
    amostras = paginated_data
    
    pages = (total + per_page - 1) // per_page
    end = min(page * per_page, total)
    max_pages = min(pages, 10)
    
    for amostra in amostras:
        for c in cilindro:
            if c.get("id") == amostra.get("cilindro_id"):
                amostra["cilindro_nome"] = c.get("codigo")
                break
        for e in elementos:
            if e.get("id") == amostra.get("elemento_id"):
                amostra["elemento_nome"] = e.get("nome")
                break
    
    return render_template(
        "amostra.html", 
        amostras=amostras, 
        cilindro=cilindro, 
        elementos=elementos,
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        end=end,
        max_pages=max_pages
    )
