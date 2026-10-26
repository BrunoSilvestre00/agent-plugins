# ai-plugins

Marketplace de plugins do Claude Code para um ciclo de desenvolvimento
com agentes — da quebra do épico em PBIs até o Pull Request validado
(`BrunoSilvestre00/ai-plugins-public`).

> **Versão pública.** Estes plugins nasceram do fluxo real de um time de
> engenharia; esta é a versão publicável, com nomes de projetos internos
> e dados de negócio genericizados. O processo, as fases e os gates são
> os mesmos que o time usa no dia a dia.

Cada plugin é
autossuficiente — instala e usa, sem depender de nenhum servidor externo
(os únicos que precisam de um serviço fora do plugin são o `dev-toolkit`
e o `pbi-toolkit`, que falam com o Jira via MCP; isso é o próprio
propósito deles, não uma dependência de infraestrutura extra).

## Plugins

| Plugin | O que é |
|---|---|
| [`pbi-toolkit`](plugins/pbi-toolkit/README.md) | PO quebra um épico em PBIs: grava um `.md` por PBI no repo (insumo do Spec Kit) e cria as issues no Jira via MCP da Atlassian |
| [`dev-toolkit`](plugins/dev-toolkit/README.md) | Ciclo de dev automatizado: refinamento técnico do backlog (`refine`, opcional) → PBI pronto no Jira → avaliação de arquitetura contra um checklist completo de infra (`architect`) → decomposição em tasks → implementação isolada (`implementer`/`verifier`) → revisão final de arquitetura (`architect`) → UM PR por PBI → Testes. Também tem comandos isolados sob demanda: diagrama de arquitetura (`diagram`) e auditoria retroativa de arquitetura pra PBI já em teste/concluído (`review`) |
| [`dev-patterns`](plugins/dev-patterns/README.md) | Skills de convenção de código e infra do time — gerais, frontend (React/TS/Redux), backend (Python/Clean Architecture) e DevOps/IaC (Terraform) — mais comandos de scaffold inicial por stack — instala e as convenções ficam disponíveis para o Claude Code usar sozinho |

Instale só o que precisar: o PO de um projeto pode querer só o
`pbi-toolkit`; um repositório frontend puro pode querer só o
`dev-patterns`; um repositório que segue o ciclo de dev do time no Jira
quer o `dev-toolkit`. `pbi-toolkit` e `dev-toolkit` compartilham a mesma
seção `## Dev Flow Config` no `CLAUDE.md` do projeto quando os dois estão
instalados juntos (ver README de cada um).

## Instalação

```bash
# 1. Adicionar o marketplace (uma vez por dev)
claude plugin marketplace add BrunoSilvestre00/ai-plugins-public

# 2. Instalar o(s) plugin(s) que precisar
claude plugin install pbi-toolkit@ai-plugins
claude plugin install dev-toolkit@ai-plugins
claude plugin install dev-patterns@ai-plugins
```

Atualizações: basta o time dar push neste repo e cada dev rodar
`/plugin marketplace update ai-plugins` (ou reinstalar o plugin).

## Estrutura

```
ai-plugins/
├── .claude-plugin/
│   └── marketplace.json          # catálogo do marketplace do time
├── plugins/
│   ├── pbi-toolkit/                # ver README próprio
│   ├── dev-toolkit/                # ver README próprio
│   └── dev-patterns/              # ver README próprio
└── examples/
    └── CLAUDE.md.example         # config por projeto, compartilhada por pbi-toolkit e dev-toolkit
```

## Versionamento

Semântico, por plugin, em `plugin.json` e refletido no `marketplace.json`.
Mudanças de comportamento (fases/gates do ciclo, skill nova/removida) =
minor. Correções de texto = patch. Mudanças que exigem reconfigurar os
repositórios consumidores = major, com aviso no PR. Detalhes específicos de
cada plugin (e, no caso do `dev-patterns`, de cada skill) ficam no README
de cada um.
# agent-plugins
