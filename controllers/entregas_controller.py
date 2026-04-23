import os

from controllers.termo_controller import gerar_pdf_termo_telefone
from extensions import db
from models.entregas_model import Entregas
from models.telefone_model import Telefone
from datetime import datetime
from utils.logs import registrar_log
from models.pessoatelefone_model import PessoaTelefone
from flask import send_file, current_app


def snapshot_entrega(entrega):
    return {
        "id": entrega.id,
        "dataentrega": entrega.dataentrega.isoformat() if entrega.dataentrega else None,
        "iddepartamento": entrega.iddepartamento,
        "idpessoa": entrega.idpessoa,
        "idtelefone": entrega.idtelefone,
        "idlugartelefone": entrega.idlugartelefone,
        "status": entrega.status
    }

def salvar_termo_pdf(buffer, entrega_id):
    pasta = os.path.join(current_app.root_path, "static", "termos")
    os.makedirs(pasta, exist_ok=True)

    nome_arquivo = f"termo_telefone_{entrega_id}.pdf"
    caminho = os.path.join(pasta, nome_arquivo)

    buffer.seek(0)
    with open(caminho, "wb") as f:
        f.write(buffer.read())

    return f"/static/termos/{nome_arquivo}"

def entregarTelefone(data):
    try:
        entrega = Entregas(
            dataentrega=datetime.strptime(
                data.get("dataentrega"), "%Y-%m-%d"
            ) if data.get("dataentrega") else datetime.utcnow(),

            iddepartamento=data["iddepartamento"],
            idpessoa=data["idpessoa"],
            idtelefone=data["idtelefone"],
            idlugartelefone=data["idlugartelefone"],
            status=1
        )

        db.session.add(entrega)
        db.session.flush()  # gera entrega.id

        telefone = Telefone.query.get(data["idtelefone"])
        antes = {}

        if telefone:
            antes = {
                "telefone_id": telefone.id,
                "montado": telefone.montado
            }
            telefone.montado = True

        db.session.commit()

        # ==============================
        # 📄 GERAR E SALVAR TERMO
        # ==============================
        termo_url = None
        if telefone:
            pdf_buffer = gerar_pdf_termo_telefone([telefone.id])
            termo_url = salvar_termo_pdf(pdf_buffer, entrega.id)

        depois = snapshot_entrega(entrega)
        depois["telefone_montado"] = telefone.montado if telefone else None
        depois["termo_pdf"] = termo_url

        registrar_log(
            entidade="entregas",
            entidade_id=entrega.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Telefone entregue e termo gerado com sucesso"
        )

        return {
            "message": "Telefone entregue com sucesso",
            "entrega": entrega.to_dict(),
            "termo_url": termo_url
        }, 201

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="entregas",
            entidade_id=None,
            antes=data,
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        print("ERRO AO ENTREGAR TELEFONE:", e)
        return {"erro": "Erro ao registrar entrega"}, 500


def obter_dados_telefone_para_entrega(idtelefone):
    telefone = Telefone.query.get(idtelefone)

    if not telefone:
        return None

    # 🔹 Pessoa vinculada (pega a primeira ativa)
    pessoa_telefone = PessoaTelefone.query.filter_by(
        idtelefone=idtelefone
    ).first()

    idpessoa = pessoa_telefone.pessoa.id if pessoa_telefone and pessoa_telefone.pessoa else None

    # 🔹 Lugar / Departamento
    iddepartamento = None
    idlugartelefone = None

    if telefone.lugartelefone:
        idlugartelefone = telefone.lugartelefone.id
        if telefone.lugartelefone.departamento:
            iddepartamento = telefone.lugartelefone.departamento.id

    return {
        "idtelefone": telefone.id,
        "idpessoa": idpessoa,
        "iddepartamento": iddepartamento,
        "idlugartelefone": idlugartelefone
    }

def entregar_telefones_selecionados(data):
    try:
        telefones = data.get("telefones", [])

        if not telefones:
            return {"error": "Nenhum telefone informado"}, 400

        entregas_realizadas = []
        telefones_entregues = []  # 🔑 para o termo

        for idtelefone in telefones:
            dados = obter_dados_telefone_para_entrega(idtelefone)

            if not dados:
                raise Exception(f"Telefone {idtelefone} não encontrado")

            entrega = Entregas(
                dataentrega=datetime.strptime(
                    data.get("dataentrega"), "%Y-%m-%d"
                ) if data.get("dataentrega") else datetime.utcnow(),

                iddepartamento=dados["iddepartamento"],
                idpessoa=dados["idpessoa"],
                idtelefone=idtelefone,
                idlugartelefone=dados["idlugartelefone"],
                status=1
            )

            db.session.add(entrega)
            db.session.flush()

            telefone = Telefone.query.get(idtelefone)
            antes = {}

            if telefone:
                antes = {
                    "telefone_id": telefone.id,
                    "montado": telefone.montado
                }
                telefone.montado = True

            depois = snapshot_entrega(entrega)
            if telefone:
                depois["telefone_montado"] = telefone.montado

            registrar_log(
                entidade='entregas',
                entidade_id=entrega.id,
                antes=antes,
                depois=depois,
                retorno='SUCESSO',
                mensagem=f'Telefone {idtelefone} entregue com sucesso'
            )

            entregas_realizadas.append(entrega.id)
            telefones_entregues.append(idtelefone)

        # ✅ Commita tudo primeiro
        db.session.commit()

        # ==============================
        # 📄 GERAR TERMO DE TELEFONE
        # ==============================
        pdf_buffer = gerar_pdf_termo_telefone(telefones_entregues)

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="termo_entrega_telefone.pdf"
        )

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='entregas',
            entidade_id=None,
            antes=data,
            depois="",
            retorno='ERRO',
            mensagem=str(e)
        )

        print("ERRO AO ENTREGAR TELEFONES:", e)
        return {"error": "Erro ao registrar entregas"}, 500
