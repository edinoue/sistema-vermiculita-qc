#!/usr/bin/env python
"""
Script para aplicar migrações e popular dados iniciais
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from quality_control.models import AnalysisType, Property, AnalysisTypeProperty

def create_analysis_types():
    """Criar tipos de análise padrão"""
    print("Criando tipos de análise padrão...")
    
    # Análise Pontual
    pontual, created = AnalysisType.objects.get_or_create(
        code='PONTUAL',
        defaults={
            'name': 'Análise Pontual',
            'description': 'Análises realizadas diretamente no fluxo de produção',
            'frequency_per_shift': 3,
            'is_active': True
        }
    )
    print(f"Tipo de análise pontual: {'criado' if created else 'já existe'}")
    
    # Análise Composta
    composta, created = AnalysisType.objects.get_or_create(
        code='COMPOSTA',
        defaults={
            'name': 'Análise Composta',
            'description': 'Análises que representam 12 horas de produção',
            'frequency_per_shift': 1,
            'is_active': True
        }
    )
    print(f"Tipo de análise composta: {'criado' if created else 'já existe'}")

def create_default_properties():
    """Criar propriedades padrão"""
    print("Criando propriedades padrão...")
    
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
        },
        {
            'identifier': 'PH',
            'name': 'pH',
            'unit': '',
            'category': 'QUIMICA',
            'data_type': 'DECIMAL',
            'test_method': 'Medidor de pH',
            'description': 'Nível de pH do material'
        },
        {
            'identifier': 'GRANULOMETRIA',
            'name': 'Granulometria',
            'unit': 'mm',
            'category': 'FISICA',
            'data_type': 'DECIMAL',
            'test_method': 'Peneiramento',
            'description': 'Tamanho das partículas'
        }
    ]
    
    for prop_data in properties_data:
        prop, created = Property.objects.get_or_create(
            identifier=prop_data['identifier'],
            defaults=prop_data
        )
        print(f"Propriedade {prop.identifier}: {'criada' if created else 'já existe'}")

def configure_analysis_type_properties():
    """Configurar propriedades para cada tipo de análise"""
    print("Configurando propriedades por tipo de análise...")
    
    try:
        pontual = AnalysisType.objects.get(code='PONTUAL')
        composta = AnalysisType.objects.get(code='COMPOSTA')
        
        # Propriedades para análise pontual
        pontual_properties = ['UMIDADE', 'TEMPERATURA', 'DENSIDADE']
        for i, prop_id in enumerate(pontual_properties):
            try:
                prop = Property.objects.get(identifier=prop_id)
                AnalysisTypeProperty.objects.get_or_create(
                    analysis_type=pontual,
                    property=prop,
                    defaults={
                        'is_required': True,
                        'display_order': i + 1,
                        'is_active': True
                    }
                )
                print(f"Propriedade {prop_id} configurada para análise pontual")
            except Property.DoesNotExist:
                print(f"Propriedade {prop_id} não encontrada")
        
        # Propriedades para análise composta
        composta_properties = ['UMIDADE', 'TEMPERATURA', 'DENSIDADE', 'PH', 'GRANULOMETRIA']
        for i, prop_id in enumerate(composta_properties):
            try:
                prop = Property.objects.get(identifier=prop_id)
                AnalysisTypeProperty.objects.get_or_create(
                    analysis_type=composta,
                    property=prop,
                    defaults={
                        'is_required': prop_id in ['UMIDADE', 'TEMPERATURA'],
                        'display_order': i + 1,
                        'is_active': True
                    }
                )
                print(f"Propriedade {prop_id} configurada para análise composta")
            except Property.DoesNotExist:
                print(f"Propriedade {prop_id} não encontrada")
                
    except AnalysisType.DoesNotExist as e:
        print(f"Erro: {e}")

def main():
    """Função principal"""
    print("=== Aplicando migrações e configurando dados iniciais ===")
    
    try:
        # Aplicar migrações
        print("Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("Migrações aplicadas com sucesso!")
        
        # Criar dados iniciais
        create_analysis_types()
        create_default_properties()
        configure_analysis_type_properties()
        
        print("\n=== Configuração concluída com sucesso! ===")
        print("O sistema está pronto para uso.")
        
    except Exception as e:
        print(f"Erro durante a configuração: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

