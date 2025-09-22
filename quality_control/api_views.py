"""
API Views do app quality_control
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import time

from core.models import ProductionLine, Shift
from .models import Product, Property, SpotAnalysis, CompositeSample
from .serializers import (
    ProductSerializer, PropertySerializer, 
    SpotAnalysisSerializer, CompositeSampleSerializer
)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para produtos
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer


class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para propriedades
    """
    queryset = Property.objects.filter(is_active=True)
    serializer_class = PropertySerializer
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """
        Retorna propriedades disponíveis para um produto específico
        """
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'error': 'product_id é obrigatório'}, status=400)
        
        # Buscar propriedades mapeadas para o produto
        from .models import ProductPropertyMap
        mappings = ProductPropertyMap.objects.filter(
            product_id=product_id,
            is_active=True,
            show_in_spot_analysis=True
        ).select_related('property')
        
        properties = [mapping.property for mapping in mappings]
        serializer = self.get_serializer(properties, many=True)
        return Response(serializer.data)


class SpotAnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet para análises pontuais
    """
    queryset = SpotAnalysis.objects.all()
    serializer_class = SpotAnalysisSerializer
    
    def get_queryset(self):
        queryset = SpotAnalysis.objects.select_related(
            'production_line', 'product', 'property', 'shift'
        ).order_by('-date', '-sample_time')
        
        # Filtros
        date = self.request.query_params.get('date')
        line_id = self.request.query_params.get('line_id')
        product_id = self.request.query_params.get('product_id')
        shift_id = self.request.query_params.get('shift_id')
        
        if date:
            queryset = queryset.filter(date=date)
        if line_id:
            queryset = queryset.filter(production_line_id=line_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if shift_id:
            queryset = queryset.filter(shift_id=shift_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(
            operator=self.request.user,
            created_by=self.request.user
        )


class CompositeSampleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para amostras compostas
    """
    queryset = CompositeSample.objects.all()
    serializer_class = CompositeSampleSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            operator=self.request.user,
            created_by=self.request.user
        )


class CurrentShiftView(APIView):
    """
    API para obter informações do turno atual
    """
    def get(self, request):
        current_time = timezone.now().time()
        current_date = timezone.now().date()
        
        # Determinar turno atual
        if time(6, 0) <= current_time < time(18, 0):
            shift_name = 'A'
        else:
            shift_name = 'B'
        
        try:
            shift = Shift.objects.get(name=shift_name)
            return Response({
                'shift_id': shift.id,
                'shift_name': shift.name,
                'shift_display': shift.get_name_display(),
                'current_date': current_date,
                'current_time': timezone.now().isoformat(),
            })
        except Shift.DoesNotExist:
            return Response({'error': 'Turno não encontrado'}, status=404)


class ShiftDataView(APIView):
    """
    API para obter dados de um turno específico
    """
    def get(self, request, date, shift, line_id):
        production_line = get_object_or_404(ProductionLine, id=line_id)
        shift_obj = get_object_or_404(Shift, name=shift)
        
        # Buscar análises pontuais
        spot_analyses = SpotAnalysis.objects.filter(
            production_line=production_line,
            date=date,
            shift=shift_obj
        ).select_related('property', 'product').order_by('property__identifier', 'sequence')
        
        # Buscar amostra composta
        try:
            composite_sample = CompositeSample.objects.get(
                production_line=production_line,
                date=date,
                shift=shift_obj
            )
        except CompositeSample.DoesNotExist:
            composite_sample = None
        
        # Serializar dados
        spot_analyses_data = SpotAnalysisSerializer(spot_analyses, many=True).data
        composite_sample_data = CompositeSampleSerializer(composite_sample).data if composite_sample else None
        
        return Response({
            'production_line': {
                'id': production_line.id,
                'name': production_line.name,
                'code': production_line.code,
            },
            'shift': {
                'id': shift_obj.id,
                'name': shift_obj.name,
                'display': shift_obj.get_name_display(),
            },
            'date': date,
            'spot_analyses': spot_analyses_data,
            'composite_sample': composite_sample_data,
        })
