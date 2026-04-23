from flask import request, jsonify, make_response, session
from datetime import datetime
from sqlalchemy import and_, desc, or_
from models.pendencias_model import Pendencias
from extensions import db
from utils.logs import registrar_log
from utils.pendencia_pdf import gerar_pdf_chamado_profissional

# 🔍 MAPA DE TIPOS (do JS)
MAPA_TIPOS = {
    'ramal': [2, 22],
    'grupo': [3, 32],
    'pessoa': [4, 42],
    'telefone': [1],
    'grupocaptura': [5]
}


def snapshot_pendencia(dep):
    return {
        "id": dep.id,
        "telefoneramal": dep.telefoneramal.id if dep.telefoneramal else None,
        "pessoatelefone": dep.pessoatelefone.id if dep.pessoatelefone else None,
        "ramalnumerogrupo": dep.ramalnumerogrupo.id if dep.ramalnumerogrupo else None,
        "usuarioresolvido": dep.usuarioresolvido.id if dep.usuarioresolvido else None,
        "usuarioresponsavel": dep.usuarioresponsavel.id if dep.usuarioresponsavel else None,
        "descricaotipopendencia": dep.descricaotipopendencia,
        "tipopendencia": dep.tipopendencia,
        "status": dep.status,
        "dataentrada": dep.dataentrada.isoformat() if dep.dataentrada else None,
        "datasaida": dep.datasaida.isoformat() if dep.datasaida else None,
    }


# ✅ LISTAR PENDENTES (status=1 → pendente baseado no seu código)
def listar_pendencias():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    filtro_tipo = request.args.get('filtro_tipo', '')

    query = Pendencias.query.filter_by(status=1)

    if search:
        query = query.filter(Pendencias.descricaotipopendencia.ilike(f'%{search}%'))
    if filtro_tipo in MAPA_TIPOS:
        query = query.filter(Pendencias.tipopendencia.in_(MAPA_TIPOS[filtro_tipo]))

    paginacao = query.order_by(desc(Pendencias.dataentrada)).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return {
        "pendencias": [snapshot_pendencia(p) for p in paginacao.items],
        "page": paginacao.page,
        "pages": paginacao.pages,
        "total": paginacao.total,
        "has_prev": paginacao.has_prev,
        "has_next": paginacao.has_next
    }

# ✅ LISTAR FINALIZADAS
def listar_pendenciasfinalizadas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    filtro_tipo = request.args.get('filtro_tipo', '')

    query = Pendencias.query.filter_by(status=2)

    if search:
        query = query.filter(Pendencias.descricaotipopendencia.ilike(f'%{search}%'))
    if filtro_tipo in MAPA_TIPOS:
        query = query.filter(Pendencias.tipopendencia.in_(MAPA_TIPOS[filtro_tipo]))

    paginacao = query.order_by(desc(Pendencias.dataentrada)).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return {
        "pendencias": [snapshot_pendencia(p) for p in paginacao.items],
        "page": paginacao.page,
        "pages": paginacao.pages,
        "total": paginacao.total,
        "has_prev": paginacao.has_prev,
        "has_next": paginacao.has_next
    }

# Suas funções DELETE (OK, só fix status)
def remover_pendencia(id):
    dep = Pendencias.query.get_or_404(id)
    antes = snapshot_pendencia(dep)

    dep.status = 0  # Inativo
    db.session.commit()

    depois = snapshot_pendencia(dep)
    registrar_log(entidade='pendencias', entidade_id=id, antes=antes, depois=depois, retorno='SUCESSO',
                  mensagem='Removida')

    return jsonify({"mensagem": "Pendência removida"}), 200


def entregar_pendencia(id):
    dep = Pendencias.query.get_or_404(id)
    antes = snapshot_pendencia(dep)

    dep.status = 2  # Finalizada
    dep.datasaida = datetime.utcnow()
    dep.usuarioresolvido_id = session.get("user_id")  # Fix ID

    db.session.commit()
    depois = snapshot_pendencia(dep)
    registrar_log(entidade='pendencias', entidade_id=id, antes=antes, depois=depois, retorno='SUCESSO',
                  mensagem='Finalizada')

    return jsonify({"mensagem": "Finalizada"}), 200


def devolver_pendencia(id):
    dep = Pendencias.query.get_or_404(id)
    antes = snapshot_pendencia(dep)

    dep.status = 1  # Pendente novamente
    db.session.commit()

    depois = snapshot_pendencia(dep)
    registrar_log(entidade='pendencias', entidade_id=id, antes=antes, depois=depois, retorno='SUCESSO',
                  mensagem='Devolvida')

    return jsonify({"mensagem": "Devolvida"}), 200


def criar_pendencia(descricaotipopendencia, idusuarioresponsavel):
    try:
        pendencia = Pendencias(
            descricaotipopendencia=descricaotipopendencia,
            idusuarioresponsavel=idusuarioresponsavel,
            status=1,  # Pendente
            dataentrada=datetime.utcnow()
        )
        db.session.add(pendencia)
        db.session.commit()

        depois = snapshot_pendencia(pendencia)
        registrar_log(
            entidade='pendencias', entidade_id=pendencia.id,
            antes={}, depois=depois, retorno='SUCESSO',
            mensagem='Pendência criada'
        )

        return jsonify({"mensagem": "Criada", "id": pendencia.id}), 201

    except Exception as e:
        db.session.rollback()
        print("ERRO CRIAR:", e)
        return jsonify({"erro": str(e)}), 500



def finalizar_pendencias_ramais():
    try:
        # 1. Buscar pendências ativas do tipo ramal (2 ou 22)
        pendencias = (
            Pendencias.query
            .filter(
                Pendencias.status == 1,
                Pendencias.tipopendencia.in_([2, 22])
            )
            .order_by(Pendencias.dataentrada.asc())
            .all()
        )

        if not pendencias:
            return jsonify({
                "mensagem": "Nenhuma pendência de ramal encontrada"
            }), 200

        lista_dados = []

        # 2. Processar e finalizar cada pendência
        for p in pendencias:
            # Chama sua função de finalização
            entregar_pendencia(p.id)

            # Coleta os dados para o PDF
            lista_dados.append(snapshot_pendencia(p))

        # 3. Gerar o PDF unificado em memória (BytesIO)
        pdf_buffer = gerar_pdf_chamado_profissional(lista_dados)

        # 4. Configurar a resposta para abrir no navegador (inline)
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=solicitacao_alteracoes.pdf'

        return response

    except Exception as e:
        db.session.rollback()
        print("ERRO NO CONTROLLER FINALIZAR RAMAIS:", e)
        return jsonify({
            "erro": "Erro interno ao finalizar pendências e gerar PDF"
        }), 500


# Nota: Certifique-se de que a função entregar_pendencia está acessível
# ou importada corretamente neste escopo.


def finalizar_pendencias_numerovirtual():
    try:
        # 1. Buscar pendências ativas do tipo número virtual (3 ou 32)
        pendencias = (
            Pendencias.query
            .filter(
                Pendencias.status == 1,
                Pendencias.tipopendencia.in_([3, 32])
            )
            .order_by(Pendencias.dataentrada.asc())
            .all()
        )

        if not pendencias:
            return jsonify({
                "mensagem": "Nenhuma pendência de número virtual encontrada"
            }), 200

        lista_dados = []
        total = 0

        # 2. Processar e finalizar cada pendência
        for p in pendencias:
            # Chama sua função de finalização existente
            entregar_pendencia(p.id)

            # Coleta os dados para o PDF
            lista_dados.append(snapshot_pendencia(p))
            total += 1

        # 3. Gerar o PDF unificado com o layout profissional
        pdf_buffer = gerar_pdf_chamado_profissional(lista_dados)

        # 4. Retornar o PDF para abrir no navegador
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=chamado_pendencias_numerovirtual.pdf'

        return response

    except Exception as e:
        db.session.rollback()
        print("ERRO NO CONTROLLER FINALIZAR NUMERO VIRTUAL:", e)
        return jsonify({
            "erro": "Erro interno ao finalizar pendências e gerar PDF"
        }), 500


def finalizar_pendencias_pessoa():
    try:
        # 1. Buscar pendências ativas do tipo pessoa (4 ou 42)
        pendencias = (
            Pendencias.query
            .filter(
                Pendencias.status == 1,
                Pendencias.tipopendencia.in_([4, 42])
            )
            .order_by(Pendencias.dataentrada.asc())
            .all()
        )

        if not pendencias:
            return jsonify({
                "mensagem": "Nenhuma pendência de pessoa encontrada"
            }), 200

        lista_dados = []
        total = 0

        # 2. Processar e finalizar cada pendência
        for p in pendencias:
            # Chama sua função de finalização existente
            entregar_pendencia(p.id)

            # Coleta os dados para o PDF
            lista_dados.append(snapshot_pendencia(p))
            total += 1

        # 3. Gerar o PDF unificado com o layout profissional
        pdf_buffer = gerar_pdf_chamado_profissional(lista_dados)

        # 4. Retornar o PDF para abrir no navegador
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=chamado_pendencias_pessoa.pdf'

        return response

    except Exception as e:
        db.session.rollback()
        print("ERRO NO CONTROLLER FINALIZAR PESSOA:", e)
        return jsonify({
            "erro": "Erro interno ao finalizar pendências e gerar PDF"
        }), 500

def finalizar_pendencias_grupocaptura():
    try:
        # 1. Buscar pendências ativas do tipo Grupo de Captura
        pendencias = (
            Pendencias.query
            .filter(
                Pendencias.status == 1,
                Pendencias.tipopendencia.in_([5])  # ajuste se houver mais de um tipo
            )
            .order_by(Pendencias.dataentrada.asc())
            .all()
        )

        if not pendencias:
            return jsonify({
                "mensagem": "Nenhuma pendência de grupo de captura encontrada"
            }), 200

        lista_dados = []

        # 2. Processar e finalizar cada pendência
        for p in pendencias:
            # Finaliza a pendência (soft delete / conclusão)
            entregar_pendencia(p.id)

            # Coleta os dados para o PDF
            lista_dados.append(snapshot_pendencia(p))

        # 3. Gerar o PDF unificado em memória
        pdf_buffer = gerar_pdf_chamado_profissional(lista_dados)

        # 4. Retornar o PDF para abrir no navegador
        response = make_response(pdf_buffer.getvalue())
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = (
            "inline; filename=solicitacao_grupo_captura.pdf"
        )

        return response

    except Exception as e:
        db.session.rollback()
        print("ERRO NO CONTROLLER FINALIZAR GRUPO DE CAPTURA:", e)
        return jsonify({
            "erro": "Erro interno ao finalizar pendências de grupo de captura"
        }), 500


def finalizar_pendencias_todas():
    try:
        # 1. Buscar todas as pendências ativas
        pendencias = (
            Pendencias.query
            .filter(
                Pendencias.status == 1,
            )
            .order_by(Pendencias.dataentrada.asc())
            .all()
        )

        if not pendencias:
            return jsonify({
                "mensagem": "Nenhuma pendência encontrada"
            }), 200

        lista_dados = []
        total = 0

        # 2. Processar e finalizar cada pendência
        for p in pendencias:
            # Chama sua função de finalização existente
            entregar_pendencia(p.id)

            # Coleta os dados para o PDF
            lista_dados.append(snapshot_pendencia(p))
            total += 1

        # 3. Gerar o PDF unificado com o layout profissional
        pdf_buffer = gerar_pdf_chamado_profissional(lista_dados)

        # 4. Retornar o PDF para abrir no navegador
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=chamado_geral_pendencias.pdf'

        return response

    except Exception as e:
        db.session.rollback()
        print("ERRO NO CONTROLLER FINALIZAR TODAS:", e)
        return jsonify({
            "erro": "Erro interno ao finalizar pendências e gerar PDF"
        }), 500