from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from io import BytesIO
from datetime import datetime
import os


def obter_data_extenso():
    meses = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }
    agora = datetime.now()
    return f"{agora.day} de {meses[agora.month]} de {agora.year}"


def gerar_pdf_chamado_profissional(lista_pendencias):
    """
    Gera um PDF profissional com logo, tabela de pendências e avisos de sistema.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Estilos Personalizados
    estilo_texto = ParagraphStyle(
        'TextoSimples',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )

    estilo_aviso = ParagraphStyle(
        'AvisoRodape',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )

    elementos = []

    # 1. Cabeçalho com Logo
    caminho_logo = os.path.join(os.getcwd(), "static", "img", "img-logoPiracicaba.png")
    try:
        logo = Image(caminho_logo, width=150, height=50)
        logo.hAlign = 'CENTER'
        elementos.append(logo)
    except:
        elementos.append(Paragraph("<b>PREFEITURA DE PIRACICABA</b>", styles['Title']))

    elementos.append(Spacer(1, 20))

    # 2. Data e Texto de Abertura
    data_atual = obter_data_extenso()
    elementos.append(Paragraph(f"Piracicaba, {data_atual}", styles['Normal']))
    elementos.append(Spacer(1, 20))

    elementos.append(Paragraph("Prezado,", styles['Normal']))
    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph(
        "Solicito que sejam feitas as alterações abaixo conforme detalhado nas pendências registradas no sistema:",
        estilo_texto))
    elementos.append(Spacer(1, 15))

    # 3. Tabela de Pendências
    dados_tabela = [["Item", "Descrição da Pendência"]]

    for i, p in enumerate(lista_pendencias, 1):
        descricao = p.get('descricaotipopendencia', 'Sem descrição.')
        p_desc = Paragraph(descricao, estilo_texto)
        dados_tabela.append([str(i), p_desc])

    tabela = Table(dados_tabela, colWidths=[40, 450])

    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
    ]))

    elementos.append(tabela)
    elementos.append(Spacer(1, 30))

    # 4. Observação de Desconsideração
    observacao_texto = (
        "<b>Observação:</b> Favor desconsiderar os itens listados que já se encontram devidamente "
        "processados (vinculados ou desvinculados) no sistema de telefonia, uma vez que este "
        "relatório reflete as solicitações registradas até o momento de sua geração."
    )
    elementos.append(Paragraph(observacao_texto, estilo_texto))
    elementos.append(Spacer(1, 20))

    # 5. Rodapé Informativo (Aviso do Sistema)
    aviso_texto = (
        "Este arquivo foi gerado automaticamente pelo sistema de gerenciamento de telefone IP "
        "desenvolvido pelo Centro de Informática."
    )
    elementos.append(Paragraph(aviso_texto, estilo_aviso))

    doc.build(elementos)
    buffer.seek(0)
    return buffer
