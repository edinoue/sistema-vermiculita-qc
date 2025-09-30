#!/usr/bin/env python
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from quality_control.views import spot_dashboard_by_line_view

print("🧪 Testando Dashboard...")

factory = RequestFactory()
request = factory.get('/qc/dashboard/spot/')
user = User.objects.first()
if not user:
    user = User.objects.create_user('test', 'test@test.com', 'test123')
request.user = user

try:
    response = spot_dashboard_by_line_view(request)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Dashboard funcionando")
        # Verificar se há dados no contexto
        if hasattr(response, 'context_data'):
            context = response.context_data
            lines_data = context.get('lines_data', [])
            production = context.get('production')
            print(f"  - Linhas: {len(lines_data)}")
            print(f"  - Produção: {production}")
            
            if lines_data:
                for i, line_data in enumerate(lines_data):
                    line = line_data['line']
                    products = line_data['products']
                    print(f"    {i+1}. {line.name} - {len(products)} produtos")
            else:
                print("  ⚠️  Nenhuma linha encontrada")
        else:
            print("  ⚠️  Sem context_data")
    else:
        print(f"❌ Erro: {response.status_code}")
        
except Exception as e:
    print(f"❌ Erro: {str(e)}")
    import traceback
    traceback.print_exc()

print("✅ Teste concluído!")
