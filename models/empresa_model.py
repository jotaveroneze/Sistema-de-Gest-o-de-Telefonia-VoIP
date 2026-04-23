from extensions import db, bcrypt

class Empresa(db.Model):
    __tablename__ = 'empresa'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    status = db.Column(db.Integer, default=1)  # 1 = ativo, 0 = inativo

    def __repr__(self):
        return f'<Modelo {self.nome}>'

    # Converte o objeto em dicionário (necessário para jsonify)
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome
        }