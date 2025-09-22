# Guia de Deploy - Sistema de Controle de Qualidade

## Visão Geral

Este guia fornece instruções detalhadas para fazer o deploy do Sistema de Controle de Qualidade em diferentes plataformas de nuvem. O sistema foi desenvolvido para ser facilmente deployado em serviços gratuitos como Railway e Render.

## Pré-requisitos

Antes de iniciar o deploy, certifique-se de ter:

- Conta no GitHub, GitLab ou Bitbucket com o código do projeto
- Conta na plataforma de deploy escolhida (Railway, Render, etc.)
- Conhecimento básico de Git e variáveis de ambiente

## Deploy no Railway (Recomendado)

O Railway oferece uma plataforma moderna e gratuita ideal para aplicações Django. O processo de deploy é automatizado e inclui banco PostgreSQL gratuito.

### Passo 1: Preparação do Repositório

Certifique-se de que todos os arquivos necessários estão no repositório:

- `railway.json`: Configuração específica do Railway
- `Procfile`: Comandos de inicialização
- `requirements.txt`: Dependências Python
- `runtime.txt`: Versão do Python
- `start.sh`: Script de inicialização personalizado

### Passo 2: Criação do Projeto

1. Acesse [railway.app](https://railway.app) e faça login
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Conecte sua conta GitHub e selecione o repositório
5. O Railway detectará automaticamente que é uma aplicação Django

### Passo 3: Configuração do Banco de Dados

1. No dashboard do projeto, clique em "Add Service"
2. Selecione "PostgreSQL"
3. O Railway criará automaticamente uma instância PostgreSQL
4. A variável `DATABASE_URL` será configurada automaticamente

### Passo 4: Configuração de Variáveis de Ambiente

Configure as seguintes variáveis no Railway:

```
DJANGO_SETTINGS_MODULE=vermiculita_system.settings_production
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=False
ALLOWED_HOSTS=*
COMPANY_NAME=Mineração Vermiculita
TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br
```

### Passo 5: Deploy Automático

1. Faça push do código para o branch principal
2. O Railway iniciará automaticamente o build e deploy
3. Acompanhe os logs para verificar se tudo está funcionando
4. Após o deploy, acesse a URL fornecida pelo Railway

## Deploy no Render

O Render é uma alternativa excelente ao Railway, também oferecendo tier gratuito com PostgreSQL.

### Passo 1: Criação do Web Service

1. Acesse [render.com](https://render.com) e faça login
2. Clique em "New +" e selecione "Web Service"
3. Conecte seu repositório GitHub/GitLab
4. Configure as seguintes opções:
   - **Name**: vermiculita-qc
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `./start.sh`

### Passo 2: Configuração do Banco PostgreSQL

1. Clique em "New +" e selecione "PostgreSQL"
2. Configure o nome do banco
3. Anote a URL de conexão fornecida

### Passo 3: Variáveis de Ambiente

Configure as mesmas variáveis do Railway, adicionando:

```
DATABASE_URL=postgresql://user:password@host:port/database
```

### Passo 4: Deploy

O Render iniciará automaticamente o build após a configuração. O processo pode levar alguns minutos na primeira vez.

## Deploy no Heroku

Embora o Heroku não ofereça mais tier gratuito, ainda é uma opção robusta para produção.

### Passo 1: Instalação do Heroku CLI

```bash
# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh

# macOS
brew tap heroku/brew && brew install heroku

# Windows
# Baixe o instalador do site oficial
```

### Passo 2: Criação da Aplicação

```bash
heroku login
heroku create vermiculita-qc
heroku addons:create heroku-postgresql:mini
```

### Passo 3: Configuração de Variáveis

```bash
heroku config:set DJANGO_SETTINGS_MODULE=vermiculita_system.settings_production
heroku config:set SECRET_KEY=sua-chave-secreta
heroku config:set DEBUG=False
```

### Passo 4: Deploy

```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

## Configurações de Produção

### Segurança

O arquivo `settings_production.py` inclui configurações de segurança essenciais:

- HTTPS obrigatório em produção
- Headers de segurança configurados
- Cookies seguros habilitados
- Proteção CSRF ativa

### Performance

Para melhor performance em produção:

- WhiteNoise para servir arquivos estáticos
- Gunicorn com múltiplos workers
- Cache configurado (pode ser expandido com Redis)
- Compressão de arquivos estáticos

### Monitoramento

Configure monitoramento básico:

- Logs estruturados em arquivos
- Health checks automáticos
- Métricas de sistema disponíveis

## Configuração de Domínio Personalizado

### Railway

1. No dashboard do projeto, vá para "Settings"
2. Na seção "Domains", clique em "Add Domain"
3. Insira seu domínio personalizado
4. Configure os registros DNS conforme instruído

### Render

1. Vá para "Settings" do seu web service
2. Na seção "Custom Domains", adicione seu domínio
3. Configure os registros DNS apontando para o Render

## Backup e Manutenção

### Backup do Banco de Dados

**Railway:**
```bash
# Conectar ao banco via Railway CLI
railway connect postgresql
# Fazer backup
pg_dump $DATABASE_URL > backup.sql
```

**Render:**
```bash
# Usar a URL do PostgreSQL fornecida
pg_dump postgresql://user:pass@host:port/db > backup.sql
```

### Atualizações

Para atualizar o sistema:

1. Faça as alterações no código
2. Teste localmente
3. Faça commit e push para o repositório
4. O deploy será automático nas plataformas configuradas

### Logs e Debugging

**Railway:**
```bash
railway logs
```

**Render:**
Acesse os logs através do dashboard web

**Heroku:**
```bash
heroku logs --tail
```

## Solução de Problemas

### Erro de Build

Se o build falhar, verifique:

- Todas as dependências estão no `requirements.txt`
- A versão do Python está correta no `runtime.txt`
- Não há erros de sintaxe no código

### Erro de Banco de Dados

Para problemas de conexão com banco:

- Verifique se a variável `DATABASE_URL` está configurada
- Confirme que as migrações foram executadas
- Teste a conexão localmente com as mesmas credenciais

### Erro de Arquivos Estáticos

Se arquivos CSS/JS não carregam:

- Execute `python manage.py collectstatic` localmente
- Verifique se o WhiteNoise está configurado corretamente
- Confirme que `STATIC_ROOT` está definido

### Performance Lenta

Para melhorar performance:

- Ative cache com Redis se disponível
- Otimize queries do banco de dados
- Configure CDN para arquivos estáticos
- Monitore uso de memória e CPU

## Configurações Avançadas

### SSL/TLS

Todas as plataformas mencionadas oferecem SSL gratuito. Certifique-se de que:

- `SECURE_SSL_REDIRECT = True` em produção
- Cookies estão configurados como seguros
- Headers HSTS estão ativos

### Escalabilidade

Para aplicações com maior demanda:

- Configure múltiplos workers do Gunicorn
- Implemente cache distribuído com Redis
- Use CDN para arquivos estáticos
- Configure load balancer se necessário

### Integração Contínua

Configure CI/CD para automatizar deploys:

- GitHub Actions para testes automáticos
- Deploy automático após merge na main
- Rollback automático em caso de falha

Este guia cobre os cenários mais comuns de deploy. Para situações específicas ou problemas não cobertos aqui, consulte a documentação oficial das plataformas ou entre em contato com o suporte técnico.
