from extensions import db
from datetime import datetime

class Entregas(db.Model):
    __tablename__ = 'entregas'

    id = db.Column(db.Integer, primary_key=True)
    dataentrega = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    iddepartamento = db.Column(db.Integer, db.ForeignKey('departamento.id'), nullable=False)
    idpessoa = db.Column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    idtelefone = db.Column(db.Integer, db.ForeignKey('telefone.id'), nullable=False)
    idlugartelefone = db.Column(db.Integer, db.ForeignKey('lugartelefone.id'), nullable=False)

    status = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "id": self.id,
            "dataentrega": self.dataentrega.strftime('%Y-%m-%d'),
            "iddepartamento": self.iddepartamento,
            "idpessoa": self.idpessoa,
            "idtelefone": self.idtelefone,
            "idlugartelefone": self.idlugartelefone,
            "status": self.status
        }
