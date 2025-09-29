#!/usr/bin/env python
"""
Script para testar localmente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line

def test_local():
    """Testar localmente"""
    print("=== Testando sistema localmente ===")
    
    try:
        # Aplicar migrações
        print("Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("Migrações aplicadas com sucesso!")
        
        # Configurar dados iniciais
        print("Configurando dados iniciais...")
        from setup_initial_data import setup_initial_data
        setup_initial_data()
        
        # Verificar sistema
        print("Verificando sistema...")
        from verify_system import verify_system
        verify_system()
        
        print("\n=== Teste local concluído com sucesso! ===")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_local()





