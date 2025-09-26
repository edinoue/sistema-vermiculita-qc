#!/usr/bin/env python
"""
Sistema de backup automático para preservar dados
"""

import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import *
from core.models import *
from django.contrib.auth.models import User

def backup_all_data():
    """Fazer backup de todos os dados importantes"""
    
    print("💾 FAZENDO BACKUP COMPLETO DOS DADOS")
    print("=" * 60)
    
    backup_data = {
        'timestamp': datetime.now().isoformat(),
        'users': [],
        'products': [],
        'properties': [],
        'specifications': [],
        'spot_analyses': [],
        'composite_samples': [],
        'composite_sample_results': [],
        'analysis_types': [],
        'analysis_type_properties': [],
        'production_lines': [],
        'shifts': [],
        'plants': []
    }
    
    try:
        # 1. Backup de usuários
        print("\n1. BACKUP DE USUÁRIOS:")
        users = User.objects.all()
        for user in users:
            backup_data['users'].append({
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat(),
                'is_active': user.is_active
            })
        print(f"   ✅ {len(users)} usuários salvos")
        
        # 2. Backup de produtos
        print("\n2. BACKUP DE PRODUTOS:")
        products = Product.objects.all()
        for product in products:
            backup_data['products'].append({
                'code': product.code,
                'name': product.name,
                'description': product.description,
                'is_active': product.is_active,
                'display_order': product.display_order
            })
        print(f"   ✅ {len(products)} produtos salvos")
        
        # 3. Backup de propriedades
        print("\n3. BACKUP DE PROPRIEDADES:")
        properties = Property.objects.all()
        for prop in properties:
            backup_data['properties'].append({
                'identifier': prop.identifier,
                'name': prop.name,
                'unit': prop.unit,
                'category': prop.category,
                'data_type': prop.data_type,
                'is_active': prop.is_active,
                'display_order': prop.display_order
            })
        print(f"   ✅ {len(properties)} propriedades salvas")
        
        # 4. Backup de especificações
        print("\n4. BACKUP DE ESPECIFICAÇÕES:")
        specifications = Specification.objects.all()
        for spec in specifications:
            backup_data['specifications'].append({
                'product_code': spec.product.code,
                'property_identifier': spec.property.identifier,
                'lsl': float(spec.lsl) if spec.lsl else None,
                'usl': float(spec.usl) if spec.usl else None,
                'target': float(spec.target) if spec.target else None,
                'is_active': spec.is_active
            })
        print(f"   ✅ {len(specifications)} especificações salvas")
        
        # 5. Backup de análises pontuais
        print("\n5. BACKUP DE ANÁLISES PONTUAIS:")
        spot_analyses = SpotAnalysis.objects.all()
        for analysis in spot_analyses:
            backup_data['spot_analyses'].append({
                'product_code': analysis.product.code,
                'production_line_name': analysis.production_line.name,
                'shift_name': analysis.shift.name,
                'property_identifier': analysis.property.identifier,
                'value': float(analysis.value),
                'unit': analysis.unit,
                'test_method': analysis.test_method,
                'status': analysis.status,
                'sample_time': analysis.sample_time.isoformat(),
                'operator_username': analysis.operator.username if analysis.operator else None,
                'observations': analysis.observations
            })
        print(f"   ✅ {len(spot_analyses)} análises pontuais salvas")
        
        # 6. Backup de amostras compostas
        print("\n6. BACKUP DE AMOSTRAS COMPOSTAS:")
        composite_samples = CompositeSample.objects.all()
        for sample in composite_samples:
            backup_data['composite_samples'].append({
                'product_code': sample.product.code,
                'production_line_name': sample.production_line.name,
                'shift_name': sample.shift.name,
                'date': sample.date.isoformat(),
                'collection_time': sample.collection_time.isoformat(),
                'quantity_produced': float(sample.quantity_produced) if sample.quantity_produced else None,
                'status': sample.status,
                'sequence': sample.sequence,
                'operator_username': sample.operator.username if sample.operator else None,
                'observations': sample.observations
            })
        print(f"   ✅ {len(composite_samples)} amostras compostas salvas")
        
        # 7. Backup de resultados de amostras compostas
        print("\n7. BACKUP DE RESULTADOS DE AMOSTRAS COMPOSTAS:")
        composite_results = CompositeSampleResult.objects.all()
        for result in composite_results:
            backup_data['composite_sample_results'].append({
                'composite_sample_id': result.composite_sample.id,
                'property_identifier': result.property.identifier,
                'value': float(result.value),
                'unit': result.unit,
                'test_method': result.test_method,
                'status': result.status
            })
        print(f"   ✅ {len(composite_results)} resultados salvos")
        
        # 8. Backup de tipos de análise
        print("\n8. BACKUP DE TIPOS DE ANÁLISE:")
        analysis_types = AnalysisType.objects.all()
        for atype in analysis_types:
            backup_data['analysis_types'].append({
                'code': atype.code,
                'name': atype.name,
                'description': atype.description,
                'is_active': atype.is_active
            })
        print(f"   ✅ {len(analysis_types)} tipos de análise salvos")
        
        # 9. Backup de linhas de produção
        print("\n9. BACKUP DE LINHAS DE PRODUÇÃO:")
        production_lines = ProductionLine.objects.all()
        for line in production_lines:
            backup_data['production_lines'].append({
                'name': line.name,
                'description': line.description,
                'is_active': line.is_active
            })
        print(f"   ✅ {len(production_lines)} linhas de produção salvas")
        
        # 10. Backup de turnos
        print("\n10. BACKUP DE TURNOS:")
        shifts = Shift.objects.all()
        for shift in shifts:
            backup_data['shifts'].append({
                'name': shift.name,
                'start_time': shift.start_time.strftime('%H:%M'),
                'end_time': shift.end_time.strftime('%H:%M'),
                'is_active': shift.is_active
            })
        print(f"   ✅ {len(shifts)} turnos salvos")
        
        # Salvar backup em arquivo
        backup_filename = f"backup_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ BACKUP SALVO EM: {backup_filename}")
        print(f"   Tamanho: {os.path.getsize(backup_filename)} bytes")
        
        return backup_filename
        
    except Exception as e:
        print(f"   ❌ ERRO NO BACKUP: {e}")
        return None

def restore_all_data(backup_filename):
    """Restaurar dados do backup"""
    
    print(f"🔄 RESTAURANDO DADOS DE: {backup_filename}")
    print("=" * 60)
    
    try:
        with open(backup_filename, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print(f"   ✅ Backup carregado: {backup_data['timestamp']}")
        
        # Restaurar dados (implementar conforme necessário)
        print("   ⚠️  Restauração manual necessária")
        print("   - Execute os scripts de setup após deploy")
        print("   - Use os dados do backup como referência")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO NA RESTAURAÇÃO: {e}")
        return False

if __name__ == '__main__':
    backup_filename = backup_all_data()
    if backup_filename:
        print(f"\n💾 BACKUP CONCLUÍDO: {backup_filename}")
        print("   - Salve este arquivo em local seguro")
        print("   - Use para restaurar dados após deploy")
    else:
        print("\n❌ BACKUP FALHOU")



