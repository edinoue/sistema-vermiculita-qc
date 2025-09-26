#!/usr/bin/env python
"""
Script de teste para verificar o agrupamento de análises pontuais por amostra
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, datetime
from quality_control.models import (
    SpotSample, SpotAnalysis, Product, Property, 
    AnalysisType, Specification
)
from core.models import ProductionLine, Shift

def test_spot_sample_grouping():
    """Testar o agrupamento de análises pontuais"""
    print("🧪 Testando agrupamento de análises pontuais por amostra...")
    
    try:
        # Verificar se existem dados básicos
        products = Product.objects.filter(is_active=True)
        if not products.exists():
            print("❌ Nenhum produto ativo encontrado")
            return False
        
        properties = Property.objects.filter(is_active=True)
        if not properties.exists():
            print("❌ Nenhuma propriedade ativa encontrada")
            return False
        
        analysis_types = AnalysisType.objects.filter(is_active=True)
        if not analysis_types.exists():
            print("❌ Nenhum tipo de análise ativo encontrado")
            return False
        
        lines = ProductionLine.objects.filter(is_active=True)
        if not lines.exists():
            print("❌ Nenhuma linha de produção ativa encontrada")
            return False
        
        shifts = Shift.objects.all()
        if not shifts.exists():
            print("❌ Nenhum turno encontrado")
            return False
        
        print("✅ Dados básicos encontrados")
        
        # Criar uma amostra pontual de teste
        product = products.first()
        line = lines.first()
        shift = shifts.first()
        analysis_type = analysis_types.filter(code='PONTUAL').first()
        
        if not analysis_type:
            print("❌ Tipo de análise 'PONTUAL' não encontrado")
            return False
        
        # Criar amostra pontual
        spot_sample = SpotSample.objects.create(
            analysis_type=analysis_type,
            date=date.today(),
            shift=shift,
            production_line=line,
            product=product,
            sequence=1,
            sample_time=timezone.now(),
            observations="Amostra de teste para agrupamento"
        )
        
        print(f"✅ Amostra pontual criada: {spot_sample}")
        
        # Criar análises para diferentes propriedades
        created_analyses = 0
        for i, property in enumerate(properties[:3]):  # Testar com as primeiras 3 propriedades
            analysis = SpotAnalysis.objects.create(
                spot_sample=spot_sample,
                property=property,
                value=Decimal(f"{10.5 + i}"),  # Valores de teste
                unit=property.unit,
                test_method=f"Método de teste {i+1}"
            )
            created_analyses += 1
            print(f"✅ Análise criada: {analysis}")
        
        # Verificar se a amostra foi criada corretamente
        sample_analyses = spot_sample.spotanalysis_set.all()
        print(f"✅ Amostra possui {sample_analyses.count()} análises")
        
        # Verificar status da amostra
        spot_sample.update_status()
        print(f"✅ Status da amostra: {spot_sample.status}")
        
        # Testar busca por identificação única
        unique_sample = SpotSample.objects.filter(
            date=spot_sample.date,
            shift=spot_sample.shift,
            production_line=spot_sample.production_line,
            product=spot_sample.product,
            sequence=spot_sample.sequence
        ).first()
        
        if unique_sample and unique_sample.id == spot_sample.id:
            print("✅ Identificação única da amostra funcionando")
        else:
            print("❌ Problema na identificação única da amostra")
            return False
        
        # Limpar dados de teste
        spot_sample.delete()
        print("✅ Dados de teste removidos")
        
        print("\n🎉 Teste de agrupamento concluído com sucesso!")
        print("\n📋 Resumo da implementação:")
        print("   • Modelo SpotSample criado para agrupar análises")
        print("   • Modelo SpotAnalysis modificado para referenciar SpotSample")
        print("   • Views criadas para gerenciar amostras agrupadas")
        print("   • Templates criados para interface do usuário")
        print("   • URLs configuradas para as novas funcionalidades")
        print("   • Menu de navegação atualizado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_spot_sample_grouping()
    sys.exit(0 if success else 1)
