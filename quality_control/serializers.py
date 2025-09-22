"""
Serializers para a API do quality_control
"""

from rest_framework import serializers
from .models import (
    Product, Property, ProductPropertyMap, Specification,
    SpotAnalysis, CompositeSample, CompositeSampleResult
)


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer para produtos
    """
    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'description', 'is_active']


class PropertySerializer(serializers.ModelSerializer):
    """
    Serializer para propriedades
    """
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    data_type_display = serializers.CharField(source='get_data_type_display', read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'identifier', 'name', 'unit', 'category', 'category_display',
            'test_method', 'data_type', 'data_type_display', 'description', 'is_active'
        ]


class ProductPropertyMapSerializer(serializers.ModelSerializer):
    """
    Serializer para mapeamento produto-propriedade
    """
    product = ProductSerializer(read_only=True)
    property = PropertySerializer(read_only=True)
    
    class Meta:
        model = ProductPropertyMap
        fields = [
            'id', 'product', 'property', 'show_in_spot_analysis',
            'show_in_composite_sample', 'show_in_dashboard', 'show_in_report', 'is_active'
        ]


class SpecificationSerializer(serializers.ModelSerializer):
    """
    Serializer para especificações
    """
    product = ProductSerializer(read_only=True)
    property = PropertySerializer(read_only=True)
    
    class Meta:
        model = Specification
        fields = ['id', 'product', 'property', 'lsl', 'target', 'usl', 'is_active']


class SpotAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer para análises pontuais
    """
    production_line_name = serializers.CharField(source='production_line.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    property_identifier = serializers.CharField(source='property.identifier', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    operator_name = serializers.CharField(source='operator.get_full_name', read_only=True)
    
    class Meta:
        model = SpotAnalysis
        fields = [
            'id', 'date', 'shift', 'shift_name', 'production_line', 'production_line_name',
            'product', 'product_name', 'property', 'property_name', 'property_identifier',
            'sequence', 'value', 'unit', 'test_method', 'status', 'status_display',
            'action_taken', 'sample_time', 'operator', 'operator_name'
        ]
        read_only_fields = ['status', 'operator']


class CompositeSampleResultSerializer(serializers.ModelSerializer):
    """
    Serializer para resultados de amostras compostas
    """
    property_name = serializers.CharField(source='property.name', read_only=True)
    property_identifier = serializers.CharField(source='property.identifier', read_only=True)
    
    class Meta:
        model = CompositeSampleResult
        fields = [
            'id', 'property', 'property_name', 'property_identifier',
            'value', 'unit', 'test_method'
        ]


class CompositeSampleSerializer(serializers.ModelSerializer):
    """
    Serializer para amostras compostas
    """
    production_line_name = serializers.CharField(source='production_line.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    operator_name = serializers.CharField(source='operator.get_full_name', read_only=True)
    results = CompositeSampleResultSerializer(source='compositesampleresult_set', many=True, read_only=True)
    
    class Meta:
        model = CompositeSample
        fields = [
            'id', 'uuid', 'date', 'shift', 'shift_name', 'production_line', 'production_line_name',
            'product', 'product_name', 'collection_time', 'quantity_produced',
            'status', 'status_display', 'observations', 'operator', 'operator_name', 'results'
        ]
        read_only_fields = ['uuid', 'operator']
