#!/usr/bin/env python
"""
Script para debugar o sistema de aprovação
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import Product, Property, Specification, SpotAnalysis, CompositeSample, CompositeSampleResult

def debug_approval_system():
    """Debugar o sistema de aprovação"""
    
    print("🔍 DEBUGANDO SISTEMA DE APROVAÇÃO")
    print("=" * 50)
    
    # 1. Verificar se existem especificações
    print("\n1. VERIFICANDO ESPECIFICAÇÕES:")
    specifications = Specification.objects.filter(is_active=True)
    print(f"   Total de especificações ativas: {specifications.count()}")
    
    for spec in specifications:
        print(f"   - {spec.product.code} - {spec.property.identifier}: LSL={spec.lsl}, USL={spec.usl}, Target={spec.target}")
    
    # 2. Verificar análises pontuais recentes
    print("\n2. VERIFICANDO ANÁLISES PONTUAIS RECENTES:")
    spot_analyses = SpotAnalysis.objects.all().order_by('-created_at')[:5]
    print(f"   Total de análises pontuais: {SpotAnalysis.objects.count()}")
    
    for analysis in spot_analyses:
        print(f"   - {analysis.date} - {analysis.property.identifier}: {analysis.value} - Status: {analysis.status}")
        
        # Verificar se há especificação para esta análise
        try:
            spec = Specification.objects.get(
                product=analysis.product, 
                property=analysis.property, 
                is_active=True
            )
            print(f"     Especificação: LSL={spec.lsl}, USL={spec.usl}")
            
            # Testar cálculo manual
            if spec.lsl is not None and analysis.value < spec.lsl:
                print(f"     ❌ DEVERIA SER REJEITADO: {analysis.value} < {spec.lsl}")
            elif spec.usl is not None and analysis.value > spec.usl:
                print(f"     ❌ DEVERIA SER REJEITADO: {analysis.value} > {spec.usl}")
            else:
                print(f"     ✅ CORRETO: {analysis.value} dentro dos limites")
                
        except Specification.DoesNotExist:
            print(f"     ⚠️  NENHUMA ESPECIFICAÇÃO ENCONTRADA")
    
    # 3. Verificar amostras compostas recentes
    print("\n3. VERIFICANDO AMOSTRAS COMPOSTAS RECENTES:")
    composite_samples = CompositeSample.objects.all().order_by('-created_at')[:5]
    print(f"   Total de amostras compostas: {CompositeSample.objects.count()}")
    
    for sample in composite_samples:
        print(f"   - {sample.date} - {sample.product.code}")
        
        # Verificar resultados
        results = CompositeSampleResult.objects.filter(composite_sample=sample)
        print(f"     Resultados: {results.count()}")
        
        for result in results:
            print(f"       - {result.property.identifier}: {result.value} - Status: {result.status}")
            
            # Verificar se há especificação para este resultado
            try:
                spec = Specification.objects.get(
                    product=sample.product, 
                    property=result.property, 
                    is_active=True
                )
                print(f"         Especificação: LSL={spec.lsl}, USL={spec.usl}")
                
                # Testar cálculo manual
                if spec.lsl is not None and result.value < spec.lsl:
                    print(f"         ❌ DEVERIA SER REJEITADO: {result.value} < {spec.lsl}")
                elif spec.usl is not None and result.value > spec.usl:
                    print(f"         ❌ DEVERIA SER REJEITADO: {result.value} > {spec.usl}")
                else:
                    print(f"         ✅ CORRETO: {result.value} dentro dos limites")
                    
            except Specification.DoesNotExist:
                print(f"         ⚠️  NENHUMA ESPECIFICAÇÃO ENCONTRADA")
    
    # 4. Testar criação de especificação para TEOR_VERM
    print("\n4. TESTANDO ESPECIFICAÇÃO PARA TEOR_VERM:")
    try:
        product = Product.objects.get(code='VER_CONC')
        property = Property.objects.get(identifier='TEOR_VERM')
        
        spec, created = Specification.objects.get_or_create(
            product=product,
            property=property,
            defaults={
                'lsl': 82.0,
                'target': 92.0,
                'usl': None,
                'is_active': True
            }
        )
        
        if created:
            print(f"   ✅ Especificação criada: LSL={spec.lsl}, USL={spec.usl}")
        else:
            print(f"   🔄 Especificação já existe: LSL={spec.lsl}, USL={spec.usl}")
            
        # Testar com valor 70
        test_value = 70.0
        print(f"   Testando valor {test_value}:")
        
        if spec.lsl is not None and test_value < spec.lsl:
            print(f"   ❌ DEVERIA SER REJEITADO: {test_value} < {spec.lsl}")
        else:
            print(f"   ✅ APROVADO: {test_value} >= {spec.lsl}")
            
    except Exception as e:
        print(f"   ❌ ERRO: {e}")

if __name__ == '__main__':
    debug_approval_system()




