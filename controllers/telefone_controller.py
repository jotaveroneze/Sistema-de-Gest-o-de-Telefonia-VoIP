from datetime import datetime, date, time

from extensions import db
from flask import render_template, jsonify, request

from models.telefone_model import Telefone
from models.telefoneramal_model import TelefoneRamal
from models.pessoatelefone_model import PessoaTelefone
from models.entregas_model import Entregas

from utils.logs import registrar_log
# ===============================
# LISTAR
# ===============================
def listar_telefone():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip().lower()  # Do input JS

    per_page = 5  # ✅ FIXO 5, igual listar_pessoa!

    # ✅ Query base: só ativos, ordenado
    query = Telefone.query.filter_by(status=1).order_by(Telefone.patrimonio)

    if search:  # ✅ Filtra modelo/patrimônio/serial/MAC (campos principais)
        query = query.filter(
            db.or_(
                Telefone.modelo.has(nome__ilike=f'%{search}%'),  # Assumindo modelo.nome
                Telefone.patrimonio.ilike(f'%{search}%'),
                Telefone.serial.ilike(f'%{search}%'),
                Telefone.macaddress.ilike(f'%{search}%')
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # ✅ Processa só itens da página (eficiente!)
    resultado = []
    for t in pagination.items:
        # 🔹 Ramais (igual seu código)
        ramais = TelefoneRamal.query.filter_by(idtelefone=t.id, status=1).all()
        lista_ramal = [r.ramal.numero for r in ramais] if ramais else ["-"]

        # 🔹 Pessoas vinculadas (igual)
        pessoas_telefone = PessoaTelefone.query.filter_by(idtelefone=t.id, status=1).all()
        lista_pessoa = []
        lista_funcional = []
        lista_cpf = []
        lista_idpessoa = []

        if pessoas_telefone:
            for pt in pessoas_telefone:
                if pt.pessoa:
                    lista_pessoa.append(pt.pessoa.nome)
                    lista_funcional.append(pt.pessoa.funcional)
                    lista_cpf.append(pt.pessoa.cpf)
                    lista_idpessoa.append(pt.pessoa.id)
        else:
            lista_pessoa = ["-"]
            lista_funcional = ["-"]
            lista_cpf = ["-"]
            lista_idpessoa = [None]

        # 🔹 Lugar / Departamento (igual, otimizado)
        iddepartamento = None
        secretaria = "-"
        departamento = "-"
        if t.lugartelefone and t.lugartelefone.departamento:
            iddepartamento = t.lugartelefone.departamento.id
            departamento = t.lugartelefone.departamento.nome
            if t.lugartelefone.departamento.secretaria:
                secretaria = t.lugartelefone.departamento.secretaria.sigla

        # 🔹 Entregue (igual)
        entregue = Entregas.query.filter_by(idtelefone=t.id, status=1).first()

        # 🔹 Datas (igual, mas só para este telefone)
        datas_pessoa = [pt.dataalteracao for pt in pessoas_telefone if pt.dataalteracao]
        datas_ramais = [rm.dataalteracao for rm in ramais if rm.dataalteracao]

        def to_datetime(d):
            if isinstance(d, date) and not isinstance(d, datetime):
                return datetime.combine(d, time.min)
            return d

        todas_datas = []
        if datas_pessoa: todas_datas.append(to_datetime(max(datas_pessoa)))
        if datas_ramais: todas_datas.append(to_datetime(max(datas_ramais)))
        ultimaalteracao = max(todas_datas) if todas_datas else None

        resultado.append({
            "id": t.id,
            "modelo": t.modelo.nome if t.modelo else "-",
            "patrimonio": t.patrimonio,
            "serial": t.serial,
            "macaddress": t.macaddress,
            "secretaria": secretaria,
            "departamento": departamento,
            "iddepartamento": iddepartamento,
            "lugartelefone": t.lugartelefone.nomelugar if t.lugartelefone else "-",
            "idlugartelefone": t.idlugartelefone,
            "andar": t.lugartelefone.andar if t.lugartelefone else None,
            "endereco": t.lugartelefone.endereco if t.lugartelefone else None,
            "pessoas": lista_pessoa,
            "funcionais": lista_funcional,
            "cpfs": lista_cpf,
            "idpessoas": lista_idpessoa,
            "montado": t.montado,
            "patrimoniado": t.patrimoniado,
            "defeito": t.defeito,
            "entregue": entregue.dataentrega.strftime("%d/%m/%Y") if entregue and entregue.dataentrega else None,
            "ramais": lista_ramal,
            "ultimaalteracao": ultimaalteracao.strftime("%d/%m/%Y %H:%M") if ultimaalteracao else None,  # ✅ Formato melhor
        })

    return {
        'telefones': resultado,
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }


# ===============================
# SNAPSHOT
# ===============================
def snapshot_telefone(t):
    return {
        "id": t.id,
        "patrimonio": t.patrimonio,
        "serial": t.serial,
        "macaddress": t.macaddress,
        "nometelefone": t.nometelefone,
        "processocompra": t.processocompra,
        "notafiscal": t.notafiscal,
        "montado": t.montado,
        "patrimoniado": t.patrimoniado,
        "defeito": t.defeito,
        "idmodelo": t.idmodelo,
        "idlugartelefone": t.idlugartelefone,
        "status": t.status
    }


# ===============================
# ADICIONAR
# ===============================
def adicionar_telefone(data):
    try:
        telefone = Telefone(
            patrimonio=data.get("patrimonio"),
            serial=data.get("serial"),
            macaddress=data.get("macaddress"),
            nometelefone=data.get("nometelefone"),
            processocompra=data.get("processocompra"),
            notafiscal=data.get("notafiscal"),
            montado=data.get("montado", False),
            patrimoniado=data.get("patrimoniado", False),
            defeito=data.get("defeito", False),
            idmodelo=data.get("idmodelo"),
            idlugartelefone=data.get("idlugarlocal")
        )

        db.session.add(telefone)
        db.session.flush()  # 🔑 garante ID

        registrar_log(
            entidade="telefone",
            entidade_id=telefone.id,
            antes="",
            depois=snapshot_telefone(telefone),
            retorno="SUCESSO",
            mensagem="Telefone cadastrado"
        )

        db.session.commit()
        return telefone.to_dict(), 201

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="telefone",
            entidade_id=None,
            antes="",
            depois=data,
            retorno="ERRO",
            mensagem=str(e)
        )

        return {"erro": "Erro ao cadastrar telefone"}, 500


# ===============================
# EDITAR ✅ CORRIGIDO
# ===============================
def editar_telefone(id, data):
    try:
        telefone = Telefone.query.get(id)
        if not telefone:
            return {"erro": "Telefone não encontrado"}, 404

        antes = snapshot_telefone(telefone)

        telefone.patrimonio = data.get("patrimonio", telefone.patrimonio)
        telefone.serial = data.get("serial", telefone.serial)
        telefone.macaddress = data.get("macaddress", telefone.macaddress)
        telefone.nometelefone = data.get("nometelefone", telefone.nometelefone)
        telefone.processocompra = data.get("processocompra", telefone.processocompra)
        telefone.notafiscal = data.get("notafiscal", telefone.notafiscal)
        telefone.montado = data.get("montado", telefone.montado)
        telefone.patrimoniado = data.get("patrimoniado", telefone.patrimoniado)
        telefone.defeito = data.get("defeito", telefone.defeito)
        telefone.idmodelo = data.get("idmodelo", telefone.idmodelo)
        telefone.idlugartelefone = data.get("idlugarlocal", telefone.idlugartelefone)

        db.session.commit()

        depois = snapshot_telefone(telefone)

        registrar_log(
            entidade="telefone",
            entidade_id=telefone.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Telefone editado"
        )

        return telefone.to_dict(), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="telefone",
            entidade_id=id,
            antes="",
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        return {"erro": "Erro interno"}, 500


# ===============================
# REMOVER (SOFT DELETE)
# ===============================
def remover_telefone(id):
    try:
        telefone = Telefone.query.get(id)
        if not telefone:
            return jsonify({"erro": "Telefone não encontrado"}), 404

        antes = snapshot_telefone(telefone)

        telefone.status = 0
        telefone.patrimonio = f"[DELETADO {telefone.id}] {telefone.patrimonio}"

        db.session.commit()

        depois = snapshot_telefone(telefone)

        registrar_log(
            entidade="telefone",
            entidade_id=telefone.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Telefone desativado"
        )

        return jsonify({"mensagem": "Telefone excluído com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="telefone",
            entidade_id=id,
            antes="",
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        return jsonify({"erro": "Erro interno"}), 500


def handle_telefone():
    return render_template("telefone/telefone.html")
