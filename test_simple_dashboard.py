#!/usr/bin/env python
"""
Script para testar a nova view simplificada do dashboard
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from quality_control.views_dashboard_simple import spot_dashboard_by_line_view_simple

def test_simple_dashboard():
    """Testar a nova view simplificada"""
    print("🧪 Testando dashboard simplificado...")
    
    # Criar request fake
    factory = RequestFactory()
    request = factory.get('/qc/dashboard/spot/')
    
    # Criar usuário fake
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    request.user = user
    
    try:
        # Chamar a view
        response = spot_dashboard_by_line_view_simple(request)
        
        print(f"✅ Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Dashboard carregado com sucesso!")
            
            # Verificar se há dados no contexto
            context = response.context_data
            if context:
                lines_data = context.get('lines_data', [])
                properties = context.get('properties', [])
                stats = context.get('stats', {})
                
                print(f"📊 Linhas encontradas: {len(lines_data)}")
                print(f"📊 Propriedades encontradas: {len(properties)}")
                print(f"📊 Estatísticas: {stats}")
                
                for i, line_data in enumerate(lines_data):
                    line = line_data['line']
                    plant = line_data['plant']
                    products = line_data['products']
                    
                    print(f"\n🔧 Linha {i+1}: {line.name} (Planta: {plant.name})")
                    print(f"   Produtos: {len(products)}")
                    
                    for j, product_data in enumerate(products):
                        product = product_data['product']
                        sample = product_data['sample']
                        status = product_data['status']
                        
                        print(f"   📦 Produto {j+1}: {product.name}")
                        print(f"      Status: {status}")
                        if sample:
                            print(f"      Amostra: {sample.id} (Seq: {sample.sample_sequence})")
                            print(f"      Observações: {sample.observations}")
                            print(f"      Horário: {sample.sample_time}")
                        else:
                            print(f"      Amostra: Nenhuma")
        else:
            print(f"❌ Erro no dashboard: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_simple_dashboard()
