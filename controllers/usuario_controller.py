from models.user_model import User
from extensions import db, bcrypt
from flask_bcrypt import Bcrypt
from flask import current_app, jsonify, request
from utils.logs import registrar_log


# =========================
# SNAPSHOT
# =========================
def snapshot_usuario(u):
    return {
        "id": u.id,
        "nome": u.nome,
        "email": u.email,
        "ramal": u.ramal,
        "adm": u.adm,
        "iddepartamento": u.iddepartamento,
        "status": u.status
    }


def get_bcrypt():
    return Bcrypt(current_app)


# =========================
# CRIAR USUÁRIO
# =========================
def criar_usuario_controller(data):
    try:
        nome = data.get("nome")
        email = data.get("email")
        ramal = data.get("ramal")
        adm = data.get("adm", False)
        iddepartamento = data.get("iddepartamento")

        bcrypt_app = Bcrypt(current_app)
        senha_hash = bcrypt_app.generate_password_hash("pmp@2026").decode("utf-8")

        novo = User(
            nome=nome,
            email=email,
            ramal=ramal,
            adm=adm,
            iddepartamento=iddepartamento,
            senha_hash=senha_hash
        )

        db.session.add(novo)
        db.session.flush()  # pega ID antes do commit

        registrar_log(
            entidade="usuario",
            entidade_id=novo.id,
            antes="",
            depois=snapshot_usuario(novo),
            retorno="SUCESSO",
            mensagem="Usuário criado"
        )

        db.session.commit()
        return jsonify({"mensagem": "Usuário criado com sucesso"}), 201

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="usuario",
            entidade_id=None,
            antes="",
            depois=data,
            retorno="ERRO",
            mensagem=str(e)
        )

        print("ERRO AO CRIAR:", e)
        return jsonify({"error": "Erro interno"}), 500


# =========================
# LISTAR USUÁRIOS
# =========================
def listar_usuarios_controller():
    usuarios = User.query.filter_by(status=1).all()

    lista = []
    for u in usuarios:
        lista.append({
            "id": u.id,
            "nome": u.nome,
            "email": u.email,
            "ramal": u.ramal,
            "adm": u.adm,
            "departamento": u.departamento.nome if u.departamento else ""
        })

    return jsonify(lista), 200


# =========================
# REMOVER (DESATIVAR)
# =========================
def remover_usuario_controller(user_id):
    try:
        usuario = User.query.get(user_id)
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        antes = snapshot_usuario(usuario)

        usuario.status = 0
        usuario.email = "[DELETADO " + str(usuario.id) + "] " + usuario.email
        db.session.commit()

        registrar_log(
            entidade="usuario",
            entidade_id=user_id,
            antes=antes,
            depois=snapshot_usuario(usuario),
            retorno="SUCESSO",
            mensagem="Usuário desativado"
        )

        return jsonify({"mensagem": "Usuário desativado com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="usuario",
            entidade_id=user_id,
            antes="",
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        print("ERRO AO DESATIVAR USUÁRIO:", e)
        return jsonify({"erro": "Erro interno"}), 500


# =========================
# RESETAR SENHA
# =========================
def resetar_senha_controller(user_id):
    try:
        usuario = User.query.get(user_id)
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        antes = snapshot_usuario(usuario)

        usuario.senha_hash = bcrypt.generate_password_hash("pmp@2026").decode("utf-8")
        usuario.primeiroacesso = 1
        db.session.commit()

        registrar_log(
            entidade="usuario",
            entidade_id=user_id,
            antes=antes,
            depois=snapshot_usuario(usuario),
            retorno="SUCESSO",
            mensagem="Senha resetada"
        )

        return jsonify({"mensagem": "Senha resetada com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="usuario",
            entidade_id=user_id,
            antes="",
            depois="",
            retorno="ERRO",
            mensagem=str(e)
        )

        print("ERRO AO RESETAR SENHA:", e)
        return jsonify({"erro": "Erro interno"}), 500


# =========================
# EDITAR USUÁRIO
# =========================
def editar_usuario_controller(id_usuario):
    try:
        usuario = User.query.get(id_usuario)
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        dados = request.get_json()
        antes = snapshot_usuario(usuario)

        usuario.nome = dados.get("nome", usuario.nome)
        usuario.email = dados.get("email", usuario.email)
        usuario.ramal = dados.get("ramal", usuario.ramal)
        usuario.adm = dados.get("adm", usuario.adm)

        dep_id = dados.get("departamento")
        if dep_id is not None:
            usuario.iddepartamento = int(dep_id)

        db.session.commit()

        registrar_log(
            entidade="usuario",
            entidade_id=id_usuario,
            antes=antes,
            depois=snapshot_usuario(usuario),
            retorno="SUCESSO",
            mensagem="Usuário editado"
        )

        return jsonify({"mensagem": "Usuário atualizado com sucesso"}), 200

    except Exception as e:
        db.session.rollback()

        registrar_log(
            entidade="usuario",
            entidade_id=id_usuario,
            antes="",
            depois=dados if 'dados' in locals() else "",
            retorno="ERRO",
            mensagem=str(e)
        )

        print("ERRO AO EDITAR:", e)
        return jsonify({"erro": "Erro interno"}), 500
