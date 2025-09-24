"""
Configuração do Django Admin para o app quality_control
"""

from django.contrib import admin
from .models import (
    AnalysisType, AnalysisTypeProperty, Product, Property, ProductPropertyMap, Specification,
    SpotAnalysis, CompositeSample, CompositeSampleResult,
    ChemicalAnalysis, ChemicalAnalysisResult,
    QualityReport, LoadingOrder
)


@admin.register(AnalysisType)
class AnalysisTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'frequency_per_shift', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['code']


class AnalysisTypePropertyInline(admin.TabularInline):
    model = AnalysisTypeProperty
    extra = 0
    fields = ['property', 'is_required', 'display_order', 'is_active']


@admin.register(AnalysisTypeProperty)
class AnalysisTypePropertyAdmin(admin.ModelAdmin):
    list_display = ['analysis_type', 'property', 'is_required', 'display_order', 'is_active']
    list_filter = ['analysis_type', 'property__category', 'is_required', 'is_active']
    search_fields = ['analysis_type__name', 'property__name']
    ordering = ['analysis_type', 'display_order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'name', 'category', 'unit', 'data_type', 'is_active']
    list_filter = ['category', 'data_type', 'is_active', 'created_at']
    search_fields = ['identifier', 'name']
    ordering = ['category', 'identifier']


@admin.register(ProductPropertyMap)
class ProductPropertyMapAdmin(admin.ModelAdmin):
    list_display = ['product', 'property', 'show_in_spot_analysis', 'show_in_composite_sample', 'show_in_dashboard', 'show_in_report', 'is_active']
    list_filter = ['product', 'property__category', 'is_active']
    search_fields = ['product__name', 'property__name']
    ordering = ['product', 'property']


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ['product', 'property', 'lsl', 'target', 'usl', 'is_active']
    list_filter = ['product', 'property__category', 'is_active']
    search_fields = ['product__name', 'property__name']
    ordering = ['product', 'property']


class CompositeSampleResultInline(admin.TabularInline):
    model = CompositeSampleResult
    extra = 0


@admin.register(CompositeSample)
class CompositeSampleAdmin(admin.ModelAdmin):
    list_display = ['date', 'shift', 'production_line', 'product', 'status', 'collection_time']
    list_filter = ['date', 'shift', 'production_line', 'product', 'status']
    search_fields = ['production_line__name', 'product__name']
    ordering = ['-date', '-collection_time']
    inlines = [CompositeSampleResultInline]


@admin.register(SpotAnalysis)
class SpotAnalysisAdmin(admin.ModelAdmin):
    list_display = ['analysis_type', 'date', 'shift', 'production_line', 'product', 'property', 'sequence', 'value', 'status']
    list_filter = ['analysis_type', 'date', 'shift', 'production_line', 'product', 'property', 'status']
    search_fields = ['production_line__name', 'product__name', 'property__name']
    ordering = ['-date', '-sample_time']


class ChemicalAnalysisResultInline(admin.TabularInline):
    model = ChemicalAnalysisResult
    extra = 0


@admin.register(ChemicalAnalysis)
class ChemicalAnalysisAdmin(admin.ModelAdmin):
    list_display = ['date', 'type', 'batch_number', 'laboratory', 'report_number']
    list_filter = ['type', 'date', 'laboratory']
    search_fields = ['batch_number', 'report_number', 'laboratory']
    ordering = ['-date']
    inlines = [ChemicalAnalysisResultInline]


@admin.register(QualityReport)
class QualityReportAdmin(admin.ModelAdmin):
    list_display = ['report_number', 'date', 'client_name', 'product', 'loading_type', 'status', 'total_quantity']
    list_filter = ['date', 'product', 'loading_type', 'status', 'plant']
    search_fields = ['report_number', 'client_name', 'invoice_number']
    ordering = ['-date', '-created_at']
    filter_horizontal = ['composite_samples']


@admin.register(LoadingOrder)
class LoadingOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'quality_report', 'status', 'loading_date', 'completion_date']
    list_filter = ['status', 'loading_date', 'completion_date']
    search_fields = ['order_number', 'quality_report__report_number', 'quality_report__client_name']
    ordering = ['-created_at']
