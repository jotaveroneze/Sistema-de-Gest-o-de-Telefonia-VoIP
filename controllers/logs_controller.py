from flask import request
from sqlalchemy import desc, or_, func
from models.logs_model import Log


def listar_logs():  # ← SEM jsonify!
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 3, type=int)
    search = request.args.get('search', '').lower()
    data_filtro = request.args.get('data', '')

    print(f"🔍 DEBUG: page={page}, search='{search}'")  # ← Para testar

    query = Log.query.order_by(desc(Log.dataalteracao))

    if search:
        query = query.filter(
            or_(
                Log.entidade.ilike(f'%{search}%'),
                Log.mensagem.ilike(f'%{search}%'),
                Log.usuario_email.ilike(f'%{search}%'),
                Log.rota.ilike(f'%{search}%')
            )
        )

    if data_filtro:
        query = query.filter(func.date(Log.dataalteracao) == data_filtro)

    paginacao = query.paginate(page=page, per_page=per_page, error_out=False)

    print(f"🔍 RESULTADO: {paginacao.total} total, {len(paginacao.items)} itens")

    lista = []
    for log in paginacao.items:
        lista.append({
            "id": log.id,
            "data": log.dataalteracao.isoformat() if log.dataalteracao else None,
            "entidade": log.entidade or "",
            "antes": log.antes or "",
            "depois": log.depois or "",
            "usuario": getattr(log.usuario, 'nome', '') if log.usuario else "",
            "email": log.usuario_email or "",
            "ip": log.ip or "",
            "rota": log.rota or "",
            "retorno": log.retorno or "",
            "mensagem": log.mensagem or ""
        })

    # ✅ RETORNA DADOS PUROS (dict), SEM jsonify!
    return {
        "page": paginacao.page,
        "pages": paginacao.pages,
        "total": paginacao.total,
        "has_prev": paginacao.has_prev,
        "has_next": paginacao.has_next,
        "data": lista
    }
