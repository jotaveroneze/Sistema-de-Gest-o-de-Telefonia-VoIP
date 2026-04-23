from extensions import db
from models.vinculo_model import Vinculo
from flask import render_template, jsonify


# Listar todos os modelo
def listar_vinculo():
    vinculo = (
        Vinculo.query
        .order_by(Vinculo.nome)
        .all()
    )
    return [d.to_dict() for d in vinculo]
