from flask import Blueprint, jsonify
from flask_login import login_required
from controllers.lixeria_controller import listar_lixeira, restaurar_pendencia_controller, excluir_definitivo_controller

lixeira_bp = Blueprint("lixeira", __name__, url_prefix="/lixeira")


@lixeira_bp.route("/listar", methods=["GET"])
@login_required
def route_listar_lixeira():
    return jsonify(listar_lixeira()), 200


@lixeira_bp.route("/restaurar/<int:id>", methods=["PUT"])
def restaurar(id):
    resposta, status = restaurar_pendencia_controller(id)
    return jsonify(resposta), status

@lixeira_bp.route("/excluir/<int:id>", methods=["PUT"])
def excluir_definitivo(id):
    resposta, status = excluir_definitivo_controller(id)
    return jsonify(resposta), status
