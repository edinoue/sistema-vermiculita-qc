#!/usr/bin/env python
"""
Script para configurar banco de dados PostgreSQL no Railway
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

def setup_railway_database():
    """Configurar banco de dados PostgreSQL no Railway"""
    
    print("🔧 CONFIGURANDO BANCO DE DADOS POSTGRESQL NO RAILWAY")
    print("=" * 60)
    
    print("\n1. CONFIGURAÇÃO NO RAILWAY:")
    print("   a) Acesse: https://railway.app/dashboard")
    print("   b) Selecione seu projeto")
    print("   c) Clique em 'New' → 'Database' → 'PostgreSQL'")
    print("   d) Aguarde a criação do banco")
    print("   e) Copie a DATABASE_URL gerada")
    
    print("\n2. CONFIGURAR VARIÁVEL DE AMBIENTE:")
    print("   a) No Railway, vá em 'Variables'")
    print("   b) Adicione: DATABASE_URL = [URL_DO_POSTGRESQL]")
    print("   c) Exemplo: postgresql://user:pass@host:port/dbname")
    
    print("\n3. VERIFICAR CONFIGURAÇÃO:")
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        print(f"   ✅ DATABASE_URL configurada: {database_url[:50]}...")
        if 'postgresql' in database_url:
            print("   ✅ PostgreSQL detectado")
        else:
            print("   ⚠️  Ainda usando SQLite")
    else:
        print("   ❌ DATABASE_URL não configurada")
        print("   ⚠️  Usando SQLite (dados serão perdidos)")
    
    print("\n4. APLICAR MIGRAÇÕES:")
    print("   python manage.py migrate")
    
    print("\n5. CRIAR SUPERUSUÁRIO:")
    print("   python manage.py createsuperuser")
    
    print("\n✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("   - Dados serão persistidos entre deploys")
    print("   - Backup automático no Railway")
    print("   - Escalabilidade para produção")

if __name__ == '__main__':
    setup_railway_database()





