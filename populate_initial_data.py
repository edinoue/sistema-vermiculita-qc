#!/usr/bin/env python
"""
Script para popular o sistema com dados iniciais
"""

import os
import sys
import django
from datetime import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from core.models import Plant, ProductionLine, Shift
from quality_control.models import Product, Property, ProductPropertyMap, Specification


def create_initial_data():
    print("Criando dados iniciais...")
    
    # Criar turnos
    shift_a, created = Shift.objects.get_or_create(
        name='A',
        defaults={
            'start_time': time(6, 0),
            'end_time': time(18, 0),
            'description': 'Turno diurno'
        }
    )
    if created:
        print(f"✓ Turno {shift_a} criado")
    
    shift_b, created = Shift.objects.get_or_create(
        name='B',
        defaults={
            'start_time': time(18, 0),
            'end_time': time(6, 0),
            'description': 'Turno noturno'
        }
    )
    if created:
        print(f"✓ Turno {shift_b} criado")
    
    # Criar planta
    plant, created = Plant.objects.get_or_create(
        code='VER01',
        defaults={
            'name': 'Planta Vermiculita Principal',
            'description': 'Unidade principal de processamento de vermiculita'
        }
    )
    if created:
        print(f"✓ Planta {plant} criada")
    
    # Criar linhas de produção
    lines_data = [
        {'code': 'L01', 'name': 'Linha de Concentração 1'},
        {'code': 'L02', 'name': 'Linha de Concentração 2'},
        {'code': 'L03', 'name': 'Linha de Expansão'},
    ]
    
    for line_data in lines_data:
        line, created = ProductionLine.objects.get_or_create(
            plant=plant,
            code=line_data['code'],
            defaults={
                'name': line_data['name'],
                'description': f"Linha de produção {line_data['name']}"
            }
        )
        if created:
            print(f"✓ Linha {line} criada")
    
    # Criar produtos
    products_data = [
        {'code': 'VER_CONC', 'name': 'Vermiculita Concentrada'},
        {'code': 'VER_EXP', 'name': 'Vermiculita Expandida'},
        {'code': 'AM30', 'name': 'AM30'},
    ]
    
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            code=product_data['code'],
            defaults={
                'name': product_data['name'],
                'description': f"Produto {product_data['name']}"
            }
        )
        if created:
            print(f"✓ Produto {product} criado")
    
    # Criar propriedades físicas
    physical_properties = [
        {'id': 'UMIDADE', 'name': 'Umidade', 'unit': '%', 'method': 'Estufa 105°C'},
        {'id': 'GRANULOMETRIA', 'name': 'Granulometria', 'unit': 'mesh', 'method': 'Peneiramento'},
        {'id': 'DENSIDADE', 'name': 'Densidade Aparente', 'unit': 'g/cm³', 'method': 'Picnômetro'},
        {'id': 'TEOR_VERM', 'name': 'Teor de Vermiculita', 'unit': '%', 'method': 'Separação Magnética'},
        {'id': 'REND_VOL', 'name': 'Rendimento Volumétrico', 'unit': 'ml/g', 'method': 'Expansão Térmica'},
    ]
    
    for prop_data in physical_properties:
        prop, created = Property.objects.get_or_create(
            identifier=prop_data['id'],
            defaults={
                'name': prop_data['name'],
                'unit': prop_data['unit'],
                'category': 'FISICA',
                'test_method': prop_data['method'],
                'data_type': 'DECIMAL'
            }
        )
        if created:
            print(f"✓ Propriedade física {prop} criada")
    
    # Criar propriedades químicas
    chemical_properties = [
        {'id': 'PH', 'name': 'pH', 'unit': '', 'method': 'pHmetro'},
        {'id': 'CTC', 'name': 'Capacidade de Troca Catiônica', 'unit': 'meq/100g', 'method': 'Acetato de Amônio'},
        {'id': 'CRA', 'name': 'Capacidade de Retenção de Água', 'unit': '%', 'method': 'Centrifugação'},
        {'id': 'CE', 'name': 'Condutividade Elétrica', 'unit': 'mS/cm', 'method': 'Condutivímetro'},
        {'id': 'SIO2', 'name': 'Óxido de Silício (SiO₂)', 'unit': '%', 'method': 'FRX'},
        {'id': 'AL2O3', 'name': 'Óxido de Alumínio (Al₂O₃)', 'unit': '%', 'method': 'FRX'},
        {'id': 'MGO', 'name': 'Óxido de Magnésio (MgO)', 'unit': '%', 'method': 'FRX'},
        {'id': 'FE2O3', 'name': 'Óxido de Ferro (Fe₂O₃)', 'unit': '%', 'method': 'FRX'},
    ]
    
    for prop_data in chemical_properties:
        prop, created = Property.objects.get_or_create(
            identifier=prop_data['id'],
            defaults={
                'name': prop_data['name'],
                'unit': prop_data['unit'],
                'category': 'QUIMICA',
                'test_method': prop_data['method'],
                'data_type': 'DECIMAL'
            }
        )
        if created:
            print(f"✓ Propriedade química {prop} criada")
    
    # Criar mapeamentos produto-propriedade para Vermiculita Concentrada
    ver_conc = Product.objects.get(code='VER_CONC')
    essential_properties = ['UMIDADE', 'GRANULOMETRIA', 'TEOR_VERM', 'PH']
    
    for prop_id in essential_properties:
        prop = Property.objects.get(identifier=prop_id)
        mapping, created = ProductPropertyMap.objects.get_or_create(
            product=ver_conc,
            property=prop,
            defaults={
                'show_in_spot_analysis': True,
                'show_in_composite_sample': True,
                'show_in_dashboard': True,
                'show_in_report': True
            }
        )
        if created:
            print(f"✓ Mapeamento {ver_conc.code} - {prop.identifier} criado")
    
    # Criar especificações para Vermiculita Concentrada
    specifications = [
        {'prop': 'UMIDADE', 'lsl': 0.0, 'target': 8.0, 'usl': 12.0},
        {'prop': 'TEOR_VERM', 'lsl': 85.0, 'target': 92.0, 'usl': None},
        {'prop': 'PH', 'lsl': 6.5, 'target': 7.5, 'usl': 8.5},
    ]
    
    for spec_data in specifications:
        prop = Property.objects.get(identifier=spec_data['prop'])
        spec, created = Specification.objects.get_or_create(
            product=ver_conc,
            property=prop,
            defaults={
                'lsl': spec_data['lsl'],
                'target': spec_data['target'],
                'usl': spec_data['usl']
            }
        )
        if created:
            print(f"✓ Especificação {ver_conc.code} - {prop.identifier} criada")
    
    print("\n✅ Dados iniciais criados com sucesso!")
    print("\nCredenciais de acesso:")
    print("Usuário: admin")
    print("Senha: admin123")
    print("\nAcesse o admin em: http://localhost:8000/admin/")


if __name__ == '__main__':
    create_initial_data()
