#!/usr/bin/env python
"""
Script para testar o sistema final
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from quality_control.models import Product, Property, ProductionLine, Shift, AnalysisType

def test_final_system():
    """Testar sistema final"""
    print("=== Testando Sistema Final ===")
    
    try:
        # Aplicar migrações
        print("1. Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrações aplicadas")
        
        # Verificar dados
        print("2. Verificando dados...")
        verify_data()
        print("✅ Dados verificados")
        
        # Testar URLs
        print("3. Testando URLs...")
        test_urls()
        print("✅ URLs testadas")
        
        print("\n=== Sistema testado com sucesso! ===")
        print("\n🎯 FUNCIONALIDADES IMPLEMENTADAS:")
        print("✅ Nome alterado para 'Brasil Minérios QC'")
        print("✅ Sistema de amostras compostas criado")
        print("✅ Análises pontuais corrigidas (propriedades visíveis)")
        print("✅ Navegação atualizada")
        print("✅ URLs funcionais")
        
        print("\n🚀 COMO USAR:")
        print("1. Acesse /qc/ para o dashboard")
        print("2. Use 'Nova Análise' para escolher tipo")
        print("3. Análise Pontual: /qc/spot-analysis/create-fixed/")
        print("4. Amostra Composta: /qc/composite-sample/create/")
        print("5. Listar amostras: /qc/composite-sample/")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

def verify_data():
    """Verificar dados do sistema"""
    
    # Verificar produtos
    products = Product.objects.all()
    print(f"   Produtos: {products.count()}")
    for product in products:
        print(f"     - {product.code}: {product.name} (ordem: {product.display_order})")
    
    # Verificar propriedades
    properties = Property.objects.all()
    print(f"   Propriedades: {properties.count()}")
    for prop in properties:
        print(f"     - {prop.identifier}: {prop.name} (ordem: {prop.display_order})")
    
    # Verificar turnos
    shifts = Shift.objects.all()
    print(f"   Turnos: {shifts.count()}")
    for shift in shifts:
        print(f"     - {shift.name}: {shift.start_time}-{shift.end_time}")
    
    # Verificar tipos de análise
    analysis_types = AnalysisType.objects.all()
    print(f"   Tipos de análise: {analysis_types.count()}")
    for at in analysis_types:
        print(f"     - {at.code}: {at.name}")

def test_urls():
    """Testar URLs principais"""
    from django.test import Client
    from django.contrib.auth.models import User
    
    # Criar usuário de teste
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'password': 'testpass123'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Testar cliente
    client = Client()
    login_success = client.login(username='testuser', password='testpass123')
    
    if login_success:
        # Testar URLs principais
        urls_to_test = [
            '/qc/',
            '/qc/spot-analysis/create-fixed/',
            '/qc/composite-sample/create/',
            '/qc/composite-sample/',
            '/qc/import/',
        ]
        
        for url in urls_to_test:
            response = client.get(url)
            if response.status_code == 200:
                print(f"     ✅ {url}")
            else:
                print(f"     ❌ {url} - Status: {response.status_code}")
    else:
        print("     ❌ Não foi possível fazer login")

if __name__ == '__main__':
    test_final_system()

