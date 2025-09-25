#!/usr/bin/env python
"""
Script para corrigir exibição de reprovações no dashboard
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import SpotAnalysis, CompositeSample, CompositeSampleResult
from django.utils import timezone
from datetime import timedelta

def fix_dashboard_rejections_display():
    """Corrigir exibição de reprovações no dashboard"""
    
    print("🔧 CORRIGINDO EXIBIÇÃO DE REPROVAÇÕES NO DASHBOARD")
    print("=" * 60)
    
    # 1. Verificar análises existentes
    print("\n1. VERIFICANDO ANÁLISES EXISTENTES:")
    
    spot_total = SpotAnalysis.objects.count()
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    print(f"   Análises pontuais: {spot_total} (reprovadas: {spot_rejected})")
    
    composite_total = CompositeSample.objects.count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    print(f"   Amostras compostas: {composite_total} (reprovadas: {composite_rejected})")
    
    # 2. Forçar recálculo de status (se necessário)
    print("\n2. FORÇANDO RECÁLCULO DE STATUS:")
    
    # Recálculo para análises pontuais
    spot_analyses = SpotAnalysis.objects.all()
    spot_updated = 0
    for analysis in spot_analyses:
        old_status = analysis.status
        analysis.save()  # Isso vai recalcular o status
        if analysis.status != old_status:
            spot_updated += 1
            print(f"   - Análise {analysis.id}: {old_status} → {analysis.status}")
    
    print(f"   ✅ {spot_updated} análises pontuais atualizadas")
    
    # Recálculo para amostras compostas
    composite_samples = CompositeSample.objects.all()
    composite_updated = 0
    for sample in composite_samples:
        old_status = sample.status
        sample.update_status()  # Método que criamos
        if sample.status != old_status:
            composite_updated += 1
            print(f"   - Amostra {sample.id}: {old_status} → {sample.status}")
    
    print(f"   ✅ {composite_updated} amostras compostas atualizadas")
    
    # 3. Verificar totais após recálculo
    print("\n3. VERIFICANDO TOTAIS APÓS RECÁLCULO:")
    
    spot_rejected_new = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected_new = CompositeSample.objects.filter(status='REJECTED').count()
    total_rejections = spot_rejected_new + composite_rejected_new
    
    print(f"   Análises pontuais reprovadas: {spot_rejected_new}")
    print(f"   Amostras compostas reprovadas: {composite_rejected_new}")
    print(f"   Total reprovações: {total_rejections}")
    
    # 4. Verificar dados de hoje
    print("\n4. VERIFICANDO DADOS DE HOJE:")
    today = timezone.now().date()
    
    spot_today = SpotAnalysis.objects.filter(
        sample_time__date=today,
        status='REJECTED'
    ).count()
    
    composite_today = CompositeSample.objects.filter(
        date=today,
        status='REJECTED'
    ).count()
    
    print(f"   Reprovações hoje: {spot_today + composite_today}")
    
    # 5. Testar API do dashboard
    print("\n5. TESTANDO API DO DASHBOARD:")
    from django.test import Client
    from django.contrib.auth.models import User
    
    client = Client()
    
    # Criar usuário de teste
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'is_staff': True}
    )
    if created:
        user.set_password('testpass')
        user.save()
    
    # Fazer login e testar API
    client.login(username='testuser', password='testpass')
    response = client.get('/qc/dashboard-data/')
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            totals = data.get('totals', {})
            api_rejections = totals.get('total_rejections', 0)
            api_today = totals.get('today_rejections', 0)
            
            print(f"   API retorna {api_rejections} reprovações totais")
            print(f"   API retorna {api_today} reprovações hoje")
            
            if api_rejections == total_rejections:
                print("   ✅ API está retornando dados corretos")
            else:
                print("   ⚠️  API não está retornando dados corretos")
                print(f"   - Esperado: {total_rejections}, Recebido: {api_rejections}")
        else:
            print("   ❌ API retornou success=False")
    else:
        print(f"   ❌ API retornou status {response.status_code}")
    
    print("\n✅ CORREÇÃO CONCLUÍDA!")
    
    if total_rejections > 0:
        print(f"   ✅ {total_rejections} reprovações encontradas")
        print("   - Dashboard deve mostrar dados corretos")
        print("   - Recarregue a página para ver as mudanças")
    else:
        print("   ⚠️  Nenhuma reprovação encontrada")
        print("   - Verifique se as amostras foram realmente reprovadas")
        print("   - Verifique se as especificações estão configuradas")

if __name__ == '__main__':
    fix_dashboard_rejections_display()

