#!/usr/bin/env python
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from quality_control.models_production import ProductionRegistration, ProductionLineRegistration, ProductionProductRegistration
from core.models import Shift, Plant, ProductionLine
from quality_control.models import Product, Property, AnalysisType, SpotSample, SpotAnalysis
import random

print("🚀 Criando dados de exemplo...")

# Criar superusuário
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@test.com',
        'is_superuser': True,
        'is_staff': True
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
print(f"✅ Usuário: {admin_user}")

# Criar turno
shift, created = Shift.objects.get_or_create(
    name='A',
    defaults={'start_time': '06:00:00', 'end_time': '18:00:00'}
)
print(f"✅ Turno: {shift}")

# Criar planta
plant, created = Plant.objects.get_or_create(
    code='VER01',
    defaults={'name': 'Planta Principal', 'is_active': True}
)
print(f"✅ Planta: {plant}")

# Criar linha
line, created = ProductionLine.objects.get_or_create(
    name='Linha Principal',
    plant=plant,
    defaults={'is_active': True}
)
print(f"✅ Linha: {line}")

# Criar produtos
products = []
for i, name in enumerate(['Vermiculita Concentrada Médio', 'Vermiculita Concentrada Fino', 'Vermiculita Concentrada Super Fino', 'Vermiculita Concentrada Micron']):
    product, created = Product.objects.get_or_create(
        code=f'VERM{i+1:03d}',
        defaults={'name': name, 'is_active': True}
    )
    products.append(product)
print(f"✅ Produtos: {len(products)}")

# Criar propriedades
properties = []
for name, code, unit in [('Teor de Vermiculita', 'TEOR_VERM', '%'), ('Rendimento na Expansão', 'REND_EXP', '%')]:
    prop, created = Property.objects.get_or_create(
        code=code,
        defaults={'name': name, 'unit': unit, 'is_active': True}
    )
    properties.append(prop)
print(f"✅ Propriedades: {len(properties)}")

# Criar produção
today = timezone.now().date()
production, created = ProductionRegistration.objects.get_or_create(
    date=today,
    shift=shift,
    defaults={'operator': admin_user, 'status': 'ACTIVE'}
)
print(f"✅ Produção: {production}")

# Adicionar linha à produção
ProductionLineRegistration.objects.get_or_create(
    production=production,
    production_line=line,
    defaults={'is_active': True}
)

# Adicionar produtos à produção
for product in products:
    ProductionProductRegistration.objects.get_or_create(
        production=production,
        product=product,
        defaults={'is_active': True}
    )

# Criar amostras e análises
for i, product in enumerate(products):
    sample = SpotSample.objects.create(
        production_line=line,
        product=product,
        date=today,
        shift=shift,
        sample_sequence=i + 1,
        sample_time=timezone.now().time(),
        observations=f'Amostra {i+1}',
        created_by=admin_user
    )
    
    for prop in properties:
        if prop.code == 'TEOR_VERM':
            value = round(random.uniform(85.0, 95.0), 2)
        else:
            value = round(random.uniform(15.0, 25.0), 2)
        
        SpotAnalysis.objects.create(
            spot_sample=sample,
            property=prop,
            value=value,
            status='APPROVED',
            created_by=admin_user
        )
    
    print(f"✅ Amostra {i+1} criada com análises")

print("🎉 Dados criados com sucesso!")
