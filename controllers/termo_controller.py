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

def gerar_pdf_termo_telefone(lista_ips):
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

        # ==============================
        # BUSCA TELEFONE PELO IP
        # ==============================
        telefone = Telefone.query.filter_by(id=id).first()
        if not telefone:
            continue

        # Pessoa vinculada
        pt = PessoaTelefone.query.filter_by(idtelefone=telefone.id).first()
        pessoa = pt.pessoa if pt else None

        # Ramal
        ramal_obj = TelefoneRamal.query.filter_by(idtelefone=telefone.id).first()
        ramal = ramal_obj.ramal.numero if ramal_obj and ramal_obj.ramal else "-"

        # Localização
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
            "TERMO DE RECEBIMENTO DE EQUIPAMENTO DE TELECOMUNICAÇÃO",
            titulo_style
        ))

        # ==============================
        # TEXTO INICIAL
        # ==============================
        texto_inicial = f"""
        Eu, <b>{pessoa.nome if pessoa else '-'}</b>, portador(a) da Matrícula Funcional
        <b>{pessoa.funcional if pessoa else '-'}</b>, lotado(a) no(a) <b>{departamento}</b>
        da <b>{secretaria}</b>, declaro, para os devidos fins, ter recebido da Prefeitura
        Municipal de Piracicaba o equipamento de telecomunicação abaixo especificado,
        destinado exclusivamente ao uso institucional.
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

        story.append(Paragraph("<b>Detalhamento do Equipamento</b>", texto_style))
        story.append(tabela)
        story.append(Spacer(1, 15))

        # ==============================
        # DECLARAÇÃO
        # ==============================
        declaracao = """
        Declaro que recebi o equipamento em perfeitas condições de funcionamento,
        acompanhado de <i>patch cord</i> (cabo de rede), sem fonte de alimentação,
        comprometendo-me a utilizá-lo exclusivamente para fins profissionais e a
        zelar por sua correta conservação.
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

        story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer
