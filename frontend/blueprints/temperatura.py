# Temperatura blueprint - CRUD operations
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash

from utils.supabase_utils import get_supabase_client, get_admin_client
from utils.validators import safe_float
from utils.constants import ITEMS_PER_PAGE
from utils.erros_utils import formatar_erro_supabase
from blueprints.helpers import get_user_id, is_admin, registrar_historico, pode_acessar_aba, get_authenticated_client

temperatura_bp = Blueprint('temperatura', __name__)


@temperatura_bp.route("/temperaturas", methods=["GET", "POST"])
def temperatura_list():
    if not pode_acessar_aba("temperatura"):
        flash("Você não tem permissão para acessar esta aba.", "warning")
        return redirect(url_for("dashboard"))
    
    user_id = get_user_id()
    admin = is_admin()
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "create":
            cilindro_id = request.form.get("cilindro_id", "").strip()
            temperatura = request.form.get("temperatura", "").strip()
            data = request.form.get("data", "").strip()
            hora = request.form.get("hora", "").strip()
            
            if not cilindro_id or not temperatura or not data or not hora:
                flash("Cilindro, temperatura, data e hora são obrigatórios", "danger")
                return redirect(url_for("temperatura.temperatura_list"))
            
            try:
                temp_val = safe_float(temperatura, 25.0)
                if temp_val < -50 or temp_val > 100:
                    flash("Temperatura deve estar entre -50°C e 100°C", "danger")
                    return redirect(url_for("temperatura.temperatura_list"))
            except ValueError as e:
                flash(f"Temperatura inválida: {str(e)}", "danger")
                return redirect(url_for("temperatura.temperatura_list"))
            
            try:
                datetime.strptime(data, "%Y-%m-%d")
            except ValueError:
                flash("Data inválida", "danger")
                return redirect(url_for("temperatura.temperatura_list"))
            
            try:
                datetime.strptime(hora, "%H:%M")
            except ValueError:
                flash("Hora inválida", "danger")
                return redirect(url_for("temperatura.temperatura_list"))
            
            try:
                cilindro_check = get_admin_client().table("cilindro").select("codigo").eq("id", cilindro_id).execute()
                if not cilindro_check.data:
                    flash("Cilindro não encontrado", "danger")
                    return redirect(url_for("temperatura.temperatura_list"))
                cilindro_codigo = cilindro_check.data[0].get("codigo")
            except Exception as e:
                flash(f"Erro ao buscar cilindro: {str(e)}", "danger")
                return redirect(url_for("temperatura.temperatura_list"))
            
            try:
                data_insert = {
                    "cilindro_id": int(cilindro_id),
                    "temperatura": temp_val,
                    "data": data,
                    "hora": hora,
                    "user_id": user_id
                }
                
                if admin:
                    client = get_admin_client()
                else:
                    client = get_authenticated_client()
                
                client.table("temperatura").insert(data_insert).execute()
                registrar_historico("temperatura", "criado", f"{cilindro_codigo} - {temp_val}°C", user_id)
                flash("Temperatura registrada com sucesso!", "success")
            except Exception as e:
                error_str = str(e)
                flash(formatar_erro_supabase(error_str, "registrar temperatura"), "danger")
            
        elif action == "update":
            temperatura_id = request.form.get("temperatura_id", "").strip()
            cilindro_id = request.form.get("cilindro_id", "").strip()
            temperatura = request.form.get("temperatura", "").strip()
            data = request.form.get("data", "").strip()
            hora = request.form.get("hora", "").strip()
            
            if not temperatura_id or not cilindro_id or not temperatura or not data or not hora:
                flash("ID, cilindro, temperatura, data e hora são obrigatórios", "danger")
                return redirect(url_for("temperatura.temperatura_list"))
            
            try:
                temp_val = safe_float(temperatura, 25.0)
                if temp_val < -50 or temp_val > 100:
                    flash("Temperatura deve estar entre -50°C e 100°C", "danger")
                    return redirect(url_for("temperatura.temperatura_list"))
            except ValueError as e:
                flash(f"Temperatura inválida: {str(e)}", "danger")
                return redirect(url_for("temperatura.temperatura_list"))
            
            try:
                cilindro_check = get_admin_client().table("cilindro").select("codigo").eq("id", cilindro_id).execute()
                if not cilindro_check.data:
                    flash("Cilindro não encontrado", "danger")
                    return redirect(url_for("temperatura.temperatura_list"))
                cilindro_codigo = cilindro_check.data[0].get("codigo")
            except Exception as e:
                flash(f"Erro ao buscar cilindro: {str(e)}", "danger")
                return redirect(url_for("temperatura.temperatura_list"))
            
            try:
                data_update = {
                    "cilindro_id": int(cilindro_id),
                    "temperatura": temp_val,
                    "data": data,
                    "hora": hora
                }
                
                if not admin:
                    get_supabase_client().table("temperatura").update(data_update).eq("id", temperatura_id).eq("user_id", user_id).execute()
                else:
                    get_supabase_client().table("temperatura").update(data_update).eq("id", temperatura_id).execute()
                
                registrar_historico("temperatura", "atualizado", f"{cilindro_codigo} - {temp_val}°C", user_id)
                flash("Temperatura atualizada com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao atualizar temperatura: {str(e)}", "danger")
            
        elif action == "delete":
            temperatura_id = request.form.get("temperatura_id", "").strip()
            
            if not temperatura_id:
                flash("ID da temperatura é obrigatório", "danger")
                return redirect(url_for("temperatura.temperatura_list"))
            
            try:
                temp_info = get_supabase_client().table("temperatura").select("cilindro_id,temperatura,user_id").eq("id", temperatura_id).execute().data
                if not temp_info:
                    flash("Registro de temperatura não encontrado", "danger")
                    return redirect(url_for("temperatura.temperatura_list"))
                
                if not admin and temp_info[0].get("user_id") != user_id:
                    flash("Você não tem permissão para excluir este registro.", "danger")
                    return redirect(url_for("temperatura.temperatura_list"))
                
                cilindro_id = temp_info[0].get("cilindro_id")
                temp_val = temp_info[0].get("temperatura")
                
                cilindro_info = get_supabase_client().table("cilindro").select("codigo").eq("id", cilindro_id).execute().data
                cilindro_codigo = cilindro_info[0].get("codigo") if cilindro_info else str(cilindro_id)
                
                get_admin_client().table("temperatura").delete().eq("id", temperatura_id).execute()
                
                registrar_historico("temperatura", "excluido", f"{cilindro_codigo} - {temp_val}°C", user_id)
                flash("Registro de temperatura excluído com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao excluir temperatura: {str(e)}", "danger")
            
            return redirect(url_for("temperatura.temperatura_list"))
        
        elif action == "delete_multiple":
            temperatura_ids = request.form.getlist("temperatura_ids")
            
            if not temperatura_ids:
                flash("Nenhum registro selecionado", "danger")
                return redirect(url_for("temperatura.temperatura_list"))
            
            try:
                deleted_count = 0
                not_owned = []
                
                for temp_id in temperatura_ids:
                    try:
                        temp_info = get_supabase_client().table("temperatura").select("cilindro_id,temperatura,user_id").eq("id", temp_id).execute().data
                        if not temp_info:
                            continue
                        
                        if not admin and temp_info[0].get("user_id") != user_id:
                            not_owned.append(temp_id)
                            continue
                        
                        cilindro_id = temp_info[0].get("cilindro_id")
                        temp_val = temp_info[0].get("temperatura")
                        
                        cilindro_info = get_supabase_client().table("cilindro").select("codigo").eq("id", cilindro_id).execute().data
                        cilindro_codigo = cilindro_info[0].get("codigo") if cilindro_info else str(cilindro_id)
                        
                        get_admin_client().table("temperatura").delete().eq("id", temp_id).execute()
                        
                        registrar_historico("temperatura", "excluido", f"{cilindro_codigo} - {temp_val}°C", user_id)
                        deleted_count += 1
                    except Exception:
                        continue
                
                if deleted_count > 0:
                    flash(f"{deleted_count} registro(s) excluído(s) com sucesso!", "success")
                if not_owned:
                    flash(f"Alguns registros não foram excluídos (não pertencem a você): {', '.join(not_owned)}", "warning")
            except Exception as e:
                flash(f"Erro ao excluir registros: {str(e)}", "danger")
            
            return redirect(url_for("temperatura.temperatura_list"))
    
    response = get_supabase_client().table("temperatura").select("*").order("created_at", desc=True).execute()
    temperaturas = response.data or []
    
    cilindro_ids = list(set(t.get("cilindro_id") for t in temperaturas if t.get("cilindro_id")))
    cilindro_dict = {}
    if cilindro_ids:
        cilindro_response = get_admin_client().table("cilindro").select("id,codigo").in_("id", cilindro_ids).execute()
        cilindro_dict = {c.get("id"): c.get("codigo") for c in (cilindro_response.data or [])}
    
    for t in temperaturas:
        t["cilindro_codigo"] = cilindro_dict.get(t.get("cilindro_id"), "")
    
    total = len(temperaturas)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = temperaturas[start:end]
    
    temperaturas = paginated_data
    
    cilindro_list_response = get_authenticated_client().table("cilindro").select("id,codigo").eq("user_id", user_id).order("codigo").execute()
    cilindro_list = cilindro_list_response.data or []
    
    pages = (total + per_page - 1) // per_page if total > 0 else 1
    end_page = min(page * per_page, total) if total > 0 else 0
    max_pages = min(pages, 10)
        
    return render_template(
        "temperatura.html", 
        temperaturas=temperaturas, 
        cilindro_list=cilindro_list,
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        end=end_page,
        max_pages=max_pages
    )