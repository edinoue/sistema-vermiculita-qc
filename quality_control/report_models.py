"""
Modelos para laudos e ordens de carregamento
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image

from core.models import ProductionLine
from .models import Product, CompositeSample, SpotAnalysis


class QualityReport(models.Model):
    """
    Laudo de qualidade
    """
    
    STATUS_CHOICES = [
        ('DRAFT', 'Rascunho'),
        ('PENDING', 'Pendente de Aprovação'),
        ('APPROVED', 'Aprovado'),
        ('REJECTED', 'Rejeitado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    REPORT_TYPE_CHOICES = [
        ('COMPOSITE', 'Amostra Composta'),
        ('BATCH', 'Lote de Produção'),
        ('SHIFT', 'Turno'),
        ('CUSTOM', 'Personalizado'),
    ]
    
    # Identificação
    report_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Número do Laudo",
        help_text="Número único do laudo (gerado automaticamente)"
    )
    
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        default='COMPOSITE',
        verbose_name="Tipo de Laudo"
    )
    
    # Dados do produto
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Produto"
    )
    
    production_line = models.ForeignKey(
        ProductionLine,
        on_delete=models.PROTECT,
        verbose_name="Linha de Produção"
    )
    
    # Período de análise
    start_date = models.DateField(
        verbose_name="Data Inicial"
    )
    
    end_date = models.DateField(
        verbose_name="Data Final"
    )
    
    # Amostras relacionadas
    composite_samples = models.ManyToManyField(
        CompositeSample,
        blank=True,
        verbose_name="Amostras Compostas"
    )
    
    spot_analyses = models.ManyToManyField(
        SpotAnalysis,
        blank=True,
        verbose_name="Análises Pontuais"
    )
    
    # Informações do cliente/destinatário
    customer_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nome do Cliente"
    )
    
    customer_document = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="CNPJ/CPF do Cliente"
    )
    
    destination = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Destino"
    )
    
    # Quantidade e lote
    batch_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número do Lote"
    )
    
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Quantidade (ton)"
    )
    
    # Status e aprovação
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name="Status"
    )
    
    # Responsáveis
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_reports',
        verbose_name="Criado por"
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='approved_reports',
        null=True,
        blank=True,
        verbose_name="Aprovado por"
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Aprovação"
    )
    
    # Observações
    observations = models.TextField(
        blank=True,
        verbose_name="Observações"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Arquivo PDF gerado
    pdf_file = models.FileField(
        upload_to='reports/pdfs/',
        null=True,
        blank=True,
        verbose_name="Arquivo PDF"
    )
    
    class Meta:
        verbose_name = "Laudo de Qualidade"
        verbose_name_plural = "Laudos de Qualidade"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Laudo {self.report_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        if not self.report_number:
            self.report_number = self.generate_report_number()
        super().save(*args, **kwargs)
    
    def generate_report_number(self):
        """Gera número único do laudo"""
        year = timezone.now().year
        month = timezone.now().month
        
        # Contar laudos do mês atual
        count = QualityReport.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).count() + 1
        
        return f"LQ{year}{month:02d}{count:04d}"
    
    def approve(self, user):
        """Aprova o laudo"""
        self.status = 'APPROVED'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
    
    def reject(self, user):
        """Rejeita o laudo"""
        self.status = 'REJECTED'
        self.save()
    
    @property
    def is_approved(self):
        return self.status == 'APPROVED'
    
    @property
    def can_be_approved(self):
        return self.status in ['DRAFT', 'PENDING']


class LoadingOrder(models.Model):
    """
    Ordem de carregamento
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('IN_PROGRESS', 'Em Andamento'),
        ('COMPLETED', 'Concluída'),
        ('CANCELLED', 'Cancelada'),
    ]
    
    TRANSPORT_TYPE_CHOICES = [
        ('TRUCK', 'Caminhão'),
        ('TRAIN', 'Trem'),
        ('SHIP', 'Navio'),
        ('OTHER', 'Outro'),
    ]
    
    # Identificação
    order_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número da Ordem",
        help_text="Número único da ordem (gerado automaticamente)"
    )
    
    # Laudo relacionado
    quality_report = models.ForeignKey(
        QualityReport,
        on_delete=models.PROTECT,
        verbose_name="Laudo de Qualidade"
    )
    
    # Informações do transporte
    vehicle_plate = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Placa do Veículo"
    )
    
    driver_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nome do Motorista"
    )
    
    driver_document = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="CPF do Motorista"
    )
    
    transport_type = models.CharField(
        max_length=20,
        choices=TRANSPORT_TYPE_CHOICES,
        default='TRUCK',
        verbose_name="Tipo de Transporte"
    )
    
    # Datas
    scheduled_date = models.DateTimeField(
        verbose_name="Data Programada"
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Início do Carregamento"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fim do Carregamento"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Status"
    )
    
    # Responsável
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Criado por"
    )
    
    # QR Code
    qr_code = models.ImageField(
        upload_to='loading_orders/qr_codes/',
        null=True,
        blank=True,
        verbose_name="QR Code"
    )
    
    # Observações
    observations = models.TextField(
        blank=True,
        verbose_name="Observações"
    )
    
    class Meta:
        verbose_name = "Ordem de Carregamento"
        verbose_name_plural = "Ordens de Carregamento"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ordem {self.order_number} - {self.quality_report.product.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        super().save(*args, **kwargs)
        
        # Gerar QR Code após salvar
        if not self.qr_code:
            self.generate_qr_code()
    
    def generate_order_number(self):
        """Gera número único da ordem"""
        year = timezone.now().year
        month = timezone.now().month
        
        # Contar ordens do mês atual
        count = LoadingOrder.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).count() + 1
        
        return f"OC{year}{month:02d}{count:04d}"
    
    def generate_qr_code(self):
        """Gera QR Code para a ordem"""
        qr_data = {
            'order_number': self.order_number,
            'product': self.quality_report.product.name,
            'quantity': str(self.quality_report.quantity) if self.quality_report.quantity else '',
            'report_number': self.quality_report.report_number,
            'url': f"/loading-order/{self.id}/"
        }
        
        # Criar string do QR Code
        qr_string = f"Ordem: {qr_data['order_number']}\n"
        qr_string += f"Produto: {qr_data['product']}\n"
        qr_string += f"Laudo: {qr_data['report_number']}\n"
        if qr_data['quantity']:
            qr_string += f"Quantidade: {qr_data['quantity']} ton\n"
        qr_string += f"URL: {qr_data['url']}"
        
        # Gerar QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        # Criar imagem
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Salvar em BytesIO
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Salvar no modelo
        filename = f"qr_code_{self.order_number}.png"
        self.qr_code.save(filename, File(buffer), save=False)
        
        # Salvar o modelo novamente
        super().save(update_fields=['qr_code'])
    
    def start_loading(self):
        """Inicia o carregamento"""
        self.status = 'IN_PROGRESS'
        self.started_at = timezone.now()
        self.save()
    
    def complete_loading(self):
        """Completa o carregamento"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()
    
    def cancel_loading(self):
        """Cancela o carregamento"""
        self.status = 'CANCELLED'
        self.save()
    
    @property
    def duration(self):
        """Duração do carregamento"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def is_completed(self):
        return self.status == 'COMPLETED'
    
    @property
    def is_in_progress(self):
        return self.status == 'IN_PROGRESS'


class ReportTemplate(models.Model):
    """
    Template para laudos
    """
    
    name = models.CharField(
        max_length=200,
        verbose_name="Nome do Template"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    
    # Template HTML
    html_template = models.TextField(
        verbose_name="Template HTML",
        help_text="Template HTML com variáveis Django"
    )
    
    # CSS personalizado
    css_styles = models.TextField(
        blank=True,
        verbose_name="Estilos CSS"
    )
    
    # Configurações
    is_default = models.BooleanField(
        default=False,
        verbose_name="Template Padrão"
    )
    
    # Produtos aplicáveis
    products = models.ManyToManyField(
        Product,
        blank=True,
        verbose_name="Produtos Aplicáveis"
    )
    
    class Meta:
        verbose_name = "Template de Laudo"
        verbose_name_plural = "Templates de Laudos"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Garantir que apenas um template seja padrão
        if self.is_default:
            ReportTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
