#!/usr/bin/env python
"""
Script para configurar especificações de propriedades
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import Product, Property, Specification

def setup_specifications():
    """Configurar especificações para propriedades"""
    
    print("🔧 Configurando especificações de propriedades...")
    
    # Buscar produtos
    products = Product.objects.filter(is_active=True)
    if not products.exists():
        print("❌ Nenhum produto encontrado. Execute primeiro o setup_initial_data.py")
        return
    
    # Buscar propriedades
    properties = Property.objects.filter(is_active=True)
    if not properties.exists():
        print("❌ Nenhuma propriedade encontrada. Execute primeiro o setup_initial_data.py")
        return
    
    # Especificações padrão (exemplo)
    specifications_data = {
        'UMID': {
            'lsl': 8.0,  # Limite inferior
            'usl': 12.0,  # Limite superior
            'target': 10.0  # Valor alvo
        },
        'SiO2': {
            'lsl': 45.0,
            'usl': 55.0,
            'target': 50.0
        },
        'Fe2O3': {
            'lsl': 8.0,
            'usl': 15.0,
            'target': 12.0
        },
        'Al2O3': {
            'lsl': 10.0,
            'usl': 20.0,
            'target': 15.0
        },
        'MgO': {
            'lsl': 20.0,
            'usl': 30.0,
            'target': 25.0
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
    
    print(f"\n✅ Especificações configuradas com sucesso!")
    print(f"   📊 Criadas: {created_count}")
    print(f"   🔄 Atualizadas: {updated_count}")
    print(f"   📦 Produtos: {products.count()}")
    print(f"   🔬 Propriedades: {properties.count()}")

if __name__ == '__main__':
    setup_specifications()
