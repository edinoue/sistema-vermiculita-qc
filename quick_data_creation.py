#!/usr/bin/env python
"""
Script rápido para criar dados de teste
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.utils import timezone
from quality_control.models import SpotSample, SpotAnalysis, Product, Property
from core.models import Shift, Plant, ProductionLine
import pytz

# Obter horário correto do Brasil
brazil_tz = pytz.timezone('America/Sao_Paulo')
current_time_brazil = timezone.now().astimezone(brazil_tz)
today = timezone.now().date()

print(f"📅 Data atual: {today}")
print(f"🕐 Horário Brasil: {current_time_brazil}")
print(f"🕐 Hora Brasil: {current_time_brazil.hour}")

# Determinar turno atual
current_shift = None
if 7 <= current_time_brazil.hour < 19:
    current_shift = Shift.objects.filter(name='A').first()
    print("🔍 Turno atual: A (7h-19h)")
else:
    current_shift = Shift.objects.filter(name='B').first()
    print("🔍 Turno atual: B (19h-7h)")

if not current_shift:
    print("❌ Nenhum turno encontrado!")
    exit()

print(f"✅ Turno encontrado: {current_shift.name}")

# Verificar se já há dados do turno atual
existing_samples = SpotSample.objects.filter(date=today, shift=current_shift)
print(f"📊 Amostras existentes do turno atual: {existing_samples.count()}")

if existing_samples.exists():
    print("✅ Já existem amostras do turno atual")
    for sample in existing_samples:
        print(f"  - {sample.product.name} - {sample.production_line.name}")
else:
    print("🔧 Criando dados de teste...")
    
    # Garantir que temos plantas e linhas
    plant, created = Plant.objects.get_or_create(
        name="Módulo I",
        defaults={'is_active': True}
    )
    print(f"🏭 Planta: {plant.name} ({'criada' if created else 'existente'})")
    
    line, created = ProductionLine.objects.get_or_create(
        name="Filial 04",
        plant=plant,
        defaults={'is_active': True}
    )
    print(f"🏭 Linha: {line.name} ({'criada' if created else 'existente'})")
    
    # Garantir que temos produtos
    products = []
    product_names = ["Vermiculita 1", "Vermiculita 2", "Vermiculita 3", "Vermiculita 4"]
    
    for name in product_names:
        product, created = Product.objects.get_or_create(
            name=name,
            defaults={'is_active': True}
        )
        products.append(product)
        print(f"📦 Produto: {product.name} ({'criado' if created else 'existente'})")
    
    # Garantir que temos propriedades
    properties = []
    property_data = [
        {"name": "Teor de Vermiculita", "unit": "%", "display_order": 1},
        {"name": "Rendimento na Expansão", "unit": "kg/m³", "display_order": 2},
    ]
    
    for prop_data in property_data:
        prop, created = Property.objects.get_or_create(
            name=prop_data["name"],
            defaults={
                'unit': prop_data["unit"],
                'display_order': prop_data["display_order"],
                'is_active': True
            }
        )
        properties.append(prop)
        print(f"🔬 Propriedade: {prop.name} ({'criada' if created else 'existente'})")
    
    # Criar amostras do turno atual
    print(f"🔧 Criando amostras do turno {current_shift.name}...")
    
    for i, product in enumerate(products):
        # Criar amostra
        sample = SpotSample.objects.create(
            product=product,
            production_line=line,
            shift=current_shift,
            date=today,
            sample_sequence=i + 1,
            observations=f"Amostra {i + 1} do turno {current_shift.name}",
            sample_time=timezone.now().time()
        )
        print(f"  ✅ Amostra criada: {product.name} - Seq: {sample.sample_sequence}")
        
        # Criar análises para cada propriedade
        for j, prop in enumerate(properties):
            # Valores de exemplo
            if prop.name == "Teor de Vermiculita":
                value = f"{85 + (i * 2) + (j * 1)}"  # 85-90%
                status = "APPROVED" if 85 <= float(value) <= 95 else "REJECTED"
            else:  # Rendimento na Expansão
                value = f"{1200 + (i * 50) + (j * 25)}"  # 1200-1350 kg/m³
                status = "APPROVED" if 1200 <= float(value) <= 1400 else "REJECTED"
            
            analysis = SpotAnalysis.objects.create(
                spot_sample=sample,
                property=prop,
                value=value,
                status=status
            )
            print(f"    - {prop.name}: {value} {prop.unit} ({status})")
    
    print(f"🎉 Dados do turno {current_shift.name} criados com sucesso!")

# Verificar dados criados
print(f"\n📊 Verificando dados criados...")
created_samples = SpotSample.objects.filter(date=today, shift=current_shift)
print(f"  Amostras do turno atual: {created_samples.count()}")

for sample in created_samples:
    analyses = SpotAnalysis.objects.filter(spot_sample=sample)
    print(f"    - {sample.product.name} - {analyses.count()} análises")
    for analysis in analyses:
        print(f"      {analysis.property.name}: {analysis.value} {analysis.property.unit} ({analysis.status})")

print(f"\n✅ Processo concluído!")
