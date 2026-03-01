from flask import Blueprint, request, jsonify
from utils.supabase import get_supabase
from utils.decorators import token_required
from config import ELEMENTOS_PADRAO

elemento_bp = Blueprint("elemento", __name__, url_prefix="/api/elementos")


@elemento_bp.route("", methods=["GET"])
@token_required
def get_elementos():
    supabase = get_supabase()
    user_id = request.user_id

    response = supabase.table("elementos").select("*").eq("user_id", user_id).execute()

    if not response.data:
        for elemento in ELEMENTOS_PADRAO:
            supabase.table("elementos").insert(
                {
                    "nome": elemento["nome"],
                    "consumo_lpm": elemento["consumo_lpm"],
                    "user_id": user_id,
                }
            ).execute()

        response = (
            supabase.table("elementos").select("*").eq("user_id", user_id).execute()
        )

    return jsonify(response.data), 200


@elemento_bp.route("", methods=["POST"])
@token_required
def create_elemento():
    supabase = get_supabase()
    user_id = request.user_id
    data = request.get_json()

    if not data.get("nome"):
        return jsonify({"message": "Nome é obrigatório"}), 400

    existing = (
        supabase.table("elementos")
        .select("id")
        .eq("nome", data["nome"])
        .eq("user_id", user_id)
        .execute()
    )
    if existing.data:
        return jsonify({"message": "Elemento já existe"}), 400

    new_data = {
        "nome": data["nome"],
        "consumo_lpm": data.get("consumo_lpm", 1.5),
        "user_id": user_id,
    }

    response = supabase.table("elementos").insert(new_data).execute()

    return jsonify(
        {"message": "Elemento criado com sucesso", "data": response.data[0]}
    ), 201


@elemento_bp.route("/<int:elemento_id>", methods=["GET"])
@token_required
def get_elemento(elemento_id):
    supabase = get_supabase()
    user_id = request.user_id

    response = (
        supabase.table("elementos")
        .select("*")
        .eq("id", elemento_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not response.data:
        return jsonify({"message": "Elemento não encontrado"}), 404

    return jsonify(response.data[0]), 200


@elemento_bp.route("/<int:elemento_id>", methods=["PUT"])
@token_required
def update_elemento(elemento_id):
    supabase = get_supabase()
    user_id = request.user_id
    data = request.get_json()

    existing = (
        supabase.table("elementos")
        .select("id")
        .eq("id", elemento_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not existing.data:
        return jsonify({"message": "Elemento não encontrado"}), 404

    if data.get("nome"):
        duplicate = (
            supabase.table("elementos")
            .select("id")
            .eq("nome", data["nome"])
            .eq("user_id", user_id)
            .neq("id", elemento_id)
            .execute()
        )
        if duplicate.data:
            return jsonify({"message": "Nome já existe"}), 400

    update_data = {
        "nome": data.get("nome", existing.data[0]["nome"]),
        "consumo_lpm": data.get("consumo_lpm", existing.data[0]["consumo_lpm"]),
    }

    response = (
        supabase.table("elementos").update(update_data).eq("id", elemento_id).execute()
    )

    return jsonify(
        {"message": "Elemento atualizado com sucesso", "data": response.data[0]}
    ), 200


@elemento_bp.route("/<int:elemento_id>", methods=["DELETE"])
@token_required
def delete_elemento(elemento_id):
    supabase = get_supabase()
    user_id = request.user_id

    existing = (
        supabase.table("elementos")
        .select("id")
        .eq("id", elemento_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not existing.data:
        return jsonify({"message": "Elemento não encontrado"}), 404

    supabase.table("elementos").delete().eq("id", elemento_id).execute()

    return jsonify({"message": "Elemento excluído com sucesso"}), 200
