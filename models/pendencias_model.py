from extensions import db

class Pendencias(db.Model):
    __tablename__ = 'pendencias'

    id = db.Column(db.Integer, primary_key=True)

    dataentrada = db.Column(db.DateTime, nullable=False)
    datasaida = db.Column(db.DateTime, nullable=True)

    from sqlalchemy import Enum

    tipopendencia = db.Column(
        Enum('1', '2', '3', '4', '5', '12', '22', '32', '42', '52', name='enum_tipopendencia'),
        default='1',
        nullable=False
    )

    descricaotipopendencia = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, default=1)  # 1 = ativo, 0 = inativo

    # ======================
    # FOREIGN KEYS
    # ======================

    idtelefoneramal = db.Column(db.Integer, db.ForeignKey('telefoneramal.id'), nullable=True)
    telefoneramal = db.relationship("TelefoneRamal", backref="pendencias")

    idpessoatelefone = db.Column(db.Integer, db.ForeignKey('pessoatelefone.id'), nullable=True)
    pessoatelefone = db.relationship("PessoaTelefone", backref="pendencias")

    idramalnumerogrupo = db.Column(db.Integer, db.ForeignKey('ramalnumerogrupo.id'), nullable=True)
    ramalnumerogrupo = db.relationship("RamalNumeroGrupo", backref="pendencias")

    idusuarioresolvido = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    usuarioresolvido = db.relationship(
        "User",
        foreign_keys=[idusuarioresolvido],
        backref="pendencias_resolvidas"
    )

    idusuarioresponsavel = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuarioresponsavel = db.relationship(
        "User",
        foreign_keys=[idusuarioresponsavel],
        backref="pendencias_responsavel"
    )

    def __repr__(self):
        return f'<Pendencia {self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "telefoneramal": self.telefoneramal.id if self.telefoneramal else None,
            "pessoatelefone": self.pessoatelefone.id if self.pessoatelefone else None,
            "ramalnumerogrupo": self.ramalnumerogrupo.id if self.ramalnumerogrupo else None,
            "usuarioresolvido": self.usuarioresolvido.id if self.usuarioresolvido else None,
            "usuarioresponsavel": self.usuarioresponsavel.id if self.usuarioresponsavel else None,
            "descricaotipopendencia": self.descricaotipopendencia,
            "tipopendencia": self.tipopendencia,
            "status": self.status,
            "dataentrada": self.dataentrada.isoformat() if self.dataentrada else None,
            "datasaida": self.datasaida.isoformat() if self.datasaida else None,
        }
