#!/usr/bin/env python
"""
Script para corrigir erros de sintaxe automaticamente
"""

import os
import re

def fix_indentation_errors(file_path):
    """Corrigir erros de indentação"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Corrigir indentação incorreta
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Se a linha tem conteúdo mas não está indentada corretamente
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                # Verificar se deveria estar indentada
                if any(keyword in line for keyword in ['analysis_type =', 'properties =', 'for property in']):
                    # Adicionar indentação adequada
                    fixed_lines.append('            ' + line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # Salvar arquivo corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        
        print(f"✅ {file_path} - Indentação corrigida")
        return True
        
    except Exception as e:
        print(f"❌ {file_path} - Erro ao corrigir: {e}")
        return False

def fix_missing_imports(file_path):
    """Corrigir imports faltando"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se AnalysisType está sendo usado mas não importado
        if 'AnalysisType' in content and 'from .models import' in content:
            if 'AnalysisType' not in content.split('from .models import')[1].split('\n')[0]:
                # Adicionar AnalysisType ao import
                content = content.replace(
                    'from .models import Product, Property, CompositeSample, CompositeSampleResult',
                    'from .models import Product, Property, CompositeSample, CompositeSampleResult, AnalysisType'
                )
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ {file_path} - Import AnalysisType adicionado")
                return True
        
        return True
        
    except Exception as e:
        print(f"❌ {file_path} - Erro ao corrigir imports: {e}")
        return False

def main():
    """Corrigir erros de sintaxe"""
    print("=== Corrigindo Erros de Sintaxe ===")
    
    # Arquivos para corrigir
    files_to_fix = [
        'quality_control/views_spot_improved.py',
        'quality_control/views_spot_fixed.py',
        'quality_control/views_composite.py',
        'quality_control/views_import.py',
    ]
    
    success_count = 0
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"Corrigindo {file_path}...")
            
            # Corrigir indentação
            if fix_indentation_errors(file_path):
                success_count += 1
            
            # Corrigir imports
            fix_missing_imports(file_path)
        else:
            print(f"⚠️  {file_path} - Arquivo não encontrado")
    
    print(f"\n=== Correção concluída: {success_count} arquivos processados ===")
    
    if success_count > 0:
        print("✅ Erros de sintaxe corrigidos!")
        print("\n🚀 Agora você pode fazer o deploy:")
        print("1. git add .")
        print("2. git commit -m 'Fix syntax errors'")
        print("3. git push")
    else:
        print("❌ Nenhum arquivo foi corrigido.")

if __name__ == '__main__':
    main()




