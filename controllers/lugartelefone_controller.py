from flask import request, jsonify
from extensions import db
from models.lugartelefone_model import LugarTelefone
from models.departamento_model import Departamento
from utils.logs import registrar_log

def snapshot_lugar(lugar):
    return {
        "id": lugar.id,
        "nomelugar": lugar.nomelugar,
        "endereco": lugar.endereco,
        "andar": lugar.andar,
        "iddepartamento": lugar.iddepartamento,
        "status": getattr(lugar, "status", None)
    }


# LISTAR LUGARES
def listar_lugares():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '').lower()
    andar = request.args.get('andar', '')

    query = LugarTelefone.query.filter_by(status=1)

    # 🔍 FILTRO TEXTO (busca em vários campos)
    if search:
        query = query.filter(
            db.or_(
                LugarTelefone.nomelugar.ilike(f'%{search}%'),
                LugarTelefone.endereco.ilike(f'%{search}%'),
                LugarTelefone.secretaria.ilike(f'%{search}%'),
                LugarTelefone.departamento.ilike(f'%{search}%')
            )
        )

    # 🏢 FILTRO ANDAR
    if andar:
        query = query.filter(LugarTelefone.andar == andar)

    paginacao = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "page": paginacao.page,
        "pages": paginacao.pages,  # ✅ JS espera "pages"
        "total": paginacao.total,
        "has_prev": paginacao.has_prev,  # ✅ JS espera isso
        "has_next": paginacao.has_next,  # ✅ JS espera isso
        "data": [l.to_dict() for l in paginacao.items]
    }), 200

# CRIAR LUGAR
def criar_lugar():
    data = request.get_json()

    try:
        nomelugar = data.get("nomelugar")
        endereco = data.get("endereco")
        andar = data.get("andar")
        iddepartamento = data.get("iddepartamento")

        if not nomelugar or not endereco or not iddepartamento:
            return jsonify({"error": "Campos obrigatórios faltando"}), 400

        departamento = Departamento.query.get(iddepartamento)
        if not departamento:
            return jsonify({"error": "Departamento não encontrado"}), 404

        lugar = LugarTelefone(
            nomelugar=nomelugar,
            endereco=endereco,
            andar=andar,
            iddepartamento=iddepartamento,
            status=1
        )

        db.session.add(lugar)
        db.session.flush()

        depois = snapshot_lugar(lugar)

        db.session.commit()

        registrar_log(
            entidade="lugar_telefone",
            entidade_id=lugar.id,
            antes="",
            depois=depois,
            retorno="SUCESSO",
            mensagem="Lugar de telefone criado"
        )

        return jsonify(lugar.to_dict()), 201

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="lugar_telefone",
            entidade_id=None,
            antes=data,
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        return jsonify({"error": "Erro ao criar lugar"}), 500

# EDITAR LUGAR
def editar_lugar(id):
    lugar = LugarTelefone.query.get(id)
    if not lugar:
        return jsonify({"error": "Lugar não encontrado"}), 404

    data = request.get_json()
    antes = snapshot_lugar(lugar)

    try:
        lugar.nomelugar = data.get("nomelugar", lugar.nomelugar)
        lugar.endereco = data.get("endereco", lugar.endereco)
        lugar.andar = data.get("andar", lugar.andar)
        lugar.iddepartamento = data.get("iddepartamento", lugar.iddepartamento)

        db.session.commit()

        depois = snapshot_lugar(lugar)

        registrar_log(
            entidade="lugar_telefone",
            entidade_id=lugar.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Lugar de telefone editado"
        )

        return jsonify(lugar.to_dict()), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="lugar_telefone",
            entidade_id=id,
            antes=antes,
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        return jsonify({"error": "Erro ao editar lugar"}), 500


# REMOVER LUGAR
def remover_lugar(id):
    lugar = LugarTelefone.query.get(id)
    if not lugar:
        return jsonify({"error": "Lugar não encontrado"}), 404

    antes = snapshot_lugar(lugar)

    try:
        lugar.status = 0
        lugar.nomelugar = f"[DELETADO {lugar.id}] {lugar.nomelugar}"

        db.session.commit()

        depois = snapshot_lugar(lugar)

        registrar_log(
            entidade="lugar_telefone",
            entidade_id=lugar.id,
            antes=antes,
            depois=depois,
            retorno="SUCESSO",
            mensagem="Lugar de telefone desativado"
        )

        return jsonify({"message": "Lugar removido com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="lugar_telefone",
            entidade_id=id,
            antes=antes,
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        return jsonify({"error": "Erro ao remover lugar"}), 500

def obter_lugar(id):
    lugar = LugarTelefone.query.get(id)
    if not lugar:
        return {"error": "Lugar não encontrado"}, 404
    return lugar.to_dict(), 200