import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api_client import api_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tempo de Chama - LabGas Manager", page_icon="🔥")

if not st.session_state.get('authenticated'):
    st.error("Você precisa fazer login para acessar esta página.")
    st.stop()

api_client.set_token(st.session_state.get('token'))

st.title("🔥 Tempo de Chama")

response_cilindros = api_client.get_cilindros()
response_elementos = api_client.get_elementos()
cilindros_list = response_cilindros.json() if response_cilindros.status_code == 200 else []
elementos_list = response_elementos.json() if response_elementos.status_code == 200 else []

if not cilindros_list or not elementos_list:
    st.warning("Cadastrecilindros e elementos primeiro.")
else:
    with st.expander("➕ Registrar Novo Tempo de Chama", expanded=False):
        with st.form("novo_tempo"):
            col1, col2, col3 = st.columns(3)
            with col1:
                horas = st.number_input("Horas", min_value=0, value=0, step=1)
            with col2:
                minutos = st.number_input("Minutos", min_value=0, value=0, step=1)
            with col3:
                segundos = st.number_input("Segundos", min_value=0, value=0, step=1)
            
            cilindro_selecionado = st.selectbox("Cilindro *", cilindros_list, 
                                      format_func=lambda x: x.get('codigo', ''))
            elemento_selecionado = st.selectbox("Elemento *", elementos_list, 
                                       format_func=lambda x: x.get('nome', ''))
            
            submitted = st.form_submit_button("Registrar", use_container_width=True)
            
            if submitted:
                if not cilindro_selecionado or not elemento_selecionado:
                    st.error("Cilindro e Elemento são obrigatórios.")
                else:
                    result = api_client.create_tempo({
                        "horas": horas,
                        "minutos": minutos,
                        "segundos": segundos,
                        "cilindro_id": cilindro_selecionado.get('id'),
                        "elemento_id": elemento_selecionado.get('id')
                    })
                    
                    if result.status_code in [200, 201]:
                        st.success("Tempo de chama registrado com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"Erro ao registrar: {result.json().get('message', 'Erro desconhecido')}")

st.markdown("---")

response = api_client.get_tempos()
tempos = response.json() if response.status_code == 200 else []

if not tempos:
    st.info("Nenhum tempo de chama registrado.")
else:
    df = pd.DataFrame(tempos)
    
    for i, row in df.iterrows():
        cilindro_match = next((c for c in cilindros_list if c.get('id') == row.get('cilindro_id')), None)
        elemento_match = next((e for e in elementos_list if e.get('id') == row.get('elemento_id')), None)
        df.at[i, 'cilindro_nome'] = cilindro_match.get('codigo', 'N/A') if cilindro_match else 'N/A'
        df.at[i, 'elemento_nome'] = elemento_match.get('nome', 'N/A') if elemento_match else 'N/A'
        
        total_segundos = row.get('horas', 0) * 3600 + row.get('minutos', 0) * 60 + row.get('segundos', 0)
        consumo = elemento_match.get('consumo_lpm', 0) * (total_segundos / 60) if elemento_match else 0
        df.at[i, 'consumo_litros'] = consumo
    
    df['tempo_formatado'] = df.apply(
        lambda x: f"{int(x['horas']):02d}:{int(x['minutos']):02d}:{int(x['segundos']):02d}", axis=1
    )
    
    st.dataframe(
        df[['tempo_formatado', 'cilindro_nome', 'elemento_nome', 'consumo_litros']].rename(
            columns={
                'tempo_formatado': 'Tempo',
                'cilindro_nome': 'Cilindro',
                'elemento_nome': 'Elemento',
                'consumo_litros': 'Consumo (L)'
            }
        ),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    st.subheader("📈 Análise de Consumo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        consumo_por_elemento = df.groupby('elemento_nome')['consumo_litros'].sum().reset_index()
        if not consumo_por_elemento.empty:
            fig1 = px.pie(consumo_por_elemento, values='consumo_litros', names='elemento_nome',
                         title='Consumo por Elemento')
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        consumo_por_cilindro = df.groupby('cilindro_nome')['consumo_litros'].sum().reset_index()
        if not consumo_por_cilindro.empty:
            fig2 = px.bar(consumo_por_cilindro, x='cilindro_nome', y='consumo_litros',
                         title='Consumo por Cilindro', color='consumo_litros')
            st.plotly_chart(fig2, use_container_width=True)
