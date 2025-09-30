#!/usr/bin/env python
"""
Script para verificar propriedades e especificações
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import Product, Property, Specification

def check_properties():
    """Verificar propriedades e especificações"""
    
    print("🔍 VERIFICANDO PROPRIEDADES E ESPECIFICAÇÕES")
    print("=" * 50)
    
    # 1. Verificar propriedades
    properties = Property.objects.filter(is_active=True)
    print(f"\n🔬 Propriedades ativas: {properties.count()}")
    for prop in properties:
        print(f"   ID: {prop.id}, Identifier: '{prop.identifier}', Name: '{prop.name}'")
    
    # 2. Verificar produtos
    products = Product.objects.filter(is_active=True)
    print(f"\n📦 Produtos ativos: {products.count()}")
    for product in products:
        print(f"   ID: {product.id}, Code: '{product.code}', Name: '{product.name}'")
    
    # 3. Verificar especificações
    specs = Specification.objects.filter(is_active=True)
    print(f"\n📋 Especificações ativas: {specs.count()}")
    for spec in specs:
        print(f"   Produto: {spec.product.code}, Propriedade: {spec.property.identifier}")
        print(f"   LSL: {spec.lsl}, USL: {spec.usl}, Target: {spec.target}")
    
    # 4. Verificar se há especificações para TEOR_VERM e RENDIMENTO
    print(f"\n🔍 Verificando especificações específicas:")
    
    teor_verm_props = Property.objects.filter(identifier='TEOR_VERM')
    rendimento_props = Property.objects.filter(identifier='RENDIMENTO')
    
    print(f"   TEOR_VERM encontradas: {teor_verm_props.count()}")
    for prop in teor_verm_props:
        print(f"      - {prop.identifier} ({prop.name})")
    
    print(f"   RENDIMENTO encontradas: {rendimento_props.count()}")
    for prop in rendimento_props:
        print(f"      - {prop.identifier} ({prop.name})")
    
    # 5. Verificar especificações para essas propriedades
    if teor_verm_props.exists():
        teor_specs = Specification.objects.filter(property__in=teor_verm_props)
        print(f"   Especificações TEOR_VERM: {teor_specs.count()}")
        for spec in teor_specs:
            print(f"      - {spec.product.code}: LSL={spec.lsl}, USL={spec.usl}")
    
    if rendimento_props.exists():
        rend_specs = Specification.objects.filter(property__in=rendimento_props)
        print(f"   Especificações RENDIMENTO: {rend_specs.count()}")
        for spec in rend_specs:
            print(f"      - {spec.product.code}: LSL={spec.lsl}, USL={spec.usl}")

if __name__ == '__main__':
    check_properties()
