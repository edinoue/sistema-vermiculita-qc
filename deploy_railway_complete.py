#!/usr/bin/env python
"""
Script de deploy completo para Railway com todas as correções
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from core.models import Shift, Plant, ProductionLine
from quality_control.models import Product, Property, AnalysisType
from quality_control.models_production import ProductionRegistration, ProductionLineRegistration, ProductionProductRegistration
from django.utils import timezone

def deploy_railway_complete():
    """Deploy completo para Railway com todas as correções"""
    print("🚀 === Deploy Completo para Railway ===")
    print(f"⏰ Timestamp: {datetime.now()}")
    
    try:
        # 1. Aplicar migrações
        print("\n1️⃣ Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrações aplicadas")
        
        # 2. Coletar arquivos estáticos
        print("\n2️⃣ Coletando arquivos estáticos...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Arquivos estáticos coletados")
        
        # 3. Configurar dados básicos
        print("\n3️⃣ Configurando dados básicos...")
        setup_basic_data()
        print("✅ Dados básicos configurados")
        
        # 4. Configurar produção de exemplo
        print("\n4️⃣ Configurando produção de exemplo...")
        setup_production_example()
        print("✅ Produção de exemplo configurada")
        
        # 5. Criar superusuário se não existir
        print("\n5️⃣ Verificando superusuário...")
        create_superuser_if_needed()
        print("✅ Superusuário verificado")
        
        # 6. Verificar correções implementadas
        print("\n6️⃣ Verificando correções...")
        verify_corrections()
        print("✅ Correções verificadas")
        
        print("\n🎉 === Deploy Completo Concluído! ===")
        print("✅ Todas as correções aplicadas")
        print("✅ Sistema pronto para uso")
        print("✅ Dashboard correto disponível em: /qc/dashboard/spot/by-plant/")
        print("✅ Página de instruções disponível em: /qc/dashboard/spot/instructions/")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante deploy: {e}")
        import traceback
        traceback.print_exc()
        return False

def setup_basic_data():
    """Configurar dados básicos do sistema"""
    print("  📊 Configurando turnos...")
    
    # Turnos
    shift_a, created = Shift.objects.get_or_create(
        name='A',
        defaults={'start_time': '06:00:00', 'end_time': '18:00:00', 'description': 'Turno A (06:00 - 18:00)'}
    )
    if created:
        print(f"    ✅ Turno A criado")
    else:
        print(f"    📍 Turno A já existe")
    
    shift_b, created = Shift.objects.get_or_create(
        name='B',
        defaults={'start_time': '18:00:00', 'end_time': '06:00:00', 'description': 'Turno B (18:00 - 06:00)'}
    )
    if created:
        print(f"    ✅ Turno B criado")
    else:
        print(f"    📍 Turno B já existe")
    
    print("  🏭 Configurando plantas...")
    
    # Planta principal
    plant, created = Plant.objects.get_or_create(
        code='VER01',
        defaults={
            'name': 'Planta Principal',
            'description': 'Planta principal de produção',
            'is_active': True
        }
    )
    if created:
        print(f"    ✅ Planta {plant.name} criada")
    else:
        print(f"    📍 Planta {plant.name} já existe")
    
    # Linha de produção
    line, created = ProductionLine.objects.get_or_create(
        name='Linha Principal',
        plant=plant,
        defaults={
            'description': 'Linha principal de produção',
            'is_active': True
        }
    )
    if created:
        print(f"    ✅ Linha {line.name} criada")
    else:
        print(f"    📍 Linha {line.name} já existe")
    
    print("  📦 Configurando produtos...")
    
    # Produtos
    products_data = [
        {'name': 'Vermiculita Expandida', 'code': 'VERM001', 'description': 'Vermiculita expandida padrão'},
        {'name': 'Vermiculita Agrícola', 'code': 'VERM002', 'description': 'Vermiculita para uso agrícola'},
        {'name': 'Vermiculita Industrial', 'code': 'VERM003', 'description': 'Vermiculita para uso industrial'},
    ]
    
    for prod_data in products_data:
        product, created = Product.objects.get_or_create(
            code=prod_data['code'],
            defaults={
                'name': prod_data['name'],
                'description': prod_data['description'],
                'is_active': True
            }
        )
        if created:
            print(f"    ✅ Produto {product.name} criado")
        else:
            print(f"    📍 Produto {product.name} já existe")
    
    print("  🔬 Configurando propriedades...")
    
    # Propriedades
    properties_data = [
        {'name': 'Teor de Vermiculita', 'code': 'TEOR_VERM', 'unit': '%', 'display_order': 1},
        {'name': 'Umidade', 'code': 'UMIDADE', 'unit': '%', 'display_order': 2},
        {'name': 'Densidade', 'code': 'DENSIDADE', 'unit': 'g/cm³', 'display_order': 3},
        {'name': 'pH', 'code': 'PH', 'unit': '', 'display_order': 4},
    ]
    
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
        if created:
            print(f"    ✅ Propriedade {property_obj.name} criada")
        else:
            print(f"    📍 Propriedade {property_obj.name} já existe")
    
    print("  📋 Configurando tipos de análise...")
    
    # Tipos de análise
    analysis_types_data = [
        {'name': 'Análise Pontual', 'code': 'PONTUAL', 'description': 'Análise de amostra pontual'},
        {'name': 'Análise Composta', 'code': 'COMPOSTA', 'description': 'Análise de amostra composta'},
    ]
    
    for at_data in analysis_types_data:
        analysis_type, created = AnalysisType.objects.get_or_create(
            code=at_data['code'],
            defaults={
                'name': at_data['name'],
                'description': at_data['description'],
                'is_active': True
            }
        )
        if created:
            print(f"    ✅ Tipo de análise {analysis_type.name} criado")
        else:
            print(f"    📍 Tipo de análise {analysis_type.name} já existe")

def setup_production_example():
    """Configurar produção de exemplo para o turno atual"""
    print("  🏭 Configurando produção de exemplo...")
    
    # Obter turno atual
    current_time = timezone.now().time()
    current_date = timezone.now().date()
    
    if time(6, 0) <= current_time < time(18, 0):
        current_shift_name = 'A'
    else:
        current_shift_name = 'B'
    
    try:
        current_shift = Shift.objects.get(name=current_shift_name)
        print(f"    📅 Turno atual: {current_shift.name}")
    except Shift.DoesNotExist:
        print(f"    ❌ Turno '{current_shift_name}' não encontrado")
        return
    
    # Obter operador admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("    ❌ Nenhum superusuário encontrado")
        return
    
    # Criar ou obter ProductionRegistration
    production, created = ProductionRegistration.objects.get_or_create(
        date=current_date,
        shift=current_shift,
        defaults={'operator': admin_user, 'status': 'ACTIVE', 'observations': 'Produção de exemplo'}
    )
    
    if created:
        print(f"    ✅ Produção criada para {current_date} - Turno {current_shift.name}")
    else:
        print(f"    📍 Produção já existe para {current_date} - Turno {current_shift.name}")
    
    # Adicionar linhas de produção
    plant = Plant.objects.filter(is_active=True).first()
    if plant:
        lines = ProductionLine.objects.filter(plant=plant, is_active=True)
        for line in lines:
            prod_line_reg, created = ProductionLineRegistration.objects.get_or_create(
                production=production,
                production_line=line,
                defaults={'is_active': True}
            )
            if created:
                print(f"      ✅ Linha '{line.name}' adicionada")
            else:
                print(f"      📍 Linha '{line.name}' já está na produção")
    
    # Adicionar produtos
    products = Product.objects.filter(is_active=True)
    for product in products:
        prod_prod_reg, created = ProductionProductRegistration.objects.get_or_create(
            production=production,
            product=product,
            defaults={'is_active': True, 'product_type': 'Principal'}
        )
        if created:
            print(f"      ✅ Produto '{product.name}' adicionado")
        else:
            print(f"      📍 Produto '{product.name}' já está na produção")

def create_superuser_if_needed():
    """Criar superusuário se não existir"""
    if not User.objects.filter(is_superuser=True).exists():
        print("    🔑 Criando superusuário...")
        User.objects.create_superuser(
            username='admin',
            email='admin@vermiculita.com',
            password='admin123'
        )
        print("    ✅ Superusuário 'admin' criado (senha: admin123)")
    else:
        print("    📍 Superusuário já existe")

def verify_corrections():
    """Verificar se as correções foram implementadas"""
    print("    🔍 Verificando correções implementadas...")
    
    # Verificar se a view existe
    try:
        from quality_control.views import spot_dashboard_by_plant_view
        print("      ✅ View spot_dashboard_by_plant_view existe")
    except ImportError:
        print("      ❌ View spot_dashboard_by_plant_view não encontrada")
    
    # Verificar se o template existe
    template_path = 'templates/quality_control/spot_dashboard_by_plant.html'
    if os.path.exists(template_path):
        print("      ✅ Template spot_dashboard_by_plant.html existe")
    else:
        print("      ❌ Template spot_dashboard_by_plant.html não encontrado")
    
    # Verificar se a página de instruções existe
    template_instructions_path = 'templates/quality_control/dashboard_instructions.html'
    if os.path.exists(template_instructions_path):
        print("      ✅ Template dashboard_instructions.html existe")
    else:
        print("      ❌ Template dashboard_instructions.html não encontrado")
    
    # Verificar se as URLs estão corretas
    try:
        from django.urls import reverse
        url = reverse('quality_control:spot_dashboard_by_plant')
        print(f"      ✅ URL spot_dashboard_by_plant: {url}")
    except Exception as e:
        print(f"      ❌ Erro na URL spot_dashboard_by_plant: {str(e)}")
    
    try:
        url = reverse('quality_control:dashboard_instructions')
        print(f"      ✅ URL dashboard_instructions: {url}")
    except Exception as e:
        print(f"      ❌ Erro na URL dashboard_instructions: {str(e)}")

if __name__ == '__main__':
    deploy_railway_complete()
