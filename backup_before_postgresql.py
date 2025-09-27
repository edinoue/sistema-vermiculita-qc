#!/usr/bin/env python
"""
Script para fazer backup antes de configurar PostgreSQL
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

def backup_before_postgresql():
    """Fazer backup antes de configurar PostgreSQL"""
    
    print("💾 BACKUP ANTES DE CONFIGURAR POSTGRESQL")
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
        
        # Salvar backup em arquivo
        backup_filename = f"backup_antes_postgresql_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ BACKUP SALVO EM: {backup_filename}")
        print(f"   Tamanho: {os.path.getsize(backup_filename)} bytes")
        
        # Resumo dos dados
        total_items = (
            len(backup_data['users']) +
            len(backup_data['products']) +
            len(backup_data['properties']) +
            len(backup_data['specifications']) +
            len(backup_data['spot_analyses']) +
            len(backup_data['composite_samples']) +
            len(backup_data['composite_sample_results'])
        )
        
        print(f"\n📊 RESUMO DO BACKUP:")
        print(f"   - Total de itens: {total_items}")
        print(f"   - Usuários: {len(backup_data['users'])}")
        print(f"   - Produtos: {len(backup_data['products'])}")
        print(f"   - Propriedades: {len(backup_data['properties'])}")
        print(f"   - Especificações: {len(backup_data['specifications'])}")
        print(f"   - Análises pontuais: {len(backup_data['spot_analyses'])}")
        print(f"   - Amostras compostas: {len(backup_data['composite_samples'])}")
        print(f"   - Resultados: {len(backup_data['composite_sample_results'])}")
        
        print(f"\n💾 BACKUP CONCLUÍDO!")
        print(f"   - Arquivo: {backup_filename}")
        print(f"   - Salve em local seguro")
        print(f"   - Use para restaurar após configurar PostgreSQL")
        
        return backup_filename
        
    except Exception as e:
        print(f"   ❌ ERRO NO BACKUP: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    backup_filename = backup_before_postgresql()
    if backup_filename:
        print(f"\n🎉 BACKUP REALIZADO COM SUCESSO!")
        print(f"   Arquivo: {backup_filename}")
        print(f"   Agora você pode configurar PostgreSQL com segurança")
    else:
        print(f"\n❌ BACKUP FALHOU")
        print(f"   Verifique os erros acima antes de continuar")




