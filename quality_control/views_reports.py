"""
Views para geração de relatórios
"""

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
import json

from .models import SpotAnalysis, CompositeSample, Product, Property, ProductionLine
from .models_import import ImportTemplate, ImportSession


@login_required
def generate_report(request):
    """Gerar relatório em PDF"""
    try:
        # Obter parâmetros
        report_type = request.GET.get('type', 'monthly')
        product_id = request.GET.get('product')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        # Definir período padrão
        if not date_from:
            date_from = (timezone.now() - timedelta(days=30)).date()
        if not date_to:
            date_to = timezone.now().date()
        
        # Filtrar análises
        spot_analyses = SpotAnalysis.objects.filter(
            sample_time__date__range=[date_from, date_to]
        )
        
        composite_samples = CompositeSample.objects.filter(
            date__range=[date_from, date_to]
        )
        
        if product_id:
            spot_analyses = spot_analyses.filter(product_id=product_id)
            composite_samples = composite_samples.filter(product_id=product_id)
        
        # Gerar dados do relatório
        report_data = {
            'period': f"{date_from} a {date_to}",
            'total_spot_analyses': spot_analyses.count(),
            'total_composite_samples': composite_samples.count(),
            'products': Product.objects.filter(is_active=True),
            'properties': Property.objects.filter(is_active=True),
        }
        
        # Análises por produto
        spot_by_product = spot_analyses.values('product__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        composite_by_product = composite_samples.values('product__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        report_data['spot_by_product'] = list(spot_by_product)
        report_data['composite_by_product'] = list(composite_by_product)
        
        # Análises por propriedade
        spot_by_property = spot_analyses.values('property__name').annotate(
            count=Count('id'),
            avg_value=Avg('value')
        ).order_by('-count')
        
        report_data['spot_by_property'] = list(spot_by_property)
        
        # Gerar HTML do relatório
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Relatório de Qualidade - {report_data['period']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c5530; }}
                h2 {{ color: #4a7c59; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Relatório de Controle de Qualidade</h1>
            <p><strong>Período:</strong> {report_data['period']}</p>
            
            <div class="summary">
                <h2>Resumo Executivo</h2>
                <p><strong>Total de Análises Pontuais:</strong> {report_data['total_spot_analyses']}</p>
                <p><strong>Total de Amostras Compostas:</strong> {report_data['total_composite_samples']}</p>
                <p><strong>Total Geral:</strong> {report_data['total_spot_analyses'] + report_data['total_composite_samples']}</p>
            </div>
            
            <h2>Análises por Produto</h2>
            <table>
                <tr>
                    <th>Produto</th>
                    <th>Análises Pontuais</th>
                    <th>Amostras Compostas</th>
                    <th>Total</th>
                </tr>
        """
        
        # Combinar dados por produto
        all_products = {}
        for item in report_data['spot_by_product']:
            all_products[item['product__name']] = {
                'spot': item['count'],
                'composite': 0
            }
        
        for item in report_data['composite_by_property']:
            if item['product__name'] in all_products:
                all_products[item['product__name']]['composite'] = item['count']
            else:
                all_products[item['product__name']] = {
                    'spot': 0,
                    'composite': item['count']
                }
        
        for product_name, data in all_products.items():
            total = data['spot'] + data['composite']
            html_content += f"""
                <tr>
                    <td>{product_name}</td>
                    <td>{data['spot']}</td>
                    <td>{data['composite']}</td>
                    <td>{total}</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h2>Análises por Propriedade</h2>
            <table>
                <tr>
                    <th>Propriedade</th>
                    <th>Quantidade</th>
                    <th>Valor Médio</th>
                </tr>
        """
        
        for item in report_data['spot_by_property']:
            html_content += f"""
                <tr>
                    <td>{item['property__name']}</td>
                    <td>{item['count']}</td>
                    <td>{item['avg_value']:.2f if item['avg_value'] else 'N/A'}</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <p><em>Relatório gerado em: """ + timezone.now().strftime('%d/%m/%Y %H:%M') + """</em></p>
        </body>
        </html>
        """
        
        # Retornar como HTML (pode ser convertido para PDF)
        return HttpResponse(html_content, content_type='text/html')
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def download_report(request):
    """Download de relatório"""
    try:
        # Gerar relatório
        response = generate_report(request)
        
        # Se for HTML, converter para PDF (implementar conversão se necessário)
        if response.status_code == 200:
            response['Content-Disposition'] = 'attachment; filename="relatorio_qualidade.html"'
            return response
        else:
            return JsonResponse({'error': 'Erro ao gerar relatório'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





