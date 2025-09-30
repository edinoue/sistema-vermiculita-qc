#!/usr/bin/env python
"""
Script para testar o cálculo de status
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import Product, Property, Specification
from quality_control.models_production import SpotAnalysisRegistration
from decimal import Decimal

def test_status_calculation():
    """Testar cálculo de status"""
    
    print("🧪 TESTANDO CÁLCULO DE STATUS")
    print("=" * 40)
    
    # 1. Verificar produtos e propriedades
    products = Product.objects.filter(is_active=True)
    properties = Property.objects.filter(is_active=True)
    
    print(f"📦 Produtos: {products.count()}")
    for product in products:
        print(f"   - {product.name} ({product.code})")
    
    print(f"\n🔬 Propriedades: {properties.count()}")
    for prop in properties:
        print(f"   - {prop.identifier} ({prop.name})")
    
    # 2. Verificar especificações
    specs = Specification.objects.filter(is_active=True)
    print(f"\n📋 Especificações: {specs.count()}")
    for spec in specs:
        print(f"   - {spec.product.code} - {spec.property.identifier}: LSL={spec.lsl}, USL={spec.usl}")
    
    # 3. Verificar análises
    analyses = SpotAnalysisRegistration.objects.all()
    print(f"\n🔬 Análises: {analyses.count()}")
    
    for analysis in analyses:
        print(f"\n📊 Análise {analysis.id}:")
        print(f"   Produto: {analysis.product.name}")
        print(f"   Status atual: {analysis.analysis_result}")
        
        # Verificar especificações para este produto
        product_specs = Specification.objects.filter(product=analysis.product, is_active=True)
        print(f"   Especificações do produto: {product_specs.count()}")
        
        # Verificar resultados
        results = analysis.property_results.all()
        print(f"   Resultados: {results.count()}")
        
        for result in results:
            print(f"      {result.property.identifier}: {result.value}")
            
            # Buscar especificação
            spec = product_specs.filter(property=result.property).first()
            if spec:
                print(f"         Especificação: LSL={spec.lsl}, USL={spec.usl}")
                
                # Testar limites
                if spec.lsl and result.value < spec.lsl:
                    print(f"         ❌ ABAIXO DO LSL!")
                elif spec.usl and result.value > spec.usl:
                    print(f"         ❌ ACIMA DO USL!")
                else:
                    print(f"         ✅ DENTRO DOS LIMITES")
            else:
                print(f"         ⚠️ SEM ESPECIFICAÇÃO")
        
        # Testar cálculo
        print(f"   Testando cálculo...")
        calculated = analysis.calculate_analysis_result()
        print(f"   Status calculado: {calculated}")
        
        if calculated != analysis.analysis_result:
            print(f"   🔄 ATUALIZANDO: {analysis.analysis_result} → {calculated}")
            analysis.analysis_result = calculated
            analysis.save()
        else:
            print(f"   ✅ Status já correto")

if __name__ == '__main__':
    test_status_calculation()

