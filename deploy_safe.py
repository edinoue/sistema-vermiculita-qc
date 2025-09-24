#!/usr/bin/env python
"""
Script para deploy seguro
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection

def safe_migrate():
    """Aplicar migrações de forma segura"""
    print("=== Aplicando migrações ===")
    
    try:
        # Aplicar migrações
        execute_from_command_line(['manage.py', 'migrate'])
        print("Migrações aplicadas com sucesso!")
        
        # Configurar dados iniciais
        from setup_initial_data import setup_initial_data
        setup_initial_data()
        
        print("\n=== Deploy concluído com sucesso! ===")
        
    except Exception as e:
        print(f"Erro durante o deploy: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    safe_migrate()
