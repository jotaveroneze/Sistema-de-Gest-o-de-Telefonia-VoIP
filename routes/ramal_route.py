from flask import Blueprint, request,jsonify
from controllers.ramal_controller import  (
    adicionar_ramal,
    listar_ramal, remover_ramal,
    editar_ramal, listar_ramal_em_uso,listar_ramal_vago,
    listar_ramal_detalhe, listar_ramais_disponiveis_por_grupo, listar_ramal_com_telefones
)
from flask_login import login_required

from models.ramal_model import Ramal

ramal_bp = Blueprint("ramal", __name__, url_prefix="/ramal")

@ramal_bp.route("/criar", methods=["POST"])
@login_required
def criar_ramal():
    data = request.get_json()

    try:
        numero = data.get("numero")
        gravado = data.get("gravado", 0)  # padrão 0
        id_tronco = data.get("idtronco")

        ramal = adicionar_ramal(numero, gravado, id_tronco)
        return jsonify(ramal), 201

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

    except Exception as e:
        print(e)  # para debug
        return jsonify({"erro": "Erro interno ao criar ramal"}), 500


@ramal_bp.route("/listar", methods=["GET"])
@login_required
def listar_ramal_route():
    return listar_ramal()

@ramal_bp.route("/listar_em_uso", methods=["GET"])
@login_required
def listar_ramal_em_uso_route():
    return listar_ramal_em_uso()

@ramal_bp.route("/listar_vago", methods=["GET"])
@login_required
def listar_ramal_vago_route():
    return listar_ramal_vago()

@ramal_bp.route("/listar_detalhe", methods=["GET"])
@login_required
def listar_ramal_detalhe_route():
    return listar_ramal_detalhe()

@ramal_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def removerramal(id):
    return remover_ramal(id)

@ramal_bp.route("/editar/<int:id_ramal>", methods=["PUT"])
@login_required
def editar_ramal_route(id_ramal):
    data = request.get_json()

    try:
        ramal = editar_ramal(
            id=id_ramal,
            numero=data.get("numero"),
            idtronco=data.get("idtronco"),
            gravado=data.get("gravado", 0)
        )

        return jsonify(ramal), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except Exception as e:
        print(e)
        return jsonify({"erro": "Erro interno ao editar ramal"}), 500


@ramal_bp.route("/listar-disponiveis/<int:id_numerogrupo>", methods=["GET"])
@login_required
def listar_ramais_disponiveis_route(id_numerogrupo):
    retorno = listar_ramais_disponiveis_por_grupo(id_numerogrupo)
    return jsonify(retorno)

@ramal_bp.route("/listar_com_telefones", methods=["GET"])
@login_required
def listar_ramal_com_telefones_route():
    return jsonify(listar_ramal_com_telefones())

@ramal_bp.route("/disponiveis", methods=["GET"])
def listar_ramais_disponiveis():
    try:
        ramais = (
            Ramal.query
            .filter(
                Ramal.status == 1,
                Ramal.idgrupocaptura.is_(None)
            )
            .order_by(Ramal.numero)
            .all()
        )

        resultado = [
            {
                "id": r.id,
                "numero": r.numero
            }
            for r in ramais
        ]

        return jsonify(resultado), 200

    except Exception as e:
        print("❌ Erro ao listar ramais disponíveis:", e)
        return jsonify({"erro": "Erro ao buscar ramais disponíveis"}), 500
