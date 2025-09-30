#!/usr/bin/env python
"""
Script para configurar dados básicos de turnos e produção
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from core.models import Shift, Plant, ProductionLine
from quality_control.models import Product, Property, AnalysisType
from django.utils import timezone
from datetime import time

def setup_shifts():
    """Configura turnos padrão"""
    print("🕐 Configurando turnos...")
    
    # Turno A (06:00 - 18:00)
    shift_a, created = Shift.objects.get_or_create(
        name='A',
        defaults={
            'start_time': time(6, 0),
            'end_time': time(18, 0),
            'description': 'Turno A (06:00 - 18:00)'
        }
    )
    
    if created:
        print(f"✅ Turno A criado: {shift_a.name}")
    else:
        print(f"📍 Turno A já existe: {shift_a.name}")
    
    # Turno B (18:00 - 06:00)
    shift_b, created = Shift.objects.get_or_create(
        name='B',
        defaults={
            'start_time': time(18, 0),
            'end_time': time(6, 0),
            'description': 'Turno B (18:00 - 06:00)'
        }
    )
    
    if created:
        print(f"✅ Turno B criado: {shift_b.name}")
    else:
        print(f"📍 Turno B já existe: {shift_b.name}")
    
    return shift_a, shift_b

def setup_analysis_types():
    """Configura tipos de análise padrão"""
    print("\n🔬 Configurando tipos de análise...")
    
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
    
    if created:
        print(f"✅ Análise Pontual criada: {pontual.name}")
    else:
        print(f"📍 Análise Pontual já existe: {pontual.name}")
    
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
    
    if created:
        print(f"✅ Análise Composta criada: {composta.name}")
    else:
        print(f"📍 Análise Composta já existe: {composta.name}")
    
    return pontual, composta

def setup_properties():
    """Configura propriedades padrão"""
    print("\n📊 Configurando propriedades...")
    
    properties_data = [
        {
            'identifier': 'TEOR_VERM',
            'name': 'Teor de Vermiculita',
            'unit': '%',
            'category': 'QUIMICA',
            'display_order': 1
        },
        {
            'identifier': 'RENDIMENTO',
            'name': 'Rendimento',
            'unit': '%',
            'category': 'FISICA',
            'display_order': 2
        },
        {
            'identifier': 'UMIDADE',
            'name': 'Umidade',
            'unit': '%',
            'category': 'FISICA',
            'display_order': 3
        },
        {
            'identifier': 'GRANULOMETRIA',
            'name': 'Granulometria',
            'unit': 'mm',
            'category': 'FISICA',
            'display_order': 4
        }
    ]
    
    for prop_data in properties_data:
        prop, created = Property.objects.get_or_create(
            identifier=prop_data['identifier'],
            defaults={
                'name': prop_data['name'],
                'unit': prop_data['unit'],
                'category': prop_data['category'],
                'display_order': prop_data['display_order'],
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Propriedade criada: {prop.name}")
        else:
            print(f"📍 Propriedade já existe: {prop.name}")

def create_sample_data():
    """Cria dados de exemplo para teste"""
    print("\n🧪 Criando dados de exemplo...")
    
    from quality_control.models import SpotSample, SpotAnalysis
    from django.contrib.auth.models import User
    
    # Obter dados necessários
    shift_a = Shift.objects.get(name='A')
    shift_b = Shift.objects.get(name='B')
    pontual = AnalysisType.objects.get(code='PONTUAL')
    
    # Obter usuário admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_user('admin', 'admin@example.com', 'admin123')
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
    
    # Obter plantas e linhas
    plants = Plant.objects.filter(is_active=True)
    lines = ProductionLine.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    properties = Property.objects.filter(is_active=True)
    
    if not plants.exists() or not lines.exists() or not products.exists() or not properties.exists():
        print("❌ Dados básicos não encontrados. Execute primeiro o setup de plantas e produtos.")
        return
    
    # Criar algumas amostras de exemplo para hoje
    today = timezone.now().date()
    
    # Determinar turno atual
    current_hour = timezone.now().hour
    current_shift = shift_a if 6 <= current_hour < 18 else shift_b
    
    print(f"📅 Criando amostras para {today} - Turno {current_shift.name}")
    
    # Criar amostras para cada linha e produto
    samples_created = 0
    for line in lines[:2]:  # Apenas 2 primeiras linhas
        for product in products:
            # Criar amostra
            sample = SpotSample.objects.create(
                analysis_type=pontual,
                date=today,
                shift=current_shift,
                production_line=line,
                product=product,
                sample_sequence=1,
                sample_time=timezone.now(),
                operator=admin_user,
                observations=f"Amostra de teste para {product.name}",
                status='APPROVED'
            )
            
            # Criar análises para cada propriedade
            for prop in properties:
                # Valores de exemplo baseados no produto
                if prop.identifier == 'TEOR_VERM':
                    value = 85.5 if 'CONC' in product.code else 78.2
                elif prop.identifier == 'RENDIMENTO':
                    value = 92.3 if 'CONC' in product.code else 88.7
                elif prop.identifier == 'UMIDADE':
                    value = 2.1 if 'CONC' in product.code else 3.5
                else:  # GRANULOMETRIA
                    value = 1.2 if 'CONC' in product.code else 0.8
                
                SpotAnalysis.objects.create(
                    spot_sample=sample,
                    property=prop,
                    value=value,
                    unit=prop.unit,
                    test_method=f"Método padrão para {prop.name}",
                    status='APPROVED'
                )
            
            samples_created += 1
            print(f"  ✅ Amostra criada: {product.name} - {line.name}")
    
    print(f"🎉 {samples_created} amostras de exemplo criadas!")

def main():
    print("🚀 Configurando dados básicos do sistema")
    print("=" * 50)
    
    # Configurar turnos
    shift_a, shift_b = setup_shifts()
    
    # Configurar tipos de análise
    pontual, composta = setup_analysis_types()
    
    # Configurar propriedades
    setup_properties()
    
    # Criar dados de exemplo
    create_sample_data()
    
    print("\n✅ Configuração concluída!")
    print("   Agora o dashboard deve mostrar dados reais.")

if __name__ == '__main__':
    main()
