from flask import Blueprint
from controllers.alterarsenha_controller import alterar_senha_controller

alterarsenha_bp = Blueprint("alterarsenha", __name__)

@alterarsenha_bp.route("/alterar_senha", methods=["POST"])
def alterar_senha():
    return alterar_senha_controller()
