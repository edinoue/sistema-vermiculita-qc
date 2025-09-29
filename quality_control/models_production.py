"""
Modelos para cadastro de produção
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import ProductionLine, Shift
from .models import Product, AnalysisType

class ProductionRegistration(models.Model):
    """
    Cadastro de produção do turno
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Ativo'),
        ('COMPLETED', 'Finalizado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    # Identificação da produção
    date = models.DateField('Data', default=timezone.now)
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT, verbose_name='Turno')
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Operador')
    
    # Status e observações
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    observations = models.TextField('Observações', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Cadastro de Produção'
        verbose_name_plural = 'Cadastros de Produção'
        ordering = ['-date', '-created_at']
        unique_together = [['date', 'shift']]
    
    def __str__(self):
        return f"Produção - {self.date} - {self.shift.name}"
    
    def get_active_lines(self):
        """Retorna as linhas de produção ativas para esta produção"""
        return self.productionlines.filter(is_active=True)
    
    def get_active_products(self):
        """Retorna os produtos ativos para esta produção"""
        return self.products.filter(is_active=True)


class ProductionLineRegistration(models.Model):
    """
    Linhas de produção registradas para uma produção
    """
    production = models.ForeignKey(ProductionRegistration, on_delete=models.CASCADE, 
                                 related_name='productionlines', verbose_name='Produção')
    production_line = models.ForeignKey(ProductionLine, on_delete=models.PROTECT, 
                                      verbose_name='Linha de Produção')
    is_active = models.BooleanField('Ativa', default=True)
    
    class Meta:
        verbose_name = 'Linha de Produção'
        verbose_name_plural = 'Linhas de Produção'
        unique_together = [['production', 'production_line']]
    
    def __str__(self):
        return f"{self.production} - {self.production_line.name}"


class ProductionProductRegistration(models.Model):
    """
    Produtos registrados para uma produção
    """
    production = models.ForeignKey(ProductionRegistration, on_delete=models.CASCADE, 
                                 related_name='products', verbose_name='Produção')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Produto')
    product_type = models.CharField('Tipo do Produto', max_length=100, blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Produto da Produção'
        verbose_name_plural = 'Produtos da Produção'
        unique_together = [['production', 'product']]
    
    def __str__(self):
        return f"{self.production} - {self.product.name}"


class SpotAnalysisRegistration(models.Model):
    """
    Registro de análise pontual com nova estrutura
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('APPROVED', 'Aprovado'),
        ('REJECTED', 'Reprovado'),
    ]
    
    # Dados básicos
    production = models.ForeignKey(ProductionRegistration, on_delete=models.PROTECT, 
                                verbose_name='Produção')
    date = models.DateField('Data')
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT, verbose_name='Turno')
    production_line = models.ForeignKey(ProductionLine, on_delete=models.PROTECT, 
                                      verbose_name='Local de Produção')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Produto')
    analysis_type = models.ForeignKey(AnalysisType, on_delete=models.PROTECT, 
                                    verbose_name='Tipo de Análise')
    
    # Pontual
    pontual_number = models.PositiveIntegerField('Número da Pontual', choices=[
        (1, '1'),
        (2, '2'),
        (3, '3'),
    ])
    
    # Resultados
    analysis_result = models.CharField('Resultado da Análise', max_length=20, 
                                     choices=STATUS_CHOICES, default='PENDING')
    
    # Timestamps
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Operador')
    
    class Meta:
        verbose_name = 'Registro de Análise Pontual'
        verbose_name_plural = 'Registros de Análise Pontual'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"Análise {self.pontual_number} - {self.product.name} - {self.date}"
    
    def calculate_analysis_result(self):
        """
        Calcula o resultado da análise baseado nas especificações do produto
        """
        from .models import Specification
        
        # Buscar especificações do produto
        specifications = Specification.objects.filter(
            product=self.product,
            is_active=True
        )
        
        if not specifications.exists():
            # Se não há especificações, manter como aprovado
            return 'APPROVED'
        
        # Verificar cada propriedade analisada
        for property_result in self.property_results.all():
            try:
                # Buscar especificação para esta propriedade
                spec = specifications.filter(property=property_result.property).first()
                
                if spec:
                    value = property_result.value
                    
                    # Verificar limites
                    if spec.lsl is not None and value < spec.lsl:
                        return 'REJECTED'  # Abaixo do limite inferior
                    if spec.usl is not None and value > spec.usl:
                        return 'REJECTED'  # Acima do limite superior
                        
            except Exception:
                # Em caso de erro, manter como aprovado
                continue
        
        # Se chegou até aqui, está dentro dos limites
        return 'APPROVED'


class SpotAnalysisPropertyResult(models.Model):
    """
    Resultados das propriedades para uma análise pontual
    """
    analysis = models.ForeignKey(SpotAnalysisRegistration, on_delete=models.CASCADE, 
                               related_name='property_results', verbose_name='Análise')
    property = models.ForeignKey('Property', on_delete=models.PROTECT, verbose_name='Propriedade')
    value = models.DecimalField('Valor', max_digits=10, decimal_places=4)
    unit = models.CharField('Unidade', max_length=20)
    test_method = models.CharField('Método de Teste', max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Resultado de Propriedade'
        verbose_name_plural = 'Resultados de Propriedades'
        unique_together = [['analysis', 'property']]
    
    def __str__(self):
        return f"{self.analysis} - {self.property.name}: {self.value} {self.unit}"
