#!/usr/bin/env python
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.views import spot_dashboard_by_plant_view
from django.test import RequestFactory
from django.contrib.auth.models import User

print("🔍 Debugando View...")

factory = RequestFactory()
request = factory.get('/qc/dashboard/spot/by-plant/')
user = User.objects.first()
request.user = user

try:
    print("Chamando view...")
    response = spot_dashboard_by_plant_view(request)
    print(f"Status: {response.status_code}")
    print(f"Tipo: {type(response)}")
    
    # Se for HttpResponse, verificar o conteúdo
    if hasattr(response, 'content'):
        content = response.content.decode('utf-8')
        if 'error' in content.lower() or 'exception' in content.lower():
            print("❌ Erro encontrado no conteúdo:")
            print(content[:500])
        else:
            print("✅ Conteúdo parece OK")
            print(f"Tamanho: {len(content)} caracteres")
    
except Exception as e:
    print(f"❌ Erro na view: {str(e)}")
    import traceback
    traceback.print_exc()

print("✅ Debug concluído!")
