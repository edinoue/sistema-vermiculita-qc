#!/usr/bin/env python
"""
Script para testar criação de amostras compostas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import Product, Property, Specification, CompositeSample, CompositeSampleResult, AnalysisType
from decimal import Decimal
from django.utils import timezone

def test_composite_sample_creation():
    """Testar criação de amostras compostas"""
    
    print("🧪 TESTANDO CRIAÇÃO DE AMOSTRAS COMPOSTAS")
    print("=" * 60)
    
    # 1. Verificar dados necessários
    print("\n1. VERIFICANDO DADOS NECESSÁRIOS:")
    try:
        product = Product.objects.get(code='VER_CONC')
        property = Property.objects.get(identifier='TEOR_VERM')
        analysis_type = AnalysisType.objects.get(code='COMPOSTA')
        
        print(f"   ✅ Produto: {product.code} - {product.name}")
        print(f"   ✅ Propriedade: {property.identifier} - {property.name}")
        print(f"   ✅ Tipo de análise: {analysis_type.code} - {analysis_type.name}")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        return
    
    # 2. Verificar especificação
    print("\n2. VERIFICANDO ESPECIFICAÇÃO:")
    try:
        spec = Specification.objects.get(
            product=product, 
            property=property, 
            is_active=True
        )
        print(f"   ✅ Especificação encontrada:")
        print(f"      LSL: {spec.lsl}")
        print(f"      USL: {spec.usl}")
        print(f"      Target: {spec.target}")
        print(f"      Ativa: {spec.is_active}")
        
    except Specification.DoesNotExist:
        print(f"   ❌ ESPECIFICAÇÃO NÃO ENCONTRADA")
        print(f"   🔧 Criando especificação...")
        
        spec = Specification.objects.create(
            product=product,
            property=property,
            lsl=Decimal('82.0'),
            target=Decimal('92.0'),
            usl=None,
            is_active=True
        )
        print(f"   ✅ Especificação criada: LSL={spec.lsl}, USL={spec.usl}")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        return
    
    # 3. Criar amostra composta
    print("\n3. CRIANDO AMOSTRA COMPOSTA:")
    try:
        from quality_control.models import Shift, ProductionLine
        
        shift = Shift.objects.first()
        production_line = ProductionLine.objects.first()
        
        sample = CompositeSample.objects.create(
            date=timezone.now().date(),
            shift=shift,
            production_line=production_line,
            product=product,
            collection_time=timezone.now(),
            status='APPROVED'
        )
        
        print(f"   ✅ Amostra composta criada:")
        print(f"      ID: {sample.id}")
        print(f"      Data: {sample.date}")
        print(f"      Produto: {sample.product.code}")
        print(f"      Status: {sample.status}")
        
    except Exception as e:
        print(f"   ❌ ERRO ao criar amostra composta: {e}")
        return
    
    # 4. Criar resultado com valor 70 (deveria ser rejeitado)
    print("\n4. CRIANDO RESULTADO COM VALOR 70:")
    try:
        result = CompositeSampleResult.objects.create(
            composite_sample=sample,
            property=property,
            value=Decimal('70.0'),
            unit=property.unit,
            test_method='Teste manual'
        )
        
        print(f"   ✅ Resultado criado:")
        print(f"      ID: {result.id}")
        print(f"      Propriedade: {result.property.identifier}")
        print(f"      Valor: {result.value}")
        print(f"      Status: {result.status}")
        
        # Verificar se o status foi calculado corretamente
        if result.status == 'REJECTED':
            print(f"   ✅ CORRETO: Resultado foi rejeitado como esperado")
        else:
            print(f"   ❌ PROBLEMA: Resultado foi aprovado quando deveria ser rejeitado")
            
    except Exception as e:
        print(f"   ❌ ERRO ao criar resultado: {e}")
        return
    
    # 5. Verificar se o resultado aparece na view
    print("\n5. VERIFICANDO SE RESULTADO APARECE NA VIEW:")
    try:
        results = CompositeSampleResult.objects.filter(composite_sample=sample)
        print(f"   Total de resultados encontrados: {results.count()}")
        
        for r in results:
            print(f"      - {r.property.identifier}: {r.value} - Status: {r.status}")
            
        if results.count() > 0:
            print(f"   ✅ Resultados encontrados na view")
        else:
            print(f"   ❌ PROBLEMA: Nenhum resultado encontrado na view")
            
    except Exception as e:
        print(f"   ❌ ERRO ao verificar resultados: {e}")
    
    # 6. Testar cálculo manual de status
    print("\n6. TESTANDO CÁLCULO MANUAL DE STATUS:")
    try:
        test_value = Decimal('70.0')
        print(f"   Valor de teste: {test_value}")
        print(f"   LSL: {spec.lsl}")
        print(f"   USL: {spec.usl}")
        
        if spec.lsl is not None and test_value < spec.lsl:
            print(f"   ❌ DEVERIA SER REJEITADO: {test_value} < {spec.lsl}")
        elif spec.usl is not None and test_value > spec.usl:
            print(f"   ❌ DEVERIA SER REJEITADO: {test_value} > {spec.usl}")
        else:
            print(f"   ✅ APROVADO: {test_value} dentro dos limites")
            
    except Exception as e:
        print(f"   ❌ ERRO ao testar cálculo: {e}")

if __name__ == '__main__':
    test_composite_sample_creation()




