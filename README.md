# agent-plugins

Marketplace de plugins para **Claude Code e Codex**, cobrindo o ciclo de
desenvolvimento com agentes — da quebra do épico em PBIs ao Pull Request
validado: [BrunoSilvestre00/agent-plugins](https://github.com/BrunoSilvestre00/agent-plugins).

> **Versão pública.** Estes plugins nasceram do fluxo real de um time de
> engenharia; nomes de projetos internos e dados de negócio foram
> genericizados. As fases e os gates do processo foram preservados.

## Plugins

| Plugin | O que faz |
|---|---|
| [`pbi-toolkit`](plugins/pbi-toolkit/README.md) | Refina épicos em PBIs, grava os artefatos no repositório e cria as issues no Jira via MCP oficial da Atlassian. |
| [`dev-toolkit`](plugins/dev-toolkit/README.md) | Refina backlog, avalia arquitetura, decompõe e implementa tasks em worktrees, exige revisão independente, abre PRs e acompanha o CI antes de mover o PBI para Testes. Inclui diagrama e revisão retroativa. |
| [`dev-patterns`](plugins/dev-patterns/README.md) | Convenções de código, testes, revisão, infraestrutura e observabilidade para frontend, backend e Terraform/AWS, além de scaffolds por stack. |

Instale apenas os plugins necessários. `dev-patterns` não depende de serviços
externos. Os fluxos com Jira precisam da conexão MCP oficial da Atlassian;
GitHub/PRs precisam do GitHub CLI autenticado. Spec Kit e diagramas AWS são
integrações opcionais, usadas somente quando disponíveis no ambiente.

## Instalação

### Claude Code

Com o Claude Code instalado e autenticado:

Manifestos e carregamento local dos componentes validados com Claude Code
**2.1.311**.

```bash
claude plugin marketplace add BrunoSilvestre00/agent-plugins

# Instale somente os plugins necessários
claude plugin install pbi-toolkit@ai-plugins
claude plugin install dev-toolkit@ai-plugins
claude plugin install dev-patterns@ai-plugins
```

Os comandos existentes continuam disponíveis, como `/pbi-toolkit:quebrar-epico`
e `/dev-toolkit:work-task`. Eles encaminham para os mesmos procedimentos
usados pelas skills do Codex. Reinicie a sessão após instalar/atualizar.

Para atualizar o catálogo, rode `/plugin marketplace update ai-plugins`
no Claude Code e atualize os plugins pelo gerenciador de plugins.

### Codex

Use uma versão do Codex CLI com `codex plugin add` e
`codex plugin marketplace` disponíveis (instalação local validada com
**Codex CLI 0.163.0**). Com o Codex instalado e autenticado:

```bash
codex plugin marketplace add BrunoSilvestre00/agent-plugins

# Instale somente os plugins necessários
codex plugin add pbi-toolkit@ai-plugins
codex plugin add dev-toolkit@ai-plugins
codex plugin add dev-patterns@ai-plugins

# Confira os plugins do marketplace
codex plugin list --marketplace ai-plugins
```

Inicie uma nova conversa após instalar/atualizar. No Codex interativo,
use `$nome-da-skill` com os argumentos como texto; `/plugins` abre o
gerenciador de plugins. As chamadas com `$` abaixo são mensagens para o
agente, não comandos para executar no terminal.

O Codex acrescenta o namespace do plugin ao nome declarado pela skill.
Por isso a chamada completa é, por exemplo,
`$dev-toolkit:dev-toolkit-work-task PROJ-123`, conforme a tabela abaixo.

Para atualizar o catálogo após uma nova versão:

```bash
codex plugin marketplace upgrade ai-plugins
```

Depois atualize/reinstale os plugins desejados pelo gerenciador ou por
`codex plugin add <plugin>@ai-plugins` e abra uma nova conversa.

Para testar uma cópia local antes de publicar, registre o diretório clonado
com `codex plugin marketplace add /caminho/agent-plugins` no lugar do endereço
GitHub. Ambos os catálogos usam o identificador `ai-plugins`.

Os formatos dos manifestos e do catálogo seguem a
[documentação oficial de plugins](https://developers.openai.com/plugins/build/plugins).

## Uso nos dois agentes

| Ação | Claude Code | Codex |
|---|---|---|
| Configurar refinamento | `/pbi-toolkit:setup PROJ` | `$pbi-toolkit:pbi-toolkit-setup PROJ` |
| Quebrar épico em PBIs | `/pbi-toolkit:quebrar-epico PROJ-123` | `$pbi-toolkit:pbi-toolkit-quebrar-epico PROJ-123` |
| Registrar lições do refinamento | `/pbi-toolkit:compound` | `$pbi-toolkit:pbi-toolkit-compound` |
| Configurar desenvolvimento | `/dev-toolkit:setup PROJ` | `$dev-toolkit:dev-toolkit-setup PROJ` |
| Listar PBIs prontos | `/dev-toolkit:tasks PROJ` | `$dev-toolkit:dev-toolkit-tasks PROJ` |
| Refinar tecnicamente | `/dev-toolkit:refine PROJ-123` | `$dev-toolkit:dev-toolkit-refine PROJ-123` |
| Gerar diagrama | `/dev-toolkit:diagram PROJ-123` | `$dev-toolkit:dev-toolkit-diagram PROJ-123` |
| Preparar worktree | `/dev-toolkit:worktree PROJ-123` | `$dev-toolkit:dev-toolkit-worktree PROJ-123` |
| Desenvolver PBI | `/dev-toolkit:work-task PROJ-123` | `$dev-toolkit:dev-toolkit-work-task PROJ-123` |
| Consultar pendências | `/dev-toolkit:triage PROJ` | `$dev-toolkit:dev-toolkit-triage PROJ` |
| Revisar arquitetura retroativamente | `/dev-toolkit:review PROJ-123` | `$dev-toolkit:dev-toolkit-review PROJ-123` |
| Registrar lições de desenvolvimento | `/dev-toolkit:compound PROJ-123` | `$dev-toolkit:dev-toolkit-compound PROJ-123` |
| Scaffold frontend | `/dev-patterns:scaffold-frontend meu-app` | `$dev-patterns:dev-patterns-scaffold-frontend meu-app` |
| Scaffold backend | `/dev-patterns:scaffold-backend meu-servico` | `$dev-patterns:dev-patterns-scaffold-backend meu-servico` |
| Scaffold Terraform | `/dev-patterns:scaffold-terraform minha-infra` | `$dev-patterns:dev-patterns-scaffold-terraform minha-infra` |

As skills de convenção existentes, como `backend-testing-pattern`, mantêm
os nomes e podem ser selecionadas automaticamente pelo agente.

### Configuração do projeto

Execute `setup` dentro do repositório consumidor. Em projetos novos, ele
grava a configuração em **AGENTS.md no Codex** e **CLAUDE.md no Claude Code**.
Se um desses arquivos já tiver `## Dev Flow Config` ou `## PBI Config`, ambos
os agentes reutilizam essa seção. Não é preciso duplicar a configuração;
se houver valores divergentes nos dois arquivos, o fluxo pede a resolução
do conflito antes de continuar.

Exemplos: [AGENTS.md](examples/AGENTS.md.example) e
[CLAUDE.md](examples/CLAUDE.md.example). As instruções usam `ARQUIVO_CONFIG`
como marcador para o arquivo escolhido; ele nunca deve virar um nome literal.

### Jira e agentes especializados

`pbi-toolkit` e `dev-toolkit` incluem o MCP oficial da Atlassian em
`.mcp.json`. Conecte e autentique esse servidor via OAuth no agente atual;
a instalação do pacote não prova que a conta esteja conectada. Uma conexão
oficial já disponível na sessão também pode ser usada. Sem Jira, o
`pbi-toolkit` pode gerar os artefatos locais e reportar as issues pendentes.

O ciclo do `dev-toolkit` exige **subagentes** para architect, implementer e
verifier, com revisões em contextos separados. No Claude Code são agentes
nativos do plugin; no Codex, o orquestrador passa os mesmos procedimentos
aos subagentes disponíveis na sessão, usando o modelo configurado no Codex.
Se a sessão não disponibilizar delegação, o fluxo para no gate correspondente,
sem substituir revisão independente por autorrevisão.

As versões atuais do Codex habilitam subagentes por padrão. Se a sua
configuração os desabilitou, confira `agents.enabled` no `config.toml`;
`/subagents` mostra as threads no CLI. Consulte a
[documentação de subagentes](https://developers.openai.com/codex/subagents).

As worktrees são criadas explicitamente pelo fluxo. Diretórios irmãos podem
exigir permissão adicional da sandbox. `/loop` é um recurso do Claude Code;
no Codex, execute triage sob demanda ou use um agendador já configurado.

## Estrutura e manutenção

```text
agent-plugins/
├── .claude-plugin/marketplace.json   # catálogo do Claude Code
├── .agents/plugins/marketplace.json  # catálogo do Codex
├── plugins/<plugin>/
│   ├── .claude-plugin/plugin.json    # manifesto do Claude Code
│   ├── .codex-plugin/plugin.json     # manifesto do Codex
│   ├── commands/                    # atalhos legados do Claude Code
│   ├── skills/                      # entradas compartilhadas e convenções
│   │   └── <skill>/references/       # procedimentos completos
│   └── references/                  # runtime, configuração e papéis
├── examples/                        # AGENTS.md e CLAUDE.md
└── scripts/validate_plugins.py
```

Mantenha as regras de negócio nos procedimentos das skills. Os atalhos em
`commands/` e `agents/` devem encaminhar para esses arquivos, para que os
dois agentes executem as mesmas fases e gates. Cada plugin contém seus
próprios recursos e pode ser instalado isoladamente.

Validação estrutural (Python 3.10+; sem dependências externas):

```bash
python scripts/validate_plugins.py
```

Teste de instalação, listagem, cache e descoberta das skills no runtime do
Codex CLI, com `CODEX_HOME` temporário
e sem alterar a configuração pessoal:

```bash
python scripts/validate_plugins.py --codex
```

Validação dos manifestos pelo Claude Code e conferência do inventário real
de skills, comandos, agentes e MCPs, sem instalar os plugins nem iniciar
uma conversa:

```bash
python scripts/validate_plugins.py --claude
```

Também é possível executar os dois checks com `--codex --claude`. O
validador do Claude pode emitir avisos de publicação sobre ícone e URL de
privacidade; eles não impedem o carregamento local dos plugins.

Esses checks validam os pacotes e as referências. OAuth/Jira, criação de PRs,
CI e o ciclo completo com subagentes precisam ser exercitados em um projeto
de teste autenticado; não são executados por esse script.

## Versionamento

Semântico, por plugin, sincronizado nos dois manifestos e no catálogo do
Claude Code. Mudanças de comportamento e novas skills = minor; correções =
patch; mudanças que exigem reconfiguração dos consumidores = major.
