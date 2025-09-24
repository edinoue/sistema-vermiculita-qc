"""
Modelos base compartilhados entre os apps do sistema
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo abstrato que adiciona campos de timestamp
    """
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        abstract = True


class AuditModel(TimeStampedModel):
    """
    Modelo abstrato que adiciona campos de auditoria
    """
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='%(class)s_created',
        verbose_name='Criado por',
        null=True, 
        blank=True
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='%(class)s_updated',
        verbose_name='Atualizado por',
        null=True, 
        blank=True
    )
    
    class Meta:
        abstract = True


class Plant(AuditModel):
    """
    Modelo para representar plantas/unidades de produção
    """
    name = models.CharField('Nome', max_length=100, unique=True)
    code = models.CharField('Código', max_length=20, unique=True)
    description = models.TextField('Descrição', blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Planta'
        verbose_name_plural = 'Plantas'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ProductionLine(AuditModel):
    """
    Modelo para representar linhas de produção
    """
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, verbose_name='Planta')
    name = models.CharField('Nome', max_length=100)
    code = models.CharField('Código', max_length=20)
    description = models.TextField('Descrição', blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    qr_code_url = models.URLField('URL do QR Code', blank=True)
    
    class Meta:
        verbose_name = 'Linha de Produção'
        verbose_name_plural = 'Linhas de Produção'
        ordering = ['plant', 'name']
        unique_together = [['plant', 'code']]
    
    def __str__(self):
        return f"{self.plant.code} - {self.name}"


class Shift(models.Model):
    """
    Modelo para representar turnos de trabalho
    """
    SHIFT_CHOICES = [
        ('A', 'Turno A (07:00-19:00)'),
        ('B', 'Turno B (19:00-07:00)'),
    ]
    
    name = models.CharField('Nome', max_length=1, choices=SHIFT_CHOICES, unique=True)
    start_time = models.TimeField('Horário de Início')
    end_time = models.TimeField('Horário de Fim')
    description = models.TextField('Descrição', blank=True)
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['name']
    
    def __str__(self):
        return f"Turno {self.name}"


class UserProfile(AuditModel):
    """
    Extensão do modelo User do Django para informações adicionais
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('QA', 'Controle de Qualidade'),
        ('OPERATOR', 'Operador'),
        ('VIEWER', 'Visualizador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuário')
    role = models.CharField('Perfil', max_length=20, choices=ROLE_CHOICES, default='VIEWER')
    phone = models.CharField('Telefone', max_length=20, blank=True)
    plants = models.ManyToManyField(Plant, verbose_name='Plantas', blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuário'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"


class ChangeLog(models.Model):
    """
    Modelo para registrar alterações importantes no sistema
    """
    ACTION_CHOICES = [
        ('CREATE', 'Criação'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Exclusão'),
        ('APPROVE', 'Aprovação'),
        ('REJECT', 'Rejeição'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuário')
    action = models.CharField('Ação', max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField('Modelo', max_length=100)
    object_id = models.PositiveIntegerField('ID do Objeto')
    object_repr = models.CharField('Representação do Objeto', max_length=200)
    changes = models.JSONField('Alterações', default=dict)
    justification = models.TextField('Justificativa', blank=True)
    timestamp = models.DateTimeField('Data/Hora', default=timezone.now)
    ip_address = models.GenericIPAddressField('Endereço IP', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Log de Alteração'
        verbose_name_plural = 'Logs de Alteração'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.model_name} #{self.object_id}"
