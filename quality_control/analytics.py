"""
Módulo de análises estatísticas para controle de qualidade
"""

import numpy as np
import pandas as pd
from scipy import stats
from django.db.models import Avg, StdDev, Count, Min, Max
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

from .models import SpotAnalysis, CompositeSample, Specification, Property


class QualityAnalytics:
    """
    Classe para análises estatísticas de qualidade
    """
    
    @staticmethod
    def calculate_basic_statistics(queryset) -> Dict:
        """
        Calcula estatísticas básicas para um queryset de análises
        """
        if not queryset.exists():
            return {
                'count': 0,
                'mean': None,
                'std': None,
                'min': None,
                'max': None,
                'median': None
            }
        
        values = list(queryset.values_list('value', flat=True))
        
        return {
            'count': len(values),
            'mean': np.mean(values),
            'std': np.std(values, ddof=1) if len(values) > 1 else 0,
            'min': np.min(values),
            'max': np.max(values),
            'median': np.median(values),
            'q25': np.percentile(values, 25),
            'q75': np.percentile(values, 75)
        }
    
    @staticmethod
    def calculate_capability_indices(values: List[float], lsl: float = None, usl: float = None, target: float = None) -> Dict:
        """
        Calcula índices de capabilidade (Cp, Cpk, Pp, Ppk)
        """
        if not values or len(values) < 2:
            return {}
        
        values_array = np.array(values)
        mean = np.mean(values_array)
        std = np.std(values_array, ddof=1)
        
        result = {
            'mean': mean,
            'std': std,
            'n': len(values)
        }
        
        # Cp e Cpk (capabilidade do processo)
        if lsl is not None and usl is not None:
            cp = (usl - lsl) / (6 * std) if std > 0 else None
            result['cp'] = cp
            
            if cp is not None:
                cpu = (usl - mean) / (3 * std)
                cpl = (mean - lsl) / (3 * std)
                cpk = min(cpu, cpl)
                result['cpk'] = cpk
                result['cpu'] = cpu
                result['cpl'] = cpl
        
        # Pp e Ppk (performance do processo)
        # Para simplificar, usando a mesma fórmula (em produção, usaria dados históricos mais longos)
        if 'cp' in result:
            result['pp'] = result['cp']
            result['ppk'] = result['cpk']
        
        # Porcentagem fora da especificação
        if lsl is not None and usl is not None:
            out_of_spec = np.sum((values_array < lsl) | (values_array > usl))
            result['percent_out_of_spec'] = (out_of_spec / len(values)) * 100
        
        return result
    
    @staticmethod
    def generate_control_chart_data(queryset, chart_type='individual') -> Dict:
        """
        Gera dados para cartas de controle SPC
        """
        if not queryset.exists():
            return {}
        
        # Ordenar por data e hora
        data = queryset.order_by('date', 'sample_time').values('date', 'sample_time', 'value', 'sequence')
        df = pd.DataFrame(data)
        
        if chart_type == 'individual':
            return QualityAnalytics._generate_individual_chart(df)
        elif chart_type == 'xbar_r':
            return QualityAnalytics._generate_xbar_r_chart(df)
        
        return {}
    
    @staticmethod
    def _generate_individual_chart(df: pd.DataFrame) -> Dict:
        """
        Gera carta I-MR (Individual-Moving Range)
        """
        values = df['value'].values
        
        if len(values) < 2:
            return {}
        
        # Carta Individual (I)
        mean = np.mean(values)
        
        # Moving Range
        moving_ranges = np.abs(np.diff(values))
        mr_mean = np.mean(moving_ranges)
        
        # Limites de controle para carta Individual
        ucl_i = mean + 2.66 * mr_mean
        lcl_i = mean - 2.66 * mr_mean
        
        # Limites de controle para carta Moving Range
        ucl_mr = 3.27 * mr_mean
        lcl_mr = 0  # Sempre zero para MR
        
        # Detectar pontos fora de controle
        out_of_control_i = (values > ucl_i) | (values < lcl_i)
        out_of_control_mr = moving_ranges > ucl_mr
        
        return {
            'chart_type': 'individual',
            'individual_chart': {
                'values': values.tolist(),
                'mean': mean,
                'ucl': ucl_i,
                'lcl': lcl_i,
                'out_of_control': out_of_control_i.tolist()
            },
            'moving_range_chart': {
                'values': moving_ranges.tolist(),
                'mean': mr_mean,
                'ucl': ucl_mr,
                'lcl': lcl_mr,
                'out_of_control': out_of_control_mr.tolist()
            },
            'timestamps': df['sample_time'].dt.strftime('%Y-%m-%d %H:%M').tolist()
        }
    
    @staticmethod
    def _generate_xbar_r_chart(df: pd.DataFrame) -> Dict:
        """
        Gera carta X̄-R (X-bar and Range)
        """
        # Agrupar por data e turno para formar subgrupos
        df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['sample_time'].astype(str))
        df['subgroup'] = df.groupby(['date']).ngroup()
        
        subgroups = df.groupby('subgroup')['value'].apply(list).values
        
        if len(subgroups) < 2:
            return {}
        
        # Calcular médias e ranges dos subgrupos
        xbar_values = [np.mean(subgroup) for subgroup in subgroups]
        range_values = [np.max(subgroup) - np.min(subgroup) for subgroup in subgroups]
        
        # Tamanho médio dos subgrupos
        n = np.mean([len(subgroup) for subgroup in subgroups])
        
        # Constantes para cartas de controle (aproximadas para n=2-5)
        A2_values = {2: 1.88, 3: 1.02, 4: 0.73, 5: 0.58}
        D3_values = {2: 0, 3: 0, 4: 0, 5: 0}
        D4_values = {2: 3.27, 3: 2.57, 4: 2.28, 5: 2.11}
        
        n_int = int(round(n))
        A2 = A2_values.get(n_int, 0.58)
        D3 = D3_values.get(n_int, 0)
        D4 = D4_values.get(n_int, 2.11)
        
        # Limites de controle
        xbar_mean = np.mean(xbar_values)
        range_mean = np.mean(range_values)
        
        ucl_xbar = xbar_mean + A2 * range_mean
        lcl_xbar = xbar_mean - A2 * range_mean
        
        ucl_r = D4 * range_mean
        lcl_r = D3 * range_mean
        
        # Detectar pontos fora de controle
        out_of_control_xbar = (np.array(xbar_values) > ucl_xbar) | (np.array(xbar_values) < lcl_xbar)
        out_of_control_r = (np.array(range_values) > ucl_r) | (np.array(range_values) < lcl_r)
        
        return {
            'chart_type': 'xbar_r',
            'xbar_chart': {
                'values': xbar_values,
                'mean': xbar_mean,
                'ucl': ucl_xbar,
                'lcl': lcl_xbar,
                'out_of_control': out_of_control_xbar.tolist()
            },
            'range_chart': {
                'values': range_values,
                'mean': range_mean,
                'ucl': ucl_r,
                'lcl': lcl_r,
                'out_of_control': out_of_control_r.tolist()
            },
            'subgroup_labels': [f"Subgrupo {i+1}" for i in range(len(subgroups))]
        }
    
    @staticmethod
    def calculate_correlation_matrix(chemical_data: List[Dict], physical_data: List[Dict]) -> Dict:
        """
        Calcula matriz de correlação entre variáveis químicas e físicas
        """
        if not chemical_data or not physical_data:
            return {}
        
        # Converter para DataFrames
        chem_df = pd.DataFrame(chemical_data)
        phys_df = pd.DataFrame(physical_data)
        
        # Combinar dados por identificador comum (ex: lote, data)
        if 'batch_id' in chem_df.columns and 'batch_id' in phys_df.columns:
            merged_df = pd.merge(chem_df, phys_df, on='batch_id', how='inner')
        else:
            # Se não houver identificador comum, usar índice
            merged_df = pd.concat([chem_df, phys_df], axis=1)
        
        # Selecionar apenas colunas numéricas
        numeric_cols = merged_df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {}
        
        # Calcular matriz de correlação
        corr_matrix = merged_df[numeric_cols].corr()
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'variables': numeric_cols.tolist(),
            'sample_size': len(merged_df)
        }
    
    @staticmethod
    def detect_trends_and_patterns(queryset, window_size: int = 7) -> Dict:
        """
        Detecta tendências e padrões nos dados
        """
        if not queryset.exists():
            return {}
        
        data = queryset.order_by('date', 'sample_time').values('date', 'value')
        df = pd.DataFrame(data)
        
        # Média móvel
        df['moving_avg'] = df['value'].rolling(window=window_size).mean()
        
        # Detectar tendência (regressão linear)
        x = np.arange(len(df))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, df['value'])
        
        # Detectar outliers (método IQR)
        Q1 = df['value'].quantile(0.25)
        Q3 = df['value'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df['value'] < lower_bound) | (df['value'] > upper_bound)]
        
        return {
            'trend': {
                'slope': slope,
                'r_squared': r_value ** 2,
                'p_value': p_value,
                'direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
            },
            'moving_average': df['moving_avg'].dropna().tolist(),
            'outliers': {
                'count': len(outliers),
                'indices': outliers.index.tolist(),
                'values': outliers['value'].tolist()
            },
            'statistics': {
                'mean': df['value'].mean(),
                'std': df['value'].std(),
                'cv': (df['value'].std() / df['value'].mean()) * 100 if df['value'].mean() != 0 else 0
            }
        }


class DashboardMetrics:
    """
    Classe para métricas do dashboard
    """
    
    @staticmethod
    def get_daily_summary(date: datetime.date = None) -> Dict:
        """
        Obtém resumo diário das análises
        """
        if date is None:
            date = timezone.now().date()
        
        spot_analyses = SpotAnalysis.objects.filter(date=date)
        composite_samples = CompositeSample.objects.filter(date=date)
        
        return {
            'date': date,
            'spot_analyses': {
                'total': spot_analyses.count(),
                'approved': spot_analyses.filter(status='APPROVED').count(),
                'alert': spot_analyses.filter(status='ALERT').count(),
                'rejected': spot_analyses.filter(status='REJECTED').count()
            },
            'composite_samples': {
                'total': composite_samples.count(),
                'approved': composite_samples.filter(status='APPROVED').count(),
                'rejected': composite_samples.filter(status='REJECTED').count()
            }
        }
    
    @staticmethod
    def get_weekly_trends(weeks: int = 4) -> Dict:
        """
        Obtém tendências semanais
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(weeks=weeks)
        
        # Agrupar por semana
        weekly_data = []
        current_date = start_date
        
        while current_date <= end_date:
            week_end = min(current_date + timedelta(days=6), end_date)
            
            spot_analyses = SpotAnalysis.objects.filter(
                date__range=[current_date, week_end]
            )
            
            weekly_data.append({
                'week_start': current_date,
                'week_end': week_end,
                'total_analyses': spot_analyses.count(),
                'approval_rate': (
                    spot_analyses.filter(status='APPROVED').count() / 
                    spot_analyses.count() * 100
                ) if spot_analyses.count() > 0 else 0
            })
            
            current_date = week_end + timedelta(days=1)
        
        return {
            'weeks': weekly_data,
            'period': f"{start_date} to {end_date}"
        }
