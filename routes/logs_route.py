from flask import Blueprint, jsonify
from flask_login import login_required
from controllers.logs_controller import listar_logs  # ← IMPORT DA FUNÇÃO

logs_bp = Blueprint("logs", __name__, url_prefix="/logs")

@logs_bp.route("/listar", methods=["GET"])
@login_required
def route_listar_logs():
    dados = listar_logs()  # ← SEM .listar()
    return jsonify(dados)  # ✅ Dict → JSON

@logs_bp.route("/debug", methods=["GET"])  # ← Para teste
def debug_logs():
    dados = listar_logs()
    return jsonify(dados)
