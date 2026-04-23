from flask import Blueprint
from flask_login import login_required

from controllers.relatorio_controller import gerar_relatorio_dashboard_pdf_controller

relatorio_bp = Blueprint("relatorio", __name__)

@relatorio_bp.route("/relatorio/dashboard/pdf", methods=["GET"])
@login_required
def relatorio_dashboard_pdf():
    return gerar_relatorio_dashboard_pdf_controller()
