from sqlalchemy import distinct, and_, exists, or_

from extensions import db
from models.entregas_model import Entregas
from models.grupocaptura_model import Grupocaptura
from models.numerogrupo_model import Numerogrupo
from models.pendencias_model import Pendencias
from models.ramalnumerogrupo_model import RamalNumeroGrupo
from models.telefone_model import Telefone
from models.pessoa_model import Pessoa
from models.ramal_model import Ramal
from models.telefoneramal_model import TelefoneRamal
from models.secretaria_model import Secretaria
from flask import jsonify
from models.departamento_model import Departamento
from models.lugartelefone_model import LugarTelefone

def get_dashboard_dados():
    # Total de pessoas ativas
    total_ativos = db.session.query(Pessoa).filter(Pessoa.status == 1).count()

    # Total de telefones ativos
    total_telefone = db.session.query(Telefone).filter(Telefone.status == 1).count()

    # ============================
    # TELEFONES ENTREGUES
    # ============================
    telefones_entregues = (
        db.session.query(distinct(Entregas.idtelefone))
        .join(Telefone, Telefone.id == Entregas.idtelefone)
        .filter(
            Entregas.status == 1,
            Telefone.status == 1
        )
        .count()
    )

    # 1. Contagem de Vínculo Telefone/Ramal (idtelefoneramal não é nulo)
    ramal_pendente = (
        Pendencias.query
        .filter(
            Pendencias.idtelefoneramal.isnot(None),
            Pendencias.status == 1
        )
        .count()
    )

    # 2. Contagem de Alteração de Pessoa (idpessoatelefone não é nulo)
    pessoa_pendente = (
        Pendencias.query
        .filter(
            Pendencias.idpessoatelefone.isnot(None),
            Pendencias.status == 1
        )
        .count()
    )

    # 3. Contagem de Alteração de Número de Grupo (idramalnumerogrupo não é nulo)
    grupo_pendente = (
        Pendencias.query
        .filter(
            Pendencias.idramalnumerogrupo.isnot(None),
            Pendencias.status == 1
        )
        .count()
    )

    # 4. Contagem de Outras Pendências (onde todas as FKs específicas são nulas)
    outras_pendencias = (
        Pendencias.query
        .filter(
            Pendencias.idtelefoneramal.is_(None),
            Pendencias.idpessoatelefone.is_(None),
            Pendencias.idramalnumerogrupo.is_(None),
            Pendencias.status == 1
        )
        .count()
    )

    # Telefones não entregues
    telefones_nao_entregues = total_telefone - telefones_entregues

    # ============================
    # RAMAIS
    # ============================
    total_ramais = db.session.query(Ramal).count()

    ramais_em_uso = (
        db.session.query(Ramal.id)
        .filter(
            Ramal.status == 1,
            or_(
                # 📞 Ramal vinculado a telefone ativo
                exists().where(
                    and_(
                        TelefoneRamal.idramal == Ramal.id,
                        TelefoneRamal.status == 1
                    )
                ),

                # 👥 Número do ramal usado em número de grupo
                exists().where(
                    and_(
                        Numerogrupo.numero == Ramal.numero,
                        Numerogrupo.status == 1
                    )
                )
            )
        )
        .distinct()
        .count()
    )

    ramais_livres = total_ramais - ramais_em_uso

    mensagem_uso = (
        f"Existem {ramais_em_uso} ramais em uso."
        if ramais_em_uso > 0
        else "Nenhum ramal em uso."
    )

    mensagem_livre = (
        f"Existem {ramais_livres} ramais livres."
        if ramais_livres > 0
        else "Nenhum ramal livre."
    )

    total_grupos = db.session.query(Numerogrupo).filter(Numerogrupo.status == 1).count()
    # Nova contagem: Ramais em Grupos
    # Conta quantos ramais únicos estão em pelo menos um grupo ativo.
    ramais_em_grupo = (
        db.session.query(distinct(RamalNumeroGrupo.idramal))
        .join(Numerogrupo, Numerogrupo.id == RamalNumeroGrupo.idnumerogrupo)
        .filter(
            RamalNumeroGrupo.status == 1,
            Numerogrupo.status == 1
        )
        .count()
    )

    grupos_ativos = db.session.query(Numerogrupo).filter(Numerogrupo.status == 1).all()

    # 2. Prepara a estrutura de dados para o relatório
    dados_composicao_grupos = []
    for grupo in grupos_ativos:
        # Busca os ramais associados a este grupo, ordenados pela 'ordem'
        ramais_do_grupo = (
            db.session.query(RamalNumeroGrupo)
            .filter(
                RamalNumeroGrupo.idnumerogrupo == grupo.id,
                RamalNumeroGrupo.status == 1
            )
            .order_by(RamalNumeroGrupo.ordem)
            .all()
        )

        # Monta a lista de ramais para o dicionário
        lista_ramais = [
            {
                "numero_ramal": rng.ramal.numero,
                "ordem": rng.ordem
            }
            for rng in ramais_do_grupo
        ]

        # Adiciona o grupo e seus ramais à lista principal
        if lista_ramais:  # Apenas adiciona grupos que têm ramais
            dados_composicao_grupos.append({
                "numero_grupo": grupo.numero,
                "ramais": lista_ramais
            })

    grupos_de_captura_ativos = (
        db.session.query(Grupocaptura)
        .join(Ramal, Grupocaptura.id == Ramal.idgrupocaptura)
        .filter(Grupocaptura.status == 1)
        .distinct()
        .all()
    )

    # 2. Prepara a estrutura de dados para o relatório
    dados_composicao_captura = []
    for grupo_captura in grupos_de_captura_ativos:
        # Busca os ramais ativos associados a este grupo
        ramais_do_grupo = (
            db.session.query(Ramal)
            .filter(
                Ramal.idgrupocaptura == grupo_captura.id,
                Ramal.status == 1
            )
            .order_by(Ramal.numero)  # Ordena por número do ramal
            .all()
        )

        # Monta a lista de ramais para o dicionário
        lista_ramais = [
            {
                "numero_ramal": ramal.numero,
                "gravado": "Sim" if ramal.gravado == 1 else "Não"
            }
            for ramal in ramais_do_grupo
        ]

        # Adiciona o grupo e seus ramais à lista principal
        if lista_ramais:  # Apenas adiciona grupos que têm ramais ativos
            dados_composicao_captura.append({
                "nome_grupo": grupo_captura.nome,
                "ramais": lista_ramais
            })

    return {
        "pessoa": total_ativos,
        "telefone": total_telefone,

        # 🔥 novos dados
        "telefones_entregues": telefones_entregues,
        "telefones_nao_entregues": telefones_nao_entregues,
        "ramais_em_grupo": ramais_em_grupo,
        "ramal_pendente": ramal_pendente,
        "pessoa_pendente": pessoa_pendente,
        "grupo_pendente": grupo_pendente,
        "outras_pendencias": outras_pendencias,
        "ramais_em_uso": ramais_em_uso,
        "ramais_livres": ramais_livres,
        "total_grupos": total_grupos,
        "mensagem_uso": mensagem_uso,
        "mensagem_livre": mensagem_livre,
        "dados_composicao_grupos": dados_composicao_grupos,
        "dados_composicao_captura": dados_composicao_captura
    }

def grafico_telefones_secretaria_controller():
    resultado = (
        db.session.query(
            Secretaria.sigla.label("secretaria"),
            db.func.sum(
                db.case((Telefone.montado == 1, 1), else_=0)
            ).label("montados"),
            db.func.sum(
                db.case((Telefone.montado == 0, 1), else_=0)
            ).label("nao_montados")
        )
        .join(Departamento, Departamento.idsecretaria == Secretaria.id)
        .join(LugarTelefone, LugarTelefone.iddepartamento == Departamento.id)
        .join(Telefone, Telefone.idlugartelefone == LugarTelefone.id)
        .group_by(Secretaria.sigla)
        .all()
    )

    return jsonify([
        {
            "secretaria": row.secretaria,
            "montados": int(row.montados),
            "nao_montados": int(row.nao_montados)
        }
        for row in resultado
    ])

