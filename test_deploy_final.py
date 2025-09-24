#!/usr/bin/env python
"""
Script para testar deploy final
"""

import os
import sys
import ast

def test_python_syntax(file_path):
    """Testar sintaxe de um arquivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tentar compilar o arquivo
        ast.parse(content)
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path} - Erro de sintaxe na linha {e.lineno}: {e.msg}")
        return False
        
    except Exception as e:
        print(f"⚠️  {file_path} - Erro: {e}")
        return False

def main():
    """Testar deploy final"""
    print("=== Testando Deploy Final ===")
    
    # Arquivos críticos para o deploy
    critical_files = [
        'quality_control/views_spot_improved.py',
        'quality_control/views_spot_fixed.py',
        'quality_control/views_composite.py',
        'quality_control/views_import.py',
        'quality_control/views_simple.py',
        'backup_data.py',
        'deploy_safe_with_backup.py',
        'setup_complete_initial_data.py',
    ]
    
    success_count = 0
    total_count = len(critical_files)
    
    print("Testando arquivos críticos...")
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            if test_python_syntax(file_path):
                print(f"✅ {file_path}")
                success_count += 1
            else:
                print(f"❌ {file_path}")
        else:
            print(f"⚠️  {file_path} - Arquivo não encontrado")
    
    print(f"\n=== Resultado: {success_count}/{total_count} arquivos OK ===")
    
    if success_count == total_count:
        print("✅ Deploy pronto! Todos os arquivos têm sintaxe correta!")
        print("\n🚀 Comandos para deploy:")
        print("1. git add .")
        print("2. git commit -m 'Fix syntax errors'")
        print("3. git push")
        return True
    else:
        print("❌ Deploy não pode prosseguir! Corrija os erros de sintaxe primeiro.")
        return False

if __name__ == '__main__':
    main()
