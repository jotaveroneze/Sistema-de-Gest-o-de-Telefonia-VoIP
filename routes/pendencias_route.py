from flask import Blueprint, jsonify, render_template, session, request
from flask_login import login_required
from controllers.pendencias_controller import listar_pendencias, listar_pendenciasfinalizadas, remover_pendencia, \
    entregar_pendencia, devolver_pendencia, criar_pendencia, finalizar_pendencias_ramais, \
    finalizar_pendencias_numerovirtual, finalizar_pendencias_pessoa, finalizar_pendencias_todas, \
    finalizar_pendencias_grupocaptura
from models.pendencias_model import Pendencias

pendencias_bp = Blueprint('pendencias', __name__, url_prefix="/pendencias")

@pendencias_bp.route("/")
@pendencias_bp.route("/<int:page>")
@login_required
def index(page=1):
    return render_template("pendencias.html", page=page)

@pendencias_bp.route("/listarfinalizadas", methods=["GET"])
@login_required
def route_listar_pendenciasfinalizadas():
    return listar_pendenciasfinalizadas()  # ✅ Controller faz tudo!



@pendencias_bp.route("/listar", methods=["GET"])
@login_required
def route_listar_pendencias():
    # Controller já lê request.args + faz tudo!
    return listar_pendencias()  # ✅ Única linha!

# DELETE
@pendencias_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def route_remover_pendencia(id):
    try:
        return remover_pendencia(id)  # Retorna jsonify já pronto

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except Exception as e:
        print("ERRO AO REMOVER PENDÊNCIA:", e)
        return jsonify({"erro": "Erro interno"}), 500

@pendencias_bp.route("/entregar/<int:id>", methods=["DELETE"])
@login_required
def route_entregar_pendencia(id):
    try:
        return entregar_pendencia(id)  # Retorna jsonify já pronto

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except Exception as e:
        print("ERRO AO FINALIZAR PENDÊNCIA:", e)
        return jsonify({"erro": "Erro interno"}), 500

@pendencias_bp.route("/devolver/<int:id>", methods=["DELETE"])
@login_required
def route_devolver_pendencia(id):
    try:
        return devolver_pendencia(id)  # Retorna jsonify já pronto

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except Exception as e:
        print("ERRO AO DEVOLVER PENDÊNCIA:", e)
        return jsonify({"erro": "Erro interno"}), 500

@pendencias_bp.route("/criar/<string:tipopendencia>", methods=["POST"])
@login_required
def criar(tipopendencia):
    idusuarioresponsavel = session['user_id']
    return criar_pendencia(descricaotipopendencia=tipopendencia, idusuarioresponsavel=idusuarioresponsavel)

@pendencias_bp.route("/finalizar-ramais", methods=["DELETE"])
@login_required
def route_finalizar_pendencias_ramais():
    try:
        return finalizar_pendencias_ramais()

    except Exception as e:
        print("ERRO NA ROTA FINALIZAR RAMAIS:", e)
        return jsonify({"erro": "Erro interno"}), 500


@pendencias_bp.route("/finalizar-numerovirtual", methods=["DELETE"])
@login_required
def route_finalizar_pendencias_numerovirtual():
    try:
        return finalizar_pendencias_numerovirtual()

    except Exception as e:
        print("ERRO NA ROTA FINALIZAR NUMEROS VIRTUAIS:", e)
        return jsonify({"erro": "Erro interno"}), 500

@pendencias_bp.route("/finalizar-pessoa", methods=["DELETE"])
@login_required
def route_finalizar_pendencias_pessoa():
    try:
        return finalizar_pendencias_pessoa()

    except Exception as e:
        print("ERRO NA ROTA FINALIZAR PESSOA:", e)
        return jsonify({"erro": "Erro interno"}), 500

@pendencias_bp.route("/finalizar-grupocaptura", methods=["DELETE"])
@login_required
def route_finalizar_pendencias_grupocaptura():
    try:
        return finalizar_pendencias_grupocaptura()

    except Exception as e:
        print("ERRO NA ROTA FINALIZAR GRUPO DE CAPTURA:", e)
        return jsonify({"erro": "Erro interno"}), 500

@pendencias_bp.route("/finalizar-todas", methods=["DELETE"])
@login_required
def route_finalizar_pendencias_todas():
    try:
        return finalizar_pendencias_todas()

    except Exception as e:
        print("ERRO NA ROTA FINALIZAR PENDENCIAS:", e)
        return jsonify({"erro": "Erro interno"}), 500


@pendencias_bp.route("/abertas")
def pendencias_abertas():
    qtd = Pendencias.query.filter_by(status=1).count()  # supondo status=1 = aberta
    return jsonify({"qtd": qtd})