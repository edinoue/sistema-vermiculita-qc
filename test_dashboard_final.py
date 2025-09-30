#!/usr/bin/env python
"""
Teste final do dashboard
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from quality_control.views import spot_dashboard_by_plant_view
from quality_control.models_production import ProductionRegistration, ProductionLineRegistration, ProductionProductRegistration
from core.models import Shift, Plant, ProductionLine
from quality_control.models import Product
from django.utils import timezone

def test_dashboard():
    print("🧪 Testando Dashboard Final")
    print("=" * 40)
    
    # Verificar dados básicos
    today = timezone.now().date()
    current_shift = Shift.objects.filter(name='A').first() if 6 <= timezone.now().hour < 18 else Shift.objects.filter(name='B').first()
    
    print(f"📅 Data: {today}")
    print(f"🕐 Turno: {current_shift}")
    
    # Verificar produção
    production = ProductionRegistration.objects.filter(
        date=today,
        shift=current_shift,
        status='ACTIVE'
    ).first()
    
    print(f"🏭 Produção: {production}")
    
    if not production:
        print("❌ Nenhuma produção encontrada!")
        print("   Criando produção de exemplo...")
        
        # Criar produção
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_user('admin', 'admin@example.com', 'admin123')
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
        
        # Cadastrar linhas
        lines = ProductionLine.objects.filter(is_active=True)
        for line in lines:
            ProductionLineRegistration.objects.get_or_create(
                production=production,
                production_line=line,
                defaults={'is_active': True}
            )
            print(f"  ✅ Linha cadastrada: {line.name}")
        
        # Cadastrar produtos
        products = Product.objects.filter(is_active=True)
        for product in products:
            ProductionProductRegistration.objects.get_or_create(
                production=production,
                product=product,
                defaults={'is_active': True, 'product_type': 'Principal'}
            )
            print(f"  ✅ Produto cadastrado: {product.name}")
    
    # Testar view
    print(f"\n🔍 Testando view...")
    try:
        factory = RequestFactory()
        request = factory.get('/qc/dashboard/spot/by-plant/')
        user = User.objects.first()
        request.user = user
        
        response = spot_dashboard_by_plant_view(request)
        print(f"  - Status: {response.status_code}")
        
        if response.status_code == 200:
            context = response.context_data
            plants_data = context.get('plants_data', [])
            production_ctx = context.get('production')
            
            print(f"  - Plantas no contexto: {len(plants_data)}")
            print(f"  - Produção no contexto: {production_ctx}")
            
            if plants_data:
                print("  - Dados das plantas:")
                for i, plant_data in enumerate(plants_data):
                    plant = plant_data['plant']
                    products_count = len(plant_data['products'])
                    print(f"    {i+1}. {plant.name} - {products_count} produtos")
            else:
                print("  ⚠️  Nenhuma planta encontrada no contexto")
        else:
            print(f"  ❌ Erro na view: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Erro ao testar view: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n✅ Teste concluído!")

if __name__ == '__main__':
    test_dashboard()
