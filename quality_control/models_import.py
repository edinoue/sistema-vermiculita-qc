"""
Modelos para sistema de importação de dados
"""

from django.db import models
from django.contrib.auth.models import User
from .models import Product, Property, ProductionLine, Shift, AnalysisType


class ImportTemplate(models.Model):
    """
    Template para importação de dados
    """
    TEMPLATE_TYPE_CHOICES = [
        ('SPOT', 'Análises Pontuais'),
        ('COMPOSITE', 'Amostras Compostas'),
        ('BOTH', 'Ambos'),
    ]
    
    name = models.CharField('Nome do Template', max_length=100, unique=True)
    template_type = models.CharField('Tipo', max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    description = models.TextField('Descrição', blank=True)
    
    # Configurações do template
    excel_file = models.FileField('Arquivo Excel', upload_to='import_templates/', help_text='Arquivo Excel de exemplo')
    instructions = models.TextField('Instruções', blank=True, help_text='Instruções para preenchimento')
    
    # Campos obrigatórios
    required_columns = models.JSONField('Colunas Obrigatórias', default=list, help_text='Lista de colunas obrigatórias')
    optional_columns = models.JSONField('Colunas Opcionais', default=list, help_text='Lista de colunas opcionais')
    
    # Mapeamento de campos
    field_mapping = models.JSONField('Mapeamento de Campos', default=dict, help_text='Mapeamento entre colunas Excel e campos do sistema')
    
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Criado por', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Template de Importação'
        verbose_name_plural = 'Templates de Importação'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class ImportSession(models.Model):
    """
    Sessão de importação de dados
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('PROCESSING', 'Processando'),
        ('COMPLETED', 'Concluído'),
        ('FAILED', 'Falhou'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    template = models.ForeignKey(ImportTemplate, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuário')
    
    # Arquivo importado
    excel_file = models.FileField('Arquivo Excel', upload_to='imports/')
    original_filename = models.CharField('Nome Original', max_length=255)
    
    # Status e resultados
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_rows = models.PositiveIntegerField('Total de Linhas', default=0)
    processed_rows = models.PositiveIntegerField('Linhas Processadas', default=0)
    successful_rows = models.PositiveIntegerField('Linhas com Sucesso', default=0)
    failed_rows = models.PositiveIntegerField('Linhas com Erro', default=0)
    
    # Logs e erros
    error_log = models.TextField('Log de Erros', blank=True)
    success_log = models.TextField('Log de Sucessos', blank=True)
    
    # Timestamps
    started_at = models.DateTimeField('Iniciado em', auto_now_add=True)
    completed_at = models.DateTimeField('Concluído em', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Sessão de Importação'
        verbose_name_plural = 'Sessões de Importação'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Importação {self.id} - {self.original_filename} ({self.get_status_display()})"
    
    @property
    def progress_percentage(self):
        """Percentual de progresso"""
        if self.total_rows == 0:
            return 0
        return (self.processed_rows / self.total_rows) * 100


class ImportError(models.Model):
    """
    Erros específicos de importação
    """
    session = models.ForeignKey(ImportSession, on_delete=models.CASCADE, related_name='errors')
    row_number = models.PositiveIntegerField('Número da Linha')
    column_name = models.CharField('Nome da Coluna', max_length=100, blank=True)
    error_type = models.CharField('Tipo de Erro', max_length=50)
    error_message = models.TextField('Mensagem de Erro')
    raw_data = models.TextField('Dados Brutos', blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Erro de Importação'
        verbose_name_plural = 'Erros de Importação'
        ordering = ['row_number']
    
    def __str__(self):
        return f"Erro na linha {self.row_number}: {self.error_message[:50]}..."





