from extensions import db

class Tronco(db.Model):
    __tablename__ = 'tronco'

    id = db.Column(db.Integer, primary_key=True)
    numerochave = db.Column(db.String(50), nullable=False)
    ramalinicial = db.Column(db.String(50), nullable=False)
    ramalfinal = db.Column(db.String(50), nullable=False)

    idoperadora = db.Column(
        db.Integer,
        db.ForeignKey('operadora.id'),
        nullable=False
    )

    status = db.Column(db.Integer, default=1)  # 1 = ativo, 0 = inativo

    operadora = db.relationship('Operadora')

    def __repr__(self):
        return f'<Tronco {self.numerochave}>'

    def to_dict(self):
        return {
            "id": self.id,
            "numerochave": self.numerochave,
            "ramalinicial": self.ramalinicial,
            "ramalfinal": self.ramalfinal,
            "idoperadora": self.idoperadora,
            "operadora": self.operadora.nome if self.operadora else None,
            "status": self.status
        }
