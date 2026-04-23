from sqlalchemy import UniqueConstraint

from extensions import db, bcrypt

class RamalNumeroGrupo(db.Model):
    __tablename__ = 'ramalnumerogrupo'

    id = db.Column(db.Integer, primary_key=True)

    idramal = db.Column(db.Integer, db.ForeignKey('ramal.id'), nullable=False)
    ramal = db.relationship("Ramal", backref="ramalnumerogrupo")
    status = db.Column(db.Integer, default=1)  # 1 = ativo, 0 = inativo

    idnumerogrupo = db.Column(db.Integer, db.ForeignKey('numerodegrupo.id'), nullable=False)
    numerogrupo = db.relationship("Numerogrupo", backref="ramalnumerogrupo")

    # Coluna para armazenar a ordem de prioridade dos ramais dentro de um grupo
    ordem = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint('idnumerogrupo', 'ordem', name='_numerogrupo_ordem_uc'),
    )

    def __repr__(self):
        return f'<RamalNumeroGrupo Ramal: {self.idramal}, Grupo: {self.idnumerogrupo}, Ordem: {self.ordem}>'

    def to_dict(self):
        # Coleta os dados dos ramais que pertencem ao mesmo grupo.
        # Para cada 'ramal_grupo' na lista de ramais do grupo,
        # um dicionário com o número do ramal e sua ordem é criado.
        ramais_do_grupo = [
            {
                "ramal": ramal_grupo.ramal.numero,
                "ordem": ramal_grupo.ordem
            }
            for ramal_grupo in self.numerogrupo.ramalnumerogrupo
        ]

        return {
            "id": self.id,
            "idramal": self.idramal,
            "ramal": self.ramal.numero,
            "idnumerogrupo": self.idnumerogrupo,
            "numerogrupo": self.numerogrupo.numero,
            "ordem": self.ordem,
            "ramais_do_grupo": ramais_do_grupo,  # Nova chave com a lista de ramais
        }
