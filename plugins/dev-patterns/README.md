# dev-patterns

Plugin para Claude Code e Codex **autossuficiente**: skills de convenção de código do
time — geral e por stack. Não depende de MCP nem de nenhum servidor
externo — instala e usa.

**Compatibilidade:** as regras estão em skills compartilhadas. Nos exemplos
abaixo, `/dev-patterns:ação` é a entrada do Claude Code; no Codex use
`$dev-patterns:dev-patterns-ação` (por exemplo, `$dev-patterns:dev-patterns-scaffold-backend meu-servico`).
Quando o texto mencionar `CLAUDE.md`, no Codex o arquivo novo é `AGENTS.md`;
uma seção de configuração já existente em qualquer um deles é reutilizada.
Veja a [tabela completa e as regras de configuração](../../README.md#uso-nos-dois-agentes).

Cobre hoje:

- **Frontend** (React 18 + TypeScript + Redux + styled-components),
  minerado de um projeto legado real — separando o que é bom a
  replicar do que é resquício a evitar, e preenchendo lacunas de
  prática, notadamente TDD.
- **Backend** (Python + Clean/Hexagonal Architecture: entidade de
  domínio, caso de uso, repositório + Unit of Work, evento de domínio,
  port & adapter para integração externa, endpoint FastAPI), minerado de
  um serviço em produção — aqui o padrão em si já era sólido, a lacuna
  era não ter sido transformado em skill nenhuma ainda.
- **DevOps / Infra as Code** (Terraform + AWS: state remoto, identidades
  OIDC, mínimo privilégio), minerado de dois projetos reais (um de
  serviço único, outro com múltiplos contexts/serviços) — cruzado entre
  os dois pra separar convenção real do time de decisão pontual de um
  projeto só.
- **Observability** (Datadog: instrumentação Python + Lambda/Terraform),
  minerado de três serviços reais — aqui a mineração encontrou uma
  lacuna real, não só ausência de skill: um serviço com
  `patch(fastapi=True)` como única instrumentação nunca traceava sua
  chamada de saída pro provedor externo nem suas queries de banco, e um
  conjunto de Lambdas tinha exclusão de log configurada sem nenhuma
  layer/dependência do Datadog. As skills já nascem corrigindo os dois
  achados, não os replicando.

## Instalação

### Claude Code

```bash
# 1. Adicionar o marketplace (uma vez por dev — mesmo passo do dev-toolkit)
claude plugin marketplace add BrunoSilvestre00/agent-plugins

# 2. Instalar
claude plugin install dev-patterns@ai-plugins
```

### Codex

No terminal, com uma versão que ofereça `codex plugin add`:

```bash
codex plugin marketplace add BrunoSilvestre00/agent-plugins
codex plugin add dev-patterns@ai-plugins
```

Abra uma nova conversa após instalar. Para atualizar o catálogo, use
`codex plugin marketplace upgrade ai-plugins` e atualize/reinstale o plugin.
Os requisitos e o teste de instalação estão no [README principal](../../README.md).

As skills ficam disponíveis para o Claude Code invocar sozinho quando
relevante (ex.: ao criar um componente novo, ele reconhece que
`react-view-component-pattern` se aplica) ou por pedido explícito do dev
("segue o padrão da skill de formulário aqui"). Os comandos (abaixo) são
ação pontual — rode quando for bootstrapar um projeto novo.

## Comandos incluídos

| Claude Code | Codex | O que faz |
|---|---|---|
| `/dev-patterns:scaffold-backend <nome>` | `$dev-patterns:dev-patterns-scaffold-backend <nome>` | Esqueleto de projeto backend Python — **uv** (não pip/requirements.txt), `pyproject.toml`/ruff, pre-commit, Dockerfile, CI, container de DI vazio |
| `/dev-patterns:scaffold-frontend <nome>` | `$dev-patterns:dev-patterns-scaffold-frontend <nome>` | Esqueleto de projeto frontend React/TS — **yarn** via Corepack (não npm), Vite+Vitest, Redux, eslint, CI |
| `/dev-patterns:scaffold-terraform <nome>` | `$dev-patterns:dev-patterns-scaffold-terraform <nome>` | Esqueleto de módulo Terraform (state remoto por ambiente, Makefile, gate estático de CI) |

Todos os três geram só esqueleto — pastas e configuração funcional, sem
nenhum código de domínio/exemplo. O primeiro módulo real do projeto é
quem aplica as skills de padrão acima.

**Gerenciador de pacote, padronizado e cruzado contra projetos reais**:
backend usa `uv` (lockfile de verdade, mais rápido que pip); frontend
usa `yarn` via Corepack (mesma escolha do projeto que originou as skills
de frontend). Nenhum dos dois foi escolha arbitrária do scaffold.

`scaffold-backend`/`scaffold-frontend` já preenchem `test_command`/
`lint_command`/`base_branch` do `CLAUDE.md` com o valor real (não
placeholder — este plugin já sabe qual é). Se o plugin `dev-toolkit`
também estiver instalado nesta sessão, o scaffold invoca
`/dev-toolkit:setup` sozinho pra completar `jira_projects`/status do
Jira com os nomes reais do workflow, em vez de deixar placeholder — sem
criar dependência: sem `dev-toolkit` instalado, o scaffold funciona
normalmente, só com placeholder nesses dois campos.

## Skills incluídas

### Geral (qualquer stack)

| Skill | Quando se aplica |
|---|---|
| `commit-messages` | Escrever qualquer mensagem de commit |
| `code-review-conventions` | Revisar qualquer PR, antes de aplicar a skill de review específica do stack |

### Frontend

| Skill | Quando se aplica |
|---|---|
| `react-view-component-pattern` | Criar um componente ou view novo |
| `redux-domain-pattern` | Adicionar um domínio de estado Redux novo |
| `react-hook-form-pattern` | Criar um formulário, single ou multi-step |
| `frontend-tdd` | Antes de implementar qualquer componente/view/hook — teste primeiro |
| `http-client-pattern` | Adicionar uma chamada de API nova |
| `frontend-code-review-conventions` | Revisar um PR frontend |

### Backend

| Skill | Quando se aplica |
|---|---|
| `python-domain-entity-pattern` | Criar/alterar uma entidade de domínio |
| `python-domain-event-pattern` | Adicionar um evento de domínio novo |
| `python-use-case-pattern` | Adicionar um caso de uso novo |
| `python-repository-pattern` | Adicionar persistência para um agregado novo |
| `python-provider-adapter-pattern` | Integrar com um serviço/provedor externo novo |
| `python-api-endpoint-pattern` | Adicionar um endpoint ou webhook novo |
| `python-observability-datadog-pattern` | Instrumentar (ou revisar a instrumentação) de um serviço Python com Datadog |
| `backend-testing-pattern` | Escrever o teste de qualquer caso de uso/entidade/adapter |
| `backend-code-review-conventions` | Revisar um PR de backend |

### DevOps / Infra as Code (Terraform)

| Skill | Quando se aplica |
|---|---|
| `terraform-project-pattern` | Criar/estruturar infraestrutura Terraform de um serviço |
| `terraform-security-pattern` | Desenhar acesso de CI à AWS, permissão de serviço/função, ou segredo |
| `terraform-datadog-lambda-pattern` | Provisionar ou alterar uma Lambda que precisa de trace/log no Datadog |

## Por que autossuficiente

A primeira versão dessas skills foi pensada para um registro central
com MCP, mas isso significa depender de um servidor disponível para
instalar/consumir. Este plugin existe pra não precisar disso: o conteúdo
mora dentro do próprio plugin (`skills/<nome>/SKILL.md`), versionado
junto com ele — instalar o plugin já traz tudo.

## Versionamento

Cada skill tem sua própria versão (SemVer) e `CHANGELOG.md` na pasta —
independente da versão do plugin como um todo (`plugin.json`/
`marketplace.json`), que sobe quando uma skill é adicionada/removida ou
quando várias mudam junto numa mesma release do plugin.

## Adicionar uma skill nova (geral ou de um stack novo)

Crie `skills/<nome-da-skill>/SKILL.md` (frontmatter `name`, `description`,
e versão em `metadata.version`) + `CHANGELOG.md`, seguindo o formato das skills acima.
Nada mais precisa mudar — a descoberta é automática por pasta. Skill
específica de stack ganha um nome prefixado (`react-`/`python-`/...) ou
sufixado (`frontend-`/`backend-`); skill geral não precisa de prefixo.

## Sobre as skills gerais

`commit-messages` e `code-review-conventions` foram mineradas do
registro canônico de convenções do time — ele é só a fonte de
referência aqui, nunca uma dependência: nada neste plugin fala com esse
registro nem com o MCP dele. O conteúdo original de lá continua
existindo e intocado; isto aqui é uma cópia adaptada e autossuficiente,
não uma migração.

## O que ainda falta (dimensão DevOps)

Infra as Code com Terraform está coberta (seção acima). Lint/pre-commit/
Dockerfile/CI de aplicação agora vêm de graça em projeto **novo**, como
parte dos comandos de scaffold. O que ainda falta: um jeito de
**retrofitar** isso num repositório **já existente** que não tem —
`/setup-lint`, `/setup-dockerfile`, `/setup-ci` isolados, para rodar num
projeto que já tem código, sem recriar a estrutura inteira. Ainda não
construído; equivalente de frontend continua fora de escopo por exigir
tocar no CI/husky real de um projeto que já existe (decisão diferente de
"criar do zero", que os comandos de scaffold já cobrem).
