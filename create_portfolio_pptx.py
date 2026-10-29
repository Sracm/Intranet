import os
import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_portfolio_powerpoint(dataset_path='portfolio_final_dataset.json', output_pptx='Portfolio_Anderson_Mello_BI_Executive.pptx'):
    """
    Gera apresentação PowerPoint (PPTX) 16:9 profissional com o Design System MQ
    (Fundo Escuro #111111, Dourado #CB9727, Branco, tipografia Montserrat/Calibri),
    contendo capa executiva, resumo de competências e slides detalhados com as telas
    reais de cada dashboard para edição completa pelo usuário.
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"{dataset_path} não encontrado.")

    with open(dataset_path, 'r', encoding='utf-8') as f:
        dashboards = json.load(f)

    prs = Presentation()
    # Configura formato Widescreen 16:9 moderno (13.33 x 7.5 polegadas)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_slide_layout = prs.slide_layouts[6]

    # Paleta de cores MQ
    COLOR_BG = RGBColor(14, 15, 18)          # #0E0F12
    COLOR_SURFACE = RGBColor(26, 28, 33)     # #1A1C21
    COLOR_GOLD = RGBColor(203, 151, 39)      # #CB9727
    COLOR_GOLD_LIGHT = RGBColor(229, 183, 75)# #E5B74B
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_GRAY = RGBColor(160, 166, 175)
    COLOR_MUTED = RGBColor(100, 110, 125)

    def set_slide_background(slide):
        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, prs.slide_height
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = COLOR_BG
        bg_shape.line.fill.background()
        return bg_shape

    # ════════════════════════════════════════════════════════════════════════════
    # SLIDE 1: CAPA EXECUTIVA
    # ════════════════════════════════════════════════════════════════════════════
    slide1 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide1)

    # Borda decorativa dourada
    border = slide1.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9)
    )
    border.fill.background()
    border.line.color.rgb = COLOR_GOLD
    border.line.width = Pt(1.5)

    # Badge MQ PRO
    badge = slide1.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.3), Inches(1.3), Inches(2.8), Inches(0.45)
    )
    badge.fill.solid()
    badge.fill.fore_color.rgb = COLOR_GOLD
    badge.line.fill.background()
    tb_badge = badge.text_frame
    tb_badge.text = "VISÃO COMPLETA, CONTROLE TOTAL."
    p = tb_badge.paragraphs[0]
    p.font.name = "Montserrat"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0, 0, 0)
    p.alignment = PP_ALIGN.CENTER

    # Título Principal
    txBox = slide1.shapes.add_textbox(Inches(1.3), Inches(1.9), Inches(10.5), Inches(2.2))
    tf = txBox.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "Cockpit Executivo Estratégico"
    p1.font.name = "Montserrat"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE

    p2 = tf.add_paragraph()
    p2.text = "& Soluções Analíticas de Alta Performance"
    p2.font.name = "Montserrat"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_GOLD

    p3 = tf.add_paragraph()
    p3.text = "Catálogo executivo de dashboards em Power BI e aplicações Fullstack Python conectadas a ERPs."
    p3.font.name = "Montserrat"
    p3.font.size = Pt(14)
    p3.font.color.rgb = COLOR_GRAY
    p3.space_before = Pt(14)

    # 4 Caixas de Métricas
    metrics = [
        ("66+", "Dashboards Criados"),
        ("13", "Áreas Corporativas"),
        ("100%", "Automação")
    ]
    card_w = Inches(2.4)
    card_gap = Inches(0.3)
    start_x = Inches(1.3)
    for i, (val, lbl) in enumerate(metrics):
        cx = start_x + (i * (card_w + card_gap))
        cbox = slide1.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, cx, Inches(4.3), card_w, Inches(1.1)
        )
        cbox.fill.solid()
        cbox.fill.fore_color.rgb = COLOR_SURFACE
        cbox.line.color.rgb = RGBColor(45, 50, 60)
        cbox.line.width = Pt(1)
        ctf = cbox.text_frame
        ctf.text = val
        cp1 = ctf.paragraphs[0]
        cp1.font.name = "Montserrat"
        cp1.font.size = Pt(22)
        cp1.font.bold = True
        cp1.font.color.rgb = COLOR_GOLD
        cp1.alignment = PP_ALIGN.CENTER
        
        cp2 = ctf.add_paragraph()
        cp2.text = lbl
        cp2.font.name = "Montserrat"
        cp2.font.size = Pt(9)
        cp2.font.bold = True
        cp2.font.color.rgb = COLOR_GRAY
        cp2.alignment = PP_ALIGN.CENTER

    # Rodapé do Autor
    txAuthor = slide1.shapes.add_textbox(Inches(1.3), Inches(5.6), Inches(10.5), Inches(0.8))
    atf = txAuthor.text_frame
    ap1 = atf.paragraphs[0]
    ap1.text = "Antonio Mello  |  Especialista em BI & Engenharia de Dados"
    ap1.font.name = "Montserrat"
    ap1.font.size = Pt(12)
    ap1.font.bold = True
    ap1.font.color.rgb = COLOR_WHITE

    ap2 = atf.add_paragraph()
    ap2.text = "E-mail: acmello.106@gmail.com   •   São Paulo, SP   •   Power BI • DAX • SQL • Python • Oracle"
    ap2.font.name = "Montserrat"
    ap2.font.size = Pt(10)
    ap2.font.color.rgb = COLOR_GOLD_LIGHT

    # ════════════════════════════════════════════════════════════════════════════
    # SLIDE 2: SUMÁRIO EXECUTIVO & COMPETÊNCIAS
    # ════════════════════════════════════════════════════════════════════════════
    slide2 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide2)

    # Top bar
    hbar = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.6), Inches(11.733), Inches(0.04))
    hbar.fill.solid()
    hbar.fill.fore_color.rgb = COLOR_GOLD
    hbar.line.fill.background()

    stx = slide2.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.733), Inches(0.6))
    stf = stx.text_frame
    sp = stf.paragraphs[0]
    sp.text = "PERFIL PROFISSIONAL & ARQUITETURA TÉCNICA"
    sp.font.name = "Montserrat"
    sp.font.size = Pt(18)
    sp.font.bold = True
    sp.font.color.rgb = COLOR_WHITE

    # 3 Blocos de Competências
    competences = [
        ("MODELAGEM & BUSINESS INTELLIGENCE",
         "• Criação de Data Warehouses corporativos sob metodologia dimensional Star Schema (Fatos e Dimensões).\n"
         "• Fórmulas analíticas complexas com DAX Avançado, Time Intelligence e otimização VertiPaq.\n"
         "• Governança de dados de ponta a ponta com Row-Level Security (RLS) dinâmico por perfil e departamento."),
        
        ("ENGENHARIA & FULLSTACK ANALYTICS",
         "• Desenvolvimento de Cockpits e Portais Web em Python (Flask) integrados nativamente ao Oracle ERP Sankhya e MariaDB.\n"
         "• Automação total de pipelines de dados, dispensando licenciamentos por usuário em telas operacionais de chão e TV.\n"
         "• Painéis de alta disponibilidade com atualização em tempo real para TV de diretoria e equipes."),
        
        ("IMPACTO & VISÃO DE NEGÓCIO",
         "• Atuação direta com Diretores Executivos e Gerências para traduzir desafios operacionais em KPIs de tomada de ação.\n"
         "• Redução expressiva de ruptura de estoque através de módulos inteligentes de Demanda & Reabastecimento.\n"
         "• Acompanhamento diário consolidado de DRE Gerencial, Comissões e Indicadores Financeiros/Vendas.")
    ]

    col_w = Inches(3.7)
    col_gap = Inches(0.31)
    for i, (title, desc) in enumerate(competences):
        col_x = Inches(0.8) + (i * (col_w + col_gap))
        box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, col_x, Inches(1.8), col_w, Inches(4.8))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_SURFACE
        box.line.color.rgb = COLOR_GOLD if i == 0 else RGBColor(45, 50, 60)
        box.line.width = Pt(1.5) if i == 0 else Pt(1)

        btf = box.text_frame
        btf.margin_left = Inches(0.25)
        btf.margin_right = Inches(0.25)
        btf.margin_top = Inches(0.3)
        
        bp1 = btf.paragraphs[0]
        bp1.text = title
        bp1.font.name = "Montserrat"
        bp1.font.size = Pt(12)
        bp1.font.bold = True
        bp1.font.color.rgb = COLOR_GOLD

        bp2 = btf.add_paragraph()
        bp2.text = desc
        bp2.font.name = "Montserrat"
        bp2.font.size = Pt(10)
        bp2.font.color.rgb = COLOR_GRAY
        bp2.space_before = Pt(12)

    # ════════════════════════════════════════════════════════════════════════════
    # SLIDES DOS DASHBOARDS (2 DASHBOARDS POR SLIDE COM IMAGEM & DETALHES)
    # ════════════════════════════════════════════════════════════════════════════
    fallback_img = 'static/portfolio_screenshots/pbi_sample.jpg'

    # Agrupa de 2 em 2 para visualização ampla e legível
    chunk_size = 2
    for chunk_idx in range(0, len(dashboards), chunk_size):
        chunk = dashboards[chunk_idx:chunk_idx+chunk_size]
        slide = prs.slides.add_slide(blank_slide_layout)
        set_slide_background(slide)

        # Header do slide
        hbar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.5), Inches(11.733), Inches(0.03))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = COLOR_GOLD
        hbar.line.fill.background()

        stx = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.733), Inches(0.5))
        stf = stx.text_frame
        sp = stf.paragraphs[0]
        sp.text = f"GALERIA DE DASHBOARDS  |  {chunk[0].get('department', 'Geral').upper()}"
        sp.font.name = "Montserrat"
        sp.font.size = Pt(14)
        sp.font.bold = True
        sp.font.color.rgb = COLOR_WHITE

        # Renderiza até 2 cards por slide (lado esquerdo e lado direito)
        for card_i, dash in enumerate(chunk):
            col_x = Inches(0.8) + (card_i * Inches(5.95))
            
            # Card Container
            card_box = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, col_x, Inches(1.3), Inches(5.75), Inches(5.7)
            )
            card_box.fill.solid()
            card_box.fill.fore_color.rgb = COLOR_SURFACE
            card_box.line.color.rgb = RGBColor(40, 45, 55)
            card_box.line.width = Pt(1)

            # Imagem do Dashboard
            raw_img = dash.get('image', '').split('?')[0].lstrip('/')
            img_to_use = raw_img if os.path.exists(raw_img) else fallback_img

            if os.path.exists(img_to_use):
                try:
                    slide.shapes.add_picture(
                        img_to_use, col_x + Inches(0.2), Inches(1.5), Inches(5.35), Inches(2.9)
                    )
                except Exception as e:
                    pass

            # Informações Textuais Abaixo da Tela
            dtx = slide.shapes.add_textbox(col_x + Inches(0.2), Inches(4.45), Inches(5.35), Inches(2.4))
            dtf = dtx.text_frame
            dtf.word_wrap = True
            dtf.margin_left = dtf.margin_right = dtf.margin_top = dtf.margin_bottom = 0

            # Badge Tecnologia + Departamento
            p_top = dtf.paragraphs[0]
            is_full = 'Fullstack' in dash.get('tech', '')
            tech_txt = "WEB APP PYTHON / FLASK" if is_full else "POWER BI SERVICE"
            p_top.text = f"[{dash.get('department', 'Geral')}]  •  {tech_txt}"
            p_top.font.name = "Montserrat"
            p_top.font.size = Pt(8.5)
            p_top.font.bold = True
            p_top.font.color.rgb = COLOR_GOLD

            # Título do Dashboard
            p_title = dtf.add_paragraph()
            p_title.text = dash.get('title', 'Sem título')[:45]
            p_title.font.name = "Montserrat"
            p_title.font.size = Pt(12)
            p_title.font.bold = True
            p_title.font.color.rgb = COLOR_WHITE
            p_title.space_before = Pt(3)

            # Descrição
            p_desc = dtf.add_paragraph()
            p_desc.text = dash.get('description', 'Cockpit analítico para monitoramento de KPIs estratégicos.')[:130]
            p_desc.font.name = "Montserrat"
            p_desc.font.size = Pt(8.5)
            p_desc.font.color.rgb = COLOR_GRAY
            p_desc.space_before = Pt(3)

            # Impacto
            p_imp = dtf.add_paragraph()
            p_imp.text = "Impacto: " + dash.get('impact', 'Agilidade na tomada de decisão.')[:100]
            p_imp.font.name = "Montserrat"
            p_imp.font.size = Pt(8.5)
            p_imp.font.color.rgb = COLOR_GOLD_LIGHT
            p_imp.space_before = Pt(3)

            # Stack
            p_stk = dtf.add_paragraph()
            stack_txt = "Stack: " + " • ".join(dash.get('stack', [])[:4])
            p_stk.text = stack_txt
            p_stk.font.name = "Montserrat"
            p_stk.font.size = Pt(7.5)
            p_stk.font.color.rgb = COLOR_MUTED
            p_stk.space_before = Pt(3)

    prs.save(output_pptx)
    print(f"Apresentação PowerPoint criada com sucesso em: {output_pptx}")
    return output_pptx

if __name__ == '__main__':
    create_portfolio_powerpoint()
