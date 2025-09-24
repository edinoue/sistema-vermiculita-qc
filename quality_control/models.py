"""
Modelos para o sistema de controle de qualidade
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

from core.models import AuditModel, Plant, ProductionLine, Shift


class AnalysisType(models.Model):
    """
    Tipos de análise (Pontual, Composta, etc.)
    """
    name = models.CharField('Nome', max_length=100, unique=True)
    code = models.CharField('Código', max_length=20, unique=True)
    description = models.TextField('Descrição', blank=True)
    frequency_per_shift = models.PositiveIntegerField('Frequência por Turno', default=1)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Tipo de Análise'
        verbose_name_plural = 'Tipos de Análise'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Product(AuditModel):
    """
    Modelo para representar produtos (Vermiculita Concentrada, Expandida, AM30, etc.)
    """
    name = models.CharField('Nome', max_length=100, unique=True)
    code = models.CharField('Código', max_length=20, unique=True)
    description = models.TextField('Descrição', blank=True)
    display_order = models.PositiveIntegerField('Ordem de Exibição', default=0, help_text='Ordem em que o produto aparece nas listas')
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Property(AuditModel):
    """
    Modelo para representar propriedades/variáveis de qualidade
    """
    CATEGORY_CHOICES = [
        ('FISICA', 'Física'),
        ('QUIMICA', 'Química'),
    ]
    
    DATA_TYPE_CHOICES = [
        ('DECIMAL', 'Decimal'),
        ('INTEGER', 'Inteiro'),
        ('TEXT', 'Texto'),
        ('BOOLEAN', 'Sim/Não'),
    ]
    
    identifier = models.CharField('Identificador', max_length=50, unique=True)
    name = models.CharField('Nome de Exibição', max_length=100)
    unit = models.CharField('Unidade de Medida', max_length=20, blank=True)
    category = models.CharField('Categoria', max_length=20, choices=CATEGORY_CHOICES)
    test_method = models.CharField('Método de Ensaio', max_length=100, blank=True)
    data_type = models.CharField('Tipo de Dado', max_length=20, choices=DATA_TYPE_CHOICES, default='DECIMAL')
    display_order = models.PositiveIntegerField('Ordem de Exibição', default=0, help_text='Ordem em que a propriedade aparece nos formulários')
    description = models.TextField('Descrição', blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Propriedade'
        verbose_name_plural = 'Propriedades'
        ordering = ['display_order', 'category', 'name']
    
    def __str__(self):
        return f"{self.identifier} - {self.name}"


class AnalysisTypeProperty(models.Model):
    """
    Configuração de quais propriedades aparecem em cada tipo de análise
    """
    analysis_type = models.ForeignKey(AnalysisType, on_delete=models.CASCADE, verbose_name='Tipo de Análise')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name='Propriedade')
    is_required = models.BooleanField('Obrigatório', default=False)
    display_order = models.PositiveIntegerField('Ordem de Exibição', default=0)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Propriedade do Tipo de Análise'
        verbose_name_plural = 'Propriedades dos Tipos de Análise'
        unique_together = [['analysis_type', 'property']]
        ordering = ['display_order', 'property__name']
    
    def __str__(self):
        return f"{self.analysis_type.name} - {self.property.name}"


class ProductPropertyMap(AuditModel):
    """
    Mapeamento entre produtos e propriedades, definindo onde cada propriedade aparece
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Produto')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name='Propriedade')
    
    # Onde a propriedade aparece
    show_in_spot_analysis = models.BooleanField('Análises Pontuais', default=True)
    show_in_composite_sample = models.BooleanField('Amostra Composta', default=True)
    show_in_dashboard = models.BooleanField('Dashboard', default=True)
    show_in_report = models.BooleanField('Laudo', default=True)
    
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Mapa Produto-Propriedade'
        verbose_name_plural = 'Mapas Produto-Propriedade'
        unique_together = [['product', 'property']]
    
    def __str__(self):
        return f"{self.product.code} - {self.property.identifier}"


class Specification(AuditModel):
    """
    Especificações (garantias de qualidade) para produtos e propriedades
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Produto')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name='Propriedade')
    
    # Limites de especificação
    lsl = models.DecimalField('LSL (Limite Inferior)', max_digits=10, decimal_places=4, null=True, blank=True)
    target = models.DecimalField('Valor Alvo', max_digits=10, decimal_places=4, null=True, blank=True)
    usl = models.DecimalField('USL (Limite Superior)', max_digits=10, decimal_places=4, null=True, blank=True)
    
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Especificação'
        verbose_name_plural = 'Especificações'
        unique_together = [['product', 'property']]
    
    def __str__(self):
        return f"{self.product.code} - {self.property.identifier}"
    
    def can_calculate_capability(self):
        """Verifica se é possível calcular Cp/Cpk"""
        return self.lsl is not None and self.usl is not None


class SpotAnalysis(AuditModel):
    """
    Análises realizadas durante o turno (pontuais ou compostas)
    """
    STATUS_CHOICES = [
        ('APPROVED', 'Aprovado'),
        ('ALERT', 'Alerta'),
        ('REJECTED', 'Reprovado'),
    ]
    
    # Identificação
    analysis_type = models.ForeignKey(AnalysisType, on_delete=models.PROTECT, verbose_name='Tipo de Análise')
    date = models.DateField('Data')
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT, verbose_name='Turno')
    production_line = models.ForeignKey(ProductionLine, on_delete=models.PROTECT, verbose_name='Linha de Produção')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Produto')
    property = models.ForeignKey(Property, on_delete=models.PROTECT, verbose_name='Propriedade')
    
    # Dados da análise
    sequence = models.PositiveSmallIntegerField('Sequência', validators=[MinValueValidator(1), MaxValueValidator(3)])
    value = models.DecimalField('Valor', max_digits=10, decimal_places=4)
    unit = models.CharField('Unidade', max_length=20)
    test_method = models.CharField('Método', max_length=100, blank=True)
    
    # Status e ações
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES)
    action_taken = models.TextField('Ação Tomada', blank=True)
    
    # Metadados
    sample_time = models.DateTimeField('Horário da Amostra', default=timezone.now)
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Operador', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Análise Pontual'
        verbose_name_plural = 'Análises Pontuais'
        ordering = ['-date', '-sample_time']
        unique_together = [['analysis_type', 'date', 'shift', 'production_line', 'product', 'property', 'sequence']]
    
    def __str__(self):
        return f"{self.date} - {self.shift} - {self.production_line} - {self.property.identifier} #{self.sequence}"
    
    def save(self, *args, **kwargs):
        """Calcula o status automaticamente baseado nas especificações"""
        if not self.status:
            self.status = self.calculate_status()
        super().save(*args, **kwargs)
    
    def calculate_status(self):
        """Calcula o status baseado nas especificações"""
        try:
            spec = Specification.objects.get(product=self.product, property=self.property, is_active=True)
            
            if spec.lsl is not None and self.value < spec.lsl:
                return 'REJECTED'
            if spec.usl is not None and self.value > spec.usl:
                return 'REJECTED'
            
            # Pode implementar lógica de alerta aqui (ex: próximo aos limites)
            return 'APPROVED'
            
        except Specification.DoesNotExist:
            return 'APPROVED'


class CompositeSample(AuditModel):
    """
    Amostras compostas coletadas ao final do turno
    """
    STATUS_CHOICES = [
        ('APPROVED', 'Aprovado'),
        ('REJECTED', 'Reprovado'),
    ]
    
    # Identificação
    uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
    date = models.DateField('Data')
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT, verbose_name='Turno')
    production_line = models.ForeignKey(ProductionLine, on_delete=models.PROTECT, verbose_name='Linha de Produção')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Produto')
    
    # Dados da coleta
    collection_time = models.DateTimeField('Horário da Coleta')
    quantity_produced = models.DecimalField('Quantidade Produzida (kg)', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status
    status = models.CharField('Status Final', max_length=20, choices=STATUS_CHOICES)
    observations = models.TextField('Observações', blank=True)
    
    # Operador responsável
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Operador', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Amostra Composta'
        verbose_name_plural = 'Amostras Compostas'
        ordering = ['-date', '-collection_time']
        unique_together = [['date', 'shift', 'production_line', 'product']]
    
    def __str__(self):
        return f"{self.date} - {self.shift} - {self.production_line} - {self.product.code}"


class CompositeSampleResult(AuditModel):
    """
    Resultados das análises das amostras compostas
    """
    composite_sample = models.ForeignKey(CompositeSample, on_delete=models.CASCADE, verbose_name='Amostra Composta')
    property = models.ForeignKey(Property, on_delete=models.PROTECT, verbose_name='Propriedade')
    
    value = models.DecimalField('Valor', max_digits=10, decimal_places=4)
    unit = models.CharField('Unidade', max_length=20)
    test_method = models.CharField('Método', max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Resultado da Amostra Composta'
        verbose_name_plural = 'Resultados das Amostras Compostas'
        unique_together = [['composite_sample', 'property']]
    
    def __str__(self):
        return f"{self.composite_sample} - {self.property.identifier}: {self.value}"


class ChemicalAnalysis(AuditModel):
    """
    Análises químicas eventuais e mensais
    """
    TYPE_CHOICES = [
        ('SPORADIC', 'Esporádica'),
        ('MONTHLY', 'Mensal'),
    ]
    
    # Identificação
    type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES)
    date = models.DateField('Data da Análise')
    batch_number = models.CharField('Número do Lote', max_length=50)
    report_number = models.CharField('Número do Laudo', max_length=50, blank=True)
    laboratory = models.CharField('Laboratório', max_length=100, blank=True)
    
    # Relacionamento com amostra composta (se aplicável)
    composite_sample = models.ForeignKey(
        CompositeSample, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Amostra Composta Relacionada'
    )
    
    class Meta:
        verbose_name = 'Análise Química'
        verbose_name_plural = 'Análises Químicas'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.date} - Lote {self.batch_number}"


class ChemicalAnalysisResult(AuditModel):
    """
    Resultados das análises químicas
    """
    chemical_analysis = models.ForeignKey(ChemicalAnalysis, on_delete=models.CASCADE, verbose_name='Análise Química')
    property = models.ForeignKey(Property, on_delete=models.PROTECT, verbose_name='Propriedade')
    
    value = models.DecimalField('Valor', max_digits=10, decimal_places=4)
    unit = models.CharField('Unidade', max_length=20)
    
    class Meta:
        verbose_name = 'Resultado da Análise Química'
        verbose_name_plural = 'Resultados das Análises Químicas'
        unique_together = [['chemical_analysis', 'property']]
    
    def __str__(self):
        return f"{self.chemical_analysis} - {self.property.identifier}: {self.value}"


class QualityReport(AuditModel):
    """
    Laudos de qualidade
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Rascunho'),
        ('APPROVED', 'Aprovado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    # Identificação
    uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
    report_number = models.CharField('Número do Laudo', max_length=50, unique=True)
    date = models.DateField('Data do Laudo')
    
    # Produto e local
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Produto')
    plant = models.ForeignKey(Plant, on_delete=models.PROTECT, verbose_name='Planta')
    
    # Dados do cliente e carregamento
    client_name = models.CharField('Nome do Cliente', max_length=200)
    invoice_number = models.CharField('Número da Nota Fiscal', max_length=50, blank=True)
    driver_name = models.CharField('Nome do Motorista', max_length=100, blank=True)
    truck_plate = models.CharField('Placa do Caminhão', max_length=20, blank=True)
    total_quantity = models.DecimalField('Quantidade Total (kg)', max_digits=10, decimal_places=2)
    
    # Tipo de carregamento
    LOADING_TYPE_CHOICES = [
        ('NATIONAL', 'Nacional'),
        ('EXPORT', 'Exportação'),
    ]
    loading_type = models.CharField('Tipo de Carregamento', max_length=20, choices=LOADING_TYPE_CHOICES)
    
    # Status e controle
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Amostras compostas incluídas no laudo
    composite_samples = models.ManyToManyField(CompositeSample, verbose_name='Amostras Compostas')
    
    # Usuário que aprovou
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='approved_reports',
        verbose_name='Aprovado por'
    )
    approved_at = models.DateTimeField('Aprovado em', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Laudo de Qualidade'
        verbose_name_plural = 'Laudos de Qualidade'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"Laudo {self.report_number} - {self.client_name}"


class LoadingOrder(AuditModel):
    """
    Ordens de carregamento geradas junto com os laudos
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('IN_PROGRESS', 'Em Andamento'),
        ('COMPLETED', 'Concluída'),
        ('CANCELLED', 'Cancelada'),
    ]
    
    # Relacionamento com o laudo
    quality_report = models.OneToOneField(QualityReport, on_delete=models.CASCADE, verbose_name='Laudo de Qualidade')
    
    # Dados da ordem
    order_number = models.CharField('Número da Ordem', max_length=50, unique=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Dados logísticos
    loading_date = models.DateField('Data de Carregamento', null=True, blank=True)
    completion_date = models.DateTimeField('Data de Conclusão', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Ordem de Carregamento'
        verbose_name_plural = 'Ordens de Carregamento'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ordem {self.order_number} - {self.quality_report.client_name}"


# Os modelos de laudos estão em report_models.py para evitar conflitos
