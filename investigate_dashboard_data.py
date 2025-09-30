#!/usr/bin/env python
"""
Script para investigar por que o dashboard não encontra os dados existentes
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.utils import timezone
from quality_control.models import SpotSample, SpotAnalysis
from quality_control.models_production import ProductionRegistration, ProductionLineRegistration, ProductionProductRegistration
from core.models import Shift, Plant, ProductionLine

def investigate_dashboard_data():
    """Investigar dados existentes e por que o dashboard não os encontra"""
    print("🔍 === Investigando Dados do Dashboard ===")
    
    today = timezone.now().date()
    print(f"📅 Data atual: {today}")
    
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
    
    # 3. Verificar TODAS as produções (não apenas ativas)
    print("\n2️⃣ Verificando TODAS as produções...")
    all_productions = ProductionRegistration.objects.filter(date=today)
    print(f"  Produções hoje: {all_productions.count()}")
    for prod in all_productions:
        print(f"    - {prod.date} - Turno {prod.shift.name} - Status: {prod.status}")
    
    # 4. Verificar produção ativa para o turno atual
    print("\n3️⃣ Verificando produção ativa para turno atual...")
    active_production = ProductionRegistration.objects.filter(
        date=today,
        shift=current_shift,
        status='ACTIVE'
    ).first()
    print(f"  Produção ativa: {active_production}")
    
    # 5. Verificar TODAS as amostras pontuais
    print("\n4️⃣ Verificando TODAS as amostras pontuais...")
    all_samples = SpotSample.objects.filter(date=today)
    print(f"  Amostras hoje: {all_samples.count()}")
    for sample in all_samples:
        print(f"    - {sample.product.name} - Turno: {sample.shift.name} - Linha: {sample.production_line.name}")
    
    # 6. Verificar amostras do turno atual
    print("\n5️⃣ Verificando amostras do turno atual...")
    current_samples = SpotSample.objects.filter(date=today, shift=current_shift)
    print(f"  Amostras turno atual: {current_samples.count()}")
    for sample in current_samples:
        print(f"    - {sample.product.name} - Linha: {sample.production_line.name}")
    
    # 7. Verificar linhas de produção cadastradas
    print("\n6️⃣ Verificando linhas de produção...")
    all_lines = ProductionLine.objects.all()
    print(f"  Linhas cadastradas: {all_lines.count()}")
    for line in all_lines:
        print(f"    - {line.name} - Planta: {line.plant.name}")
    
    # 8. Verificar linhas na produção ativa
    if active_production:
        print("\n7️⃣ Verificando linhas na produção ativa...")
        production_lines = ProductionLineRegistration.objects.filter(
            production=active_production,
            is_active=True
        )
        print(f"  Linhas na produção ativa: {production_lines.count()}")
        for line_reg in production_lines:
            print(f"    - {line_reg.production_line.name} - Ativa: {line_reg.is_active}")
    else:
        print("\n7️⃣ Nenhuma produção ativa encontrada")
    
    # 9. Verificar produtos na produção ativa
    if active_production:
        print("\n8️⃣ Verificando produtos na produção ativa...")
        production_products = ProductionProductRegistration.objects.filter(
            production=active_production,
            is_active=True
        )
        print(f"  Produtos na produção ativa: {production_products.count()}")
        for prod_reg in production_products:
            print(f"    - {prod_reg.product.name} - Ativo: {prod_reg.is_active}")
    else:
        print("\n8️⃣ Nenhuma produção ativa encontrada")
    
    # 10. Testar lógica do dashboard
    print("\n9️⃣ Testando lógica do dashboard...")
    if active_production:
        lines_data = []
        production_lines = ProductionLineRegistration.objects.filter(
            production=active_production,
            is_active=True
        ).select_related('production_line__plant')
        
        print(f"  Linhas encontradas na produção: {production_lines.count()}")
        
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
    else:
        print("  ❌ Nenhuma produção ativa - dashboard ficará vazio")
    
    # 11. Verificar se há dados de outros turnos
    print("\n🔟 Verificando dados de outros turnos...")
    other_shift = Shift.objects.exclude(name=current_shift_name).first()
    if other_shift:
        other_samples = SpotSample.objects.filter(date=today, shift=other_shift)
        print(f"  Amostras turno {other_shift.name}: {other_samples.count()}")
        
        other_production = ProductionRegistration.objects.filter(
            date=today,
            shift=other_shift,
            status='ACTIVE'
        ).first()
        print(f"  Produção ativa turno {other_shift.name}: {other_production}")
    
    print("\n✅ Investigação concluída!")

if __name__ == '__main__':
    investigate_dashboard_data()
