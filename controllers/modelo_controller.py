from sqlalchemy.exc import IntegrityError

from extensions import db
from models.modelo_model import Modelo
from flask import render_template, jsonify
from utils.logs import registrar_log

def snapshot_modelo(modelo):
    return {
        "id": modelo.id,
        "nome": modelo.nome,
        "status": getattr(modelo, "status", None)
    }


# Listar todos os modelo
def listar_modelo():
    modelo = (
        Modelo.query
        .filter_by(status=1)
        .order_by(Modelo.nome)
        .all()
    )
    return [d.to_dict() for d in modelo]



# Adicionar novo modelo
def adicionar_modelo(nome):
    if not nome:
        raise ValueError("Nome é obrigatório")

    try:
        modelo = Modelo(nome=nome, status=1)
        db.session.add(modelo)
        db.session.flush()

        depois = snapshot_modelo(modelo)
        db.session.commit()

        existente = Modelo.query.filter_by(nome=nome).first()
        if existente:
            return {'erro': 'Empresa já cadastrada'}, 409

        registrar_log(
            entidade="modelo",
            entidade_id=modelo.id,
            antes="",
            depois=depois,
            retorno="SUCESSO",
            mensagem="Modelo cadastrado com sucesso"
        )

        return modelo.to_dict()

    except IntegrityError:
        db.session.rollback()
        # ✅ Lança ValueError com mensagem amigável
        raise ValueError(f"Modelo '{nome}' já existe!")

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="modelo",
            entidade_id=None,
            antes={"nome": nome},
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        raise

# Editar modelo
def editar_modelo(id, nome):
    modelo = Modelo.query.get(id)
    if not modelo:
        raise LookupError("Modelo não encontrado")
    if not nome:
        raise ValueError("Nome é obrigatório")

    antes = snapshot_modelo(modelo)

    try:
        modelo.nome = nome
        db.session.commit()

        depois = snapshot_modelo(modelo)

        registrar_log(
            entidade="modelo",
            entidade_id=modelo.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Modelo editado com sucesso"
        )

        return modelo.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="modelo",
            entidade_id=id,
            antes=antes,
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        raise

# Remover modelo
def remover_modelo(id):
    try:
        modelo = Modelo.query.get(id)
        if not modelo:
            return jsonify({"erro": "Modelo não encontrado"}), 404

        antes = snapshot_modelo(modelo)

        modelo.status = 0
        modelo.nome = f"[DELETADO {modelo.id}] {modelo.nome}"

        db.session.commit()

        depois = snapshot_modelo(modelo)

        registrar_log(
            entidade="modelo",
            entidade_id=modelo.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Modelo desativado"
        )

        return jsonify({"mensagem": "Modelo excluído com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="modelo",
            entidade_id=id,
            antes="",
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        return jsonify({"erro": "Erro interno"}), 500


def handle_modelo():
    return render_template("modelo/modelo.html")
