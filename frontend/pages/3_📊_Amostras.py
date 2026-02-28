import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api_client import api_client
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Amostras - LabGas Manager", page_icon="📊")

if not st.session_state.get('authenticated'):
    st.error("Você precisa fazer login para acessar esta página.")
    st.stop()

api_client.set_token(st.session_state.get('token'))

st.title("📊 Amostras")

response_cilindros = api_client.get_cilindros()
response_elementos = api_client.get_elementos()
cilindros = response_cilindros.json() if response_cilindros.status_code == 200 else []
elementos = response_elementos.json() if response_elementos.status_code == 200 else []

if not cilindros:
    st.warning("Cadastrecilindros primeiro.")
elif not elementos:
    st.warning("Cadastre elementos primeiro.")
else:
    with st.expander("➕ Registrar Nova Amostra", expanded=False):
        with st.form("nova_amostra"):
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("Data *", value=datetime.now().date())
            with col2:
                hora = st.time_input("Hora *", value=datetime.now().time())
            
            cilindro_selecionado = st.selectbox("Cilindro *", cilindros, 
                                      format_func=lambda x: x.get('codigo', ''))
            elemento_selecionado = st.selectbox("Elemento *", elementos, 
                                       format_func=lambda x: x.get('nome', ''))
            tempo_chama_segundos = st.number_input("Tempo de Chama (segundos)", 
                                                   min_value=0, value=0, step=1)
            
            submitted = st.form_submit_button("Registrar", use_container_width=True)
            
            if submitted:
                if not cilindro_selecionado or not elemento_selecionado:
                    st.error("Cilindro e Elemento são obrigatórios.")
                else:
                    result = api_client.create_amostra({
                        "data": data.isoformat(),
                        "hora": hora.isoformat(),
                        "cilindro_id": cilindro_selecionado.get('id'),
                        "elemento_id": elemento_selecionado.get('id'),
                        "tempo_chama_segundos": tempo_chama_segundos
                    })
                    
                    if result.status_code in [200, 201]:
                        st.success("Amostra registrada com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"Erro ao registrar: {result.json().get('message', 'Erro desconhecido')}")

st.markdown("---")

response = api_client.get_amostras()
amostras = response.json() if response.status_code == 200 else []

if not amostras:
    st.info("Nenhuma amostra registrada.")
else:
    df = pd.DataFrame(amostras)
    
    for i, row in df.iterrows():
        cilindro = next((c for c in cilindros if c.get('id') == row.get('cilindro_id')), None)
        elemento = next((e for e in elementos if e.get('id') == row.get('elemento_id')), None)
        df.at[i, 'cilindro_nome'] = cilindro.get('codigo', 'N/A') if cilindro else 'N/A'
        df.at[i, 'elemento_nome'] = elemento.get('nome', 'N/A') if elemento else 'N/A'
    
    df['data'] = pd.to_datetime(df['data']).dt.strftime('%d/%m/%Y')
    
    st.dataframe(
        df[['data', 'hora', 'cilindro_nome', 'elemento_nome', 'tempo_chama_segundos']].rename(
            columns={
                'data': 'Data',
                'hora': 'Hora',
                'cilindro_nome': 'Cilindro',
                'elemento_nome': 'Elemento',
                'tempo_chama_segundos': 'Tempo (s)'
            }
        ),
        use_container_width=True,
        hide_index=True
    )
