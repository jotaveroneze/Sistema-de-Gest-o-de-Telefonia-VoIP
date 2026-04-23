from extensions import db
from models.numerogrupo_model import Numerogrupo
from models.ramalnumerogrupo_model import RamalNumeroGrupo
from flask import render_template, jsonify
from models.departamento_model import Departamento
from models.tronco_model import Tronco
from utils.logs import registrar_log

def snapshot_numerogrupo(ng):
    return {
        "id": ng.id,
        "numero": ng.numero,
        "idtronco": ng.idtronco,
        "descricao": ng.descricao,
        "status": ng.status,
        "gravado": ng.gravado,
        "iddepartamento": ng.iddepartamento,
        "tronco": ng.tronco.id if ng.tronco else None,
    }


def listar_numerogrupo():
    numerogrupo = (
        Numerogrupo.query
        .filter_by(status=1)
        .order_by(Numerogrupo.numero)
        .all()
    )

    lista = []
    for u in numerogrupo:
        lista.append({
            "id": u.id,
            "numero": u.numero,
            "numerochave": u.tronco.numerochave if u.tronco else "",
            "departamento": u.departamento.nome if u.departamento else "",
            "sigla": u.departamento.secretaria.sigla if u.departamento else "",
            "descricao": u.descricao,
            "gravado": u.gravado
        })
    return lista


# Adicionar novo telefone
def adicionar_numerogrupo(numero, descricao=None, status=1, gravado=0, iddepartamento=None, tronco=None):
    if not numero:
        raise ValueError("Número é obrigatório")

    try:
        # Se recebeu id_tronco, busca o objeto Tronco
        tronco_obj = None
        if tronco:
            tronco_obj = Tronco.query.get(tronco)
            if not tronco_obj:
                raise ValueError("Tronco não encontrado")

        numerogrupo = Numerogrupo(
            numero=numero,
            descricao=descricao,
            status=status,
            gravado=gravado,
            tronco=tronco_obj  # ✅ passa o objeto, não o int
        )

        if iddepartamento:
            departamento = Departamento.query.get(iddepartamento)
            if not departamento:
                raise ValueError("Departamento não encontrado")
            numerogrupo.departamento = departamento

        db.session.add(numerogrupo)
        db.session.flush()  # 🔑 gera ID

        depois = snapshot_numerogrupo(numerogrupo)

        db.session.commit()

        registrar_log(
            entidade="numerogrupo",
            entidade_id=numerogrupo.id,
            antes="",
            depois=depois,
            retorno="SUCESSO",
            mensagem="Número de Grupo cadastrado com sucesso"
        )

        return numerogrupo.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="numerogrupo",
            entidade_id=None,
            antes={
                "numero": numero,
                "descricao": descricao,
                "status": status,
                "gravado": gravado,
                "iddepartamento": iddepartamento,
                "tronco": tronco
            },
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        raise


# Editar telefone
def editar_numerogrupo(id_numerogrupo, iddepartamento, numero, descricao, gravado=0, tronco=None):
    numerogrupo = Numerogrupo.query.get(id_numerogrupo)
    if not numerogrupo:
        raise ValueError("Número de Grupo não encontrado")
    if not numero:
        raise ValueError("Número é obrigatório")

    antes = snapshot_numerogrupo(numerogrupo)

    try:
        numerogrupo.numero = numero
        numerogrupo.descricao = descricao
        numerogrupo.gravado = gravado
        numerogrupo.idtronco = tronco

        if iddepartamento:
            departamento = Departamento.query.get(iddepartamento)
            if not departamento:
                raise ValueError("Departamento não encontrado")
            numerogrupo.departamento = departamento
        else:
            numerogrupo.departamento = None

        db.session.commit()

        depois = snapshot_numerogrupo(numerogrupo)

        registrar_log(
            entidade="numerogrupo",
            entidade_id=numerogrupo.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Número de Grupo editado com sucesso"
        )

        return numerogrupo.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="numerogrupo",
            entidade_id=id_numerogrupo,
            antes=antes,
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        raise


def removernumerogrupo(id):
    try:
        numerogrupo = Numerogrupo.query.get(id)
        if not numerogrupo:
            return jsonify({"erro": "Número de Grupo não encontrado"}), 404

        antes = snapshot_numerogrupo(numerogrupo)

        # 🔹 Remove vínculos com ramais
        RamalNumeroGrupo.query.filter_by(idnumerogrupo=id).delete()

        # 🔹 Soft delete
        numerogrupo.status = 0

        db.session.commit()

        depois = snapshot_numerogrupo(numerogrupo)

        registrar_log(
            entidade="numerogrupo",
            entidade_id=numerogrupo.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Número de Grupo desativado e ramais desvinculados"
        )

        return jsonify({"mensagem": "Número de Grupo desativado com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="numerogrupo",
            entidade_id=id,
            antes="",
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        print("ERRO AO DESATIVAR Número de Grupo:", e)
        return jsonify({"erro": "Erro interno"}), 500



def handle_numerogrupo():
    return render_template("numerogrupo/numerogrupo.html")
