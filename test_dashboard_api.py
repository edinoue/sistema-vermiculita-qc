#!/usr/bin/env python
"""
Script para testar a API do dashboard
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_dashboard_api():
    """Testar a API do dashboard"""
    
    print("🔍 TESTANDO API DO DASHBOARD")
    print("=" * 60)
    
    try:
        # 1. Criar cliente de teste
        client = Client()
        
        # 2. Criar usuário de teste (se não existir)
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com', 'is_staff': True}
        )
        if created:
            user.set_password('testpass')
            user.save()
            print("   ✅ Usuário de teste criado")
        else:
            print("   ✅ Usuário de teste já existe")
        
        # 3. Fazer login
        login_success = client.login(username='testuser', password='testpass')
        if login_success:
            print("   ✅ Login realizado com sucesso")
        else:
            print("   ❌ Falha no login")
            return
        
        # 4. Testar API do dashboard
        print("\n4. TESTANDO API DO DASHBOARD:")
        response = client.get('/qc/dashboard-data/')
        
        if response.status_code == 200:
            print("   ✅ API respondeu com sucesso")
            
            try:
                data = response.json()
                print(f"   ✅ JSON válido: {data.get('success', False)}")
                
                if data.get('success'):
                    totals = data.get('totals', {})
                    print(f"\n   DADOS RETORNADOS:")
                    print(f"   - Total análises pontuais: {totals.get('spot_analyses', 0)}")
                    print(f"   - Total amostras compostas: {totals.get('composite_samples', 0)}")
                    print(f"   - Total reprovações: {totals.get('total_rejections', 0)}")
                    print(f"   - Total alertas: {totals.get('total_alerts', 0)}")
                    print(f"   - Total aprovadas: {totals.get('total_approved', 0)}")
                    print(f"   - Reprovações hoje: {totals.get('today_rejections', 0)}")
                    print(f"   - Alertas hoje: {totals.get('today_alerts', 0)}")
                    
                    # Verificar se há dados de reprovação
                    if totals.get('total_rejections', 0) == 0:
                        print("\n   ⚠️  PROBLEMA: API retorna 0 reprovações")
                        print("   - Verifique se há análises com status 'REJECTED'")
                        print("   - Verifique se a API está contando corretamente")
                    else:
                        print(f"\n   ✅ API retorna {totals.get('total_rejections', 0)} reprovações")
                        
                else:
                    print("   ❌ API retornou success=False")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ Erro ao decodificar JSON: {e}")
                print(f"   Resposta: {response.content[:200]}...")
        else:
            print(f"   ❌ API retornou status {response.status_code}")
            print(f"   Resposta: {response.content[:200]}...")
        
        # 5. Testar URL alternativa
        print("\n5. TESTANDO URL ALTERNATIVA:")
        response_alt = client.get('/qc/dashboard-data/')
        
        if response_alt.status_code == 200:
            print("   ✅ URL alternativa funciona")
        else:
            print(f"   ❌ URL alternativa falhou: {response_alt.status_code}")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_dashboard_api()
