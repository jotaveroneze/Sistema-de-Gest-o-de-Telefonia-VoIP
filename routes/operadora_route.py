from flask import Blueprint, request, jsonify
from controllers.operadora_controller import  (
    adicionar_operadora,
    listaroperadora, removeroperadora,
    editar_operadora
)
from flask_login import login_required


operadora_bp = Blueprint("operadora", __name__, url_prefix="/operadora")


@operadora_bp.route("/criar", methods=["POST"])
@login_required
def criar_operadora():
    data = request.get_json()

    try:
        operadora = adicionar_operadora(
            nome=data.get("nome"),
            contrato=data.get("contrato"),
            processo=data.get("processo")
        )

        return jsonify(operadora), 201

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

    except Exception as e:
        return jsonify({"erro": "Erro interno ao criar operadora"}), 500



@operadora_bp.route("/listar", methods=["GET"])
@login_required
def listar_operadora_route():
    return listaroperadora()


@operadora_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def remover_operadora(id):
    return removeroperadora(id)

@operadora_bp.route("/editar/<int:id_operadora>", methods=["PUT"])
@login_required
def editar_operadora_route(id_operadora):
    data = request.get_json()

    try:
        operadora = editar_operadora(
            id=id_operadora,
            nome=data.get("nome"),
            contrato=data.get("contrato"),
            processo=data.get("processo")
        )

        return jsonify(operadora), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except Exception:
        return jsonify({"erro": "Erro interno ao editar operadora"}), 500

