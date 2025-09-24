#!/usr/bin/env python
"""
Script para configurar dados iniciais completos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import AnalysisType, Property, AnalysisTypeProperty
from core.models import Plant, ProductionLine, Shift

def setup_complete_initial_data():
    """Configurar dados iniciais completos"""
    print("=== Configurando dados iniciais completos ===")
    
    try:
        # Criar planta padrão
        print("1. Criando planta padrão...")
        plant, created = Plant.objects.get_or_create(
            name='Planta Principal',
            defaults={
                'code': 'PP',
                'description': 'Planta principal de produção',
                'is_active': True
            }
        )
        if created:
            print(f"  ✅ {plant.name} criada")
        else:
            print(f"  ⚠️  {plant.name} já existe")
        
        # Criar linhas de produção
        print("2. Criando linhas de produção...")
        production_lines = [
            {
                'name': 'Linha 1',
                'code': 'L1',
                'description': 'Linha de produção 1',
                'is_active': True
            },
            {
                'name': 'Linha 2',
                'code': 'L2',
                'description': 'Linha de produção 2',
                'is_active': True
            }
        ]
        
        for line_data in production_lines:
            line, created = ProductionLine.objects.get_or_create(
                plant=plant,
                code=line_data['code'],
                defaults=line_data
            )
            if created:
                print(f"  ✅ {line.name} criada")
            else:
                print(f"  ⚠️  {line.name} já existe")
        
        # Criar turnos
        print("3. Criando turnos...")
        shifts_data = [
            {
                'name': 'A',
                'start_time': '07:00',
                'end_time': '19:00',
                'description': 'Turno A (07:00-19:00)'
            },
            {
                'name': 'B',
                'start_time': '19:00',
                'end_time': '07:00',
                'description': 'Turno B (19:00-07:00)'
            }
        ]
        
        for shift_data in shifts_data:
            shift, created = Shift.objects.get_or_create(
                name=shift_data['name'],
                defaults=shift_data
            )
            if created:
                print(f"  ✅ {shift.get_name_display()} criado")
            else:
                print(f"  ⚠️  {shift.get_name_display()} já existe")
        
        # Criar tipos de análise
        print("4. Criando tipos de análise...")
        analysis_types = [
            {
                'name': 'Análise Pontual',
                'code': 'PONTUAL',
                'description': 'Análise realizada diretamente no fluxo de produção',
                'frequency_per_shift': 3,
                'is_active': True
            },
            {
                'name': 'Análise Composta',
                'code': 'COMPOSTA',
                'description': 'Amostra representativa de 12 horas de produção',
                'frequency_per_shift': 1,
                'is_active': True
            }
        ]
        
        for at_data in analysis_types:
            analysis_type, created = AnalysisType.objects.get_or_create(
                code=at_data['code'],
                defaults=at_data
            )
            if created:
                print(f"  ✅ {analysis_type.name} criado")
            else:
                print(f"  ⚠️  {analysis_type.name} já existe")
        
        # Criar propriedades padrão
        print("5. Criando propriedades padrão...")
        default_properties = [
            {
                'identifier': 'UMIDADE',
                'name': 'Umidade',
                'unit': '%',
                'category': 'FISICA',
                'test_method': 'Método padrão',
                'data_type': 'DECIMAL',
                'display_order': 1,
                'description': 'Teor de umidade da amostra',
                'is_active': True
            },
            {
                'identifier': 'DENSIDADE',
                'name': 'Densidade',
                'unit': 'g/cm³',
                'category': 'FISICA',
                'test_method': 'Método padrão',
                'data_type': 'DECIMAL',
                'display_order': 2,
                'description': 'Densidade da amostra',
                'is_active': True
            },
            {
                'identifier': 'GRANULOMETRIA',
                'name': 'Granulometria',
                'unit': 'mm',
                'category': 'GRANULOMETRIA',
                'test_method': 'Método padrão',
                'data_type': 'DECIMAL',
                'display_order': 3,
                'description': 'Distribuição granulométrica',
                'is_active': True
            }
        ]
        
        for prop_data in default_properties:
            property, created = Property.objects.get_or_create(
                identifier=prop_data['identifier'],
                defaults=prop_data
            )
            if created:
                print(f"  ✅ {property.name} criada")
            else:
                print(f"  ⚠️  {property.name} já existe")
        
        print("\n=== Configuração concluída! ===")
        
    except Exception as e:
        print(f"Erro durante a configuração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    setup_complete_initial_data()
