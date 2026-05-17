import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT

STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'storage')
OUTPUT_FILE = os.path.join(STORAGE_DIR, 'calendar.pdf')

class CREATEPDF:
    def __init__(self):
        """Initialize PDF with ReportLab."""
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR, exist_ok=True)
        
        self.doc = SimpleDocTemplate(
            OUTPUT_FILE,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        self.story = []
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles for better appearance."""
        self.styles.add(ParagraphStyle(
            name='MonthTitle',
            parent=self.styles['Heading1'],
            fontSize=32,
            textColor=HexColor('#667eea'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='EventDate',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#4a5568'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='EventActivity',
            parent=self.styles['Normal'],
            fontSize=13,
            textColor=HexColor('#2d3748'),
            spaceAfter=8,
            fontName='Helvetica-Bold',
            borderColor=HexColor('#e2e8f0'),
            borderPadding=8,
            borderRadius=4
        ))
        
        self.styles.add(ParagraphStyle(
            name='EventDescription',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#718096'),
            spaceAfter=4,
            leading=14,
            fontName='Helvetica'
        ))

    def add_event(self, month: str, date: str, title: str, description: str = ''):
        """Add a stylish event page."""
        # Month Title
        month_title = Paragraph(f'{month} 2026', self.styles['MonthTitle'])
        self.story.append(month_title)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Event Box
        if date:
            event_date = Paragraph(f'📅 {date}', self.styles['EventDate'])
            self.story.append(event_date)
        
        event_activity = Paragraph(title, self.styles['EventActivity'])
        self.story.append(event_activity)
        self.story.append(Spacer(1, 0.1*inch))
        
        if description:
            event_desc = Paragraph(description, self.styles['EventDescription'])
            self.story.append(event_desc)
        
        self.story.append(Spacer(1, 0.3*inch))
        
        # Add separator line
        separator_data = [['_' * 80]]
        separator_table = Table(separator_data, colWidths=[7.5*inch])
        separator_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#cbd5e0')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        self.story.append(separator_table)
        self.story.append(Spacer(1, 0.2*inch))

    def add_event_bilingual(self, month: str, date: str, title_en: str, title_bn: str, description_en: str = '', description_bn: str = ''):
        """Add bilingual event page (English and Bengali)."""
        # Month Title with bilingual
        month_title = Paragraph(f'{month} 2026 | {self._get_bengali_month(month)} ২০२६', self.styles['MonthTitle'])
        self.story.append(month_title)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Date
        if date:
            event_date = Paragraph(f'📅 {date}', self.styles['EventDate'])
            self.story.append(event_date)
        
        # English Title
        event_activity_en = Paragraph(f'<b>English:</b> {title_en}', self.styles['EventActivity'])
        self.story.append(event_activity_en)
        self.story.append(Spacer(1, 0.08*inch))
        
        # Bengali Title
        event_activity_bn = Paragraph(f'<b>বাংলা:</b> {title_bn}', self.styles['EventActivity'])
        self.story.append(event_activity_bn)
        self.story.append(Spacer(1, 0.1*inch))
        
        # English Description
        if description_en:
            event_desc_en = Paragraph(f'<b>Details (EN):</b> {description_en}', self.styles['EventDescription'])
            self.story.append(event_desc_en)
            self.story.append(Spacer(1, 0.08*inch))
        
        # Bengali Description
        if description_bn:
            event_desc_bn = Paragraph(f'<b>বিবরণ (বাংলা):</b> {description_bn}', self.styles['EventDescription'])
            self.story.append(event_desc_bn)
        
        self.story.append(Spacer(1, 0.3*inch))
        
        # Separator
        separator_data = [['_' * 80]]
        separator_table = Table(separator_data, colWidths=[7.5*inch])
        separator_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#cbd5e0')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        self.story.append(separator_table)
        self.story.append(Spacer(1, 0.2*inch))

    def _get_bengali_month(self, month: str) -> str:
        """Convert English month to Bengali."""
        months = {
            'January': 'জানুয়ারি',
            'February': 'ফেব্রুয়ারি',
            'March': 'মার্চ',
            'April': 'এপ্রিল',
            'May': 'মে',
            'June': 'জুন',
            'July': 'জুলাই',
            'August': 'আগস্ট',
            'September': 'সেপ্টেম্বর',
            'October': 'অক্টোবর',
            'November': 'নভেম্বর',
            'December': 'ডিসেম্বর'
        }
        return months.get(month, month)


    def save(self) -> str:
        """Build and save the PDF."""
        self.doc.build(self.story)
        return OUTPUT_FILE

    def clear(self):
        """Reset for a fresh PDF."""
        self.story = []

