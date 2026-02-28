import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.api_client import api_client

st.set_page_config(page_title="Cilindros - LabGas Manager", page_icon="📦")

if not st.session_state.get('authenticated'):
    st.error("Você precisa fazer login para acessar esta página.")
    st.stop()

user = st.session_state.get('user')
if user:
    api_client.set_token(st.session_state.get('token'))

LITROS_EQUIVALENTES_KG = 956.0
GAS_KG_DEFAULT = 1.0
CUSTO_DEFAULT = 290.00
CILINDRO_STATUS = ['ativo', 'em_uso', 'esgotado', 'inativo']

def formatar_data(data):
    if data:
        try:
            from datetime import datetime
            return datetime.strptime(str(data), '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            return data
    return data

st.title("📦 Cilindros")

with st.expander("➕ Cadastrar Novo Cilindro", expanded=False):
    with st.form("form_cilindro"):
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código *", placeholder="Ex: CIL-001")
            data_compra = st.date_input("Data de Compra *")
        with col2:
            gas_kg = st.number_input("Gás (kg)", min_value=0.1, value=GAS_KG_DEFAULT, step=0.1)
            custo = st.number_input("Custo (R$)", min_value=0.0, value=CUSTO_DEFAULT, step=1.0)
        
        status = st.selectbox("Status", CILINDRO_STATUS)
        
        submitted = st.form_submit_button("Cadastrar", use_container_width=True)
        
        if submitted:
            if not codigo:
                st.error("Código é obrigatório.")
            elif not data_compra:
                st.error("Data de compra é obrigatória.")
            else:
                response = api_client.get_cilindros()
                if response.status_code == 200:
                    existing = response.json()
                    if any(c.get('codigo') == codigo for c in existing):
                        st.error("Código já existe para este usuário.")
                    else:
                        litros = gas_kg * LITROS_EQUIVALENTES_KG
                        data_compra_str = data_compra.isoformat() if hasattr(data_compra, 'isoformat') else str(data_compra)
                        
                        result = api_client.create_cilindro({
                            "codigo": codigo,
                            "data_compra": data_compra_str,
                            "gas_kg": gas_kg,
                            "litros_equivalentes": litros,
                            "custo": custo,
                            "status": status
                        })
                        
                        if result.status_code in [200, 201]:
                            st.success("Cilindro cadastrado com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao cadastrar: {result.json().get('message', 'Erro desconhecido')}")
                else:
                    st.error("Erro ao verificar códigos existentes.")

st.markdown("---")

response = api_client.get_cilindros()
data = response.json() if response.status_code == 200 else []

if not data:
    st.info("Nenhum cilindro cadastrado.")
else:
    filtro_status = st.selectbox("Filtrar por Status", ["Todos"] + CILINDRO_STATUS)
    
    filtered_data = data
    if filtro_status != "Todos":
        filtered_data = [c for c in data if c.get('status') == filtro_status]
    
    import pandas as pd
    df = pd.DataFrame(filtered_data)
    if not df.empty:
        df['data_compra_fmt'] = df['data_compra'].apply(formatar_data)
        df['litros_fmt'] = df['litros_equivalentes'].apply(lambda x: f"{x:.2f}")
        df['gas_kg_fmt'] = df['gas_kg'].apply(lambda x: f"{x:.2f}")
        df['custo_fmt'] = df['custo'].apply(lambda x: f"R$ {x:.2f}")
        
        st.dataframe(
            df[['codigo', 'data_compra_fmt', 'gas_kg_fmt', 'litros_fmt', 'custo_fmt', 'status']].rename(
                columns={
                    'codigo': 'Código',
                    'data_compra_fmt': 'Data Compra',
                    'gas_kg_fmt': 'Gás (kg)',
                    'litros_fmt': 'Litros',
                    'custo_fmt': 'Custo',
                    'status': 'Status'
                }
            ),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        st.subheader("✏️ Editar/Excluir Cilindro")
        
        selected = st.selectbox(
            "Selecione um Cilindro",
            filtered_data,
            format_func=lambda x: f"{x.get('codigo', '')} - {x.get('status', '')}"
        )
        
        if selected:
            with st.expander("Editar Cilindro"):
                with st.form("form_edit"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_codigo = st.text_input("Código", value=selected.get('codigo', ''))
                        edit_data_val = selected.get('data_compra')
                        if edit_data_val:
                            try:
                                edit_data_val = pd.to_datetime(edit_data_val).date()
                            except:
                                edit_data_val = None
                        edit_data = st.date_input("Data de Compra", value=edit_data_val)
                    with col2:
                        edit_kg = st.number_input("Gás (kg)", min_value=0.1, 
                                                    value=float(selected.get('gas_kg', GAS_KG_DEFAULT)), step=0.1)
                        edit_custo = st.number_input("Custo (R$)", min_value=0.0, 
                                                    value=float(selected.get('custo', CUSTO_DEFAULT)), step=1.0)
                    
                    edit_status_idx = 0
                    try:
                        edit_status_idx = CILINDRO_STATUS.index(selected.get('status', 'ativo'))
                    except:
                        pass
                    edit_status = st.selectbox("Status", CILINDRO_STATUS, index=edit_status_idx)
                    
                    update_btn = st.form_submit_button("Salvar Alterações", use_container_width=True)
                    
                    if update_btn:
                        if not edit_codigo:
                            st.error("Código é obrigatório.")
                        else:
                            edit_litros = edit_kg * LITROS_EQUIVALENTES_KG
                            edit_data_str = edit_data.isoformat() if edit_data else None
                            
                            result = api_client.update_cilindro(selected.get('id'), {
                                "codigo": edit_codigo,
                                "data_compra": edit_data_str,
                                "gas_kg": edit_kg,
                                "litros_equivalentes": edit_litros,
                                "custo": edit_custo,
                                "status": edit_status
                            })
                            
                            if result.status_code == 200:
                                st.success("Cilindro atualizado com sucesso!")
                                st.rerun()
                            else:
                                st.error(f"Erro ao atualizar: {result.json().get('message', 'Erro desconhecido')}")
            
            if st.button("🗑️ Excluir Cilindro", type="primary"):
                if st.session_state.get('confirm_delete'):
                    result = api_client.delete_cilindro(selected.get('id'))
                    if result.status_code == 200:
                        st.success("Cilindro excluído com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"Erro ao excluir: {result.json().get('message', 'Erro desconhecido')}")
                else:
                    st.session_state['confirm_delete'] = True
                    st.warning("Clique novamente para confirmar a exclusão.")
