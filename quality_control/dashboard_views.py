"""
Views para dashboards e análises estatísticas
"""

import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta

from core.models import ProductionLine, Shift
from .models import (
    Product, Property, SpotAnalysis, CompositeSample, 
    Specification, ProductPropertyMap
)
from .analytics import QualityAnalytics, DashboardMetrics


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard principal do sistema
    """
    template_name = 'quality_control/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        
        # Métricas básicas
        daily_summary = DashboardMetrics.get_daily_summary(today)
        weekly_trends = DashboardMetrics.get_weekly_trends(4)
        
        # Análises por linha de produção
        lines_data = []
        for line in ProductionLine.objects.filter(is_active=True):
            line_analyses = SpotAnalysis.objects.filter(
                production_line=line,
                date__gte=last_7_days
            )
            
            lines_data.append({
                'line': line,
                'total_analyses': line_analyses.count(),
                'approval_rate': (
                    line_analyses.filter(status='APPROVED').count() / 
                    line_analyses.count() * 100
                ) if line_analyses.count() > 0 else 0
            })
        
        # Top propriedades analisadas
        top_properties = (
            SpotAnalysis.objects.filter(date__gte=last_7_days)
            .values('property__identifier', 'property__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        context.update({
            'daily_summary': daily_summary,
            'weekly_trends': weekly_trends,
            'lines_data': lines_data,
            'top_properties': top_properties,
            'today': today,
        })
        
        return context


class ControlChartView(LoginRequiredMixin, TemplateView):
    """
    View para cartas de controle SPC
    """
    template_name = 'quality_control/control_chart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'production_lines': ProductionLine.objects.filter(is_active=True),
            'products': Product.objects.filter(is_active=True),
            'properties': Property.objects.filter(is_active=True),
        })
        
        return context


class CapabilityAnalysisView(LoginRequiredMixin, TemplateView):
    """
    View para análise de capabilidade
    """
    template_name = 'quality_control/capability_analysis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Produtos com especificações
        products_with_specs = Product.objects.filter(
            specification__isnull=False,
            is_active=True
        ).distinct()
        
        context.update({
            'products': products_with_specs,
            'production_lines': ProductionLine.objects.filter(is_active=True),
        })
        
        return context


class CorrelationAnalysisView(LoginRequiredMixin, TemplateView):
    """
    View para análise de correlação
    """
    template_name = 'quality_control/correlation_analysis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'products': Product.objects.filter(is_active=True),
            'chemical_properties': Property.objects.filter(
                category='QUIMICA', 
                is_active=True
            ),
            'physical_properties': Property.objects.filter(
                category='FISICA', 
                is_active=True
            ),
        })
        
        return context


# API Views para dados dos gráficos

class DashboardDataAPIView(LoginRequiredMixin, TemplateView):
    """
    API para dados do dashboard
    """
    
    def get(self, request, *args, **kwargs):
        data_type = request.GET.get('type', 'summary')
        
        if data_type == 'summary':
            return self._get_summary_data()
        elif data_type == 'trends':
            return self._get_trends_data()
        elif data_type == 'distribution':
            return self._get_distribution_data()
        
        return JsonResponse({'error': 'Tipo de dados inválido'}, status=400)
    
    def _get_summary_data(self):
        """Dados de resumo para o dashboard"""
        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)
        
        # Análises por status nos últimos 30 dias
        status_data = (
            SpotAnalysis.objects.filter(date__gte=last_30_days)
            .values('status')
            .annotate(count=Count('id'))
        )
        
        # Análises por linha de produção
        line_data = (
            SpotAnalysis.objects.filter(date__gte=last_30_days)
            .values('production_line__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Tendência diária (últimos 7 dias)
        daily_trend = []
        for i in range(7):
            date = today - timedelta(days=i)
            count = SpotAnalysis.objects.filter(date=date).count()
            daily_trend.append({
                'date': date.strftime('%d/%m'),
                'count': count
            })
        
        daily_trend.reverse()
        
        return JsonResponse({
            'status_distribution': list(status_data),
            'line_distribution': list(line_data),
            'daily_trend': daily_trend
        })
    
    def _get_trends_data(self):
        """Dados de tendências"""
        days = int(self.request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Tendência de aprovação por dia
        approval_trend = []
        current_date = start_date
        
        while current_date <= end_date:
            total = SpotAnalysis.objects.filter(date=current_date).count()
            approved = SpotAnalysis.objects.filter(
                date=current_date, 
                status='APPROVED'
            ).count()
            
            approval_rate = (approved / total * 100) if total > 0 else 0
            
            approval_trend.append({
                'date': current_date.strftime('%d/%m'),
                'approval_rate': round(approval_rate, 1),
                'total': total
            })
            
            current_date += timedelta(days=1)
        
        return JsonResponse({
            'approval_trend': approval_trend
        })
    
    def _get_distribution_data(self):
        """Dados de distribuição"""
        property_id = self.request.GET.get('property_id')
        days = int(self.request.GET.get('days', 30))
        
        if not property_id:
            return JsonResponse({'error': 'property_id é obrigatório'}, status=400)
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        analyses = SpotAnalysis.objects.filter(
            property_id=property_id,
            date__gte=start_date
        ).values_list('value', flat=True)
        
        if not analyses:
            return JsonResponse({'error': 'Nenhum dado encontrado'}, status=404)
        
        values = list(analyses)
        stats = QualityAnalytics.calculate_basic_statistics(
            SpotAnalysis.objects.filter(
                property_id=property_id,
                date__gte=start_date
            )
        )
        
        # Histograma (bins simples)
        import numpy as np
        hist, bin_edges = np.histogram(values, bins=10)
        
        histogram_data = []
        for i in range(len(hist)):
            histogram_data.append({
                'bin_start': round(bin_edges[i], 3),
                'bin_end': round(bin_edges[i+1], 3),
                'count': int(hist[i])
            })
        
        return JsonResponse({
            'statistics': stats,
            'histogram': histogram_data,
            'raw_values': values
        })


class ControlChartDataAPIView(LoginRequiredMixin, TemplateView):
    """
    API para dados das cartas de controle
    """
    
    def get(self, request, *args, **kwargs):
        property_id = request.GET.get('property_id')
        line_id = request.GET.get('line_id')
        days = int(request.GET.get('days', 30))
        chart_type = request.GET.get('chart_type', 'individual')
        
        if not property_id:
            return JsonResponse({'error': 'property_id é obrigatório'}, status=400)
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Filtrar análises
        queryset = SpotAnalysis.objects.filter(
            property_id=property_id,
            date__gte=start_date
        )
        
        if line_id:
            queryset = queryset.filter(production_line_id=line_id)
        
        # Gerar dados da carta de controle
        chart_data = QualityAnalytics.generate_control_chart_data(
            queryset, 
            chart_type=chart_type
        )
        
        if not chart_data:
            return JsonResponse({'error': 'Dados insuficientes para gerar carta'}, status=404)
        
        # Adicionar especificações se disponíveis
        try:
            property_obj = Property.objects.get(id=property_id)
            if line_id:
                line_obj = ProductionLine.objects.get(id=line_id)
                # Buscar especificação para o produto principal da linha
                # (simplificado - em produção, seria mais complexo)
                specs = Specification.objects.filter(
                    property=property_obj
                ).first()
            else:
                specs = Specification.objects.filter(
                    property=property_obj
                ).first()
            
            if specs:
                chart_data['specifications'] = {
                    'lsl': specs.lsl,
                    'target': specs.target,
                    'usl': specs.usl
                }
        except (Property.DoesNotExist, ProductionLine.DoesNotExist):
            pass
        
        return JsonResponse(chart_data)


class CapabilityDataAPIView(LoginRequiredMixin, TemplateView):
    """
    API para dados de análise de capabilidade
    """
    
    def get(self, request, *args, **kwargs):
        product_id = request.GET.get('product_id')
        property_id = request.GET.get('property_id')
        days = int(request.GET.get('days', 30))
        
        if not product_id or not property_id:
            return JsonResponse({
                'error': 'product_id e property_id são obrigatórios'
            }, status=400)
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Buscar especificação
        try:
            spec = Specification.objects.get(
                product_id=product_id,
                property_id=property_id
            )
        except Specification.DoesNotExist:
            return JsonResponse({
                'error': 'Especificação não encontrada'
            }, status=404)
        
        # Buscar dados
        analyses = SpotAnalysis.objects.filter(
            product_id=product_id,
            property_id=property_id,
            date__gte=start_date
        )
        
        if not analyses.exists():
            return JsonResponse({
                'error': 'Nenhum dado encontrado'
            }, status=404)
        
        values = list(analyses.values_list('value', flat=True))
        
        # Calcular índices de capabilidade
        capability_data = QualityAnalytics.calculate_capability_indices(
            values=values,
            lsl=spec.lsl,
            usl=spec.usl,
            target=spec.target
        )
        
        # Adicionar informações da especificação
        capability_data['specification'] = {
            'lsl': spec.lsl,
            'target': spec.target,
            'usl': spec.usl,
            'product': spec.product.name,
            'property': spec.property.name
        }
        
        return JsonResponse(capability_data)
