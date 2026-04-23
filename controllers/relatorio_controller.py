from extensions import db
from flask import send_file
from models.secretaria_model import Secretaria
from models.departamento_model import Departamento
from models.lugartelefone_model import LugarTelefone
from models.telefone_model import Telefone
from controllers.home_controller import get_dashboard_dados
from utils.relatorios_dashboard_pdf import gerar_relatorio_dashboard


def gerar_relatorio_dashboard_pdf_controller():
    # Dados do dashboard
    dados_dashboard = get_dashboard_dados()

    # Dados do gráfico (sem jsonify)
    resultado = (
        db.session.query(
            Secretaria.sigla.label("secretaria"),
            db.func.sum(db.case((Telefone.montado == 1, 1), else_=0)).label("montados"),
            db.func.sum(db.case((Telefone.montado == 0, 1), else_=0)).label("nao_montados")
        )
        .join(Departamento, Departamento.idsecretaria == Secretaria.id)
        .join(LugarTelefone, LugarTelefone.iddepartamento == Departamento.id)
        .join(Telefone, Telefone.idlugartelefone == LugarTelefone.id)
        .group_by(Secretaria.sigla)
        .all()
    )

    dados_grafico = [
        {
            "secretaria": row.secretaria,
            "montados": int(row.montados),
            "nao_montados": int(row.nao_montados)
        }
        for row in resultado
    ]

    pdf = gerar_relatorio_dashboard(dados_dashboard, dados_grafico)

    return send_file(
        pdf,
        as_attachment=True,
        download_name="relatorio_dashboard.pdf",
        mimetype="application/pdf"
    )
