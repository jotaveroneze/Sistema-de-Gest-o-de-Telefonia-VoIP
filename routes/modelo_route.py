from flask import Blueprint, jsonify,request
from controllers.modelo_controller import (
    listar_modelo,
    adicionar_modelo,
    editar_modelo,
    remover_modelo
)
from flask_login import login_required

modelo_bp = Blueprint("modelo", __name__, url_prefix="/modelo")

# GET /modelo/listar
@modelo_bp.route("/listar", methods=["GET"])
@login_required
def route_listar_modelo():
    deps = listar_modelo()
    return jsonify(deps)

# POST /modelo/adicionar
@modelo_bp.route("/adicionar", methods=["POST"])
@login_required
def route_adicionar_modelo():
    data = request.get_json()
    nome = data.get("nome")

    try:
        dep = adicionar_modelo(nome)
        return jsonify(dep), 201

    except ValueError as e:
        # ✅ Captura tanto "Nome obrigatório" quanto "já existe"
        return jsonify({"erro": str(e)}), 409

    except Exception as e:
        return jsonify({"erro": "Erro interno"}), 500

# PUT /modelo/editar/<id>
@modelo_bp.route("/editar/<int:id>", methods=["PUT"])
@login_required
def route_editar_modelo(id):
    data = request.get_json()
    nome = data.get("nome")
    try:
        dep = editar_modelo(id, nome)
        return jsonify(dep)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except LookupError as e:
        return jsonify({"error": str(e)}), 404

# DELETE /modelo/remover/<id>
@modelo_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def route_remover_modelo(id):
    try:
        return remover_modelo(id)  # Retorna jsonify já pronto

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except Exception as e:
        print("ERRO AO REMOVER modelo:", e)
        return jsonify({"erro": "Erro interno"}), 500

