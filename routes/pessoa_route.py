from flask import Blueprint, jsonify,request
from controllers.pessoa_controller import (
    listar_pessoa,
    adicionar_pessoa,
    editar_pessoa,
    remover_pessoa
)
from flask_login import login_required

from models.pessoa_model import Pessoa

pessoa_bp = Blueprint("pessoa", __name__, url_prefix="/pessoa")

# GET /pessoa/listar
@pessoa_bp.route("/listar", methods=["GET"])
@login_required
def route_listar_pessoa():
    deps = listar_pessoa()
    return jsonify(deps)

# POST /pessoa/adicionar
@pessoa_bp.route("/adicionar", methods=["POST"])
@login_required
def route_adicionar_pessoa():
    data = request.get_json()

    try:
        pessoa = adicionar_pessoa(
            nome=data.get("nome"),
            funcional=data.get("funcional"),
            cpf=data.get("cpf"),
            id_vinculo=data.get("idvinculo"),
            id_departamento=data.get("iddepartamento"),
            id_empresa=data.get("idempresa")
        )

        return jsonify(pessoa), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "Erro interno ao cadastrar pessoa"}), 500


# PUT /pessoa/editar/<id>
@pessoa_bp.route("/editar/<int:id>", methods=["PUT"])
@login_required
def route_editar_pessoa(id):
    data = request.get_json()

    try:
        pessoa = editar_pessoa(id, data)
        return jsonify(pessoa), 200

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

# DELETE /pessoa/remover/<id>
@pessoa_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def route_remover_pessoa(id):
    try:
        return remover_pessoa(id)  # Retorna jsonify já pronto

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except Exception as e:
        print("ERRO AO REMOVER pessoa:", e)
        return jsonify({"erro": "Erro interno"}), 500

@pessoa_bp.route("/todas")
@login_required
def listar_todas_pessoas():
    todas = Pessoa.query.filter_by(status=1).order_by(Pessoa.nome).all()
    return jsonify([p.to_dict() for p in todas])  # ~500 pessoas? Rápido!

