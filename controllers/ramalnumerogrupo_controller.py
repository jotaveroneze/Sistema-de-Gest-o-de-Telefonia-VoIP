from datetime import datetime

from flask_login import current_user

from controllers.pendencias_controller import snapshot_pendencia
from extensions import db
from models.pendencias_model import Pendencias
from models.ramalnumerogrupo_model import RamalNumeroGrupo
from models.numerogrupo_model import Numerogrupo
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from utils.logs import registrar_log

# =========================
# HELPERS
# =========================
def snapshot_ramal_numerogrupo(v):
    return {
        "id": v.id,
        "idramal": v.idramal,
        "idnumerogrupo": v.idnumerogrupo
    }


# =========================
# LISTAR POR GRUPO
# =========================
def listar_ramalnumerogrupo_por_grupo(id_numerogrupo):
    registros = RamalNumeroGrupo.query.filter_by(
        idnumerogrupo=id_numerogrupo,
        status = 1
    ).order_by(RamalNumeroGrupo.ordem).all()

    if not registros:
        return {
            "numerogrupo": "",
            "ramais": []
        }

    return {
        "numerogrupo": registros[0].numerogrupo.numero,
        "ramais": [
            {
                "id": r.id,              # id do vínculo
                "ramal": r.ramal.numero,
                "idramal": r.idramal,
                "ordem": r.ordem         # Inclui a ordem no retorno
            } for r in registros
        ]
    }

# =========================
# DESVINCULAR
# =========================
def desvincular_ramal_numerogrupo(id_ramal_numerogrupo):
    try:
        registro = RamalNumeroGrupo.query.get(id_ramal_numerogrupo)
        if not registro:
            return jsonify({"erro": "Vínculo não encontrado"}), 404

        antes = snapshot_ramal_numerogrupo(registro)

        # 1. CRIA PENDÊNCIA DE DESVINCULO (apenas se não existir uma ativa)

        ramal_desc = (
            registro.ramal.numero
            if hasattr(registro.ramal, "numero")
            else registro.idramal
        )

        grupo_desc = (
            registro.numerogrupo.numero
            if hasattr(registro.numerogrupo, "numero")
            else registro.idnumerogrupo
        )

        descricao = f"Desvincular o ramal ({ramal_desc}) do número virtual ({grupo_desc})"

        pendencia_existe = Pendencias.query.filter_by(
            tipopendencia='32',
            idramalnumerogrupo=id_ramal_numerogrupo,
            status=1
        ).first()

        if not pendencia_existe:
            pendencia = Pendencias(
                descricaotipopendencia=descricao,
                tipopendencia='32',
                idramalnumerogrupo=id_ramal_numerogrupo,
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
                mensagem="Pendência criada para desvincular ramal do número virtual"
            )

            db.session.add(pendencia)
            db.session.flush()

            registrar_log(
                entidade="pendencias",
                entidade_id=pendencia.id,
                antes="",
                depois=snapshot_pendencia(pendencia),
                retorno="SUCESSO",
                mensagem="Pendência criada para desvínculo de número virtual"
            )

        # 2. DESATIVA O REGISTRO (Muda status de 1 para 0)
        registro.status = 0
        db.session.commit()

        registrar_log(
            entidade="ramal_numerogrupo",
            entidade_id=id_ramal_numerogrupo,
            antes=antes,
            depois="",
            retorno="SUCESSO",
            mensagem="Ramal desvinculado do número virtual"
        )

        return {"success": True}
    except Exception as e:
        db.session.rollback()
        # ... log de erro ...
        raise e




# =========================
# ADICIONAR RAMAIS AO GRUPO
# =========================
def adicionar_ramais_ao_grupo(id_numerogrupo, ramais_input):
    # ramais_input pode ser uma lista de IDs (ex: [1, 2, 3])
    # ou uma lista de dicionários (ex: [{'id_ramal': 1, 'ordem': 1}, ...])
    try:
        processed_ramais = []
        if all(isinstance(item, int) for item in ramais_input):
            # Se for uma lista de IDs, atribui ordem sequencial
            for i, id_ramal in enumerate(ramais_input):
                processed_ramais.append({'id_ramal': id_ramal, 'ordem': i + 1})
        elif all(isinstance(item, dict) and 'id_ramal' in item and 'ordem' in item for item in ramais_input):
            # Se for uma lista de dicionários com ordem, usa-os diretamente
            processed_ramais = ramais_input
        else:
            raise TypeError("O parâmetro 'ramais_input' deve ser uma lista de IDs de ramais ou uma lista de dicionários com 'id_ramal' e 'ordem'.")

        for item_ramal in processed_ramais:
            id_ramal = item_ramal['id_ramal']
            ordem_ramal = item_ramal['ordem']

            vinculo = RamalNumeroGrupo.query.filter_by(
                idnumerogrupo=id_numerogrupo,
                idramal=id_ramal
            ).first()

            if vinculo:
                # Se o vínculo existe e está ativo com a mesma ordem, pula
                if vinculo.status == 1 and vinculo.ordem == ordem_ramal:
                    continue
                else:
                    # Se a ordem mudou ou o status está inativo, precisamos reordenar
                    # Primeiro, removemos o vínculo da ordem atual para evitar conflitos temporários
                    old_ordem = vinculo.ordem
                    vinculo.ordem = -1 # Valor temporário para evitar UniqueConstraint
                    db.session.flush()

                    # Desloca os ramais existentes para abrir espaço para a nova ordem
                    # Apenas se a nova ordem for menor ou igual à antiga, e se a nova ordem for diferente
                    if ordem_ramal != old_ordem or vinculo.status == 0:
                        db.session.query(RamalNumeroGrupo).filter(
                            RamalNumeroGrupo.idnumerogrupo == id_numerogrupo,
                            RamalNumeroGrupo.ordem >= ordem_ramal
                        ).update({
                            RamalNumeroGrupo.ordem: RamalNumeroGrupo.ordem + 1
                        }, synchronize_session=False)
                        db.session.flush()

                    antes_vinculo = snapshot_ramal_numerogrupo(vinculo)
                    vinculo.status = 1
                    vinculo.ordem = ordem_ramal # Atribui a nova ordem
                    mensagem_log = "Ramal reativado/ordem atualizada no número virtual"
            else:
                # SE NÃO EXISTE, CRIA UM NOVO
                # Desloca os ramais existentes para abrir espaço para a nova ordem
                db.session.query(RamalNumeroGrupo).filter(
                    RamalNumeroGrupo.idnumerogrupo == id_numerogrupo,
                    RamalNumeroGrupo.ordem >= ordem_ramal
                ).update({
                    RamalNumeroGrupo.ordem: RamalNumeroGrupo.ordem + 1
                }, synchronize_session=False)
                db.session.flush()

                antes_vinculo = ""
                vinculo = RamalNumeroGrupo(
                    idnumerogrupo=id_numerogrupo,
                    idramal=id_ramal,
                    status=1,
                    ordem=ordem_ramal # Atribui a ordem
                )
                db.session.add(vinculo)
                mensagem_log = "Ramal vinculado ao número virtual"

            db.session.flush()

            registrar_log(
                entidade="ramal_numerogrupo",
                entidade_id=vinculo.id,
                antes=antes_vinculo,
                depois=snapshot_ramal_numerogrupo(vinculo),
                retorno="SUCESSO",
                mensagem=mensagem_log
            )

            # Lógica de criação de pendência
            pendencia_existe = Pendencias.query.filter_by(
                tipopendencia='3',
                idramalnumerogrupo=vinculo.id,
                status=1
            ).first()

            ramal_desc = (
                vinculo.ramal.numero
                if hasattr(vinculo.ramal, "numero")
                else vinculo.idramal
            )

            grupo_desc = (
                vinculo.numerogrupo.numero
                if hasattr(vinculo.numerogrupo, "numero")
                else vinculo.idnumerogrupo
            )

            descricao = f"Vincular o ramal ({ramal_desc}) ao número virtual ({grupo_desc}) com ordem {ordem_ramal}"

            if not pendencia_existe:
                pendencia = Pendencias(
                    descricaotipopendencia=descricao,
                    tipopendencia='3',
                    idramalnumerogrupo=vinculo.id,
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
                    mensagem="Pendência criada para vínculo de número virtual"
                )

        db.session.commit()
        return {"success": True}
    except Exception as e:
        db.session.rollback()
        # ... log de erro ...
        raise e

# =========================
# LISTAR POR RAMAL
# =========================
def listar_ramalnumerogrupo_por_ramal(id_ramal):
    registros = RamalNumeroGrupo.query.filter_by(idramal=id_ramal, status=1).all()

    return {
        "ramal": registros[0].ramal.numero if registros else "",
        "grupos": [r.to_dict() for r in registros]
    }


# =========================
# LISTAR GRUPOS DISPONÍVEIS
# =========================
def listar_numerogrupo_disponiveis_por_ramal(id_ramal):
    from sqlalchemy.sql import exists

    grupos = (
        Numerogrupo.query
        .filter(
            Numerogrupo.status == 1,
            ~exists().where(
                (RamalNumeroGrupo.idnumerogrupo == Numerogrupo.id) &
                (RamalNumeroGrupo.idramal == id_ramal) &
                (RamalNumeroGrupo.status == 1)
            )
        )
        .all()
    )

    return [
        {
            "id": g.id,
            "numero": g.numero
        }
        for g in grupos
    ]



# =========================
# ADICIONAR GRUPOS AO RAMAL
# =========================
def adicionar_numerogrupos_ao_ramal(id_ramal, grupos_input):
    # grupos_input pode ser uma lista de IDs (ex: [1, 2, 3])
    # ou uma lista de dicionários (ex: [{'id_grupo': 1, 'ordem': 1}, ...])
    try:
        processed_grupos = []
        if all(isinstance(item, int) for item in grupos_input):
            # Se for uma lista de IDs, atribui ordem sequencial
            for i, id_grupo in enumerate(grupos_input):
                processed_grupos.append({'id_grupo': id_grupo, 'ordem': i + 1})
        elif all(isinstance(item, dict) and 'id_grupo' in item and 'ordem' in item for item in grupos_input):
            # Se for uma lista de dicionários com ordem, usa-os diretamente
            processed_grupos = grupos_input
        else:
            raise TypeError("O parâmetro 'grupos_input' deve ser uma lista de IDs de grupos ou uma lista de dicionários com 'id_grupo' e 'ordem'.")

        for item_grupo in processed_grupos:
            id_grupo = item_grupo['id_grupo']
            ordem_ramal = item_grupo['ordem'] # A ordem aqui se refere à ordem do ramal dentro do grupo

            vinculo = RamalNumeroGrupo.query.filter_by(
                idramal=id_ramal,
                idnumerogrupo=id_grupo
            ).first()

            if vinculo:
                # Se o vínculo existe e está ativo com a mesma ordem, pula
                if vinculo.status == 1 and vinculo.ordem == ordem_ramal:
                    continue
                else:
                    # Se a ordem mudou ou o status está inativo, precisamos reordenar
                    # Primeiro, removemos o vínculo da ordem atual para evitar conflitos temporários
                    old_ordem = vinculo.ordem
                    vinculo.ordem = -1 # Valor temporário para evitar UniqueConstraint
                    db.session.flush()

                    # Desloca os ramais existentes para abrir espaço para a nova ordem
                    # Apenas se a nova ordem for menor ou igual à antiga, e se a nova ordem for diferente
                    if ordem_ramal != old_ordem or vinculo.status == 0:
                        db.session.query(RamalNumeroGrupo).filter(
                            RamalNumeroGrupo.idnumerogrupo == id_grupo, # Atenção: aqui é id_grupo, não id_ramal
                            RamalNumeroGrupo.ordem >= ordem_ramal
                        ).update({
                            RamalNumeroGrupo.ordem: RamalNumeroGrupo.ordem + 1
                        }, synchronize_session=False)
                        db.session.flush()

                    antes_vinculo = snapshot_ramal_numerogrupo(vinculo)
                    vinculo.status = 1
                    vinculo.ordem = ordem_ramal # Atribui a nova ordem
                    mensagem_log = "Número virtual reativado/ordem atualizada no ramal"
            else:
                # SE NÃO EXISTE, CRIA UM NOVO
                # Desloca os ramais existentes para abrir espaço para a nova ordem
                db.session.query(RamalNumeroGrupo).filter(
                    RamalNumeroGrupo.idnumerogrupo == id_grupo, # Atenção: aqui é id_grupo, não id_ramal
                    RamalNumeroGrupo.ordem >= ordem_ramal
                ).update({
                    RamalNumeroGrupo.ordem: RamalNumeroGrupo.ordem + 1
                }, synchronize_session=False)
                db.session.flush()

                antes_vinculo = ""
                vinculo = RamalNumeroGrupo(
                    idramal=id_ramal,
                    idnumerogrupo=id_grupo,
                    status=1,
                    ordem=ordem_ramal # Atribui a ordem
                )
                db.session.add(vinculo)
                mensagem_log = "Número virtual vinculado ao ramal"

            db.session.flush()

            registrar_log(
                entidade="ramal_numerogrupo",
                entidade_id=vinculo.id,
                antes=antes_vinculo,
                depois=snapshot_ramal_numerogrupo(vinculo),
                retorno="SUCESSO",
                mensagem=mensagem_log
            )

            # Lógica de criação de pendência
            pendencia_existe = Pendencias.query.filter_by(
                tipopendencia='3',
                idramalnumerogrupo=vinculo.id,
                status=1
            ).first()

            ramal_desc = (
                vinculo.ramal.numero
                if hasattr(vinculo.ramal, "numero")
                else vinculo.idramal
            )

            grupo_desc = (
                vinculo.numerogrupo.numero
                if hasattr(vinculo.numerogrupo, "numero")
                else vinculo.idnumerogrupo
            )

            descricao = f"Vincular o número virtual ({grupo_desc}) ao ramal ({ramal_desc}) com ordem {ordem_ramal}"

            if not pendencia_existe:
                pendencia = Pendencias(
                    descricaotipopendencia=descricao,
                    tipopendencia='3',
                    idramalnumerogrupo=vinculo.id,
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
                    mensagem="Pendência criada para vínculo de número virtual ao ramal"
                )

        db.session.commit()
        return {"success": True}

    except Exception as e:
        db.session.rollback()
        # ... log de erro ...
        raise e

def alterar_ordem_ramal_no_grupo(id_vinculo, direcao):
    try:
        vinculo_atual = RamalNumeroGrupo.query.get(id_vinculo)
        if not vinculo_atual:
            return {"success": False, "erro": "Vínculo não encontrado."}

        id_numerogrupo = vinculo_atual.idnumerogrupo
        ordem_atual = vinculo_atual.ordem

        if direcao == 'subir':
            vinculo_adjacente = (
                RamalNumeroGrupo.query
                .filter(
                    RamalNumeroGrupo.idnumerogrupo == id_numerogrupo,
                    RamalNumeroGrupo.ordem < ordem_atual,
                    RamalNumeroGrupo.status == 1
                )
                .order_by(RamalNumeroGrupo.ordem.desc())
                .first()
            )
        elif direcao == 'descer':
            vinculo_adjacente = (
                RamalNumeroGrupo.query
                .filter(
                    RamalNumeroGrupo.idnumerogrupo == id_numerogrupo,
                    RamalNumeroGrupo.ordem > ordem_atual,
                    RamalNumeroGrupo.status == 1
                )
                .order_by(RamalNumeroGrupo.ordem.asc())
                .first()
            )
        else:
            return {"success": False, "erro": "Direção inválida."}

        if not vinculo_adjacente:
            return {"success": False, "erro": "Não é possível mover nesta direção."}

        ordem_adjacente = vinculo_adjacente.ordem

        # Snapshot antes
        antes_atual = snapshot_ramal_numerogrupo(vinculo_atual)
        antes_adjacente = snapshot_ramal_numerogrupo(vinculo_adjacente)

        # Troca de ordem (usa -1 temporário para evitar conflito)
        vinculo_atual.ordem = -1
        db.session.flush()

        vinculo_adjacente.ordem = ordem_atual
        vinculo_atual.ordem = ordem_adjacente
        db.session.flush()

        # Logs

        registrar_log(
            entidade="ramalnumerogrupo",
            entidade_id=vinculo_adjacente.id,
            antes=antes_adjacente,
            depois=snapshot_ramal_numerogrupo(vinculo_adjacente),
            retorno="SUCESSO",
            mensagem="Ordem do ramal alterada no número virtual"
        )

        # ===== Pendência =====
        # ===== Montar descrição com a ordem atual do grupo =====
        vinculos_ordenados = (
            RamalNumeroGrupo.query
            .filter(
                RamalNumeroGrupo.idnumerogrupo == id_numerogrupo,
                RamalNumeroGrupo.status == 1
            )
            .order_by(RamalNumeroGrupo.ordem.asc())
            .all()
        )

        numero_virtual = (
            vinculos_ordenados[0].numerogrupo.numero
            if vinculos_ordenados and hasattr(vinculos_ordenados[0].numerogrupo, "numero")
            else id_numerogrupo
        )

        linhas_ordem = []
        for v in vinculos_ordenados:
            ramal_desc = (
                v.ramal.numero
                if hasattr(v.ramal, "numero")
                else v.idramal
            )
            linhas_ordem.append(f"{v.ordem}º-Ramal {ramal_desc}")

        descricao = (
                f"Alterar a ordem do número virtual ({numero_virtual}) para:\n"
                + "\n".join(linhas_ordem)
        )

        # ===== Pendência por NÚMERO DE GRUPO =====
        pendencia_existe = (
            Pendencias.query
            .join(RamalNumeroGrupo, Pendencias.idramalnumerogrupo == RamalNumeroGrupo.id)
            .filter(
                Pendencias.tipopendencia == '3',
                Pendencias.status == 1,
                RamalNumeroGrupo.idnumerogrupo == id_numerogrupo
            )
            .first()
        )

        if pendencia_existe:
            antes_pendencia = snapshot_pendencia(pendencia_existe)

            pendencia_existe.descricaotipopendencia = descricao
            pendencia_existe.idusuarioresponsavel = current_user.id
            pendencia_existe.dataentrada = datetime.now()

            db.session.flush()

            registrar_log(
                entidade="pendencias",
                entidade_id=pendencia_existe.id,
                antes=antes_pendencia,
                depois=snapshot_pendencia(pendencia_existe),
                retorno="SUCESSO",
                mensagem="Pendência atualizada para alteração de ordem do número de grupo"
            )
        else:
            pendencia = Pendencias(
                descricaotipopendencia=descricao,
                tipopendencia=3,
                idramalnumerogrupo=id_vinculo,
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
                mensagem="Pendência criada para alteração de ordem do número de grupo"
            )

        db.session.commit()
        return {"success": True}

    except Exception as e:
        db.session.rollback()
        raise e
