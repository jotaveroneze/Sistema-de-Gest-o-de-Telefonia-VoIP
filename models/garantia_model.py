from extensions import db
from datetime import datetime

class Garantia(db.Model):
    __tablename__ = 'garantia'

    id = db.Column(db.Integer, primary_key=True)
    dataentrada = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    datasaida = db.Column(db.DateTime, nullable=True)
    defeito = db.Column(db.Text, nullable=True)
    solucao = db.Column(db.Text, nullable=True)
    status = db.Column(db.Integer, nullable=False, default=1)

    idtelefone = db.Column(db.Integer, db.ForeignKey('telefone.id'), nullable=False)
    telefone = db.relationship("Telefone", backref="garantia")
