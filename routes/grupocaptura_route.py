from flask import Blueprint, jsonify,request
from sqlalchemy import and_

from controllers.grupocaptura_controller import (
    listar_grupocapturas,
    adicionar_grupocaptura,
    editar_grupocaptura,
    remover_grupocaptura, alterar_grupo_captura_controller, listar_ramais_por_grupo_captura_controller,
    vincular_ramal_grupo_captura_controller, desvincular_ramal_grupo_captura_controller
)
from flask_login import login_required

from extensions import db
from models import Telefone
from models.pessoa_model import Pessoa
from models.pessoatelefone_model import PessoaTelefone
from models.ramal_model import Ramal
from models.telefoneramal_model import TelefoneRamal

grupocaptura_bp = Blueprint("grupocaptura", __name__, url_prefix="/grupocaptura")

# GET /grupocaptura/listar
@grupocaptura_bp.route("/listar", methods=["GET"])
@login_required
def route_listar_grupocapturas():
    deps = listar_grupocapturas()
    return jsonify(deps)

# POST /grupocaptura/adicionar
@grupocaptura_bp.route("/adicionar", methods=["POST"])
@login_required
def route_adicionar_grupocaptura():
    data = request.get_json()
    nome = data.get("nome")
    try:
        dep = adicionar_grupocaptura(nome)
        return jsonify(dep), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# PUT /grupocaptura/editar/<id>
@grupocaptura_bp.route("/editar/<int:id>", methods=["PUT"])
@login_required
def route_editar_grupocaptura(id):
    data = request.get_json()
    nome = data.get("nome")
    try:
        dep = editar_grupocaptura(id, nome)
        return jsonify(dep)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except LookupError as e:
        return jsonify({"error": str(e)}), 404

# DELETE /grupocaptura/remover/<id>
@grupocaptura_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def route_remover_grupocaptura(id):
    try:
        return remover_grupocaptura(id)  # Retorna jsonify já pronto

    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

    except Exception as e:
        print("ERRO AO REMOVER GRUPO CAPTURA:", e)
        return jsonify({"erro": "Erro interno"}), 500



@grupocaptura_bp.route("/alterar-grupo-captura", methods=["POST"])
@login_required
def alterar_grupo_captura():
    data = request.get_json()
    return alterar_grupo_captura_controller(data)

@grupocaptura_bp.route("/ramais/<int:id_grupo>", methods=["GET"])
def listar_ramais_por_grupo_captura(id_grupo):
    try:
        resultado = listar_ramais_por_grupo_captura_controller(id_grupo)
        return jsonify(resultado), 200

    except Exception as e:
        print("❌ Erro ao listar ramais do grupo captura:", e)
        return jsonify({"erro": "Erro ao buscar ramais"}), 500

@grupocaptura_bp.route("/vincular-ramal", methods=["POST"])
def vincular_ramal_grupo_captura():
    try:
        data = request.get_json()
        return vincular_ramal_grupo_captura_controller(data)

    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao vincular ramal:", e)
        return jsonify({"erro": "Erro ao vincular ramal"}), 500


@grupocaptura_bp.route("/desvincular-ramal", methods=["POST"])
def desvincular_ramal_grupo_captura():
    data = request.get_json()
    return desvincular_ramal_grupo_captura_controller(data)

