#!/usr/bin/env python
"""
Script para testar se o problema de CSRF foi resolvido
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from quality_control.models import AnalysisType, Property

def test_csrf_fix():
    """Testar se o problema de CSRF foi resolvido"""
    print("=== Testando correção de CSRF ===")
    
    try:
        # Criar usuário de teste
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com', 'password': 'testpass123'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print("Usuário de teste criado")
        else:
            print("Usuário de teste já existe")
        
        # Criar tipos de análise se não existirem
        pontual, created = AnalysisType.objects.get_or_create(
            code='PONTUAL',
            defaults={
                'name': 'Análise Pontual',
                'description': 'Análises realizadas diretamente no fluxo de produção',
                'frequency_per_shift': 3,
                'is_active': True
            }
        )
        print(f"Tipo de análise pontual: {'criado' if created else 'já existe'}")
        
        # Testar cliente
        client = Client()
        
        # Fazer login
        login_success = client.login(username='testuser', password='testpass123')
        print(f"Login: {'sucesso' if login_success else 'falhou'}")
        
        if login_success:
            # Testar acesso à página de criação
            response = client.get('/qc/spot-analysis/create-simple/')
            print(f"Acesso à página de criação: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Página de criação acessível")
            else:
                print(f"❌ Erro ao acessar página: {response.status_code}")
                print(f"Conteúdo da resposta: {response.content.decode()[:200]}...")
        else:
            print("❌ Não foi possível fazer login")
        
        print("\n=== Teste concluído! ===")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_csrf_fix()






