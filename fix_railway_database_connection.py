#!/usr/bin/env python
"""
Script para corrigir conexão com PostgreSQL no Railway
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

def fix_railway_database_connection():
    """Corrigir conexão com PostgreSQL no Railway"""
    
    print("🔧 CORRIGINDO CONEXÃO COM POSTGRESQL NO RAILWAY")
    print("=" * 60)
    
    # 1. Verificar DATABASE_URL atual
    print("\n1. VERIFICANDO DATABASE_URL ATUAL:")
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        print(f"   ✅ DATABASE_URL configurada: {database_url[:50]}...")
        
        # Verificar se é PostgreSQL
        if 'postgresql' in database_url:
            print("   ✅ PostgreSQL detectado")
            
            # Verificar hostname
            if 'postgres.railway.internal' in database_url:
                print("   ⚠️  PROBLEMA: Hostname 'postgres.railway.internal' não resolve")
                print("   💡 SOLUÇÃO: Use o hostname público do Railway")
            else:
                print("   ✅ Hostname parece correto")
        else:
            print("   ❌ Não é PostgreSQL")
    else:
        print("   ❌ DATABASE_URL não configurada")
        print("   💡 SOLUÇÃO: Configure PostgreSQL no Railway")
    
    # 2. Instruções para corrigir
    print("\n2. COMO CORRIGIR:")
    print("   a) Acesse Railway Dashboard")
    print("   b) Vá no seu banco PostgreSQL")
    print("   c) Clique em 'Connect'")
    print("   d) Copie a DATABASE_URL pública (não interna)")
    print("   e) Vá em 'Variables' → 'DATABASE_URL'")
    print("   f) Cole a nova URL e salve")
    
    # 3. Verificar configuração do Django
    print("\n3. CONFIGURAÇÃO DO DJANGO:")
    from django.conf import settings
    db_config = settings.DATABASES['default']
    print(f"   Engine: {db_config['ENGINE']}")
    print(f"   Host: {db_config.get('HOST', 'N/A')}")
    print(f"   Port: {db_config.get('PORT', 'N/A')}")
    print(f"   Database: {db_config.get('NAME', 'N/A')}")
    
    # 4. Testar conexão
    print("\n4. TESTANDO CONEXÃO:")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("   ✅ Conexão funcionando!")
            else:
                print("   ❌ Conexão falhou")
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        print("   💡 SOLUÇÃO: Verifique a DATABASE_URL")
    
    print("\n✅ DIAGNÓSTICO CONCLUÍDO!")
    print("   - Se ainda houver erro, verifique a DATABASE_URL")
    print("   - Use o hostname público do Railway, não interno")
    print("   - Aguarde alguns minutos após configurar o banco")

if __name__ == '__main__':
    fix_railway_database_connection()




