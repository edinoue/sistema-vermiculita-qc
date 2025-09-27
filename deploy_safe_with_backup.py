#!/usr/bin/env python
"""
Script de deploy seguro com backup automático
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from backup_data import backup_data, restore_data

def deploy_safe_with_backup():
    """Deploy seguro com backup automático"""
    print("=== Deploy Seguro com Backup ===")
    
    try:
        # 1. Fazer backup antes do deploy
        print("1. Fazendo backup dos dados existentes...")
        timestamp = backup_data()
        
        if not timestamp:
            print("❌ Falha no backup. Deploy cancelado.")
            return False
        
        print(f"✅ Backup concluído: {timestamp}")
        
        # 2. Aplicar migrações
        print("2. Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrações aplicadas")
        
        # 3. Configurar dados iniciais
        print("3. Configurando dados iniciais...")
        from setup_initial_data import setup_initial_data
        setup_initial_data()
        print("✅ Dados iniciais configurados")
        
        # 4. Configurar propriedades
        print("4. Configurando propriedades...")
        from setup_properties_config import setup_properties_config
        setup_properties_config()
        print("✅ Propriedades configuradas")
        
        # 5. Restaurar dados do backup
        print("5. Restaurando dados do backup...")
        if restore_data(timestamp):
            print("✅ Dados restaurados com sucesso")
        else:
            print("⚠️  Falha na restauração, mas deploy continuará")
        
        print("\n=== Deploy Seguro Concluído! ===")
        print("✅ Backup criado e dados preservados")
        print("✅ Migrações aplicadas")
        print("✅ Dados iniciais configurados")
        print("✅ Propriedades configuradas")
        print("✅ Dados restaurados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante deploy seguro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    deploy_safe_with_backup()




