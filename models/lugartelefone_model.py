from extensions import db

class LugarTelefone(db.Model):
    __tablename__ = 'lugartelefone'

    id = db.Column(db.Integer, primary_key=True)
    andar = db.Column(db.String(10), nullable=False)
    endereco = db.Column(db.String(100), nullable=False)
    nomelugar = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Integer, default=1)  # 1 = ativo, 0 = inativo

    iddepartamento = db.Column(db.Integer, db.ForeignKey('departamento.id'), nullable=False)
    departamento = db.relationship("Departamento", backref="lugartefone")

    def __repr__(self):
        return f'<LugarTelefone {self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "andar": self.andar,
            "endereco": self.endereco,
            "nomelugar": self.nomelugar,
            "iddepartamento": self.iddepartamento,
            "departamento": self.departamento.nome if self.departamento else None,
            "secretaria": self.departamento.secretaria.sigla if self.departamento else None,
        }
