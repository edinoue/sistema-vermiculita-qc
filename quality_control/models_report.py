"""
Modelos para sistema de laudos e relatórios
"""

from django.db import models
from django.contrib.auth.models import User
from .models import SpotAnalysis, CompositeSample


class ReportTemplate(models.Model):
    """
    Modelo para templates de laudos personalizáveis
    """
    TEMPLATE_TYPE_CHOICES = [
        ('SPOT', 'Análise Pontual'),
        ('COMPOSITE', 'Análise Composta'),
        ('GENERAL', 'Geral'),
    ]
    
    name = models.CharField('Nome do Template', max_length=100, unique=True)
    template_type = models.CharField('Tipo de Template', max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    description = models.TextField('Descrição', blank=True)
    
    # Configurações do template
    header_template = models.TextField('Cabeçalho (HTML)', blank=True, help_text='HTML para o cabeçalho do laudo')
    footer_template = models.TextField('Rodapé (HTML)', blank=True, help_text='HTML para o rodapé do laudo')
    body_template = models.TextField('Corpo (HTML)', blank=True, help_text='HTML para o corpo do laudo')
    
    # Configurações de impressão
    page_size = models.CharField('Tamanho da Página', max_length=20, default='A4', choices=[
        ('A4', 'A4'),
        ('A3', 'A3'),
        ('LETTER', 'Carta'),
    ])
    orientation = models.CharField('Orientação', max_length=20, default='PORTRAIT', choices=[
        ('PORTRAIT', 'Retrato'),
        ('LANDSCAPE', 'Paisagem'),
    ])
    
    # Metadados
    is_active = models.BooleanField('Ativo', default=True)
    is_default = models.BooleanField('Template Padrão', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Criado por', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Template de Laudo'
        verbose_name_plural = 'Templates de Laudos'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def save(self, *args, **kwargs):
        # Se este template for marcado como padrão, desmarcar outros do mesmo tipo
        if self.is_default:
            ReportTemplate.objects.filter(
                template_type=self.template_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class ReportField(models.Model):
    """
    Campos que podem ser incluídos nos laudos
    """
    FIELD_TYPE_CHOICES = [
        ('TEXT', 'Texto'),
        ('NUMBER', 'Número'),
        ('DATE', 'Data'),
        ('TIME', 'Hora'),
        ('BOOLEAN', 'Sim/Não'),
        ('IMAGE', 'Imagem'),
        ('TABLE', 'Tabela'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField('Nome do Campo', max_length=100)
    field_type = models.CharField('Tipo do Campo', max_length=20, choices=FIELD_TYPE_CHOICES)
    source_field = models.CharField('Campo de Origem', max_length=100, help_text='Campo do modelo de dados (ex: product.name)')
    display_order = models.PositiveIntegerField('Ordem de Exibição', default=0)
    is_required = models.BooleanField('Obrigatório', default=True)
    format_string = models.CharField('Formato', max_length=100, blank=True, help_text='Formato para exibição (ex: %.2f para números)')
    
    class Meta:
        verbose_name = 'Campo do Laudo'
        verbose_name_plural = 'Campos do Laudo'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return f"{self.template.name} - {self.name}"


class GeneratedReport(models.Model):
    """
    Laudos gerados
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Rascunho'),
        ('FINAL', 'Final'),
        ('APPROVED', 'Aprovado'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.PROTECT)
    title = models.CharField('Título', max_length=200)
    report_number = models.CharField('Número do Laudo', max_length=50, unique=True)
    
    # Dados do laudo
    spot_analysis = models.ForeignKey(SpotAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    composite_sample = models.ForeignKey(CompositeSample, on_delete=models.CASCADE, null=True, blank=True)
    
    # Status e metadados
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    generated_at = models.DateTimeField('Gerado em', auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Gerado por')
    
    # Arquivo gerado
    pdf_file = models.FileField('Arquivo PDF', upload_to='reports/', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Laudo Gerado'
        verbose_name_plural = 'Laudos Gerados'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.report_number} - {self.title}"





