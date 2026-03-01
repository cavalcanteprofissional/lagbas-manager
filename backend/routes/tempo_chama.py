from flask import Blueprint, request, jsonify
from utils.supabase import get_supabase
from utils.decorators import token_required

tempo_chama_bp = Blueprint("tempo_chama", __name__, url_prefix="/api/tempo-chama")


@tempo_chama_bp.route("", methods=["GET"])
@token_required
def get_tempos():
    supabase = get_supabase()
    user_id = request.user_id

    response = (
        supabase.table("tempo_chama").select("*").eq("user_id", user_id).execute()
    )

    return jsonify(response.data), 200


@tempo_chama_bp.route("", methods=["POST"])
@token_required
def create_tempo():
    supabase = get_supabase()
    user_id = request.user_id
    data = request.get_json()

    if (
        data.get("horas") is None
        or data.get("minutos") is None
        or data.get("segundos") is None
    ):
        return jsonify({"message": "Horas, minutos e segundos são obrigatórios"}), 400

    new_data = {
        "horas": data["horas"],
        "minutos": data["minutos"],
        "segundos": data["segundos"],
        "cilindro_id": data.get("cilindro_id"),
        "elemento_id": data.get("elemento_id"),
        "user_id": user_id,
    }

    response = supabase.table("tempo_chama").insert(new_data).execute()

    return jsonify(
        {"message": "Tempo de chama registrado com sucesso", "data": response.data[0]}
    ), 201


@tempo_chama_bp.route("/<int:tempo_id>", methods=["GET"])
@token_required
def get_tempo(tempo_id):
    supabase = get_supabase()
    user_id = request.user_id

    response = (
        supabase.table("tempo_chama")
        .select("*")
        .eq("id", tempo_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not response.data:
        return jsonify({"message": "Tempo de chama não encontrado"}), 404

    return jsonify(response.data[0]), 200


@tempo_chama_bp.route("/<int:tempo_id>", methods=["DELETE"])
@token_required
def delete_tempo(tempo_id):
    supabase = get_supabase()
    user_id = request.user_id

    existing = (
        supabase.table("tempo_chama")
        .select("id")
        .eq("id", tempo_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not existing.data:
        return jsonify({"message": "Tempo de chama não encontrado"}), 404

    supabase.table("tempo_chama").delete().eq("id", tempo_id).execute()

    return jsonify({"message": "Tempo de chama excluído com sucesso"}), 200
