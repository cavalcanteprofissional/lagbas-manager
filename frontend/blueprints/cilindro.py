# Cilindro blueprint - CRUD operations
import re
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from utils.supabase_utils import get_supabase_client, get_admin_client
from utils.validators import safe_float
from utils.constants import ITEMS_PER_PAGE, LITROS_EQUIVALENTES_KG, GAS_KG_DEFAULT, CUSTO_DEFAULT, CILINDRO_STATUS
from blueprints.helpers import get_user_id, is_admin, registrar_historico

cilindro_bp = Blueprint('cilindro', __name__)


@cilindro_bp.route("/cilindros", methods=["GET", "POST"])
def list():
    user_id = get_user_id()
    admin = is_admin()
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "create":
            codigo = request.form.get("codigo", "").strip()
            data_compra = request.form.get("data_compra", "").strip()
            gas_kg = request.form.get("gas_kg", "")
            custo = request.form.get("custo", "")
            status = request.form.get("status", "ativo")
            
            if not codigo or not data_compra:
                flash("Código e data de compra são obrigatórios", "danger")
                return redirect(url_for("cilindro.list"))
            
            if not re.match(r'^CIL-\d{3}$', codigo):
                flash("Código deve seguir o formato CIL-XXX (ex: CIL-001, CIL-002)", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                datetime.strptime(data_compra, "%Y-%m-%d")
            except ValueError:
                flash("Data de compra inválida", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                gas_kg_val = safe_float(gas_kg, GAS_KG_DEFAULT)
                custo_val = safe_float(custo, CUSTO_DEFAULT)
                if gas_kg_val < 0 or custo_val < 0:
                    raise ValueError("Valores não podem ser negativos")
            except ValueError as e:
                flash(f"Valores inválidos: {str(e)}", "danger")
                return redirect(url_for("cilindro.list"))
            
            if not admin:
                try:
                    existing = get_admin_client().table("cilindro").select("id").eq("user_id", user_id).eq("codigo", codigo).execute()
                    if existing.data:
                        flash("Código já existe para este usuário", "danger")
                        return redirect(url_for("cilindro.list"))
                except Exception as e:
                    flash(f"Erro ao verificar código: {str(e)}", "danger")
                    return redirect(url_for("cilindro.list"))
            
            try:
                data = {
                    "codigo": codigo,
                    "data_compra": data_compra,
                    "gas_kg": gas_kg_val,
                    "litros_equivalentes": gas_kg_val * LITROS_EQUIVALENTES_KG,
                    "custo": custo_val,
                    "status": status,
                    "user_id": user_id
                }
                
                if admin:
                    client = get_admin_client()
                else:
                    client = get_supabase_client()
                
                client.table("cilindro").insert(data).execute()
                registrar_historico("cilindro", "criado", codigo, user_id)
                flash("Cilindro criado com sucesso!", "success")
            except Exception as e:
                error_str = str(e)
                if "23505" in error_str or "duplicate key" in error_str.lower():
                    flash("Código já existe. Por favor, utilize outro código.", "danger")
                else:
                    flash(f"Erro ao criar cilindro: {error_str}", "danger")
            
        elif action == "update":
            cilindro_id = request.form.get("cilindro_id", "").strip()
            codigo = request.form.get("codigo", "").strip()
            data_compra = request.form.get("data_compra", "").strip()
            data_inicio_consumo = request.form.get("data_inicio_consumo", "").strip()
            data_fim = request.form.get("data_fim", "").strip()
            gas_kg = request.form.get("gas_kg", "")
            custo = request.form.get("custo", "")
            status = request.form.get("status", "ativo")
            
            if not cilindro_id or not codigo or not data_compra:
                flash("ID do cilindro, código e data de compra são obrigatórios", "danger")
                return redirect(url_for("cilindro.list"))
            
            if not re.match(r'^CIL-\d{3}$', codigo):
                flash("Código deve seguir o formato CIL-XXX (ex: CIL-001, CIL-002)", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                gas_kg_val = safe_float(gas_kg, GAS_KG_DEFAULT)
                custo_val = safe_float(custo, CUSTO_DEFAULT)
                if gas_kg_val < 0 or custo_val < 0:
                    raise ValueError("Valores não podem ser negativos")
            except ValueError as e:
                flash(f"Valores inválidos: {str(e)}", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                if not admin:
                    existing = get_admin_client().table("cilindro").select("id").eq("user_id", user_id).eq("codigo", codigo).neq("id", cilindro_id).execute()
                    if existing.data:
                        flash("Código já existe para este usuário", "danger")
                        return redirect(url_for("cilindro.list"))
            except Exception as e:
                flash(f"Erro ao verificar código: {str(e)}", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                data = {
                    "codigo": codigo,
                    "data_compra": data_compra,
                    "data_inicio_consumo": data_inicio_consumo or None,
                    "data_fim": data_fim or None,
                    "gas_kg": gas_kg_val,
                    "litros_equivalentes": gas_kg_val * LITROS_EQUIVALENTES_KG,
                    "custo": custo_val,
                    "status": status
                }
                
                if not admin:
                    get_supabase_client().table("cilindro").update(data).eq("id", cilindro_id).eq("user_id", user_id).execute()
                else:
                    get_supabase_client().table("cilindro").update(data).eq("id", cilindro_id).execute()
                
                registrar_historico("cilindro", "atualizado", codigo, user_id)
                flash("Cilindro atualizado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao atualizar cilindro: {str(e)}", "danger")
            
        elif action == "delete":
            cilindro_id = request.form.get("cilindro_id", "").strip()
            
            if not cilindro_id:
                abort(400, description="ID do cilindro é obrigatório")
            
            try:
                amostra_count = get_supabase_client().table("amostra").select("id", count="exact").eq("cilindro_id", cilindro_id).execute()
                if amostra_count.count and amostra_count.count > 0:
                    flash("Não é possível excluir este cilindro pois existem amostras vinculadas a ele. Exclua primeiro as amostras.", "warning")
                    return redirect(url_for("cilindro.list"))
                
                cilindro_info = get_supabase_client().table("cilindro").select("codigo").eq("id", cilindro_id).execute().data
                cilindro_codigo = cilindro_info[0].get("codigo") if cilindro_info else "N/A"
                
                get_admin_client().table("cilindro").delete().eq("id", cilindro_id).execute()
                
                registrar_historico("cilindro", "excluido", cilindro_codigo, user_id)
                flash("Cilindro excluído com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao excluir cilindro: {str(e)}", "danger")
            
            return redirect(url_for("cilindro.list"))
        
        elif action == "delete_multiple":
            cilindro_ids = request.form.getlist("cilindro_ids")
            
            if not cilindro_ids:
                flash("Nenhum cilindro selecionado", "danger")
                return redirect(url_for("cilindro.list"))
            
            try:
                deleted_count = 0
                skipped = []
                
                for cilindro_id in cilindro_ids:
                    try:
                        amostra_count = get_supabase_client().table("amostra").select("id", count="exact").eq("cilindro_id", cilindro_id).execute()
                        if amostra_count.count and amostra_count.count > 0:
                            cilindro_info = get_supabase_client().table("cilindro").select("codigo").eq("id", cilindro_id).execute().data
                            skipped.append(cilindro_info[0].get("codigo") if cilindro_info else cilindro_id)
                            continue
                        
                        cilindro_info = get_supabase_client().table("cilindro").select("codigo").eq("id", cilindro_id).execute().data
                        cilindro_codigo = cilindro_info[0].get("codigo") if cilindro_info else "N/A"
                        
                        get_admin_client().table("cilindro").delete().eq("id", cilindro_id).execute()
                        
                        registrar_historico("cilindro", "excluido", cilindro_codigo, user_id)
                        deleted_count += 1
                    except Exception:
                        continue
                
                if deleted_count > 0:
                    flash(f"{deleted_count} cilindro(s) excluído(s) com sucesso!", "success")
                if skipped:
                    flash(f"Alguns cilindos não puderam ser excluídos (amostras vinculadas): {', '.join(skipped)}", "warning")
            except Exception as e:
                flash(f"Erro ao excluir cilindos: {str(e)}", "danger")
            
            return redirect(url_for("cilindro.list"))
    
    response = get_supabase_client().table("cilindro").select("*").order("created_at", desc=True).execute()
    cilindro = response.data or []
    
    total = len(cilindro)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = cilindro[start:end]
    
    cilindro = paginated_data
    
    pages = (total + per_page - 1) // per_page
    end = min(page * per_page, total)
    max_pages = min(pages, 10)
        
    return render_template(
        "cilindro.html", 
        cilindro=cilindro, 
        status_options=CILINDRO_STATUS,
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        end=end,
        max_pages=max_pages
    )
