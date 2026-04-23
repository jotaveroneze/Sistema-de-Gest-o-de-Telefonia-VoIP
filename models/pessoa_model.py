from extensions import db, bcrypt

class Pessoa(db.Model):
    __tablename__ = 'pessoa'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    funcional = db.Column(db.Integer, nullable=True)
    cpf = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Integer, default=1)  # 1 = ativo, 0 = inativo

    idvinculo = db.Column(db.Integer, db.ForeignKey('vinculo.id'), nullable=False)
    vinculo = db.relationship("Vinculo", backref="pessoa")

    iddepartamento = db.Column(db.Integer, db.ForeignKey('departamento.id'), nullable=False)
    departamento = db.relationship("Departamento", backref="pessoa")

    idempresa = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship("Empresa", backref="pessoa")

    def __repr__(self):
        return f'<Modelo {self.nome}>'

    # Converte o objeto em dicionário (necessário para jsonify)
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "funcional": self.funcional,
            "cpf": self.cpf,
            "vinculo": self.vinculo.nome if self.vinculo else "",
            "idvinculo": self.idvinculo if self.idvinculo else "",
            "departamento": self.departamento.nome if self.departamento else "",
            "secretaria": self.departamento.secretaria.sigla if self.departamento and self.departamento.secretaria else "",
            "empresa": self.empresa.nome if self.empresa else ""
        }