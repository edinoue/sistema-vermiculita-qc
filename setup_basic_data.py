#!/usr/bin/env python
"""
Script para criar dados básicos necessários para o sistema
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.contrib.auth.models import User
from quality_control.models import AnalysisType, Product, Property
from core.models import Plant, ProductionLine, Shift

def setup_basic_data():
    """Criar dados básicos se não existirem"""
    print("🔧 Configurando dados básicos...")
    
    # Criar tipos de análise
    analysis_types = [
        {'code': 'PONTUAL', 'name': 'Análise Pontual', 'description': 'Análises realizadas diretamente no fluxo de produção'},
        {'code': 'COMPOSTA', 'name': 'Análise Composta', 'description': 'Análises que representam 12 horas de produção'},
    ]
    
    for at_data in analysis_types:
        analysis_type, created = AnalysisType.objects.get_or_create(
            code=at_data['code'],
            defaults=at_data
        )
        if created:
            print(f"✅ Tipo de análise criado: {analysis_type.name}")
        else:
            print(f"ℹ️ Tipo de análise já existe: {analysis_type.name}")
    
    # Criar turnos
    shifts = [
        {'name': 'Manhã', 'start_time': '06:00', 'end_time': '14:00'},
        {'name': 'Tarde', 'start_time': '14:00', 'end_time': '22:00'},
        {'name': 'Noite', 'start_time': '22:00', 'end_time': '06:00'},
    ]
    
    for shift_data in shifts:
        shift, created = Shift.objects.get_or_create(
            name=shift_data['name'],
            defaults=shift_data
        )
        if created:
            print(f"✅ Turno criado: {shift.name}")
        else:
            print(f"ℹ️ Turno já existe: {shift.name}")
    
    # Criar planta primeiro
    plant, created = Plant.objects.get_or_create(
        name='Planta Principal',
        defaults={'description': 'Planta principal de produção'}
    )
    if created:
        print(f"✅ Planta criada: {plant.name}")
    else:
        print(f"ℹ️ Planta já existe: {plant.name}")
    
    # Criar linhas de produção
    lines = [
        {'name': 'Linha 1', 'code': 'L1', 'description': 'Linha de produção principal', 'plant': plant},
        {'name': 'Linha 2', 'code': 'L2', 'description': 'Linha de produção secundária', 'plant': plant},
    ]
    
    for line_data in lines:
        line, created = ProductionLine.objects.get_or_create(
            name=line_data['name'],
            defaults=line_data
        )
        if created:
            print(f"✅ Linha de produção criada: {line.name}")
        else:
            print(f"ℹ️ Linha de produção já existe: {line.name}")
    
    # Criar produtos
    products = [
        {'code': 'VC', 'name': 'Vermiculita Concentrada', 'description': 'Vermiculita concentrada'},
        {'code': 'VE', 'name': 'Vermiculita Expandida', 'description': 'Vermiculita expandida'},
        {'code': 'AM30', 'name': 'AM30', 'description': 'Produto AM30'},
    ]
    
    for product_data in products:
        product, created = Product.objects.get_or_create(
            code=product_data['code'],
            defaults=product_data
        )
        if created:
            print(f"✅ Produto criado: {product.name}")
        else:
            print(f"ℹ️ Produto já existe: {product.name}")
    
    # Criar propriedades
    properties = [
        {'identifier': 'UMIDADE', 'name': 'Umidade', 'unit': '%', 'category': 'FÍSICA', 'data_type': 'DECIMAL'},
        {'identifier': 'TEOR_VERM', 'name': 'Teor de Vermiculita', 'unit': '%', 'category': 'QUÍMICA', 'data_type': 'DECIMAL'},
        {'identifier': 'GRANULOMETRIA', 'name': 'Granulometria', 'unit': 'mm', 'category': 'FÍSICA', 'data_type': 'DECIMAL'},
    ]
    
    for prop_data in properties:
        property, created = Property.objects.get_or_create(
            identifier=prop_data['identifier'],
            defaults=prop_data
        )
        if created:
            print(f"✅ Propriedade criada: {property.name}")
        else:
            print(f"ℹ️ Propriedade já existe: {property.name}")
    
    # Criar usuário admin se não existir
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("✅ Usuário admin criado: admin/admin123")
    else:
        print("ℹ️ Usuário admin já existe")
    
    print("\n🎉 Dados básicos configurados com sucesso!")
    return True

if __name__ == "__main__":
    success = setup_basic_data()
    sys.exit(0 if success else 1)
