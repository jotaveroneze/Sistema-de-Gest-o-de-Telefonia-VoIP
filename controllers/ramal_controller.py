from extensions import db
from models.grupocaptura_model import Grupocaptura
from models.numerogrupo_model import Numerogrupo
from models.ramal_model import Ramal
from models.telefoneramal_model import TelefoneRamal
from models.operadora_model import Operadora
from models.tronco_model import Tronco
from models.ramalnumerogrupo_model import RamalNumeroGrupo
from flask import render_template, jsonify, request
from sqlalchemy import exists, and_, or_
from models.pessoatelefone_model import PessoaTelefone
from models.telefone_model import Telefone
from models.pessoa_model import Pessoa
from utils.logs import registrar_log

def listar_ramal():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page_RAMAL', 15, type=int)

    # FILTROS (adicione ANTES da query)
    search = request.args.get('search', '').strip()
    gravado_filter = request.args.get('gravado', 'todos').strip()

    filtros = [Ramal.status == 1]
    if search:
        filtros.append(Ramal.numero.like(f'%{search}%'))
    if gravado_filter != 'todos':
        gravado_val = 1 if gravado_filter == 'sim' else 0
        filtros.append(Ramal.gravado == gravado_val)

    paginacao = (
        db.session.query(
            Ramal,
            exists().where(
                or_(
                    and_(TelefoneRamal.idramal == Ramal.id, TelefoneRamal.status == 1),
                    and_(Numerogrupo.numero == Ramal.numero, Numerogrupo.status == 1)
                )
            ).label("em_uso")
        )
        .filter(*filtros)
        .order_by(Ramal.numero)
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    resultado = []
    for ramal, em_uso in paginacao.items:
        d = ramal.to_dict()
        d["em_uso"] = bool(em_uso)
        resultado.append(d)

    return jsonify({
        "ramais": resultado,
        "page": paginacao.page,
        "pages": paginacao.pages,
        "total": paginacao.total,
        "has_prev": paginacao.has_prev,
        "has_next": paginacao.has_next,
    })


def listar_ramal_detalhe():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page_RAMAL', 10, type=int)

    # FILTROS (adicione ANTES da query)
    search = request.args.get('search', '').strip()
    gravado_filter = request.args.get('gravado', 'todos').strip()

    filtros = [Ramal.status == 1]
    if search:
        filtros.append(Ramal.numero.like(f'%{search}%'))
    if gravado_filter != 'todos':
        gravado_val = 1 if gravado_filter == 'sim' else 0
        filtros.append(Ramal.gravado == gravado_val)

    # primeira parte: pagina só os Ramais + metadados básicos
    base_query = (
        db.session.query(
            Ramal,
            Tronco.numerochave,
            Tronco.ramalinicial,
            Tronco.ramalfinal,
            Operadora.nome.label("operadora"),
            Grupocaptura.nome.label("grupo_captura"),
            exists().where(
                or_(
                    and_(TelefoneRamal.idramal == Ramal.id, TelefoneRamal.status == 1),
                    and_(Numerogrupo.numero == Ramal.numero, Numerogrupo.status == 1)
                )
            ).label("em_uso")
        )
        .join(Tronco, Tronco.id == Ramal.idtronco)
        .join(Operadora, Operadora.id == Tronco.idoperadora)
        .filter(*filtros)
        .outerjoin(Grupocaptura, Grupocaptura.id == Ramal.idgrupocaptura)
        .order_by(Ramal.numero)
    )

    paginacao = base_query.paginate(page=page, per_page=per_page, error_out=False)

    ramais_ids = [r.id for r, *_ in paginacao.items]

    # busca grupos só para os ramais desta página
    grupos = (
        db.session.query(RamalNumeroGrupo, Numerogrupo)
        .join(Numerogrupo, Numerogrupo.id == RamalNumeroGrupo.idnumerogrupo)
        .filter(
            RamalNumeroGrupo.status == 1,
            RamalNumeroGrupo.idramal.in_(ramais_ids)
        )
        .all()
    )
    grupos_por_ramal = {}
    for ramalGrupo, numerogrupo in grupos:
        grupos_por_ramal.setdefault(ramalGrupo.idramal, []).append({
            "idramalnumerogrupo": ramalGrupo.id,
            "idnumerogrupo": numerogrupo.id,
            "numero": numerogrupo.numero,
            "descricao": numerogrupo.descricao,
            "departamento": numerogrupo.departamento.nome if numerogrupo.departamento else None,
            "sigla": (
                numerogrupo.departamento.secretaria.sigla
                if numerogrupo.departamento and numerogrupo.departamento.secretaria
                else None
            )
        })

    # busca telefones só para os ramais desta página
    telefones = (
        db.session.query(TelefoneRamal, Telefone, PessoaTelefone)
        .join(Telefone, Telefone.id == TelefoneRamal.idtelefone)
        .outerjoin(
            PessoaTelefone,
            and_(
                PessoaTelefone.idtelefone == Telefone.id,
                PessoaTelefone.status == 1
            )
        )
        .filter(
            Telefone.status == 1,
            TelefoneRamal.status == 1,
            TelefoneRamal.idramal.in_(ramais_ids)
        )
        .all()
    )

    telefones_por_ramal = {}
    for telefoneRamal, telefone, pessoaTelefone in telefones:
        ramal_id = telefoneRamal.idramal
        if ramal_id not in telefones_por_ramal:
            telefones_por_ramal[ramal_id] = {}

        ramal_dict = telefones_por_ramal[ramal_id]
        if telefone.id not in ramal_dict:
            ramal_dict[telefone.id] = {
                "idtelefoneramal": telefoneRamal.id,
                "idtelefone": telefone.id,
                "patrimonio": telefone.patrimonio,
                "serial": telefone.serial,
                "pessoas": []
            }

        if pessoaTelefone and pessoaTelefone.pessoa:
            pessoa = pessoaTelefone.pessoa
            ramal_dict[telefone.id]["pessoas"].append({
                "idpessoatelefone": pessoaTelefone.id,
                "nome": pessoa.nome,
                "funcional": pessoa.funcional,
                "cpf": pessoa.cpf,
                "departamento": pessoa.departamento.nome if pessoa.departamento else None,
                "secretaria": (
                    pessoa.departamento.secretaria.sigla
                    if pessoa.departamento and pessoa.departamento.secretaria
                    else None
                )
            })

    resultado = []
    for (
            ramal,
            numerochave,
            ramalinicial,
            ramalfinal,
            operadora,
            grupo_captura,
            em_uso
    ) in paginacao.items:
        d = ramal.to_dict()
        d["numerochave"] = numerochave
        d["ramalinicial"] = ramalinicial
        d["ramalfinal"] = ramalfinal
        d["operadora"] = operadora
        d["grupo_captura"] = grupo_captura
        d["em_uso"] = bool(em_uso)
        d["numeros_grupo"] = grupos_por_ramal.get(ramal.id, [])
        d["telefones"] = list(telefones_por_ramal.get(ramal.id, {}).values())
        resultado.append(d)

    return jsonify({
        "ramais": resultado,
        "page": paginacao.page,
        "pages": paginacao.pages,
        "total": paginacao.total,
        "has_prev": paginacao.has_prev,
        "has_next": paginacao.has_next,
    })


def listar_ramal_em_uso():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page_RAMAL', 10, type=int)

    # FILTROS (adicione ANTES da query)
    search = request.args.get('search', '').strip()
    gravado_filter = request.args.get('gravado', 'todos').strip()

    filtros = [Ramal.status == 1]
    if search:
        filtros.append(Ramal.numero.like(f'%{search}%'))
    if gravado_filter != 'todos':
        gravado_val = 1 if gravado_filter == 'sim' else 0
        filtros.append(Ramal.gravado == gravado_val)

    # 1️⃣ Query para CONTAR/PAGINAR RAMAIS ÚNICOS em uso
    ramais_query = (
        db.session.query(Ramal.id)
        .filter(*filtros)
        .filter(
            or_(
                exists().where(
                    and_(
                        TelefoneRamal.idramal == Ramal.id,
                        TelefoneRamal.status == 1
                    )
                ),
                exists().where(
                    and_(
                        Numerogrupo.numero == Ramal.numero,
                        Numerogrupo.status == 1
                    )
                )
            )
        )
        .distinct()  # ✅ Únicos
        .order_by(Ramal.numero)
    )

    # 2️⃣ Paginação de RAMAIS únicos
    ramais_paginados = ramais_query.paginate(page=page, per_page=per_page, error_out=False)
    ramais_ids = [rid[0] for rid in ramais_paginados.items]  # IDs da página atual

    # 3️⃣ Busca detalhes só para estes ramais (eficiente!)
    if not ramais_ids:
        return jsonify({
            "ramais": [],
            "page": ramais_paginados.page,
            "pages": ramais_paginados.pages,
            "total": ramais_paginados.total,
            "has_prev": ramais_paginados.has_prev,
            "has_next": ramais_paginados.has_next,
        })

    # 4️⃣ Detalhes completos só para ramais da página
    registros = (
        db.session.query(Ramal, TelefoneRamal, Telefone, PessoaTelefone)
        .outerjoin(TelefoneRamal, and_(TelefoneRamal.idramal == Ramal.id, TelefoneRamal.status == 1))
        .outerjoin(Telefone, and_(Telefone.id == TelefoneRamal.idtelefone, Telefone.status == 1))
        .outerjoin(PessoaTelefone, and_(PessoaTelefone.idtelefone == Telefone.id, PessoaTelefone.status == 1))
        .filter(Ramal.id.in_(ramais_ids))
        .order_by(Ramal.numero, Telefone.id)
        .all()
    )

    resultado = {}
    for ramal, telefoneRamal, telefone, pessoaTelefone in registros:
        if ramal.id not in resultado:
            resultado[ramal.id] = {
                "id": ramal.id,
                "numero": ramal.numero,
                "gravado": ramal.gravado,
                "em_uso": True,
                "telefones": []
            }

        if telefone:
            telefone_existente = next(
                (t for t in resultado[ramal.id]["telefones"] if t["idtelefone"] == telefone.id),
                None
            )
            if not telefone_existente:
                telefone_existente = {
                    "idtelefoneramal": telefoneRamal.id if telefoneRamal else None,
                    "idtelefone": telefone.id,
                    "patrimonio": telefone.patrimonio,
                    "serial": telefone.serial,
                    "pessoas": []
                }
                resultado[ramal.id]["telefones"].append(telefone_existente)

            if pessoaTelefone and pessoaTelefone.pessoa:
                pessoa = pessoaTelefone.pessoa
                telefone_existente["pessoas"].append({
                    "idpessoatelefone": pessoaTelefone.id,
                    "nome": pessoa.nome,
                    "funcional": pessoa.funcional,
                    "cpf": pessoa.cpf,
                    "departamento": pessoa.departamento.nome if pessoa.departamento else None,
                    "secretaria": (
                        pessoa.departamento.secretaria.sigla
                        if pessoa.departamento and pessoa.departamento.secretaria
                        else None
                    )
                })

    return jsonify({
        "ramais": list(resultado.values()),
        "page": ramais_paginados.page,
        "pages": ramais_paginados.pages,
        "total": ramais_paginados.total,  # ✅ Agora 249!
        "has_prev": ramais_paginados.has_prev,
        "has_next": ramais_paginados.has_next,
    })




def listar_ramal_vago():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page_RAMAL', 10, type=int)

    # FILTROS (adicione ANTES da query)
    search = request.args.get('search', '').strip()
    gravado_filter = request.args.get('gravado', 'todos').strip()

    filtros = [Ramal.status == 1]
    if search:
        filtros.append(Ramal.numero.like(f'%{search}%'))
    if gravado_filter != 'todos':
        gravado_val = 1 if gravado_filter == 'sim' else 0
        filtros.append(Ramal.gravado == gravado_val)

    paginacao = (
        db.session.query(Ramal)
        .filter(Ramal.status == 1)
        .filter(~exists().where(and_(TelefoneRamal.idramal == Ramal.id, TelefoneRamal.status == 1)))
        .filter(~exists().where(and_(Numerogrupo.numero == Ramal.numero, Numerogrupo.status == 1)))
        .order_by(Ramal.numero)
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    resultado = [r.to_dict() | {"em_uso": False} for r in paginacao.items]

    return jsonify({
        "ramais": resultado,
        "page": paginacao.page,
        "pages": paginacao.pages,
        "total": paginacao.total,
        "has_prev": paginacao.has_prev,
        "has_next": paginacao.has_next,
    })


def snapshot_ramal(r):
    return {
        "id": r.id,
        "numero": r.numero,
        "idtronco": r.idtronco,
        "gravado": r.gravado,
        "status": getattr(r, "status", None)
    }


def adicionar_ramal(numero, gravado, id_tronco):
    if not numero:
        raise ValueError("Número é obrigatório")

    if not id_tronco:
        raise ValueError("Tronco é obrigatório")

    try:
        # garante 0 ou 1
        gravado = 1 if gravado else 0

        ramal = Ramal(
            numero=numero,
            gravado=gravado,
            idtronco=id_tronco
        )

        db.session.add(ramal)

        # 🔑 Garante ID antes do commit
        db.session.flush()

        depois = {
            "id": ramal.id,
            "numero": ramal.numero,
            "gravado": ramal.gravado,
            "idtronco": ramal.idtronco,
            "status": ramal.status
        }

        registrar_log(
            entidade='ramal',
            entidade_id=ramal.id,
            antes="",
            depois=depois,
            retorno='SUCESSO',
            mensagem='Ramal cadastrado com sucesso'
        )

        db.session.commit()
        return ramal.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='ramal',
            entidade_id=None,
            antes="",
            depois={
                "numero": numero,
                "gravado": gravado,
                "idtronco": id_tronco
            },
            retorno='ERRO',
            mensagem=str(e)
        )

        raise e


# Editar
def editar_ramal(id, numero, idtronco, gravado):
    try:
        ramal = Ramal.query.get(id)
        if not ramal:
            raise LookupError("Ramal não encontrado")

        if not numero:
            raise ValueError("Número é obrigatório")

        if not idtronco:
            raise ValueError("Tronco é obrigatório")

        # 📌 ANTES
        antes = {
            "id": ramal.id,
            "numero": ramal.numero,
            "gravado": ramal.gravado,
            "idtronco": ramal.idtronco,
            "status": ramal.status
        }

        ramal.numero = numero
        ramal.idtronco = idtronco
        ramal.gravado = 1 if gravado else 0

        db.session.commit()

        # 📌 DEPOIS
        depois = {
            "id": ramal.id,
            "numero": ramal.numero,
            "gravado": ramal.gravado,
            "idtronco": ramal.idtronco,
            "status": ramal.status
        }

        registrar_log(
            entidade='ramal',
            entidade_id=ramal.id,
            antes=antes,
            depois=depois,
            retorno='SUCESSO',
            mensagem='Ramal editado com sucesso'
        )

        return ramal.to_dict()

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='ramal',
            entidade_id=id,
            antes="",
            depois="",
            retorno='ERRO',
            mensagem=str(e)
        )

        raise e


# Remover

def remover_ramal(id):
    try:
        ramal = Ramal.query.get(id)
        if not ramal:
            return jsonify({"erro": "Ramal não encontrado"}), 404

        # 📌 ANTES
        antes = {
            "id": ramal.id,
            "numero": ramal.numero,
            "gravado": ramal.gravado,
            "idtronco": ramal.idtronco,
            "status": ramal.status
        }

        ramal.status = 0

        # 📌 DEPOIS
        depois = {
            "id": ramal.id,
            "numero": ramal.numero,
            "gravado": ramal.gravado,
            "idtronco": ramal.idtronco,
            "status": ramal.status
        }

        db.session.commit()

        registrar_log(
            entidade='ramal',
            entidade_id=ramal.id,
            antes=antes,
            depois=depois,
            retorno='SUCESSO',
            mensagem='Ramal desativado (soft delete)'
        )

        return jsonify({"mensagem": "Ramal excluído com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade='ramal',
            entidade_id=id,
            antes="",
            depois="",
            retorno='ERRO',
            mensagem=str(e)
        )

        print("ERRO AO DESATIVAR RAMAL:", e)



def handle_ramal():
    return render_template("ramal/ramal.html")


def listar_ramais_disponiveis_por_grupo(id_numerogrupo):
    # ids de ramais já vinculados ao número de grupo
    ramais_vinculados = (
        RamalNumeroGrupo.query
        .with_entities(RamalNumeroGrupo.idramal)
        .filter_by(idnumerogrupo=id_numerogrupo, status=1)
        .subquery()
    )

    # ramais NÃO vinculados e ATIVOS (status = 1)
    ramais = (
        Ramal.query
        .filter(
            ~Ramal.id.in_(ramais_vinculados),
            Ramal.status == 1
        )
        .all()
    )

    return [
        {
            "id": r.id,
            "ramal": r.numero
        } for r in ramais
    ]

def listar_ramal_com_telefones():
    registros = (
        db.session.query(
            Ramal,
            TelefoneRamal,
            Telefone,
            PessoaTelefone,
            Pessoa,

            # 🔹 Número do ramal está em algum número de grupo ativo
            exists()
            .select_from(Numerogrupo)
            .where(
                and_(
                    Numerogrupo.numero == Ramal.numero,
                    Numerogrupo.status == 1
                )
            )
            .label("em_grupo")
        )
        .outerjoin(
            TelefoneRamal,
            and_(
                TelefoneRamal.idramal == Ramal.id,
                TelefoneRamal.status == 1
            )
        )
        .outerjoin(
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
        .outerjoin(
            Pessoa,
            and_(
                Pessoa.id == PessoaTelefone.idpessoa,
                Pessoa.status == 1
            )
        )
        .order_by(Ramal.numero)
        .all()
    )

    resultado = {}

    for ramal, tr, telefone, pt, pessoa, em_grupo in registros:

        if ramal.id not in resultado:
            resultado[ramal.id] = {
                **ramal.to_dict(),
                "em_uso": (tr is not None) or em_grupo,
                "em_grupo": em_grupo,
                "telefones": {}
            }

        if telefone:
            tel_dict = resultado[ramal.id]["telefones"].setdefault(
                telefone.id,
                {
                    "patrimonio": telefone.patrimonio,
                    "serial": telefone.serial,
                    "pessoas": []
                }
            )

            if pessoa:
                tel_dict["pessoas"].append({
                    "nome": pessoa.nome,
                    "funcional": pessoa.funcional,
                    "departamento": pessoa.departamento.nome if pessoa.departamento else "",
                    "secretaria": (
                        pessoa.departamento.secretaria.sigla
                        if pessoa.departamento and pessoa.departamento.secretaria
                        else ""
                    )
                })

    for r in resultado.values():
        r["telefones"] = list(r["telefones"].values())

    return list(resultado.values())

