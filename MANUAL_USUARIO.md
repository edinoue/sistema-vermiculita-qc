# Manual do Usuário - Sistema de Controle de Qualidade

## Introdução

O Sistema de Controle de Qualidade da Vermiculita é uma plataforma completa desenvolvida para gerenciar e monitorar a qualidade dos produtos de mineração. Este manual fornece instruções detalhadas sobre como utilizar todas as funcionalidades do sistema.

## Acesso ao Sistema

### Login Inicial

Para acessar o sistema, utilize as credenciais fornecidas pelo administrador. O usuário padrão para testes é:

- **Usuário**: admin
- **Senha**: admin123

Após o primeiro acesso, recomenda-se alterar a senha através do menu de perfil do usuário.

### Interface Principal

A página inicial apresenta um dashboard com as principais funcionalidades organizadas em cards intuitivos. O sistema detecta automaticamente dispositivos móveis e oferece uma interface otimizada para smartphones e tablets.

## Funcionalidades Principais

### Análises Pontuais

As análises pontuais representam o coração do sistema de controle de qualidade. Durante cada turno de 12 horas, é possível registrar até três medições por linha de produção para cada propriedade do produto.

**Como registrar uma análise pontual:**

1. Acesse o menu "Nova Análise" na página inicial
2. Selecione a linha de produção onde a análise foi realizada
3. Escolha o produto que está sendo analisado
4. O sistema carregará automaticamente as propriedades aplicáveis ao produto selecionado
5. Insira o valor medido para cada propriedade
6. O sistema calculará automaticamente o status (Aprovado/Alerta/Rejeitado) baseado nas especificações cadastradas
7. Adicione observações se necessário
8. Confirme o registro

O sistema valida automaticamente os dados inseridos contra as especificações de qualidade cadastradas, alertando imediatamente sobre valores fora dos limites estabelecidos.

### Dashboard e Análises Estatísticas

O dashboard oferece uma visão completa da qualidade em tempo real, incluindo gráficos interativos e métricas importantes.

**Cartas de Controle Estatístico:**

O sistema gera automaticamente cartas de controle SPC (Statistical Process Control) para monitoramento contínuo da qualidade. Duas modalidades estão disponíveis:

- **Carta I-MR**: Para valores individuais e amplitude móvel
- **Carta X̄-R**: Para médias e amplitudes de subgrupos

As cartas incluem limites de controle calculados automaticamente e detecção de tendências, fornecendo alertas quando o processo sai de controle estatístico.

**Análises de Capabilidade:**

O sistema calcula índices de capabilidade do processo, incluindo Cp, Cpk, Pp e Ppk, oferecendo uma visão quantitativa da capacidade do processo em atender às especificações.

### Sistema de Laudos

A geração de laudos de qualidade é completamente automatizada, produzindo documentos profissionais em formato PDF.

**Processo de criação de laudos:**

1. Acesse o menu "Laudos de Qualidade"
2. Clique em "Novo Laudo"
3. Defina o período de análise (data inicial e final)
4. Selecione a linha de produção e produto
5. Insira informações do cliente e destino
6. O sistema populará automaticamente todas as análises do período
7. Revise as informações e salve como rascunho
8. Submeta para aprovação quando estiver completo

O laudo gerado inclui todas as análises realizadas no período, conformidade com especificações, gráficos de tendência e assinaturas dos responsáveis técnicos.

### Ordens de Carregamento

Cada laudo aprovado pode gerar ordens de carregamento com QR codes únicos para rastreabilidade completa.

**Criação de ordens de carregamento:**

1. A partir de um laudo aprovado, clique em "Gerar Ordem de Carregamento"
2. Insira dados do veículo e motorista
3. Defina a data programada para carregamento
4. O sistema gerará automaticamente um QR code único
5. A ordem pode ser acompanhada em tempo real (Pendente → Em Andamento → Concluída)

### Interface Mobile e QR Codes

O sistema oferece uma interface completamente otimizada para dispositivos móveis, permitindo que operadores registrem análises diretamente no chão de fábrica.

**Funcionalidades mobile:**

- Formulários com campos grandes e fáceis de tocar
- Detecção automática do turno atual
- Carregamento dinâmico de propriedades por produto
- Validação em tempo real
- Funcionamento offline básico

**QR Codes para acesso rápido:**

Cada linha de produção possui um QR code único que, quando escaneado, leva a uma página pública com informações em tempo real da linha, incluindo análises do turno atual e estatísticas do dia.

## Exportação e Importação de Dados

### Exportação

O sistema oferece funcionalidades robustas de exportação em múltiplos formatos:

**Tipos de exportação disponíveis:**

- **Análises Pontuais**: Todas as medições realizadas com filtros por período, linha e produto
- **Laudos de Qualidade**: Relatórios completos com status e aprovações
- **Amostras Compostas**: Dados das amostras coletadas ao final dos turnos

**Formatos suportados:**

- **Excel (.xlsx)**: Formato recomendado com formatação profissional e múltiplas planilhas
- **CSV**: Formato simples para integração com outros sistemas

### Importação

Para facilitar a migração de dados históricos, o sistema suporta importação via arquivos Excel com validação automática e relatório de erros detalhado.

**Processo de importação:**

1. Baixe o template de importação disponível no sistema
2. Preencha os dados seguindo o formato especificado
3. Faça upload do arquivo através da interface de importação
4. O sistema validará automaticamente todos os dados
5. Revise o relatório de validação
6. Confirme a importação dos dados válidos

## Administração do Sistema

### Cadastros Básicos

O sistema requer alguns cadastros fundamentais para funcionamento adequado:

**Produtos**: Cadastre todos os produtos da mineração com códigos únicos e categorias apropriadas.

**Propriedades**: Defina as propriedades físicas e químicas que serão analisadas, incluindo unidades de medida e categorias.

**Especificações**: Estabeleça os limites de qualidade para cada combinação produto-propriedade, incluindo limites inferior e superior de especificação e valores alvo.

**Linhas de Produção**: Configure as linhas de produção com códigos únicos e associação às plantas industriais.

### Gestão de Usuários

O sistema suporta múltiplos perfis de usuário com permissões específicas:

- **Administradores**: Acesso completo a todas as funcionalidades
- **Supervisores**: Podem aprovar laudos e acessar relatórios gerenciais
- **Operadores**: Focados na entrada de dados e consultas básicas
- **Visualizadores**: Acesso apenas para consulta e relatórios

### Backup e Segurança

O sistema inclui funcionalidades de backup automático e manual, garantindo a segurança dos dados históricos. Todos os acessos e modificações são registrados em logs de auditoria para rastreabilidade completa.

## Solução de Problemas

### Problemas Comuns

**Erro ao salvar análise**: Verifique se todos os campos obrigatórios foram preenchidos e se os valores estão dentro dos limites técnicos aceitáveis.

**QR Code não funciona**: Certifique-se de que o dispositivo está conectado à internet e que o aplicativo de câmera tem permissão para acessar links.

**Laudo não gera PDF**: Verifique se existem análises no período selecionado e se o laudo foi aprovado.

**Interface lenta**: Limpe o cache do navegador e verifique a conexão com a internet.

### Suporte Técnico

Para questões técnicas ou dúvidas sobre funcionalidades, entre em contato com a equipe de suporte através dos canais disponíveis no sistema ou consulte a documentação técnica completa.

## Boas Práticas

### Entrada de Dados

Mantenha consistência na entrada de dados, sempre verificando as unidades de medida e a precisão dos valores inseridos. Utilize o campo de observações para registrar informações relevantes sobre condições especiais durante a análise.

### Monitoramento

Acompanhe regularmente os dashboards e cartas de controle para identificar tendências e tomar ações preventivas antes que problemas de qualidade se manifestem.

### Backup

Realize exportações periódicas dos dados como backup adicional, especialmente antes de grandes atualizações do sistema ou mudanças na configuração.

Este manual será atualizado conforme novas funcionalidades sejam implementadas. Mantenha-se informado sobre atualizações através dos canais de comunicação internos.
