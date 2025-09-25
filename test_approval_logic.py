#!/usr/bin/env python
"""
Script para testar a lógica de aprovação
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import Product, Property, Specification, SpotAnalysis, CompositeSample, CompositeSampleResult
from decimal import Decimal

def test_approval_logic():
    """Testar a lógica de aprovação"""
    
    print("🧪 TESTANDO LÓGICA DE APROVAÇÃO")
    print("=" * 50)
    
    # 1. Verificar se existe especificação para TEOR_VERM
    print("\n1. VERIFICANDO ESPECIFICAÇÃO PARA TEOR_VERM:")
    try:
        product = Product.objects.get(code='VER_CONC')
        property = Property.objects.get(identifier='TEOR_VERM')
        
        spec, created = Specification.objects.get_or_create(
            product=product,
            property=property,
            defaults={
                'lsl': Decimal('82.0'),
                'target': Decimal('92.0'),
                'usl': None,
                'is_active': True
            }
        )
        
        print(f"   Produto: {product.code} - {product.name}")
        print(f"   Propriedade: {property.identifier} - {property.name}")
        print(f"   Especificação: LSL={spec.lsl}, USL={spec.usl}, Target={spec.target}")
        print(f"   Ativa: {spec.is_active}")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        return
    
    # 2. Testar cálculo de status com valor 70
    print("\n2. TESTANDO CÁLCULO DE STATUS COM VALOR 70:")
    test_value = Decimal('70.0')
    
    print(f"   Valor de teste: {test_value}")
    print(f"   LSL: {spec.lsl}")
    print(f"   USL: {spec.usl}")
    
    # Testar lógica manual
    if spec.lsl is not None and test_value < spec.lsl:
        print(f"   ❌ DEVERIA SER REJEITADO: {test_value} < {spec.lsl}")
    elif spec.usl is not None and test_value > spec.usl:
        print(f"   ❌ DEVERIA SER REJEITADO: {test_value} > {spec.usl}")
    else:
        print(f"   ✅ APROVADO: {test_value} dentro dos limites")
    
    # 3. Testar criação de análise pontual
    print("\n3. TESTANDO CRIAÇÃO DE ANÁLISE PONTUAL:")
    try:
        from quality_control.models import AnalysisType, Shift, ProductionLine
        from django.utils import timezone
        
        # Buscar dados necessários
        analysis_type = AnalysisType.objects.get(code='PONTUAL')
        shift = Shift.objects.first()
        production_line = ProductionLine.objects.first()
        
        # Criar análise pontual
        analysis = SpotAnalysis.objects.create(
            analysis_type=analysis_type,
            date=timezone.now().date(),
            product=product,
            production_line=production_line,
            shift=shift,
            sample_time=timezone.now(),
            sequence=1,
            property=property,
            value=test_value,
            unit=property.unit,
            test_method='Teste manual'
        )
        
        print(f"   ✅ Análise criada com ID: {analysis.id}")
        print(f"   Status calculado: {analysis.status}")
        print(f"   Valor: {analysis.value}")
        
        # Verificar se o status foi calculado corretamente
        if analysis.status == 'REJECTED':
            print(f"   ✅ CORRETO: Análise foi rejeitada como esperado")
        else:
            print(f"   ❌ PROBLEMA: Análise foi aprovada quando deveria ser rejeitada")
            
    except Exception as e:
        print(f"   ❌ ERRO ao criar análise pontual: {e}")
    
    # 4. Testar criação de resultado de amostra composta
    print("\n4. TESTANDO CRIAÇÃO DE RESULTADO DE AMOSTRA COMPOSTA:")
    try:
        # Criar amostra composta
        composite_sample = CompositeSample.objects.create(
            date=timezone.now().date(),
            shift=shift,
            production_line=production_line,
            product=product,
            collection_time=timezone.now(),
            status='APPROVED'
        )
        
        # Criar resultado
        result = CompositeSampleResult.objects.create(
            composite_sample=composite_sample,
            property=property,
            value=test_value,
            unit=property.unit,
            test_method='Teste manual'
        )
        
        print(f"   ✅ Resultado criado com ID: {result.id}")
        print(f"   Status calculado: {result.status}")
        print(f"   Valor: {result.value}")
        
        # Verificar se o status foi calculado corretamente
        if result.status == 'REJECTED':
            print(f"   ✅ CORRETO: Resultado foi rejeitado como esperado")
        else:
            print(f"   ❌ PROBLEMA: Resultado foi aprovado quando deveria ser rejeitado")
            
    except Exception as e:
        print(f"   ❌ ERRO ao criar resultado de amostra composta: {e}")

if __name__ == '__main__':
    test_approval_logic()
