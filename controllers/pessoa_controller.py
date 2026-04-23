from datetime import datetime
from re import search

from controllers.pendencias_controller import snapshot_pendencia
from extensions import db
from sqlalchemy import or_, func
from models.pendencias_model import Pendencias
from models.pessoa_model import Pessoa
from flask import render_template, jsonify, request
from utils.logs import registrar_log
from flask_login import current_user

def snapshot_pessoa(p):
    return {
        "id": p.id,
        "nome": p.nome,
        "funcional": p.funcional,
        "cpf": p.cpf,
        "idvinculo": p.idvinculo,
        "iddepartamento": p.iddepartamento,
        "idempresa": p.idempresa,
        "status": getattr(p, "status", None)
    }


# Listar todos os pessoa
# pessoa_controller.py - listar_pessoa()
def listar_pessoa():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()  # Do input

    per_page = 10  # ✅ FIXO 10!

    query = Pessoa.query.filter_by(status=1).order_by(Pessoa.nome)

    if search:  # ✅ Filtra TODAS
        query = query.filter(
            db.or_(
                Pessoa.nome.ilike(f'%{search}%'),
                Pessoa.funcional.cast(db.String).ilike(f'%{search}%'),
                Pessoa.cpf.ilike(f'%{search}%')
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        'pessoas': [p.to_dict() for p in pagination.items],
        'page': pagination.page, 'pages': pagination.pages,
        'total': pagination.total,
        'has_next': pagination.has_next, 'has_prev': pagination.has_prev
    }


# Adicionar novo pessoa
def adicionar_pessoa(nome, funcional=None, cpf=None, id_vinculo=None, id_departamento=None, id_empresa=None):
    if not nome:
        raise ValueError("Nome é obrigatório")
    if not id_vinculo:
        raise ValueError("Vínculo é obrigatório")
    if not id_departamento:
        raise ValueError("Departamento é obrigatório")
    if not id_empresa:
        raise ValueError("Empresa é obrigatória")

        # ✅ converte string vazia para None
    funcional = int(funcional) if funcional else None
    cpf = cpf if cpf else None

    try:
        pessoa = Pessoa(
            nome=nome,
            funcional=funcional,
            cpf=cpf,
            idvinculo=id_vinculo,
            iddepartamento=id_departamento,
            idempresa=id_empresa,
            status=1
        )

        db.session.add(pessoa)
        db.session.flush()  # 🔑 garante ID

        depois = snapshot_pessoa(pessoa)

        db.session.commit()

        registrar_log(
            entidade="pessoa",
            entidade_id=pessoa.id,
            antes="",
            depois=depois,
            retorno="SUCESSO",
            mensagem="Pessoa cadastrada com sucesso"
        )

        return pessoa.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="pessoa",
            entidade_id=None,
            antes={
                "nome": nome,
                "funcional": funcional,
                "cpf": cpf,
                "idvinculo": id_vinculo,
                "iddepartamento": id_departamento,
                "idempresa": id_empresa
            },
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        raise



# Editar pessoa
def editar_pessoa(id, data):
    pessoa = Pessoa.query.get(id)
    if not pessoa:
        raise LookupError("Pessoa não encontrada")

    antes = snapshot_pessoa(pessoa)

    nome           = data.get("nome")
    funcional      = data.get("funcional") or None  # ✅ string vazia → None
    cpf            = data.get("cpf") or None         # ✅ string vazia → None
    idvinculo      = data.get("idvinculo")
    iddepartamento = data.get("iddepartamento")
    idempresa      = data.get("idempresa")

    if not nome:
        raise ValueError("Nome é obrigatório")
    if not idvinculo:
        raise ValueError("Vínculo é obrigatório")
    if not iddepartamento:
        raise ValueError("Departamento é obrigatório")
    if not idempresa:
        raise ValueError("Empresa é obrigatória")

    try:
        pessoa.nome           = nome
        pessoa.funcional      = funcional
        pessoa.cpf            = cpf
        pessoa.idvinculo      = idvinculo
        pessoa.iddepartamento = iddepartamento
        pessoa.idempresa      = idempresa

        db.session.commit()

        depois = snapshot_pessoa(pessoa)

        # ✅ Cria pendência de edição de pessoa (se não existir ativa)
        descricao = (
            f"Editar nome SIIP: {antes['nome']} → {pessoa.nome} "
        )

        pendencia_existe = Pendencias.query.filter_by(
            tipopendencia='4',
            status=1,
            descricaotipopendencia=descricao
        ).first()

        if not pendencia_existe:
            pendencia = Pendencias(
                descricaotipopendencia=descricao,
                tipopendencia='4',               # ✅ string — conforme o Enum do model
                idusuarioresponsavel=current_user.id,
                idusuarioresolvido=None,
                dataentrada=datetime.now(),
                status=1
            )
            db.session.add(pendencia)
            db.session.flush()

            registrar_log(
                entidade="pendencias",
                entidade_id=pendencia.id,
                antes="",
                depois=snapshot_pendencia(pendencia),
                retorno="SUCESSO",
                mensagem="Pendência criada para edição de pessoa"
            )

            db.session.commit()  # ✅ commit da pendência separado

        registrar_log(
            entidade="pessoa",
            entidade_id=pessoa.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Pessoa editada com sucesso"
        )

        return pessoa.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="pessoa",
            entidade_id=id,
            antes=antes,
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        raise



# Remover pessoa
def remover_pessoa(id):
    try:
        pessoa = Pessoa.query.get(id)
        if not pessoa:
            return jsonify({"erro": "Pessoa não encontrada"}), 404

        antes = snapshot_pessoa(pessoa)

        pessoa.status = 0
        pessoa.nome = f"[DELETADO {pessoa.id}] {pessoa.nome}"

        db.session.commit()

        depois = snapshot_pessoa(pessoa)

        registrar_log(
            entidade="pessoa",
            entidade_id=pessoa.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Pessoa desativada"
        )

        return jsonify({"mensagem": "Pessoa excluída com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="pessoa",
            entidade_id=id,
            antes="",
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        print("ERRO AO DESATIVAR pessoa:", e)
        return jsonify({"erro": "Erro interno"}), 500


def handle_pessoa():
    return render_template("pessoa/pessoa.html")
