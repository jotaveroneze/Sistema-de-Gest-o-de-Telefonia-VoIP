from flask import Blueprint, jsonify,request
from controllers.departamento_controller import (
    listar_departamentos,
    adicionar_departamento,
    editar_departamento,
    remover_departamento
)
from flask_login import login_required

departamento_bp = Blueprint("departamento", __name__, url_prefix="/departamento")

# GET /departamento/listar
@departamento_bp.route("/listar", methods=["GET"])
@login_required
def route_listar_departamentos():
    deps = listar_departamentos()
    return jsonify(deps)

# POST /departamento/adicionar
@departamento_bp.route("/adicionar", methods=["POST"])
@login_required
def route_adicionar_departamento():
    data = request.get_json()
    nome = data.get("nome")
    idsecretaria = data.get("idsecretaria")
    try:
        dep = adicionar_departamento(nome, idsecretaria)
        return jsonify(dep), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# PUT /departamento/editar/<id>
@departamento_bp.route("/editar/<int:id>", methods=["PUT"])
@login_required
def route_editar_departamento(id):
    data = request.get_json()
    nome = data.get("nome")
    idsecretaria = data.get("idsecretaria")
    try:
        dep = editar_departamento(id, nome, idsecretaria)
        return jsonify(dep)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except LookupError as e:
        return jsonify({"error": str(e)}), 404

# DELETE /departamento/remover/<id>
@departamento_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def route_remover_departamento(id):
    try:
        return remover_departamento(id)  # Retorna jsonify já pronto

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except Exception as e:
        print("ERRO AO REMOVER DEPARTAMENTO:", e)
        return jsonify({"erro": "Erro interno"}), 500

