from flask import Blueprint, request, jsonify
from flask_login import login_required

from controllers.entregas_controller import entregarTelefone, entregar_telefones_selecionados

entregas_bp = Blueprint("entregas", __name__, url_prefix="/entregas")


@entregas_bp.route("/entregar", methods=["POST"])
@login_required
def entregar():
    data = request.get_json()
    return entregarTelefone(data)

@entregas_bp.route("/entregarSelecionados", methods=["POST"])
@login_required
def entregar_selecionados():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Dados não enviados"}), 400

    return entregar_telefones_selecionados(data)