import os,sys

from routes.grupocaptura_route import grupocaptura_bp
from routes.importar_route import importar_bp

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, session, jsonify
from datetime import timedelta

from routes.home_route import home_bp
from routes.relatorio_route import relatorio_bp
from routes.user_route import user_bp
from routes.usuario_route import usuario_bp
from routes.rotas_route import rotas_bp
from extensions import db, bcrypt
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from models import *
from routes.departamento_route import departamento_bp
from routes.modelo_route import modelo_bp
from routes.alterarsenha_route import alterarsenha_bp
from routes.secretaria_route import secretaria_bp
from routes.telefone_route import telefone_bp
from routes.ramal_route import ramal_bp
from routes.empresa_route import empresa_bp
from routes.pessoa_route import pessoa_bp
from routes.vinculo_route import vinculo_bp
from routes.tronco_route import tronco_bp
from routes.operadora_route import operadora_bp
from routes.numerogrupo_route import numerogrupo_bp
from routes.ramalnumerogrupo_route import ramalnumerogrupo_bp
from routes.lugartelefone_route import lugartelefone_bp
from routes.telefoneramal_route import telefoneramal_bp
from routes.home_route import home_bp
from routes.backup_route import backup_bp
from routes.exportar_route import exportar_bp
from routes.pessoatelefone_route import pessoatelefone_bp
from routes.relatorio_route import relatorio_bp
from routes.entregas_route import entregas_bp
from routes.termo_route import termo_bp
from routes.importar_route import importar_bp
from routes.garantia_route import garantia_bp
from routes.pendencias_route import pendencias_bp
from routes.grupocaptura_route import grupocaptura_bp
from routes.logs_route import logs_bp
from routes.lixeira_route import lixeira_bp

#region APP
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
app = Flask(__name__)
app.secret_key = "********************"

app.config['SQLALCHEMY_DATABASE_URI'] = (
   'mysql+pymysql://telefonista:ligue-mecomapolicia@CI276399/controletelefonepmp'
)

#app.config['SQLALCHEMY_DATABASE_URI'] = (
#    'mysql+pymysql://appuser:gabrielcu@localhost/controletelefonepmp'
#)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=30)

#endregion

# Inicializa extensões
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "user.login"

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "unauthorized"}), 401

# Importa os modelos **depois** da inicialização do db
from models.user_model import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    return {
        "user_nome": session.get("user_nome"),
        "user_email": session.get("user_email"),
        "user_primeiroacesso": session.get("user_primeiroacesso")
    }

# Registra blueprints
app.register_blueprint(user_bp)
app.register_blueprint(rotas_bp)
app.register_blueprint(usuario_bp)
app.register_blueprint(departamento_bp)
app.register_blueprint(modelo_bp)
app.register_blueprint(alterarsenha_bp)
app.register_blueprint(secretaria_bp)
app.register_blueprint(telefone_bp)
app.register_blueprint(ramal_bp)
app.register_blueprint(empresa_bp)
app.register_blueprint(pessoa_bp)
app.register_blueprint(vinculo_bp)
app.register_blueprint(tronco_bp)
app.register_blueprint(operadora_bp)
app.register_blueprint(numerogrupo_bp)
app.register_blueprint(ramalnumerogrupo_bp)
app.register_blueprint(lugartelefone_bp)
app.register_blueprint(telefoneramal_bp)
app.register_blueprint(home_bp)
app.register_blueprint(backup_bp)
app.register_blueprint(exportar_bp)
app.register_blueprint(pessoatelefone_bp)
app.register_blueprint(relatorio_bp)
app.register_blueprint(entregas_bp)
app.register_blueprint(termo_bp)
app.register_blueprint(importar_bp)
app.register_blueprint(garantia_bp)
app.register_blueprint(pendencias_bp)
app.register_blueprint(grupocaptura_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(lixeira_bp)

if __name__ == "__main__":
    app.run(debug=True)

