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

print("🧪 Testando Dashboard...")

factory = RequestFactory()
request = factory.get('/qc/dashboard/spot/by-plant/')
user = User.objects.first()
request.user = user

try:
    response = spot_dashboard_by_plant_view(request)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ View executada com sucesso!")
        print(f"Tipo de resposta: {type(response)}")
        
        # Verificar se é um TemplateResponse
        if hasattr(response, 'context_data'):
            context = response.context_data
            plants_data = context.get('plants_data', [])
            production = context.get('production')
            
            print(f"Plantas: {len(plants_data)}")
            print(f"Produção: {production}")
            
            if plants_data:
                for i, plant_data in enumerate(plants_data):
                    plant = plant_data['plant']
                    products_count = len(plant_data['products'])
                    print(f"  {i+1}. {plant.name} - {products_count} produtos")
            else:
                print("  Nenhuma planta encontrada")
        else:
            print("  Resposta não é TemplateResponse")
    else:
        print(f"Erro: {response.status_code}")
        
except Exception as e:
    print(f"Erro: {str(e)}")
    import traceback
    traceback.print_exc()

print("✅ Teste concluído!")
