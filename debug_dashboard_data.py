#!/usr/bin/env python
"""
Script para debugar dados do dashboard
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.utils import timezone
from quality_control.models import SpotSample, SpotAnalysis, Property, Product
from quality_control.models_production import ProductionRegistration, ProductionLineRegistration, ProductionProductRegistration
from core.models import Shift, Plant, ProductionLine

def debug_dashboard_data():
    """Debugar dados do dashboard"""
    print("🔍 === Debug Dashboard Data ===")
    
    today = timezone.now().date()
    print(f"📅 Data: {today}")
    
    # 1. Verificar turnos
    print("\n1️⃣ Verificando turnos...")
    shifts = Shift.objects.all()
    print(f"  Turnos encontrados: {shifts.count()}")
    for shift in shifts:
        print(f"    - {shift.name}: {shift.start_time} - {shift.end_time}")
    
    # 2. Verificar turno atual
    current_time = timezone.now()
    if 6 <= current_time.hour < 18:
        current_shift_name = 'A'
    else:
        current_shift_name = 'B'
    
    current_shift = Shift.objects.filter(name=current_shift_name).first()
    print(f"  Turno atual: {current_shift_name} -> {current_shift}")
    
    # 3. Verificar produção
    print("\n2️⃣ Verificando produção...")
    production = ProductionRegistration.objects.filter(
        date=today,
        shift=current_shift,
        status='ACTIVE'
    ).first()
    print(f"  Produção ativa: {production}")
    
    if production:
        print(f"    - Operador: {production.operator}")
        print(f"    - Status: {production.status}")
        print(f"    - Observações: {production.observations}")
    
    # 4. Verificar linhas de produção
    print("\n3️⃣ Verificando linhas de produção...")
    if production:
        lines = ProductionLineRegistration.objects.filter(
            production=production,
            is_active=True
        ).select_related('production_line__plant')
        print(f"  Linhas cadastradas: {lines.count()}")
        for line_reg in lines:
            line = line_reg.production_line
            plant = line.plant
            print(f"    - {line.name} ({plant.name})")
    else:
        print("  Nenhuma produção ativa encontrada")
    
    # 5. Verificar produtos
    print("\n4️⃣ Verificando produtos...")
    if production:
        products = ProductionProductRegistration.objects.filter(
            production=production,
            is_active=True
        ).select_related('product')
        print(f"  Produtos cadastrados: {products.count()}")
        for prod_reg in products:
            print(f"    - {prod_reg.product.name}")
    else:
        print("  Nenhuma produção ativa encontrada")
    
    # 6. Verificar amostras pontuais
    print("\n5️⃣ Verificando amostras pontuais...")
    samples = SpotSample.objects.filter(date=today, shift=current_shift)
    print(f"  Amostras hoje: {samples.count()}")
    for sample in samples:
        print(f"    - {sample.product.name} - {sample.production_line.name} - Seq: {sample.sample_sequence}")
    
    # 7. Verificar análises
    print("\n6️⃣ Verificando análises...")
    analyses = SpotAnalysis.objects.filter(spot_sample__date=today, spot_sample__shift=current_shift)
    print(f"  Análises hoje: {analyses.count()}")
    for analysis in analyses:
        print(f"    - {analysis.spot_sample.product.name} - {analysis.property.name}: {analysis.value} {analysis.property.unit}")
    
    # 8. Verificar propriedades
    print("\n7️⃣ Verificando propriedades...")
    properties = Property.objects.filter(is_active=True).order_by('display_order')
    print(f"  Propriedades ativas: {properties.count()}")
    for prop in properties:
        print(f"    - {prop.name} ({prop.unit})")
    
    # 9. Testar lógica do dashboard
    print("\n8️⃣ Testando lógica do dashboard...")
    if production and current_shift:
        lines_data = []
        production_lines = ProductionLineRegistration.objects.filter(
            production=production,
            is_active=True
        ).select_related('production_line__plant')
        
        for line_reg in production_lines:
            line = line_reg.production_line
            plant = line.plant
            
            # Buscar amostras desta linha
            line_samples = SpotSample.objects.filter(
                production_line=line,
                date=today,
                shift=current_shift
            )
            print(f"    Linha {line.name}: {line_samples.count()} amostras")
            
            for sample in line_samples:
                analyses = SpotAnalysis.objects.filter(spot_sample=sample)
                print(f"      Amostra {sample.sample_sequence}: {analyses.count()} análises")
    
    print("\n✅ Debug concluído!")

if __name__ == '__main__':
    debug_dashboard_data()
