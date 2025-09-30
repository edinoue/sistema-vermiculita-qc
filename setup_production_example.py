#!/usr/bin/env python
"""
Script para criar uma produção de exemplo para o turno atual
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from core.models import Shift, Plant, ProductionLine
from quality_control.models import Product
from quality_control.models_production import ProductionRegistration, ProductionLineRegistration, ProductionProductRegistration
from django.contrib.auth.models import User
from django.utils import timezone

def create_production_example():
    """Cria uma produção de exemplo para o turno atual"""
    
    print("🏭 Criando Produção de Exemplo")
    print("=" * 40)
    
    # Obter turno atual
    current_time = timezone.now()
    if 6 <= current_time.hour < 18:
        current_shift = Shift.objects.filter(name='A').first()
        print(f"📅 Turno atual: A (06:00 - 18:00)")
    else:
        current_shift = Shift.objects.filter(name='B').first()
        print(f"📅 Turno atual: B (18:00 - 06:00)")
    
    if not current_shift:
        print("❌ Nenhum turno encontrado!")
        return False
    
    # Obter usuário admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_user('admin', 'admin@example.com', 'admin123')
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
    
    # Verificar se já existe produção para hoje
    today = timezone.now().date()
    existing_production = ProductionRegistration.objects.filter(
        date=today,
        shift=current_shift
    ).first()
    
    if existing_production:
        print(f"📍 Produção já existe para {today} - {current_shift.name}")
        print(f"   Status: {existing_production.get_status_display()}")
        return existing_production
    
    # Criar produção
    production = ProductionRegistration.objects.create(
        date=today,
        shift=current_shift,
        operator=admin_user,
        status='ACTIVE',
        observations=f'Produção de exemplo para {current_shift.name}'
    )
    
    print(f"✅ Produção criada: {production}")
    
    # Obter plantas e linhas ativas
    plants = Plant.objects.filter(is_active=True)
    lines = ProductionLine.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    print(f"🏭 Plantas ativas: {plants.count()}")
    print(f"🏭 Linhas ativas: {lines.count()}")
    print(f"📦 Produtos ativos: {products.count()}")
    
    # Cadastrar linhas de produção
    lines_added = 0
    for line in lines:
        line_reg, created = ProductionLineRegistration.objects.get_or_create(
            production=production,
            production_line=line,
            defaults={'is_active': True}
        )
        
        if created:
            lines_added += 1
            print(f"  ✅ Linha cadastrada: {line.name} ({line.plant.name})")
        else:
            print(f"  📍 Linha já cadastrada: {line.name} ({line.plant.name})")
    
    # Cadastrar produtos
    products_added = 0
    for product in products:
        prod_reg, created = ProductionProductRegistration.objects.get_or_create(
            production=production,
            product=product,
            defaults={
                'is_active': True,
                'product_type': 'Principal'
            }
        )
        
        if created:
            products_added += 1
            print(f"  ✅ Produto cadastrado: {product.name}")
        else:
            print(f"  📍 Produto já cadastrado: {product.name}")
    
    print(f"\n🎉 Produção configurada com sucesso!")
    print(f"   - Linhas cadastradas: {lines_added}")
    print(f"   - Produtos cadastrados: {products_added}")
    print(f"   - Status: {production.get_status_display()}")
    
    return production

def main():
    print("🚀 Configurando Produção de Exemplo")
    print("=" * 50)
    
    production = create_production_example()
    
    if production:
        print(f"\n✅ Configuração concluída!")
        print(f"   Agora o dashboard deve mostrar os locais de produção cadastrados.")
        print(f"   Acesse: http://localhost:8000/qc/dashboard/spot/by-plant/")
    else:
        print(f"\n❌ Erro na configuração!")

if __name__ == '__main__':
    main()
