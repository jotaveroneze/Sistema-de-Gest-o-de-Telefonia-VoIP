from extensions import db

class Ramal(db.Model):
    __tablename__ = 'ramal'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, default=1)  # 1 = ativo, 0 = inativo
    gravado = db.Column(db.Integer, default=0)  # 1 = sim, 0 = não

    idtronco = db.Column(db.Integer, db.ForeignKey('tronco.id'), nullable=False)
    tronco = db.relationship("Tronco", backref="ramal")

    idgrupocaptura = db.Column(db.Integer, db.ForeignKey('grupocaptura.id'), nullable=True)
    grupocaptura = db.relationship("Grupocaptura", backref="ramal")

    def __repr__(self):
        return f'<Ramal {self.numero}>'

    def to_dict(self):
        return {
            "id": self.id,
            "numero": self.numero,
            "grupo_captura": (
                self.grupocaptura.nome if self.grupocaptura else None
            ),
            "status": self.status,
            "gravado": self.gravado,
            "idtronco": self.idtronco,
        }
