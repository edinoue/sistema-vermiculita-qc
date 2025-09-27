#!/usr/bin/env python
"""
Script para criar planilha padrão de importação
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime, time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import Product, Property, ProductionLine, Shift, AnalysisType

def create_import_template():
    """Criar planilha padrão para importação"""
    print("=== Criando planilha padrão de importação ===")
    
    # Criar diretório se não existir
    os.makedirs('import_templates', exist_ok=True)
    
    # Dados para análises pontuais
    spot_data = {
        'Data': ['2024-01-15', '2024-01-15', '2024-01-15'],
        'Hora_Amostra': ['08:30', '14:30', '20:30'],
        'Tipo_Analise': ['PONTUAL', 'PONTUAL', 'PONTUAL'],
        'Produto_Codigo': ['CONC_MEDIO', 'CONC_FINO', 'CONC_MEDIO'],
        'Linha_Producao': ['Linha 1', 'Linha 2', 'Linha 1'],
        'Turno': ['A', 'A', 'B'],
        'Sequencia': [1, 1, 1],
        'Umidade_%': [5.2, 4.8, 5.5],
        'Temperatura_C': [25.3, 24.8, 26.1],
        'Densidade_g_cm3': [0.85, 0.82, 0.87],
        'Metodo_Teste': ['Método padrão', 'Método padrão', 'Método padrão'],
        'Observacoes': ['Amostra normal', 'Amostra normal', 'Amostra normal']
    }
    
    # Dados para amostras compostas
    composite_data = {
        'Data_Coleta': ['2024-01-15', '2024-01-15'],
        'Hora_Inicio': ['07:00', '19:00'],
        'Hora_Fim': ['19:00', '07:00'],
        'Tipo_Analise': ['COMPOSTA', 'COMPOSTA'],
        'Produto_Codigo': ['CONC_MEDIO', 'CONC_FINO'],
        'Linha_Producao': ['Linha 1', 'Linha 2'],
        'Turno': ['A', 'B'],
        'Umidade_%': [5.1, 4.9],
        'Temperatura_C': [25.5, 25.2],
        'Densidade_g_cm3': [0.86, 0.84],
        'pH': [7.2, 7.0],
        'Granulometria_mm': [2.5, 2.3],
        'Metodo_Teste': ['Método padrão', 'Método padrão'],
        'Observacoes': ['Amostra composta 12h', 'Amostra composta 12h']
    }
    
    # Criar planilha com múltiplas abas
    with pd.ExcelWriter('import_templates/template_importacao_dados.xlsx', engine='openpyxl') as writer:
        
        # Aba de instruções
        instructions_data = {
            'INSTRUÇÕES': [
                'INSTRUÇÕES PARA IMPORTAÇÃO DE DADOS',
                '',
                '1. ANÁLISES PONTUAIS:',
                '- Use a aba "Analises_Pontuais" para dados de análises pontuais',
                '- Preencha todas as colunas obrigatórias',
                '- Data no formato YYYY-MM-DD',
                '- Hora no formato HH:MM',
                '- Código do produto deve existir no sistema',
                '- Linha de produção deve existir no sistema',
                '- Turno deve ser A ou B',
                '- Sequência deve ser 1, 2 ou 3',
                '',
                '2. AMOSTRAS COMPOSTAS:',
                '- Use a aba "Amostras_Compostas" para dados de amostras compostas',
                '- Preencha todas as colunas obrigatórias',
                '- Data no formato YYYY-MM-DD',
                '- Horas no formato HH:MM',
                '- Código do produto deve existir no sistema',
                '- Linha de produção deve existir no sistema',
                '- Turno deve ser A ou B',
                '',
                '3. COLUNAS OBRIGATÓRIAS:',
                '- Data/Hora da amostra',
                '- Tipo de análise (PONTUAL ou COMPOSTA)',
                '- Código do produto',
                '- Linha de produção',
                '- Turno',
                '- Pelo menos uma propriedade (Umidade, Temperatura, etc.)',
                '',
                '4. FORMATO DOS DADOS:',
                '- Números decimais use ponto (.) como separador',
                '- Datas no formato YYYY-MM-DD',
                '- Horas no formato HH:MM',
                '- Códigos devem ser exatos (case-sensitive)',
                '',
                '5. EXEMPLOS:',
                '- Veja os dados de exemplo nas abas',
                '- Não altere os cabeçalhos das colunas',
                '- Mantenha o formato das colunas',
                '',
                '6. VALIDAÇÃO:',
                '- O sistema validará os dados antes da importação',
                '- Erros serão reportados em uma planilha separada',
                '- Corrija os erros e reimporte se necessário'
            ]
        }
        
        instructions_df = pd.DataFrame(instructions_data)
        instructions_df.to_excel(writer, sheet_name='INSTRUÇÕES', index=False)
        
        # Aba de análises pontuais
        spot_df = pd.DataFrame(spot_data)
        spot_df.to_excel(writer, sheet_name='Analises_Pontuais', index=False)
        
        # Aba de amostras compostas
        composite_df = pd.DataFrame(composite_data)
        composite_df.to_excel(writer, sheet_name='Amostras_Compostas', index=False)
        
        # Aba de referência (produtos, linhas, turnos)
        reference_data = {
            'PRODUTOS_DISPONIVEIS': ['CONC_MEDIO', 'CONC_FINO', 'CONC_GROSSO', 'EXPANDIDA'],
            'LINHAS_DISPONIVEIS': ['Linha 1', 'Linha 2', 'Linha 3'],
            'TURNOS_DISPONIVEIS': ['A', 'B'],
            'TIPOS_ANALISE': ['PONTUAL', 'COMPOSTA'],
            'PROPRIEDADES_DISPONIVEIS': ['Umidade_%', 'Temperatura_C', 'Densidade_g_cm3', 'pH', 'Granulometria_mm']
        }
        
        reference_df = pd.DataFrame(reference_data)
        reference_df.to_excel(writer, sheet_name='REFERENCIA', index=False)
    
    print("✅ Planilha padrão criada: import_templates/template_importacao_dados.xlsx")
    
    # Criar dados de exemplo no sistema
    create_sample_data()
    
    print("✅ Dados de exemplo criados no sistema")
    print("\n=== Planilha de importação criada com sucesso! ===")

def create_sample_data():
    """Criar dados de exemplo no sistema"""
    
    # Criar produtos
    products_data = [
        {'code': 'CONC_MEDIO', 'name': 'Concentrado Médio', 'display_order': 1},
        {'code': 'CONC_FINO', 'name': 'Concentrado Fino', 'display_order': 2},
        {'code': 'CONC_GROSSO', 'name': 'Concentrado Grosso', 'display_order': 3},
        {'code': 'EXPANDIDA', 'name': 'Vermiculita Expandida', 'display_order': 4},
    ]
    
    for prod_data in products_data:
        Product.objects.get_or_create(
            code=prod_data['code'],
            defaults={
                'name': prod_data['name'],
                'display_order': prod_data['display_order'],
                'is_active': True
            }
        )
    
    # Criar propriedades
    properties_data = [
        {'identifier': 'UMIDADE', 'name': 'Umidade', 'unit': '%', 'display_order': 1},
        {'identifier': 'TEMPERATURA', 'name': 'Temperatura', 'unit': '°C', 'display_order': 2},
        {'identifier': 'DENSIDADE', 'name': 'Densidade', 'unit': 'g/cm³', 'display_order': 3},
        {'identifier': 'PH', 'name': 'pH', 'unit': '', 'display_order': 4},
        {'identifier': 'GRANULOMETRIA', 'name': 'Granulometria', 'unit': 'mm', 'display_order': 5},
    ]
    
    for prop_data in properties_data:
        Property.objects.get_or_create(
            identifier=prop_data['identifier'],
            defaults={
                'name': prop_data['name'],
                'unit': prop_data['unit'],
                'display_order': prop_data['display_order'],
                'category': 'FISICA',
                'data_type': 'DECIMAL',
                'is_active': True
            }
        )
    
    # Criar linhas de produção
    lines_data = [
        {'name': 'Linha 1', 'code': 'L1', 'display_order': 1},
        {'name': 'Linha 2', 'code': 'L2', 'display_order': 2},
        {'name': 'Linha 3', 'code': 'L3', 'display_order': 3},
    ]
    
    for line_data in lines_data:
        ProductionLine.objects.get_or_create(
            code=line_data['code'],
            defaults={
                'name': line_data['name'],
                'display_order': line_data['display_order'],
                'is_active': True
            }
        )
    
    # Criar turnos
    shifts_data = [
        {'name': 'A', 'start_time': time(7, 0), 'end_time': time(19, 0)},
        {'name': 'B', 'start_time': time(19, 0), 'end_time': time(7, 0)},
    ]
    
    for shift_data in shifts_data:
        Shift.objects.get_or_create(
            name=shift_data['name'],
            defaults={
                'start_time': shift_data['start_time'],
                'end_time': shift_data['end_time'],
                'description': f"Turno {shift_data['name']} ({shift_data['start_time'].strftime('%H:%M')}-{shift_data['end_time'].strftime('%H:%M')})"
            }
        )

if __name__ == '__main__':
    create_import_template()




