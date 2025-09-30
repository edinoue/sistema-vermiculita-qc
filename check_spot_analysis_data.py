#!/usr/bin/env python
"""
Script para verificar dados das análises pontuais no banco
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

def check_spot_analysis_data():
    """Verificar dados das análises pontuais"""
    print("🔍 === Verificando Dados das Análises Pontuais ===")
    
    today = timezone.now().date()
    print(f"📅 Data atual: {today}")
    
    # 1. Verificar amostras pontuais
    print("\n1️⃣ Amostras Pontuais:")
    samples = SpotSample.objects.all()
    print(f"  Total de amostras: {samples.count()}")
    
    for sample in samples[:5]:  # Mostrar apenas as primeiras 5
        print(f"    - ID: {sample.id}")
        print(f"      Produto: {sample.product.name}")
        print(f"      Linha: {sample.production_line.name}")
        print(f"      Data: {sample.date}")
        print(f"      Turno: {sample.shift.name}")
        print(f"      Sequência: {sample.sample_sequence}")
        print(f"      Observações: {sample.observations}")
        print(f"      Horário: {sample.sample_time}")
        print()
    
    # 2. Verificar análises pontuais
    print("\n2️⃣ Análises Pontuais:")
    analyses = SpotAnalysis.objects.all()
    print(f"  Total de análises: {analyses.count()}")
    
    for analysis in analyses[:5]:  # Mostrar apenas as primeiras 5
        print(f"    - ID: {analysis.id}")
        print(f"      Amostra: {analysis.spot_sample.id}")
        print(f"      Propriedade: {analysis.property.name}")
        print(f"      Valor: {analysis.value} {analysis.property.unit}")
        print(f"      Status: {analysis.status}")
        print(f"      Data: {analysis.created_at}")
        print()
    
    # 3. Verificar produtos
    print("\n3️⃣ Produtos:")
    products = Product.objects.all()
    print(f"  Total de produtos: {products.count()}")
    for product in products:
        print(f"    - {product.name} (Ativo: {product.is_active})")
    
    # 4. Verificar propriedades
    print("\n4️⃣ Propriedades:")
    properties = Property.objects.all()
    print(f"  Total de propriedades: {properties.count()}")
    for prop in properties:
        print(f"    - {prop.name} - {prop.unit} (Ativo: {prop.is_active})")
    
    # 5. Verificar linhas de produção
    print("\n5️⃣ Linhas de Produção:")
    lines = ProductionLine.objects.all()
    print(f"  Total de linhas: {lines.count()}")
    for line in lines:
        print(f"    - {line.name} - Planta: {line.plant.name} (Ativo: {line.is_active})")
    
    # 6. Verificar cadastros de produção
    print("\n6️⃣ Cadastros de Produção:")
    productions = ProductionRegistration.objects.all()
    print(f"  Total de produções: {productions.count()}")
    for prod in productions:
        print(f"    - {prod.date} - Turno: {prod.shift.name} - Status: {prod.status}")
    
    # 7. Verificar amostras de hoje
    print("\n7️⃣ Amostras de Hoje:")
    today_samples = SpotSample.objects.filter(date=today)
    print(f"  Amostras hoje: {today_samples.count()}")
    for sample in today_samples:
        print(f"    - {sample.product.name} - Linha: {sample.production_line.name} - Turno: {sample.shift.name}")
    
    # 8. Verificar análises de hoje
    print("\n8️⃣ Análises de Hoje:")
    today_analyses = SpotAnalysis.objects.filter(spot_sample__date=today)
    print(f"  Análises hoje: {today_analyses.count()}")
    for analysis in today_analyses:
        print(f"    - {analysis.spot_sample.product.name} - {analysis.property.name}: {analysis.value} {analysis.property.unit} ({analysis.status})")
    
    print("\n✅ Verificação concluída!")

if __name__ == '__main__':
    check_spot_analysis_data()
