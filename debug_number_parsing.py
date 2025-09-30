#!/usr/bin/env python
"""
Script para debugar parsing de números e critérios de aprovação
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import SpotSample, SpotAnalysis, Property
from core.models import Product

def debug_number_parsing():
    """Debugar parsing de números e critérios"""
    print("🔍 === DEBUG NUMBER PARSING ===")
    
    # 1. Verificar propriedades e seus valores
    print("\n1️⃣ Propriedades e valores:")
    properties = Property.objects.all()
    for prop in properties:
        print(f"  {prop.name}: {prop.unit}")
        print(f"    Valor mínimo: {prop.min_value}")
        print(f"    Valor máximo: {prop.max_value}")
        print(f"    Tipo: {type(prop.min_value)} / {type(prop.max_value)}")
        print()
    
    # 2. Verificar análises e seus valores
    print("\n2️⃣ Análises e valores:")
    analyses = SpotAnalysis.objects.all()
    for analysis in analyses:
        print(f"  Amostra: {analysis.spot_sample.id}")
        print(f"  Produto: {analysis.spot_sample.product.name}")
        print(f"  Propriedade: {analysis.property.name}")
        print(f"  Valor: {analysis.value} (tipo: {type(analysis.value)})")
        print(f"  Status: {analysis.status}")
        print(f"  Min: {analysis.property.min_value}, Max: {analysis.property.max_value}")
        
        # Testar comparação
        try:
            if analysis.property.min_value is not None and analysis.property.max_value is not None:
                is_approved = analysis.property.min_value <= analysis.value <= analysis.property.max_value
                print(f"  Aprovado? {is_approved} (min <= valor <= max)")
            else:
                print(f"  Aprovado? Sem critérios definidos")
        except Exception as e:
            print(f"  Erro na comparação: {e}")
        print()
    
    # 3. Verificar amostras específicas
    print("\n3️⃣ Amostras específicas:")
    samples = SpotSample.objects.filter(product__name__icontains='Médio')
    for sample in samples:
        print(f"  Amostra: {sample.id} - {sample.product.name}")
        analyses = SpotAnalysis.objects.filter(spot_sample=sample)
        for analysis in analyses:
            print(f"    {analysis.property.name}: {analysis.value} {analysis.property.unit} ({analysis.status})")
            print(f"    Critérios: {analysis.property.min_value} - {analysis.property.max_value}")
            
            # Testar conversão de vírgula para ponto
            try:
                if isinstance(analysis.value, str) and ',' in str(analysis.value):
                    value_float = float(str(analysis.value).replace(',', '.'))
                    print(f"    Valor convertido: {value_float}")
                    
                    if analysis.property.min_value is not None and analysis.property.max_value is not None:
                        is_approved = analysis.property.min_value <= value_float <= analysis.property.max_value
                        print(f"    Aprovado após conversão? {is_approved}")
            except Exception as e:
                print(f"    Erro na conversão: {e}")
        print()
    
    # 4. Testar diferentes formatos de número
    print("\n4️⃣ Testando formatos de número:")
    test_values = ['94,00', '94.00', '94', '8,50', '8.50', '8']
    
    for test_value in test_values:
        print(f"  Valor original: '{test_value}'")
        try:
            # Tentar conversão com vírgula
            if ',' in test_value:
                converted = float(test_value.replace(',', '.'))
                print(f"    Convertido (vírgula->ponto): {converted}")
            
            # Tentar conversão direta
            try:
                direct = float(test_value)
                print(f"    Conversão direta: {direct}")
            except:
                print(f"    Conversão direta: ERRO")
        except Exception as e:
            print(f"    Erro: {e}")
        print()
    
    print("✅ Debug concluído!")

if __name__ == '__main__':
    debug_number_parsing()
