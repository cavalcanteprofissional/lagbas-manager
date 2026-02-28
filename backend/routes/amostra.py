from flask import Blueprint, request, jsonify
from backend.utils.supabase import get_supabase
from backend.utils.decorators import token_required

amostra_bp = Blueprint('amostra', __name__, url_prefix='/api/amostras')


@amostra_bp.route('', methods=['GET'])
@token_required
def get_amostras():
    supabase = get_supabase()
    user_id = request.user_id
    
    response = supabase.table("amostra").select("*").eq("user_id", user_id).execute()
    
    return jsonify(response.data), 200


@amostra_bp.route('', methods=['POST'])
@token_required
def create_amostra():
    supabase = get_supabase()
    user_id = request.user_id
    data = request.get_json()
    
    if not data.get('data') or not data.get('hora'):
        return jsonify({'message': 'Data e hora são obrigatórios'}), 400
    
    new_data = {
        "data": data['data'],
        "hora": data['hora'],
        "cilindro_id": data.get('cilindro_id'),
        "elemento_id": data.get('elemento_id'),
        "tempo_chama_segundos": data.get('tempo_chama_segundos', 0),
        "user_id": user_id
    }
    
    response = supabase.table("amostra").insert(new_data).execute()
    
    return jsonify({
        'message': 'Amostra criada com sucesso',
        'data': response.data[0]
    }), 201


@amostra_bp.route('/<int:amostra_id>', methods=['GET'])
@token_required
def get_amostra(amostra_id):
    supabase = get_supabase()
    user_id = request.user_id
    
    response = supabase.table("amostra").select("*").eq("id", amostra_id).eq("user_id", user_id).execute()
    
    if not response.data:
        return jsonify({'message': 'Amostra não encontrada'}), 404
    
    return jsonify(response.data[0]), 200


@amostra_bp.route('/<int:amostra_id>', methods=['PUT'])
@token_required
def update_amostra(amostra_id):
    supabase = get_supabase()
    user_id = request.user_id
    data = request.get_json()
    
    existing = supabase.table("amostra").select("id").eq("id", amostra_id).eq("user_id", user_id).execute()
    if not existing.data:
        return jsonify({'message': 'Amostra não encontrada'}), 404
    
    update_data = {
        "data": data.get('data', existing.data[0]['data']),
        "hora": data.get('hora', existing.data[0]['hora']),
        "cilindro_id": data.get('cilindro_id', existing.data[0].get('cilindro_id')),
        "elemento_id": data.get('elemento_id', existing.data[0].get('elemento_id')),
        "tempo_chama_segundos": data.get('tempo_chama_segundos', existing.data[0].get('tempo_chama_segundos', 0))
    }
    
    response = supabase.table("amostra").update(update_data).eq("id", amostra_id).execute()
    
    return jsonify({
        'message': 'Amostra atualizada com sucesso',
        'data': response.data[0]
    }), 200


@amostra_bp.route('/<int:amostra_id>', methods=['DELETE'])
@token_required
def delete_amostra(amostra_id):
    supabase = get_supabase()
    user_id = request.user_id
    
    existing = supabase.table("amostra").select("id").eq("id", amostra_id).eq("user_id", user_id).execute()
    if not existing.data:
        return jsonify({'message': 'Amostra não encontrada'}), 404
    
    supabase.table("amostra").delete().eq("id", amostra_id).execute()
    
    return jsonify({'message': 'Amostra excluída com sucesso'}), 200
