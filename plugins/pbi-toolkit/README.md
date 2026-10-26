# pbi-toolkit

Plugin de Claude Code do time para refinamento padronizado: o PO roda
**dentro do repositório do projeto**, e o plugin transforma um épico em
PBIs — gravando um artefato `.md` por PBI no repo (insumo direto do Spec
Kit) e criando as issues no Jira via MCP da Atlassian. Sem copy-paste em
nenhuma etapa.

## Fluxo do time

```
PO (Claude Code no repo do projeto)            Dev (Claude Code no mesmo repo)
──────────────────────────────────             ────────────────────────────────
/pbi-toolkit:quebrar-epico PROJ-123
  ├─ entrevista de refinamento (1 pergunta por vez)
  ├─ proposta de fatiamento ► aprovação do PO
  ├─ grava docs/pbis/<epico>/NN-<pbi>.md
  └─ cria Histórias no Jira vinculadas          /speckit.specify Implemente o PBI
     ao épico (com confirmação), cada           descrito em docs/pbis/<epico>/NN-<pbi>.md
     card apontando para o artefato               ├─ /speckit.clarify (se houver [NEEDS CLARIFICATION])
                                                  ├─ /speckit.plan
                                                  ├─ /speckit.tasks
                                                  └─ /speckit.implement
```

Épico já decomposto antes? Rodar `/pbi-toolkit:quebrar-epico` de novo com
a mesma chave entra em modo incremental em vez de repetir o fluxo acima
do zero — ver "Adicionar um PBI a um épico já decomposto" mais abaixo.

## Instalação

```bash
# 1. Adicionar o marketplace (uma vez por dev — mesmo passo do dev-toolkit/dev-patterns)
claude plugin marketplace add BrunoSilvestre00/agent-plugins

# 2. Instalar o plugin
claude plugin install pbi-toolkit@ai-plugins
```

Para o time inteiro sem passo manual, adicione ao `.claude/settings.json`
dos repositórios de projeto:

```json
{
  "extraKnownMarketplaces": {
    "ai-plugins": { "source": { "source": "github", "repo": "BrunoSilvestre00/agent-plugins" } }
  },
  "enabledPlugins": { "pbi-toolkit@ai-plugins": true }
}
```

### Pré-requisitos no repositório do projeto

- **Spec Kit** inicializado (`specify init`), com a constitution do time preenchida — é ela que carrega os padrões técnicos. Usamos o core oficial do GitHub; extensões só com `verified: true` no catálogo oficial (`specify extension search --verified`) **e** aprovação do time (shortlist atual em avaliação: CI Guard, Architecture Guard).
- **Plugin oficial da Atlassian** instalado (criação das issues): `/plugin install atlassian@claude-plugins-official` (autentica via OAuth, respeitando as permissões da sua conta). Sem ele, o plugin gera os artefatos no repo e avisa que as issues não puderam ser criadas.

### Opcionais aprovados

- **product-management** (Anthropic) — para o discovery/escrita do épico, antes deste plugin: `claude plugin marketplace add anthropics/knowledge-work-plugins` e depois `claude plugin install product-management@knowledge-work-plugins`.
- **grill-me** (Matt Pocock) — entrevista de stress-test complementar ao refinamento. Instalar **somente do repositório original** (`mattpocock/skills`), nunca de forks ou wrappers de terceiros.

## Política de ferramentas do time

Somente as ferramentas acima são aprovadas. **Não instale skills, plugins, agents ou CLIs de terceiros** (marketplaces da comunidade, forks do grill-me, skills de PRD/user story avulsas, CLIs de Jira que pedem API token, extensões do Spec Kit) sem revisão do time: uma skill é instrução que o agente executa com acesso ao repositório e ao Jira — trate como dependência de código. Propostas de novas ferramentas passam por leitura completa do SKILL.md/scripts e aprovação do time antes de entrar nesta lista.

## Escolhendo o projeto/board de destino

Issues do Jira vivem em **projetos**; o board é um filtro que as exibe. O destino é definido **por repositório**, no `CLAUDE.md`. Config mínima (autossuficiente — este plugin não depende de nenhum outro):

```markdown
## PBI Config

- jira_projects: PROJ            # vários boards no mesmo repo: PLAT, MOB, PAY
- status_ready: Ready for Dev    # opcional: PBI aprovado na DoR é movido para cá
- issue_type_pbi: História
- issue_type_epico: Épico
```

Com a seção presente, o plugin cria direto no projeto configurado (só confirmando o resumo); com várias chaves, pergunta em qual projeto o épico vive. Sem a seção, pergunta na primeira execução e oferece criá-la. Indicar outro destino na conversa sempre prevalece. `.pbi-toolkit.json` segue aceito como legado.

## Convivência com o `dev-toolkit` (opcional)

Quando o repo também usa o plugin `dev-toolkit` (deste mesmo marketplace), os dois compartilham UMA seção: use `## Dev Flow Config` com as chaves de ambos (este plugin lê dela `jira_projects`, `status_ready` e `issue_type_*`, ignorando o resto). O encaixe natural: issues nascem **sem assignee** e o PBI aprovado na DoR vai para `status_ready` — exatamente o filtro do `/dev-toolkit:tasks`, e o que o `/dev-toolkit:refine` avalia tecnicamente (arquitetura, histórico do time) antes de qualquer dev puxar o card. Mas nada aqui exige o `dev-toolkit`: sem ele, o PBI completo no Jira serve a qualquer fluxo de desenvolvimento (dev direto, Spec Kit, outro toolkit).

## Uso

```
/pbi-toolkit:setup PROJ            # 1x por repositório: CLAUDE.md (Dev Flow Config) + docs/
/pbi-toolkit:quebrar-epico PROJ-123
/pbi-toolkit:quebrar-epico "Permitir pagamento via PIX no checkout"
/pbi-toolkit:quebrar-epico docs/prd/pix.md
/pbi-toolkit:quebrar-epico PROJ-123   # épico já decomposto? entra em modo incremental sozinho
/pbi-toolkit:compound            # ao fim do épico: grava 1-3 lições em docs/knowledge/
```

Ou em linguagem natural: "quebra esse épico em PBIs", "gera os PBIs disso e cria no Jira".

O plugin sempre pede confirmação antes de criar qualquer issue no Jira e não commita os artefatos sem você pedir.

### Adicionar um PBI a um épico já decomposto

Rode `/pbi-toolkit:quebrar-epico <mesma chave>` de novo — o plugin detecta que `docs/pbis/<epico>/README.md` já existe e entra em **modo incremental**: não repete a entrevista completa (lê o resumo já registrado), pergunta só o que motivou o PBI novo, continua a numeração `NN` de onde parou, e atualiza (nunca recria) o `README.md` do épico. Se o épico já estiver no teto de 6–8 PBIs (`references/regras-fatiamento.md`), o plugin avisa que a iniciativa provavelmente cresceu além do épico original, em vez de simplesmente empilhar mais um PBI.

Motivo comum pra esse caso: o time de dev (via `dev-toolkit`) descobriu, numa avaliação de arquitetura ou revisão final, que o escopo era maior que uma task — o `architect` sinaliza isso e recomenda rodar este comando. Outro motivo igualmente comum: o próprio PO, numa revisão manual, percebe que um PBI já avançado (às vezes já em teste, tarde demais para emendar o artefato original) tratou uma decisão de negócio de forma ilustrativa em vez de exaustiva — ex.: o contrato de campos de uma entidade (ver "Contrato de campos de uma entidade capturada" abaixo). Em qualquer um dos dois casos, o modo incremental oferece registrar a descoberta como lição (ver Compounding abaixo) na hora, sem esperar o fim do épico.

### Contrato de campos de uma entidade capturada

Quando um PBI captura/persiste uma entidade (tipicamente o PBI de caminho mínimo/walking skeleton que a introduz), a seção "Regras de negócio" do `references/template-pbi.md` exige o contrato de campos **completo**, não só exemplos — cada campo da entidade, com obrigatório ou opcional decidido explicitamente. `references/dor.md` tem o item correspondente na Definition of Ready, bloqueando um PBI de sair de refinamento com "dados obrigatórios (título, empresa, X)" como lista ilustrativa em vez de exaustiva — esse tipo de lacuna só costuma aparecer depois, numa revisão manual ou retroativa, quando já é tarde para emendar o PBI original (nesse caso, vira PBI incremental novo, não uma edição no PBI já avançado — ver acima).

### Dados como dimensão própria do checklist

O passo 1 do fluxo (`references/checklist-epico.md`) tem um item dedicado a dados: se o épico cria/acumula um ativo de dados, qualidade/validação, retenção/expiração, e medição/relatório da métrica-alvo do épico são consideradas explicitamente — nunca deixadas cair em "fora de escopo" sem dono. `references/regras-fatiamento.md` tem o padrão de corte correspondente ("por ciclo de vida do dado"): cada sub-dimensão só vira PBI próprio se aplicável a este épico (senão absorve na PBI de captura), respeitando o teto de 6–8 PBIs. Distinção clara do anti-padrão "PBI de camada técnica": não é "criar a tabela X" nem "expor a métrica num endpoint", é o comportamento observável que o dado precisa ter (dado ruim é filtrado, dado velho expira, alguém toma uma decisão a partir da métrica).

## Compounding (lições aprendidas)

Cada ciclo pode terminar com `/pbi-toolkit:compound`: o plugin extrai 1–3 lições (PBIs que voltaram, fatiamentos que erraram o tamanho, dependências que surpreenderam, escopo descoberto tarde pelo dev que o corte original não previa) e grava em `docs/knowledge/` como markdown versionado com frontmatter pesquisável. No refinamento seguinte, o passo 1 consulta essa pasta antes de entrevistar — lição registrada vira resposta-padrão a confirmar, não pergunta repetida. Formato e regras em `references/licoes.md`.

`docs/knowledge/` é a mesma pasta que o `/dev-toolkit:refine` lê (se o repo também usar o `dev-toolkit`) — uma lição registrada aqui pelo PO também informa o lado do dev, e uma descoberta do dev que virou PBI incremental também informa o próximo refinamento do PO. Uma base de conhecimento só, os dois lados se beneficiam.

## Estrutura

```
plugins/pbi-toolkit/
├── .claude-plugin/plugin.json
├── commands/
│   ├── setup.md                  # /pbi-toolkit:setup (provisiona o repo)
│   ├── quebrar-epico.md          # /pbi-toolkit:quebrar-epico
│   └── compound.md               # /pbi-toolkit:compound (lições aprendidas)
└── skills/epico-para-pbi/
    ├── SKILL.md                  # fluxo principal
    └── references/
        ├── checklist-epico.md    # o que precisa estar claro no épico (9 itens, incl. dados)
        ├── regras-fatiamento.md  # como cortar (incl. ciclo de vida do dado) e anti-padrões
        ├── template-pbi.md       # corpo do artefato/issue (RN exige contrato de campos completo)
        ├── handoff-speckit.md    # formato do .md e contrato com o Spec Kit
        ├── licoes.md             # formato das lições em docs/knowledge/
        └── dor.md                # Definition of Ready (incl. contrato de campos completo)
```

## Manutenção e versionamento

Os arquivos em `references/` são o contrato do time — mudou o processo, edite, **incremente `version` no `plugin.json` e no `marketplace.json`** (raiz do repo) e faça push. O time atualiza com `/plugin marketplace update ai-plugins` (ou automaticamente, conforme configuração). A Definition of Done técnica vive na constitution do Spec Kit em cada projeto, para não haver duas fontes de verdade.
