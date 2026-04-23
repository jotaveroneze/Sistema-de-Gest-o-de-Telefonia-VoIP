from flask import request, session, jsonify, render_template, redirect, url_for
from models.user_model import User
from extensions import db, bcrypt

def alterar_senha_controller():
    if "user_id" not in session:
        return jsonify({"ok": False, "mensagem": "Usuário não autenticado"}), 401

    nova_senha = request.form.get("novasenha")
    confirmar_senha = request.form.get("confirmarsenha")

    if not nova_senha or not confirmar_senha:
        return jsonify({"ok": False, "mensagem": "Campos inválidos"}), 400

    if nova_senha != confirmar_senha:
        return jsonify({"ok": False, "mensagem": "Senhas não coincidem"}), 400

    user_id = session["user_id"]
    usuario = User.query.get(user_id)

    if not usuario:
        return jsonify({"ok": False, "mensagem": "Usuário não encontrado"}), 404

    # 🔥 Atualiza senha com bcrypt
    usuario.senha_hash = bcrypt.generate_password_hash(nova_senha).decode("utf-8")
    usuario.primeiroacesso = 0
    db.session.commit()
    db.session.refresh(usuario)

    # 🔥 Limpa a sessão (desloga o usuário)
    session.clear()

    # 🔥 Redireciona para a página de login
    return redirect(url_for("user.login"))
