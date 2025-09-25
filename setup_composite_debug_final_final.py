#!/usr/bin/env python
"""
Configuração debug final final de amostras compostas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import AnalysisType, Property, AnalysisTypeProperty

def setup_debug_final_final():
    """Configuração debug final final"""
    print("=== Configuração Debug Final Final Amostras Compostas ===")
    
    # 1. Criar tipo COMPOSTA
    composta_type, created = AnalysisType.objects.get_or_create(
        code='COMPOSTA',
        defaults={
            'name': 'Análise Composta',
            'description': 'Análises que representam 12 horas de produção',
            'frequency_per_shift': 1,
            'is_active': True
        }
    )
    print(f"Tipo COMPOSTA: {'criado' if created else 'já existe'}")
    
    # 2. Configurar propriedades
    properties = Property.objects.filter(is_active=True)
    print(f"Propriedades: {properties.count()}")
    
    for prop in properties:
        atp, created = AnalysisTypeProperty.objects.get_or_create(
            analysis_type=composta_type,
            property=prop,
            defaults={
                'is_required': False,
                'display_order': prop.display_order,
                'is_active': True
            }
        )
        print(f"  {prop.identifier}: {'configurado' if created else 'já configurado'}")
    
    print("=== Configuração debug final finalizada ===")

if __name__ == '__main__':
    setup_debug_final_final()

