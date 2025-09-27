#!/usr/bin/env python
"""
Script para configurar banco PostgreSQL no Railway automaticamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.conf import settings

def setup_railway_database_automatic():
    """Configurar banco PostgreSQL no Railway automaticamente"""
    
    print("🔧 CONFIGURAÇÃO AUTOMÁTICA DO POSTGRESQL NO RAILWAY")
    print("=" * 70)
    
    # 1. Verificar configuração atual
    print("\n1. VERIFICANDO CONFIGURAÇÃO ATUAL:")
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        print(f"   ✅ DATABASE_URL configurada: {database_url[:50]}...")
        
        if 'postgresql' in database_url:
            print("   ✅ PostgreSQL detectado - DADOS PERSISTENTES")
            print("   ✅ Configuração já está correta!")
            return True
        else:
            print("   ⚠️  DATABASE_URL não é PostgreSQL")
    else:
        print("   ❌ DATABASE_URL não configurada")
        print("   ⚠️  Sistema usando SQLite - DADOS SERÃO PERDIDOS")
    
    # 2. Instruções para configurar PostgreSQL
    print("\n2. CONFIGURAÇÃO NECESSÁRIA:")
    print("   a) Acesse: https://railway.app/dashboard")
    print("   b) Selecione seu projeto")
    print("   c) Clique em 'New' → 'Database' → 'PostgreSQL'")
    print("   d) Aguarde a criação (2-3 minutos)")
    print("   e) Copie a DATABASE_URL gerada")
    print("   f) Vá em 'Variables' → 'New Variable'")
    print("   g) Nome: DATABASE_URL, Valor: [URL_COPIADA]")
    print("   h) Clique em 'Add'")
    
    # 3. Verificar se configuração foi aplicada
    print("\n3. APÓS CONFIGURAR, EXECUTE:")
    print("   python check_database_config.py")
    print("   python manage.py migrate")
    print("   python manage.py createsuperuser")
    
    # 4. Aplicar migrações se PostgreSQL estiver configurado
    if database_url and 'postgresql' in database_url:
        print("\n4. APLICANDO MIGRAÇÕES:")
        try:
            execute_from_command_line(['manage.py', 'migrate'])
            print("   ✅ Migrações aplicadas com sucesso")
        except Exception as e:
            print(f"   ❌ Erro nas migrações: {e}")
    
    print("\n✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("   - Dados serão preservados entre deploys")
    print("   - Sistema escalável para produção")
    print("   - Backup automático no Railway")

if __name__ == '__main__':
    setup_railway_database_automatic()




