import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api_client import api_client

st.set_page_config(page_title="Usuários - LabGas Manager", page_icon="👥")

if not st.session_state.get('authenticated'):
    st.error("Você precisa fazer login para acessar esta página.")
    st.stop()

user = st.session_state.get('user')

st.title("👥 Perfil do Usuário")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Informações do Usuário")
    st.markdown(f"**Email:** {user.get('email', 'N/A')}")
    st.markdown(f"**Função:** Usuário")

with col2:
    st.subheader("Alterar Senha")
    with st.form("alterar_senha"):
        nova_senha = st.text_input("Nova Senha", type="password")
        confirmar_senha = st.text_input("Confirmar Senha", type="password")
        
        if st.form_submit_button("Alterar Senha"):
            if nova_senha != confirmar_senha:
                st.error("Senhas não conferem.")
            elif len(nova_senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            else:
                st.info("Funcionalidade de alteração de senha via API em desenvolvimento.")

st.markdown("---")

st.subheader("Estatísticas do Usuário")

response_cilindros = api_client.get_cilindros()
response_elementos = api_client.get_elementos()
response_amostras = api_client.get_amostras()
response_tempos = api_client.get_tempos()

cilindros = response_cilindros.json() if response_cilindros.status_code == 200 else []
elementos = response_elementos.json() if response_elementos.status_code == 200 else []
amostras = response_amostras.json() if response_amostras.status_code == 200 else []
tempos = response_tempos.json() if response_tempos.status_code == 200 else []

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Cilindros", len(cilindros))
with col2:
    st.metric("Elementos", len(elementos))
with col3:
    st.metric("Amostras", len(amostras))
with col4:
    st.metric("Registros de Tempo", len(tempos))
