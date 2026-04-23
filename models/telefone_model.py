from extensions import db

class Telefone(db.Model):
    __tablename__ = 'telefone'

    id = db.Column(db.Integer, primary_key=True)
    patrimonio = db.Column(db.Integer, nullable=False)
    processocompra = db.Column(db.String(70), nullable=False)
    notafiscal = db.Column(db.String(100), nullable=False)
    serial = db.Column(db.String(50), nullable=False)
    macaddress = db.Column(db.String(50), nullable=False)
    nometelefone = db.Column(db.String(50), nullable=False)

    status = db.Column(db.Integer, default=1)
    montado = db.Column(db.Integer, default=0)
    patrimoniado = db.Column(db.Integer, default=0)
    defeito = db.Column(db.Integer, default=0)

    idmodelo = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=False)
    modelo = db.relationship("Modelo", backref="telefone")


    # ✅ NOVO VÍNCULO COM LUGAR TELEFONE
    idlugartelefone = db.Column(
        db.Integer,
        db.ForeignKey('lugartelefone.id'),
        nullable=True
    )

    lugartelefone = db.relationship(
        "LugarTelefone",
        backref="telefone"
    )

    def __repr__(self):
        return f'<Telefone {self.nometelefone}>'

    def to_dict(self):
        return {
            "id": self.id,
            "nometelefone": self.nometelefone,
            "patrimonio": self.patrimonio,
            "serial": self.serial,
            "macaddress": self.macaddress,
            "status": self.status,
            "montado": self.montado,
            "patrimoniado": self.patrimoniado,
            "defeito": self.defeito,
            "processocompra": self.processocompra,
            "notafiscal": self.notafiscal,

            # MODELO
            "idmodelo": self.idmodelo,
            "modelo": self.modelo.nome if self.modelo else None,

            # LUGAR TELEFONE
            "idlugartelefone": self.idlugartelefone,
            "lugartelefone": self.lugartelefone.nomelugar if self.lugartelefone else None,
            "andar": self.lugartelefone.andar if self.lugartelefone else None,
            "endereco": self.lugartelefone.endereco if self.lugartelefone else None,

            # DEPARTAMENTO
            "iddepartamento": (
                self.lugartelefone.iddepartamento
                if self.lugartelefone else None
            ),
            "departamento": (
                self.lugartelefone.departamento.nome
                if self.lugartelefone and self.lugartelefone.departamento else None
            ),

            # SECRETARIA
            "idsecretaria": (
                self.lugartelefone.departamento.idsecretaria
                if self.lugartelefone and self.lugartelefone.departamento else None
            ),
            "secretaria": (
                self.lugartelefone.departamento.secretaria.sigla
                if (
                        self.lugartelefone
                        and self.lugartelefone.departamento
                        and self.lugartelefone.departamento.secretaria
                ) else None
            )
        }

