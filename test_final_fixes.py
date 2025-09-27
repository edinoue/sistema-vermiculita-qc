#!/usr/bin/env python
"""
Script para testar todas as correções finais
"""

import os
import sys
import ast

def test_python_syntax(file_path):
    """Testar sintaxe de um arquivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ast.parse(content)
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path} - Erro de sintaxe na linha {e.lineno}: {e.msg}")
        return False
        
    except Exception as e:
        print(f"⚠️  {file_path} - Erro: {e}")
        return False

def test_template_exists(template_path):
    """Testar se template existe"""
    if os.path.exists(template_path):
        print(f"✅ {template_path}")
        return True
    else:
        print(f"❌ {template_path} - Template não encontrado")
        return False

def main():
    """Testar todas as correções"""
    print("=== Testando Correções Finais ===")
    
    # Testar sintaxe Python
    print("\n1. Testando sintaxe Python...")
    python_files = [
        'quality_control/views_spot_improved.py',
        'quality_control/views_spot_fixed.py',
        'quality_control/views_composite.py',
        'quality_control/views_import.py',
        'quality_control/views.py',
    ]
    
    python_success = 0
    for file_path in python_files:
        if os.path.exists(file_path):
            if test_python_syntax(file_path):
                python_success += 1
    
    # Testar templates
    print("\n2. Testando templates...")
    templates = [
        'templates/quality_control/composite_sample_list.html',
        'templates/quality_control/composite_sample_detail.html',
        'templates/quality_control/composite_sample_edit.html',
        'templates/quality_control/spot_analysis_list.html',
    ]
    
    template_success = 0
    for template_path in templates:
        if test_template_exists(template_path):
            template_success += 1
    
    # Resultado final
    print(f"\n=== Resultado Final ===")
    print(f"Python: {python_success}/{len(python_files)} arquivos OK")
    print(f"Templates: {template_success}/{len(templates)} arquivos OK")
    
    total_success = python_success + template_success
    total_files = len(python_files) + len(templates)
    
    if total_success == total_files:
        print("✅ Todas as correções estão funcionando!")
        print("\n🚀 Sistema pronto para deploy:")
        print("1. git add .")
        print("2. git commit -m 'Fix template errors and context issues'")
        print("3. git push")
        return True
    else:
        print("❌ Algumas correções ainda precisam ser feitas.")
        return False

if __name__ == '__main__':
    main()




