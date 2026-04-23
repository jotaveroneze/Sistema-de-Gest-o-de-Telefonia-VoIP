from flask import Blueprint, jsonify
from flask_login import login_required

from controllers.grupocaptura_controller import handle_grupocaptura
from controllers.rotas_controller import (
    handle_home,
    handle_usuario,
    handle_departamento,
    handle_alterarsenha,
    handle_telefone,
    handle_modelos,
    handle_ramal,
    handle_empresa,
    handle_pessoa,
    handle_tronco,
    handle_numerogrupo,
    handle_pendencias,
    handle_grupocaptura,
    handle_lugartelefone,
    handle_logs,
    handle_operadora,
    handle_lixeira
)

from controllers.home_controller import get_dashboard_dados

rotas_bp = Blueprint("rotas", __name__)

@rotas_bp.route("/home")
@login_required
def home():
    return handle_home()

@rotas_bp.route("/usuario")
@login_required
def usuario():
    return handle_usuario()

@rotas_bp.route("/departamento")
@login_required
def departamento():
    return handle_departamento()

@rotas_bp.route("/alterarsenha")
@login_required
def alterarsenha():
    return handle_alterarsenha()

@rotas_bp.route("/telefone")
@login_required
def telefone():
    return handle_telefone()

@rotas_bp.route("/modelo")
@login_required
def modelo():
    return handle_modelos()

@rotas_bp.route("/ramais")
@login_required
def ramal():
    return handle_ramal()

@rotas_bp.route("/empresa")
@login_required
def empresa():
    return handle_empresa()

@rotas_bp.route("/pessoas")
@login_required
def pessoa():
    return handle_pessoa()

@rotas_bp.route("/tronco")
@login_required
def tronco():
    return handle_tronco()

@rotas_bp.route("/numerogrupo")
@login_required
def numerogrupo():
    return handle_numerogrupo()

@rotas_bp.route("/pendencias")
@login_required
def pendencias():
    return handle_pendencias()

@rotas_bp.route("/grupocaptura")
@login_required
def grupocaptura():
    return handle_grupocaptura()

@rotas_bp.route("/lugartelefone")
@login_required
def lugartelefone():
    return handle_lugartelefone()

@rotas_bp.route("/logs")
@login_required
def logs():
    return handle_logs()

@rotas_bp.route("/operadora")
@login_required
def operadora():
    return handle_operadora()

@rotas_bp.route("/lixeira")
@login_required
def lixeira():
    return handle_lixeira()

@rotas_bp.route("/api/dashboard")
@login_required
def dashboard_dados():
    return jsonify(get_dashboard_dados())