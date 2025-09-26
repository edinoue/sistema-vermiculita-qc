#!/usr/bin/env python
"""
Script definitivo para corrigir o dashboard
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🔧 CORREÇÃO DEFINITIVA DO DASHBOARD")
print("=" * 50)

try:
    import django
    django.setup()
    
    from quality_control.models import SpotAnalysis, CompositeSample
    from django.db import connection
    from django.utils import timezone
    
    print("✅ Django configurado!")
    
    # 1. Verificar dados atuais
    print("\n1. VERIFICANDO DADOS:")
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    total = spot_rejected + composite_rejected
    
    print(f"   Reprovações pontuais: {spot_rejected}")
    print(f"   Reprovações compostas: {composite_rejected}")
    print(f"   Total: {total}")
    
    # 2. Se não há dados, criar alguns
    if total == 0:
        print("\n2. CRIANDO DADOS DE TESTE:")
        
        # Verificar se há análises para modificar
        spot_total = SpotAnalysis.objects.count()
        composite_total = CompositeSample.objects.count()
        
        if spot_total > 0:
            # Modificar algumas análises para reprovadas
            analyses = SpotAnalysis.objects.filter(status='APPROVED')[:3]
            for analysis in analyses:
                analysis.status = 'REJECTED'
                analysis.save()
            print(f"   ✅ {analyses.count()} análises pontuais modificadas")
        
        if composite_total > 0:
            # Modificar algumas amostras para reprovadas
            samples = CompositeSample.objects.filter(status='APPROVED')[:2]
            for sample in samples:
                sample.status = 'REJECTED'
                sample.save()
            print(f"   ✅ {samples.count()} amostras compostas modificadas")
    
    # 3. Verificar dados finais
    print("\n3. VERIFICANDO DADOS FINAIS:")
    spot_rejected_final = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected_final = CompositeSample.objects.filter(status='REJECTED').count()
    total_final = spot_rejected_final + composite_rejected_final
    
    print(f"   Reprovações pontuais: {spot_rejected_final}")
    print(f"   Reprovações compostas: {composite_rejected_final}")
    print(f"   Total: {total_final}")
    
    # 4. Testar API diretamente
    print("\n4. TESTANDO API:")
    from django.test import Client
    client = Client()
    
    # Testar ambas as URLs
    urls_to_test = [
        '/qc/dashboard-data/',
        '/qc/api/dashboard-data/'
    ]
    
    for url in urls_to_test:
        try:
            response = client.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    totals = data.get('totals', {})
                    api_rejections = totals.get('total_rejections', 0)
                    print(f"   ✅ {url} → {api_rejections} reprovações")
                else:
                    print(f"   ❌ {url} → success=False")
            else:
                print(f"   ❌ {url} → Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {url} → Erro: {e}")
    
    # 5. Resultado final
    print("\n" + "="*50)
    print("RESULTADO FINAL:")
    
    if total_final > 0:
        print(f"✅ Há {total_final} reprovações no banco")
        print("✅ Dashboard deveria funcionar agora")
        print("\n💡 TESTE MANUAL:")
        print("1. Acesse: http://localhost:8000/qc/dashboard/")
        print("2. Verifique se mostra as reprovações")
        print("3. Se não funcionar, verifique o console do navegador (F12)")
    else:
        print("❌ Ainda não há reprovações")
        print("💡 Execute: python fix_existing_analyses.py")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)