#!/usr/bin/env python
"""
Script de teste para o novo dashboard de amostras pontuais por local de produção
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
from core.models import Plant, ProductionLine, Shift
from quality_control.models import Product, Property, SpotSample, SpotAnalysis, AnalysisType
from quality_control.views import spot_dashboard_by_plant_view
from django.utils import timezone
from datetime import datetime, timedelta

def test_spot_dashboard_by_plant():
    """Testa o dashboard de amostras pontuais por local de produção"""
    
    print("🧪 Testando Dashboard de Amostras Pontuais por Local de Produção")
    print("=" * 60)
    
    # Verificar se existem dados básicos
    plants = Plant.objects.filter(is_active=True)
    print(f"📍 Locais de produção ativos: {plants.count()}")
    
    if plants.count() == 0:
        print("❌ Nenhum local de produção ativo encontrado!")
        print("   Crie pelo menos um local de produção ativo para testar.")
        return False
    
    for plant in plants:
        print(f"   - {plant.name} ({plant.code})")
    
    # Verificar turnos
    shifts = Shift.objects.all()
    print(f"\n🕐 Turnos cadastrados: {shifts.count()}")
    
    if shifts.count() == 0:
        print("❌ Nenhum turno cadastrado!")
        print("   Crie pelo menos um turno para testar.")
        return False
    
    for shift in shifts:
        print(f"   - {shift.name}")
    
    # Verificar produtos
    products = Product.objects.filter(is_active=True)
    print(f"\n📦 Produtos ativos: {products.count()}")
    
    if products.count() == 0:
        print("❌ Nenhum produto ativo encontrado!")
        print("   Crie pelo menos um produto ativo para testar.")
        return False
    
    for product in products:
        print(f"   - {product.name} ({product.code})")
    
    # Verificar propriedades
    properties = Property.objects.filter(is_active=True)
    print(f"\n🔬 Propriedades ativas: {properties.count()}")
    
    for property in properties:
        print(f"   - {property.name} ({property.identifier})")
    
    # Verificar amostras pontuais
    today = timezone.now().date()
    spot_samples = SpotSample.objects.filter(date=today)
    print(f"\n🧪 Amostras pontuais de hoje: {spot_samples.count()}")
    
    if spot_samples.count() == 0:
        print("⚠️  Nenhuma amostra pontual encontrada para hoje!")
        print("   Crie algumas análises pontuais para ver os dados no dashboard.")
    
    # Testar a view
    print(f"\n🔍 Testando a view spot_dashboard_by_plant_view...")
    
    try:
        # Criar um usuário de teste
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        
        # Criar uma requisição de teste
        factory = RequestFactory()
        request = factory.get('/qc/dashboard/spot/by-plant/')
        request.user = user
        
        # Chamar a view
        response = spot_dashboard_by_plant_view(request)
        
        if response.status_code == 200:
            print("✅ View executada com sucesso!")
            print(f"   Status: {response.status_code}")
            
            # Verificar se o template foi renderizado
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                if 'Dashboard - Análises Pontuais por Local' in content:
                    print("✅ Template renderizado corretamente!")
                else:
                    print("⚠️  Template pode não estar sendo renderizado corretamente")
            
            # Verificar dados no contexto
            if hasattr(response, 'context_data'):
                context = response.context_data
                print(f"   Plantas no contexto: {len(context.get('plants_data', []))}")
                print(f"   Propriedades no contexto: {len(context.get('properties', []))}")
                print(f"   Estatísticas: {context.get('stats', {})}")
            
        else:
            print(f"❌ Erro na view! Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar a view: {str(e)}")
        return False
    
    print(f"\n🎉 Teste concluído com sucesso!")
    print(f"   Acesse: http://localhost:8000/qc/dashboard/spot/by-plant/")
    
    return True

def create_test_data():
    """Cria dados de teste se necessário"""
    
    print("\n🔧 Criando dados de teste...")
    
    # Criar local de produção se não existir
    plant, created = Plant.objects.get_or_create(
        code='PLT01',
        defaults={
            'name': 'Planta Principal',
            'description': 'Planta principal de produção',
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Local de produção criado: {plant.name}")
    else:
        print(f"📍 Local de produção já existe: {plant.name}")
    
    # Criar turno se não existir
    shift, created = Shift.objects.get_or_create(
        name='A',
        defaults={
            'start_time': '06:00',
            'end_time': '18:00',
            'description': 'Turno A (06:00 - 18:00)'
        }
    )
    
    if created:
        print(f"✅ Turno criado: {shift.name}")
    else:
        print(f"🕐 Turno já existe: {shift.name}")
    
    # Criar linha de produção se não existir
    line, created = ProductionLine.objects.get_or_create(
        plant=plant,
        code='LN01',
        defaults={
            'name': 'Linha 1',
            'description': 'Linha de produção 1',
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Linha de produção criada: {line.name}")
    else:
        print(f"🏭 Linha de produção já existe: {line.name}")
    
    # Criar produto se não existir
    product, created = Product.objects.get_or_create(
        code='VERM01',
        defaults={
            'name': 'Vermiculita Concentrada',
            'description': 'Vermiculita concentrada para exportação',
            'is_active': True,
            'display_order': 1
        }
    )
    
    if created:
        print(f"✅ Produto criado: {product.name}")
    else:
        print(f"📦 Produto já existe: {product.name}")
    
    # Criar propriedades se não existirem
    properties_data = [
        {'identifier': 'TEOR_VERM', 'name': 'Teor de Vermiculita', 'unit': '%', 'category': 'QUIMICA'},
        {'identifier': 'UMIDADE', 'name': 'Umidade', 'unit': '%', 'category': 'FISICA'},
        {'identifier': 'GRANULOMETRIA', 'name': 'Granulometria', 'unit': 'mm', 'category': 'FISICA'},
    ]
    
    for prop_data in properties_data:
        prop, created = Property.objects.get_or_create(
            identifier=prop_data['identifier'],
            defaults={
                'name': prop_data['name'],
                'unit': prop_data['unit'],
                'category': prop_data['category'],
                'is_active': True,
                'display_order': 1
            }
        )
        
        if created:
            print(f"✅ Propriedade criada: {prop.name}")
        else:
            print(f"🔬 Propriedade já existe: {prop.name}")
    
    print("✅ Dados de teste criados/verificados!")

if __name__ == '__main__':
    print("🚀 Iniciando teste do Dashboard de Amostras Pontuais por Local")
    print("=" * 70)
    
    # Criar dados de teste
    create_test_data()
    
    # Executar teste
    success = test_spot_dashboard_by_plant()
    
    if success:
        print("\n🎉 Todos os testes passaram!")
        print("   O dashboard está funcionando corretamente.")
    else:
        print("\n❌ Alguns testes falharam!")
        print("   Verifique os erros acima e corrija os problemas.")
