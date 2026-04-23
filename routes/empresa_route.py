from flask import Blueprint, jsonify,request
from controllers.empresa_controller import (
    listar_empresa,
    adicionar_empresa,
    editar_empresa,
    remover_empresa
)
from flask_login import login_required

empresa_bp = Blueprint("empresa", __name__, url_prefix="/empresa")

# GET /modelo/listar
@empresa_bp.route("/listar", methods=["GET"])
@login_required
def route_listar_empresa():
    deps = listar_empresa()
    return jsonify(deps)

# POST /empresa/adicionar
@empresa_bp.route("/adicionar", methods=["POST"])
@login_required
def route_adicionar_empresa():
    data = request.get_json()
    nome = data.get("nome")
    try:
        dep = adicionar_empresa(nome)
        return jsonify(dep), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# PUT /empresa/editar/<id>
@empresa_bp.route("/editar/<int:id>", methods=["PUT"])
@login_required
def route_editar_empresa(id):
    data = request.get_json()
    nome = data.get("nome")
    try:
        dep = editar_empresa(id, nome)
        return jsonify(dep)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except LookupError as e:
        return jsonify({"error": str(e)}), 404

# DELETE /empresa/remover/<id>
@empresa_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def route_remover_empresa(id):
    try:
        return remover_empresa(id)  # Retorna jsonify já pronto

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except Exception as e:
        print("ERRO AO REMOVER empresa:", e)
        return jsonify({"erro": "Erro interno"}), 500

