#!/usr/bin/env python
"""
Script para configurar dados iniciais após deploy
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import AnalysisType, Property, AnalysisTypeProperty

def setup_initial_data():
    """Configurar dados iniciais"""
    print("=== Configurando dados iniciais ===")
    
    try:
        # Verificar se os tipos de análise já existem
        pontual = AnalysisType.objects.filter(code='PONTUAL').first()
        composta = AnalysisType.objects.filter(code='COMPOSTA').first()
        
        if not pontual:
            pontual = AnalysisType.objects.create(
                code='PONTUAL',
                name='Análise Pontual',
                description='Análises realizadas diretamente no fluxo de produção',
                frequency_per_shift=3,
                is_active=True
            )
            print("Tipo de análise pontual criado")
        else:
            print("Tipo de análise pontual já existe")
        
        if not composta:
            composta = AnalysisType.objects.create(
                code='COMPOSTA',
                name='Análise Composta',
                description='Análises que representam 12 horas de produção',
                frequency_per_shift=1,
                is_active=True
            )
            print("Tipo de análise composta criado")
        else:
            print("Tipo de análise composta já existe")
        
        # Criar propriedades padrão se não existirem
        properties_data = [
            {
                'identifier': 'UMIDADE',
                'name': 'Umidade',
                'unit': '%',
                'category': 'FISICA',
                'data_type': 'DECIMAL',
                'test_method': 'Método padrão de umidade',
                'description': 'Teor de umidade do material'
            },
            {
                'identifier': 'TEMPERATURA',
                'name': 'Temperatura',
                'unit': '°C',
                'category': 'FISICA',
                'data_type': 'DECIMAL',
                'test_method': 'Termômetro digital',
                'description': 'Temperatura do material'
            },
            {
                'identifier': 'DENSIDADE',
                'name': 'Densidade',
                'unit': 'g/cm³',
                'category': 'FISICA',
                'data_type': 'DECIMAL',
                'test_method': 'Método de densidade',
                'description': 'Densidade do material'
            }
        ]
        
        for prop_data in properties_data:
            prop, created = Property.objects.get_or_create(
                identifier=prop_data['identifier'],
                defaults=prop_data
            )
            print(f"Propriedade {prop.identifier}: {'criada' if created else 'já existe'}")
        
        print("\n=== Configuração concluída! ===")
        
    except Exception as e:
        print(f"Erro durante a configuração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    setup_initial_data()
