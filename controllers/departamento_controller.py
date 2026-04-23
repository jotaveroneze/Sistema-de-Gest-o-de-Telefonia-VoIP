from extensions import db
from models.departamento_model import Departamento
from flask import render_template, jsonify
from utils.logs import registrar_log

# Listar todos os departamentos
def listar_departamentos():
    departamentos = (
        Departamento.query
        .filter_by(status=1)
        .order_by(Departamento.nome)
        .all()
    )

    lista = []
    for u in departamentos:
        lista.append({
            "id": u.id,
            "nome": u.nome,
            "sigla": u.secretaria.sigla if u.secretaria else ""
        })
    return lista

def snapshot_departamento(dep):
    return {
        "id": dep.id,
        "nome": dep.nome,
        "idsecretaria": dep.idsecretaria,
        "status": dep.status
    }

# Adicionar novo departamento
def adicionar_departamento(nome, idsecretaria):
    if not nome:
        raise ValueError("Nome é obrigatório")

    try:
        dep = Departamento(
            nome=nome,
            idsecretaria=idsecretaria,
            status=1
        )

        db.session.add(dep)
        db.session.flush()  # 🔑 gera ID

        depois = snapshot_departamento(dep)

        registrar_log(
            entidade='departamento',
            entidade_id=dep.id,
            antes="",
            depois=depois,
            retorno='SUCESSO',
            mensagem='Departamento cadastrado com sucesso'
        )

        db.session.commit()
        return dep.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='departamento',
            entidade_id=None,
            antes="",
            depois={
                "nome": nome,
                "idsecretaria": idsecretaria
            },
            retorno='ERRO',
            mensagem=str(e)
        )

        raise e


# Editar departamento
def editar_departamento(id, nome, idsecretaria):
    try:
        dep = Departamento.query.get(id)
        if not dep:
            raise LookupError("Departamento não encontrado")

        if not nome:
            raise ValueError("Nome é obrigatório")

        # 📌 ANTES
        antes = snapshot_departamento(dep)

        # 📌 ALTERAÇÃO
        dep.nome = nome
        dep.idsecretaria = idsecretaria

        db.session.commit()

        # 📌 DEPOIS
        depois = snapshot_departamento(dep)

        registrar_log(
            entidade='departamento',
            entidade_id=dep.id,
            antes=antes,
            depois=depois,
            retorno='SUCESSO',
            mensagem='Departamento editado com sucesso'
        )

        return dep.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='departamento',
            entidade_id=id,
            antes="",
            depois="",
            retorno='ERRO',
            mensagem=str(e)
        )

        raise e


# Remover departamento
def remover_departamento(id):
    try:
        dep = Departamento.query.get(id)
        if not dep:
            return jsonify({"erro": "Departamento não encontrado"}), 404

        # 📌 ANTES
        antes = snapshot_departamento(dep)

        # 📌 SOFT DELETE
        dep.status = 0
        dep.nome = f"[DELETADO {dep.id}] {dep.nome}"

        db.session.commit()

        # 📌 DEPOIS
        depois = snapshot_departamento(dep)

        registrar_log(
            entidade='departamento',
            entidade_id=dep.id,
            antes=antes,
            depois=depois,
            retorno='SUCESSO',
            mensagem='Departamento desativado (soft delete)'
        )

        return jsonify({"mensagem": "Departamento desativado com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='departamento',
            entidade_id=id,
            antes="",
            depois="",
            retorno='ERRO',
            mensagem=str(e)
        )

        print("ERRO AO DESATIVAR DEPARTAMENTO:", e)
        return jsonify({"erro": "Erro interno"}), 500

def handle_departamento():
    return render_template("departamento/departamento.html")
