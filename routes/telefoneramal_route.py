from flask import Blueprint, request, jsonify
from flask_login import login_required

from controllers.telefoneramal_controller import  (
    listar_pessoas_do_ramal,listar_telefones_disponiveis,
    remover_telefone_do_ramal,vincular_telefones,
    listar_ramais_disponiveis_para_telefone,
    listar_ramais_vinculados_por_telefone_controller,
    vincular_ramais_telefone_controller,
    remover_ramal_telefone_controller
)

telefoneramal_bp = Blueprint("telefoneramal", __name__, url_prefix="/telefoneramal")


# 🔍 Listar pessoas vinculadas ao ramal
@telefoneramal_bp.route("/listar/<int:id_ramal>/pessoas", methods=["GET"])
@login_required
def route_listar_pessoas_do_ramal(id_ramal):
    return listar_pessoas_do_ramal(id_ramal)

# ❌ Remover pessoa do ramal
@telefoneramal_bp.route("/remover/<int:id_pessoatelefone>", methods=["DELETE"])
@login_required
def route_remover_telefone_do_ramal(id_pessoatelefone):
    return remover_telefone_do_ramal(id_pessoatelefone)

@telefoneramal_bp.route("/<int:idramal>/telefones-disponiveis", methods=["GET"])
@login_required
def route_listar_telefones_disponiveis(idramal):
    return listar_telefones_disponiveis(idramal)

@telefoneramal_bp.route("/vincular_telefones", methods=["POST"])
@login_required
def route_vincular_telefones():
    return vincular_telefones()

@telefoneramal_bp.route(
    "/listar_disponiveis_para_telefone/<int:id_telefone>",
    methods=["GET"]
)
@login_required
def route_listar_ramais_disponiveis_para_telefone(id_telefone):
    return listar_ramais_disponiveis_para_telefone(id_telefone)

@telefoneramal_bp.route("/listar_por_telefone/<int:id_telefone>", methods=["GET"])
@login_required
def listar_ramais_vinculados_por_telefone_route(id_telefone):
    return listar_ramais_vinculados_por_telefone_controller(id_telefone)

@telefoneramal_bp.route("/vincular", methods=["POST"])
@login_required
def vincular_ramais_telefone_route():
    return vincular_ramais_telefone_controller()

@telefoneramal_bp.route("/<int:id_vinculo>", methods=["DELETE"])
@login_required
def remover_ramal_telefone_route(id_vinculo):
    return remover_ramal_telefone_controller(id_vinculo)