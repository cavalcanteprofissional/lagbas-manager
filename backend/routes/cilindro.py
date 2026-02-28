from flask import Blueprint, request, jsonify
from backend.utils.supabase import get_supabase
from backend.utils.decorators import token_required
from backend.config import LITROS_EQUIVALENTES_KG, CUSTO_DEFAULT, GAS_KG_DEFAULT

cilindro_bp = Blueprint('cilindro', __name__, url_prefix='/api/cilindros')


@cilindro_bp.route('', methods=['GET'])
@token_required
def get_cilindros():
    supabase = get_supabase()
    user_id = request.user_id
    
    response = supabase.table("cilindro").select("*").eq("user_id", user_id).execute()
    
    return jsonify(response.data), 200


@cilindro_bp.route('', methods=['POST'])
@token_required
def create_cilindro():
    supabase = get_supabase()
    user_id = request.user_id
    data = request.get_json()
    
    if not data.get('codigo'):
        return jsonify({'message': 'Código é obrigatório'}), 400
    
    if not data.get('data_compra'):
        return jsonify({'message': 'Data de compra é obrigatória'}), 400
    
    existing = supabase.table("cilindro").select("id").eq("codigo", data['codigo']).eq("user_id", user_id).execute()
    if existing.data:
        return jsonify({'message': 'Código já existe'}), 400
    
    gas_kg = data.get('gas_kg', GAS_KG_DEFAULT)
    litros = gas_kg * LITROS_EQUIVALENTES_KG
    custo = data.get('custo', CUSTO_DEFAULT)
    
    new_data = {
        "codigo": data['codigo'],
        "data_compra": data['data_compra'],
        "gas_kg": gas_kg,
        "litros_equivalentes": litros,
        "custo": custo,
        "status": data.get('status', 'ativo'),
        "user_id": user_id
    }
    
    response = supabase.table("cilindro").insert(new_data).execute()
    
    return jsonify({
        'message': 'Cilindro criado com sucesso',
        'data': response.data[0]
    }), 201


@cilindro_bp.route('/<int:cilindro_id>', methods=['GET'])
@token_required
def get_cilindro(cilindro_id):
    supabase = get_supabase()
    user_id = request.user_id
    
    response = supabase.table("cilindro").select("*").eq("id", cilindro_id).eq("user_id", user_id).execute()
    
    if not response.data:
        return jsonify({'message': 'Cilindro não encontrado'}), 404
    
    return jsonify(response.data[0]), 200


@cilindro_bp.route('/<int:cilindro_id>', methods=['PUT'])
@token_required
def update_cilindro(cilindro_id):
    supabase = get_supabase()
    user_id = request.user_id
    data = request.get_json()
    
    existing = supabase.table("cilindro").select("id").eq("id", cilindro_id).eq("user_id", user_id).execute()
    if not existing.data:
        return jsonify({'message': 'Cilindro não encontrado'}), 404
    
    if data.get('codigo'):
        duplicate = supabase.table("cilindro").select("id").eq("codigo", data['codigo']).eq("user_id", user_id).neq("id", cilindro_id).execute()
        if duplicate.data:
            return jsonify({'message': 'Código já existe'}), 400
    
    gas_kg = data.get('gas_kg', existing.data[0].get('gas_kg', GAS_KG_DEFAULT))
    litros = gas_kg * LITROS_EQUIVALENTES_KG
    
    update_data = {
        "codigo": data.get('codigo', existing.data[0]['codigo']),
        "data_compra": data.get('data_compra', existing.data[0]['data_compra']),
        "gas_kg": gas_kg,
        "litros_equivalentes": litros,
        "custo": data.get('custo', existing.data[0]['custo']),
        "status": data.get('status', existing.data[0]['status'])
    }
    
    response = supabase.table("cilindro").update(update_data).eq("id", cilindro_id).execute()
    
    return jsonify({
        'message': 'Cilindro atualizado com sucesso',
        'data': response.data[0]
    }), 200


@cilindro_bp.route('/<int:cilindro_id>', methods=['DELETE'])
@token_required
def delete_cilindro(cilindro_id):
    supabase = get_supabase()
    user_id = request.user_id
    
    existing = supabase.table("cilindro").select("id").eq("id", cilindro_id).eq("user_id", user_id).execute()
    if not existing.data:
        return jsonify({'message': 'Cilindro não encontrado'}), 404
    
    supabase.table("cilindro").delete().eq("id", cilindro_id).execute()
    
    return jsonify({'message': 'Cilindro excluído com sucesso'}), 200
