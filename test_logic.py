#!/usr/bin/env python
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models_production import ProductionRegistration, ProductionLineRegistration, ProductionProductRegistration
from core.models import Shift
from django.utils import timezone

print("🔍 Testando Lógica do Dashboard...")

# Obter turno atual
current_time = timezone.now()
if 6 <= current_time.hour < 18:
    current_shift = Shift.objects.filter(name='A').first()
else:
    current_shift = Shift.objects.filter(name='B').first()

print(f"Turno: {current_shift}")

# Obter produção ativa
today = timezone.now().date()
production = ProductionRegistration.objects.filter(
    date=today,
    shift=current_shift,
    status='ACTIVE'
).first()

print(f"Produção: {production}")

if production:
    # Obter linhas de produção cadastradas
    production_lines = ProductionLineRegistration.objects.filter(
        production=production,
        is_active=True
    ).select_related('production_line__plant')
    
    print(f"Linhas cadastradas: {production_lines.count()}")
    
    # Agrupar por planta
    plants_dict = {}
    for line_reg in production_lines:
        plant = line_reg.production_line.plant
        if plant.id not in plants_dict:
            plants_dict[plant.id] = {
                'plant': plant,
                'production_lines': [],
                'products': []
            }
        plants_dict[plant.id]['production_lines'].append(line_reg.production_line)
        print(f"  - {line_reg.production_line.name} ({plant.name})")
    
    print(f"Plantas encontradas: {len(plants_dict)}")
    
    # Obter produtos cadastrados
    production_products = ProductionProductRegistration.objects.filter(
        production=production,
        is_active=True
    ).select_related('product')
    
    print(f"Produtos cadastrados: {production_products.count()}")
    for prod_reg in production_products:
        print(f"  - {prod_reg.product.name}")
    
    # Testar agrupamento por planta
    for plant_id, plant_data in plants_dict.items():
        plant = plant_data['plant']
        print(f"\nPlanta: {plant.name}")
        print(f"  Linhas: {len(plant_data['production_lines'])}")
        
        # Filtrar produtos para esta planta
        plant_products = []
        for prod_reg in production_products:
            # Verificar se o produto tem amostras nesta planta
            from quality_control.models import SpotSample
            has_samples = SpotSample.objects.filter(
                production_line__plant=plant,
                product=prod_reg.product,
                date=today,
                shift=current_shift
            ).exists()
            
            if has_samples:
                plant_products.append(prod_reg.product)
        
        print(f"  Produtos com amostras: {len(plant_products)}")
        for product in plant_products:
            print(f"    - {product.name}")

else:
    print("❌ Nenhuma produção encontrada!")

print("✅ Teste concluído!")
