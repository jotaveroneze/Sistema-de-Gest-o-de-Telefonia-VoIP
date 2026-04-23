from extensions import db
from models.tronco_model import Tronco
from flask import render_template, jsonify
from utils.logs import registrar_log


# =========================
# SNAPSHOT
# =========================
def snapshot_tronco(t):
    return {
        "id": t.id,
        "numerochave": t.numerochave,
        "ramalinicial": t.ramalinicial,
        "ramalfinal": t.ramalfinal,
        "idoperadora": t.idoperadora,
        "status": t.status
    }


# =========================
# LISTAR
# =========================
def listar_tronco():
    tronco = (
        Tronco.query
        .filter_by(status=1)
        .all()
    )
    return [d.to_dict() for d in tronco]


# =========================
# ADICIONAR
# =========================
def adicionar_tronco(numerochave, ramalinicial, ramalfinal, id_operadora):
    try:
        if not numerochave:
            raise ValueError("Número Chave é obrigatório")

        if not ramalinicial:
            raise ValueError("Ramal Inicial é obrigatório")

        if not ramalfinal:
            raise ValueError("Ramal Final é obrigatório")

        if not id_operadora:
            raise ValueError("Operadora é obrigatória")

        tronco = Tronco(
            numerochave=numerochave,
            ramalinicial=int(ramalinicial),
            ramalfinal=int(ramalfinal),
            idoperadora=id_operadora
        )

        db.session.add(tronco)
        db.session.flush()  # pega o ID antes do commit

        registrar_log(
            entidade="tronco",
            entidade_id=tronco.id,
            antes="",
            depois=snapshot_tronco(tronco),
            retorno="SUCESSO",
            mensagem="Tronco cadastrado"
        )

        db.session.commit()
        return tronco.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="tronco",
            entidade_id=None,
            antes="",
            depois={
                "numerochave": numerochave,
                "ramalinicial": ramalinicial,
                "ramalfinal": ramalfinal,
                "idoperadora": id_operadora
            },
            retorno="ERRO",
            mensagem=str(e)
        )

        raise


# =========================
# EDITAR
# =========================
def editar_tronco(id, numerochave, ramalinicial, ramalfinal, idoperadora):
    try:
        tronco = Tronco.query.get(id)

        if not tronco:
            raise LookupError("Tronco não encontrado")

        if not numerochave:
            raise ValueError("Número chave é obrigatório")

        if not ramalinicial:
            raise ValueError("Ramal inicial é obrigatório")

        if not ramalfinal:
            raise ValueError("Ramal final é obrigatório")

        if not idoperadora:
            raise ValueError("Operadora é obrigatória")

        antes = snapshot_tronco(tronco)

        tronco.numerochave = numerochave
        tronco.ramalinicial = int(ramalinicial)
        tronco.ramalfinal = int(ramalfinal)
        tronco.idoperadora = idoperadora

        db.session.commit()

        registrar_log(
            entidade="tronco",
            entidade_id=id,
            antes=antes,
            depois=snapshot_tronco(tronco),
            retorno="SUCESSO",
            mensagem="Tronco editado"
        )

        return tronco.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="tronco",
            entidade_id=id,
            antes="",
            depois={
                "numerochave": numerochave,
                "ramalinicial": ramalinicial,
                "ramalfinal": ramalfinal,
                "idoperadora": idoperadora
            },
            retorno="ERRO",
            mensagem=str(e)
        )

        raise


# =========================
# REMOVER (DESATIVAR)
# =========================
def removertronco(id):
    try:
        dep = Tronco.query.get(id)
        if not dep:
            return jsonify({"erro": "Tronco não encontrado"}), 404

        antes = snapshot_tronco(dep)

        # Desativa ao invés de deletar
        dep.status = 0
        db.session.commit()

        registrar_log(
            entidade="tronco",
            entidade_id=id,
            antes=antes,
            depois=snapshot_tronco(dep),
            retorno="SUCESSO",
            mensagem="Tronco desativado"
        )

        return jsonify({"mensagem": "Tronco excluído com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="tronco",
            entidade_id=id,
            antes="",
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        print("ERRO AO DESATIVAR Tronco:", e)
        return jsonify({"erro": "Erro interno"}), 500


# =========================
# VIEW
# =========================
def handle_tronco():
    return render_template("tronco/tronco.html")
