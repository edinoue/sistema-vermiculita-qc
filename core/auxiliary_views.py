"""
Views para funcionalidades auxiliares
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime, timedelta
import json

from .models import ProductionLine, Shift
from .utils import QRCodeGenerator, DataExporter, DataImporter, AuditLogger
from quality_control.models import SpotAnalysis, QualityReport, CompositeSample


class QRCodeView(LoginRequiredMixin, TemplateView):
    """
    Visualização de QR Code para linha de produção
    """
    template_name = 'core/qr_code.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        line_code = kwargs.get('line_code')
        line = get_object_or_404(ProductionLine, code=line_code)
        
        # Gerar QR Code
        qr_image_base64 = QRCodeGenerator.generate_line_qr_code(line, format='BASE64')
        
        # Dados do turno atual
        current_shift = Shift.get_current_shift()
        today = timezone.now().date()
        
        # Análises de hoje
        today_analyses = SpotAnalysis.objects.filter(
            production_line=line,
            date=today
        )
        
        if current_shift:
            shift_analyses = today_analyses.filter(shift=current_shift)
        else:
            shift_analyses = SpotAnalysis.objects.none()
        
        context.update({
            'line': line,
            'qr_image': qr_image_base64,
            'current_shift': current_shift,
            'today': today,
            'today_analyses_count': today_analyses.count(),
            'shift_analyses_count': shift_analyses.count(),
            'last_analyses': today_analyses.order_by('-sample_time')[:5],
        })
        
        return context


class LineSummaryView(TemplateView):
    """
    Resumo público da linha de produção (acessível via QR Code)
    """
    template_name = 'core/line_summary_public.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        line_code = kwargs.get('line_code')
        line = get_object_or_404(ProductionLine, code=line_code)
        
        # Dados do turno atual
        current_shift = Shift.get_current_shift()
        today = timezone.now().date()
        
        # Análises de hoje
        today_analyses = SpotAnalysis.objects.filter(
            production_line=line,
            date=today
        ).select_related('property', 'product', 'shift')
        
        # Estatísticas
        total_today = today_analyses.count()
        approved_today = today_analyses.filter(status='APPROVED').count()
        alert_today = today_analyses.filter(status='ALERT').count()
        rejected_today = today_analyses.filter(status='REJECTED').count()
        
        # Últimas análises
        recent_analyses = today_analyses.order_by('-sample_time')[:10]
        
        # Análises por propriedade
        properties_summary = (
            today_analyses.values('property__identifier', 'property__name', 'property__unit')
            .annotate(
                count=Count('id'),
                avg_value=Avg('value')
            )
            .order_by('property__identifier')
        )
        
        context.update({
            'line': line,
            'current_shift': current_shift,
            'today': today,
            'total_today': total_today,
            'approved_today': approved_today,
            'alert_today': alert_today,
            'rejected_today': rejected_today,
            'approval_rate': (approved_today / total_today * 100) if total_today > 0 else 0,
            'recent_analyses': recent_analyses,
            'properties_summary': properties_summary,
            'is_public_view': True,
        })
        
        return context


class ShiftSummaryView(TemplateView):
    """
    Resumo do turno (acessível via QR Code)
    """
    template_name = 'core/shift_summary_public.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        date_str = kwargs.get('date')
        shift_name = kwargs.get('shift')
        line_id = kwargs.get('line_id')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise Http404("Data inválida")
        
        shift = get_object_or_404(Shift, name=shift_name)
        line = get_object_or_404(ProductionLine, id=line_id)
        
        # Análises do turno
        shift_analyses = SpotAnalysis.objects.filter(
            production_line=line,
            date=date,
            shift=shift
        ).select_related('property', 'product', 'operator')
        
        # Amostras compostas
        composite_samples = CompositeSample.objects.filter(
            production_line=line,
            date=date,
            shift=shift
        ).select_related('product', 'operator')
        
        # Estatísticas
        total_analyses = shift_analyses.count()
        approved = shift_analyses.filter(status='APPROVED').count()
        alert = shift_analyses.filter(status='ALERT').count()
        rejected = shift_analyses.filter(status='REJECTED').count()
        
        # Análises por produto
        products_summary = (
            shift_analyses.values('product__name', 'product__code')
            .annotate(count=Count('id'))
            .order_by('product__name')
        )
        
        context.update({
            'line': line,
            'shift': shift,
            'date': date,
            'shift_analyses': shift_analyses.order_by('property__identifier', 'sequence'),
            'composite_samples': composite_samples,
            'total_analyses': total_analyses,
            'approved': approved,
            'alert': alert,
            'rejected': rejected,
            'approval_rate': (approved / total_analyses * 100) if total_analyses > 0 else 0,
            'products_summary': products_summary,
            'is_public_view': True,
        })
        
        return context


class DataExportView(LoginRequiredMixin, TemplateView):
    """
    Interface para exportação de dados
    """
    template_name = 'core/data_export.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'production_lines': ProductionLine.objects.filter(is_active=True),
            'export_types': [
                ('spot_analyses', 'Análises Pontuais'),
                ('composite_samples', 'Amostras Compostas'),
                ('quality_reports', 'Laudos de Qualidade'),
            ]
        })
        
        return context


@login_required
def export_data(request):
    """
    Exporta dados baseado nos filtros
    """
    if request.method != 'POST':
        return redirect('core:data_export')
    
    export_type = request.POST.get('export_type')
    format_type = request.POST.get('format', 'excel')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    line_id = request.POST.get('line_id')
    
    try:
        # Converter datas
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Filtrar dados baseado no tipo
        if export_type == 'spot_analyses':
            queryset = SpotAnalysis.objects.select_related(
                'product', 'property', 'production_line', 'shift', 'operator'
            )
            
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
            if end_date:
                queryset = queryset.filter(date__lte=end_date)
            if line_id:
                queryset = queryset.filter(production_line_id=line_id)
            
            queryset = queryset.order_by('-date', '-sample_time')
            
            if format_type == 'excel':
                buffer, filename = DataExporter.export_spot_analyses_to_excel(queryset)
                response = HttpResponse(
                    buffer.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                
                # Log da exportação
                AuditLogger.log_data_export(request.user, 'SpotAnalysis', queryset.count())
                
                return response
            
        elif export_type == 'quality_reports':
            queryset = QualityReport.objects.select_related(
                'product', 'production_line', 'created_by', 'approved_by'
            )
            
            if start_date:
                queryset = queryset.filter(start_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(end_date__lte=end_date)
            if line_id:
                queryset = queryset.filter(production_line_id=line_id)
            
            queryset = queryset.order_by('-created_at')
            
            if format_type == 'excel':
                buffer, filename = DataExporter.export_quality_reports_to_excel(queryset)
                response = HttpResponse(
                    buffer.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                
                AuditLogger.log_data_export(request.user, 'QualityReport', queryset.count())
                
                return response
        
        messages.error(request, 'Tipo de exportação não suportado.')
        
    except Exception as e:
        messages.error(request, f'Erro na exportação: {str(e)}')
    
    return redirect('core:data_export')


class DataImportView(LoginRequiredMixin, TemplateView):
    """
    Interface para importação de dados
    """
    template_name = 'core/data_import.html'
    
    def post(self, request, *args, **kwargs):
        if 'import_file' not in request.FILES:
            messages.error(request, 'Nenhum arquivo selecionado.')
            return self.get(request, *args, **kwargs)
        
        import_file = request.FILES['import_file']
        import_type = request.POST.get('import_type', 'spot_analyses')
        
        try:
            # Salvar arquivo temporariamente
            file_path = default_storage.save(
                f'temp_imports/{import_file.name}',
                ContentFile(import_file.read())
            )
            
            full_path = default_storage.path(file_path)
            
            # Importar dados
            if import_type == 'spot_analyses':
                df, error = DataImporter.import_from_excel(full_path)
                
                if error:
                    messages.error(request, f'Erro ao ler arquivo: {error}')
                else:
                    imported_count, errors = DataImporter.import_spot_analyses_from_dataframe(
                        df, request.user
                    )
                    
                    if imported_count > 0:
                        messages.success(request, f'{imported_count} análises importadas com sucesso!')
                        
                        # Log da importação
                        AuditLogger.log_user_action(
                            user=request.user,
                            action='IMPORT_DATA',
                            object_type='SpotAnalysis',
                            object_id=None,
                            details={
                                'imported_count': imported_count,
                                'filename': import_file.name
                            }
                        )
                    
                    if errors:
                        error_msg = f'{len(errors)} erros encontrados:\n' + '\n'.join(errors[:10])
                        if len(errors) > 10:
                            error_msg += f'\n... e mais {len(errors) - 10} erros.'
                        messages.warning(request, error_msg)
            
            # Limpar arquivo temporário
            default_storage.delete(file_path)
            
        except Exception as e:
            messages.error(request, f'Erro na importação: {str(e)}')
        
        return self.get(request, *args, **kwargs)


class SystemStatsAPIView(LoginRequiredMixin, TemplateView):
    """
    API para estatísticas do sistema
    """
    
    def get(self, request, *args, **kwargs):
        # Estatísticas gerais
        total_analyses = SpotAnalysis.objects.count()
        total_reports = QualityReport.objects.count()
        total_samples = CompositeSample.objects.count()
        
        # Estatísticas dos últimos 30 dias
        last_30_days = timezone.now().date() - timedelta(days=30)
        
        recent_analyses = SpotAnalysis.objects.filter(date__gte=last_30_days)
        recent_reports = QualityReport.objects.filter(created_at__gte=last_30_days)
        
        # Taxa de aprovação
        approved_analyses = recent_analyses.filter(status='APPROVED').count()
        approval_rate = (approved_analyses / recent_analyses.count() * 100) if recent_analyses.count() > 0 else 0
        
        # Análises por linha
        lines_data = list(
            recent_analyses.values('production_line__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Análises por dia (últimos 7 dias)
        daily_data = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            count = SpotAnalysis.objects.filter(date=date).count()
            daily_data.append({
                'date': date.strftime('%d/%m'),
                'count': count
            })
        daily_data.reverse()
        
        return JsonResponse({
            'total_analyses': total_analyses,
            'total_reports': total_reports,
            'total_samples': total_samples,
            'recent_analyses': recent_analyses.count(),
            'recent_reports': recent_reports.count(),
            'approval_rate': round(approval_rate, 1),
            'lines_data': lines_data,
            'daily_data': daily_data,
        })


@login_required
def generate_shift_qr(request, line_id, date_str, shift_name):
    """
    Gera QR Code para turno específico
    """
    try:
        line = get_object_or_404(ProductionLine, id=line_id)
        shift = get_object_or_404(Shift, name=shift_name)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        qr_image = QRCodeGenerator.generate_shift_qr_code(line, shift, date)
        
        # Retornar imagem
        response = HttpResponse(content_type='image/png')
        qr_image.save(response, 'PNG')
        
        return response
        
    except Exception as e:
        return HttpResponse(f'Erro ao gerar QR Code: {str(e)}', status=400)


class BackupView(LoginRequiredMixin, TemplateView):
    """
    Interface para backup e restore
    """
    template_name = 'core/backup.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas para backup
        context.update({
            'total_analyses': SpotAnalysis.objects.count(),
            'total_reports': QualityReport.objects.count(),
            'total_samples': CompositeSample.objects.count(),
            'database_size': self._get_database_size(),
        })
        
        return context
    
    def _get_database_size(self):
        """
        Estima o tamanho do banco de dados
        """
        try:
            import os
            from django.conf import settings
            
            if 'sqlite' in settings.DATABASES['default']['ENGINE']:
                db_path = settings.DATABASES['default']['NAME']
                if os.path.exists(db_path):
                    size_bytes = os.path.getsize(db_path)
                    size_mb = size_bytes / (1024 * 1024)
                    return f"{size_mb:.2f} MB"
            
            return "N/A"
        except:
            return "N/A"


@login_required
def create_backup(request):
    """
    Cria backup dos dados
    """
    try:
        # Exportar todas as análises
        all_analyses = SpotAnalysis.objects.all().select_related(
            'product', 'property', 'production_line', 'shift', 'operator'
        )
        
        buffer, filename = DataExporter.export_spot_analyses_to_excel(
            all_analyses, 
            f"backup_completo_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Log do backup
        AuditLogger.log_user_action(
            user=request.user,
            action='CREATE_BACKUP',
            object_type='System',
            object_id=None,
            details={
                'record_count': all_analyses.count(),
                'backup_type': 'full'
            }
        )
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erro ao criar backup: {str(e)}')
        return redirect('core:backup')
