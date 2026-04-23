from flask import Blueprint, request, jsonify
from controllers.numerogrupo_controller import  (
    adicionar_numerogrupo,
    listar_numerogrupo, removernumerogrupo,
    editar_numerogrupo
)
from flask_login import login_required


numerogrupo_bp = Blueprint("numerogrupo", __name__, url_prefix="/numerogrupo")


@numerogrupo_bp.route("/adicionar", methods=["POST"])
@login_required
def criar_numerogrupo():
    data = request.get_json() or {}

    try:
        numero = data.get("numero")
        if not numero:
            raise ValueError("Número é obrigatório")

        descricao = data.get("descricao", "")
        gravado = int(data.get("gravado", 0))
        status = int(data.get("status", 1))
        iddepartamento = data.get("iddepartamento")
        idtronco = data.get("id_tronco")
        numerogrupo = adicionar_numerogrupo(
            numero=numero,
            descricao=descricao,
            gravado=gravado,
            status=status,
            iddepartamento=iddepartamento,
            tronco = idtronco# tratar dentro da função adicionar
        )

        return jsonify(numerogrupo), 201

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400




@numerogrupo_bp.route("/listar", methods=["GET"])
@login_required
def listar_numerogrupo_route():
    return listar_numerogrupo()


@numerogrupo_bp.route("/remover/<int:id>", methods=["DELETE"])
@login_required
def remover_numerogrupo(id):
    return removernumerogrupo(id)

@numerogrupo_bp.route("/editar/<int:id_numerogrupo>", methods=["PUT"])
@login_required
def editar_numerogrupo_route(id_numerogrupo):
    data = request.get_json() or {}

    try:
        numerogrupo = editar_numerogrupo(
            id_numerogrupo=id_numerogrupo,
            numero=data.get("numero"),
            iddepartamento=data.get("iddepartamento"),
            descricao=data.get("descricao"),
            gravado=bool(data.get("gravado", False)),
            tronco=data.get("idtronco")
        )
        return jsonify(numerogrupo)
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


