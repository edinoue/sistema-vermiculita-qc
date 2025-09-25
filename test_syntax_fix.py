#!/usr/bin/env python
"""
Script para testar sintaxe de arquivos Python
"""

import ast
import os
import sys

def test_python_syntax(file_path):
    """Testar sintaxe de um arquivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tentar compilar o arquivo
        ast.parse(content)
        print(f"✅ {file_path} - Sintaxe OK")
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path} - Erro de sintaxe:")
        print(f"   Linha {e.lineno}: {e.text}")
        print(f"   {e.msg}")
        return False
        
    except Exception as e:
        print(f"⚠️  {file_path} - Erro: {e}")
        return False

def main():
    """Testar sintaxe de todos os arquivos Python"""
    print("=== Testando Sintaxe de Arquivos Python ===")
    
    # Arquivos para testar
    files_to_test = [
        'quality_control/views_spot_improved.py',
        'quality_control/views_spot_fixed.py',
        'quality_control/views_composite.py',
        'quality_control/views_import.py',
        'quality_control/views_simple.py',
        'backup_data.py',
        'deploy_safe_with_backup.py',
        'setup_complete_initial_data.py',
        'test_backup_system.py',
    ]
    
    success_count = 0
    total_count = len(files_to_test)
    
    for file_path in files_to_test:
        if os.path.exists(file_path):
            if test_python_syntax(file_path):
                success_count += 1
        else:
            print(f"⚠️  {file_path} - Arquivo não encontrado")
    
    print(f"\n=== Resultado: {success_count}/{total_count} arquivos OK ===")
    
    if success_count == total_count:
        print("✅ Todos os arquivos têm sintaxe correta!")
        return True
    else:
        print("❌ Alguns arquivos têm problemas de sintaxe!")
        return False

if __name__ == '__main__':
    main()

