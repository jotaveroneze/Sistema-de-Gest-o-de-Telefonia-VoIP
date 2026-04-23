from flask import Blueprint
from flask_login import login_required

from controllers.pessoatelefone_controller import (
    listar_pessoas_por_telefone_controller,
    listar_pessoas_disponiveis_controller,
    vincular_pessoa_telefone_controller,
    remover_pessoa_telefone_controller
)

pessoatelefone_bp = Blueprint(
    "pessoatelefone", __name__, url_prefix="/pessoatelefone"
)

@pessoatelefone_bp.route("/listar/<int:idtelefone>", methods=["GET"])
@login_required
def listar_pessoas(idtelefone):
    return listar_pessoas_por_telefone_controller(idtelefone)

@pessoatelefone_bp.route("/disponiveis/<int:idtelefone>", methods=["GET"])
@login_required
def listar_pessoas_disponiveis(idtelefone):
    return listar_pessoas_disponiveis_controller(idtelefone)

@pessoatelefone_bp.route("/vincular", methods=["POST"])
@login_required
def vincular():
    return vincular_pessoa_telefone_controller()

@pessoatelefone_bp.route("/<int:id_vinculo>", methods=["DELETE"])
@login_required
def remover(id_vinculo):
    return remover_pessoa_telefone_controller(id_vinculo)
