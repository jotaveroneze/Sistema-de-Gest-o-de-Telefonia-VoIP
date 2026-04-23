from flask_login import UserMixin
from extensions import db, bcrypt
from flask_bcrypt import Bcrypt

class User(db.Model, UserMixin):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    adm = db.Column(db.Boolean, nullable=False, default=False)
    primeiroacesso = db.Column(db.Boolean, nullable=False, default=True)
    ramal = db.Column(db.String(7), nullable=False)
    senha_hash = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    status = db.Column(db.Integer, default=1)  # 1 = ativo, 0 = inativo

    # Coluna de chave estrangeira para Departamento
    iddepartamento = db.Column(db.Integer, db.ForeignKey('departamento.id'), nullable=False)
    departamento = db.relationship("Departamento", backref="usuarios")

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_id(user_id):
        return User.query.get(int(user_id))

    @staticmethod
    def authenticate(email, password):
        user = User.get_by_email(email)

        if not user:
            return None

        if user.status == 0:
            return None

        if not bcrypt.check_password_hash(user.senha_hash, password):
            return None

        # ✔ login permitido
        return user

    def set_password(self, password):
        self.senha_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.senha_hash, password)
