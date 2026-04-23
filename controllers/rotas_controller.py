from flask import render_template, session, redirect, url_for, request
from functools import wraps
from flask import jsonify
from flask_login import login_required

def verificar_primeiro_acesso(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("user_primeiroacesso") == 1:
            return render_template("alterarsenha.html")
        return func(*args, **kwargs)
    return wrapper


@verificar_primeiro_acesso
def handle_home():
    return render_template("home.html")

@verificar_primeiro_acesso
def handle_usuario():
    return render_template("usuario.html")

@verificar_primeiro_acesso
def handle_departamento():
    return render_template("departamento.html")

@verificar_primeiro_acesso
def handle_modelos():
    return render_template("modelo.html")

def handle_alterarsenha():
    return render_template("alterarsenha.html")

@verificar_primeiro_acesso
def handle_telefone():
    return render_template("telefone.html")

@verificar_primeiro_acesso
def handle_ramal():
    return render_template("ramal.html")

@verificar_primeiro_acesso
def handle_empresa():
    return render_template("empresa.html")

@verificar_primeiro_acesso
def handle_pessoa():
    return render_template("pessoa.html")

@verificar_primeiro_acesso
def handle_tronco():
    return render_template("tronco.html")

@verificar_primeiro_acesso
def handle_numerogrupo():
    return render_template("numerogrupo.html")

@verificar_primeiro_acesso
def handle_pendencias():
    return render_template("pendencias.html")

@verificar_primeiro_acesso
def handle_grupocaptura():
    return render_template("grupocaptura.html")

@verificar_primeiro_acesso
def handle_lugartelefone():
    return render_template("lugartelefone.html")

@verificar_primeiro_acesso
def handle_logs():
    return render_template("logs.html")

@verificar_primeiro_acesso
def handle_operadora():
    return render_template("operadora.html")

@verificar_primeiro_acesso
def handle_lixeira():
    return render_template("lixeira.html")



