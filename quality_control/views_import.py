"""
Views para sistema de importação de dados
"""

import pandas as pd
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import datetime, time
import json

from .models import Product, Property, ProductionLine, Shift, AnalysisType, SpotAnalysis, CompositeSample
from .models_import import ImportTemplate, ImportSession, ImportError

@login_required
def import_dashboard(request):
    """Dashboard de importação"""
    templates = ImportTemplate.objects.filter(is_active=True)
    recent_imports = ImportSession.objects.filter(user=request.user).order_by('-started_at')[:10]
    
    context = {
        'templates': templates,
        'recent_imports': recent_imports,
    }
    
    return render(request, 'quality_control/import_dashboard.html', context)

@login_required
def download_template(request, template_id):
    """Download do template de importação"""
    template = get_object_or_404(ImportTemplate, id=template_id, is_active=True)
    
    if template.excel_file:
        response = HttpResponse(template.excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{template.name}.xlsx"'
        return response
    else:
        messages.error(request, 'Arquivo de template não encontrado.')
        return redirect('quality_control:import_dashboard')

@login_required
def upload_data(request):
    """Upload e processamento de dados"""
    if request.method == 'POST':
        try:
            excel_file = request.FILES.get('excel_file')
            template_id = request.POST.get('template_id')
            
            if not excel_file:
                messages.error(request, 'Nenhum arquivo foi selecionado.')
                return redirect('quality_control:import_dashboard')
            
            # Criar sessão de importação
            session = ImportSession.objects.create(
                template_id=template_id,
                user=request.user,
                excel_file=excel_file,
                original_filename=excel_file.name,
                status='PENDING'
            )
            
            # Processar arquivo
            process_import_file(session)
            
            messages.success(request, f'Importação iniciada. ID da sessão: {session.id}')
            return redirect('quality_control:import_status', session_id=session.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao processar arquivo: {str(e)}')
            return redirect('quality_control:import_dashboard')
    
    return redirect('quality_control:import_dashboard')

def process_import_file(session):
    """Processar arquivo de importação"""
    try:
        session.status = 'PROCESSING'
        session.save()
        
        # Ler arquivo Excel
        excel_file = session.excel_file.path
        df_spot = pd.read_excel(excel_file, sheet_name='Analises_Pontuais')
        df_composite = pd.read_excel(excel_file, sheet_name='Amostras_Compostas')
        
        total_rows = len(df_spot) + len(df_composite)
        session.total_rows = total_rows
        session.save()
        
        # Processar análises pontuais
        spot_success = process_spot_analyses(session, df_spot)
        
        # Processar amostras compostas
        composite_success = process_composite_samples(session, df_composite)
        
        # Atualizar estatísticas
        session.processed_rows = total_rows
        session.successful_rows = spot_success + composite_success
        session.failed_rows = total_rows - (spot_success + composite_success)
        session.status = 'COMPLETED'
        session.completed_at = timezone.now()
        session.save()
        
    except Exception as e:
        session.status = 'FAILED'
        session.error_log = str(e)
        session.save()

def process_spot_analyses(session, df):
    """Processar análises pontuais"""
    success_count = 0
    
    for index, row in df.iterrows():
        try:
            # Validar dados obrigatórios
            required_fields = ['Data', 'Hora_Amostra', 'Tipo_Analise', 'Produto_Codigo', 'Linha_Producao', 'Turno']
            for field in required_fields:
                if pd.isna(row.get(field)):
                    raise ValueError(f'Campo obrigatório {field} está vazio')
            
            # Buscar objetos relacionados
            product = Product.objects.get(code=row['Produto_Codigo'])
            line = ProductionLine.objects.get(name=row['Linha_Producao'])
            shift = Shift.objects.get(name=row['Turno'])
            analysis_type = AnalysisType.objects.get(code=row['Tipo_Analise'])
            
            # Criar análise pontual
            analysis = SpotAnalysis.objects.create(
                analysis_type=analysis_type,
                date=row['Data'],
                product=product,
                production_line=line,
                shift=shift,
                sample_time=f"{row['Data']} {row['Hora_Amostra']}",
                sequence=row.get('Sequencia', 1),
                property=Property.objects.first(),  # Propriedade padrão
                value=row.get('Umidade_%', 0),
                unit=row.get('Umidade_%', '%'),
                test_method=row.get('Metodo_Teste', 'Método padrão'),
                status='PENDENTE'
            )
            
            success_count += 1
            
        except Exception as e:
            # Registrar erro
            ImportError.objects.create(
                session=session,
                row_number=index + 2,  # +2 porque Excel começa na linha 2
                error_type='VALIDATION_ERROR',
                error_message=str(e),
                raw_data=str(row.to_dict())
            )
    
    return success_count

def process_composite_samples(session, df):
    """Processar amostras compostas"""
    success_count = 0
    
    for index, row in df.iterrows():
        try:
            # Validar dados obrigatórios
            required_fields = ['Data_Coleta', 'Hora_Inicio', 'Hora_Fim', 'Tipo_Analise', 'Produto_Codigo', 'Linha_Producao', 'Turno']
            for field in required_fields:
                if pd.isna(row.get(field)):
                    raise ValueError(f'Campo obrigatório {field} está vazio')
            
            # Buscar objetos relacionados
            product = Product.objects.get(code=row['Produto_Codigo'])
            line = ProductionLine.objects.get(name=row['Linha_Producao'])
            shift = Shift.objects.get(name=row['Turno'])
            
            # Criar amostra composta
            sample = CompositeSample.objects.create(
                product=product,
                production_line=line,
                shift=shift,
                collection_date=row['Data_Coleta'],
                start_time=f"{row['Data_Coleta']} {row['Hora_Inicio']}",
                end_time=f"{row['Data_Coleta']} {row['Hora_Fim']}",
                status='PENDENTE'
            )
            
            success_count += 1
            
        except Exception as e:
            # Registrar erro
            ImportError.objects.create(
                session=session,
                row_number=index + 2,  # +2 porque Excel começa na linha 2
                error_type='VALIDATION_ERROR',
                error_message=str(e),
                raw_data=str(row.to_dict())
            )
    
    return success_count

@login_required
def import_status(request, session_id):
    """Status da importação"""
    session = get_object_or_404(ImportSession, id=session_id, user=request.user)
    errors = session.errors.all()
    
    context = {
        'session': session,
        'errors': errors,
    }
    
    return render(request, 'quality_control/import_status.html', context)

@login_required
def download_errors(request, session_id):
    """Download dos erros de importação"""
    session = get_object_or_404(ImportSession, id=session_id, user=request.user)
    errors = session.errors.all()
    
    # Criar DataFrame com erros
    error_data = []
    for error in errors:
        error_data.append({
            'Linha': error.row_number,
            'Coluna': error.column_name,
            'Tipo_Erro': error.error_type,
            'Mensagem': error.error_message,
            'Dados_Brutos': error.raw_data
        })
    
    df = pd.DataFrame(error_data)
    
    # Criar arquivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="erros_importacao_{session_id}.xlsx"'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Erros', index=False)
    
    return response

@login_required
def create_template(request):
    """Criar template de importação"""
    if request.method == 'POST':
        try:
            # Criar template
            template = ImportTemplate.objects.create(
                name=request.POST.get('name'),
                template_type=request.POST.get('template_type'),
                description=request.POST.get('description'),
                created_by=request.user
            )
            
            messages.success(request, 'Template criado com sucesso!')
            return redirect('quality_control:import_dashboard')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar template: {str(e)}')
    
    return render(request, 'quality_control/create_template.html')

