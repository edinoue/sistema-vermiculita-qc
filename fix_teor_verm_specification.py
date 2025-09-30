#!/usr/bin/env python
"""
Script para corrigir especificação do TEOR_VERM
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import Product, Property, Specification
from decimal import Decimal

def fix_teor_verm_specification():
    """Corrigir especificação do TEOR_VERM"""
    
    print("🔧 CORRIGINDO ESPECIFICAÇÃO DO TEOR_VERM")
    print("=" * 50)
    
    try:
        # Buscar produto e propriedade
        product = Product.objects.get(code='VER_CONC')
        property = Property.objects.get(identifier='TEOR_VERM')
        
        print(f"   Produto: {product.code} - {product.name}")
        print(f"   Propriedade: {property.identifier} - {property.name}")
        
        # Criar ou atualizar especificação
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
            print(f"   ✅ Especificação criada:")
        else:
            print(f"   🔄 Especificação atualizada:")
            spec.lsl = Decimal('82.0')
            spec.target = Decimal('92.0')
            spec.usl = None
            spec.is_active = True
            spec.save()
        
        print(f"      LSL: {spec.lsl}")
        print(f"      Target: {spec.target}")
        print(f"      USL: {spec.usl}")
        print(f"      Ativa: {spec.is_active}")
        
        # Testar com valor 70
        test_value = Decimal('70.0')
        print(f"\n   🧪 TESTANDO COM VALOR {test_value}:")
        
        if spec.lsl is not None and test_value < spec.lsl:
            print(f"      ❌ DEVERIA SER REJEITADO: {test_value} < {spec.lsl}")
        else:
            print(f"      ✅ APROVADO: {test_value} >= {spec.lsl}")
            
    except Exception as e:
        print(f"   ❌ ERRO: {e}")

if __name__ == '__main__':
    fix_teor_verm_specification()






