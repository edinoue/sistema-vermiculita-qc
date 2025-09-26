#!/usr/bin/env python
"""
Script para debugar amostras compostas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import Product, Property, Specification, CompositeSample, CompositeSampleResult
from decimal import Decimal

def debug_composite_sample():
    """Debugar amostras compostas"""
    
    print("🔍 DEBUGANDO AMOSTRAS COMPOSTAS")
    print("=" * 50)
    
    # 1. Verificar amostras compostas existentes
    print("\n1. VERIFICANDO AMOSTRAS COMPOSTAS EXISTENTES:")
    composite_samples = CompositeSample.objects.all().order_by('-created_at')[:5]
    print(f"   Total de amostras compostas: {CompositeSample.objects.count()}")
    
    for sample in composite_samples:
        print(f"   - ID: {sample.id}, Data: {sample.date}, Produto: {sample.product.code}")
        
        # Verificar resultados
        results = CompositeSampleResult.objects.filter(composite_sample=sample)
        print(f"     Resultados: {results.count()}")
        
        for result in results:
            print(f"       - {result.property.identifier}: {result.value} - Status: {result.status}")
            
            # Verificar se há especificação
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
    
    # 2. Verificar especificações para TEOR_VERM
    print("\n2. VERIFICANDO ESPECIFICAÇÕES PARA TEOR_VERM:")
    try:
        product = Product.objects.get(code='VER_CONC')
        property = Property.objects.get(identifier='TEOR_VERM')
        
        spec = Specification.objects.get(
            product=product, 
            property=property, 
            is_active=True
        )
        
        print(f"   Produto: {product.code} - {product.name}")
        print(f"   Propriedade: {property.identifier} - {property.name}")
        print(f"   Especificação: LSL={spec.lsl}, USL={spec.usl}, Target={spec.target}")
        print(f"   Ativa: {spec.is_active}")
        
    except Specification.DoesNotExist:
        print(f"   ❌ ESPECIFICAÇÃO NÃO ENCONTRADA para {product.code} - {property.identifier}")
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
    
    # 3. Testar criação de resultado com valor 70
    print("\n3. TESTANDO CRIAÇÃO DE RESULTADO COM VALOR 70:")
    try:
        from quality_control.models import Shift, ProductionLine
        from django.utils import timezone
        
        # Buscar dados necessários
        shift = Shift.objects.first()
        production_line = ProductionLine.objects.first()
        
        # Criar amostra composta
        sample = CompositeSample.objects.create(
            date=timezone.now().date(),
            shift=shift,
            production_line=production_line,
            product=product,
            collection_time=timezone.now(),
            status='APPROVED'
        )
        
        print(f"   ✅ Amostra composta criada com ID: {sample.id}")
        
        # Criar resultado com valor 70
        result = CompositeSampleResult.objects.create(
            composite_sample=sample,
            property=property,
            value=Decimal('70.0'),
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
            
        # Verificar se o resultado aparece na view
        results = CompositeSampleResult.objects.filter(composite_sample=sample)
        print(f"   Resultados encontrados na view: {results.count()}")
        
        for r in results:
            print(f"     - {r.property.identifier}: {r.value} - Status: {r.status}")
            
    except Exception as e:
        print(f"   ❌ ERRO ao criar resultado: {e}")

if __name__ == '__main__':
    debug_composite_sample()



