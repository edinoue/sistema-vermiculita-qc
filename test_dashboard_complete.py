#!/usr/bin/env python
"""
Script completo para testar o dashboard
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import SpotAnalysis, CompositeSample, CompositeSampleResult, Product, Property, Specification
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

def test_dashboard_complete():
    """Teste completo do dashboard"""
    
    print("🔍 TESTE COMPLETO DO DASHBOARD")
    print("=" * 60)
    
    # 1. Verificar dados existentes
    print("\n1. VERIFICANDO DADOS EXISTENTES:")
    
    spot_total = SpotAnalysis.objects.count()
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    spot_approved = SpotAnalysis.objects.filter(status='APPROVED').count()
    spot_alert = SpotAnalysis.objects.filter(status='ALERT').count()
    
    print(f"   Análises pontuais: {spot_total}")
    print(f"   - Reprovadas: {spot_rejected}")
    print(f"   - Aprovadas: {spot_approved}")
    print(f"   - Alertas: {spot_alert}")
    
    composite_total = CompositeSample.objects.count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    composite_approved = CompositeSample.objects.filter(status='APPROVED').count()
    composite_alert = CompositeSample.objects.filter(status='ALERT').count()
    
    print(f"   Amostras compostas: {composite_total}")
    print(f"   - Reprovadas: {composite_rejected}")
    print(f"   - Aprovadas: {composite_approved}")
    print(f"   - Alertas: {composite_alert}")
    
    # 2. Criar dados de teste se necessário
    print("\n2. CRIANDO DADOS DE TESTE:")
    
    if spot_rejected == 0 and composite_rejected == 0:
        print("   ⚠️  Nenhuma reprovação encontrada, criando dados de teste...")
        
        # Criar usuário de teste
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com', 'is_staff': True}
        )
        if created:
            user.set_password('testpass')
            user.save()
            print("   ✅ Usuário de teste criado")
        
        # Criar produto de teste
        product, created = Product.objects.get_or_create(
            code='TESTE',
            defaults={'name': 'Produto de Teste', 'is_active': True}
        )
        if created:
            print("   ✅ Produto de teste criado")
        
        # Criar propriedade de teste
        property_obj, created = Property.objects.get_or_create(
            identifier='TESTE_PROP',
            defaults={
                'name': 'Propriedade de Teste',
                'unit': '%',
                'category': 'QUIMICA',
                'data_type': 'DECIMAL',
                'is_active': True
            }
        )
        if created:
            print("   ✅ Propriedade de teste criada")
        
        # Criar especificação que vai causar reprovação
        spec, created = Specification.objects.get_or_create(
            product=product,
            property=property_obj,
            defaults={
                'lsl': Decimal('80.0'),  # Limite inferior 80%
                'usl': Decimal('90.0'),  # Limite superior 90%
                'target': Decimal('85.0'),  # Alvo 85%
                'is_active': True
            }
        )
        if created:
            print("   ✅ Especificação de teste criada")
        
        # Criar análise pontual que será reprovada
        from core.models import Shift, ProductionLine
        
        shift = Shift.objects.first()
        production_line = ProductionLine.objects.first()
        
        if shift and production_line:
            analysis = SpotAnalysis.objects.create(
                product=product,
                property=property_obj,
                production_line=production_line,
                shift=shift,
                date=timezone.now().date(),
                sequence=1,
                value=Decimal('75.0'),  # Valor abaixo do limite (80%)
                unit='%',
                test_method='Método de teste',
                sample_time=timezone.now(),
                operator=user
            )
            print(f"   ✅ Análise pontual criada (ID: {analysis.id}, Status: {analysis.status})")
        
        # Criar amostra composta que será reprovada
        sample = CompositeSample.objects.create(
            product=product,
            production_line=production_line,
            shift=shift,
            date=timezone.now().date(),
            collection_time=timezone.now(),
            sequence=1,
            status='APPROVED'  # Será atualizado pelo resultado
        )
        
        # Criar resultado que será reprovado
        result = CompositeSampleResult.objects.create(
            composite_sample=sample,
            property=property_obj,
            value=Decimal('75.0'),  # Valor abaixo do limite (80%)
            unit='%',
            test_method='Método de teste'
        )
        
        # Atualizar status da amostra
        sample.update_status()
        print(f"   ✅ Amostra composta criada (ID: {sample.id}, Status: {sample.status})")
        print(f"   ✅ Resultado criado (ID: {result.id}, Status: {result.status})")
    
    # 3. Verificar totais após criação
    print("\n3. VERIFICANDO TOTAIS APÓS CRIAÇÃO:")
    
    spot_rejected_new = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected_new = CompositeSample.objects.filter(status='REJECTED').count()
    total_rejections = spot_rejected_new + composite_rejected_new
    
    print(f"   Análises pontuais reprovadas: {spot_rejected_new}")
    print(f"   Amostras compostas reprovadas: {composite_rejected_new}")
    print(f"   Total reprovações: {total_rejections}")
    
    # 4. Testar API do dashboard
    print("\n4. TESTANDO API DO DASHBOARD:")
    
    from django.test import Client
    
    client = Client()
    
    # Fazer login
    login_success = client.login(username='testuser', password='testpass')
    if not login_success:
        print("   ❌ Falha no login")
        return
    
    # Testar ambas as URLs
    urls_to_test = [
        '/qc/api/dashboard-data/',
        '/qc/dashboard-data/'
    ]
    
    for url in urls_to_test:
        print(f"\n   Testando URL: {url}")
        response = client.get(url)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    totals = data.get('totals', {})
                    api_rejections = totals.get('total_rejections', 0)
                    api_today = totals.get('today_rejections', 0)
                    
                    print(f"   ✅ API respondeu: {api_rejections} reprovações totais, {api_today} hoje")
                    
                    if api_rejections == total_rejections:
                        print("   ✅ API está retornando dados corretos")
                    else:
                        print(f"   ⚠️  API não está retornando dados corretos (esperado: {total_rejections}, recebido: {api_rejections})")
                else:
                    print("   ❌ API retornou success=False")
            except json.JSONDecodeError as e:
                print(f"   ❌ Erro ao decodificar JSON: {e}")
        else:
            print(f"   ❌ API retornou status {response.status_code}")
    
    print("\n✅ TESTE CONCLUÍDO!")
    
    if total_rejections > 0:
        print(f"   ✅ {total_rejections} reprovações encontradas")
        print("   - Dashboard deve mostrar dados corretos")
        print("   - Recarregue a página para ver as mudanças")
    else:
        print("   ⚠️  Nenhuma reprovação encontrada")
        print("   - Verifique se as especificações estão configuradas")

if __name__ == '__main__':
    test_dashboard_complete()

