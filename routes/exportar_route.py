from flask import Blueprint
from controllers.exportar_controller import export_excel_controller
from flask_login import login_required

exportar_bp = Blueprint("export_bp", __name__)

@exportar_bp.route("/export_excel", methods=["POST"])
@login_required
def export_excel():
    return export_excel_controller()
