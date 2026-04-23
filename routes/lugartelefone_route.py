from flask import Blueprint, jsonify,request
from controllers.lugartelefone_controller import obter_lugar, listar_lugares, criar_lugar, editar_lugar, remover_lugar
from flask_login import login_required
from models.lugartelefone_model import LugarTelefone

lugartelefone_bp = Blueprint("lugartelefone", __name__, url_prefix="/lugartelefone")

# GET /lugartelefone/listar
@lugartelefone_bp.route("/listar", methods=["GET"])
@login_required
def route_listar_lugartelefones():
    return listar_lugares()


# POST /lugartelefone/adicionar
@lugartelefone_bp.route("/criar", methods=["POST"])
@login_required
def criar():
    return criar_lugar()

@lugartelefone_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def removerlugar(id):
    return remover_lugar(id)

@lugartelefone_bp.route("/editar/<int:id>", methods=["PUT"])
@login_required
def route_editar_lugar(id):
    return editar_lugar(id)

@lugartelefone_bp.route("/<int:id>", methods=["GET"])
@login_required
def route_obter_lugar(id):
    resultado, status = obter_lugar(id)
    return jsonify(resultado), status

@lugartelefone_bp.route("/todos")
@login_required
def listar_todos_lugares():
    return listar_lugares()