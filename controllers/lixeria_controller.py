from flask import Blueprint
from extensions import db
from models.pendencias_model import Pendencias

def listar_lixeira():

    pendencias = (
        Pendencias.query
        .filter_by(status=0)  # 🔥 apenas excluídas
        .order_by(Pendencias.dataentrada.desc())
        .all()
    )

    lista = []

    for p in pendencias:
        lista.append({
            "id": p.id,
            "telefoneramal": p.telefoneramal.telefone.patrimonio if p.telefoneramal else None,
            "pessoatelefone": p.pessoatelefone.pessoa.nome if p.pessoatelefone else None,
            "ramalnumerogrupo": p.ramalnumerogrupo.ramal.numero if p.ramalnumerogrupo else None,
            "tipopendencia": p.tipopendencia,
            "descricaotipopendencia": p.descricaotipopendencia,
            "dataentrada": p.dataentrada,
            "datasaida": p.datasaida
        })

    return lista

def restaurar_pendencia_controller(id):
    pendencia = Pendencias.query.get(id)

    if not pendencia:
        return {"erro": "Registro não encontrado"}, 404

    pendencia.status = 1
    db.session.commit()

    return {"mensagem": "Restaurado com sucesso"}, 200

def excluir_definitivo_controller(id):
    pendencia = Pendencias.query.get(id)

    if not pendencia:
        return {"erro": "Registro não encontrado"}, 404

    pendencia.status = -1
    db.session.commit()

    return {"mensagem": "Excluído definitivamente"}, 200