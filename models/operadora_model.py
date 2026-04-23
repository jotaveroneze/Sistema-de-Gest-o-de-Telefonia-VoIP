
from extensions import db, bcrypt

class Operadora(db.Model):
    __tablename__ = 'operadora'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    contrato = db.Column(db.String(50), nullable=False)
    processo = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Integer, default=1)  # 1 = ativo, 0 = inativo

    def __repr__(self):
        return f'<Operadora {self.nome}>'

    # Converte o objeto em dicionário (necessário para jsonify)
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "contrato": self.contrato,
            "processo": self.processo,
            "status": self.status
        }
