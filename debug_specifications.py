#!/usr/bin/env python
"""
Script para debugar especificações e status
"""

import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🔍 DEBUGANDO ESPECIFICAÇÕES E STATUS")
print("=" * 50)

try:
    import django
    django.setup()
    
    from quality_control.models import SpotAnalysis, Specification, Product, Property
    
    print("✅ Django configurado com sucesso!")
    
    # 1. Verificar especificações
    print("\n1. VERIFICANDO ESPECIFICAÇÕES:")
    
    specs = Specification.objects.all()
    print(f"   Total de especificações: {specs.count()}")
    
    for spec in specs:
        print(f"   - Produto: {spec.product.name}")
        print(f"     Propriedade: {spec.property.name}")
        print(f"     LSL: {spec.lsl}")
        print(f"     USL: {spec.usl}")
        print(f"     Ativa: {spec.is_active}")
        print()
    
    # 2. Verificar análises e seus valores
    print("\n2. VERIFICANDO ANÁLISES:")
    
    analyses = SpotAnalysis.objects.all()[:5]
    for analysis in analyses:
        print(f"   Análise {analysis.id}:")
        print(f"     Produto: {analysis.product.name}")
        print(f"     Propriedade: {analysis.property.name}")
        print(f"     Valor: {analysis.value}")
        print(f"     Status: {analysis.status}")
        
        # Verificar se há especificação para esta combinação
        try:
            spec = Specification.objects.get(
                product=analysis.product, 
                property=analysis.property, 
                is_active=True
            )
            print(f"     Especificação encontrada:")
            print(f"       LSL: {spec.lsl}")
            print(f"       USL: {spec.usl}")
            
            # Verificar se o valor deveria ser reprovado
            if spec.lsl is not None and analysis.value < spec.lsl:
                print(f"       ❌ VALOR ABAIXO DO LSL: {analysis.value} < {spec.lsl}")
            elif spec.usl is not None and analysis.value > spec.usl:
                print(f"       ❌ VALOR ACIMA DO USL: {analysis.value} > {spec.usl}")
            else:
                print(f"       ✅ VALOR DENTRO DOS LIMITES")
                
        except Specification.DoesNotExist:
            print(f"     ❌ Nenhuma especificação encontrada")
        
        print()
    
    # 3. Testar cálculo de status
    print("\n3. TESTANDO CÁLCULO DE STATUS:")
    
    for analysis in analyses:
        calculated_status = analysis.calculate_status()
        print(f"   Análise {analysis.id}: Status atual = {analysis.status}, Calculado = {calculated_status}")
        
        if analysis.status != calculated_status:
            print(f"     ⚠️  DISCREPÂNCIA DETECTADA!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
