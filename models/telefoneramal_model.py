from datetime import datetime

from extensions import db

class TelefoneRamal(db.Model):
    __tablename__ = 'telefoneramal'

    id = db.Column(db.Integer, primary_key=True)
    dataalteracao = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    status = db.Column(db.Integer, default=1)  # 1 = ativo, 0 = inativo

    idtelefone = db.Column(db.Integer, db.ForeignKey('telefone.id'), nullable=False)
    telefone = db.relationship("Telefone", backref="telefoneramal")

    idramal = db.Column(db.Integer, db.ForeignKey('ramal.id'), nullable=False)
    ramal = db.relationship("Ramal", backref="telefoneramal")

    def __repr__(self):
        return f'<Telefoneramal {self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "dataalteracao": self.dataalteracao,
            "idtelefone": self.idtelefone,
            "idramal": self.idramal,
        }
