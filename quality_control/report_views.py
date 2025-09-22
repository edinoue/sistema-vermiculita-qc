"""
Views para laudos e ordens de carregamento
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta

from core.models import ProductionLine
from .models import Product, SpotAnalysis, CompositeSample
from .report_models import QualityReport, LoadingOrder, ReportTemplate
from .pdf_generator import generate_quality_report_pdf


class QualityReportListView(LoginRequiredMixin, ListView):
    """
    Lista de laudos de qualidade
    """
    model = QualityReport
    template_name = 'quality_control/reports/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = QualityReport.objects.select_related(
            'product', 'production_line', 'created_by', 'approved_by'
        ).order_by('-created_at')
        
        # Filtros
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        product_id = self.request.GET.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        line_id = self.request.GET.get('line')
        if line_id:
            queryset = queryset.filter(production_line_id=line_id)
        
        # Busca por número do laudo
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(report_number__icontains=search) |
                Q(batch_number__icontains=search) |
                Q(customer_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'products': Product.objects.filter(is_active=True),
            'production_lines': ProductionLine.objects.filter(is_active=True),
            'status_choices': QualityReport.STATUS_CHOICES,
            'current_filters': {
                'status': self.request.GET.get('status', ''),
                'product': self.request.GET.get('product', ''),
                'line': self.request.GET.get('line', ''),
                'search': self.request.GET.get('search', ''),
            }
        })
        return context


class QualityReportDetailView(LoginRequiredMixin, DetailView):
    """
    Detalhes do laudo de qualidade
    """
    model = QualityReport
    template_name = 'quality_control/reports/report_detail.html'
    context_object_name = 'report'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Análises relacionadas
        spot_analyses = self.object.spot_analyses.all().order_by('property__category', 'property__identifier')
        composite_samples = self.object.composite_samples.all().order_by('date')
        
        # Agrupar análises por propriedade
        analyses_by_property = {}
        for analysis in spot_analyses:
            prop_key = analysis.property.identifier
            if prop_key not in analyses_by_property:
                analyses_by_property[prop_key] = {
                    'property': analysis.property,
                    'analyses': []
                }
            analyses_by_property[prop_key]['analyses'].append(analysis)
        
        # Ordens de carregamento relacionadas
        loading_orders = LoadingOrder.objects.filter(quality_report=self.object)
        
        context.update({
            'spot_analyses': spot_analyses,
            'composite_samples': composite_samples,
            'analyses_by_property': analyses_by_property,
            'loading_orders': loading_orders,
        })
        
        return context


class QualityReportCreateView(LoginRequiredMixin, CreateView):
    """
    Criação de laudo de qualidade
    """
    model = QualityReport
    template_name = 'quality_control/reports/report_form.html'
    fields = [
        'report_type', 'product', 'production_line', 'start_date', 'end_date',
        'customer_name', 'customer_document', 'destination', 'batch_number',
        'quantity', 'observations'
    ]
    success_url = reverse_lazy('quality_control:report_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Buscar análises do período automaticamente
        self._auto_populate_analyses()
        
        messages.success(self.request, f'Laudo {self.object.report_number} criado com sucesso!')
        return response
    
    def _auto_populate_analyses(self):
        """Popula automaticamente as análises do período"""
        # Análises pontuais
        spot_analyses = SpotAnalysis.objects.filter(
            product=self.object.product,
            production_line=self.object.production_line,
            date__range=[self.object.start_date, self.object.end_date]
        )
        self.object.spot_analyses.set(spot_analyses)
        
        # Amostras compostas
        composite_samples = CompositeSample.objects.filter(
            product=self.object.product,
            production_line=self.object.production_line,
            date__range=[self.object.start_date, self.object.end_date]
        )
        self.object.composite_samples.set(composite_samples)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'products': Product.objects.filter(is_active=True),
            'production_lines': ProductionLine.objects.filter(is_active=True),
        })
        return context


class LoadingOrderListView(LoginRequiredMixin, ListView):
    """
    Lista de ordens de carregamento
    """
    model = LoadingOrder
    template_name = 'quality_control/reports/loading_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = LoadingOrder.objects.select_related(
            'quality_report__product', 'quality_report__production_line', 'created_by'
        ).order_by('-created_at')
        
        # Filtros
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'status_choices': LoadingOrder.STATUS_CHOICES,
            'current_status': self.request.GET.get('status', ''),
        })
        return context


class LoadingOrderDetailView(LoginRequiredMixin, DetailView):
    """
    Detalhes da ordem de carregamento
    """
    model = LoadingOrder
    template_name = 'quality_control/reports/loading_order_detail.html'
    context_object_name = 'order'


class LoadingOrderCreateView(LoginRequiredMixin, CreateView):
    """
    Criação de ordem de carregamento
    """
    model = LoadingOrder
    template_name = 'quality_control/reports/loading_order_form.html'
    fields = [
        'quality_report', 'vehicle_plate', 'driver_name', 'driver_document',
        'transport_type', 'scheduled_date', 'observations'
    ]
    success_url = reverse_lazy('quality_control:loading_order_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        messages.success(self.request, f'Ordem {self.object.order_number} criada com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Apenas laudos aprovados podem gerar ordens
        approved_reports = QualityReport.objects.filter(
            status='APPROVED'
        ).select_related('product', 'production_line')
        
        context['approved_reports'] = approved_reports
        return context


# Views de ação

@login_required
def approve_report(request, pk):
    """Aprovar laudo"""
    report = get_object_or_404(QualityReport, pk=pk)
    
    if not report.can_be_approved:
        messages.error(request, 'Este laudo não pode ser aprovado.')
        return redirect('quality_control:report_detail', pk=pk)
    
    report.approve(request.user)
    messages.success(request, f'Laudo {report.report_number} aprovado com sucesso!')
    
    return redirect('quality_control:report_detail', pk=pk)


@login_required
def reject_report(request, pk):
    """Rejeitar laudo"""
    report = get_object_or_404(QualityReport, pk=pk)
    
    if not report.can_be_approved:
        messages.error(request, 'Este laudo não pode ser rejeitado.')
        return redirect('quality_control:report_detail', pk=pk)
    
    report.reject(request.user)
    messages.warning(request, f'Laudo {report.report_number} rejeitado.')
    
    return redirect('quality_control:report_detail', pk=pk)


@login_required
def generate_report_pdf(request, pk):
    """Gerar PDF do laudo"""
    report = get_object_or_404(QualityReport, pk=pk)
    
    try:
        # Gerar PDF
        pdf_file = generate_quality_report_pdf(report)
        
        # Retornar arquivo para download
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="laudo_{report.report_number}.pdf"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erro ao gerar PDF: {str(e)}')
        return redirect('quality_control:report_detail', pk=pk)


@login_required
def start_loading(request, pk):
    """Iniciar carregamento"""
    order = get_object_or_404(LoadingOrder, pk=pk)
    
    if order.status != 'PENDING':
        messages.error(request, 'Esta ordem não pode ser iniciada.')
        return redirect('quality_control:loading_order_detail', pk=pk)
    
    order.start_loading()
    messages.success(request, f'Carregamento da ordem {order.order_number} iniciado!')
    
    return redirect('quality_control:loading_order_detail', pk=pk)


@login_required
def complete_loading(request, pk):
    """Completar carregamento"""
    order = get_object_or_404(LoadingOrder, pk=pk)
    
    if order.status != 'IN_PROGRESS':
        messages.error(request, 'Esta ordem não está em andamento.')
        return redirect('quality_control:loading_order_detail', pk=pk)
    
    order.complete_loading()
    messages.success(request, f'Carregamento da ordem {order.order_number} concluído!')
    
    return redirect('quality_control:loading_order_detail', pk=pk)


@login_required
def cancel_loading(request, pk):
    """Cancelar carregamento"""
    order = get_object_or_404(LoadingOrder, pk=pk)
    
    if order.status in ['COMPLETED', 'CANCELLED']:
        messages.error(request, 'Esta ordem não pode ser cancelada.')
        return redirect('quality_control:loading_order_detail', pk=pk)
    
    order.cancel_loading()
    messages.warning(request, f'Ordem {order.order_number} cancelada.')
    
    return redirect('quality_control:loading_order_detail', pk=pk)


# Views públicas (para QR codes)

def loading_order_public(request, pk):
    """
    View pública para visualizar ordem de carregamento via QR code
    """
    order = get_object_or_404(LoadingOrder, pk=pk)
    
    context = {
        'order': order,
        'is_public_view': True,
    }
    
    return render(request, 'quality_control/reports/loading_order_public.html', context)


def qr_code_redirect(request, order_number):
    """
    Redireciona QR code para a ordem correspondente
    """
    try:
        order = LoadingOrder.objects.get(order_number=order_number)
        return redirect('quality_control:loading_order_public', pk=order.pk)
    except LoadingOrder.DoesNotExist:
        raise Http404("Ordem de carregamento não encontrada")


# API Views

class ReportStatsAPIView(LoginRequiredMixin, DetailView):
    """
    API para estatísticas de laudos
    """
    
    def get(self, request, *args, **kwargs):
        # Estatísticas gerais
        total_reports = QualityReport.objects.count()
        approved_reports = QualityReport.objects.filter(status='APPROVED').count()
        pending_reports = QualityReport.objects.filter(status='PENDING').count()
        
        # Laudos por mês (últimos 6 meses)
        monthly_data = []
        for i in range(6):
            date = timezone.now().date().replace(day=1) - timedelta(days=30*i)
            count = QualityReport.objects.filter(
                created_at__year=date.year,
                created_at__month=date.month
            ).count()
            monthly_data.append({
                'month': date.strftime('%m/%Y'),
                'count': count
            })
        
        monthly_data.reverse()
        
        # Laudos por produto
        product_data = list(
            QualityReport.objects.values('product__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        return JsonResponse({
            'total_reports': total_reports,
            'approved_reports': approved_reports,
            'pending_reports': pending_reports,
            'approval_rate': (approved_reports / total_reports * 100) if total_reports > 0 else 0,
            'monthly_data': monthly_data,
            'product_data': product_data,
        })
