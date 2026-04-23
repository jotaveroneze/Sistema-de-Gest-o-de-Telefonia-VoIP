from extensions import db
from models.empresa_model import Empresa
from flask import render_template, jsonify
from utils.logs import registrar_log
from sqlalchemy.exc import IntegrityError

# Listar todos os empresa
def listar_empresa():
    empresa = (
        Empresa.query
        .filter_by(status=1)
        .order_by(Empresa.nome)
        .all()
    )
    return [d.to_dict() for d in empresa]



# Adicionar novo empresa
def adicionar_empresa(nome):
    nome = nome.strip() if nome else ""

    if not nome:
        return {'erro': 'Nome é obrigatório'}, 400

    existente = Empresa.query.filter_by(nome=nome).first()
    if existente:
        return {'erro': 'Empresa já cadastrada'}, 409
    print(nome)

    try:
        empresa = Empresa(nome=nome)
        db.session.add(empresa)
        db.session.flush()

        registrar_log(
            entidade='empresa',
            entidade_id=empresa.id,
            antes="",
            depois={"nome": empresa.nome},
            retorno='SUCESSO',
            mensagem='Empresa cadastrada com sucesso'
        )

        db.session.commit()
        return empresa.to_dict(), 201

    except IntegrityError:  # ✅ Captura erro UNIQUE do banco
        db.session.rollback()

        registrar_log(
            entidade='empresa',
            entidade_id=None,
            antes="",
            depois={"nome": nome},
            retorno='ERRO',
            mensagem='Empresa já cadastrada (conflito no banco)'
        )

        return {'erro': 'Empresa já cadastrada'}, 409  # ✅ Retorna 409, não 500

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='empresa',
            entidade_id=None,
            antes="",
            depois={"nome": nome},
            retorno='ERRO',
            mensagem=str(e)
        )

        return {'erro': 'Erro interno ao cadastrar empresa'}, 500


# Editar modelo
def editar_empresa(id, nome):
    try:
        empresa = Empresa.query.get(id)
        if not empresa:
            raise LookupError("Empresa não encontrada")

        if not nome:
            raise ValueError("Nome é obrigatório")

        # 📌 Estado ANTES
        antes = {
            "id": empresa.id,
            "nome": empresa.nome
        }

        # 📌 Alteração
        empresa.nome = nome

        db.session.commit()

        # 📌 Estado DEPOIS
        depois = {
            "id": empresa.id,
            "nome": empresa.nome
        }

        # 📌 Log de sucesso
        registrar_log(
            entidade='empresa',
            entidade_id=empresa.id,
            antes=antes,
            depois=depois,
            retorno='SUCESSO',
            mensagem='Empresa editada com sucesso'
        )

        return empresa.to_dict()

    except Exception as e:
        db.session.rollback()

        # 📌 Log de erro
        registrar_log(
            entidade='empresa',
            entidade_id=id,
            antes="",
            depois="",
            retorno='ERRO',
            mensagem=str(e)
        )

        raise e


# Remover empresa
def remover_empresa(id):
    try:
        empresa = Empresa.query.get(id)
        if not empresa:
            return jsonify({"erro": "empresa não encontrada"}), 404

        # 📌 Estado ANTES
        antes = {
            "id": empresa.id,
            "nome": empresa.nome,
            "status": empresa.status
        }

        # 📌 Soft delete
        empresa.status = 0
        empresa.nome = f"[DELETADO {empresa.id}] {empresa.nome}"

        # 📌 Estado DEPOIS
        depois = {
            "id": empresa.id,
            "nome": empresa.nome,
            "status": empresa.status
        }

        db.session.commit()

        # 📌 Log de sucesso
        registrar_log(
            entidade='empresa',
            entidade_id=empresa.id,
            antes=antes,
            depois=depois,
            retorno='SUCESSO',
            mensagem='Empresa desativada (soft delete)'
        )

        return jsonify({"mensagem": "Empresa excluída com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        # 📌 Log de erro
        registrar_log(
            entidade='empresa',
            entidade_id=id,
            antes="",
            depois="",
            retorno='ERRO',
            mensagem=str(e)
        )

        print("ERRO AO DESATIVAR empresa:", e)
        return jsonify({"erro": "Erro interno"}), 500


def handle_empresa():
    return render_template("empresa/empresa.html")

