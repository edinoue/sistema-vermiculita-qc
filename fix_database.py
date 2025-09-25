#!/usr/bin/env python
"""
Script para corrigir o banco de dados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def fix_database():
    """Corrigir o banco de dados"""
    print("=== Corrigindo banco de dados ===")
    
    with connection.cursor() as cursor:
        # Verificar se a tabela AnalysisType existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='quality_control_analysistype'
        """)
        
        if not cursor.fetchone():
            print("Criando tabela AnalysisType...")
            cursor.execute("""
                CREATE TABLE quality_control_analysistype (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    created_by_id INTEGER,
                    updated_by_id INTEGER,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    code VARCHAR(20) NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    frequency_per_shift INTEGER NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    FOREIGN KEY (created_by_id) REFERENCES auth_user (id),
                    FOREIGN KEY (updated_by_id) REFERENCES auth_user (id)
                )
            """)
        
        # Verificar se a tabela AnalysisTypeProperty existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='quality_control_analysistypeproperty'
        """)
        
        if not cursor.fetchone():
            print("Criando tabela AnalysisTypeProperty...")
            cursor.execute("""
                CREATE TABLE quality_control_analysistypeproperty (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    created_by_id INTEGER,
                    updated_by_id INTEGER,
                    analysis_type_id INTEGER NOT NULL,
                    property_id INTEGER NOT NULL,
                    is_required BOOLEAN NOT NULL,
                    display_order INTEGER NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    FOREIGN KEY (analysis_type_id) REFERENCES quality_control_analysistype (id),
                    FOREIGN KEY (property_id) REFERENCES quality_control_property (id),
                    FOREIGN KEY (created_by_id) REFERENCES auth_user (id),
                    FOREIGN KEY (updated_by_id) REFERENCES auth_user (id),
                    UNIQUE (analysis_type_id, property_id)
                )
            """)
        
        # Verificar se a coluna analysis_type_id existe na tabela SpotAnalysis
        cursor.execute("PRAGMA table_info(quality_control_spotanalysis)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'analysis_type_id' not in columns:
            print("Adicionando coluna analysis_type_id...")
            cursor.execute("""
                ALTER TABLE quality_control_spotanalysis 
                ADD COLUMN analysis_type_id INTEGER
            """)
        
        # Inserir tipos de análise padrão
        cursor.execute("""
            INSERT OR IGNORE INTO quality_control_analysistype 
            (created_at, updated_at, name, code, description, frequency_per_shift, is_active)
            VALUES 
            (datetime('now'), datetime('now'), 'Análise Pontual', 'PONTUAL', 'Análises realizadas diretamente no fluxo de produção', 3, 1),
            (datetime('now'), datetime('now'), 'Análise Composta', 'COMPOSTA', 'Análises que representam 12 horas de produção', 1, 1)
        """)
        
        # Atualizar registros existentes para usar análise pontual como padrão
        cursor.execute("""
            UPDATE quality_control_spotanalysis 
            SET analysis_type_id = (
                SELECT id FROM quality_control_analysistype 
                WHERE code = 'PONTUAL'
            )
            WHERE analysis_type_id IS NULL
        """)
        
        print("Banco de dados corrigido com sucesso!")

def main():
    """Função principal"""
    try:
        fix_database()
        print("\n=== Correção concluída! ===")
        print("O sistema deve funcionar agora.")
        
    except Exception as e:
        print(f"Erro durante a correção: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

