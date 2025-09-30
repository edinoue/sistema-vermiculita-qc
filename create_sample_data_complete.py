#!/usr/bin/env python
"""
Script completo para criar dados de exemplo no sistema
"""

import os
import sys
import django
from datetime import datetime, time

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from quality_control.models_production import ProductionRegistration, ProductionLineRegistration, ProductionProductRegistration
from core.models import Shift, Plant, ProductionLine
from quality_control.models import Product, Property, AnalysisType, SpotSample, SpotAnalysis
from django.utils import timezone

def create_sample_data_complete():
    """Criar dados de exemplo completos"""
    print("🚀 === Criando Dados de Exemplo Completos ===")
    
    # 1. Criar superusuário se não existir
    print("\n1️⃣ Verificando superusuário...")
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@vermiculita.com',
            password='admin123'
        )
        print("✅ Superusuário 'admin' criado")
    else:
        print("✅ Superusuário já existe")
    
    # 2. Criar turnos
    print("\n2️⃣ Criando turnos...")
    shift_a, created = Shift.objects.get_or_create(
        name='A',
        defaults={'start_time': '06:00:00', 'end_time': '18:00:00', 'description': 'Turno A (06:00 - 18:00)'}
    )
    if created:
        print("✅ Turno A criado")
    else:
        print("📍 Turno A já existe")
    
    shift_b, created = Shift.objects.get_or_create(
        name='B',
        defaults={'start_time': '18:00:00', 'end_time': '06:00:00', 'description': 'Turno B (18:00 - 06:00)'}
    )
    if created:
        print("✅ Turno B criado")
    else:
        print("📍 Turno B já existe")
    
    # 3. Criar planta
    print("\n3️⃣ Criando planta...")
    plant, created = Plant.objects.get_or_create(
        code='VER01',
        defaults={
            'name': 'Planta Principal',
            'description': 'Planta principal de produção',
            'is_active': True
        }
    )
    if created:
        print("✅ Planta criada")
    else:
        print("📍 Planta já existe")
    
    # 4. Criar linha de produção
    print("\n4️⃣ Criando linha de produção...")
    line, created = ProductionLine.objects.get_or_create(
        name='Linha Principal',
        plant=plant,
        defaults={
            'description': 'Linha principal de produção',
            'is_active': True
        }
    )
    if created:
        print("✅ Linha de produção criada")
    else:
        print("📍 Linha de produção já existe")
    
    # 5. Criar produtos
    print("\n5️⃣ Criando produtos...")
    products_data = [
        {'name': 'Vermiculita Concentrada Médio', 'code': 'VERM001'},
        {'name': 'Vermiculita Concentrada Fino', 'code': 'VERM002'},
        {'name': 'Vermiculita Concentrada Super Fino', 'code': 'VERM003'},
        {'name': 'Vermiculita Concentrada Micron', 'code': 'VERM004'},
    ]
    
    products = []
    for prod_data in products_data:
        product, created = Product.objects.get_or_create(
            code=prod_data['code'],
            defaults={
                'name': prod_data['name'],
                'description': f'Produto {prod_data["name"]}',
                'is_active': True
            }
        )
        products.append(product)
        if created:
            print(f"✅ Produto {product.name} criado")
        else:
            print(f"📍 Produto {product.name} já existe")
    
    # 6. Criar propriedades
    print("\n6️⃣ Criando propriedades...")
    properties_data = [
        {'name': 'Teor de Vermiculita', 'code': 'TEOR_VERM', 'unit': '%', 'display_order': 1},
        {'name': 'Rendimento na Expansão', 'code': 'REND_EXP', 'unit': '%', 'display_order': 2},
        {'name': 'Umidade', 'code': 'UMIDADE', 'unit': '%', 'display_order': 3},
        {'name': 'Densidade', 'code': 'DENSIDADE', 'unit': 'g/cm³', 'display_order': 4},
    ]
    
    properties = []
    for prop_data in properties_data:
        property_obj, created = Property.objects.get_or_create(
            code=prop_data['code'],
            defaults={
                'name': prop_data['name'],
                'unit': prop_data['unit'],
                'display_order': prop_data['display_order'],
                'is_active': True
            }
        )
        properties.append(property_obj)
        if created:
            print(f"✅ Propriedade {property_obj.name} criada")
        else:
            print(f"📍 Propriedade {property_obj.name} já existe")
    
    # 7. Criar tipo de análise
    print("\n7️⃣ Criando tipo de análise...")
    analysis_type, created = AnalysisType.objects.get_or_create(
        code='PONTUAL',
        defaults={
            'name': 'Análise Pontual',
            'description': 'Análise de amostra pontual',
            'is_active': True
        }
    )
    if created:
        print("✅ Tipo de análise criado")
    else:
        print("📍 Tipo de análise já existe")
    
    # 8. Criar produção para o turno atual
    print("\n8️⃣ Criando produção para o turno atual...")
    today = timezone.now().date()
    current_time = timezone.now().time()
    
    if 6 <= current_time.hour < 18:
        current_shift = shift_a
    else:
        current_shift = shift_b
    
    production, created = ProductionRegistration.objects.get_or_create(
        date=today,
        shift=current_shift,
        defaults={
            'operator': admin_user,
            'status': 'ACTIVE',
            'observations': 'Produção de exemplo'
        }
    )
    if created:
        print(f"✅ Produção criada para {today} - Turno {current_shift.name}")
    else:
        print(f"📍 Produção já existe para {today} - Turno {current_shift.name}")
    
    # 9. Adicionar linha à produção
    print("\n9️⃣ Adicionando linha à produção...")
    line_reg, created = ProductionLineRegistration.objects.get_or_create(
        production=production,
        production_line=line,
        defaults={'is_active': True}
    )
    if created:
        print("✅ Linha adicionada à produção")
    else:
        print("📍 Linha já está na produção")
    
    # 10. Adicionar produtos à produção
    print("\n🔟 Adicionando produtos à produção...")
    for product in products:
        prod_reg, created = ProductionProductRegistration.objects.get_or_create(
            production=production,
            product=product,
            defaults={'is_active': True, 'product_type': 'Principal'}
        )
        if created:
            print(f"✅ Produto {product.name} adicionado à produção")
        else:
            print(f"📍 Produto {product.name} já está na produção")
    
    # 11. Criar amostras pontuais com análises
    print("\n1️⃣1️⃣ Criando amostras pontuais com análises...")
    import random
    
    for i, product in enumerate(products):
        # Criar amostra
        sample = SpotSample.objects.create(
            production_line=line,
            product=product,
            date=today,
            shift=current_shift,
            sample_sequence=i + 1,
            sample_time=timezone.now().time(),
            observations=f'Amostra de exemplo para {product.name}',
            created_by=admin_user
        )
        print(f"✅ Amostra {sample.sample_sequence} criada para {product.name}")
        
        # Criar análises para cada propriedade
        for property_obj in properties:
            # Gerar valores aleatórios realistas
            if property_obj.code == 'TEOR_VERM':
                value = round(random.uniform(85.0, 95.0), 2)
                status = 'APPROVED' if value >= 90 else 'ALERT' if value >= 85 else 'REJECTED'
            elif property_obj.code == 'REND_EXP':
                value = round(random.uniform(15.0, 25.0), 2)
                status = 'APPROVED' if value >= 20 else 'ALERT' if value >= 15 else 'REJECTED'
            elif property_obj.code == 'UMIDADE':
                value = round(random.uniform(2.0, 8.0), 2)
                status = 'APPROVED' if value <= 5 else 'ALERT' if value <= 8 else 'REJECTED'
            elif property_obj.code == 'DENSIDADE':
                value = round(random.uniform(0.8, 1.2), 2)
                status = 'APPROVED' if 0.9 <= value <= 1.1 else 'ALERT' if 0.8 <= value <= 1.2 else 'REJECTED'
            else:
                value = round(random.uniform(1.0, 100.0), 2)
                status = 'APPROVED'
            
            analysis = SpotAnalysis.objects.create(
                spot_sample=sample,
                property=property_obj,
                value=value,
                status=status,
                analysis_type=analysis_type,
                created_by=admin_user
            )
            print(f"  ✅ Análise {property_obj.name}: {value} {property_obj.unit} ({status})")
    
    print("\n🎉 === Dados de Exemplo Criados com Sucesso! ===")
    print("✅ Sistema populado com dados de exemplo")
    print("✅ Dashboard deve mostrar dados reais agora")
    print(f"✅ Acesse: http://localhost:8000/qc/dashboard/spot/")

if __name__ == '__main__':
    create_sample_data_complete()
