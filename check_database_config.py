#!/usr/bin/env python
"""
Script para verificar configuração do banco de dados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.conf import settings
from django.db import connection

def check_database_config():
    """Verificar configuração do banco de dados"""
    
    print("🔍 VERIFICANDO CONFIGURAÇÃO DO BANCO DE DADOS")
    print("=" * 60)
    
    # 1. Verificar variável de ambiente
    print("\n1. VARIÁVEL DE AMBIENTE DATABASE_URL:")
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        print(f"   ✅ DATABASE_URL configurada: {database_url[:50]}...")
        
        if 'postgresql' in database_url:
            print("   ✅ PostgreSQL detectado - DADOS PERSISTENTES")
            db_type = 'postgresql'
        elif 'mysql' in database_url:
            print("   ✅ MySQL detectado - DADOS PERSISTENTES")
            db_type = 'mysql'
        else:
            print("   ⚠️  Banco não identificado")
            db_type = 'unknown'
    else:
        print("   ❌ DATABASE_URL não configurada")
        print("   ⚠️  Usando SQLite - DADOS SERÃO PERDIDOS")
        db_type = 'sqlite'
    
    # 2. Verificar configuração do Django
    print("\n2. CONFIGURAÇÃO DO DJANGO:")
    db_config = settings.DATABASES['default']
    print(f"   Engine: {db_config['ENGINE']}")
    print(f"   Name: {db_config.get('NAME', 'N/A')}")
    print(f"   Host: {db_config.get('HOST', 'N/A')}")
    print(f"   Port: {db_config.get('PORT', 'N/A')}")
    print(f"   User: {db_config.get('USER', 'N/A')}")
    
    # 3. Verificar conexão com banco
    print("\n3. TESTE DE CONEXÃO:")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("   ✅ Conexão com banco funcionando")
            else:
                print("   ❌ Falha na conexão com banco")
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
    
    # 4. Verificar se é SQLite
    if 'sqlite' in db_config['ENGINE']:
        print("\n4. ⚠️  PROBLEMA IDENTIFICADO:")
        print("   - Sistema usando SQLite (temporário)")
        print("   - Dados serão perdidos a cada deploy")
        print("   - Necessário configurar PostgreSQL")
        
        print("\n5. SOLUÇÃO:")
        print("   a) Acesse Railway Dashboard")
        print("   b) Adicione PostgreSQL Database")
        print("   c) Configure DATABASE_URL")
        print("   d) Execute: python setup_railway_database.py")
        
    else:
        print("\n4. ✅ BANCO PERSISTENTE CONFIGURADO:")
        print("   - Dados serão preservados entre deploys")
        print("   - Sistema funcionando corretamente")
    
    return db_type

if __name__ == '__main__':
    check_database_config()

