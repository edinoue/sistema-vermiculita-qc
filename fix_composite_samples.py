#!/usr/bin/env python
"""
Script para corrigir problemas com amostras compostas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import Product, Property, Specification, CompositeSample, CompositeSampleResult
from decimal import Decimal

def fix_composite_samples():
    """Corrigir problemas com amostras compostas"""
    
    print("🔧 CORRIGINDO PROBLEMAS COM AMOSTRAS COMPOSTAS")
    print("=" * 60)
    
    # 1. Criar/Verificar especificação para TEOR_VERM
    print("\n1. CRIANDO/VERIFICANDO ESPECIFICAÇÃO PARA TEOR_VERM:")
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
        
        if created:
            print(f"   ✅ Especificação criada para {product.code} - {property.identifier}")
        else:
            print(f"   🔄 Especificação já existe para {product.code} - {property.identifier}")
            # Atualizar valores se necessário
            spec.lsl = Decimal('82.0')
            spec.target = Decimal('92.0')
            spec.usl = None
            spec.is_active = True
            spec.save()
            print(f"   🔄 Especificação atualizada")
        
        print(f"      LSL: {spec.lsl}, Target: {spec.target}, USL: {spec.usl}")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        return
    
    # 2. Corrigir resultados existentes
    print("\n2. CORRIGINDO RESULTADOS EXISTENTES:")
    results = CompositeSampleResult.objects.all()
    print(f"   Total de resultados: {results.count()}")
    
    corrected_count = 0
    for result in results:
        old_status = result.status
        
        # Garantir que a unidade está correta
        if not result.unit:
            result.unit = result.property.unit
        
        # Recalcular status
        result.save()  # Isso vai recalcular o status
        new_status = result.status
        
        if old_status != new_status:
            print(f"   🔄 {result.composite_sample.id} - {result.property.identifier}: {old_status} → {new_status}")
            corrected_count += 1
        
        # Verificar se valor 70 está sendo rejeitado corretamente
        if result.property.identifier == 'TEOR_VERM' and result.value == 70:
            if result.status != 'REJECTED':
                print(f"   ❌ PROBLEMA: Valor 70 para TEOR_VERM não foi rejeitado!")
                print(f"      Status: {result.status}, Valor: {result.value}")
            else:
                print(f"   ✅ CORRETO: Valor 70 para TEOR_VERM foi rejeitado")
    
    print(f"   ✅ {corrected_count} resultados corrigidos")
    
    # 3. Verificar amostras compostas e seus resultados
    print("\n3. VERIFICANDO AMOSTRAS COMPOSTAS E RESULTADOS:")
    samples = CompositeSample.objects.all().order_by('-created_at')[:5]
    
    for sample in samples:
        print(f"   Amostra ID {sample.id} ({sample.date}):")
        results = CompositeSampleResult.objects.filter(composite_sample=sample)
        print(f"      Resultados: {results.count()}")
        
        for result in results:
            print(f"        - {result.property.identifier}: {result.value} ({result.status})")
    
    # 4. Verificar se unidades estão corretas
    print("\n4. VERIFICANDO UNIDADES:")
    results_without_unit = CompositeSampleResult.objects.filter(unit__isnull=True)
    if results_without_unit.exists():
        print(f"   ❌ {results_without_unit.count()} resultados sem unidade")
        for result in results_without_unit:
            result.unit = result.property.unit
            result.save()
            print(f"      🔄 Unidade corrigida para {result.property.identifier}: {result.unit}")
    else:
        print(f"   ✅ Todas as unidades estão corretas")

if __name__ == '__main__':
    fix_composite_samples()





