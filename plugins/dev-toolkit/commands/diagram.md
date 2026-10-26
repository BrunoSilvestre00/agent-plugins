---
description: Gera ou atualiza o diagrama de arquitetura (.drawio, ícones oficiais AWS4) de um PBI/épico, priorizando a IaC real do repositório quando existir
argument-hint: "[PBI-ID ou chave do épico — opcional, senão pergunta o que diagramar]"
---

# Diagrama de arquitetura

Entrada (pode estar vazia): $ARGUMENTS

Comando isolado, chamável direto ou a partir de `/dev-toolkit:refine`
(Camada 5) e `/dev-toolkit:work-task` (Fase 3 e, opcionalmente, Fase 9) —
nenhum dos dois duplica esta lógica, só apontam pra cá.

## Passos

1. **Verifique se a skill `aws-architecture-diagram` está disponível**
   nesta sessão (plugin oficial `deploy-on-aws`, marketplace
   `awslabs/agent-plugins` — gera XML `.drawio` com os ícones oficiais
   AWS4, abre direto em app.diagrams.net/draw.io).
   - **Não disponível**: mencione a instalação como opção —
     `/plugin marketplace add awslabs/agent-plugins` e
     `/plugin install deploy-on-aws@agent-plugins-for-aws`. **NUNCA
     instale por conta própria.** Avise que ela exige Python 3.9+ e o
     pacote `defusedxml` (pip), e que instala o plugin inteiro (traz
     junto outras 2 skills e 3 MCP servers da AWS — instalação de plugin
     não é a-la-carte). Sem interesse, ofereça um diagrama Mermaid
     simples como alternativa (sem ícones da AWS, mas sem dependência
     nenhuma — o próprio Claude Code renderiza) e pare aqui.
   - Se o time não usa AWS como cloud provider, avise que a skill é
     AWS-específica e ofereça só a alternativa Mermaid.

2. **Determine o alvo**, por ordem de prioridade:
   - `$ARGUMENTS` com um PBI-ID ou chave de épico: busque a issue no
     Jira. Se for um PBI, busque o épico pai; se houver um comentário
     `## Decisão de Arquitetura`, essa é a fonte de conteúdo (contexto,
     decisão proposta, repositórios afetados).
   - `$ARGUMENTS` vazio: pergunte o que diagramar — um PBI/épico
     específico, ou "analisar este repositório como está".
   - Nunca invente conteúdo do PBI/épico que não veio do Jira.

3. **Escolha o modo — prefira sempre a IaC real, quando existir, mas
   escopada ao que importa, não o repositório inteiro por acaso**:
   - **Veio de um PBI específico já implementado** (ex.: chamado pela
     Fase 9 do `work-task`, depois do PR aberto ou com a branch
     `feat/{PBI-ID}` ainda viva): escopar a IaC ao `git diff
     {base_branch}...feat/{PBI-ID}` daquele repositório — só o que ESTE
     PBI criou/alterou, não qualquer arquivo de IaC que já existia no
     repo de um trabalho anterior sem relação.
   - **Veio de um PBI/épico ainda não implementado, ou de "analisar este
     repositório como está"** (sem diff nenhum pra escopar, ex.: durante
     `/refine`, a Fase 3 do `work-task`, ou invocação direta sem
     contexto): verifique se o(s) repositório(s) afetados (ou o
     repositório atual) já têm arquivos de IaC reais no estado atual:
     CloudFormation (`AWSTemplateFormatVersion`), CDK (`cdk.json`,
     construct definitions), Terraform (`resource "aws_*"`). Isso é
     literalmente o que o **Modo A (Análise de código)** da skill já faz
     sozinho — não reimplemente a detecção, apenas invoque a skill nesse
     modo quando achar arquivo de IaC.
   - **Achou IaC real** (escopada ou não, conforme o caso acima): invoque
     a skill em **Modo A**, passando o(s) repositório(s)/diff a escanear.
     Se também houver um ADR (passo 2), passe o texto dele como contexto
     adicional — a skill combina infra real descoberta no código com a
     narrativa da decisão, não escolhe um em detrimento do outro. Isto é
     o que dá um diagrama fiel ao que **existe de verdade**, não só ao
     que foi proposto.
   - **Sem IaC ainda** (proposta pré-implementação): invoque a skill em
     **Modo B (Brainstorm)**, usando o texto do ADR (ou a descrição que o
     usuário der) como entrada.
   - Confirme com o usuário o modo escolhido e o conteúdo antes de gerar,
     se não estiver óbvio pelo contexto — a skill já pede essa
     confirmação internamente no Modo A (passo "confirme a arquitetura
     descoberta"); não duplique a pergunta se ela já vai perguntar.

4. **Criar vs. atualizar**: com PBI/épico (passo 2), procure em `docs/`
   um `.drawio` já existente referenciando o slug/ID. Sem PBI/épico
   ("analisar este repositório como está"), procure por nome descritivo
   da arquitetura em vez de ID. Se achar, pergunte ao usuário se quer
   **atualizar** o existente ou criar um novo — a skill suporta os dois,
   mas por padrão sempre cria arquivo novo; só atualiza se pedido
   explicitamente. Nunca decida sozinho qual dos dois.

5. **Depois de gerado**: a skill já reporta caminho do arquivo, tipo de
   diagrama, status de validação e o link de preview do
   app.diagrams.net. Repasse isso ao usuário sem resumir.

6. **Ofereça linkar o resultado** — comentário no épico (junto ou logo
   após o `## Decisão de Arquitetura`, se houver) ou na descrição do PBI
   — **só com confirmação explícita do usuário**, nunca automaticamente.
   Sem PBI/épico envolvido ("analisar este repositório como está"), não
   há onde linkar — pule este passo, o arquivo em `docs/` já é o
   suficiente.

## Regras

- NUNCA instale plugin/marketplace nenhum por conta própria — só
  mencione a opção.
- NUNCA invente conteúdo de PBI/épico que não veio do Jira.
- NUNCA decida sozinho entre criar novo ou atualizar um diagrama
  existente — pergunte.
- NUNCA comente no Jira sem confirmação explícita do usuário.
- Prefira sempre Modo A (análise de IaC real) quando houver arquivo de
  IaC pra escanear — só cai pro Modo B (brainstorm a partir do ADR/PBI)
  quando não há nada ainda pra analisar.
