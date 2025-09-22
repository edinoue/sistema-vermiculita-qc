# Sistema de Controle de Qualidade - Vermiculita

## 📋 Visão Geral

Sistema completo de controle de qualidade para indústria de mineração de vermiculita, desenvolvido em Django com interface mobile-first, análises estatísticas avançadas e geração automática de laudos.

### 🎯 Objetivos

- **Fase 1**: Controle de Qualidade (✅ **CONCLUÍDA**)
- **Fase 2**: Controle de Produção (🔄 **PREPARADA**)

## 🚀 Funcionalidades Implementadas

### ✅ **Controle de Qualidade**
- **Análises Pontuais**: Registro de até 3 análises por turno por linha
- **Amostras Compostas**: Coleta ao final de cada turno
- **Especificações**: Limites de qualidade por produto/propriedade
- **Validação Automática**: Status baseado em especificações

### ✅ **Dashboards e Análises**
- **Dashboard Principal**: Métricas em tempo real
- **Cartas de Controle SPC**: I-MR e X̄-R
- **Análises de Capabilidade**: Cp, Cpk, Pp, Ppk
- **Correlações**: Entre variáveis químicas e físicas
- **Gráficos Interativos**: Chart.js com atualização automática

### ✅ **Sistema de Laudos**
- **Geração Automática**: PDFs profissionais
- **Workflow de Aprovação**: Rascunho → Pendente → Aprovado
- **Ordens de Carregamento**: Com QR codes automáticos
- **Templates Personalizáveis**: Layouts flexíveis

### ✅ **Interface Mobile-First**
- **Detecção Automática**: Dispositivos móveis
- **Formulários Otimizados**: Touch-friendly
- **QR Codes**: Acesso rápido às informações
- **Páginas Públicas**: Sem necessidade de login

### ✅ **Funcionalidades Auxiliares**
- **Exportação**: Excel e CSV com filtros
- **Importação**: Dados históricos via Excel
- **Backup**: Sistema completo
- **Auditoria**: Log de todas as ações
- **APIs REST**: Integração com outros sistemas

## 🏗️ Arquitetura Técnica

### **Backend**
- **Framework**: Django 5.2.6
- **API**: Django REST Framework
- **Banco de Dados**: PostgreSQL (produção) / SQLite (desenvolvimento)
- **Servidor**: Gunicorn
- **Arquivos Estáticos**: WhiteNoise

### **Frontend**
- **Framework**: Bootstrap 5
- **Gráficos**: Chart.js
- **Ícones**: Bootstrap Icons
- **Responsivo**: Mobile-first design

### **Dependências Principais**
```
Django==5.2.6
djangorestframework==3.16.1
psycopg2-binary==2.9.10
reportlab==4.2.5
openpyxl==3.1.5
pandas==2.3.2
qrcode[pil]==8.2
matplotlib==3.10.6
plotly==6.3.0
```

## 📊 Estrutura do Banco de Dados

### **Core Models**
- `Plant`: Plantas industriais
- `ProductionLine`: Linhas de produção
- `Shift`: Turnos de trabalho
- `UserProfile`: Perfis de usuário
- `AuditLog`: Log de auditoria

### **Quality Control Models**
- `Product`: Produtos da mineração
- `Property`: Propriedades físicas/químicas
- `Specification`: Especificações de qualidade
- `SpotAnalysis`: Análises pontuais
- `CompositeSample`: Amostras compostas
- `ChemicalAnalysis`: Análises químicas
- `QualityReport`: Laudos de qualidade
- `LoadingOrder`: Ordens de carregamento

## 🔧 Instalação e Configuração

### **Desenvolvimento Local**

1. **Clone o repositório**
```bash
git clone <repository-url>
cd vermiculita_qc
```

2. **Criar ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instalar dependências**
```bash
pip install -r requirements.txt
```

4. **Configurar banco de dados**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

5. **Popular dados iniciais**
```bash
python populate_initial_data.py
```

### **Deploy em Produção**

#### **Railway (Recomendado)**

1. **Criar conta**: [railway.app](https://railway.app)
2. **Conectar repositório**: GitHub/GitLab
3. **Configurar variáveis**:
   - `DJANGO_SETTINGS_MODULE=vermiculita_system.settings_production`
   - `SECRET_KEY=<sua-chave-secreta>`
   - `DEBUG=False`
4. **Deploy automático**: Push para main/master

#### **Render**

1. **Criar conta**: [render.com](https://render.com)
2. **Novo Web Service**: Conectar repositório
3. **Configurações**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `./start.sh`
4. **Variáveis de ambiente**: Copiar de `.env.production`

## 👥 Usuários e Permissões

### **Usuário Padrão**
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@vermiculita.com`

### **Perfis de Usuário**
- **Administrador**: Acesso total
- **Supervisor**: Aprovação de laudos
- **Operador**: Entrada de dados
- **Visualizador**: Apenas leitura

## 📱 Como Usar

### **Interface Web**
1. **Login**: Acesse com credenciais
2. **Dashboard**: Visualize métricas
3. **Nova Análise**: Registre dados
4. **Laudos**: Gere relatórios
5. **Exportação**: Baixe dados

### **Interface Mobile**
1. **Acesso Direto**: `/mobile/`
2. **QR Codes**: Escaneie para acesso rápido
3. **Formulários**: Otimizados para touch
4. **Offline**: Funciona sem internet

### **QR Codes**
- **Linha de Produção**: Informações em tempo real
- **Turno**: Dados específicos do turno
- **Laudo**: Acesso público ao documento
- **Ordem**: Rastreamento de carregamento

## 📈 Análises Estatísticas

### **Cartas de Controle**
- **Carta I-MR**: Valores individuais
- **Carta X̄-R**: Médias e amplitudes
- **Limites de Controle**: Calculados automaticamente
- **Detecção de Tendências**: Alertas automáticos

### **Índices de Capabilidade**
- **Cp**: Capabilidade potencial
- **Cpk**: Capabilidade real
- **Pp**: Performance potencial
- **Ppk**: Performance real

### **Análises de Correlação**
- **Matriz de Correlação**: Entre propriedades
- **Gráficos de Dispersão**: Visualização
- **Coeficientes**: Pearson e Spearman

## 📄 Geração de Laudos

### **Tipos de Laudo**
- **Qualidade**: Análises do período
- **Expedição**: Para carregamento
- **Especial**: Customizado

### **Conteúdo do Laudo**
- **Cabeçalho**: Informações da empresa
- **Dados do Produto**: Especificações
- **Resultados**: Análises realizadas
- **Conformidade**: Status vs especificações
- **Assinaturas**: Responsáveis técnicos

### **Formatos**
- **PDF**: Download direto
- **Impressão**: Layout otimizado
- **Digital**: Assinatura eletrônica

## 🔄 Importação/Exportação

### **Exportação**
- **Formatos**: Excel (.xlsx), CSV
- **Filtros**: Data, linha, produto
- **Dados**: Análises, laudos, amostras

### **Importação**
- **Formato**: Excel (.xlsx)
- **Validação**: Automática
- **Relatório**: Erros e sucessos
- **Mapeamento**: Inteligente

## 🔐 Segurança

### **Autenticação**
- **Django Auth**: Sistema padrão
- **Sessões**: Timeout configurável
- **Permissões**: Por grupo/usuário

### **Auditoria**
- **Log Completo**: Todas as ações
- **Rastreabilidade**: Quem, quando, o quê
- **Backup**: Automático
- **Retenção**: Configurável

## 🌐 APIs

### **Endpoints Principais**
- `/api/spot-analyses/`: Análises pontuais
- `/api/products/`: Produtos
- `/api/properties/`: Propriedades
- `/api/reports/`: Laudos
- `/api/dashboard/`: Dados do dashboard

### **Autenticação**
- **Token**: DRF Token
- **Session**: Django Session
- **Throttling**: Rate limiting

## 🔧 Manutenção

### **Backup**
```bash
# Backup completo
python manage.py dumpdata > backup.json

# Backup específico
python manage.py dumpdata quality_control > qc_backup.json
```

### **Logs**
- **Localização**: `/logs/django.log`
- **Rotação**: Automática
- **Níveis**: DEBUG, INFO, WARNING, ERROR

### **Monitoramento**
- **Health Check**: `/health/`
- **Status**: `/status/`
- **Métricas**: `/metrics/`

## 🚀 Roadmap - Fase 2

### **Controle de Produção** (Futuro)
- **Cadastro de Locais**: Minas, frentes
- **Registro de Produção**: Por turno
- **Controle de Máquinas**: Disponibilidade
- **Gestão de Estoque**: Integrada
- **Relatórios**: Rendimento e eficiência

### **Melhorias Planejadas**
- **Mobile App**: Nativo
- **BI Avançado**: Power BI integration
- **IoT**: Sensores automáticos
- **ML**: Predição de qualidade
- **Blockchain**: Rastreabilidade

## 📞 Suporte

### **Documentação**
- **Manual do Usuário**: `/docs/user/`
- **API Docs**: `/docs/api/`
- **Admin Guide**: `/docs/admin/`

### **Contato**
- **Email**: suporte@vermiculita.com
- **Telefone**: (11) 9999-9999
- **Chat**: Sistema interno

## 📄 Licença

Sistema proprietário desenvolvido para Mineração Vermiculita.
Todos os direitos reservados © 2025

---

**Versão**: 1.0.0  
**Última Atualização**: Setembro 2025  
**Desenvolvido por**: Equipe de Desenvolvimento  
**Status**: ✅ **PRODUÇÃO**
