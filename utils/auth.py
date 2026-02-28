import streamlit as st
from supabase import create_client
from utils.config import SUPABASE_URL, SUPABASE_KEY
from utils.database import get_supabase


class AuthManager:
    def __init__(self):
        self.supabase = get_supabase()
    
    def login(self, email: str, password: str) -> dict:
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {"success": True, "user": response.user, "session": response.session}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def register(self, email: str, password: str, user_data: dict = None) -> dict:
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data or {}
                }
            })
            return {"success": True, "user": response.user}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def logout(self):
        try:
            self.supabase.auth.sign_out()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_current_user(self):
        try:
            response = self.supabase.auth.get_user()
            return response.user if response.user else None
        except:
            return None
    
    def is_authenticated(self) -> bool:
        return self.get_current_user() is not None
    
    def reset_password(self, email: str) -> dict:
        try:
            self.supabase.auth.reset_password_for_email(email)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_password(self, new_password: str) -> dict:
        try:
            self.supabase.auth.update_user({
                "password": new_password
            })
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_role(self) -> str:
        user = self.get_current_user()
        if user and user.user_metadata:
            return user.user_metadata.get('role', 'viewer')
        return 'viewer'


auth = AuthManager()


def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    if not st.session_state['authenticated']:
        render_login_page()
        st.stop()
    
    current_user = auth.get_current_user()
    if not current_user:
        st.session_state['authenticated'] = False
        st.rerun()
    
    return current_user


def render_login_page():
    st.title("🔬 LabGas Manager - Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="seu@email.com")
        password = st.text_input("Senha", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Entrar", use_container_width=True)
        with col2:
            register_button = st.form_submit_button("Registrar", use_container_width=True)
    
    if login_button:
        if email and password:
            result = auth.login(email, password)
            if result["success"]:
                st.session_state['user'] = result['user']
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error(f"Erro no login: {result['error']}")
        else:
            st.warning("Preencha email e senha")
    
    if register_button:
        st.session_state['show_register'] = True
    
    if st.session_state.get('show_register', False):
        with st.form("register_form"):
            st.subheader("Registrar Novo Usuário")
            new_email = st.text_input("Email", placeholder="novo@email.com")
            new_password = st.text_input("Senha", type="password")
            confirm_password = st.text_input("Confirmar Senha", type="password")
            nome = st.text_input("Nome Completo")
            
            if st.form_submit_button("Criar Conta"):
                if new_password != confirm_password:
                    st.error("Senhas não conferem")
                elif new_email and new_password:
                    user_data = {"name": nome, "role": "viewer"}
                    result = auth.register(new_email, new_password, user_data)
                    if result["success"]:
                        st.success("Conta criada! Verifique seu email para confirmação.")
                        st.session_state['show_register'] = False
                        st.rerun()
                    else:
                        st.error(f"Erro no registro: {result['error']}")
                else:
                    st.warning("Preencha todos os campos")
        
        if st.button("Voltar"):
            st.session_state['show_register'] = False
            st.rerun()
