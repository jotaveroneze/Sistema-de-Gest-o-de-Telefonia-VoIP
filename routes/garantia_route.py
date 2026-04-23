from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required

from controllers.garantia_controller import (
    listar_garantias,
    listar_garantias_por_telefone,
    cadastrar_garantia,
    finalizar_garantia,
    excluir_garantia,
    devolver_garantia, gerar_pdf_termo_garantia, criar_garantia_telefone
)
from extensions import db

garantia_bp = Blueprint("garantia", __name__)

@garantia_bp.route("/garantia/listar", methods=["GET"])
@login_required
def route_listar_garantias():
    return jsonify(listar_garantias()), 200

@garantia_bp.route("/garantia/telefone/<int:idtelefone>", methods=["GET"])
@login_required
def route_listar_por_telefone(idtelefone):
    return jsonify(listar_garantias_por_telefone(idtelefone)), 200

@garantia_bp.route("/garantia/cadastrar", methods=["POST"])
@login_required
def route_cadastrar_garantia():
    dados = request.json
    cadastrar_garantia(dados)
    return jsonify({"message": "Garantia cadastrada com sucesso"}), 201

@garantia_bp.route("/garantia/finalizar/<int:id>", methods=["PUT"])
@login_required
def route_finalizar_garantia(id):
    finalizar_garantia(id)
    return jsonify({"message": "Garantia finalizada com sucesso"}), 200


@garantia_bp.route("/garantia/excluir/<int:id>", methods=["PUT"])
@login_required
def excluir(id):
    return jsonify(excluir_garantia(id))


@garantia_bp.route("/garantia/devolver/<int:id>", methods=["PUT"])
@login_required
def devolver(id):
    data = request.get_json()  # pega o JSON enviado pelo fetch
    solucao = data.get("solucao", "")  # se não veio, salva como vazio

    # Chama a função que faz a atualização no banco
    sucesso = devolver_garantia(id, solucao)

    if sucesso:
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Garantia não encontrada"}), 404


@garantia_bp.route("/garantia/gerartermogarantia", methods=["POST"])
@login_required
def gerartermo_garantia():
    data = request.get_json()

    if not data or "telefones" not in data:
        return jsonify({"error": "Lista de telefones não enviada"}), 400

    lista_telefones = data["telefones"]
    defeito_desc = data.get("defeito", "Garantia registrada via termo")  # pega defeito do frontend

    if not isinstance(lista_telefones, list) or not lista_telefones:
        return jsonify({"error": "Lista de telefones inválida"}), 400

    # 1️⃣ Gera o PDF
    pdf_buffer = gerar_pdf_termo_garantia(lista_telefones)

    # 2️⃣ Cria a garantia para cada telefone, passando o defeito
    for idtelefone in lista_telefones:
        criar_garantia_telefone(idtelefone, defeito_desc)

    db.session.commit()  # 🔥 grava tudo de uma vez

    # 3️⃣ Retorna o PDF
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="termo_garantia_telefone.pdf"
    )

