#!/usr/bin/env python
"""
Script para testar o sistema de backup
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from backup_data import backup_data, restore_data, list_backups

def test_backup_system():
    """Testar sistema de backup"""
    print("=== Testando Sistema de Backup ===")
    
    try:
        # 1. Fazer backup
        print("1. Fazendo backup...")
        timestamp = backup_data()
        
        if not timestamp:
            print("❌ Falha no backup")
            return False
        
        print(f"✅ Backup criado: {timestamp}")
        
        # 2. Listar backups
        print("2. Listando backups...")
        list_backups()
        
        # 3. Testar restauração
        print("3. Testando restauração...")
        if restore_data(timestamp):
            print("✅ Restauração funcionando")
        else:
            print("❌ Falha na restauração")
            return False
        
        print("\n✅ Sistema de backup funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_backup_system()






