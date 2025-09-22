"""
Views do app quality_control
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy
from datetime import datetime, time

from core.models import ProductionLine, Shift
from .models import (
    Product, Property, ProductPropertyMap, Specification,
    SpotAnalysis, CompositeSample, CompositeSampleResult
)


class SpotAnalysisView(LoginRequiredMixin, ListView):
    """
    Lista de análises pontuais
    """
    model = SpotAnalysis
    template_name = 'quality_control/spot_analysis_list.html'
    context_object_name = 'analyses'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SpotAnalysis.objects.select_related(
            'production_line', 'product', 'property', 'shift'
        ).order_by('-date', '-sample_time')
        
        # Filtros
        date = self.request.GET.get('date')
        line_id = self.request.GET.get('line')
        product_id = self.request.GET.get('product')
        
        if date:
            queryset = queryset.filter(date=date)
        if line_id:
            queryset = queryset.filter(production_line_id=line_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'production_lines': ProductionLine.objects.filter(is_active=True),
            'products': Product.objects.filter(is_active=True),
            'today': timezone.now().date(),
        })
        return context


class SpotAnalysisCreateView(LoginRequiredMixin, TemplateView):
    """
    Formulário mobile para criar análises pontuais
    """
    template_name = 'quality_control/spot_analysis_mobile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Determinar turno atual
        current_time = timezone.now().time()
        if time(6, 0) <= current_time < time(18, 0):
            current_shift = Shift.objects.get(name='A')
        else:
            current_shift = Shift.objects.get(name='B')
        
        context.update({
            'production_lines': ProductionLine.objects.filter(is_active=True),
            'products': Product.objects.filter(is_active=True),
            'current_shift': current_shift,
            'today': timezone.now().date(),
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            # Extrair dados do formulário
            data = {
                'date': request.POST.get('date'),
                'shift_id': request.POST.get('shift'),
                'production_line_id': request.POST.get('production_line'),
                'product_id': request.POST.get('product'),
                'property_id': request.POST.get('property'),
                'sequence': request.POST.get('sequence'),
                'value': request.POST.get('value'),
                'unit': request.POST.get('unit'),
                'action_taken': request.POST.get('action_taken', ''),
            }
            
            # Criar análise pontual
            analysis = SpotAnalysis.objects.create(
                date=data['date'],
                shift_id=data['shift_id'],
                production_line_id=data['production_line_id'],
                product_id=data['product_id'],
                property_id=data['property_id'],
                sequence=data['sequence'],
                value=data['value'],
                unit=data['unit'],
                action_taken=data['action_taken'],
                operator=request.user,
                created_by=request.user,
            )
            
            messages.success(request, f'Análise pontual #{analysis.sequence} registrada com sucesso!')
            return redirect('quality_control:spot_analysis_create')
            
        except Exception as e:
            messages.error(request, f'Erro ao registrar análise: {str(e)}')
            return self.get(request, *args, **kwargs)


class CompositeSampleView(LoginRequiredMixin, ListView):
    """
    Lista de amostras compostas
    """
    model = CompositeSample
    template_name = 'quality_control/composite_sample_list.html'
    context_object_name = 'samples'
    paginate_by = 20
    
    def get_queryset(self):
        return CompositeSample.objects.select_related(
            'production_line', 'product', 'shift'
        ).order_by('-date', '-collection_time')


class CompositeSampleCreateView(LoginRequiredMixin, TemplateView):
    """
    Formulário para criar amostras compostas
    """
    template_name = 'quality_control/composite_sample_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Determinar turno atual
        current_time = timezone.now().time()
        if time(6, 0) <= current_time < time(18, 0):
            current_shift = Shift.objects.get(name='A')
        else:
            current_shift = Shift.objects.get(name='B')
        
        context.update({
            'production_lines': ProductionLine.objects.filter(is_active=True),
            'products': Product.objects.filter(is_active=True),
            'current_shift': current_shift,
            'today': timezone.now().date(),
        })
        
        return context


class ShiftSummaryView(TemplateView):
    """
    Resumo do turno para uma linha específica
    """
    template_name = 'quality_control/shift_summary.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        date = kwargs.get('date')
        shift_name = kwargs.get('shift')
        line_id = kwargs.get('line_id')
        
        production_line = get_object_or_404(ProductionLine, id=line_id)
        shift = get_object_or_404(Shift, name=shift_name)
        
        # Buscar análises pontuais
        spot_analyses = SpotAnalysis.objects.filter(
            production_line=production_line,
            date=date,
            shift=shift
        ).order_by('property__identifier', 'sequence')
        
        # Buscar amostra composta
        try:
            composite_sample = CompositeSample.objects.get(
                production_line=production_line,
                date=date,
                shift=shift
            )
        except CompositeSample.DoesNotExist:
            composite_sample = None
        
        context.update({
            'production_line': production_line,
            'shift': shift,
            'date': date,
            'spot_analyses': spot_analyses,
            'composite_sample': composite_sample,
        })
        
        return context
