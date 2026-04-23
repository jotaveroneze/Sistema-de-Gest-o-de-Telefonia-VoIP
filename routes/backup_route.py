from flask import Blueprint, jsonify,request
from controllers.backup_controller import (
backup_manual
)
from flask_login import login_required

backup_bp = Blueprint("backup", __name__, url_prefix="/backup")


@backup_bp.route("", methods=["GET"])
@login_required
def gerar_backup():
    try:
        arquivo = backup_manual()
        return jsonify({"success": True, "mensagem": f"Backup criado com sucesso: {arquivo}"})
    except Exception as e:
        return jsonify({"success": False, "mensagem": f"Erro ao gerar backup: {str(e)}"})