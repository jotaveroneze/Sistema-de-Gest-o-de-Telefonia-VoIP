from flask import jsonify, request
from datetime import datetime

from flask_login import current_user

from controllers.pendencias_controller import snapshot_pendencia
from extensions import db
from models.pendencias_model import Pendencias
from models.pessoatelefone_model import PessoaTelefone
from models.pessoa_model import Pessoa
from models.telefone_model import Telefone
from utils.logs import registrar_log

def snapshot_pessoa_telefone(v):
    return {
        "id": v.id,
        "idpessoa": v.idpessoa,
        "idtelefone": v.idtelefone,
        "tipo": getattr(v, "tipo", None),
        "status": getattr(v, "status", None)
    }

def listar_pessoas_por_telefone_controller(idtelefone):
    try:
        registros = (
            db.session.query(PessoaTelefone)
            .join(Pessoa)
            .filter(
                PessoaTelefone.idtelefone == idtelefone,
                PessoaTelefone.status == 1,
                Pessoa.status == 1
            )
            .all()
        )

        resultado = []
        for pt in registros:
            pessoa = pt.pessoa
            resultado.append({
                "id_vinculo": pt.id,
                "nome": pessoa.nome,
                "funcional": pessoa.funcional,
                "cpf": pessoa.cpf,
                "departamento": (
                    pessoa.departamento.nome
                    if pessoa.departamento else ""
                )
            })

        return jsonify(resultado), 200

    except Exception as e:
        print("ERRO AO LISTAR PESSOAS DO TELEFONE:", e)
        return jsonify({"erro": "Erro interno"}), 500


def listar_pessoas_disponiveis_controller(idtelefone):
    try:
        subquery = (
            db.session.query(PessoaTelefone.idpessoa)
            .filter(PessoaTelefone.idtelefone == idtelefone, PessoaTelefone.status == 1)
            .subquery()
        )

        pessoas = (
            db.session.query(Pessoa)
            .filter(
                ~Pessoa.id.in_(subquery),
                Pessoa.status == 1   # 👈 somente pessoas ativas
            )
            .order_by(Pessoa.nome)
            .all()
        )

        resultado = [{
            "id": p.id,
            "nome": p.nome,
            "funcional": p.funcional,
            "cpf": p.cpf
        } for p in pessoas]

        return jsonify(resultado), 200

    except Exception as e:
        print("ERRO AO LISTAR PESSOAS DISPONÍVEIS:", e)
        return jsonify({"erro": "Erro interno"}), 500


def vincular_pessoa_telefone_controller():
    try:
        dados = request.get_json()
        idtelefone = dados.get("idtelefone")
        pessoas = dados.get("pessoas", [])

        if not idtelefone or not pessoas:
            return jsonify({"erro": "Dados inválidos"}), 400

        for idpessoa in pessoas:
            # 1. BUSCA SE JÁ EXISTE QUALQUER REGISTRO (ATIVO OU INATIVO)
            vinculo = PessoaTelefone.query.filter_by(
                idtelefone=idtelefone,
                idpessoa=idpessoa
            ).first()

            if vinculo:
                if vinculo.status == 1:
                    continue # Já está ativo, pula
                else:
                    # SE EXISTE MAS ESTÁ INATIVO, REATIVA
                    antes_vinculo = snapshot_pessoa_telefone(vinculo)
                    vinculo.status = 1
                    vinculo.dataalteracao = datetime.utcnow()
                    mensagem_log = "Vínculo pessoa-telefone reativado"
            else:
                # SE NÃO EXISTE, CRIA UM NOVO
                antes_vinculo = ""
                vinculo = PessoaTelefone(
                    idtelefone=idtelefone,
                    idpessoa=idpessoa,
                    dataalteracao=datetime.utcnow(),
                    status=1
                )
                db.session.add(vinculo)
                mensagem_log = "Vínculo pessoa-telefone criado"

            db.session.flush()

            registrar_log(
                entidade="pessoa_telefone",
                entidade_id=vinculo.id,
                antes=antes_vinculo,
                depois=snapshot_pessoa_telefone(vinculo),
                retorno="SUCESSO",
                mensagem=mensagem_log
            )

            # 2. CRIA PENDÊNCIA (apenas se não existir uma ativa)
            pendencia_existe = Pendencias.query.filter_by(
                tipopendencia='4',
                idpessoatelefone=vinculo.id,
                status=1
            ).first()

            if not pendencia_existe:
                # Ajuste conforme o campo real da sua tabela Pessoa
                pessoa_desc = (
                    vinculo.pessoa.nome
                    if hasattr(vinculo.pessoa, "nome")
                    else vinculo.idpessoa
                )

                patrimonio = vinculo.telefone.patrimonio
                serial = vinculo.telefone.serial
                mac = vinculo.telefone.macaddress

                descricao = f"Vincular a pessoa: {pessoa_desc} ao telefone PATRIMÔNIO: {patrimonio}; SERIAL: {serial}; MAC: {mac}"

                pendencia = Pendencias(
                    descricaotipopendencia=descricao,
                    tipopendencia='4',
                    idpessoatelefone=vinculo.id,
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
                    mensagem="Pendência criada para vínculo de pessoa"
                )

        db.session.commit()
        return jsonify({"mensagem": "Pessoa(s) processada(s) e pendências atualizadas"}), 200

    except Exception as e:
        db.session.rollback()
        print("ERRO AO VINCULAR PESSOA AO TELEFONE:", e)
        return jsonify({"erro": "Erro interno"}), 500



def remover_pessoa_telefone_controller(id_vinculo):
    try:
        vinculo = PessoaTelefone.query.get(id_vinculo)
        if not vinculo:
            return jsonify({"erro": "Vínculo não encontrado"}), 404

        antes = snapshot_pessoa_telefone(vinculo)

        # 1. CRIA PENDÊNCIA DE DESVINCULO (apenas se não existir uma ativa)
        pendencia_existe = Pendencias.query.filter_by(
            tipopendencia='42',
            idpessoatelefone=id_vinculo,
            status=1
        ).first()

        if not pendencia_existe:
            # Ajuste conforme o campo real da sua tabela Pessoa
            pessoa_desc = (
                vinculo.pessoa.nome
                if hasattr(vinculo.pessoa, "nome")
                else vinculo.idpessoa
            )

            patrimonio = vinculo.telefone.patrimonio
            serial = vinculo.telefone.serial
            mac = vinculo.telefone.macaddress

            descricao = f"Desvincular a pessoa: {pessoa_desc} do telefone PATRIMÔNIO: {patrimonio}; SERIAL: {serial}; MAC: {mac}"

            pendencia = Pendencias(
                descricaotipopendencia=descricao,
                tipopendencia='42',
                idpessoatelefone=id_vinculo,
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
                mensagem="Pendência criada para desvínculo de pessoa"
            )

        # 2. DESATIVA O REGISTRO (Muda status de 1 para 0)
        vinculo.status = 0
        db.session.commit()

        registrar_log(
            entidade="pessoa_telefone",
            entidade_id=id_vinculo,
            antes=antes,
            depois=snapshot_pessoa_telefone(vinculo),
            retorno="SUCESSO",
            mensagem="Vínculo pessoa-telefone desativado"
        )

        return jsonify({"mensagem": "Pessoa desvinculada com sucesso"}), 200

    except Exception as e:
        db.session.rollback()
        # ... log de erro ...
        return jsonify({"erro": "Erro interno"}), 500

