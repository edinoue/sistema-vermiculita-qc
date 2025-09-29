#!/usr/bin/env python
"""
Script para configurar especificações para análises pontuais
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import Product, Property, Specification
from decimal import Decimal

def setup_spot_analysis_specifications():
    """Configurar especificações para análises pontuais"""
    
    print("🔧 Configurando especificações para análises pontuais...")
    
    # Buscar produtos
    products = Product.objects.filter(is_active=True)
    if not products.exists():
        print("❌ Nenhum produto encontrado.")
        return
    
    # Buscar propriedades
    properties = Property.objects.filter(is_active=True)
    if not properties.exists():
        print("❌ Nenhuma propriedade encontrada.")
        return
    
    # Especificações para análises pontuais
    specifications_data = {
        'TEOR_VERM': {
            'lsl': Decimal('60.0'),  # Limite inferior
            'usl': Decimal('80.0'),  # Limite superior
            'target': Decimal('70.0')  # Valor alvo
        },
        'RENDIMENTO': {
            'lsl': Decimal('5.0'),
            'usl': Decimal('10.0'),
            'target': Decimal('7.5')
        }
    }
    
    created_count = 0
    updated_count = 0
    
    for product in products:
        print(f"📦 Configurando especificações para {product.name}...")
        
        for property in properties:
            if property.identifier in specifications_data:
                spec_data = specifications_data[property.identifier]
                
                spec, created = Specification.objects.get_or_create(
                    product=product,
                    property=property,
                    defaults={
                        'lsl': spec_data['lsl'],
                        'usl': spec_data['usl'],
                        'target': spec_data['target'],
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"  ✅ Criada especificação para {property.identifier}")
                else:
                    # Atualizar se já existir
                    spec.lsl = spec_data['lsl']
                    spec.usl = spec_data['usl']
                    spec.target = spec_data['target']
                    spec.is_active = True
                    spec.save()
                    updated_count += 1
                    print(f"  🔄 Atualizada especificação para {property.identifier}")
                
                print(f"      LSL: {spec.lsl}, Target: {spec.target}, USL: {spec.usl}")
    
    print(f"\n✅ Especificações configuradas com sucesso!")
    print(f"   📊 Criadas: {created_count}")
    print(f"   🔄 Atualizadas: {updated_count}")
    print(f"   📦 Produtos: {products.count()}")
    print(f"   🔬 Propriedades: {properties.count()}")

if __name__ == '__main__':
    setup_spot_analysis_specifications()
