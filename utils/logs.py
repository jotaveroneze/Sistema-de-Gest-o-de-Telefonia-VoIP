import json
from flask import request
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.logs_model import Log

def get_client_ip():
    # Caso esteja atrás de proxy (nginx, docker, etc.)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]

    return request.remote_addr

def safe_json(value):
    try:
        if value is None:
            return "{}"
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, default=str)
        return json.dumps(str(value), ensure_ascii=False)
    except Exception:
        return "{}"

def registrar_log(
    entidade,
    entidade_id,
    antes,
    depois,
    retorno,
    mensagem
):
    try:
        log = Log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            entidade=entidade,
            entidade_id=entidade_id or 0,
            antes=safe_json(antes),
            depois=safe_json(depois),
            ip=get_client_ip(),
            rota=request.path,
            retorno=retorno,
            mensagem=mensagem[:100]  # garante tamanho
        )

        db.session.add(log)
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        print("⚠️ ERRO AO SALVAR LOG:", e)

    except Exception as e:
        print("⚠️ ERRO INESPERADO NO LOG:", e)

