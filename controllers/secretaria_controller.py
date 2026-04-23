from extensions import db
from models.empresa_model import Empresa
from models.secretaria_model import Secretaria
from flask import render_template, jsonify
from utils.logs import registrar_log


# =========================
# LISTAR
# =========================
def listar_secretaria():
    secretaria = (
        Secretaria.query
        .filter_by(status=1)
        .order_by(Secretaria.nome)
        .all()
    )
    return [d.to_dict() for d in secretaria]


# =========================
# ADICIONAR
# =========================
def adicionar_secretaria(nome, sigla):
    if not nome:
        raise ValueError("Nome é obrigatório")

    if not sigla:
        raise ValueError("Sigla é obrigatória")

    try:
        secretaria = Secretaria(
            nome=nome,
            sigla=sigla
        )

        db.session.add(secretaria)

        # 🔑 Garante ID antes do commit
        db.session.flush()

        existente = Empresa.query.filter_by(nome=nome).first()
        if existente:
            return {'erro': 'Empresa já cadastrada'}, 409




        depois = {
            "id": secretaria.id,
            "nome": secretaria.nome,
            "sigla": secretaria.sigla,
            "status": secretaria.status
        }

        registrar_log(
            entidade='secretaria',
            entidade_id=secretaria.id,
            antes="",
            depois=depois,
            retorno='SUCESSO',
            mensagem='Secretaria cadastrada com sucesso'
        )

        db.session.commit()
        return secretaria.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='secretaria',
            entidade_id=None,
            antes="",
            depois={
                "nome": nome,
                "sigla": sigla
            },
            retorno='ERRO',
            mensagem=str(e)
        )

        raise e


# =========================
# EDITAR
# =========================
def editar_secretaria(id, sigla, nome):
    try:
        secretaria = Secretaria.query.get(id)
        if not secretaria:
            raise LookupError("Secretaria não encontrada")

        if not nome:
            raise ValueError("Nome é obrigatório")

        if not sigla:
            raise ValueError("Sigla é obrigatória")

        # 📌 ANTES
        antes = {
            "id": secretaria.id,
            "nome": secretaria.nome,
            "sigla": secretaria.sigla,
            "status": secretaria.status
        }

        # 📌 ALTERAÇÃO
        secretaria.nome = nome
        secretaria.sigla = sigla

        db.session.commit()

        # 📌 DEPOIS
        depois = {
            "id": secretaria.id,
            "nome": secretaria.nome,
            "sigla": secretaria.sigla,
            "status": secretaria.status
        }

        registrar_log(
            entidade='secretaria',
            entidade_id=secretaria.id,
            antes=antes,
            depois=depois,
            retorno='SUCESSO',
            mensagem='Secretaria editada com sucesso'
        )

        return secretaria.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='secretaria',
            entidade_id=id,
            antes="",
            depois="",
            retorno='ERRO',
            mensagem=str(e)
        )

        raise e


# =========================
# REMOVER (SOFT DELETE)
# =========================
def remover_secretaria(id):
    try:
        secretaria = Secretaria.query.get(id)
        if not secretaria:
            return jsonify({"erro": "Secretaria não encontrada"}), 404

        # 📌 ANTES
        antes = {
            "id": secretaria.id,
            "nome": secretaria.nome,
            "sigla": secretaria.sigla,
            "status": secretaria.status
        }

        # 📌 SOFT DELETE
        secretaria.status = 0
        secretaria.nome = f"[DELETADO {secretaria.id}] {secretaria.nome}"
        secretaria.sigla = f"[DELETADO {secretaria.id}] {secretaria.sigla}"

        # 📌 DEPOIS
        depois = {
            "id": secretaria.id,
            "nome": secretaria.nome,
            "sigla": secretaria.sigla,
            "status": secretaria.status
        }

        db.session.commit()

        registrar_log(
            entidade='secretaria',
            entidade_id=secretaria.id,
            antes=antes,
            depois=depois,
            retorno='SUCESSO',
            mensagem='Secretaria desativada (soft delete)'
        )

        return jsonify({"mensagem": "Secretaria excluída com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='secretaria',
            entidade_id=id,
            antes="",
            depois="",
            retorno='ERRO',
            mensagem=str(e)
        )

        print("ERRO AO DESATIVAR secretaria:", e)
        return jsonify({"erro": "Erro interno"}), 500


# =========================
# VIEW
# =========================
def handle_secretaria():
    return render_template("secretaria/secretaria.html")
