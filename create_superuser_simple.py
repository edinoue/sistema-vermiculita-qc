#!/usr/bin/env python
"""
Script simples para criar super usuário usando Django management command
"""

import os
import sys
import subprocess

def create_superuser():
    """Cria super usuário usando o comando Django"""
    
    print("🚀 Sistema de Controle de Qualidade - Vermiculita")
    print("🔧 Criação de Super Usuário")
    print("=" * 50)
    
    try:
        # Executar o comando createsuperuser do Django
        result = subprocess.run([
            sys.executable, 'manage.py', 'createsuperuser'
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ Super usuário criado com sucesso!")
            print("🎉 Agora você pode fazer login no sistema!")
        else:
            print("❌ Erro ao criar super usuário.")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    create_superuser()
