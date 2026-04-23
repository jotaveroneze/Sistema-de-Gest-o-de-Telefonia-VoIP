from flask import Blueprint, render_template, request, session,flash
from flask_login import login_required
from controllers.user_controller import (
    handle_login,
    handle_logout,
)

user_bp = Blueprint("user", __name__)

@user_bp.route("/", methods=["GET", "POST"])
def login_inicial():
    return handle_login()

@user_bp.route("/login", methods=["GET", "POST"])
def login():
    return handle_login()

@user_bp.route("/logout")
@login_required
def logout():
    return handle_logout()
