from flask import Blueprint, request
from controllers.usuario_controller import (
    criar_usuario_controller,
    listar_usuarios_controller, remover_usuario_controller,
    editar_usuario_controller, resetar_senha_controller
)
from flask_login import login_required


usuario_bp = Blueprint("usuario", __name__, url_prefix="/usuarios")


@usuario_bp.route("/criar", methods=["POST"])
@login_required
def criar_usuario():
    data = request.get_json()
    return criar_usuario_controller(data)


@usuario_bp.route("/listar", methods=["GET"])
@login_required
def listar_usuarios():
    return listar_usuarios_controller()


@usuario_bp.route("/remover_usuario/<int:id>", methods=["DELETE"])
@login_required
def remover_usuario(id):
    return remover_usuario_controller(id)

@usuario_bp.route("/editar/<int:id_usuario>", methods=["PUT"])
@login_required
def editar_usuario(id_usuario):
    return editar_usuario_controller(id_usuario)

@usuario_bp.route("/resetar_senha/<int:id>", methods=["DELETE"])
@login_required
def resetar_senha(id):
    return resetar_senha_controller(id)