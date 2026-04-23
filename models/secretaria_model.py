from extensions import db

class Secretaria(db.Model):
    __tablename__ = 'secretaria'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), nullable=False)
    status = db.Column(db.Integer, default=1)  # 1 = ativo, 0 = inativo

    def __repr__(self):
        return f'<Secretaria {self.nome}>'

    # Converte o objeto em dicionário (necessário para jsonify)
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "sigla": self.sigla
        }