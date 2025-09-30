#!/usr/bin/env python
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.utils import timezone
from quality_control.models_production import ProductionRegistration, ProductionLineRegistration, ProductionProductRegistration
from core.models import Shift, Plant, ProductionLine
from quality_control.models import Product, Property

print("🔍 Verificando dados de produção...")

today = timezone.now().date()
print(f"Data: {today}")

# Verificar turnos
shifts = Shift.objects.all()
print(f"Turnos: {shifts.count()}")
for shift in shifts:
    print(f"  - {shift.name}")

# Verificar turno atual
current_time = timezone.now()
if 6 <= current_time.hour < 18:
    current_shift_name = 'A'
else:
    current_shift_name = 'B'

current_shift = Shift.objects.filter(name=current_shift_name).first()
print(f"Turno atual: {current_shift_name} -> {current_shift}")

# Verificar produção
production = ProductionRegistration.objects.filter(
    date=today,
    shift=current_shift,
    status='ACTIVE'
).first()
print(f"Produção ativa: {production}")

if not production:
    print("❌ Nenhuma produção ativa encontrada!")
    print("Criando produção de exemplo...")
    
    # Criar produção de exemplo
    from django.contrib.auth.models import User
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_user('admin', 'admin@test.com', 'admin123')
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
    
    production = ProductionRegistration.objects.create(
        date=today,
        shift=current_shift,
        operator=admin_user,
        status='ACTIVE',
        observations='Produção de exemplo'
    )
    print(f"✅ Produção criada: {production}")
    
    # Criar planta se não existir
    plant, created = Plant.objects.get_or_create(
        code='VER01',
        defaults={
            'name': 'Planta Principal',
            'description': 'Planta principal de produção',
            'is_active': True
        }
    )
    print(f"Planta: {plant} (criada: {created})")
    
    # Criar linha de produção se não existir
    line, created = ProductionLine.objects.get_or_create(
        name='Linha Principal',
        plant=plant,
        defaults={
            'description': 'Linha principal de produção',
            'is_active': True
        }
    )
    print(f"Linha: {line} (criada: {created})")
    
    # Adicionar linha à produção
    line_reg, created = ProductionLineRegistration.objects.get_or_create(
        production=production,
        production_line=line,
        defaults={'is_active': True}
    )
    print(f"Linha na produção: {line_reg} (criada: {created})")
    
    # Criar produtos se não existirem
    products_data = [
        {'name': 'Vermiculita Concentrada Médio', 'code': 'VERM001'},
        {'name': 'Vermiculita Concentrada Fino', 'code': 'VERM002'},
        {'name': 'Vermiculita Concentrada Super Fino', 'code': 'VERM003'},
        {'name': 'Vermiculita Concentrada Micron', 'code': 'VERM004'},
    ]
    
    for prod_data in products_data:
        product, created = Product.objects.get_or_create(
            code=prod_data['code'],
            defaults={
                'name': prod_data['name'],
                'description': f'Produto {prod_data["name"]}',
                'is_active': True
            }
        )
        print(f"Produto: {product} (criado: {created})")
        
        # Adicionar produto à produção
        prod_reg, created = ProductionProductRegistration.objects.get_or_create(
            production=production,
            product=product,
            defaults={'is_active': True, 'product_type': 'Principal'}
        )
        print(f"Produto na produção: {prod_reg} (criado: {created})")

print("✅ Verificação concluída!")
