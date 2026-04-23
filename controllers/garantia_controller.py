from reportlab.lib import colors
from reportlab.platypus import PageBreak, Spacer, Paragraph

from extensions import db
from models.garantia_model import Garantia
from datetime import datetime
from flask import jsonify

import os
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors

from extensions import db
from models.telefone_model import Telefone
from models.pessoatelefone_model import PessoaTelefone
from models.telefoneramal_model import TelefoneRamal
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from datetime import datetime
from reportlab.platypus import Paragraph

caminho_imagem_header = os.path.join(
    os.getcwd(), "static", "img", "img-logoPiracicaba.png"
)

def listar_garantias():
    garantias = Garantia.query.filter_by(status=1).all()

    resultado = []
    for g in garantias:
        resultado.append({
            "id": g.id,
            "dataentrada": g.dataentrada.isoformat() if g.dataentrada else None,
            "datasaida": g.datasaida.isoformat() if g.datasaida else None,
            "defeito": g.defeito,
            "solucao": g.solucao,
            "status": g.status,
            "telefone": {
                "id": g.telefone.id,
                "patrimonio": g.telefone.patrimonio,
                "serial": g.telefone.serial
            }
        })

    return resultado  # ⬅️ SEM jsonify

def listar_garantias_por_telefone(idtelefone):
    garantias = Garantia.query.filter_by(idtelefone=idtelefone).all()

    return [{
        "id": g.id,
        "dataentrada": g.dataentrada.strftime("%Y-%m-%d"),
        "datasaida": g.datasaida.strftime("%Y-%m-%d") if g.datasaida else None,
        "defeito": g.defeito
    } for g in garantias]


def cadastrar_garantia(dados):
    nova_garantia = Garantia(
        defeito=dados.get("defeito"),
        idtelefone=dados.get("idtelefone")
    )

    db.session.add(nova_garantia)
    db.session.commit()


def finalizar_garantia(id):
    garantia = Garantia.query.get_or_404(id)
    garantia.datasaida = datetime.utcnow()
    db.session.commit()


def excluir_garantia(id):
    garantia = Garantia.query.get_or_404(id)
    garantia.status = 0
    db.session.commit()
    return {"success": True}


def devolver_garantia(id, solucao=""):
    """
    Marca a garantia como devolvida e salva a solução.
    """
    garantia = Garantia.query.get(id)
    if not garantia:
        return False

    garantia.datasaida = datetime.utcnow()
    garantia.solucao = solucao  # salva a solução informada
    db.session.commit()
    return True


def gerar_pdf_termo_garantia(lista_ips):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    titulo_style = ParagraphStyle(
        "titulo_style",
        parent=styles["Heading1"],
        alignment=1,
        fontSize=14,
        spaceAfter=25,
        fontName="Helvetica-Bold"
    )

    texto_style = ParagraphStyle(
        "texto_style",
        parent=normal,
        fontSize=11,
        leading=16,
        alignment=4,
        spaceAfter=15
    )

    assinatura_style = ParagraphStyle(
        "assinatura_style",
        parent=normal,
        fontSize=11,
        alignment=1,
        spaceBefore=40
    )

    story = []

    for id in lista_ips:

        telefone = Telefone.query.filter_by(id=id).first()
        if not telefone:
            continue

        pt = PessoaTelefone.query.filter_by(idtelefone=telefone.id).first()
        pessoa = pt.pessoa if pt else None

        ramal_obj = TelefoneRamal.query.filter_by(idtelefone=telefone.id).first()
        ramal = ramal_obj.ramal.numero if ramal_obj and ramal_obj.ramal else "-"

        lugar = "-"
        departamento = "-"
        secretaria = "-"

        if telefone.lugartelefone:
            lugar = telefone.lugartelefone.nomelugar
            if telefone.lugartelefone.departamento:
                departamento = telefone.lugartelefone.departamento.nome
                if telefone.lugartelefone.departamento.secretaria:
                    secretaria = telefone.lugartelefone.departamento.secretaria.sigla

        data_atual = datetime.today().strftime("%d/%m/%Y")

        # ==============================
        # LOGO
        # ==============================
        try:
            img = Image(caminho_imagem_header, width=8 * cm, height=2 * cm)
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 20))
        except:
            story.append(Spacer(1, 40))

        # ==============================
        # TÍTULO
        # ==============================
        story.append(Paragraph(
            "TERMO DE GARANTIA DE EQUIPAMENTO DE TELECOMUNICAÇÃO",
            titulo_style
        ))

        # ==============================
        # TEXTO INICIAL
        # ==============================
        texto_inicial = f"""
        Eu, <b>{pessoa.nome if pessoa else '-'}</b>, portador(a) da Matrícula Funcional
        <b>{pessoa.funcional if pessoa else '-'}</b>, lotado(a) no(a) <b>{departamento}</b>
        da <b>{secretaria}</b>, declaro estar ciente das condições de garantia do equipamento
        de telecomunicação fornecido pela Prefeitura Municipal de Piracicaba, conforme
        especificações abaixo.
        """
        story.append(Paragraph(texto_inicial, texto_style))

        # ==============================
        # TABELA DO EQUIPAMENTO
        # ==============================
        tabela_dados = [
            ["Item", "Especificação"],
            ["Descrição do Equipamento", "Aparelho Telefônico IP (Marca: Grandstream)"],
            ["Número de Série", telefone.serial or "-"],
            ["Endereço MAC", telefone.macaddress or "-"],
            ["Número de Patrimônio", telefone.patrimonio or "-"],
            ["Local de Instalação", lugar],
            ["Ramal Telefônico", ramal],
        ]

        tabela = Table(tabela_dados, colWidths=[6 * cm, 10 * cm])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))

        story.append(Paragraph("<b>Identificação do Equipamento</b>", texto_style))
        story.append(tabela)
        story.append(Spacer(1, 15))

        # ==============================
        # DECLARAÇÃO DE GARANTIA ATUALIZADA
        # ==============================
        declaracao = f"""
        Declaro que o equipamento listado acima será encaminhado ao Centro de Informática 
        para fins de garantia e manutenção. Durante o período em que estiver sob responsabilidade 
        do Centro de Informática, o equipamento não estará em minha posse.
        """
        story.append(Paragraph(declaracao, texto_style))

        story.append(Paragraph(f"Piracicaba, {data_atual}.", texto_style))

        # ==============================
        # ASSINATURA
        # ==============================
        story.append(Spacer(1, 30))
        story.append(Paragraph("_______________________________________________", assinatura_style))
        story.append(Paragraph(
            "<b>Nome:</b> _____________________ &nbsp;&nbsp; <b>Matrícula:</b> ________________",
            assinatura_style
        ))
        story.append(Paragraph("_______________________________________________", assinatura_style))
        story.append(Paragraph(
            "<b>Responsável pela garantia:</b> _____________________ &nbsp;&nbsp; <b>Matrícula:</b> ________________",
            assinatura_style
        ))
        story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer

def criar_garantia_telefone(idtelefone, defeito_desc="Garantia registrada via termo"):
    telefone = Telefone.query.get(idtelefone)

    if not telefone:
        return

    telefone.defeito = 1

    nova_garantia = Garantia(
        idtelefone=idtelefone,
        defeito=defeito_desc,
        status=1
    )

    db.session.add(nova_garantia)
