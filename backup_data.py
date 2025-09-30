#!/usr/bin/env python
"""
Script para backup e restauração de dados
"""

import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.core import serializers
from quality_control.models import Product, Property, AnalysisType, AnalysisTypeProperty, SpotAnalysis, CompositeSample, CompositeSampleResult
from core.models import Plant, ProductionLine, Shift

def backup_data():
    """Fazer backup de todos os dados importantes"""
    print("=== Fazendo Backup dos Dados ===")
    
    try:
        # Criar diretório de backup se não existir
        backup_dir = 'backup_data'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup de produtos
        products = Product.objects.all()
        with open(f'{backup_dir}/products_{timestamp}.json', 'w', encoding='utf-8') as f:
            f.write(serializers.serialize('json', products))
        print(f"✅ Produtos: {products.count()} registros")
        
        # Backup de propriedades
        properties = Property.objects.all()
        with open(f'{backup_dir}/properties_{timestamp}.json', 'w', encoding='utf-8') as f:
            f.write(serializers.serialize('json', properties))
        print(f"✅ Propriedades: {properties.count()} registros")
        
        # Backup de tipos de análise
        analysis_types = AnalysisType.objects.all()
        with open(f'{backup_dir}/analysis_types_{timestamp}.json', 'w', encoding='utf-8') as f:
            f.write(serializers.serialize('json', analysis_types))
        print(f"✅ Tipos de análise: {analysis_types.count()} registros")
        
        # Backup de configurações de propriedades
        atp = AnalysisTypeProperty.objects.all()
        with open(f'{backup_dir}/analysis_type_properties_{timestamp}.json', 'w', encoding='utf-8') as f:
            f.write(serializers.serialize('json', atp))
        print(f"✅ Configurações de propriedades: {atp.count()} registros")
        
        # Backup de plantas
        plants = Plant.objects.all()
        with open(f'{backup_dir}/plants_{timestamp}.json', 'w', encoding='utf-8') as f:
            f.write(serializers.serialize('json', plants))
        print(f"✅ Plantas: {plants.count()} registros")
        
        # Backup de linhas de produção
        lines = ProductionLine.objects.all()
        with open(f'{backup_dir}/production_lines_{timestamp}.json', 'w', encoding='utf-8') as f:
            f.write(serializers.serialize('json', lines))
        print(f"✅ Linhas de produção: {lines.count()} registros")
        
        # Backup de turnos
        shifts = Shift.objects.all()
        with open(f'{backup_dir}/shifts_{timestamp}.json', 'w', encoding='utf-8') as f:
            f.write(serializers.serialize('json', shifts))
        print(f"✅ Turnos: {shifts.count()} registros")
        
        # Backup de análises pontuais
        spot_analyses = SpotAnalysis.objects.all()
        with open(f'{backup_dir}/spot_analyses_{timestamp}.json', 'w', encoding='utf-8') as f:
            f.write(serializers.serialize('json', spot_analyses))
        print(f"✅ Análises pontuais: {spot_analyses.count()} registros")
        
        # Backup de amostras compostas
        composite_samples = CompositeSample.objects.all()
        with open(f'{backup_dir}/composite_samples_{timestamp}.json', 'w', encoding='utf-8') as f:
            f.write(serializers.serialize('json', composite_samples))
        print(f"✅ Amostras compostas: {composite_samples.count()} registros")
        
        # Criar arquivo de metadados
        metadata = {
            'timestamp': timestamp,
            'backup_date': datetime.now().isoformat(),
            'total_products': products.count(),
            'total_properties': properties.count(),
            'total_analysis_types': analysis_types.count(),
            'total_spot_analyses': spot_analyses.count(),
            'total_composite_samples': composite_samples.count(),
        }
        
        with open(f'{backup_dir}/metadata_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Backup concluído! Timestamp: {timestamp}")
        print(f"📁 Arquivos salvos em: {backup_dir}/")
        
        return timestamp
        
    except Exception as e:
        print(f"❌ Erro durante backup: {e}")
        import traceback
        traceback.print_exc()
        return None

def restore_data(timestamp=None):
    """Restaurar dados do backup"""
    print("=== Restaurando Dados ===")
    
    try:
        backup_dir = 'backup_data'
        
        if not timestamp:
            # Encontrar o backup mais recente
            backup_files = [f for f in os.listdir(backup_dir) if f.startswith('metadata_')]
            if not backup_files:
                print("❌ Nenhum backup encontrado")
                return False
            
            # Ordenar por timestamp
            backup_files.sort(reverse=True)
            timestamp = backup_files[0].replace('metadata_', '').replace('.json', '')
        
        print(f"📁 Restaurando backup: {timestamp}")
        
        # Restaurar produtos
        if os.path.exists(f'{backup_dir}/products_{timestamp}.json'):
            with open(f'{backup_dir}/products_{timestamp}.json', 'r', encoding='utf-8') as f:
                products_data = f.read()
            for obj in serializers.deserialize('json', products_data):
                obj.save()
            print("✅ Produtos restaurados")
        
        # Restaurar propriedades
        if os.path.exists(f'{backup_dir}/properties_{timestamp}.json'):
            with open(f'{backup_dir}/properties_{timestamp}.json', 'r', encoding='utf-8') as f:
                properties_data = f.read()
            for obj in serializers.deserialize('json', properties_data):
                obj.save()
            print("✅ Propriedades restauradas")
        
        # Restaurar tipos de análise
        if os.path.exists(f'{backup_dir}/analysis_types_{timestamp}.json'):
            with open(f'{backup_dir}/analysis_types_{timestamp}.json', 'r', encoding='utf-8') as f:
                analysis_types_data = f.read()
            for obj in serializers.deserialize('json', analysis_types_data):
                obj.save()
            print("✅ Tipos de análise restaurados")
        
        # Restaurar configurações de propriedades
        if os.path.exists(f'{backup_dir}/analysis_type_properties_{timestamp}.json'):
            with open(f'{backup_dir}/analysis_type_properties_{timestamp}.json', 'r', encoding='utf-8') as f:
                atp_data = f.read()
            for obj in serializers.deserialize('json', atp_data):
                obj.save()
            print("✅ Configurações de propriedades restauradas")
        
        # Restaurar plantas
        if os.path.exists(f'{backup_dir}/plants_{timestamp}.json'):
            with open(f'{backup_dir}/plants_{timestamp}.json', 'r', encoding='utf-8') as f:
                plants_data = f.read()
            for obj in serializers.deserialize('json', plants_data):
                obj.save()
            print("✅ Plantas restauradas")
        
        # Restaurar linhas de produção
        if os.path.exists(f'{backup_dir}/production_lines_{timestamp}.json'):
            with open(f'{backup_dir}/production_lines_{timestamp}.json', 'r', encoding='utf-8') as f:
                lines_data = f.read()
            for obj in serializers.deserialize('json', lines_data):
                obj.save()
            print("✅ Linhas de produção restauradas")
        
        # Restaurar turnos
        if os.path.exists(f'{backup_dir}/shifts_{timestamp}.json'):
            with open(f'{backup_dir}/shifts_{timestamp}.json', 'r', encoding='utf-8') as f:
                shifts_data = f.read()
            for obj in serializers.deserialize('json', shifts_data):
                obj.save()
            print("✅ Turnos restaurados")
        
        # Restaurar análises pontuais
        if os.path.exists(f'{backup_dir}/spot_analyses_{timestamp}.json'):
            with open(f'{backup_dir}/spot_analyses_{timestamp}.json', 'r', encoding='utf-8') as f:
                spot_analyses_data = f.read()
            for obj in serializers.deserialize('json', spot_analyses_data):
                obj.save()
            print("✅ Análises pontuais restauradas")
        
        # Restaurar amostras compostas
        if os.path.exists(f'{backup_dir}/composite_samples_{timestamp}.json'):
            with open(f'{backup_dir}/composite_samples_{timestamp}.json', 'r', encoding='utf-8') as f:
                composite_samples_data = f.read()
            for obj in serializers.deserialize('json', composite_samples_data):
                obj.save()
            print("✅ Amostras compostas restauradas")
        
        print(f"\n✅ Restauração concluída! Timestamp: {timestamp}")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante restauração: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_backups():
    """Listar backups disponíveis"""
    print("=== Backups Disponíveis ===")
    
    backup_dir = 'backup_data'
    if not os.path.exists(backup_dir):
        print("❌ Diretório de backup não encontrado")
        return
    
    backup_files = [f for f in os.listdir(backup_dir) if f.startswith('metadata_')]
    if not backup_files:
        print("❌ Nenhum backup encontrado")
        return
    
    backup_files.sort(reverse=True)
    
    for backup_file in backup_files:
        timestamp = backup_file.replace('metadata_', '').replace('.json', '')
        try:
            with open(f'{backup_dir}/{backup_file}', 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"📁 {timestamp}")
            print(f"   Data: {metadata.get('backup_date', 'N/A')}")
            print(f"   Produtos: {metadata.get('total_products', 0)}")
            print(f"   Propriedades: {metadata.get('total_properties', 0)}")
            print(f"   Análises pontuais: {metadata.get('total_spot_analyses', 0)}")
            print(f"   Amostras compostas: {metadata.get('total_composite_samples', 0)}")
            print()
        except Exception as e:
            print(f"⚠️  Erro ao ler {backup_file}: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'backup':
            backup_data()
        elif command == 'restore':
            timestamp = sys.argv[2] if len(sys.argv) > 2 else None
            restore_data(timestamp)
        elif command == 'list':
            list_backups()
        else:
            print("Comandos disponíveis: backup, restore [timestamp], list")
    else:
        print("Comandos disponíveis:")
        print("  python backup_data.py backup")
        print("  python backup_data.py restore [timestamp]")
        print("  python backup_data.py list")






