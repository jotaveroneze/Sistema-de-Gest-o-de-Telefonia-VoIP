from extensions import db
from datetime import datetime

class PessoaTelefone(db.Model):
    __tablename__ = "pessoatelefone"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer, default=1)

    idpessoa = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    idtelefone = db.Column(db.Integer, db.ForeignKey('telefone.id'), nullable=False)

    dataalteracao = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    pessoa = db.relationship("Pessoa", backref="pessoatelefones")
    telefone = db.relationship("Telefone", backref="pessoatelefones")

    def __repr__(self):
        return f"<PessoaTelefone pessoa={self.idpessoa} telefone={self.idtelefone}>"
