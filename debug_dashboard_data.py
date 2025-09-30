#!/usr/bin/env python
"""
Script para debugar por que o dashboard não encontra dados
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.utils import timezone
from quality_control.models import SpotSample, SpotAnalysis, Product, Property
from quality_control.models_production import ProductionRegistration, ProductionLineRegistration, ProductionProductRegistration
from core.models import Shift, Plant, ProductionLine

def debug_dashboard_data():
    """Debugar dados do dashboard"""
    print("🔍 === DEBUG DASHBOARD DATA ===")
    
    today = timezone.now().date()
    print(f"📅 Data atual: {today}")
    
    # 1. Verificar TODAS as amostras pontuais
    print("\n1️⃣ TODAS as amostras pontuais:")
    all_samples = SpotSample.objects.all()
    print(f"  Total: {all_samples.count()}")
    
    for sample in all_samples:
        print(f"    ID: {sample.id}")
        print(f"    Produto: {sample.product.name}")
        print(f"    Linha: {sample.production_line.name}")
        print(f"    Planta: {sample.production_line.plant.name}")
        print(f"    Data: {sample.date}")
        print(f"    Turno: {sample.shift.name}")
        print(f"    Sequência: {sample.sample_sequence}")
        print(f"    Observações: {sample.observations}")
        print(f"    Horário: {sample.sample_time}")
        print(f"    Criado em: {sample.created_at}")
        print()
    
    # 2. Verificar amostras de hoje
    print("\n2️⃣ Amostras de hoje:")
    today_samples = SpotSample.objects.filter(date=today)
    print(f"  Total: {today_samples.count()}")
    
    for sample in today_samples:
        print(f"    ID: {sample.id} - {sample.product.name} - {sample.production_line.name}")
    
    # 3. Verificar análises
    print("\n3️⃣ TODAS as análises:")
    all_analyses = SpotAnalysis.objects.all()
    print(f"  Total: {all_analyses.count()}")
    
    for analysis in all_analyses:
        print(f"    ID: {analysis.id}")
        print(f"    Amostra: {analysis.spot_sample.id}")
        print(f"    Produto: {analysis.spot_sample.product.name}")
        print(f"    Propriedade: {analysis.property.name}")
        print(f"    Valor: {analysis.value} {analysis.property.unit}")
        print(f"    Status: {analysis.status}")
        print(f"    Data: {analysis.created_at}")
        print()
    
    # 4. Verificar turnos
    print("\n4️⃣ Turnos:")
    shifts = Shift.objects.all()
    for shift in shifts:
        print(f"    {shift.name}: {shift.start_time} - {shift.end_time}")
    
    # 5. Verificar linhas de produção
    print("\n5️⃣ Linhas de produção:")
    lines = ProductionLine.objects.all()
    for line in lines:
        print(f"    {line.name} - Planta: {line.plant.name} - Ativo: {line.is_active}")
    
    # 6. Verificar produtos
    print("\n6️⃣ Produtos:")
    products = Product.objects.all()
    for product in products:
        print(f"    {product.name} - Ativo: {product.is_active}")
    
    # 7. Verificar propriedades
    print("\n7️⃣ Propriedades:")
    properties = Property.objects.all()
    for prop in properties:
        print(f"    {prop.name} - {prop.unit} - Ativo: {prop.is_active}")
    
    # 8. Testar a lógica do dashboard
    print("\n8️⃣ Testando lógica do dashboard:")
    
    # Buscar amostras como o dashboard faz
    all_samples_dashboard = SpotSample.objects.filter(date=today).select_related(
        'product', 'production_line', 'production_line__plant', 'shift'
    ).order_by('production_line', 'product', '-sample_sequence')
    
    print(f"  Amostras encontradas pelo dashboard: {all_samples_dashboard.count()}")
    
    for sample in all_samples_dashboard:
        print(f"    {sample.product.name} - {sample.production_line.name} - {sample.shift.name}")
        
        # Buscar análises
        analyses = SpotAnalysis.objects.filter(spot_sample=sample)
        print(f"      Análises: {analyses.count()}")
        
        for analysis in analyses:
            print(f"        {analysis.property.name}: {analysis.value} {analysis.property.unit} ({analysis.status})")
    
    # 9. Verificar se há dados de outras datas
    print("\n9️⃣ Amostras de outras datas:")
    other_samples = SpotSample.objects.exclude(date=today)
    print(f"  Total: {other_samples.count()}")
    
    for sample in other_samples[:5]:  # Mostrar apenas 5
        print(f"    {sample.date} - {sample.product.name} - {sample.production_line.name}")
    
    print("\n✅ Debug concluído!")

if __name__ == '__main__':
    debug_dashboard_data()