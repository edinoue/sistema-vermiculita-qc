#!/usr/bin/env python
"""
Script para testar o dashboard de pontuais após as correções
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from quality_control.views import spot_dashboard_view, spot_dashboard_by_plant_view
from core.models import Shift, Plant, ProductionLine
from quality_control.models import SpotSample, Product, Property
from django.utils import timezone

def test_dashboard_data():
    """Testa os dados do dashboard"""
    
    print("🧪 Testando Dashboard de Pontuais")
    print("=" * 40)
    
    # Verificar dados básicos
    print("📊 Dados do Sistema:")
    print(f"  - Turnos: {Shift.objects.count()}")
    print(f"  - Plantas: {Plant.objects.filter(is_active=True).count()}")
    print(f"  - Linhas: {ProductionLine.objects.filter(is_active=True).count()}")
    print(f"  - Produtos: {Product.objects.filter(is_active=True).count()}")
    print(f"  - Propriedades: {Property.objects.filter(is_active=True).count()}")
    
    # Verificar amostras de hoje
    today = timezone.now().date()
    samples_today = SpotSample.objects.filter(date=today)
    print(f"  - Amostras hoje: {samples_today.count()}")
    
    if samples_today.count() > 0:
        print("  📋 Amostras encontradas:")
        for sample in samples_today[:3]:
            print(f"    - {sample.product.name} - {sample.shift.name} - {sample.production_line.name}")
    
    # Testar determinação do turno atual
    current_time = timezone.now()
    print(f"\n🕐 Turno Atual:")
    print(f"  - Hora atual: {current_time.hour}:{current_time.minute}")
    
    if 6 <= current_time.hour < 18:
        current_shift = Shift.objects.filter(name='A').first()
        print(f"  - Turno: A (06:00 - 18:00)")
    else:
        current_shift = Shift.objects.filter(name='B').first()
        print(f"  - Turno: B (18:00 - 06:00)")
    
    print(f"  - Turno encontrado: {current_shift}")
    
    # Testar view do dashboard por linhas
    print(f"\n🔍 Testando Dashboard por Linhas:")
    try:
        factory = RequestFactory()
        request = factory.get('/qc/dashboard/spot/')
        user = User.objects.first()
        if not user:
            user = User.objects.create_user('test', 'test@example.com', 'test123')
        request.user = user
        
        response = spot_dashboard_view(request)
        print(f"  - Status: {response.status_code}")
        
        if response.status_code == 200:
            context = response.context_data
            lines_data = context.get('lines_data', [])
            products = context.get('products', [])
            current_shift_ctx = context.get('current_shift')
            
            print(f"  - Linhas no contexto: {len(lines_data)}")
            print(f"  - Produtos no contexto: {len(products)}")
            print(f"  - Turno no contexto: {current_shift_ctx}")
            
            if lines_data:
                print("  - Dados das linhas:")
                for i, line_data in enumerate(lines_data[:2]):
                    line = line_data['line']
                    products_count = len(line_data['products'])
                    print(f"    {i+1}. {line.name} - {products_count} produtos")
        else:
            print(f"  ❌ Erro na view: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Erro ao testar view: {str(e)}")
    
    # Testar view do dashboard por plantas
    print(f"\n🏭 Testando Dashboard por Plantas:")
    try:
        factory = RequestFactory()
        request = factory.get('/qc/dashboard/spot/by-plant/')
        user = User.objects.first()
        request.user = user
        
        response = spot_dashboard_by_plant_view(request)
        print(f"  - Status: {response.status_code}")
        
        if response.status_code == 200:
            context = response.context_data
            plants_data = context.get('plants_data', [])
            properties = context.get('properties', [])
            current_shift_ctx = context.get('current_shift')
            
            print(f"  - Plantas no contexto: {len(plants_data)}")
            print(f"  - Propriedades no contexto: {len(properties)}")
            print(f"  - Turno no contexto: {current_shift_ctx}")
            
            if plants_data:
                print("  - Dados das plantas:")
                for i, plant_data in enumerate(plants_data):
                    plant = plant_data['plant']
                    products_count = len(plant_data['products'])
                    print(f"    {i+1}. {plant.name} - {products_count} produtos")
        else:
            print(f"  ❌ Erro na view: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Erro ao testar view: {str(e)}")
    
    print(f"\n✅ Teste concluído!")

if __name__ == '__main__':
    test_dashboard_data()
