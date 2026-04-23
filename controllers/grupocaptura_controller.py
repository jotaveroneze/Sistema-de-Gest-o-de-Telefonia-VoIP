import traceback
from datetime import datetime

from flask_login import current_user
from sqlalchemy import and_

from controllers.pendencias_controller import snapshot_pendencia
from controllers.ramal_controller import snapshot_ramal
from extensions import db
from models import Telefone
from models.grupocaptura_model import Grupocaptura
from flask import render_template, jsonify

from models.pendencias_model import Pendencias
from models.pessoa_model import Pessoa
from models.pessoatelefone_model import PessoaTelefone
from models.ramal_model import Ramal
from models.telefoneramal_model import TelefoneRamal
from utils.logs import registrar_log

# Listar todos os grupocapturas
def listar_grupocapturas():
    grupocapturas = (
        Grupocaptura.query
        .filter_by(status=1)
        .order_by(Grupocaptura.nome)
        .all()
    )

    lista = []
    for u in grupocapturas:
        lista.append({
            "id": u.id,
            "nome": u.nome,
        })
    return lista

def snapshot_grupocaptura(dep):
    return {
        "id": dep.id,
        "nome": dep.nome,
        "status": dep.status
    }

# Adicionar novo grupocaptura
def adicionar_grupocaptura(nome):
    nome = nome.strip() if nome else ""

    if not nome:
        return {'erro': 'Nome é obrigatório'}, 400

    # ✅ Verifica ANTES de qualquer inserção
    existente = Grupocaptura.query.filter(
        db.func.lower(Grupocaptura.nome) == nome.lower()
    ).first()

    if existente:
        return {'erro': 'Grupo de captura já cadastrado'}, 409

    try:
        dep = Grupocaptura(nome=nome, status=1)
        db.session.add(dep)
        db.session.flush()  # ✅ Agora é seguro — duplicata já foi descartada acima

        depois = snapshot_grupocaptura(dep)

        registrar_log(
            entidade='grupocaptura',
            entidade_id=dep.id,
            antes="",
            depois=depois,
            retorno='SUCESSO',
            mensagem='Grupo Captura cadastrado com sucesso'
        )

        db.session.commit()
        return dep.to_dict(), 201  # ✅ Retorna status junto

    except IntegrityError:
        db.session.rollback()
        return {'erro': 'Grupo de captura já cadastrado'}, 409

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='grupocaptura',
            entidade_id=None,
            antes="",
            depois={"nome": nome},
            retorno='ERRO',
            mensagem=str(e)
        )

        return {'erro': 'Erro interno ao cadastrar'}, 500


# Editar grupocaptura
def editar_grupocaptura(id, nome):
    try:
        dep = Grupocaptura.query.get(id)
        if not dep:
            raise LookupError("Grupo Captura não encontrado")

        if not nome:
            raise ValueError("Nome é obrigatório")

        # 📌 ANTES
        antes = snapshot_grupocaptura(dep)

        # 📌 ALTERAÇÃO
        dep.nome = nome

        db.session.commit()

        # 📌 DEPOIS
        depois = snapshot_grupocaptura(dep)

        registrar_log(
            entidade='grupocaptura',
            entidade_id=dep.id,
            antes=antes,
            depois=depois,
            retorno='SUCESSO',
            mensagem='Grupo Captura editado com sucesso'
        )

        return dep.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='grupocaptura',
            entidade_id=id,
            antes="",
            depois="",
            retorno='ERRO',
            mensagem=str(e)
        )

        raise e


# Remover grupocaptura
def remover_grupocaptura(id):
    try:
        dep = Grupocaptura.query.get(id)
        if not dep:
            return jsonify({"erro": "Grupo Captura não encontrado"}), 404

        # 📌 ANTES
        antes = snapshot_grupocaptura(dep)

        # 📌 SOFT DELETE
        dep.status = 0
        dep.nome = f"[DELETADO {dep.id}] {dep.nome}"

        db.session.commit()

        # 📌 DEPOIS
        depois = snapshot_grupocaptura(dep)

        registrar_log(
            entidade='grupocaptura',
            entidade_id=dep.id,
            antes=antes,
            depois=depois,
            retorno='SUCESSO',
            mensagem='Grupo Captura desativado (soft delete)'
        )

        return jsonify({"mensagem": "Grupo Captura desativado com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='grupocaptura',
            entidade_id=id,
            antes="",
            depois="",
            retorno='ERRO',
            mensagem=str(e)
        )

        print("ERRO AO DESATIVAR GRUPO CAPTURA:", e)
        return jsonify({"erro": "Erro interno"}), 500

def alterar_grupo_captura_controller(data):
    try:
        idramal = data.get("idramal")
        idgrupocaptura = data.get("idgrupocaptura")  # pode ser None

        if not idramal:
            return jsonify({"erro": "idramal não informado"}), 400

        ramal = db.session.get(Ramal, idramal)
        if not ramal:
            return jsonify({"erro": "Ramal não encontrado"}), 404

        antes = snapshot_ramal(ramal)
        idgrupocaptura = int(idgrupocaptura) if idgrupocaptura is not None else None
        grupo_novo = None
        if idgrupocaptura is not None:
            grupo_novo = db.session.get(Grupocaptura, idgrupocaptura)
            if not grupo_novo:
                return jsonify({"erro": "Grupo de captura não encontrado"}), 404

        # 🔹 Se não houve mudança, não faz nada
        if ramal.idgrupocaptura == idgrupocaptura:
            return jsonify({
                "sucesso": True,
                "mensagem": "Grupo de captura já está definido"
            }), 200

        # 🔹 Descrição da pendência
        ramal_desc = ramal.numero
        grupo_antigo = ramal.grupocaptura.nome if ramal.grupocaptura else "Nenhum"
        grupo_novo_desc = grupo_novo.nome if grupo_novo else "Nenhum"

        descricao = (
            f"Alterar grupo de captura do ramal ({ramal_desc}) "
            f"de ({grupo_antigo}) para ({grupo_novo_desc})"
        )

        # 🔹 Verifica se já existe pendência ativa
        pendencia_existe = Pendencias.query.filter_by(
            tipopendencia='5',
            status=1
        ).first()

        if not pendencia_existe:
            pendencia = Pendencias(
                descricaotipopendencia=descricao,
                tipopendencia='5',
                idusuarioresponsavel=current_user.id,
                dataentrada=datetime.utcnow(),
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
                mensagem="Pendência criada para alteração de grupo de captura"
            )

        # 🔹 Aplica alteração
        ramal.idgrupocaptura = int(idgrupocaptura) if idgrupocaptura else None
        db.session.commit()

        depois = snapshot_ramal(ramal)

        registrar_log(
            entidade="ramal",
            entidade_id=ramal.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Grupo de captura do ramal alterado"
        )

        return jsonify({
            "sucesso": True,
            "idramal": ramal.id,
            "idgrupocaptura": ramal.idgrupocaptura
        }), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="ramal",
            entidade_id=data.get("idramal"),
            antes="",
            depois="",
            retorno="ERRO",
            mensagem=f"Erro ao alterar grupo de captura: {str(e)}"
        )

        return jsonify({"erro": "Erro interno"}), 500


def listar_ramais_por_grupo_captura_controller(id_grupo):
    registros = (
        db.session.query(
            Ramal.id.label("idramal"),
            Ramal.numero,
            Pessoa.nome.label("usuario")
        )
        .join(TelefoneRamal, TelefoneRamal.idramal == Ramal.id)
        .join(Telefone, Telefone.id == TelefoneRamal.idtelefone)
        .join(
            PessoaTelefone,
            and_(
                PessoaTelefone.idtelefone == Telefone.id,
                PessoaTelefone.status == 1
            )
        )
        .join(Pessoa, Pessoa.id == PessoaTelefone.idpessoa)
        .filter(
            Ramal.idgrupocaptura == id_grupo,
            Ramal.status == 1,
            TelefoneRamal.status == 1,
            Telefone.status == 1
        )
        .order_by(Ramal.numero, Pessoa.nome)
        .all()
    )

    resultado = {}

    for r in registros:
        resultado.setdefault(r.idramal, {
            "id": r.idramal,
            "numero": r.numero,
            "usuarios": []
        })

        resultado[r.idramal]["usuarios"].append(r.usuario)

    return list(resultado.values())

def vincular_ramal_grupo_captura_controller(data):
    try:
        idramal = data.get("idramal")
        idgrupocaptura = data.get("idgrupocaptura")

        if not idramal or not idgrupocaptura:
            return jsonify({"erro": "Dados inválidos"}), 400

        ramal = db.session.get(Ramal, idramal)
        if not ramal:
            return jsonify({"erro": "Ramal não encontrado"}), 404

        grupo = db.session.get(Grupocaptura, idgrupocaptura)
        if not grupo:
            return jsonify({"erro": "Grupo de captura não encontrado"}), 404

        if ramal.idgrupocaptura:
            return jsonify({"erro": "Ramal já vinculado a um grupo"}), 400

        antes = snapshot_ramal(ramal)

        descricao = (
            f"Vincular ramal ({ramal.numero}) "
            f"ao grupo de captura ({grupo.nome})"
        )

        # 🔹 Verifica pendência ativa
        pendencia_existe = Pendencias.query.filter_by(
            tipopendencia='5',
            status=1,
            descricaotipopendencia=descricao,
        ).first()

        if not pendencia_existe:
            pendencia = Pendencias(
                descricaotipopendencia=descricao,
                tipopendencia='5',
                idusuarioresponsavel=current_user.id,
                dataentrada=datetime.utcnow(),
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
                mensagem="Pendência criada para vínculo de grupo de captura"
            )

        ramal.idgrupocaptura = grupo.id
        db.session.commit()

        depois = snapshot_ramal(ramal)

        registrar_log(
            entidade="ramal",
            entidade_id=ramal.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Ramal vinculado ao grupo de captura"
        )

        return jsonify({"sucesso": True}), 200


    except Exception as e:

        db.session.rollback()

        traceback.print_exc()  # ← imprime o traceback no terminal

        try:

            registrar_log(  # ← indentado dentro do try

                entidade="ramal",

                entidade_id=data.get("idramal"),

                antes="",

                depois="",

                retorno="ERRO",

                mensagem=f"Erro ao vincular ramal ao grupo de captura: {str(e)}"

            )

        except Exception as log_err:

            print("Erro ao registrar log:", log_err)  # ← vírgula + texto corrigido

        return jsonify({"erro": "Erro interno"}), 500


def desvincular_ramal_grupo_captura_controller(data):
    try:
        idramal = data.get("idramal")

        if not idramal:
            return jsonify({"erro": "idramal não informado"}), 400

        ramal = db.session.get(Ramal, idramal)
        if not ramal:
            return jsonify({"erro": "Ramal não encontrado"}), 404

        if ramal.idgrupocaptura is None:
            return jsonify({"erro": "Ramal não está vinculado a grupo"}), 400

        antes = snapshot_ramal(ramal)

        grupo_antigo = ramal.grupocaptura.nome if ramal.grupocaptura else "Nenhum"

        descricao = (
            f"Desvincular ramal ({ramal.numero}) "
            f"do grupo de captura ({grupo_antigo})"
        )

        pendencia_existe = Pendencias.query.filter_by(
            tipopendencia='5',
            status=1,
            descricaotipopendencia = descricao,
        ).first()

        if not pendencia_existe:
            pendencia = Pendencias(
                descricaotipopendencia=descricao,
                tipopendencia='5',
                idusuarioresponsavel=current_user.id,
                dataentrada=datetime.utcnow(),
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
                mensagem="Pendência criada para desvínculo de grupo de captura"
            )

        ramal.idgrupocaptura = None
        db.session.commit()

        depois = snapshot_ramal(ramal)

        registrar_log(
            entidade="ramal",
            entidade_id=ramal.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Ramal desvinculado do grupo de captura"
        )

        return jsonify({"sucesso": True}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="ramal",
            entidade_id=data.get("idramal"),
            antes="",
            depois="",
            retorno="ERRO",
            mensagem=f"Erro ao desvincular ramal do grupo de captura: {str(e)}"
        )

        return jsonify({"erro": "Erro interno"}), 500


def handle_grupocaptura():
    return render_template("grupocaptura/grupocaptura.html")
