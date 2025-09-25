#!/usr/bin/env python
"""
Script para testar a API do dashboard
"""

import os
import sys
import requests
import json

print("🔍 TESTANDO API DO DASHBOARD")
print("=" * 50)

try:
    # Testar a API do dashboard
    response = requests.get('http://localhost:8000/qc/dashboard-data/')
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API respondeu com sucesso!")
        
        if data.get('success'):
            totals = data.get('totals', {})
            
            print(f"\n📊 DADOS DO DASHBOARD:")
            print(f"   Total análises pontuais: {totals.get('spot_analyses', 0)}")
            print(f"   Total amostras compostas: {totals.get('composite_samples', 0)}")
            print(f"   Total reprovações: {totals.get('total_rejections', 0)}")
            print(f"   Total alertas: {totals.get('total_alerts', 0)}")
            print(f"   Total aprovadas: {totals.get('total_approved', 0)}")
            print(f"   Reprovações hoje: {totals.get('today_rejections', 0)}")
            print(f"   Alertas hoje: {totals.get('today_alerts', 0)}")
            
            # Verificar se os dados estão corretos
            if totals.get('total_rejections', 0) > 0:
                print("\n✅ O dashboard deveria mostrar reprovações!")
            else:
                print("\n❌ O dashboard não tem reprovações para mostrar")
                print("💡 Isso pode ser o problema - não há dados de reprovação")
            
        else:
            print("❌ API retornou success=False")
            print(f"Resposta: {data}")
    else:
        print(f"❌ Erro na API: {response.status_code}")
        print(f"Resposta: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Não foi possível conectar ao servidor")
    print("💡 Certifique-se de que o servidor está rodando em http://localhost:8000")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "="*50)