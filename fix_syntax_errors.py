#!/usr/bin/env python
"""
Script para corrigir erros de sintaxe automaticamente
"""

import os
import re

def fix_syntax_errors():
    """Corrigir erros de sintaxe nos arquivos"""
    print("=== Corrigindo Erros de Sintaxe ===")
    
    # Arquivos para corrigir
    files_to_fix = [
        'quality_control/views_spot_fixed.py',
        'quality_control/views_spot_improved.py',
        'quality_control/views_composite.py',
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"Corrigindo {file_path}...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Corrigir indentação incorreta
                lines = content.split('\n')
                fixed_lines = []
                
                for i, line in enumerate(lines):
                    # Corrigir linhas que começam com espaços incorretos
                    if line.startswith('    ') and not line.startswith('        '):
                        # Se a linha anterior não está indentada, esta deve estar
                        if i > 0 and not lines[i-1].strip().startswith('def ') and not lines[i-1].strip().startswith('class '):
                            # Manter indentação
                            fixed_lines.append(line)
                        else:
                            # Corrigir indentação
                            fixed_lines.append('        ' + line.lstrip())
                    else:
                        fixed_lines.append(line)
                
                # Salvar arquivo corrigido
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(fixed_lines))
                
                print(f"✅ {file_path} corrigido")
                
            except Exception as e:
                print(f"❌ Erro ao corrigir {file_path}: {e}")
        else:
            print(f"⚠️  {file_path} não encontrado")
    
    print("\n=== Correção concluída! ===")

if __name__ == '__main__':
    fix_syntax_errors()






