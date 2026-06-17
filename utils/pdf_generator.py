import io
import re
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display

def get_urdu_font() -> str:
    """
    Looks for standard Windows fonts supporting Arabic/Urdu unicode characters,
    registers it with ReportLab, and returns the registered font name.
    """
    font_paths = [
        "C:\\Windows\\Fonts\\tahoma.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\times.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                name = os.path.splitext(os.path.basename(path))[0]
                pdfmetrics.registerFont(TTFont(name, path))
                return name
            except Exception:
                pass
    return 'Helvetica'

def shape_text(text: str) -> str:
    """
    Reshapes and applies the bidirectional layout algorithm to Urdu text.
    """
    if not text:
        return ""
    # Check if text contains Arabic/Urdu unicode characters
    if bool(re.search(r'[\u0600-\u06FF]', text)):
        reshaped = reshape(text)
        bidi_text = get_display(reshaped)
        return bidi_text
    return text

def generate_recipe_pdf(card: dict, unit_system: str = "metric") -> bytes:
    """
    Generates a beautifully styled PDF of the recipe card following language preferences
    (English, English+Urdu, or Urdu Only) and excluding any cost estimation.
    """
    buffer = io.BytesIO()
    margin = 0.5 * inch
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=margin,
        leftMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Theme Colors
    primary_color = colors.HexColor('#0F5132')   # Deep Emerald Green
    secondary_color = colors.HexColor('#A87C11') # Dark Gold
    text_color = colors.HexColor('#212529')      # Charcoal
    bg_light = colors.HexColor('#F8F9FA')        # Light grey background
    border_color = colors.HexColor('#DEE2E6')
    
    # Load Urdu Font if available
    urdu_font = get_urdu_font()
    
    # Typography Styles
    title_style = ParagraphStyle(
        'RecipeTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.white,
        alignment=1, # Centered
        spaceAfter=5
    )
    
    title_urdu_style = ParagraphStyle(
        'RecipeTitleUrdu',
        parent=styles['Heading1'],
        fontName=urdu_font,
        fontSize=20,
        textColor=colors.white,
        alignment=1, # Centered
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'RecipeSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        textColor=colors.white,
        alignment=1,
        spaceAfter=5
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )
    
    section_heading_urdu = ParagraphStyle(
        'SectionHeadingUrdu',
        parent=styles['Heading2'],
        fontName=urdu_font,
        fontSize=14,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=8,
        alignment=2, # Right aligned
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=text_color,
        leading=13
    )
    
    body_style_urdu = ParagraphStyle(
        'BodyTextUrdu',
        parent=styles['Normal'],
        fontName=urdu_font,
        fontSize=10,
        textColor=text_color,
        leading=14,
        alignment=2 # Right aligned
    )
    
    bold_body_style = ParagraphStyle(
        'BoldBodyText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=text_color,
        leading=13
    )
    
    bold_body_style_urdu = ParagraphStyle(
        'BoldBodyTextUrdu',
        parent=styles['Normal'],
        fontName=urdu_font,
        fontSize=10,
        textColor=text_color,
        leading=14,
        alignment=2 # Right aligned
    )
    
    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=primary_color,
        alignment=1
    )
    
    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=text_color,
        alignment=1
    )
    
    output_language = card.get("output_language", "english")
    
    # 1. Header Banner
    banner_rows = []
    
    # Render title(s) based on language preference
    if output_language == "urdu":
        title_text_urdu = shape_text(card.get("title_urdu", card.get("recipe_title", "")))
        banner_rows.append([Paragraph(title_text_urdu, title_urdu_style)])
    elif output_language == "both":
        title_text_eng = card.get("recipe_title", "")
        title_text_urdu = shape_text(card.get("title_urdu", ""))
        banner_rows.append([Paragraph(title_text_eng, title_style)])
        if title_text_urdu:
            banner_rows.append([Paragraph(title_text_urdu, title_urdu_style)])
    else:
        title_text_eng = card.get("recipe_title", "")
        banner_rows.append([Paragraph(title_text_eng, title_style)])
        
    banner_rows.append([Paragraph("Your AI Kitchen Mentor 🍳", subtitle_style)])
    
    banner_table = Table(banner_rows, colWidths=[7.5 * inch])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 15))
    
    # 2. Metadata Grid (Cooking Time, Servings, Difficulty - Budget/Cost removed)
    meta_data = [
        [
            Paragraph("COOKING TIME", meta_label_style),
            Paragraph("SERVINGS", meta_label_style),
            Paragraph("DIFFICULTY", meta_label_style)
        ],
        [
            Paragraph(card.get("cooking_time", "N/A"), meta_val_style),
            Paragraph(str(card.get("servings", "N/A")), meta_val_style),
            Paragraph(card.get("difficulty", "N/A"), meta_val_style)
        ]
    ]
    
    meta_table = Table(meta_data, colWidths=[2.5 * inch] * 3)
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # 3. Ingredients Section
    if output_language == "urdu":
        story.append(Paragraph(shape_text("ضروری اجزاء کی فہرست"), section_heading_urdu))
    else:
        story.append(Paragraph("Grocery & Ingredients List", section_heading))
        
    ingredients_detailed = card.get("ingredients_detailed", [])
    ingredients_urdu = card.get("ingredients_urdu", [])
    
    ing_rows = []
    if ingredients_detailed:
        for idx, ing in enumerate(ingredients_detailed):
            name_eng = ing.get("name", "")
            
            # Select unit based on system preference
            if unit_system == "us":
                measure = ing.get("us", "")
            elif unit_system == "desi":
                measure = ing.get("desi", "")
            else:
                measure = ing.get("metric", "")
                
            checkbox = Paragraph("<font name='Helvetica' size='12'>&#9634;</font>", body_style)
            
            # Formatting based on language preference
            if output_language == "urdu":
                name_urdu = ingredients_urdu[idx] if idx < len(ingredients_urdu) else name_eng
                item_desc = Paragraph(shape_text(f"{name_urdu} - {measure}"), body_style_urdu)
                # Swap columns for RTL
                ing_rows.append([item_desc, checkbox])
            elif output_language == "both":
                name_urdu = ingredients_urdu[idx] if idx < len(ingredients_urdu) else ""
                combined_desc = f"<b>{name_eng}</b>"
                if name_urdu:
                    combined_desc += f" / {shape_text(name_urdu)}"
                combined_desc += f" - {measure}"
                item_desc = Paragraph(combined_desc, body_style)
                ing_rows.append([checkbox, item_desc])
            else:
                item_desc = Paragraph(f"<b>{name_eng}</b> - {measure}", body_style)
                ing_rows.append([checkbox, item_desc])
    else:
        # Fallback to standard ingredient list
        for item in card.get("grocery_list", []):
            checkbox = Paragraph("<font name='Helvetica' size='12'>&#9634;</font>", body_style)
            item_desc = Paragraph(item, body_style)
            ing_rows.append([checkbox, item_desc])
            
    if ing_rows:
        if output_language == "urdu":
            # For Urdu RTL, checkbox is on the right
            ing_table = Table(ing_rows, colWidths=[7.1 * inch, 0.4 * inch])
            line_col = 0
        else:
            ing_table = Table(ing_rows, colWidths=[0.4 * inch, 7.1 * inch])
            line_col = 1
            
        ing_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('LINEBELOW', (line_col,0), (line_col,-1), 0.5, colors.HexColor('#E9ECEF')),
        ]))
        story.append(ing_table)
        
    story.append(Spacer(1, 15))
    
    # 4. Cooking Phases
    if output_language == "urdu":
        story.append(Paragraph(shape_text("طریقہ کار"), section_heading_urdu))
    else:
        story.append(Paragraph("Step-by-Step Cooking Masterclass", section_heading))
        
    phases = card.get("phases", [])
    for idx, phase in enumerate(phases):
        p_num = phase.get("phase_number", idx + 1)
        p_name = phase.get("phase_name", f"Phase {p_num}")
        technique = phase.get("technique", "")
        what_to_do_eng = phase.get("what_to_do", "")
        what_to_do_urdu = phase.get("instructions_urdu", "")
        lesson = phase.get("the_lesson", "")
        cue = phase.get("sensory_cue", "")
        
        phase_story = []
        
        if output_language == "urdu":
            header_text = shape_text(f"مرحلہ {p_num}: {p_name}")
            if technique:
                header_text = shape_text(f"({technique}) ") + header_text
            phase_story.append(Paragraph(header_text, bold_body_style_urdu))
            phase_story.append(Spacer(1, 4))
            
            instructions = what_to_do_urdu if what_to_do_urdu else what_to_do_eng
            phase_story.append(Paragraph(shape_text(instructions), body_style_urdu))
            
        elif output_language == "both":
            header_text = f"<b>Phase {p_num}: {p_name}</b>"
            if technique:
                header_text += f" <font color='{secondary_color}'><i>({technique})</i></font>"
            phase_story.append(Paragraph(header_text, bold_body_style))
            phase_story.append(Spacer(1, 4))
            
            phase_story.append(Paragraph(what_to_do_eng, body_style))
            if what_to_do_urdu:
                phase_story.append(Spacer(1, 4))
                phase_story.append(Paragraph(shape_text(what_to_do_urdu), body_style_urdu))
        else:
            header_text = f"<b>Phase {p_num}: {p_name}</b>"
            if technique:
                header_text += f" <font color='{secondary_color}'><i>({technique})</i></font>"
            phase_story.append(Paragraph(header_text, bold_body_style))
            phase_story.append(Spacer(1, 4))
            phase_story.append(Paragraph(what_to_do_eng, body_style))
            
        # Add English metadata to the card bottom (lesson/cue)
        if lesson:
            phase_story.append(Spacer(1, 4))
            lesson_txt = f"<b>Cooking Lesson:</b> {lesson}"
            phase_story.append(Paragraph(lesson_txt, body_style))
        if cue:
            phase_story.append(Spacer(1, 2))
            cue_txt = f"<b>Sensory Cue:</b> <font color='{primary_color}'>{cue}</font>"
            phase_story.append(Paragraph(cue_txt, body_style))
            
        phase_table = Table([[phase_story]], colWidths=[7.5 * inch])
        
        # RTL support: Draw the line on the right side if Urdu Only
        line_side = 'LINERIGHT' if output_language == "urdu" else 'LINELEFT'
        
        phase_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FCFDFD')),
            (line_side, (0,0), (-1,-1), 3, primary_color),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ]))
        
        story.append(phase_table)
        story.append(Spacer(1, 10))
        
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Oblique', 8)
        canvas.setFillColor(colors.HexColor('#6C757D'))
        canvas.drawString(0.5 * inch, 0.3 * inch, "Bawarchi Ease 🍳 - Cook with Confidence.")
        canvas.drawRightString(7.5 * inch, 0.3 * inch, f"Page {doc.page}")
        canvas.restoreState()
        
    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
