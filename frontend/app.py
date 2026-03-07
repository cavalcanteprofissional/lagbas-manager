import os
from datetime import timedelta
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_login import LoginManager, login_required, current_user
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from supabase import create_client, Client

from blueprints.helpers import get_authenticated_client

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise ValueError("SECRET_KEY é obrigatória para produção")

csrf = CSRFProtect(app)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv("REDIS_URL", "memory://")
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórios")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

from blueprints.auth import User

@login_manager.user_loader
def load_user(user_id):
    user_data = session.get("user_data")
    if user_data:
        return User(user_id, user_data.get("email"), user_data)
    return None


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.context_processor
def inject_user_info():
    from blueprints.helpers import is_admin, get_user_role, get_user_name
    return dict(is_admin=is_admin(), user_role=get_user_role(), user_name=get_user_name())


@app.template_filter("formatar_data")
def formatar_data(data):
    if not data:
        return "-"
    if isinstance(data, str):
        if "T" in data:
            data = data.split("T")[0]
        try:
            from datetime import datetime
            dt = datetime.strptime(data, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            return data
    return data


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("auth.login"))


@app.route("/dashboard")
@login_required
def dashboard():
    from utils.supabase_utils import get_supabase_client
    from blueprints.helpers import get_user_id
    
    user_id = get_user_id()
    supabase = get_supabase_client()
    
    cilindro_response = supabase.table("cilindro").select("*").eq("user_id", user_id).execute()
    elementos_response = supabase.table("elemento").select("*").eq("user_id", user_id).execute()
    amostras_response = supabase.table("amostra").select("*").eq("user_id", user_id).execute()

    cilindro = cilindro_response.data or []
    elementos = elementos_response.data or []
    amostras = amostras_response.data or []

    ativos = len([c for c in cilindro if c.get("status") == "ativo"])

    # Status counts (para compatibilidadde)
    status_counts = {}
    for c in cilindro:
        status = c.get("status", "desconhecido")
        status_counts[status] = status_counts.get(status, 0) + 1

    status_labels = list(status_counts.keys())
    status_values = list(status_counts.values())

    # Quantidade de amostras por cilindro (novo card)
    cilindro_amostras = {}
    for a in amostras:
        cil_id = a.get("cilindro_id")
        if cil_id:
            cilindro_amostras[cil_id] = cilindro_amostras.get(cil_id, 0) + 1

    cilindro_amostras_labels = []
    cilindro_amostras_values = []
    cilindro_dict = {c.get("id"): c.get("codigo") for c in cilindro}
    for cil_id, count in sorted(cilindro_amostras.items(), key=lambda x: x[1], reverse=True):
        cilindro_amostras_labels.append(cilindro_dict.get(cil_id, str(cil_id)))
        cilindro_amostras_values.append(count)

    # TOP 3 Elementos Mais Analisados
    elemento_amostras_count = {}
    for a in amostras:
        elem_id = a.get("elemento_id")
        if elem_id:
            elemento_amostras_count[elem_id] = elemento_amostras_count.get(elem_id, 0) + 1

    elemento_dict = {e.get("id"): e.get("nome") for e in elementos}
    elementos_mais_analisados = []
    for elem_id, count in sorted(elemento_amostras_count.items(), key=lambda x: x[1], reverse=True):
        elementos_mais_analisados.append({
            "nome": elemento_dict.get(elem_id, str(elem_id)),
            "quantidade": count
        })

    # Tempo de chama por elemento (para consumo × tempo)
    tempo_chama_elementos = {}
    for a in amostras:
        elem_id = a.get("elemento_id")
        tempo = a.get("tempo_chama", "00:00:00")
        if elem_id and tempo:
            try:
                partes = tempo.split(":")
                minutos = int(partes[0]) * 60 + int(partes[1]) + int(partes[2])/60
                tempo_chama_elementos[elem_id] = tempo_chama_elementos.get(elem_id, 0) + minutos
            except:
                pass

    # Consumo por Elemento × Tempo de Chama
    elementos_labels = []
    elementos_consumo_tempo = []
    for e in elementos:
        eid = e.get("id")
        consumo = float(e.get("consumo_lpm", 0))
        tempo = tempo_chama_elementos.get(eid, 0)
        elementos_labels.append(e.get("nome"))
        elementos_consumo_tempo.append(round(consumo * tempo, 2))

    # Eficiência de Cilindros por Elemento (matriz)
    eficiencia = {}
    for a in amostras:
        cil_id = a.get("cilindro_id")
        elem_id = a.get("elemento_id")
        if cil_id and elem_id:
            key = f"{cil_id}-{elem_id}"
            eficiencia[key] = eficiencia.get(key, 0) + 1

    eficiencia_labels = []
    eficiencia_values = []
    for key, count in sorted(eficiencia.items(), key=lambda x: x[1], reverse=True)[:10]:
        cil_id, elem_id = key.split("-")
        nome_cil = cilindro_dict.get(cil_id, str(cil_id))
        nome_elem = elemento_dict.get(elem_id, str(elem_id))
        eficiencia_labels.append(f"{nome_cil} × {nome_elem}")
        eficiencia_values.append(count)

    return render_template(
        "dashboard.html",
        cilindro=cilindro,
        elementos=elementos,
        amostras=amostras,
        ativos=ativos,
        status_counts=status_counts,
        status_labels=status_labels,
        status_values=status_values,
        cilindro_amostras_labels=cilindro_amostras_labels,
        cilindro_amostras_values=cilindro_amostras_values,
        elementos_mais_analisados=elementos_mais_analisados,
        elementos_labels=elementos_labels,
        elementos_consumo_tempo=elementos_consumo_tempo,
        eficiencia_labels=eficiencia_labels,
        eficiencia_values=eficiencia_values,
    )


@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    from blueprints.helpers import get_user_id, get_authenticated_client
    
    user_id = get_user_id()
    supabase = get_authenticated_client()

    perfil_response = supabase.table("perfil").select("*").eq("id", user_id).execute()
    perfil_data = perfil_response.data[0] if perfil_response.data else {}
    user_role = perfil_data.get("role", "usuario")
    user_nome = perfil_data.get("nome", "")

    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "update_profile":
            nome = request.form.get("nome", "").strip()
            
            try:
                perfil_check = supabase.table("perfil").select("id").eq("id", user_id).execute()
                
                if not perfil_check.data:
                    supabase.table("perfil").insert({
                        "id": user_id,
                        "role": "usuario",
                        "ativo": True,
                        "nome": nome,
                        "email": current_user.email
                    }).execute()
                    flash("Perfil criado com sucesso!", "success")
                else:
                    supabase.table("perfil").update({"nome": nome}).eq("id", user_id).execute()
                    flash("Perfil atualizado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao atualizar perfil: {str(e)}", "danger")
            
            return redirect(url_for("perfil"))

    cilindro_response = supabase.table("cilindro").select("id").eq("user_id", user_id).execute()
    elementos_response = supabase.table("elemento").select("id").eq("user_id", user_id).execute()
    amostras_response = supabase.table("amostra").select("id").eq("user_id", user_id).execute()

    stats = {
        "cilindros": len(cilindro_response.data or []),
        "elementos": len(elementos_response.data or []),
        "amostras": len(amostras_response.data or []),
    }

    return render_template("perfil.html", stats=stats, user_role=user_role, user_nome=user_nome)


from blueprints.auth import auth_bp
from blueprints.cilindro import cilindro_bp
from blueprints.elemento import elemento_bp
from blueprints.amostra import amostra_bp
from blueprints.admin import admin_bp
from blueprints.historico import historico_bp

app.register_blueprint(auth_bp)
app.register_blueprint(cilindro_bp)
app.register_blueprint(elemento_bp)
app.register_blueprint(amostra_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(historico_bp)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
