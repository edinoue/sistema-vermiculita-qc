#!/usr/bin/env python
"""
Script de deploy seguro com persistência de dados
"""

import os
import sys
import django
import subprocess
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

def check_database_config():
    """Verificar configuração do banco de dados"""
    
    print("🔍 VERIFICANDO CONFIGURAÇÃO DO BANCO")
    print("=" * 50)
    
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        print(f"✅ DATABASE_URL configurada: {database_url[:50]}...")
        
        if 'postgresql' in database_url:
            print("✅ PostgreSQL detectado - DADOS PERSISTENTES")
            return 'postgresql'
        elif 'mysql' in database_url:
            print("✅ MySQL detectado - DADOS PERSISTENTES")
            return 'mysql'
        else:
            print("⚠️  Banco não identificado")
            return 'unknown'
    else:
        print("❌ DATABASE_URL não configurada")
        print("⚠️  Usando SQLite - DADOS SERÃO PERDIDOS")
        return 'sqlite'

def backup_before_deploy():
    """Fazer backup antes do deploy"""
    
    print("\n💾 FAZENDO BACKUP ANTES DO DEPLOY")
    print("=" * 50)
    
    try:
        # Executar script de backup
        result = subprocess.run([sys.executable, 'backup_system.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backup concluído com sucesso")
            return True
        else:
            print(f"❌ Erro no backup: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar backup: {e}")
        return False

def run_migrations():
    """Executar migrações"""
    
    print("\n🔄 EXECUTANDO MIGRAÇÕES")
    print("=" * 50)
    
    try:
        result = subprocess.run(['python', 'manage.py', 'migrate'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migrações executadas com sucesso")
            return True
        else:
            print(f"❌ Erro nas migrações: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {e}")
        return False

def setup_initial_data():
    """Configurar dados iniciais"""
    
    print("\n🔧 CONFIGURANDO DADOS INICIAIS")
    print("=" * 50)
    
    try:
        # Executar script de dados iniciais
        result = subprocess.run([sys.executable, 'setup_complete_initial_data.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dados iniciais configurados")
            return True
        else:
            print(f"❌ Erro na configuração: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao configurar dados: {e}")
        return False

def deploy_safe():
    """Deploy seguro com persistência"""
    
    print("🚀 DEPLOY SEGURO COM PERSISTÊNCIA")
    print("=" * 60)
    
    # 1. Verificar banco de dados
    db_type = check_database_config()
    
    if db_type == 'sqlite':
        print("\n⚠️  ATENÇÃO: Usando SQLite - DADOS SERÃO PERDIDOS!")
        print("   Recomendação: Configure PostgreSQL no Railway")
        print("   Execute: python setup_railway_database.py")
        
        response = input("\nContinuar mesmo assim? (s/N): ")
        if response.lower() != 's':
            print("❌ Deploy cancelado")
            return False
    
    # 2. Fazer backup (se não for SQLite)
    if db_type != 'sqlite':
        if not backup_before_deploy():
            print("❌ Deploy cancelado - backup falhou")
            return False
    
    # 3. Executar migrações
    if not run_migrations():
        print("❌ Deploy cancelado - migrações falharam")
        return False
    
    # 4. Configurar dados iniciais
    if not setup_initial_data():
        print("❌ Deploy cancelado - configuração falhou")
        return False
    
    print("\n✅ DEPLOY CONCLUÍDO COM SUCESSO!")
    
    if db_type == 'sqlite':
        print("⚠️  Lembre-se: Configure PostgreSQL para persistência")
    else:
        print("✅ Dados serão preservados entre deploys")
    
    return True

if __name__ == '__main__':
    deploy_safe()




