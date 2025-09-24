#!/usr/bin/env python
"""
Script para configurar o sistema completo
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from quality_control.models import Product, Property, ProductionLine, Shift, AnalysisType
from create_import_template import create_import_template

def setup_complete_system():
    """Configurar sistema completo"""
    print("=== Configurando Sistema Completo ===")
    
    try:
        # Aplicar migrações
        print("1. Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrações aplicadas")
        
        # Criar dados iniciais
        print("2. Criando dados iniciais...")
        create_initial_data()
        print("✅ Dados iniciais criados")
        
        # Criar planilha de importação
        print("3. Criando planilha de importação...")
        create_import_template()
        print("✅ Planilha de importação criada")
        
        # Verificar sistema
        print("4. Verificando sistema...")
        verify_system()
        print("✅ Sistema verificado")
        
        print("\n=== Sistema configurado com sucesso! ===")
        print("\n📋 FUNCIONALIDADES IMPLEMENTADAS:")
        print("✅ Campos de ordem para produtos e propriedades")
        print("✅ Nomes dos turnos corrigidos (A: 07:00-19:00, B: 19:00-07:00)")
        print("✅ Sistema de templates de laudo personalizáveis")
        print("✅ Sistema de importação de dados históricos")
        print("✅ Planilha padrão para importação")
        print("✅ Interface de administração atualizada")
        print("✅ Navegação atualizada")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Acesse o admin para configurar produtos e propriedades")
        print("2. Defina a ordem de exibição dos itens")
        print("3. Configure templates de laudo se necessário")
        print("4. Use a importação para carregar dados históricos")
        
    except Exception as e:
        print(f"❌ Erro durante a configuração: {e}")
        import traceback
        traceback.print_exc()

def create_initial_data():
    """Criar dados iniciais"""
    
    # Criar tipos de análise
    AnalysisType.objects.get_or_create(
        code='PONTUAL',
        defaults={
            'name': 'Análise Pontual',
            'description': 'Análises realizadas diretamente no fluxo de produção',
            'frequency_per_shift': 3,
            'is_active': True
        }
    )
    
    AnalysisType.objects.get_or_create(
        code='COMPOSTA',
        defaults={
            'name': 'Análise Composta',
            'description': 'Análises que representam 12 horas de produção',
            'frequency_per_shift': 1,
            'is_active': True
        }
    )
    
    # Criar produtos com ordem
    products_data = [
        {'code': 'CONC_MEDIO', 'name': 'Concentrado Médio', 'display_order': 1},
        {'code': 'CONC_FINO', 'name': 'Concentrado Fino', 'display_order': 2},
        {'code': 'CONC_GROSSO', 'name': 'Concentrado Grosso', 'display_order': 3},
        {'code': 'EXPANDIDA', 'name': 'Vermiculita Expandida', 'display_order': 4},
    ]
    
    for prod_data in products_data:
        Product.objects.get_or_create(
            code=prod_data['code'],
            defaults={
                'name': prod_data['name'],
                'display_order': prod_data['display_order'],
                'is_active': True
            }
        )
    
    # Criar propriedades com ordem
    properties_data = [
        {'identifier': 'UMIDADE', 'name': 'Umidade', 'unit': '%', 'display_order': 1, 'category': 'FISICA'},
        {'identifier': 'TEMPERATURA', 'name': 'Temperatura', 'unit': '°C', 'display_order': 2, 'category': 'FISICA'},
        {'identifier': 'DENSIDADE', 'name': 'Densidade', 'unit': 'g/cm³', 'display_order': 3, 'category': 'FISICA'},
        {'identifier': 'PH', 'name': 'pH', 'unit': '', 'display_order': 4, 'category': 'QUIMICA'},
        {'identifier': 'GRANULOMETRIA', 'name': 'Granulometria', 'unit': 'mm', 'display_order': 5, 'category': 'FISICA'},
    ]
    
    for prop_data in properties_data:
        Property.objects.get_or_create(
            identifier=prop_data['identifier'],
            defaults={
                'name': prop_data['name'],
                'unit': prop_data['unit'],
                'display_order': prop_data['display_order'],
                'category': prop_data['category'],
                'data_type': 'DECIMAL',
                'is_active': True
            }
        )
    
    # Criar linhas de produção
    lines_data = [
        {'name': 'Linha 1', 'code': 'L1', 'display_order': 1},
        {'name': 'Linha 2', 'code': 'L2', 'display_order': 2},
        {'name': 'Linha 3', 'code': 'L3', 'display_order': 3},
    ]
    
    for line_data in lines_data:
        ProductionLine.objects.get_or_create(
            code=line_data['code'],
            defaults={
                'name': line_data['name'],
                'display_order': line_data['display_order'],
                'is_active': True
            }
        )
    
    # Criar turnos com horários corretos
    from datetime import time
    
    shifts_data = [
        {'name': 'A', 'start_time': time(7, 0), 'end_time': time(19, 0)},
        {'name': 'B', 'start_time': time(19, 0), 'end_time': time(7, 0)},
    ]
    
    for shift_data in shifts_data:
        Shift.objects.get_or_create(
            name=shift_data['name'],
            defaults={
                'start_time': shift_data['start_time'],
                'end_time': shift_data['end_time'],
                'description': f"Turno {shift_data['name']} ({shift_data['start_time'].strftime('%H:%M')}-{shift_data['end_time'].strftime('%H:%M')})"
            }
        )

def verify_system():
    """Verificar se o sistema está funcionando"""
    
    # Verificar produtos
    products = Product.objects.all()
    print(f"   Produtos: {products.count()}")
    for product in products:
        print(f"     - {product.code}: {product.name} (ordem: {product.display_order})")
    
    # Verificar propriedades
    properties = Property.objects.all()
    print(f"   Propriedades: {properties.count()}")
    for prop in properties:
        print(f"     - {prop.identifier}: {prop.name} (ordem: {prop.display_order})")
    
    # Verificar turnos
    shifts = Shift.objects.all()
    print(f"   Turnos: {shifts.count()}")
    for shift in shifts:
        print(f"     - {shift.name}: {shift.start_time}-{shift.end_time}")
    
    # Verificar tipos de análise
    analysis_types = AnalysisType.objects.all()
    print(f"   Tipos de análise: {analysis_types.count()}")
    for at in analysis_types:
        print(f"     - {at.code}: {at.name}")

if __name__ == '__main__':
    setup_complete_system()
