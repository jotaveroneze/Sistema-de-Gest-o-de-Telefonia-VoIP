from flask import Blueprint, jsonify,request
from controllers.vinculo_controller import (
    listar_vinculo,

)
from flask_login import login_required

vinculo_bp = Blueprint("vinculo", __name__, url_prefix="/vinculo")

# GET /modelo/listar
@vinculo_bp.route("/listar", methods=["GET"])
@login_required
def route_listar_vinculo():
    deps = listar_vinculo()
    return jsonify(deps)

