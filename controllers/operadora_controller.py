from extensions import db
from models.operadora_model import Operadora
from flask import render_template, jsonify
from utils.logs import registrar_log

def snapshot_operadora(op):
    return {
        "id": op.id,
        "nome": op.nome,
        "contrato": op.contrato,
        "processo": op.processo,
        "status": getattr(op, "status", None)
    }


# Listar todos os operadora
def listaroperadora():
    operadora = (
        Operadora.query
        .filter_by(status=1)
        .order_by(Operadora.nome)
        .all()
    )
    return [d.to_dict() for d in operadora]



# Adicionar novo operadora
def adicionar_operadora(nome, contrato, processo):
    if not nome:
        raise ValueError("Nome é obrigatório")
    if not contrato:
        raise ValueError("Contrato é obrigatório")
    if not processo:
        raise ValueError("Processo é obrigatório")

    try:
        operadora = Operadora(
            nome=nome,
            contrato=contrato,
            processo=processo,
            status=1
        )

        db.session.add(operadora)
        db.session.flush()  # 🔑 gera ID

        depois = snapshot_operadora(operadora)

        db.session.commit()

        registrar_log(
            entidade="operadora",
            entidade_id=operadora.id,
            antes="",
            depois=depois,
            retorno="SUCESSO",
            mensagem="Operadora cadastrada com sucesso"
        )

        return operadora.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="operadora",
            entidade_id=None,
            antes={
                "nome": nome,
                "contrato": contrato,
                "processo": processo
            },
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        raise


# Editar operadora
def editar_operadora(id, nome, contrato, processo):
    operadora = Operadora.query.get(id)
    if not operadora:
        raise LookupError("Operadora não encontrada")

    if not nome:
        raise ValueError("Nome é obrigatório")
    if not contrato:
        raise ValueError("Contrato é obrigatório")
    if not processo:
        raise ValueError("Processo é obrigatório")

    antes = snapshot_operadora(operadora)

    try:
        operadora.nome = nome
        operadora.contrato = contrato
        operadora.processo = processo

        db.session.commit()

        depois = snapshot_operadora(operadora)

        registrar_log(
            entidade="operadora",
            entidade_id=operadora.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Operadora editada com sucesso"
        )

        return operadora.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="operadora",
            entidade_id=id,
            antes=antes,
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        raise



# Remover operadora
def removeroperadora(id):
    try:
        operadora = Operadora.query.get(id)
        if not operadora:
            return jsonify({"erro": "Operadora não encontrada"}), 404

        antes = snapshot_operadora(operadora)

        operadora.status = 0
        operadora.nome = f"[DELETADO {operadora.id}] {operadora.nome}"

        db.session.commit()

        depois = snapshot_operadora(operadora)

        registrar_log(
            entidade="operadora",
            entidade_id=operadora.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Operadora desativada"
        )

        return jsonify({"mensagem": "Operadora excluída com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="operadora",
            entidade_id=id,
            antes="",
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        print("ERRO AO DESATIVAR operadora:", e)
        return jsonify({"erro": "Erro interno"}), 500


def handle_operadora():
    return render_template("operadora/operadora.html")
