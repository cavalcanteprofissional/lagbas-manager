import os
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

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


def get_user_id():
    return session.get("user_id")


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

            session["user_id"] = response.user.id
            session.permanent = True
            session["user_data"] = {
                "id": response.user.id,
                "email": response.user.email,
                "email_confirmed_at": response.user.email_confirmed_at,
            }

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

            flash("Conta criada! Verifique seu email para confirmação.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            flash(f"Erro no registro: {str(e)}", "danger")

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    try:
        supabase.auth.sign_out()
    except:
        pass

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

    return render_template(
        "dashboard.html",
        cilindro=cilindro,
        elementos=elementos,
        amostras=amostras,
        ativos=ativos,
        status_counts=status_counts,
    )


@app.route("/cilindros", methods=["GET", "POST"])
@login_required
def cilindro_list():
    user_id = get_user_id()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            codigo = request.form.get("codigo")
            data_compra = request.form.get("data_compra")
            data_inicio_consumo = request.form.get("data_inicio_consumo") or None
            data_fim = request.form.get("data_fim") or None
            gas_kg = float(request.form.get("gas_kg", GAS_KG_DEFAULT))
            custo = float(request.form.get("custo", CUSTO_DEFAULT))
            status = request.form.get("status", "ativo")

            existing = (
                supabase.table("cilindro")
                .select("id")
                .eq("codigo", codigo)
                .eq("user_id", user_id)
                .execute()
            )
            if existing.data:
                flash("Código já existe.", "danger")
            else:
                supabase.table("cilindro").insert(
                    {
                        "codigo": codigo,
                        "data_compra": data_compra,
                        "data_inicio_consumo": data_inicio_consumo,
                        "data_fim": data_fim,
                        "gas_kg": gas_kg,
                        "litros_equivalentes": gas_kg * LITROS_EQUIVALENTES_KG,
                        "custo": custo,
                        "status": status,
                        "user_id": user_id,
                    }
                ).execute()
                flash("Cilindro cadastrado!", "success")

        elif action == "update":
            cilindro_id = request.form.get("cilindro_id")
            codigo = request.form.get("codigo")
            data_compra = request.form.get("data_compra")
            data_inicio_consumo = request.form.get("data_inicio_consumo") or None
            data_fim = request.form.get("data_fim") or None
            gas_kg = float(request.form.get("gas_kg"))
            custo = float(request.form.get("custo"))
            status = request.form.get("status")

            supabase.table("cilindro").update(
                {
                    "codigo": codigo,
                    "data_compra": data_compra,
                    "data_inicio_consumo": data_inicio_consumo,
                    "data_fim": data_fim,
                    "gas_kg": gas_kg,
                    "litros_equivalentes": gas_kg * LITROS_EQUIVALENTES_KG,
                    "custo": custo,
                    "status": status,
                }
            ).eq("id", cilindro_id).execute()
            flash("Cilindro atualizado!", "success")

        elif action == "delete":
            cilindro_id = request.form.get("cilindro_id")
            
            amostras_response = supabase.table("amostra").select("id").eq("cilindro_id", cilindro_id).execute()
            
            if amostras_response.data:
                flash("Não é possível excluir: cilindro possui amostras vinculadas.", "danger")
            else:
                supabase.table("cilindro").delete().eq("id", cilindro_id).execute()
                flash("Cilindro excluído!", "success")

        return redirect(url_for("cilindro_list"))

    response = supabase.table("cilindro").select("*").eq("user_id", user_id).execute()
    cilindro = response.data or []

    return render_template(
        "cilindro.html", cilindro=cilindro, status_options=CILINDRO_STATUS
    )


@app.route("/elementos", methods=["GET", "POST"])
@login_required
def elemento_list():
    user_id = get_user_id()

    response = supabase.table("elemento").select("*").eq("user_id", user_id).execute()
    elementos = response.data or []

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            nome = request.form.get("nome")
            consumo_lpm = float(request.form.get("consumo_lpm"))

            existing = (
                supabase.table("elemento")
                .select("id")
                .eq("nome", nome)
                .eq("user_id", user_id)
                .execute()
            )
            if existing.data:
                flash("Elemento já existe.", "danger")
            else:
                supabase.table("elemento").insert(
                    {"nome": nome, "consumo_lpm": consumo_lpm, "user_id": user_id}
                ).execute()
                flash("Elemento cadastrado!", "success")

        elif action == "update":
            elemento_id = request.form.get("elemento_id")
            nome = request.form.get("nome")
            consumo_lpm = float(request.form.get("consumo_lpm"))

            supabase.table("elemento").update(
                {"nome": nome, "consumo_lpm": consumo_lpm}
            ).eq("id", elemento_id).execute()
            flash("Elemento atualizado!", "success")

        elif action == "delete":
            elemento_id = request.form.get("elemento_id")
            
            amostras_response = supabase.table("amostra").select("id").eq("elemento_id", elemento_id).execute()
            
            if amostras_response.data:
                flash("Não é possível excluir: elemento possui amostras vinculadas.", "danger")
            else:
                supabase.table("elemento").delete().eq("id", elemento_id).execute()
                flash("Elemento excluído!", "success")

        return redirect(url_for("elemento_list"))

    return render_template("elemento.html", elementos=elementos)


@app.route("/amostras", methods=["GET", "POST"])
@login_required
def amostra_list():
    user_id = get_user_id()

    cilindro_response = (
        supabase.table("cilindro").select("id,codigo").eq("user_id", user_id).execute()
    )
    elementos_response = (
        supabase.table("elemento").select("id,nome").eq("user_id", user_id).execute()
    )

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
            data = request.form.get("data")
            hora = request.form.get("hora") or "0"
            minuto = request.form.get("minuto") or "0"
            segundo = request.form.get("segundo") or "0"
            tempo_chama = formatar_tempo_chama(hora, minuto, segundo)
            cilindro_id = request.form.get("cilindro_id")
            elemento_id = request.form.get("elemento_id")
            quantidade_amostras = int(request.form.get("quantidade_amostras", 1))

            supabase.table("amostra").insert(
                {
                    "data": data,
                    "tempo_chama": tempo_chama,
                    "cilindro_id": cilindro_id,
                    "elemento_id": elemento_id,
                    "quantidade_amostras": quantidade_amostras,
                    "user_id": user_id,
                }
            ).execute()
            flash("Amostra registrada!", "success")
            
        elif action == "update":
            amostra_id = request.form.get("amostra_id")
            data = request.form.get("data")
            hora = request.form.get("hora") or "0"
            minuto = request.form.get("minuto") or "0"
            segundo = request.form.get("segundo") or "0"
            tempo_chama = formatar_tempo_chama(hora, minuto, segundo)
            cilindro_id = request.form.get("cilindro_id")
            elemento_id = request.form.get("elemento_id")
            quantidade_amostras = int(request.form.get("quantidade_amostras", 1))

            supabase.table("amostra").update(
                {
                    "data": data,
                    "tempo_chama": tempo_chama,
                    "cilindro_id": cilindro_id,
                    "elemento_id": elemento_id,
                    "quantidade_amostras": quantidade_amostras,
                }
            ).eq("id", amostra_id).execute()
            flash("Amostra atualizada!", "success")
            
        elif action == "delete":
            amostra_id = request.form.get("amostra_id")
            supabase.table("amostra").delete().eq("id", amostra_id).execute()
            flash("Amostra excluída!", "success")
        
        return redirect(url_for("amostra_list"))

    response = (
        supabase.table("amostra")
        .select("*")
        .eq("user_id", user_id)
        .order("data", desc=True)
        .execute()
    )
    amostras = response.data or []

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
        "amostra.html", amostras=amostras, cilindro=cilindro, elementos=elementos
    )


@app.route("/perfil")
@login_required
def perfil():
    user_id = get_user_id()

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

    return render_template("perfil.html", stats=stats)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
