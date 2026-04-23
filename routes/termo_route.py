from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required

from controllers.termo_controller import gerar_pdf_termo_telefone

termo_bp = Blueprint("termo", __name__, url_prefix="/termo")


@termo_bp.route("/gerartermo", methods=["POST"])
@login_required
def gerartermo():
    data = request.get_json()

    if not data or "telefones" not in data:
        return jsonify({"error": "Lista de telefones não enviada"}), 400

    lista_telefones = data["telefones"]

    if not isinstance(lista_telefones, list) or not lista_telefones:
        return jsonify({"error": "Lista de telefones inválida"}), 400

    pdf_buffer = gerar_pdf_termo_telefone(lista_telefones)

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="termo_entrega_telefone.pdf"
    )