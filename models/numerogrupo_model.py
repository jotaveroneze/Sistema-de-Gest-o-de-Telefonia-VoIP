
from extensions import db, bcrypt

class Numerogrupo(db.Model):
    __tablename__ = 'numerodegrupo'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.String(150), nullable=False)
    gravado = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)  # 1 = ativo, 0 = inativo

    iddepartamento = db.Column(db.Integer, db.ForeignKey('departamento.id'), nullable=False)
    departamento = db.relationship("Departamento", backref="numerogrupo")

    idtronco = db.Column(db.Integer, db.ForeignKey('tronco.id'), nullable=False)
    tronco = db.relationship("Tronco", backref="numerogrupo")

    def __repr__(self):
        return f'<Numerogrupo {self.numero} - {self.descricao}>'

    # Converte o objeto em dicionário (necessário para jsonify)
    # exemplo dentro do modelo Numerogrupo
    def to_dict(self):
        return {
            "id": self.id,
            "numero": self.numero,
            "descricao": self.descricao,
            "status": self.status,
            "gravado": self.gravado,
            "departamento_id": self.departamento.id if self.departamento else None,
            "tronco_id": self.tronco.id if self.tronco else None,
            "tronco_numero": self.tronco.numerochave if self.tronco else None
        }
