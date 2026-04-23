from flask import Blueprint, request, jsonify
from controllers.telefone_controller import (
    adicionar_telefone, listar_telefone, remover_telefone, editar_telefone
)
from flask_login import login_required
from models.telefone_model import Telefone

telefone_bp = Blueprint("telefone", __name__, url_prefix="/telefone")

@telefone_bp.route("/criar", methods=["POST"])
@login_required
def route_adicionar_telefone():
    data = request.get_json()
    resultado, status = adicionar_telefone(data)
    return jsonify(resultado), status

@telefone_bp.route("/listar", methods=["GET"])  # ✅ Já tem, usa sua função paginada
@login_required
def listar_telefone_route():
    return listar_telefone()

# ✅ ADICIONE ESTA ROTA (para carregarTodasTelefones no JS)
@telefone_bp.route("/todas", methods=["GET"])
@login_required
def listar_todas_telefones():
    telefones = Telefone.query.filter_by(status=1).order_by(Telefone.patrimonio).all()
    return jsonify([t.to_dict() for t in telefones])

@telefone_bp.route("/remover_telefone/<int:id>", methods=["DELETE"])
@login_required
def removertelefone(id):
    return remover_telefone(id)

@telefone_bp.route("/editar/<int:id>", methods=["GET"])
@login_required
def route_obter_telefone(id):
    telefone = Telefone.query.get(id)
    if not telefone:
        return jsonify({"erro": "Telefone não encontrado"}), 404
    return jsonify(telefone.to_dict()), 200

@telefone_bp.route("/editar/<int:id>", methods=["PUT"])
@login_required
def route_editar_telefone(id):
    data = request.get_json()
    resultado, status = editar_telefone(id, data)
    return jsonify(resultado), status
