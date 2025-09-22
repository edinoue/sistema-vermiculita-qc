"""
Serviço para geração de PDFs de laudos
"""

import os
from io import BytesIO
from django.template.loader import render_to_string
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import qrcode
from PIL import Image as PILImage

from .report_models import QualityReport, ReportTemplate


class PDFReportGenerator:
    """
    Gerador de PDFs para laudos de qualidade
    """
    
    def __init__(self, quality_report: QualityReport):
        self.report = quality_report
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=30*mm,
            bottomMargin=30*mm
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Estilos personalizados
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
    
    def generate_pdf(self) -> BytesIO:
        """
        Gera o PDF completo do laudo
        """
        self._add_header()
        self._add_report_info()
        self._add_product_info()
        self._add_analysis_results()
        self._add_specifications_compliance()
        self._add_observations()
        self._add_signatures()
        self._add_footer()
        
        # Construir PDF
        self.doc.build(self.story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
        # Retornar buffer
        self.buffer.seek(0)
        return self.buffer
    
    def _add_header(self):
        """Adiciona cabeçalho do laudo"""
        # Logo da empresa (se existir)
        logo_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'images', 'logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=60*mm, height=30*mm)
            self.story.append(logo)
            self.story.append(Spacer(1, 12))
        
        # Título principal
        title = Paragraph("LAUDO DE QUALIDADE", self.title_style)
        self.story.append(title)
        
        # Número do laudo
        report_number = Paragraph(f"<b>Laudo Nº:</b> {self.report.report_number}", self.subtitle_style)
        self.story.append(report_number)
        
        self.story.append(Spacer(1, 20))
    
    def _add_report_info(self):
        """Adiciona informações básicas do laudo"""
        subtitle = Paragraph("INFORMAÇÕES DO LAUDO", self.subtitle_style)
        self.story.append(subtitle)
        
        # Dados em tabela
        data = [
            ['Data de Emissão:', datetime.now().strftime('%d/%m/%Y %H:%M')],
            ['Período de Análise:', f"{self.report.start_date.strftime('%d/%m/%Y')} a {self.report.end_date.strftime('%d/%m/%Y')}"],
            ['Linha de Produção:', self.report.production_line.name],
            ['Status:', self.report.get_status_display()],
        ]
        
        if self.report.batch_number:
            data.append(['Número do Lote:', self.report.batch_number])
        
        if self.report.quantity:
            data.append(['Quantidade:', f"{self.report.quantity} toneladas"])
        
        table = Table(data, colWidths=[60*mm, 100*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def _add_product_info(self):
        """Adiciona informações do produto"""
        subtitle = Paragraph("INFORMAÇÕES DO PRODUTO", self.subtitle_style)
        self.story.append(subtitle)
        
        data = [
            ['Produto:', self.report.product.name],
            ['Código:', self.report.product.code],
            ['Categoria:', self.report.product.get_category_display()],
        ]
        
        if self.report.product.description:
            data.append(['Descrição:', self.report.product.description])
        
        # Informações do cliente
        if self.report.customer_name:
            data.append(['Cliente:', self.report.customer_name])
        
        if self.report.customer_document:
            data.append(['CNPJ/CPF:', self.report.customer_document])
        
        if self.report.destination:
            data.append(['Destino:', self.report.destination])
        
        table = Table(data, colWidths=[60*mm, 100*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def _add_analysis_results(self):
        """Adiciona resultados das análises"""
        subtitle = Paragraph("RESULTADOS DAS ANÁLISES", self.subtitle_style)
        self.story.append(subtitle)
        
        # Análises pontuais
        spot_analyses = self.report.spot_analyses.all().order_by('property__category', 'property__identifier')
        
        if spot_analyses.exists():
            # Agrupar por propriedade
            properties_data = {}
            for analysis in spot_analyses:
                prop_key = f"{analysis.property.identifier} - {analysis.property.name}"
                if prop_key not in properties_data:
                    properties_data[prop_key] = {
                        'unit': analysis.property.unit,
                        'values': [],
                        'category': analysis.property.get_category_display()
                    }
                properties_data[prop_key]['values'].append(analysis.value)
            
            # Criar tabela de resultados
            data = [['Propriedade', 'Unidade', 'Valores', 'Média', 'Categoria']]
            
            for prop_name, prop_data in properties_data.items():
                values = prop_data['values']
                mean_value = sum(values) / len(values) if values else 0
                values_str = ', '.join([f"{v:.4f}" for v in values])
                
                data.append([
                    prop_name,
                    prop_data['unit'] or '-',
                    values_str,
                    f"{mean_value:.4f}",
                    prop_data['category']
                ])
            
            table = Table(data, colWidths=[50*mm, 20*mm, 40*mm, 25*mm, 25*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            self.story.append(table)
        else:
            no_data = Paragraph("Nenhuma análise pontual encontrada.", self.normal_style)
            self.story.append(no_data)
        
        self.story.append(Spacer(1, 20))
    
    def _add_specifications_compliance(self):
        """Adiciona conformidade com especificações"""
        subtitle = Paragraph("CONFORMIDADE COM ESPECIFICAÇÕES", self.subtitle_style)
        self.story.append(subtitle)
        
        # Buscar especificações do produto
        specifications = self.report.product.specification_set.all()
        
        if specifications.exists():
            data = [['Propriedade', 'LIE', 'Alvo', 'LSE', 'Resultado', 'Status']]
            
            for spec in specifications:
                # Buscar análises desta propriedade
                analyses = self.report.spot_analyses.filter(property=spec.property)
                
                if analyses.exists():
                    values = [a.value for a in analyses]
                    mean_value = sum(values) / len(values)
                    
                    # Verificar conformidade
                    status = "CONFORME"
                    if spec.lsl and mean_value < spec.lsl:
                        status = "ABAIXO DO LIMITE"
                    elif spec.usl and mean_value > spec.usl:
                        status = "ACIMA DO LIMITE"
                    
                    # Cor do status
                    status_color = colors.green if status == "CONFORME" else colors.red
                    
                    data.append([
                        f"{spec.property.identifier} - {spec.property.name}",
                        f"{spec.lsl:.4f}" if spec.lsl else "-",
                        f"{spec.target:.4f}" if spec.target else "-",
                        f"{spec.usl:.4f}" if spec.usl else "-",
                        f"{mean_value:.4f}",
                        status
                    ])
            
            if len(data) > 1:  # Se há dados além do cabeçalho
                table = Table(data, colWidths=[40*mm, 20*mm, 20*mm, 20*mm, 25*mm, 35*mm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                
                self.story.append(table)
            else:
                no_specs = Paragraph("Nenhuma especificação encontrada para as propriedades analisadas.", self.normal_style)
                self.story.append(no_specs)
        else:
            no_specs = Paragraph("Nenhuma especificação cadastrada para este produto.", self.normal_style)
            self.story.append(no_specs)
        
        self.story.append(Spacer(1, 20))
    
    def _add_observations(self):
        """Adiciona observações"""
        if self.report.observations:
            subtitle = Paragraph("OBSERVAÇÕES", self.subtitle_style)
            self.story.append(subtitle)
            
            observations = Paragraph(self.report.observations, self.normal_style)
            self.story.append(observations)
            
            self.story.append(Spacer(1, 20))
    
    def _add_signatures(self):
        """Adiciona área de assinaturas"""
        subtitle = Paragraph("RESPONSÁVEIS", self.subtitle_style)
        self.story.append(subtitle)
        
        # Dados dos responsáveis
        data = [
            ['Elaborado por:', self.report.created_by.get_full_name() or self.report.created_by.username],
            ['Data de Elaboração:', self.report.created_at.strftime('%d/%m/%Y %H:%M')],
        ]
        
        if self.report.approved_by:
            data.extend([
                ['Aprovado por:', self.report.approved_by.get_full_name() or self.report.approved_by.username],
                ['Data de Aprovação:', self.report.approved_at.strftime('%d/%m/%Y %H:%M') if self.report.approved_at else '-'],
            ])
        
        table = Table(data, colWidths=[60*mm, 100*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 40))
        
        # Área para assinaturas físicas
        signature_text = Paragraph("_" * 50 + "<br/>Assinatura do Responsável Técnico", self.normal_style)
        self.story.append(signature_text)
    
    def _add_footer(self):
        """Adiciona rodapé"""
        self.story.append(Spacer(1, 20))
        
        footer_text = f"""
        <para align="center">
        <font size="8">
        Este laudo foi gerado automaticamente pelo Sistema de Controle de Qualidade<br/>
        Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br/>
        Laudo Nº: {self.report.report_number}
        </font>
        </para>
        """
        
        footer = Paragraph(footer_text, self.normal_style)
        self.story.append(footer)
    
    def _add_page_number(self, canvas, doc):
        """Adiciona número da página"""
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.drawRightString(200*mm, 20*mm, text)
    
    def save_pdf_to_report(self):
        """Salva o PDF gerado no modelo QualityReport"""
        pdf_buffer = self.generate_pdf()
        
        # Criar nome do arquivo
        filename = f"laudo_{self.report.report_number}.pdf"
        
        # Salvar no modelo
        self.report.pdf_file.save(
            filename,
            ContentFile(pdf_buffer.getvalue()),
            save=True
        )
        
        return self.report.pdf_file


def generate_quality_report_pdf(quality_report: QualityReport):
    """
    Função utilitária para gerar PDF de um laudo
    """
    generator = PDFReportGenerator(quality_report)
    return generator.save_pdf_to_report()
