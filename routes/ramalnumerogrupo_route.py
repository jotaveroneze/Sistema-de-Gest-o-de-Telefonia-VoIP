from flask import Blueprint, request, jsonify
from controllers.ramalnumerogrupo_controller import (
    listar_ramalnumerogrupo_por_grupo, listar_numerogrupo_disponiveis_por_ramal, adicionar_numerogrupos_ao_ramal,
    listar_ramalnumerogrupo_por_ramal, desvincular_ramal_numerogrupo, adicionar_ramais_ao_grupo,
    alterar_ordem_ramal_no_grupo
)
from flask_login import login_required


ramalnumerogrupo_bp = Blueprint("ramalnumerogrupo", __name__, url_prefix="/ramalnumerogrupo")


@ramalnumerogrupo_bp.route("/listar/<int:id_numerogrupo>", methods=["GET"])
@login_required
def listar_por_grupo_route(id_numerogrupo):
    retorno = listar_ramalnumerogrupo_por_grupo(id_numerogrupo)
    return jsonify(retorno)

@ramalnumerogrupo_bp.route("/desvincular/<int:id>", methods=["DELETE"])
@login_required
def desvincular_route(id):
    retorno = desvincular_ramal_numerogrupo(id)
    return jsonify(retorno)

@ramalnumerogrupo_bp.route("/adicionar", methods=["POST"])
@login_required
def adicionar_ramais_route():
    data = request.get_json()

    retorno = adicionar_ramais_ao_grupo(
        data["idnumerogrupo"],
        data["ramais"]
    )

    return jsonify(retorno)

@ramalnumerogrupo_bp.route("/listar-por-ramal/<int:id_ramal>", methods=["GET"])
@login_required
def listar_por_ramal_route(id_ramal):
    retorno = listar_ramalnumerogrupo_por_ramal(id_ramal)
    return jsonify(retorno)


@ramalnumerogrupo_bp.route("/numerogrupo-disponiveis/<int:id_ramal>", methods=["GET"])
@login_required
def listar_numerogrupo_disponiveis_route(id_ramal):
    retorno = listar_numerogrupo_disponiveis_por_ramal(id_ramal)
    return jsonify(retorno)


@ramalnumerogrupo_bp.route("/adicionar-por-ramal", methods=["POST"])
@login_required
def adicionar_numerogrupo_ao_ramal_route():
    data = request.get_json()

    retorno = adicionar_numerogrupos_ao_ramal(
        data["idramal"],
        data["grupos"]
    )

    return jsonify(retorno)

@ramalnumerogrupo_bp.route("/desvincular-por-ramal/<int:id>", methods=["DELETE"])
@login_required
def desvincular_por_ramal_route(id):
    retorno = desvincular_ramal_numerogrupo(id)
    return jsonify(retorno)

@ramalnumerogrupo_bp.route('/api/ramalnumerogrupo/<int:id_vinculo>/alterar-ordem', methods=['POST'])
# @login_required # Proteger a rota com autenticação
def api_alterar_ordem_ramal(id_vinculo):
    data = request.get_json()
    direcao = data.get('direcao')

    if not direcao or direcao not in ['subir', 'descer']:
        return jsonify({"success": False, "erro": "Direção inválida"}), 400

    try:
        resultado = alterar_ordem_ramal_no_grupo(id_vinculo, direcao)
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 404 # ou 400 dependendo do erro
    except Exception as e:
        # Log do erro
        return jsonify({"success": False, "erro": str(e)}), 500