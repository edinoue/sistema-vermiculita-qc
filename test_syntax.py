#!/usr/bin/env python
"""
Script para testar sintaxe dos arquivos Python
"""

import os
import sys
import ast

def test_syntax():
    """Testar sintaxe de todos os arquivos Python"""
    print("=== Testando Sintaxe dos Arquivos Python ===")
    
    # Arquivos para testar
    files_to_test = [
        'quality_control/views_spot_fixed.py',
        'quality_control/views_spot_improved.py',
        'quality_control/views_composite.py',
        'quality_control/views_import.py',
        'quality_control/views_simple.py',
        'quality_control/views.py',
        'quality_control/models.py',
        'quality_control/admin.py',
        'quality_control/urls.py',
        'core/models.py',
        'core/views.py',
        'core/urls.py',
        'vermiculita_system/settings.py',
        'vermiculita_system/urls.py',
    ]
    
    errors = []
    
    for file_path in files_to_test:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Tentar compilar o arquivo
                ast.parse(content, filename=file_path)
                print(f"✅ {file_path} - Sintaxe OK")
                
            except SyntaxError as e:
                error_msg = f"❌ {file_path} - Erro de sintaxe: {e}"
                print(error_msg)
                errors.append(error_msg)
                
            except Exception as e:
                error_msg = f"⚠️  {file_path} - Erro: {e}"
                print(error_msg)
                errors.append(error_msg)
        else:
            print(f"⚠️  {file_path} - Arquivo não encontrado")
    
    if errors:
        print(f"\n❌ {len(errors)} erros encontrados:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n✅ Todos os arquivos têm sintaxe correta!")
        return True

if __name__ == '__main__':
    success = test_syntax()
    sys.exit(0 if success else 1)





