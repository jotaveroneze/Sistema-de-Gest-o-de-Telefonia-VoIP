from datetime import datetime
from extensions import db

class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    dataalteracao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario_email = db.Column(db.String(100), nullable=False)

    entidade_id = db.Column(db.Integer, nullable=False)

    antes = db.Column(db.Text, nullable=False)
    depois = db.Column(db.Text, nullable=False)


    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship("User", backref="logs")

    entidade = db.Column(db.Enum(
        'departamento',
        'empresa',
        'entregas',
        'logs',  # ✅ adicione
        'grupocaptura',
        'lugartelefone',
        'modelo',
        'numerodegrupo',
        'operadora',
        'pessoa',
        'pessoatelefone',
        'ramal',
        'ramalnumerogrupo',
        'pessoa_telefone',
        'secretaria',
        'telefone',
        'telefoneramal',
        'tronco',
        'usuario',
        'vinculo',
        'pendencias',
        name='entidade_enum'
    ), nullable=False)

    ip = db.Column(db.String(20), nullable=False)
    rota = db.Column(db.String(60), nullable=False)
    retorno = db.Column(db.String(50), nullable=False)
    mensagem = db.Column(db.String(100), nullable=False)
