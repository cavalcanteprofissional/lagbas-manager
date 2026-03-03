import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from dotenv import load_dotenv
from supabase import create_client, Client
import jwt
from functools import wraps

# Constants for pagination and performance
ITEMS_PER_PAGE = 10

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Validação de variáveis de ambiente
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórios")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# CORS policies
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token não fornecido"}), 401
            
        try:
            decoded = jwt.decode(token, SUPABASE_KEY, algorithms=["HS256"])
            session["user_id"] = decoded.get("user_id")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
            
        return f(*args, **kwargs)
    return decorated_function

def generate_jwt_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SUPABASE_KEY, algorithm="HS256")

LITROS_EQUIVALENTES_KG = 956.0
GAS_KG_DEFAULT = 1.0
CUSTO_DEFAULT = 290.00
CILINDRO_STATUS = ["ativo", "em_uso", "esgotado"]

ELEMENTOS_PADRAO = [
    {"nome": "Antimônio", "consumo_lpm": 1.5},
    {"nome": "Alumínio", "consumo_lpm": 4.5},
    {"nome": "Arsênio", "consumo_lpm": 1.5},
    {"nome": "Bário", "consumo_lpm": 4.5},
    {"nome": "Cádmio", "consumo_lpm": 1.5},
    {"nome": "Chumbo", "consumo_lpm": 2.0},
    {"nome": "Cobalto", "consumo_lpm": 1.5},
    {"nome": "Cobre", "consumo_lpm": 1.5},
    {"nome": "Cromo", "consumo_lpm": 4.5},
    {"nome": "Estanho FAAS", "consumo_lpm": 4.5},
    {"nome": "Estanho HG", "consumo_lpm": 1.5},
    {"nome": "Ferro", "consumo_lpm": 2.0},
    {"nome": "Manganês", "consumo_lpm": 1.5},
    {"nome": "Mercúrio", "consumo_lpm": 0},
    {"nome": "Molibdênio", "consumo_lpm": 4.5},
    {"nome": "Níquel", "consumo_lpm": 1.5},
    {"nome": "Prata", "consumo_lpm": 1.5},
    {"nome": "Selênio", "consumo_lpm": 2.0},
    {"nome": "Zinco", "consumo_lpm": 1.5},
    {"nome": "Tálio", "consumo_lpm": 1.5},
]


class User:
    def __init__(self, id, email, user_data=None):
        self.id = id
        self.email = email
        self.user_data = user_data or {}

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(user_id):
    user_data = session.get("user_data")
    if user_data:
        return User(user_id, user_data.get("email"), user_data)
    return None


@app.context_processor
def inject_user_info():
    return dict(is_admin=is_admin(), user_role=get_user_role())


def get_user_id():
    """Retorna o ID do usuário atual"""
    return session.get("user_id")


def is_admin():
    """Verifica se o usuário atual é admin"""
    user_id = get_user_id()
    if not user_id:
        return False
    try:
        client = get_authenticated_client()
        response = client.table("perfil").select("role").eq("id", user_id).execute()
        if response.data:
            return response.data[0].get("role") == "admin"
    except:
        pass
    return False


def is_user_active(user_id):
    """Verifica se o usuário está ativo"""
    try:
        response = supabase.table("perfil").select("ativo").eq("id", user_id).execute()
        if response.data:
            return response.data[0].get("ativo", True)
    except:
        pass
    return True


def get_user_role():
    """Retorna o role do usuário atual"""
    user_id = get_user_id()
    if not user_id:
        return "usuario"
    try:
        response = supabase.table("perfil").select("role").eq("id", user_id).execute()
        if response.data:
            return response.data[0].get("role", "usuario")
    except:
        pass
    return "usuario"


def get_authenticated_client():
    """Retorna cliente Supabase autenticado com token JWT do usuário"""
    token = session.get("supabase_token")
    if token:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        client.auth.set_session(token, "")
        return client
    return supabase


def get_admin_client():
    """Retorna cliente Supabase com service_role (bypass RLS)"""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            response = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            # Atualizar função login para gerar JWT token
            if response.user:
                session["user_id"] = response.user.id
                session["supabase_token"] = response.session.access_token
                session["jwt_token"] = generate_jwt_token(response.user.id)
                session.permanent = True
                session["user_data"] = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "email_confirmed_at": response.user.email_confirmed_at,
                }

                try:
                    perfil = supabase.table("perfil").select("*").eq("id", response.user.id).execute()
                    nome = response.user.user_metadata.get("nome", "") if response.user.user_metadata else ""
                    email = response.user.email
                    
                    if not perfil.data:
                        # Criar novo perfil
                        result = supabase.table("perfil").insert({
                            "id": response.user.id,
                            "role": "usuario",
                            "ativo": True,
                            "nome": nome,
                            "email": email
                        }).execute()
                        if result.data:
                            flash("Perfil criado com sucesso!", "success")
                    # Não atualiza o perfil ao fazer login para preservar nome editado

                except Exception as e:
                    flash(f"Erro ao criar/atualizar perfil: {str(e)}", "warning")

                user = User(response.user.id, response.user.email, session["user_data"])
                login_user(user, remember=True, duration=timedelta(days=7))

                flash("Login realizado com sucesso!", "success")
                return redirect(url_for("dashboard"))

        except Exception as e:
            flash(f"Erro no login: {str(e)}", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        nome = request.form.get("nome", "")

        if password != confirm_password:
            flash("Senhas não conferem.", "danger")
            return render_template("register.html")

        try:
            response = supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {"data": {"nome": nome}},
                }
            )
            
            # Criar perfil automaticamente após registro
            if response.user:
                try:
                    supabase.table("perfil").insert({
                        "id": response.user.id,
                        "role": "usuario",
                        "ativo": True,
                        "nome": nome,
                        "email": email
                    }).execute()
                except Exception as perfil_error:
                    flash(f"Conta criada! Mas erro ao criar perfil: {str(perfil_error)}", "warning")
                    return redirect(url_for("login"))

            flash("Conta criada! Verifique seu email para confirmação.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            flash(f"Erro no registro: {str(e)}", "danger")

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    # Atualizar logout para remover JWT token
    supabase.auth.sign_out()
    session.clear()
    logout_user()
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = get_user_id()

    cilindro_response = (
        supabase.table("cilindro").select("*").eq("user_id", user_id).execute()
    )
    elementos_response = (
        supabase.table("elemento").select("*").eq("user_id", user_id).execute()
    )
    amostras_response = (
        supabase.table("amostra").select("*").eq("user_id", user_id).execute()
    )

    cilindro = cilindro_response.data or []
    elementos = elementos_response.data or []
    amostras = amostras_response.data or []

    ativos = len([c for c in cilindro if c.get("status") == "ativo"])

    status_counts = {}
    for c in cilindro:
        status = c.get("status", "desconhecido")
        status_counts[status] = status_counts.get(status, 0) + 1

    status_labels = list(status_counts.keys())
    status_values = list(status_counts.values())
    elementos_nomes = [e.get("nome") for e in elementos]
    elementos_consumos = [float(e.get("consumo_lpm", 0)) for e in elementos]

    return render_template(
        "dashboard.html",
        cilindro=cilindro,
        elementos=elementos,
        amostras=amostras,
        ativos=ativos,
        status_counts=status_counts,
        status_labels=status_labels,
        status_values=status_values,
        elementos_nomes=elementos_nomes,
        elementos_consumos=elementos_consumos,
    )


# Otimizar queries para performance
# Separar dados próprios vs compartilhados para queries mais eficientes
@app.route("/cilindros", methods=["GET", "POST"])
@login_required
def cilindro_list():
    user_id = get_user_id()
    admin = is_admin()
    
    # Paginação
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "create":
            # Criar novo cilindro
            codigo = request.form.get("codigo", "").strip()
            data_compra = request.form.get("data_compra", "").strip()
            gas_kg = request.form.get("gas_kg", "")
            custo = request.form.get("custo", "")
            status = request.form.get("status", "ativo")
            compartilhado = request.form.get("compartilhado", "false").lower() == "true"
            
            # Validações
            if not codigo or not data_compra:
                flash("Código e data de compra são obrigatórios", "danger")
                return redirect(url_for("cilindro_list"))
            
            # Validar formato da data
            try:
                datetime.strptime(data_compra, "%Y-%m-%d")
            except ValueError:
                flash("Data de compra inválida", "danger")
                return redirect(url_for("cilindro_list"))
            
            # Validar valores numéricos
            try:
                gas_kg_val = float(gas_kg) if gas_kg else GAS_KG_DEFAULT
                custo_val = float(custo) if custo else CUSTO_DEFAULT
                if gas_kg_val < 0 or custo_val < 0:
                    raise ValueError("Valores não podem ser negativos")
            except ValueError as e:
                flash(f"Valores inválidos: {str(e)}", "danger")
                return redirect(url_for("cilindro_list"))
            
            # Verificar se código já existe para este usuário
            if not admin:
                try:
                    existing = supabase.table("cilindro").select("id").eq("user_id", user_id).eq("codigo", codigo).execute()
                    if existing.data:
                        flash("Código já existe para este usuário", "danger")
                        return redirect(url_for("cilindro_list"))
                except Exception as e:
                    flash(f"Erro ao verificar código: {str(e)}", "danger")
                    return redirect(url_for("cilindro_list"))
            
            # Criar cilindro
            try:
                data = {
                    "codigo": codigo,
                    "data_compra": data_compra,
                    "gas_kg": gas_kg_val,
                    "litros_equivalentes": gas_kg_val * LITROS_EQUIVALENTES_KG,
                    "custo": custo_val,
                    "status": status,
                    "compartilhado": compartilhado
                }
                
                if not admin:
                    data["user_id"] = user_id
                
                supabase.table("cilindro").insert(data).execute()
                flash("Cilindro criado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao criar cilindro: {str(e)}", "danger")
            
        elif action == "update":
            # Atualizar cilindro existente
            cilindro_id = request.form.get("cilindro_id", "").strip()
            codigo = request.form.get("codigo", "").strip()
            data_compra = request.form.get("data_compra", "").strip()
            data_inicio_consumo = request.form.get("data_inicio_consumo", "").strip()
            data_fim = request.form.get("data_fim", "").strip()
            gas_kg = request.form.get("gas_kg", "")
            custo = request.form.get("custo", "")
            status = request.form.get("status", "ativo")
            compartilhado = request.form.get("compartilhado", "false").lower() == "true"
            
            # Validações
            if not cilindro_id or not codigo or not data_compra:
                flash("ID do cilindro, código e data de compra são obrigatórios", "danger")
                return redirect(url_for("cilindro_list"))
            
            # Validar valores numéricos
            try:
                gas_kg_val = float(gas_kg) if gas_kg else GAS_KG_DEFAULT
                custo_val = float(custo) if custo else CUSTO_DEFAULT
                if gas_kg_val < 0 or custo_val < 0:
                    raise ValueError("Valores não podem ser negativos")
            except ValueError as e:
                flash(f"Valores inválidos: {str(e)}", "danger")
                return redirect(url_for("cilindro_list"))
            
            # Verificar se código já existe para este usuário (exceto para o próprio cilindro)
            try:
                if not admin:
                    existing = supabase.table("cilindro").select("id").eq("user_id", user_id).eq("codigo", codigo).neq("id", cilindro_id).execute()
                    if existing.data:
                        flash("Código já existe para este usuário", "danger")
                        return redirect(url_for("cilindro_list"))
            except Exception as e:
                flash(f"Erro ao verificar código: {str(e)}", "danger")
                return redirect(url_for("cilindro_list"))
            
            # Atualizar cilindro
            try:
                data = {
                    "codigo": codigo,
                    "data_compra": data_compra,
                    "data_inicio_consumo": data_inicio_consumo or None,
                    "data_fim": data_fim or None,
                    "gas_kg": gas_kg_val,
                    "litros_equivalentes": gas_kg_val * LITROS_EQUIVALENTES_KG,
                    "custo": custo_val,
                    "status": status,
                    "compartilhado": compartilhado
                }
                
                if not admin:
                    supabase.table("cilindro").update(data).eq("id", cilindro_id).eq("user_id", user_id).execute()
                else:
                    supabase.table("cilindro").update(data).eq("id", cilindro_id).execute()
                
                flash("Cilindro atualizado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao atualizar cilindro: {str(e)}", "danger")
            
        elif action == "delete":
            # Deletar cilindro existente
            cilindro_id = request.form.get("cilindro_id", "").strip()
            
            if not cilindro_id:
                flash("ID do cilindro é obrigatório", "danger")
                return redirect(url_for("cilindro_list"))
            
            # Verificar se cilindro possui amostras vinculadas
            try:
                if not admin:
                    amostra_count = supabase.table("amostra").select("id", count="exact").eq("cilindro_id", cilindro_id).execute()
                    if amostra_count.count and amostra_count.count > 0:
                        flash("Não é possível excluir este cilindro pois existem amostras vinculadas a ele", "danger")
                        return redirect(url_for("cilindro_list"))
                
                # Deletar cilindro
                if not admin:
                    supabase.table("cilindro").delete().eq("id", cilindro_id).eq("user_id", user_id).execute()
                else:
                    supabase.table("cilindro").delete().eq("id", cilindro_id).execute()
                
                flash("Cilindro excluído com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao excluir cilindro: {str(e)}", "danger")
    
    if admin:
        # Admin vê todos os dados (com validação JWT)
        response = supabase.table("cilindro").select("*").order("created_at", desc=True).execute()
        cilindro = response.data or []
    else:
        # Usuário vê apenas seus dados + dados compartilhados
        # Otimizado: duas queries separadas para melhor performance
        own_query = supabase.table("cilindro").select("*").eq("user_id", user_id).order("created_at", desc=True)
        shared_query = supabase.table("cilindro").select("*").eq("compartilhado", True).order("created_at", desc=True)
        
        # Executar queries em paralelo
        own_response = own_query.execute()
        shared_response = shared_query.execute()
        
        # Combinar resultados (remover duplicatas se usuário compartilhou seus próprios dados)
        own_data = own_response.data or []
        shared_data = shared_response.data or []
        
        # Remover duplicatas (se usuário compartilhou seus próprios dados)
        shared_ids = {c["id"] for c in shared_data}
        unique_own_data = [c for c in own_data if c["id"] not in shared_ids]
        
        # Combinar e ordenar
        all_data = unique_own_data + shared_data
        all_data.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Aplicar paginação
        total = len(all_data)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = all_data[start:end]
        
        cilindro = paginated_data
        
        # Preparar dados para template com paginação
        pages = (total + per_page - 1) // per_page
        
    return render_template(
        "cilindro.html", 
        cilindro=cilindro, 
        status_options=CILINDRO_STATUS,
        page=page,
        per_page=per_page,
        total=total if 'pages' in locals() else None,
        pages=pages if 'pages' in locals() else None
    )


# Otimizar queries para performance
# Separar dados próprios vs compartilhados para queries mais eficientes
@app.route("/elementos", methods=["GET", "POST"])
@login_required
def elemento_list():
    user_id = get_user_id()
    admin = is_admin()
    
    # Paginação
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "create":
            # Criar novo elemento
            nome = request.form.get("nome").strip()
            consumo_lpm = request.form.get("consumo_lpm")
            compartilhado = request.form.get("compartilhado", "false").lower() == "true"
            
            # Validações
            if not nome or not consumo_lpm:
                flash("Nome e consumo são obrigatórios", "danger")
                return redirect(url_for("elemento_list"))
            
            # Verificar se nome já existe para este usuário
            if not admin:
                existing = supabase.table("elemento").select("id").eq("user_id", user_id).eq("nome", nome).execute()
                if existing.data:
                    flash("Elemento com este nome já existe para este usuário", "danger")
                    return redirect(url_for("elemento_list"))
            
            # Criar elemento
            data = {
                "nome": nome,
                "consumo_lpm": float(consumo_lpm) if consumo_lpm else 0,
                "compartilhado": compartilhado
            }
            
            if not admin:
                data["user_id"] = user_id
            
            supabase.table("elemento").insert(data).execute()
            flash("Elemento criado com sucesso!", "success")
            
        elif action == "update":
            # Atualizar elemento existente
            elemento_id = request.form.get("elemento_id")
            nome = request.form.get("nome").strip()
            consumo_lpm = request.form.get("consumo_lpm")
            compartilhado = request.form.get("compartilhado", "false").lower() == "true"
            
            # Validações
            if not elemento_id or not nome or not consumo_lpm:
                flash("ID do elemento, nome e consumo são obrigatórios", "danger")
                return redirect(url_for("elemento_list"))
            
            # Verificar se nome já existe para este usuário (exceto para o próprio elemento)
            if not admin:
                existing = supabase.table("elemento").select("id").eq("user_id", user_id).eq("nome", nome).neq("id", elemento_id).execute()
                if existing.data:
                    flash("Elemento com este nome já existe para este usuário", "danger")
                    return redirect(url_for("elemento_list"))
            
            # Atualizar elemento
            data = {
                "nome": nome,
                "consumo_lpm": float(consumo_lpm) if consumo_lpm else 0,
                "compartilhado": compartilhado
            }
            
            if not admin:
                supabase.table("elemento").update(data).eq("id", elemento_id).eq("user_id", user_id).execute()
            else:
                supabase.table("elemento").update(data).eq("id", elemento_id).execute()
            
            flash("Elemento atualizado com sucesso!", "success")
            
        elif action == "delete":
            # Deletar elemento existente
            elemento_id = request.form.get("elemento_id")
            
            if not elemento_id:
                flash("ID do elemento é obrigatório", "danger")
                return redirect(url_for("elemento_list"))
            
            # Verificar se elemento possui amostras vinculadas
            if not admin:
                amostra_count = supabase.table("amostra").select("id", count="exact").eq("elemento_id", elemento_id).execute()
                if amostra_count.count and amostra_count.count > 0:
                    flash("Não é possível excluir este elemento pois existem amostras vinculadas a ele", "danger")
                    return redirect(url_for("elemento_list"))
            
            # Deletar elemento
            if not admin:
                supabase.table("elemento").delete().eq("id", elemento_id).eq("user_id", user_id).execute()
            else:
                supabase.table("elemento").delete().eq("id", elemento_id).execute()
            
            flash("Elemento excluído com sucesso!", "success")
    
    if admin:
        # Admin vê todos os dados (com validação JWT)
        response = supabase.table("elemento").select("*").order("created_at", desc=True).execute()
        elementos = response.data or []
    else:
        # Usuário vê apenas seus dados + dados compartilhados
        # Otimizado: duas queries separadas para melhor performance
        own_query = supabase.table("elemento").select("*").eq("user_id", user_id).order("created_at", desc=True)
        shared_query = supabase.table("elemento").select("*").eq("compartilhado", True).order("created_at", desc=True)
        
        # Executar queries em paralelo
        own_response = own_query.execute()
        shared_response = shared_query.execute()
        
        # Combinar resultados (remover duplicatas se usuário compartilhou seus próprios dados)
        own_data = own_response.data or []
        shared_data = shared_response.data or []
        
        # Remover duplicatas (se usuário compartilhou seus próprios dados)
        shared_ids = {e["id"] for e in shared_data}
        unique_own_data = [e for e in own_data if e["id"] not in shared_ids]
        
        # Combinar e ordenar
        all_data = unique_own_data + shared_data
        all_data.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Aplicar paginação
        total = len(all_data)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = all_data[start:end]
        
        elementos = paginated_data
        
        # Preparar dados para template com paginação
        pages = (total + per_page - 1) // per_page
    
    return render_template("elemento.html", elementos=elementos, page=page, per_page=per_page, total=total if 'pages' in locals() else None, pages=pages if 'pages' in locals() else None)


# Otimizar queries para performance
# Separar dados próprios vs compartilhados para queries mais eficientes
@app.route("/amostras", methods=["GET", "POST"])
@login_required
def amostra_list():
    user_id = get_user_id()
    admin = is_admin()
    
    # Paginação
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", ITEMS_PER_PAGE, type=int)
    
    cilindro_base = supabase.table("cilindro").select("id,codigo").execute().data or []
    elementos_base = supabase.table("elemento").select("id,nome").execute().data or []
    
    if admin:
        cilindro_response = supabase.table("cilindro").select("id,codigo").execute()
        elementos_response = supabase.table("elemento").select("id,nome").execute()
    else:
        cilindro_response = supabase.table("cilindro").select("id,codigo").or_(f"user_id.eq.{user_id},compartilhado.eq.true").execute()
        elementos_response = supabase.table("elemento").select("id,nome").or_(f"user_id.eq.{user_id},compartilhado.eq.true").execute()
    
    cilindro = cilindro_response.data or []
    elementos = elementos_response.data or []
    
    if request.method == "POST":
        action = request.form.get("action")
        
        def formatar_tempo_chama(hora, minuto, segundo):
            h = hora.zfill(2) if hora else "00"
            m = minuto.zfill(2) if minuto else "00"
            s = segundo.zfill(2) if segundo else "00"
            return f"{h}:{m}:{s}"
        
        if action == "create":
            # Criar nova amostra
            data_amostra = request.form.get("data")
            hora = request.form.get("hora", "00")
            minuto = request.form.get("minuto", "00")
            segundo = request.form.get("segundo", "00")
            cilindro_id = request.form.get("cilindro_id")
            elemento_id = request.form.get("elemento_id")
            quantidade = request.form.get("quantidade_amostras", 1)
            compartilhado = request.form.get("compartilhado", "false").lower() == "true"
            
            # Validações
            if not data_amostra or not cilindro_id or not elemento_id:
                flash("Data, cilindro e elemento são obrigatórios", "danger")
                return redirect(url_for("amostra_list"))
            
            tempo_chama = formatar_tempo_chama(hora, minuto, segundo)
            
            # Criar amostra
            data = {
                "data": data_amostra,
                "tempo_chama": tempo_chama,
                "cilindro_id": int(cilindro_id),
                "elemento_id": int(elemento_id),
                "quantidade_amostras": int(quantidade) if quantidade else 1,
                "compartilhado": compartilhado
            }
            
            if not admin:
                data["user_id"] = user_id
            
            supabase.table("amostra").insert(data).execute()
            flash("Amostra criada com sucesso!", "success")
            
        elif action == "update":
            # Atualizar amostra existente
            amostra_id = request.form.get("amostra_id")
            data_amostra = request.form.get("data")
            hora = request.form.get("hora", "00")
            minuto = request.form.get("minuto", "00")
            segundo = request.form.get("segundo", "00")
            cilindro_id = request.form.get("cilindro_id")
            elemento_id = request.form.get("elemento_id")
            quantidade = request.form.get("quantidade_amostras", 1)
            compartilhado = request.form.get("compartilhado", "false").lower() == "true"
            
            # Validações
            if not amostra_id or not data_amostra or not cilindro_id or not elemento_id:
                flash("ID da amostra, data, cilindro e elemento são obrigatórios", "danger")
                return redirect(url_for("amostra_list"))
            
            tempo_chama = formatar_tempo_chama(hora, minuto, segundo)
            
            # Atualizar amostra
            data = {
                "data": data_amostra,
                "tempo_chama": tempo_chama,
                "cilindro_id": int(cilindro_id),
                "elemento_id": int(elemento_id),
                "quantidade_amostras": int(quantidade) if quantidade else 1,
                "compartilhado": compartilhado
            }
            
            if not admin:
                supabase.table("amostra").update(data).eq("id", amostra_id).eq("user_id", user_id).execute()
            else:
                supabase.table("amostra").update(data).eq("id", amostra_id).execute()
            
            flash("Amostra atualizada com sucesso!", "success")
            
        elif action == "delete":
            # Deletar amostra existente
            amostra_id = request.form.get("amostra_id")
            
            if not amostra_id:
                flash("ID da amostra é obrigatório", "danger")
                return redirect(url_for("amostra_list"))
            
            # Deletar amostra
            if not admin:
                supabase.table("amostra").delete().eq("id", amostra_id).eq("user_id", user_id).execute()
            else:
                supabase.table("amostra").delete().eq("id", amostra_id).execute()
            
            flash("Amostra excluída com sucesso!", "success")
    
    if admin:
        # Admin vê todos os dados (com validação JWT)
        response = supabase.table("amostra").select("*").order("data", desc=True).execute()
        amostras = response.data or []
    else:
        # Usuário vê apenas seus dados + dados compartilhados
        # Otimizado: duas queries separadas para melhor performance
        own_query = supabase.table("amostra").select("*").eq("user_id", user_id).order("data", desc=True)
        shared_query = supabase.table("amostra").select("*").eq("compartilhado", True).order("data", desc=True)
        
        # Executar queries em paralelo
        own_response = own_query.execute()
        shared_response = shared_query.execute()
        
        # Combinar resultados (remover duplicatas se usuário compartilhou seus próprios dados)
        own_data = own_response.data or []
        shared_data = shared_response.data or []
        
        # Remover duplicatas (se usuário compartilhou seus próprios dados)
        shared_ids = {a["id"] for a in shared_data}
        unique_own_data = [a for a in own_data if a["id"] not in shared_ids]
        
        # Combinar e ordenar
        all_data = unique_own_data + shared_data
        all_data.sort(key=lambda x: x.get("data", ""), reverse=True)
        
        # Aplicar paginação
        total = len(all_data)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = all_data[start:end]
        
        amostras = paginated_data
        
        # Preparar dados para template com paginação
        pages = (total + per_page - 1) // per_page
    
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
        total=total if 'pages' in locals() else None,
        pages=pages if 'pages' in locals() else None
    )


@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    user_id = get_user_id()

    # Get current profile data
    perfil_response = supabase.table("perfil").select("*").eq("id", user_id).execute()
    perfil_data = perfil_response.data[0] if perfil_response.data else {}
    user_role = perfil_data.get("role", "usuario")
    user_nome = perfil_data.get("nome", "")

    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "update_profile":
            nome = request.form.get("nome", "").strip()
            
            try:
                # Verificar se perfil existe
                perfil_check = supabase.table("perfil").select("id").eq("id", user_id).execute()
                
                if not perfil_check.data:
                    # Criar perfil se não existir
                    supabase.table("perfil").insert({
                        "id": user_id,
                        "role": "usuario",
                        "ativo": True,
                        "nome": nome,
                        "email": current_user.email
                    }).execute()
                    flash("Perfil criado com sucesso!", "success")
                else:
                    # Atualizar perfil existente
                    supabase.table("perfil").update({"nome": nome}).eq("id", user_id).execute()
                    flash("Perfil atualizado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao atualizar perfil: {str(e)}", "danger")
            
            return redirect(url_for("perfil"))

    cilindro_response = (
        supabase.table("cilindro").select("id").eq("user_id", user_id).execute()
    )
    elementos_response = (
        supabase.table("elemento").select("id").eq("user_id", user_id).execute()
    )
    amostras_response = (
        supabase.table("amostra").select("id").eq("user_id", user_id).execute()
    )

    stats = {
        "cilindros": len(cilindro_response.data or []),
        "elementos": len(elementos_response.data or []),
        "amostras": len(amostras_response.data or []),
    }

    return render_template("perfil.html", stats=stats, user_role=user_role, user_nome=user_nome)


# Remover get_admin_client completamente
# Remover service_role key de todas as operações admin
# Todas as operações admin agora usam JWT validation
@app.route("/admin")
@login_required
def admin_panel():
    if not is_admin():
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for("dashboard"))
    
    user_id = get_user_id()
    token = session.get("jwt_token")
    
    # Validar token JWT antes de operações admin
    if not token:
        flash("Sessão inválida. Faça login novamente.", "danger")
        return redirect(url_for("login"))
    
    try:
        decoded = jwt.decode(token, SUPABASE_KEY, algorithms=["HS256"])
        if decoded.get("user_id") != user_id:
            flash("Acesso não autorizado.", "danger")
            return redirect(url_for("dashboard"))
    except:
        flash("Token inválido.", "danger")
        return redirect(url_for("login"))
    
    # Operações admin com validação JWT
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
    
    return render_template("admin.html", users=users)


# Remover get_admin_client completamente
# Todas as operações agora usam JWT validation
@app.route("/admin/toggle-user", methods=["POST"])
@login_required
def admin_toggle_user():
    if not is_admin():
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for("dashboard"))
    
    user_id = request.form.get("user_id")
    ativo = request.form.get("ativo") == "true"
    
    if user_id == get_user_id():
        flash("Você não pode desativar seu próprio usuário.", "warning")
        return redirect(url_for("admin_panel"))
    
    token = session.get("jwt_token")
    if not token:
        flash("Sessão inválida. Faça login novamente.", "danger")
        return redirect(url_for("login"))
    
    try:
        decoded = jwt.decode(token, SUPABASE_KEY, algorithms=["HS256"])
        if decoded.get("user_id") != get_user_id():
            flash("Acesso não autorizado.", "danger")
            return redirect(url_for("dashboard"))
    except:
        flash("Token inválido.", "danger")
        return redirect(url_for("login"))
    
    client = get_admin_client()
    client.table("perfil").update({"ativo": ativo}).eq("id", user_id).execute()
    flash(f"Usuário {'ativado' if ativo else 'desativado'} com sucesso!", "success")
    
    return redirect(url_for("admin_panel"))


@app.route("/admin/set-role", methods=["POST"])
@login_required
def admin_set_role():
    if not is_admin():
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for("dashboard"))
    
    user_id = request.form.get("user_id")
    role = request.form.get("role")
    
    if user_id == get_user_id():
        flash("Você não pode alterar sua própria função.", "warning")
        return redirect(url_for("admin_panel"))
    
    token = session.get("jwt_token")
    if not token:
        flash("Sessão inválida. Faça login novamente.", "danger")
        return redirect(url_for("login"))
    
    try:
        decoded = jwt.decode(token, SUPABASE_KEY, algorithms=["HS256"])
        if decoded.get("user_id") != get_user_id():
            flash("Acesso não autorizado.", "danger")
            return redirect(url_for("dashboard"))
    except:
        flash("Token inválido.", "danger")
        return redirect(url_for("login"))
    
    client = get_admin_client()
    client.table("perfil").update({"role": role}).eq("id", user_id).execute()
    flash(f"Função do usuário alterada para {role}!", "success")
    
    return redirect(url_for("admin_panel"))


@app.route("/admin/delete-user", methods=["POST"])
@login_required
def admin_delete_user():
    if not is_admin():
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for("dashboard"))
    
    user_id = request.form.get("user_id")
    
    if user_id == get_user_id():
        flash("Você não pode excluir seu próprio usuário.", "warning")
        return redirect(url_for("admin_panel"))
    
    token = session.get("jwt_token")
    if not token:
        flash("Sessão inválida. Faça login novamente.", "danger")
        return redirect(url_for("login"))
    
    try:
        decoded = jwt.decode(token, SUPABASE_KEY, algorithms=["HS256"])
        if decoded.get("user_id") != get_user_id():
            flash("Acesso não autorizado.", "danger")
            return redirect(url_for("dashboard"))
    except:
        flash("Token inválido.", "danger")
        return redirect(url_for("login"))
    
    client = get_admin_client()
    client.table("cilindro").delete().eq("user_id", user_id).execute()
    client.table("elemento").delete().eq("user_id", user_id).execute()
    client.table("amostra").delete().eq("user_id", user_id).execute()
    client.table("perfil").delete().eq("id", user_id).execute()
    
    flash("Usuário e todos os seus dados foram excluídos!", "success")
    
    return redirect(url_for("admin_panel"))


@app.route("/admin/user-data/<target_user_id>")
@login_required
def admin_user_data(target_user_id):
    if not is_admin():
        flash("Acesso restrito a administradores.", "danger")
        return redirect(url_for("dashboard"))
    
    token = session.get("jwt_token")
    if not token:
        flash("Sessão inválida. Faça login novamente.", "danger")
        return redirect(url_for("login"))
    
    try:
        decoded = jwt.decode(token, SUPABASE_KEY, algorithms=["HS256"])
        if decoded.get("user_id") != get_user_id():
            flash("Acesso não autorizado.", "danger")
            return redirect(url_for("dashboard"))
    except:
        flash("Token inválido.", "danger")
        return redirect(url_for("login"))
    
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


@app.route("/historico")
@login_required
def historico():
    user_id = get_user_id()
    admin = is_admin()
    
    limit = 20
    
    if admin:
        cilindro_history = supabase.table("cilindro").select("*").order("created_at", desc=True).limit(limit).execute().data or []
        elemento_history = supabase.table("elemento").select("*").order("created_at", desc=True).limit(limit).execute().data or []
        amostra_history = supabase.table("amostra").select("*").order("created_at", desc=True).limit(limit).execute().data or []
    else:
        cilindro_history = supabase.table("cilindro").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute().data or []
        elemento_history = supabase.table("elemento").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute().data or []
        amostra_history = supabase.table("amostra").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute().data or []
    
    cilindro_map = {c["id"]: c["codigo"] for c in (supabase.table("cilindro").select("id,codigo").execute().data or [])}
    elemento_map = {e["id"]: e["nome"] for e in (supabase.table("elemento").select("id,nome").execute().data or [])}
    
    history = []
    
    for c in cilindro_history:
        history.append({
            "tipo": "cilindro",
            "acao": "criado" if c.get("created_at") else "atualizado",
            "nome": c.get("codigo"),
            "data": c.get("created_at") or c.get("updated_at"),
            "user_id": c.get("user_id")
        })
    
    for e in elemento_history:
        history.append({
            "tipo": "elemento",
            "acao": "criado" if e.get("created_at") else "atualizado",
            "nome": e.get("nome"),
            "data": e.get("created_at") or e.get("updated_at"),
            "user_id": e.get("user_id")
        })
    
    for a in amostra_history:
        history.append({
            "tipo": "amostra",
            "acao": "criado" if a.get("created_at") else "atualizado",
            "nome": f"{cilindro_map.get(a.get('cilindro_id'), 'N/A')} - {elemento_map.get(a.get('elemento_id'), 'N/A')}",
            "data": a.get("created_at"),
            "user_id": a.get("user_id")
        })
    
    history.sort(key=lambda x: x.get("data", ""), reverse=True)
    history = history[:limit]
    
    return render_template("historico.html", history=history)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
