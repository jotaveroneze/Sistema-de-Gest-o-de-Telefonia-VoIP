from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from controllers.home_controller import get_dashboard_dados, grafico_telefones_secretaria_controller

home_bp = Blueprint("home", __name__)

@home_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard_dados():
    # Debug opcional (pode remover depois)
    print("Usuário autenticado:", current_user.is_authenticated)

    dados = get_dashboard_dados()

    return jsonify(dados), 200

@home_bp.route("/grafico-telefones", methods=["GET"])
@login_required
def grafico_telefones_secretaria():
    return grafico_telefones_secretaria_controller()

