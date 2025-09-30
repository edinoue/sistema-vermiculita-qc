#!/usr/bin/env python
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.utils import timezone
from quality_control.models import SpotSample, SpotAnalysis
from quality_control.models_production import ProductionRegistration, ProductionLineRegistration, ProductionProductRegistration
from core.models import Shift

print("🧪 Testando lógica do dashboard...")

today = timezone.now().date()
print(f"Data: {today}")

# Verificar turno atual
current_time = timezone.now()
if 6 <= current_time.hour < 18:
    current_shift_name = 'A'
else:
    current_shift_name = 'B'

current_shift = Shift.objects.filter(name=current_shift_name).first()
print(f"Turno atual: {current_shift_name} -> {current_shift}")

# Verificar produção ativa
production = ProductionRegistration.objects.filter(
    date=today,
    shift=current_shift,
    status='ACTIVE'
).first()
print(f"Produção ativa: {production}")

if not production:
    print("❌ Nenhuma produção ativa encontrada!")
    print("Verificando outras produções...")
    
    # Verificar todas as produções
    all_productions = ProductionRegistration.objects.filter(date=today)
    print(f"Produções hoje: {all_productions.count()}")
    for prod in all_productions:
        print(f"  - {prod.date} - Turno {prod.shift.name} - Status: {prod.status}")
    
    # Verificar se há produção com status diferente
    other_production = ProductionRegistration.objects.filter(date=today).first()
    if other_production:
        print(f"Usando produção: {other_production} (status: {other_production.status})")
        production = other_production

if production:
    print(f"\n✅ Usando produção: {production}")
    
    # Verificar linhas na produção
    production_lines = ProductionLineRegistration.objects.filter(
        production=production,
        is_active=True
    )
    print(f"Linhas na produção: {production_lines.count()}")
    
    for line_reg in production_lines:
        line = line_reg.production_line
        print(f"  - Linha: {line.name} (Planta: {line.plant.name})")
        
        # Verificar amostras desta linha
        line_samples = SpotSample.objects.filter(
            production_line=line,
            date=today,
            shift=current_shift
        )
        print(f"    Amostras: {line_samples.count()}")
        
        for sample in line_samples:
            print(f"      - {sample.product.name} - Seq: {sample.sample_sequence}")
            
            # Verificar análises
            analyses = SpotAnalysis.objects.filter(spot_sample=sample)
            print(f"        Análises: {analyses.count()}")
            for analysis in analyses:
                print(f"          - {analysis.property.name}: {analysis.value} {analysis.property.unit} ({analysis.status})")
else:
    print("❌ Nenhuma produção encontrada!")

print("\n✅ Teste concluído!")
