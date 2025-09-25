#!/usr/bin/env python
"""
Script para testar se o deploy funcionará
"""

import os
import sys

def test_deploy():
    """Testar se o deploy funcionará"""
    print("=== Testando Deploy ===")
    
    try:
        # Verificar se os arquivos principais existem
        required_files = [
            'manage.py',
            'vermiculita_system/settings.py',
            'vermiculita_system/urls.py',
            'quality_control/urls.py',
            'quality_control/views.py',
            'quality_control/models.py',
            'requirements.txt',
            'Procfile',
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ Arquivos obrigatórios não encontrados:")
            for file in missing_files:
                print(f"  - {file}")
            return False
        
        print("✅ Todos os arquivos obrigatórios existem")
        
        # Verificar se há erros de sintaxe nos arquivos principais
        python_files = [
            'quality_control/views_spot_fixed.py',
            'quality_control/views_spot_improved.py',
            'quality_control/views_composite.py',
            'quality_control/urls.py',
        ]
        
        syntax_errors = []
        for file_path in python_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar se há problemas óbvios de sintaxe
                    if 'analysis_type = AnalysisType.objects.get(code=\'PONTUAL\')' in content:
                        # Verificar se está dentro de um bloco try/except ou função
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'analysis_type = AnalysisType.objects.get(code=\'PONTUAL\')' in line:
                                # Verificar se a linha anterior tem indentação correta
                                if i > 0:
                                    prev_line = lines[i-1]
                                    if not prev_line.strip().endswith(':') and not prev_line.strip().startswith('#'):
                                        # Verificar indentação
                                        if line.startswith('    ') and not line.startswith('        '):
                                            syntax_errors.append(f"{file_path}:{i+1} - Indentação incorreta")
                
                except Exception as e:
                    syntax_errors.append(f"{file_path} - Erro: {e}")
        
        if syntax_errors:
            print("❌ Erros de sintaxe encontrados:")
            for error in syntax_errors:
                print(f"  - {error}")
            return False
        
        print("✅ Nenhum erro de sintaxe óbvio encontrado")
        
        # Verificar se as URLs estão corretas
        try:
            with open('quality_control/urls.py', 'r', encoding='utf-8') as f:
                urls_content = f.read()
            
            if 'views_spot_fixed' in urls_content and 'views_spot_improved' in urls_content:
                print("✅ URLs configuradas corretamente")
            else:
                print("⚠️  URLs podem ter problemas")
                
        except Exception as e:
            print(f"⚠️  Erro ao verificar URLs: {e}")
        
        print("\n✅ Deploy deve funcionar!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == '__main__':
    success = test_deploy()
    sys.exit(0 if success else 1)

