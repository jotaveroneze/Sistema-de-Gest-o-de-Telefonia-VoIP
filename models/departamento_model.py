from extensions import db

class Departamento(db.Model):
    __tablename__ = 'departamento'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Integer, default=1)

    idsecretaria = db.Column(
        db.Integer,
        db.ForeignKey('secretaria.id'),
        nullable=False
    )

    secretaria = db.relationship(
        "Secretaria",
        backref="departamentos"
    )

    def __repr__(self):
        return f'<Departamento {self.nome}>'

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "status": self.status,
            "idsecretaria": self.idsecretaria,
            "secretaria": {
                "id": self.secretaria.id,
                "nome": self.secretaria.nome
            } if self.secretaria else None
        }

