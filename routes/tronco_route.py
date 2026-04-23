from flask import Blueprint, request, jsonify
from controllers.tronco_controller import  (
    adicionar_tronco,
    listar_tronco, removertronco,
    editar_tronco
)
from flask_login import login_required


tronco_bp = Blueprint("tronco", __name__, url_prefix="/tronco")


@tronco_bp.route("/criar", methods=["POST"])
@login_required
def criar_tronco():
    data = request.get_json()

    try:
        tronco = adicionar_tronco(
            numerochave=data.get("numerochave"),
            ramalinicial=data.get("ramal_inicial"),
            ramalfinal=data.get("ramal_final"),
            id_operadora=data.get("idoperadora")
        )

        return jsonify(tronco), 201

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

    except Exception as e:
        return jsonify({"erro": "Erro interno ao criar tronco"}), 500



@tronco_bp.route("/listar", methods=["GET"])
@login_required
def listar_tronco_route():
    return listar_tronco()


@tronco_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def remover_tronco(id):
    return removertronco(id)

@tronco_bp.route("/editar/<int:id_tronco>", methods=["PUT"])
@login_required
def editar_tronco_route(id_tronco):
    data = request.get_json()

    try:
        tronco = editar_tronco(
            id=id_tronco,
            numerochave=data.get("numerochave"),
            ramalinicial=data.get("ramalinicial"),
            ramalfinal=data.get("ramalfinal"),
            idoperadora=data.get("idoperadora")
        )

        return jsonify(tronco), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except Exception as e:
        return jsonify({"erro": "Erro interno ao editar tronco"}), 500

