from flask_login import current_user
from sqlalchemy import and_, or_

from controllers.pendencias_controller import snapshot_pendencia
from extensions import db
from flask import jsonify, request
from datetime import date, datetime
from sqlalchemy.sql import exists

from models.numerogrupo_model import Numerogrupo
from models.pendencias_model import Pendencias
from models.telefoneramal_model import TelefoneRamal
from models.pessoatelefone_model import PessoaTelefone
from models.telefone_model import Telefone
from models.ramal_model import Ramal

from utils.logs import registrar_log


# =========================
# LISTAR PESSOAS DO RAMAL
# =========================
def listar_pessoas_do_ramal(id_ramal):
    try:
        registros = (
            db.session.query(TelefoneRamal, Telefone, PessoaTelefone)
            .join(
                Telefone,
                and_(
                    Telefone.id == TelefoneRamal.idtelefone,
                    Telefone.status == 1
                )
            )
            .outerjoin(
                PessoaTelefone,
                and_(
                    PessoaTelefone.idtelefone == Telefone.id,
                    PessoaTelefone.status == 1
                )
            )
            .filter(
                TelefoneRamal.idramal == id_ramal,
                TelefoneRamal.status == 1
            )
            .order_by(Telefone.id)
            .all()
        )

        resultado = {}

        for telefoneramal, telefone, pessoatelefone in registros:

            if telefone.id not in resultado:
                resultado[telefone.id] = {
                    "idtelefoneramal": telefoneramal.id,
                    "idtelefone": telefone.id,
                    "patrimonio": telefone.patrimonio,
                    "serial": telefone.serial,
                    "pessoas": []
                }

            if pessoatelefone and pessoatelefone.pessoa:
                p = pessoatelefone.pessoa
                resultado[telefone.id]["pessoas"].append({
                    "idpessoatelefone": pessoatelefone.id,
                    "nome": p.nome,
                    "funcional": p.funcional,
                    "cpf": p.cpf,
                    "departamento": p.departamento.nome if p.departamento else "",
                    "secretaria": (
                        p.departamento.secretaria.sigla
                        if p.departamento and p.departamento.secretaria
                        else ""
                    )
                })

        return jsonify(list(resultado.values())), 200

    except Exception as e:
        print("ERRO AO LISTAR PESSOAS DO RAMAL:", e)
        return jsonify({"erro": "Erro interno"}), 500


# =========================
# SNAPSHOT
# =========================
def snapshot_telefoneramal(v):
    return {
        "id": v.id,
        "idtelefone": v.idtelefone,
        "idramal": v.idramal,
        "dataalteracao": str(v.dataalteracao)
    }


# =========================
# REMOVER TELEFONE DO RAMAL
# =========================
def remover_telefone_do_ramal_controller(id_telefoneramal):
    try:
        vinculo = TelefoneRamal.query.get(id_telefoneramal)

        if not vinculo:
            return jsonify({"erro": "Vínculo telefone/ramal não encontrado"}), 404

        # 📌 Snapshot antes
        antes = snapshot_telefoneramal(vinculo)

        # ==========================================
        # VERIFICA SE JÁ EXISTE PENDÊNCIA IGUAL ATIVA
        # ==========================================
        pendencia_existe = Pendencias.query.filter_by(
            tipopendencia='22',
            idtelefoneramal=vinculo.id,  # 🚩 CORRIGIDO: era 'telefone', agora é 'idtelefoneramal'
            status=1
        ).first()

        if not pendencia_existe:
            # SÓ CRIA E REGISTRA LOG SE NÃO EXISTIR UMA PENDÊNCIA ATIVA
            ramal_desc = (
                vinculo.ramal.numero
                if hasattr(vinculo.ramal, "numero")
                else vinculo.idramal
            )
            patrimonio = vinculo.telefone.patrimonio
            serial = vinculo.telefone.serial
            mac = vinculo.telefone.macaddress

            descricao = f"Desvincular o ramal: {ramal_desc} do telefone PATRIMÔNIO: {patrimonio}; SERIAL: {serial}; MAC: {mac}"

            pendencia = Pendencias(
                descricaotipopendencia=descricao,
                tipopendencia='22',
                idtelefoneramal=vinculo.id,
                idusuarioresolvido=None,
                idusuarioresponsavel=current_user.id,
                dataentrada=datetime.now(),
                status=1
            )

            db.session.add(pendencia)
            db.session.flush()

            # O log da pendência está corretamente dentro do IF agora
            registrar_log(
                entidade="pendencias",
                entidade_id=pendencia.id,
                antes="",
                depois=snapshot_pendencia(pendencia),
                retorno="SUCESSO",
                mensagem="Pendência criada após remover telefone do ramal"
            )

        # ======================
        # REMOVE VÍNCULO
        # ======================
        vinculo.status = 0
        db.session.commit()

        registrar_log(
            entidade="telefoneramal",
            entidade_id=id_telefoneramal,
            antes=antes,
            depois="",
            retorno="SUCESSO",
            mensagem="Telefone removido do ramal"
        )

        return jsonify({
            "mensagem": "Telefone removido do ramal e pendência processada com sucesso"
        }), 200

    except Exception as e:
        db.session.rollback()
        registrar_log(
            entidade="telefoneramal",
            entidade_id=id_telefoneramal,
            antes="",
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )
        print("ERRO AO REMOVER TELEFONE DO RAMAL:", e)
        return jsonify({"erro": "Erro interno"}), 500


# =========================
# LISTAR TELEFONES DISPONÍVEIS
# =========================
def listar_telefones_disponiveis(idramal):
    subquery = (
        db.session.query(TelefoneRamal.idtelefone)
        .filter(TelefoneRamal.idramal == idramal,
                TelefoneRamal.status == 1
                )
        .subquery()
    )

    registros = (
        db.session.query(Telefone, PessoaTelefone)
        .outerjoin(
            PessoaTelefone,
            and_(
                PessoaTelefone.idtelefone == Telefone.id,
                PessoaTelefone.status == 1
            )
        )
        .filter(
            Telefone.status == 1,
            ~Telefone.id.in_(subquery)
        )
        .order_by(Telefone.id)
        .all()
    )

    resultado = {}

    for telefone, pessoatelefone in registros:
        if telefone.id not in resultado:
            resultado[telefone.id] = {
                "id": telefone.id,
                "serial": telefone.serial,
                "patrimonio": telefone.patrimonio,
                "pessoas": []
            }

        if pessoatelefone and pessoatelefone.pessoa:
            p = pessoatelefone.pessoa
            resultado[telefone.id]["pessoas"].append({
                "nome": p.nome,
                "funcional": p.funcional,
                "cpf": p.cpf,
                "departamento": p.departamento.nome if p.departamento else "",
                "secretaria": (
                    p.departamento.secretaria.sigla
                    if p.departamento and p.departamento.secretaria
                    else ""
                )
            })

    return jsonify(list(resultado.values())), 200


# =========================
# VINCULAR TELEFONES AO RAMAL
# =========================
def vincular_telefones_controller():
    try:
        data = request.get_json()
        idramal = data.get("idramal")
        telefones = data.get("telefones", [])

        if not idramal or not telefones:
            return jsonify({"erro": "Dados inválidos"}), 400

        for idtelefone in telefones:
            # 1. BUSCA SE JÁ EXISTE QUALQUER REGISTRO (ATIVO OU INATIVO)
            vinculo = TelefoneRamal.query.filter_by(
                idtelefone=idtelefone,
                idramal=idramal
            ).first()

            if vinculo:
                if vinculo.status == 1:
                    # Se já está ativo, pula para o próximo telefone
                    continue
                else:
                    # SE EXISTE MAS ESTÁ INATIVO, REATIVA
                    antes_vinculo = snapshot_telefoneramal(vinculo)
                    vinculo.status = 1
                    vinculo.dataalteracao = date.today()
                    mensagem_log = "Telefone reativado no ramal"
            else:
                # SE NÃO EXISTE, CRIA UM NOVO
                antes_vinculo = ""
                vinculo = TelefoneRamal(
                    idtelefone=idtelefone,
                    idramal=idramal,
                    dataalteracao=date.today(),
                    status=1
                )
                db.session.add(vinculo)
                mensagem_log = "Telefone vinculado ao ramal"

            db.session.flush() # Garante o ID para a pendência e log

            # Log do vínculo (reativação ou criação)
            registrar_log(
                entidade="telefoneramal",
                entidade_id=vinculo.id,
                antes=antes_vinculo,
                depois=snapshot_telefoneramal(vinculo),
                retorno="SUCESSO",
                mensagem=mensagem_log
            )

            # 2. VERIFICA SE JÁ EXISTE PENDÊNCIA IGUAL ATIVA
            pendencia_existe = Pendencias.query.filter_by(
                tipopendencia=2,
                idtelefoneramal=vinculo.id,
                status=1
            ).first()

            if not pendencia_existe:
                ramal_desc = (
                    vinculo.ramal.numero
                    if hasattr(vinculo.ramal, "numero")
                    else vinculo.idramal
                )
                serial = vinculo.telefone.serial
                mac = vinculo.telefone.macaddress
                patrimonio = vinculo.telefone.patrimonio

                descricao = f"Vincular o telefone PATRIMÔNIO: {patrimonio}; SERIAL: {serial}; MAC: {mac} ao ramal: {ramal_desc}"

                pendencia = Pendencias(
                    descricaotipopendencia=descricao,
                    tipopendencia=2,
                    idtelefoneramal=vinculo.id,
                    idusuarioresolvido=None,
                    idusuarioresponsavel=current_user.id,
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
                    mensagem="Pendência criada após vínculo telefone/ramal"
                )

        db.session.commit()
        return jsonify({"mensagem": "Telefone(s) processados e pendências atualizadas"}), 200

    except Exception as e:
        db.session.rollback()
        # ... log de erro ...
        print("Erro ao vincular telefones:", e)
        return jsonify({"erro": "Erro interno"}), 500



# =========================
# LISTAR RAMAIS DISPONÍVEIS
# =========================
def listar_ramais_disponiveis_para_telefone(id_telefone):
    try:
        ramais = (
            db.session.query(
                Ramal,

                # 🔹 Em uso por OUTRO telefone OU por número de grupo
                exists().where(
                    or_(
                        and_(
                            TelefoneRamal.idramal == Ramal.id,
                            TelefoneRamal.idtelefone != id_telefone,
                            TelefoneRamal.status == 1
                        ),
                        and_(
                            Numerogrupo.numero == Ramal.numero,
                            Numerogrupo.status == 1
                        )
                    )
                ).label("em_uso"),

                # 🔹 Já vinculado a ESTE telefone
                exists().where(
                    and_(
                        TelefoneRamal.idramal == Ramal.id,
                        TelefoneRamal.idtelefone == id_telefone,
                        TelefoneRamal.status == 1
                    )
                ).label("ja_vinculado")
            )
            .filter(Ramal.status == 1)
            .order_by(Ramal.numero)
            .all()
        )
        resultado = []
        for ramal, em_uso, ja_vinculado in ramais:
            if ja_vinculado:
                continue

            resultado.append({
                "id": ramal.id,
                "numero": ramal.numero,
                "gravado": bool(ramal.gravado),
                "em_uso": bool(em_uso)
            })

        return jsonify(resultado), 200

    except Exception as e:
        print("ERRO AO LISTAR RAMAIS:", e)
        return jsonify({"erro": "Erro interno"}), 500


# =========================
# LISTAR RAMAIS VINCULADOS
# =========================
def listar_ramais_vinculados_por_telefone_controller(id_telefone):
    try:
        registros = (
            db.session.query(Ramal, TelefoneRamal)
            .join(TelefoneRamal, TelefoneRamal.idramal == Ramal.id)
            .filter(
                TelefoneRamal.idtelefone == id_telefone,
                TelefoneRamal.status == 1,
                Ramal.status == 1
            )
            .all()
        )

        resultado = []
        for ramal, tr in registros:
            resultado.append({
                "id": tr.id,
                "numero": ramal.numero,
                "gravado": bool(ramal.gravado)
            })

        return jsonify(resultado), 200

    except Exception as e:
        print("Erro ao listar ramais vinculados:", e)
        return jsonify({"erro": "Erro interno"}), 500


# =========================
# VINCULAR RAMAIS AO TELEFONE
# =========================
def vincular_ramais_telefone_controller():
    try:
        dados = request.get_json()
        id_telefone = dados.get("id_telefone")
        ramais_ids = dados.get("ramais")

        if not id_telefone or not ramais_ids:
            return jsonify({"erro": "Telefone e ramais são obrigatórios"}), 400

        for id_ramal in ramais_ids:
            # 1. BUSCA SE JÁ EXISTE QUALQUER REGISTRO (ATIVO OU INATIVO)
            vinculo = TelefoneRamal.query.filter_by(
                idtelefone=id_telefone,
                idramal=id_ramal
            ).first()

            if vinculo:
                if vinculo.status == 1:
                    # Se já está ativo, pula para o próximo ramal
                    continue
                else:
                    # SE EXISTE MAS ESTÁ INATIVO, REATIVA
                    antes_vinculo = snapshot_telefoneramal(vinculo)
                    vinculo.status = 1
                    vinculo.dataalteracao = date.today()
                    mensagem_log = "Ramal reativado no telefone"
            else:
                # SE NÃO EXISTE, CRIA UM NOVO
                antes_vinculo = ""
                vinculo = TelefoneRamal(
                    idtelefone=id_telefone,
                    idramal=id_ramal,
                    dataalteracao=date.today(),
                    status=1
                )
                db.session.add(vinculo)
                mensagem_log = "Ramal vinculado ao telefone"

            db.session.flush() # Garante que o ID do vínculo esteja disponível

            # Log do vínculo (seja novo ou reativado)
            registrar_log(
                entidade="telefoneramal",
                entidade_id=vinculo.id,
                antes=antes_vinculo,
                depois=snapshot_telefoneramal(vinculo),
                retorno="SUCESSO",
                mensagem=mensagem_log
            )

            # 2. VERIFICA SE JÁ EXISTE PENDÊNCIA IGUAL ATIVA
            pendencia_existe = Pendencias.query.filter_by(
                tipopendencia=2,
                idtelefoneramal=vinculo.id,
                status=1
            ).first()

            if not pendencia_existe:
                ramal_desc = vinculo.ramal.numero if hasattr(vinculo.ramal, "numero") else vinculo.idramal
                patrimonio = vinculo.telefone.patrimonio
                serial = vinculo.telefone.serial
                mac = vinculo.telefone.macaddress

                descricao = f"Vincular o ramal: {ramal_desc} ao telefone PATRIMÔNIO: {patrimonio}; SERIAL: {serial}; MAC: {mac}"

                pendencia = Pendencias(
                    descricaotipopendencia=descricao,
                    tipopendencia='2',
                    idtelefoneramal=vinculo.id,
                    idusuarioresolvido=None,
                    idusuarioresponsavel=current_user.id,
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
                    mensagem="Pendência criada após vínculo ramal/telefone"
                )

        db.session.commit()
        return jsonify({"mensagem": "Ramais processados e pendências atualizadas com sucesso"}), 200

    except Exception as e:
        db.session.rollback()
        # ... log de erro ...
        return jsonify({"erro": "Erro interno"}), 500



# =========================
# REMOVER RAMAL DO TELEFONE
# =========================
def remover_ramal_telefone_controller(id_vinculo):
    try:
        vinculo = TelefoneRamal.query.get(id_vinculo)

        if not vinculo:
            return jsonify({"erro": "Vínculo não encontrado"}), 404

        # 📌 Snapshot antes de remover
        antes = snapshot_telefoneramal(vinculo)

        # ==========================================
        # VERIFICA SE JÁ EXISTE PENDÊNCIA IGUAL ATIVA
        # ==========================================
        pendencia_existe = Pendencias.query.filter_by(
            tipopendencia='22',
            idtelefoneramal=vinculo.id,
            status=1
        ).first()

        if not pendencia_existe:
            # SÓ CRIA E REGISTRA LOG SE NÃO EXISTIR UMA PENDÊNCIA ATIVA
            ramal_desc = (
                vinculo.ramal.numero
                if hasattr(vinculo.ramal, "numero")
                else vinculo.idramal
            )
            patrimonio = vinculo.telefone.patrimonio
            serial = vinculo.telefone.serial
            mac = vinculo.telefone.macaddress

            descricao = f"Desvincular o ramal: {ramal_desc} do telefone PATRIMÔNIO: {patrimonio}; SERIAL: {serial}; MAC: {mac}"

            pendencia = Pendencias(
                descricaotipopendencia=descricao,
                tipopendencia='22',
                idtelefoneramal=vinculo.id,
                idusuarioresolvido=None,
                idusuarioresponsavel=current_user.id,
                dataentrada=datetime.now(),
                status=1
            )

            db.session.add(pendencia)
            db.session.flush()

            # O LOG DEVE FICAR AQUI DENTRO
            registrar_log(
                entidade="pendencias",
                entidade_id=pendencia.id,
                antes="",
                depois=snapshot_pendencia(pendencia),
                retorno="SUCESSO",
                mensagem="Pendência criada após desvincular ramal do telefone"
            )

        # ======================
        # REMOVE VÍNCULO
        # ======================
        vinculo.status = 0
        db.session.commit()

        registrar_log(
            entidade="telefoneramal",
            entidade_id=id_vinculo,
            antes=antes,
            depois="",
            retorno="SUCESSO",
            mensagem="Ramal desvinculado do telefone"
        )

        return jsonify({
            "mensagem": "Ramal desvinculado e pendência processada com sucesso"
        }), 200

    except Exception as e:
        db.session.rollback()
        # ... log de erro ...
        print("Erro ao remover ramal do telefone:", e)
        return jsonify({"erro": "Erro interno"}), 500




# =========================
# 🔁 ALIASES (IMPORTS LEGADOS)
# =========================
remover_telefone_do_ramal = remover_telefone_do_ramal_controller
vincular_telefones = vincular_telefones_controller
