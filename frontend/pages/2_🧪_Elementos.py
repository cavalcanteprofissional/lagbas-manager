import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api_client import api_client
import pandas as pd

st.set_page_config(page_title="Elementos - LabGas Manager", page_icon="🧪")

if not st.session_state.get('authenticated'):
    st.error("Você precisa fazer login para acessar esta página.")
    st.stop()

user = st.session_state.get('user')
if user:
    api_client.set_token(st.session_state.get('token'))

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
    {"nome": "Tálio", "consumo_lpm": 1.5}
]

st.title("🧪 Elementos")

response = api_client.get_elementos()
elementos = response.json() if response.status_code == 200 else []

if not elementos:
    st.info("Nenhum elemento encontrado. Os elementos padrão serão inseridos automaticamente.")
    for elemento in ELEMENTOS_PADRAO:
        api_client.create_elemento({
            "nome": elemento["nome"],
            "consumo_lpm": elemento["consumo_lpm"]
        })
    st.rerun()

with st.expander("➕ Cadastrar Novo Elemento", expanded=False):
    with st.form("novo_elemento"):
        nome = st.text_input("Nome *", placeholder="Ex: Alumínio")
        consumo_lpm = st.number_input("Consumo (L/min) *", min_value=0.0, value=1.5, step=0.1)
        
        submitted = st.form_submit_button("Cadastrar", use_container_width=True)
        
        if submitted:
            if not nome:
                st.error("Nome é obrigatório.")
            else:
                response_check = api_client.get_elementos()
                if response_check.status_code == 200:
                    existing = response_check.json()
                    if any(e.get('nome') == nome for e in existing):
                        st.error("Elemento já existe.")
                    else:
                        result = api_client.create_elemento({
                            "nome": nome,
                            "consumo_lpm": consumo_lpm
                        })
                        if result.status_code in [200, 201]:
                            st.success("Elemento cadastrado com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao cadastrar: {result.json().get('message', 'Erro desconhecido')}")

st.markdown("---")

response = api_client.get_elementos()
elementos = response.json() if response.status_code == 200 else []

if not elementos:
    st.info("Nenhum elemento cadastrado.")
else:
    df = pd.DataFrame(elementos)
    df['consumo_lpm'] = df['consumo_lpm'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(
        df[['nome', 'consumo_lpm']].rename(
            columns={
                'nome': 'Nome',
                'consumo_lpm': 'Consumo (L/min)'
            }
        ),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    st.subheader("✏️ Editar/Excluir Elemento")
    
    elemento_selecionado = st.selectbox(
        "Selecione um Elemento",
        elementos,
        format_func=lambda x: x.get('nome', '')
    )
    
    if elemento_selecionado:
        with st.expander("Editar Elemento"):
            with st.form("editar_elemento"):
                edit_nome = st.text_input("Nome", value=elemento_selecionado.get('nome', ''))
                edit_consumo = st.number_input("Consumo (L/min)", min_value=0.0, 
                                              value=float(elemento_selecionado.get('consumo_lpm', 1.5)), step=0.1)
                
                update_btn = st.form_submit_button("Salvar Alterações", use_container_width=True)
                
                if update_btn:
                    if not edit_nome:
                        st.error("Nome é obrigatório.")
                    else:
                        result = api_client.update_elemento(elemento_selecionado.get('id'), {
                            "nome": edit_nome,
                            "consumo_lpm": edit_consumo
                        })
                        
                        if result.status_code == 200:
                            st.success("Elemento atualizado com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao atualizar: {result.json().get('message', 'Erro desconhecido')}")
        
        if st.button("🗑️ Excluir Elemento", type="primary"):
            if st.session_state.get('confirm_delete_elemento'):
                result = api_client.delete_elemento(elemento_selecionado.get('id'))
                if result.status_code == 200:
                    st.success("Elemento excluído com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro ao excluir: {result.json().get('message', 'Erro desconhecido')}")
            else:
                st.session_state['confirm_delete_elemento'] = True
                st.warning("Clique novamente para confirmar a exclusão.")
