import streamlit as st
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None
    
    def set_token(self, token):
        self.token = token
    
    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def login(self, email, password):
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        return response
    
    def register(self, email, password, name=""):
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json={"email": email, "password": password, "name": name}
        )
        return response
    
    def logout(self):
        response = requests.post(
            f"{self.base_url}/api/auth/logout",
            headers=self._get_headers()
        )
        return response
    
    def get_cilindros(self):
        response = requests.get(
            f"{self.base_url}/api/cilindros",
            headers=self._get_headers()
        )
        return response
    
    def create_cilindro(self, data):
        response = requests.post(
            f"{self.base_url}/api/cilindros",
            json=data,
            headers=self._get_headers()
        )
        return response
    
    def get_elementos(self):
        response = requests.get(
            f"{self.base_url}/api/elementos",
            headers=self._get_headers()
        )
        return response
    
    def get_amostras(self):
        response = requests.get(
            f"{self.base_url}/api/amostras",
            headers=self._get_headers()
        )
        return response
    
    def get_tempos(self):
        response = requests.get(
            f"{self.base_url}/api/tempo-chama",
            headers=self._get_headers()
        )
        return response


api_client = APIClient()

st.set_page_config(page_title="LabGas Manager", page_icon="🔬", layout="wide")


def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'token' not in st.session_state:
        st.session_state['token'] = None
    if 'user' not in st.session_state:
        st.session_state['user'] = None


def check_auth():
    init_session_state()
    
    if not st.session_state['authenticated']:
        render_login_page()
        st.stop()
    
    return st.session_state['user']


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
            response = api_client.login(email, password)
            if response.status_code == 200:
                data = response.json()
                st.session_state['token'] = data['token']
                st.session_state['user'] = data['user']
                st.session_state['authenticated'] = True
                api_client.set_token(data['token'])
                st.rerun()
            else:
                st.error(f"Erro no login: {response.json().get('message', 'Erro desconhecido')}")
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
                    response = api_client.register(new_email, new_password, nome)
                    if response.status_code in [200, 201]:
                        st.success("Conta criada! Verifique seu email para confirmação.")
                        st.session_state['show_register'] = False
                        st.rerun()
                    else:
                        st.error(f"Erro no registro: {response.json().get('message', 'Erro desconhecido')}")
                else:
                    st.warning("Preencha todos os campos")
        
        if st.button("Voltar"):
            st.session_state['show_register'] = False
            st.rerun()


def logout():
    if st.session_state.get('token'):
        api_client.set_token(st.session_state['token'])
        api_client.logout()
    st.session_state['authenticated'] = False
    st.session_state['token'] = None
    st.session_state['user'] = None
    api_client.set_token(None)
    st.rerun()


APP_NAME = "LabGas Manager"
APP_VERSION = "0.1.0"


def main():
    user = check_auth()
    
    if user:
        if st.session_state.get('token'):
            api_client.set_token(st.session_state['token'])
        
        st.sidebar.title(f"🔬 {APP_NAME}")
        st.sidebar.markdown(f"**Usuário:** {user.get('email', 'N/A')}")
        st.sidebar.markdown(f"**Versão:** {APP_VERSION}")
        
        if st.sidebar.button("Logout"):
            logout()
        
        st.title("📊 Dashboard - Visão Geral")
        
        response_cilindros = api_client.get_cilindros()
        response_elementos = api_client.get_elementos()
        response_amostras = api_client.get_amostras()
        response_tempos = api_client.get_tempos()
        
        cilindro = response_cilindros.json() if response_cilindros.status_code == 200 else []
        elementos = response_elementos.json() if response_elementos.status_code == 200 else []
        amostras = response_amostras.json() if response_amostras.status_code == 200 else []
        tempos_chama = response_tempos.json() if response_tempos.status_code == 200 else []
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Cilindros Cadastrados", len(cilindro))
        with col2:
            ativos = len([c for c in cilindro if c.get('status') == 'ativo'])
            st.metric("Cilindros Ativos", ativos)
        with col3:
            st.metric("Elementos Cadastrados", len(elementos))
        with col4:
            st.metric("Amostras Registradas", len(amostras))
        
        st.markdown("---")
        
        import pandas as pd
        import plotly.express as px
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📦 Cilindros por Status")
            if cilindro:
                status_counts = {}
                for c in cilindro:
                    status = c.get('status', 'desconhecido')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                df_status = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Quantidade'])
                fig_status = px.pie(df_status, values='Quantidade', names='Status', 
                                  color='Status',
                                  color_discrete_map={
                                      'ativo': 'green',
                                      'em_uso': 'blue',
                                      'esgotado': 'red',
                                      'inativo': 'gray'
                                  })
                st.plotly_chart(fig_status, use_container_width=True)
            else:
                st.info("Nenhum cilindro cadastrado.")
        
        with col2:
            st.subheader("🧪 Elementos e Consumo (L/min)")
            if elementos:
                df_elementos = pd.DataFrame(elementos)
                df_elementos = df_elementos.sort_values('consumo_lpm', ascending=True)
                fig_consumo = px.bar(df_elementos, x='consumo_lpm', y='nome', 
                                    orientation='h',
                                    title='Consumo por Elemento (L/min)',
                                    labels={'consumo_lpm': 'Consumo (L/min)', 'nome': 'Elemento'})
                st.plotly_chart(fig_consumo, use_container_width=True)
            else:
                st.info("Nenhum elemento cadastrado.")
        
        st.markdown("---")
        
        st.subheader("⏱️ Tempo de Chama - Últimos Registros")
        if tempos_chama:
            df_tempos = pd.DataFrame(tempos_chama)
            df_tempos = df_tempos.sort_values('created_at', ascending=False).head(10)
            
            df_tempos['tempo_formatado'] = df_tempos.apply(
                lambda x: f"{x['horas']:02d}:{x['minutos']:02d}:{x['segundos']:02d}", axis=1
            )
            
            st.dataframe(
                df_tempos[['tempo_formatado', 'created_at']].rename(
                    columns={'tempo_formatado': 'Tempo', 'created_at': 'Data/Hora'}
                ),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum tempo de chama registrado.")


if __name__ == "__main__":
    main()
