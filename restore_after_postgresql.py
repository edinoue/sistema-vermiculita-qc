#!/usr/bin/env python
"""
Script para restaurar dados após configurar PostgreSQL
"""

import os
import sys
import django
import json
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import *
from core.models import *
from django.contrib.auth.models import User

def restore_after_postgresql(backup_filename):
    """Restaurar dados após configurar PostgreSQL"""
    
    print(f"🔄 RESTAURANDO DADOS DE: {backup_filename}")
    print("=" * 60)
    
    try:
        # 1. Carregar backup
        print("\n1. CARREGANDO BACKUP:")
        with open(backup_filename, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        print(f"   ✅ Backup carregado: {backup_data['timestamp']}")
        
        # 2. Restaurar usuários
        print("\n2. RESTAURANDO USUÁRIOS:")
        users_restored = 0
        for user_data in backup_data['users']:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': user_data['is_staff'],
                    'is_superuser': user_data['is_superuser'],
                    'is_active': user_data['is_active']
                }
            )
            if created:
                user.set_password('temp_password_123')  # Senha temporária
                user.save()
                users_restored += 1
        print(f"   ✅ {users_restored} usuários restaurados")
        
        # 3. Restaurar produtos
        print("\n3. RESTAURANDO PRODUTOS:")
        products_restored = 0
        for product_data in backup_data['products']:
            product, created = Product.objects.get_or_create(
                code=product_data['code'],
                defaults={
                    'name': product_data['name'],
                    'description': product_data['description'],
                    'is_active': product_data['is_active'],
                    'display_order': product_data['display_order']
                }
            )
            if created:
                products_restored += 1
        print(f"   ✅ {products_restored} produtos restaurados")
        
        # 4. Restaurar propriedades
        print("\n4. RESTAURANDO PROPRIEDADES:")
        properties_restored = 0
        for prop_data in backup_data['properties']:
            property_obj, created = Property.objects.get_or_create(
                identifier=prop_data['identifier'],
                defaults={
                    'name': prop_data['name'],
                    'unit': prop_data['unit'],
                    'category': prop_data['category'],
                    'data_type': prop_data['data_type'],
                    'is_active': prop_data['is_active'],
                    'display_order': prop_data['display_order']
                }
            )
            if created:
                properties_restored += 1
        print(f"   ✅ {properties_restored} propriedades restauradas")
        
        # 5. Restaurar especificações
        print("\n5. RESTAURANDO ESPECIFICAÇÕES:")
        specifications_restored = 0
        for spec_data in backup_data['specifications']:
            try:
                product = Product.objects.get(code=spec_data['product_code'])
                property_obj = Property.objects.get(identifier=spec_data['property_identifier'])
                
                spec, created = Specification.objects.get_or_create(
                    product=product,
                    property=property_obj,
                    defaults={
                        'lsl': Decimal(str(spec_data['lsl'])) if spec_data['lsl'] else None,
                        'usl': Decimal(str(spec_data['usl'])) if spec_data['usl'] else None,
                        'target': Decimal(str(spec_data['target'])) if spec_data['target'] else None,
                        'is_active': spec_data['is_active']
                    }
                )
                if created:
                    specifications_restored += 1
            except (Product.DoesNotExist, Property.DoesNotExist):
                print(f"   ⚠️  Produto ou propriedade não encontrado para especificação")
        print(f"   ✅ {specifications_restored} especificações restauradas")
        
        # 6. Restaurar análises pontuais
        print("\n6. RESTAURANDO ANÁLISES PONTUAIS:")
        analyses_restored = 0
        for analysis_data in backup_data['spot_analyses']:
            try:
                product = Product.objects.get(code=analysis_data['product_code'])
                property_obj = Property.objects.get(identifier=analysis_data['property_identifier'])
                production_line = ProductionLine.objects.get(name=analysis_data['production_line_name'])
                shift = Shift.objects.get(name=analysis_data['shift_name'])
                operator = User.objects.get(username=analysis_data['operator_username']) if analysis_data['operator_username'] else None
                
                analysis, created = SpotAnalysis.objects.get_or_create(
                    product=product,
                    property=property_obj,
                    production_line=production_line,
                    shift=shift,
                    date=analysis_data['date'],
                    sequence=analysis_data.get('sequence', 1),
                    defaults={
                        'value': Decimal(str(analysis_data['value'])),
                        'unit': analysis_data['unit'],
                        'test_method': analysis_data['test_method'],
                        'status': analysis_data['status'],
                        'sample_time': analysis_data['sample_time'],
                        'operator': operator,
                        'observations': analysis_data.get('observations', '')
                    }
                )
                if created:
                    analyses_restored += 1
            except Exception as e:
                print(f"   ⚠️  Erro ao restaurar análise: {e}")
        print(f"   ✅ {analyses_restored} análises pontuais restauradas")
        
        # 7. Restaurar amostras compostas
        print("\n7. RESTAURANDO AMOSTRAS COMPOSTAS:")
        samples_restored = 0
        for sample_data in backup_data['composite_samples']:
            try:
                product = Product.objects.get(code=sample_data['product_code'])
                production_line = ProductionLine.objects.get(name=sample_data['production_line_name'])
                shift = Shift.objects.get(name=sample_data['shift_name'])
                operator = User.objects.get(username=sample_data['operator_username']) if sample_data['operator_username'] else None
                
                sample, created = CompositeSample.objects.get_or_create(
                    product=product,
                    production_line=production_line,
                    shift=shift,
                    date=sample_data['date'],
                    sequence=sample_data.get('sequence', 1),
                    defaults={
                        'collection_time': sample_data['collection_time'],
                        'quantity_produced': Decimal(str(sample_data['quantity_produced'])) if sample_data['quantity_produced'] else None,
                        'status': sample_data['status'],
                        'operator': operator,
                        'observations': sample_data.get('observations', '')
                    }
                )
                if created:
                    samples_restored += 1
            except Exception as e:
                print(f"   ⚠️  Erro ao restaurar amostra: {e}")
        print(f"   ✅ {samples_restored} amostras compostas restauradas")
        
        # 8. Restaurar resultados de amostras compostas
        print("\n8. RESTAURANDO RESULTADOS DE AMOSTRAS COMPOSTAS:")
        results_restored = 0
        for result_data in backup_data['composite_sample_results']:
            try:
                # Mapear ID antigo para novo ID
                composite_sample = CompositeSample.objects.filter(
                    product__code=result_data.get('product_code', ''),
                    date=result_data.get('date', '')
                ).first()
                
                if composite_sample:
                    property_obj = Property.objects.get(identifier=result_data['property_identifier'])
                    
                    result, created = CompositeSampleResult.objects.get_or_create(
                        composite_sample=composite_sample,
                        property=property_obj,
                        defaults={
                            'value': Decimal(str(result_data['value'])),
                            'unit': result_data['unit'],
                            'test_method': result_data['test_method'],
                            'status': result_data['status']
                        }
                    )
                    if created:
                        results_restored += 1
            except Exception as e:
                print(f"   ⚠️  Erro ao restaurar resultado: {e}")
        print(f"   ✅ {results_restored} resultados restaurados")
        
        print(f"\n✅ RESTAURAÇÃO CONCLUÍDA!")
        print(f"   - Usuários: {users_restored}")
        print(f"   - Produtos: {products_restored}")
        print(f"   - Propriedades: {properties_restored}")
        print(f"   - Especificações: {specifications_restored}")
        print(f"   - Análises pontuais: {analyses_restored}")
        print(f"   - Amostras compostas: {samples_restored}")
        print(f"   - Resultados: {results_restored}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO NA RESTAURAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        backup_filename = sys.argv[1]
        restore_after_postgresql(backup_filename)
    else:
        print("❌ Uso: python restore_after_postgresql.py <backup_filename>")
        print("   Exemplo: python restore_after_postgresql.py backup_antes_postgresql_20241225_143022.json")






