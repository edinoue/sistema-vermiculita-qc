#!/usr/bin/env python
"""
Script completo para debugar o dashboard
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🔍 DEBUG COMPLETO DO DASHBOARD")
print("=" * 50)

try:
    import django
    django.setup()
    
    from quality_control.models import SpotAnalysis, CompositeSample
    from django.utils import timezone
    from django.test import Client
    import json
    
    print("✅ Django configurado!")
    
    # 1. Verificar dados no banco
    print("\n1. DADOS NO BANCO:")
    
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    total_rejections = spot_rejected + composite_rejected
    
    print(f"   Reprovações pontuais: {spot_rejected}")
    print(f"   Reprovações compostas: {composite_rejected}")
    print(f"   Total reprovações: {total_rejections}")
    
    # 2. Testar a API diretamente
    print("\n2. TESTANDO API DO DASHBOARD:")
    
    client = Client()
    response = client.get('/qc/dashboard-data/')
    
    print(f"   Status da resposta: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   Success: {data.get('success', False)}")
            
            if data.get('success'):
                totals = data.get('totals', {})
                print(f"   Total reprovações da API: {totals.get('total_rejections', 0)}")
                print(f"   Reprovações hoje da API: {totals.get('today_rejections', 0)}")
                
                if totals.get('total_rejections', 0) > 0:
                    print("   ✅ API está retornando reprovações corretamente")
                else:
                    print("   ❌ API não está retornando reprovações")
            else:
                print("   ❌ API retornou success=False")
                print(f"   Resposta: {data}")
        except Exception as e:
            print(f"   ❌ Erro ao decodificar JSON: {e}")
            print(f"   Resposta: {response.content}")
    else:
        print(f"   ❌ Erro na API: {response.status_code}")
        print(f"   Resposta: {response.content}")
    
    # 3. Verificar se há problemas de URL
    print("\n3. VERIFICANDO URLS:")
    
    from django.urls import reverse
    try:
        url = reverse('quality_control:dashboard_data_api')
        print(f"   URL da API: {url}")
    except Exception as e:
        print(f"   ❌ Erro ao obter URL: {e}")
    
    # 4. Verificar se a view existe
    print("\n4. VERIFICANDO VIEW:")
    
    from quality_control.views import dashboard_data_api
    print(f"   View existe: {dashboard_data_api is not None}")
    
    # 5. Resultado final
    print("\n" + "="*50)
    print("DIAGNÓSTICO:")
    
    if total_rejections > 0:
        print("✅ Há reprovações no banco de dados")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('totals', {}).get('total_rejections', 0) > 0:
                print("✅ API está funcionando corretamente")
                print("🔍 O problema pode estar no frontend (JavaScript)")
                print("\n💡 SOLUÇÕES:")
                print("1. Abra o console do navegador (F12)")
                print("2. Recarregue a página do dashboard")
                print("3. Verifique se há erros no console")
                print("4. Verifique se a API está sendo chamada")
            else:
                print("❌ API não está retornando reprovações")
                print("🔍 Problema na lógica da API")
        else:
            print("❌ API não está respondendo")
            print("🔍 Problema na configuração da API")
    else:
        print("❌ Não há reprovações no banco de dados")
        print("💡 Execute o script fix_rejections_final.py primeiro")
    
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)

