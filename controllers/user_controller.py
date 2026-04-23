from flask import render_template, request, session, redirect, url_for, flash
from flask_login import login_user, logout_user
from models.user_model import User
from datetime import datetime, timedelta

MAX_ATTEMPTS = 3

def handle_login():
    attempts = session.get("attempts", 0)
    block_count = session.get("block_count", 0)
    block_until = session.get("block_until")

    # ---- VERIFICA BLOQUEIO ----
    if block_until:
        block_time = datetime.strptime(block_until, "%Y-%m-%d %H:%M:%S")

        if datetime.now() < block_time:
            flash(f"Tente novamente após {block_time.strftime('%H:%M:%S')}")
            return render_template("login.html")
        else:
            # desbloqueia
            session["attempts"] = 0
            session["block_until"] = None

    # ---- LOGIN ----
    if request.method == "POST":
        email = request.form["email"]
        senha_hash = request.form["senha"]

        user = User.authenticate(email, senha_hash)   # ⭐ agora usando hash corretamente

        if user:
            # login OK → reseta bloqueios
            session["attempts"] = 0
            session["block_count"] = 0
            session["block_until"] = None

            login_user(user)
            session.permanent = True

            session["user_id"] = user.id
            session["user_nome"] = user.nome
            session["user_email"] = user.email
            session["user_primeiroacesso"] = user.primeiroacesso
            session["user_adm"] = user.adm

            return redirect(url_for("rotas.home"))


        # ------- LOGIN INCORRETO -------
        session["attempts"] = attempts + 1

        if session["attempts"] >= MAX_ATTEMPTS:
            block_minutes = 2 ** block_count
            block_time = datetime.now() + timedelta(minutes=block_minutes)

            session["block_until"] = block_time.strftime("%Y-%m-%d %H:%M:%S")
            session["block_count"] = block_count + 1

            flash(
                f"Muitas tentativas. Bloqueado por {block_minutes} minutos. "
                f"Tente novamente às {block_time.strftime('%H:%M:%S')}"
            )

        flash("Usuário ou senha incorreto")
        return redirect(url_for("user.login"))

    return render_template("login.html")


def handle_logout():
    logout_user()
    session.clear()
    flash("Você foi deslogado.")
    return redirect(url_for("user.login"))

