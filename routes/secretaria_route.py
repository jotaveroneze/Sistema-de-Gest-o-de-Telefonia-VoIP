from flask import Blueprint, jsonify,request
from flask import render_template

from controllers.departamento_controller import adicionar_departamento
from controllers.secretaria_controller import (
    listar_secretaria,
    adicionar_secretaria,
    editar_secretaria,
    remover_secretaria
)
from flask_login import login_required

secretaria_bp = Blueprint("secretaria", __name__, url_prefix="/secretaria")

@secretaria_bp.route("/", methods=["GET"])
@login_required
def nova_tela():
    return render_template('secretaria.html')


@secretaria_bp.route("/listar", methods=["GET"])
@login_required
def route_listar_secretarias():
    deps = listar_secretaria()
    return jsonify(deps)


@secretaria_bp.route("/adicionar", methods=["POST"])
@login_required
def route_adicionar_secretaria():
    data = request.get_json()
    nome = data.get("nome")
    sigla = data.get("sigla")
    try:
        dep = adicionar_secretaria(nome, sigla)
        return dep
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@secretaria_bp.route("/editar/<int:id>", methods=["PUT"])
@login_required
def route_editar_secretaria(id):
    data = request.get_json()

    sigla = data.get("sigla")
    nome = data.get("nome")

    try:
        dep = editar_secretaria(id, sigla, nome)
        return jsonify(dep), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except LookupError as e:
        return jsonify({"error": str(e)}), 404



@secretaria_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def route_remover_secretaria(id):
    print('remover secretaria')
    try:
        return remover_secretaria(id)  # Retorna jsonify já pronto

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except Exception as e:
        print("ERRO AO REMOVER SECRETARIA:", e)
        return jsonify({"erro": "Erro interno"}), 500

