"""
Módulo de Geração de Relatórios Profissionais de Dashboard Telefônico

Este módulo fornece funcionalidades avançadas para gerar relatórios em PDF
com visualizações de dados, análises estatísticas e formatação profissional.

Autor: Sistema de Relatórios
Data: Janeiro 2026
"""

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from io import BytesIO
from datetime import datetime
import os
from reportlab.platypus import Image
from reportlab.lib.units import cm

CAMINHO_LOGO = os.path.join(
    os.getcwd(), "static", "img", "img-logoPiracicaba.png"
)

def criar_estilos_personalizados():
    """
    Cria e retorna estilos personalizados para o documento.

    Returns:
        dict: Dicionário contendo os estilos personalizados
    """
    styles = getSampleStyleSheet()

    # Estilo para título principal
    styles.add(ParagraphStyle(
        name='TituloPrincipal',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    # Estilo para subtítulos
    styles.add(ParagraphStyle(
        name='Subtitulo',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5282'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.HexColor('#2c5282'),
        borderPadding=5,
        backColor=colors.HexColor('#e6f2ff')
    ))

    # Estilo para texto justificado
    styles.add(ParagraphStyle(
        name='Justificado',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=16
    ))

    # Estilo para destaques
    styles.add(ParagraphStyle(
        name='Destaque',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2d3748'),
        leftIndent=20,
        rightIndent=20,
        spaceAfter=12,
        spaceBefore=12,
        borderWidth=1,
        borderColor=colors.HexColor('#cbd5e0'),
        borderPadding=10,
        backColor=colors.HexColor('#f7fafc')
    ))

    return styles


def calcular_metricas_avancadas(dados_dashboard, dados_grafico):
    """
    Calcula métricas e indicadores avançados para análise.

    Args:
        dados_dashboard (dict): Dados gerais do dashboard
        dados_grafico (list): Dados detalhados por secretaria

    Returns:
        dict: Dicionário com métricas calculadas
    """
    total_montados = sum(item["montados"] for item in dados_grafico)
    total_nao_montados = sum(item["nao_montados"] for item in dados_grafico)
    total_telefones = total_montados + total_nao_montados

    # Taxa de entrega
    taxa_entrega = (total_montados / total_telefones * 100) if total_telefones > 0 else 0




    # Taxa de utilização de ramais
    total_ramais = dados_dashboard["ramais_em_uso"] + dados_dashboard["ramais_livres"]
    taxa_utilizacao_ramais = (dados_dashboard["ramais_em_uso"] / total_ramais * 100) if total_ramais > 0 else 0

    # Novo cálculo: Taxa de ramais em grupos
    ramais_em_grupo = dados_dashboard.get("ramais_em_grupo", 0)
    taxa_ramais_em_grupo = (ramais_em_grupo / total_ramais * 100) if total_ramais > 0 else 0

    # Média de telefones por pessoa
    media_telefones_pessoa = dados_dashboard["telefone"] / dados_dashboard["pessoa"] if dados_dashboard[
                                                                                            "pessoa"] > 0 else 0

    # Secretaria com melhor desempenho
    melhor_secretaria = max(dados_grafico, key=lambda x: x["montados"] / (x["montados"] + x["nao_montados"]) if (x[
                                                                                                                     "montados"] +
                                                                                                                 x[
                                                                                                                     "nao_montados"]) > 0 else 0)

    # Secretaria que precisa de atenção
    pior_secretaria = min(dados_grafico, key=lambda x: x["montados"] / (x["montados"] + x["nao_montados"]) if (x[
                                                                                                                   "montados"] +
                                                                                                               x[
                                                                                                                   "nao_montados"]) > 0 else 1)

    return {
        "total_montados": total_montados,
        "total_nao_montados": total_nao_montados,
        "total_telefones": total_telefones,
        "taxa_entrega": taxa_entrega,
        "taxa_utilizacao_ramais": taxa_utilizacao_ramais,
        "taxa_ramais_em_grupo": taxa_ramais_em_grupo,
        "media_telefones_pessoa": media_telefones_pessoa,
        "melhor_secretaria": melhor_secretaria,
        "pior_secretaria": pior_secretaria
    }


def criar_cabecalho(elementos, styles):
    """
    Cria o cabeçalho do relatório com logo, título e data de geração.
    """

    # =========================
    # LOGO
    # =========================
    try:
        logo = Image(CAMINHO_LOGO, width=6 * cm, height=2 * cm)
        logo.hAlign = "CENTER"
        elementos.append(logo)
        elementos.append(Spacer(1, 15))
    except Exception as e:
        print("Erro ao carregar logo:", e)

    # =========================
    # TÍTULO PRINCIPAL
    # =========================
    elementos.append(Paragraph(
        "Relatório Executivo do Sistema Telefônico Institucional",
        styles["TituloPrincipal"]
    ))

    # =========================
    # DATA DE GERAÇÃO
    # =========================
    data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")

    estilo_data = ParagraphStyle(
        "DataRelatorio",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=30
    )

    elementos.append(Paragraph(
        f"<i>Relatório gerado em: {data_atual}</i>",
        estilo_data
    ))

def criar_sumario_executivo(elementos, styles, dados_dashboard, metricas):
    """
    Cria a seção de sumário executivo com análise geral.

    Args:
        elementos (list): Lista de elementos do documento
        styles (dict): Estilos do documento
        dados_dashboard (dict): Dados do dashboard
        metricas (dict): Métricas calculadas
    """
    elementos.append(Paragraph("Sumário Executivo", styles["Subtitulo"]))

    texto_sumario = f"""
    Este relatório apresenta uma análise abrangente do sistema telefônico institucional, 
    contemplando a distribuição de ramais, telefones ativos e o status de implementação 
    por secretaria. Os dados revelam que a instituição possui atualmente 
    <b>{dados_dashboard["pessoa"]} colaboradores ativos</b> utilizando 
    <b>{dados_dashboard["telefone"]} telefones</b>, com uma taxa de entrega de equipamentos 
    de <b>{metricas["taxa_entrega"]:.1f}%</b>. A infraestrutura de ramais apresenta 
    <b>{metricas["taxa_utilizacao_ramais"]:.1f}%</b> de ocupação, indicando 
    {'um aproveitamento adequado dos recursos disponíveis' if metricas["taxa_utilizacao_ramais"] > 70 else 'potencial para expansão ou otimização'}.
    """

    elementos.append(Paragraph(texto_sumario, styles["Justificado"]))
    elementos.append(Spacer(1, 20))


def criar_tabela_resumo(elementos, styles, dados_dashboard):
    """
    Cria tabela com resumo geral dos indicadores.

    Args:
        elementos (list): Lista de elementos do documento
        styles (dict): Estilos do documento
        dados_dashboard (dict): Dados do dashboard
    """
    elementos.append(Paragraph("Indicadores Gerais", styles["Subtitulo"]))
    elementos.append(Spacer(1, 10))

    resumo = [
        ["Indicador", "Quantidade", "Unidade"],
        ["Total de Pessoas Ativas", str(dados_dashboard["pessoa"]), "colaboradores"],
        ["Total de Telefones Ativos", str(dados_dashboard["telefone"]), "aparelhos"],
        ["Ramais em Uso", str(dados_dashboard["ramais_em_uso"]), "ramais"],
        ["Ramais Livres", str(dados_dashboard["ramais_livres"]), "ramais"],
        ["Total de Ramais", str(dados_dashboard["ramais_em_uso"] + dados_dashboard["ramais_livres"]), "ramais"],
    ]

    tabela_resumo = Table(resumo, colWidths=[9 * cm, 4 * cm, 4 * cm])
    tabela_resumo.setStyle(TableStyle([
        # Cabeçalho
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),

        # Corpo da tabela
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
    ]))

    elementos.append(tabela_resumo)
    elementos.append(Spacer(1, 25))


def criar_grafico_barras(elementos, styles, dados_grafico):
    """
    Cria gráfico de barras comparativo por secretaria.

    Args:
        elementos (list): Lista de elementos do documento
        styles (dict): Estilos do documento
        dados_grafico (list): Dados por secretaria
    """
    elementos.append(Paragraph(
        "Análise Comparativa: Telefones Entregues vs. Pendentes por Secretaria",
        styles["Subtitulo"]
    ))
    elementos.append(Spacer(1, 15))

    secretarias = [item["secretaria"][:20] for item in dados_grafico]  # Limita nome
    montados = [item["montados"] for item in dados_grafico]
    nao_montados = [item["nao_montados"] for item in dados_grafico]

    drawing_bar = Drawing(500, 280)

    grafico_barra = VerticalBarChart()
    grafico_barra.x = 60
    grafico_barra.y = 60
    grafico_barra.width = 400
    grafico_barra.height = 180
    grafico_barra.data = [montados, nao_montados]
    grafico_barra.categoryAxis.categoryNames = secretarias

    # Configurações de eixos
    grafico_barra.valueAxis.valueMin = 0
    max_valor = max(montados + nao_montados) if (montados + nao_montados) else 10
    grafico_barra.valueAxis.valueMax = max_valor + (max_valor * 0.1)
    grafico_barra.valueAxis.valueStep = max(1, max_valor // 10)

    # Estilização das barras
    grafico_barra.bars[0].fillColor = colors.HexColor('#48bb78')  # Verde
    grafico_barra.bars[1].fillColor = colors.HexColor('#f56565')  # Vermelho

    # Configurações de fonte
    grafico_barra.categoryAxis.labels.fontSize = 8
    grafico_barra.categoryAxis.labels.angle = 45
    grafico_barra.valueAxis.labels.fontSize = 9

    # Adicionar legenda
    legenda = Legend()
    legenda.x = 60
    legenda.y = 20
    legenda.dx = 8
    legenda.dy = 8
    legenda.fontName = 'Helvetica'
    legenda.fontSize = 9
    legenda.columnMaximum = 2
    legenda.alignment = 'right'
    legenda.colorNamePairs = [
        (colors.HexColor('#48bb78'), 'Telefones Entregues'),
        (colors.HexColor('#f56565'), 'Telefones Pendentes')
    ]

    drawing_bar.add(grafico_barra)
    drawing_bar.add(legenda)

    elementos.append(drawing_bar)
    elementos.append(Spacer(1, 20))

    # Texto explicativo
    texto_barra = """
    O gráfico de barras apresentado demonstra a distribuição de telefones entregues 
    (em verde) e pendentes de entrega (em vermelho) em cada secretaria da instituição. 
    Esta visualização permite identificar rapidamente os setores que apresentam maior 
    déficit na infraestrutura telefônica, possibilitando a priorização de ações corretivas 
    e alocação eficiente de recursos para completar a implementação do sistema.
    """
    elementos.append(Paragraph(texto_barra, styles["Justificado"]))
    elementos.append(Spacer(1, 25))


def criar_grafico_pizza(elementos, styles, metricas):
    """
    Cria gráfico de pizza com distribuição geral.

    Args:
        elementos (list): Lista de elementos do documento
        styles (dict): Estilos do documento
        metricas (dict): Métricas calculadas
    """
    elementos.append(Paragraph(
        "Distribuição Geral do Status de Implementação",
        styles["Subtitulo"]
    ))
    elementos.append(Spacer(1, 15))

    drawing_pie = Drawing(500, 250)

    pizza = Pie()
    pizza.x = 150
    pizza.y = 30
    pizza.width = 180
    pizza.height = 180
    pizza.data = [metricas["total_montados"], metricas["total_nao_montados"]]
    pizza.labels = [
        f'Entregues\n{metricas["taxa_entrega"]:.1f}%',
        f'Pendentes\n{100 - metricas["taxa_entrega"]:.1f}%'
    ]

    # Cores
    pizza.slices[0].fillColor = colors.HexColor('#48bb78')
    pizza.slices[1].fillColor = colors.HexColor('#f56565')

    # Configurações de labels
    pizza.slices[0].fontName = 'Helvetica-Bold'
    pizza.slices[1].fontName = 'Helvetica-Bold'
    pizza.slices[0].fontSize = 11
    pizza.slices[1].fontSize = 11

    drawing_pie.add(pizza)

    elementos.append(drawing_pie)
    elementos.append(Spacer(1, 20))

    # Análise interpretativa
    texto_pizza = f"""
    A representação gráfica em formato de pizza ilustra a proporção global de telefones 
    entregues versus pendentes em toda a instituição. Com uma taxa de implementação de 
    <b>{metricas["taxa_entrega"]:.1f}%</b>, observa-se que 
    {'a maior parte dos equipamentos já foi distribuída, indicando um estágio avançado do projeto' if metricas["taxa_entrega"] > 70 else 'ainda há um volume significativo de equipamentos a serem entregues, demandando atenção da gestão'}. 
    Este indicador é fundamental para o acompanhamento do cronograma de implementação 
    e para a avaliação da efetividade das ações de distribuição.
    """
    elementos.append(Paragraph(texto_pizza, styles["Justificado"]))
    elementos.append(Spacer(1, 25))


def criar_tabela_detalhada(elementos, styles, dados_grafico):
    """
    Cria tabela detalhada com análise por secretaria.

    Args:
        elementos (list): Lista de elementos do documento
        styles (dict): Estilos do documento
        dados_grafico (list): Dados por secretaria
    """
    elementos.append(Paragraph(
        "Detalhamento Analítico por Secretaria",
        styles["Subtitulo"]
    ))
    elementos.append(Spacer(1, 10))

    tabela_secretaria = [["Secretaria", "Entregues", "Pendentes", "Total", "Taxa (%)"]]

    for item in dados_grafico:
        total = item["montados"] + item["nao_montados"]
        taxa = (item["montados"] / total * 100) if total > 0 else 0
        tabela_secretaria.append([
            item["secretaria"],
            str(item["montados"]),
            str(item["nao_montados"]),
            str(total),
            f"{taxa:.1f}%"
        ])

    # Adicionar linha de totais
    total_montados = sum(item["montados"] for item in dados_grafico)
    total_nao_montados = sum(item["nao_montados"] for item in dados_grafico)
    total_geral = total_montados + total_nao_montados
    taxa_geral = (total_montados / total_geral * 100) if total_geral > 0 else 0

    tabela_secretaria.append([
        "TOTAL GERAL",
        str(total_montados),
        str(total_nao_montados),
        str(total_geral),
        f"{taxa_geral:.1f}%"
    ])

    tabela = Table(tabela_secretaria, colWidths=[7 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm])
    tabela.setStyle(TableStyle([
        # Cabeçalho
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),

        # Corpo
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
        ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -2), 9),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor('#f7fafc')]),

        # Linha de totais
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor('#e6f2ff')),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 10),

        # Padding
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
    ]))

    elementos.append(tabela)
    elementos.append(Spacer(1, 25))


def criar_analise_metricas(elementos, styles, metricas):
    """
    Cria seção com análise de métricas avançadas.
    ...
    """
    elementos.append(Paragraph("Análise de Indicadores de Desempenho", styles["Subtitulo"]))

    # Adicionado o KPI "Taxa de Ramais em Grupos"
    kpis = [
        ["Indicador", "Valor", "Interpretação"],
        [
            "Taxa de Entrega de Equipamentos",
            f"{metricas['taxa_entrega']:.1f}%",
            "Percentual de telefones já entregues"
        ],
        [
            "Taxa de Utilização de Ramais",
            f"{metricas['taxa_utilizacao_ramais']:.1f}%",
            "Ocupação da infraestrutura de ramais"
        ],
        [
            "Taxa de Ramais em Grupos",  # <-- LINHA ADICIONADA
            f"{metricas.get('taxa_ramais_em_grupo', 0):.1f}%",  # <-- LINHA ADICIONADA
            "Percentual de ramais configurados em grupos"  # <-- LINHA ADICIONADA
        ],
        [
            "Média de Telefones por Colaborador",
            f"{metricas['media_telefones_pessoa']:.2f}",
            "Relação entre aparelhos e usuários"
        ],
    ]

    # ... (o resto da função continua igual)
    tabela_kpis = Table(kpis, colWidths=[7 * cm, 3.5 * cm, 6.5 * cm])
    tabela_kpis.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
    ]))

    elementos.append(tabela_kpis)
    elementos.append(Spacer(1, 20))


def criar_recomendacoes(elementos, styles, metricas):
    """
    Cria seção com recomendações baseadas nas métricas.

    Args:
        elementos (list): Lista de elementos do documento
        styles (dict): Estilos do documento
        metricas (dict): Métricas calculadas
    """
    elementos.append(Paragraph("Recomendações Estratégicas", styles["Subtitulo"]))

    melhor = metricas["melhor_secretaria"]
    pior = metricas["pior_secretaria"]

    total_melhor = melhor["montados"] + melhor["nao_montados"]
    taxa_melhor = (melhor["montados"] / total_melhor * 100) if total_melhor > 0 else 0

    total_pior = pior["montados"] + pior["nao_montados"]
    taxa_pior = (pior["montados"] / total_pior * 100) if total_pior > 0 else 0

    texto_recomendacoes = f"""
    Com base na análise dos dados apresentados, recomenda-se as seguintes ações prioritárias:
    <br/><br/>
    <b>1. Priorização de Entregas:</b> A secretaria <b>{pior["secretaria"]}</b> apresenta 
    a menor taxa de implementação ({taxa_pior:.1f}%), com {pior["nao_montados"]} equipamentos 
    pendentes. Recomenda-se priorizar a conclusão das entregas neste setor para garantir 
    a equidade na distribuição de recursos.
    <br/><br/>
    <b>2. Benchmarking Interno:</b> A secretaria <b>{melhor["secretaria"]}</b> demonstra 
    excelente desempenho com taxa de {taxa_melhor:.1f}% de implementação. Sugere-se 
    documentar as práticas adotadas neste setor para replicação nas demais unidades.
    <br/><br/>
    <b>3. Otimização de Ramais:</b> Com taxa de utilização de ramais em 
    {metricas["taxa_utilizacao_ramais"]:.1f}%, {'recomenda-se avaliar a possibilidade de redistribuição dos ramais livres para áreas com maior demanda' if metricas["taxa_utilizacao_ramais"] < 80 else 'a infraestrutura está adequadamente dimensionada, mas deve-se monitorar a demanda para futuras expansões'}.
    <br/><br/>
    <b>4. Acompanhamento Contínuo:</b> Estabelecer indicadores de monitoramento mensal 
    para acompanhar a evolução da taxa de entrega e identificar precocemente eventuais 
    gargalos no processo de implementação.
    """

    elementos.append(Paragraph(texto_recomendacoes, styles["Justificado"]))
    elementos.append(Spacer(1, 25))


def criar_rodape(elementos, styles):
    """
    Cria rodapé com informações adicionais.

    Args:
        elementos (list): Lista de elementos do documento
        styles (dict): Estilos do documento
    """
    texto_rodape = """
    <i>Este relatório foi gerado automaticamente pelo Centro de Informática da Prefeitura Municipal de Piracicaba. 
    Os dados apresentados refletem a situação no momento da geração e devem ser utilizados 
    exclusivamente para fins de análise gerencial e tomada de decisão estratégica.</i>
    """

    elementos.append(Spacer(1, 30))
    elementos.append(Paragraph(texto_rodape, ParagraphStyle(
        'Rodape',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_JUSTIFY,
        borderWidth=1,
        borderColor=colors.HexColor('#cbd5e0'),
        borderPadding=10,
        backColor=colors.HexColor('#f7fafc')
    )))


def criar_secao_grupos(elementos, styles, dados_dashboard):
    """
    Cria uma seção dedicada à análise dos Números de Grupo.

    Args:
        elementos (list): Lista de elementos do documento.
        styles (dict): Estilos do documento.
        dados_dashboard (dict): Dados do dashboard.
    """
    # Adiciona um PageBreak para começar a seção em uma nova página, se desejado.
    # elementos.append(PageBreak())

    elementos.append(Paragraph("Análise de Números Virtuais", styles["Subtitulo"]))

    # Dados necessários
    total_ramais = dados_dashboard.get("ramais_em_uso", 0) + dados_dashboard.get("ramais_livres", 0)
    ramais_em_grupo = dados_dashboard.get("ramais_em_grupo", 0)
    ramais_individuais = total_ramais - ramais_em_grupo
    total_grupos = dados_dashboard.get("total_grupos", 0)  # Supondo que este dado será adicionado

    # Texto explicativo
    texto_explicativo = f"""
    Os Números Virtuais são um recurso estratégico que permite direcionar uma chamada para múltiplos ramais simultaneamente ou em uma ordem de prioridade. Atualmente, a instituição possui <b>{total_grupos} números virtuais ativos</b>, otimizando o atendimento em setores de alta demanda.



    Esta configuração garante que as chamadas sejam atendidas mais rapidamente, melhora a distribuição de carga de trabalho entre os colaboradores e evita que ligações importantes sejam perdidas. Dos <b>{total_ramais} ramais</b> existentes, <b>{ramais_em_grupo}</b> estão configurados para operar dentro de números virtuais, demonstrando um uso significativo desta funcionalidade para aprimorar a eficiência da comunicação interna e externa.
    """
    elementos.append(Paragraph(texto_explicativo, styles["Justificado"]))
    elementos.append(Spacer(1, 20))

    # Gráfico de Pizza: Ramais em Grupos vs. Individuais
    if total_ramais > 0:
        drawing_pie = Drawing(500, 220)

        pizza = Pie()
        pizza.x = 150
        pizza.y = 20
        pizza.width = 160
        pizza.height = 160
        pizza.data = [ramais_em_grupo, ramais_individuais]

        taxa_em_grupo = (ramais_em_grupo / total_ramais) * 100
        taxa_individuais = 100 - taxa_em_grupo

        pizza.labels = [
            f'Em Grupos\n{taxa_em_grupo:.1f}%',
            f'Individuais\n{taxa_individuais:.1f}%'
        ]

        # Cores
        pizza.slices[0].fillColor = colors.HexColor('#63b3ed')  # Azul para grupos
        pizza.slices[1].fillColor = colors.HexColor('#a0aec0')  # Cinza para individuais

        # Configurações de labels
        pizza.slices[0].fontName = 'Helvetica-Bold'
        pizza.slices[1].fontName = 'Helvetica-Bold'
        pizza.slices[0].fontSize = 10
        pizza.slices[1].fontSize = 10

        drawing_pie.add(pizza)
        elementos.append(drawing_pie)
        elementos.append(Spacer(1, 25))


def criar_tabela_composicao_grupos(elementos, styles, dados_composicao):
    """
    Cria tabelas detalhando a composição de cada número de grupo.

    Args:
        elementos (list): Lista de elementos do documento.
        styles (dict): Estilos do documento.
        dados_composicao (list): Lista de dicionários, cada um representando um grupo e seus ramais.
    """
    if not dados_composicao:
        return  # Não faz nada se não houver dados

    elementos.append(Paragraph("Detalhamento da Composição dos Números Virtuais", styles["Subtitulo"]))
    elementos.append(Spacer(1, 15))

    # Estilo para a tabela de cada grupo
    style_tabela = TableStyle([
        # Cabeçalho
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor('#4A5568')),  # Cinza escuro
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

        # Corpo
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E0')),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
        ("TOPPADDING", (0, 1), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 7),
    ])

    for grupo in dados_composicao:
        # Usamos KeepTogether para evitar que a tabela de um grupo seja quebrada entre páginas
        bloco_grupo = []

        # Título para cada grupo
        estilo_titulo_grupo = ParagraphStyle(
            'TituloGrupo',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        bloco_grupo.append(Paragraph(f"Número Virtual: {grupo['numero_grupo']}", estilo_titulo_grupo))

        # Dados da tabela
        dados_tabela = [["Ordem de Prioridade", "Número do Ramal"]]
        for ramal in grupo['ramais']:
            dados_tabela.append([str(ramal['ordem']), str(ramal['numero_ramal'])])

        # Criação da tabela
        tabela = Table(dados_tabela, colWidths=[6 * cm, 11 * cm])
        tabela.setStyle(style_tabela)

        bloco_grupo.append(tabela)
        bloco_grupo.append(Spacer(1, 20))  # Espaço após cada tabela

        elementos.append(KeepTogether(bloco_grupo))


# No seu módulo de relatório, adicione esta nova função

def criar_tabela_composicao_captura(elementos, styles, dados_composicao):
    """
    Cria tabelas detalhando a composição de cada Grupo de Captura.

    Args:
        elementos (list): Lista de elementos do documento.
        styles (dict): Estilos do documento.
        dados_composicao (list): Lista de dicionários, cada um representando um grupo de captura e seus ramais.
    """
    if not dados_composicao:
        return  # Não faz nada se não houver dados

    elementos.append(Paragraph("Detalhamento dos Grupos de Captura", styles["Subtitulo"]))
    elementos.append(Spacer(1, 15))

    # Estilo para a tabela de cada grupo
    style_tabela = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor('#4A5568')),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E0')),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
        ("TOPPADDING", (0, 1), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 7),
    ])

    for grupo in dados_composicao:
        bloco_grupo = []

        # Título para cada grupo
        estilo_titulo_grupo = ParagraphStyle(
            'TituloGrupoCaptura',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        bloco_grupo.append(Paragraph(f"Grupo de Captura: {grupo['nome_grupo']}", estilo_titulo_grupo))

        # Dados da tabela
        dados_tabela = [["Número do Ramal", "Gravação Ativada?"]]
        for ramal in grupo['ramais']:
            dados_tabela.append([str(ramal['numero_ramal']), ramal['gravado']])

        # Criação da tabela
        tabela = Table(dados_tabela, colWidths=[8.5 * cm, 8.5 * cm])
        tabela.setStyle(style_tabela)

        bloco_grupo.append(tabela)
        bloco_grupo.append(Spacer(1, 20))

        elementos.append(KeepTogether(bloco_grupo))



def gerar_relatorio_dashboard(dados_dashboard, dados_grafico):
    """
    Gera relatório completo em PDF com análises avançadas e visualizações profissionais.

    Esta função principal orquestra a criação de um relatório executivo abrangente,
    incluindo sumário executivo, tabelas detalhadas, gráficos comparativos, análise
    de métricas e recomendações estratégicas.

    Args:
        dados_dashboard (dict): Dicionário contendo os dados gerais do dashboard.
            Estrutura esperada:
            {
                "pessoa": int,           # Total de pessoas ativas
                "telefone": int,         # Total de telefones ativos
                "ramais_em_uso": int,    # Quantidade de ramais em uso
                "ramais_livres": int     # Quantidade de ramais livres
            }

        dados_grafico (list): Lista de dicionários com dados por secretaria.
            Estrutura esperada:
            [
                {
                    "secretaria": str,    # Nome da secretaria
                    "montados": int,      # Telefones entregues
                    "nao_montados": int   # Telefones pendentes
                },
                ...
            ]

    Returns:
        BytesIO: Buffer contendo o PDF gerado, pronto para download ou envio.

    Exemplo de uso:
        >>> dados_dash = {
        ...     "pessoa": 150,
        ...     "telefone": 145,
        ...     "ramais_em_uso": 120,
        ...     "ramais_livres": 30
        ... }
        >>> dados_sec = [
        ...     {"secretaria": "Administração", "montados": 25, "nao_montados": 5},
        ...     {"secretaria": "Financeiro", "montados": 20, "nao_montados": 3}
        ... ]
        >>> buffer = gerar_relatorio_dashboard(dados_dash, dados_sec)
        >>> with open("relatorio.pdf", "wb") as f:
        ...     f.write(buffer.getvalue())
    """
    # Inicialização do documento
    buffer = BytesIO()
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Relatório Dashboard Telefônico",
        author="Sistema de Gestão"
    )
    dados_composicao = dados_dashboard.get("dados_composicao_grupos", [])
    dados_composicao_captura = dados_dashboard.get("dados_composicao_captura", [])
    # Criar estilos personalizados
    styles = criar_estilos_personalizados()

    # Calcular métricas avançadas
    metricas = calcular_metricas_avancadas(dados_dashboard, dados_grafico)

    # Lista de elementos do documento
    elementos = []

    # Construir seções do relatório
    criar_cabecalho(elementos, styles)
    criar_sumario_executivo(elementos, styles, dados_dashboard, metricas)
    criar_tabela_resumo(elementos, styles, dados_dashboard)
    criar_grafico_barras(elementos, styles, dados_grafico)
    criar_grafico_pizza(elementos, styles, metricas)
    criar_tabela_detalhada(elementos, styles, dados_grafico)
    criar_analise_metricas(elementos, styles, metricas)
    criar_secao_grupos(elementos, styles, dados_dashboard)
    criar_tabela_composicao_grupos(elementos, styles, dados_composicao)
    elementos.append(PageBreak()) # Opcional: Inicia a seção em uma nova página
    criar_tabela_composicao_captura(elementos, styles, dados_composicao_captura)
    criar_recomendacoes(elementos, styles, metricas)
    criar_rodape(elementos, styles)

    # Gerar PDF
    pdf.build(elementos)
    buffer.seek(0)

    return buffer


# Exemplo de uso e teste
if __name__ == "__main__":
    # Dados de exemplo para teste
    dados_dashboard_exemplo = {
        "pessoa": 150,
        "telefone": 145,
        "ramais_em_uso": 120,
        "ramais_livres": 30
    }

    dados_grafico_exemplo = [
        {"secretaria": "Administração", "montados": 25, "nao_montados": 5},
        {"secretaria": "Financeiro", "montados": 20, "nao_montados": 3},
        {"secretaria": "Recursos Humanos", "montados": 18, "nao_montados": 7},
        {"secretaria": "TI", "montados": 22, "nao_montados": 2},
        {"secretaria": "Operações", "montados": 30, "nao_montados": 10},
        {"secretaria": "Jurídico", "montados": 15, "nao_montados": 8}
    ]

    # Gerar relatório
    buffer = gerar_relatorio_dashboard(dados_dashboard_exemplo, dados_grafico_exemplo)

    # Salvar em arquivo
    with open("/home/ubuntu/relatorio_exemplo.pdf", "wb") as f:
        f.write(buffer.getvalue())

    print("Relatório gerado com sucesso: /home/ubuntu/relatorio_exemplo.pdf")