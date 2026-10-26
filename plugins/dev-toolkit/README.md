# dev-toolkit

Plugin do Claude Code que automatiza o ciclo de **desenvolvimento** do time
a partir de um PBI já pronto no Jira:

**PBI pronto (Jira) → Visão de implementação do dev → Avaliação de
arquitetura → Decomposição em tasks → Implementação isolada → Revisão
final de arquitetura → PR `feat/{PBI-ID}` → CI verde → Testes**

A escrita do épico e do PBI (spec, critérios de aceite) é responsabilidade
do PO e é tratada por **outro toolkit**, de forma isolada deste — este
plugin só entra quando o PBI já está pronto para dev. O dev escolhe quais
PBIs trabalhar — inclusive vários em paralelo — e o agente executa o
ciclo completo de cada um: lê o PBI, pergunta ao dev (antes de propor
qualquer abordagem) se ele quer descrever como enxerga a execução em alto
nível ou prefere decidir sozinho, avalia se o PBI (sozinho ou em
composição com o épico) exige uma decisão de arquitetura nova antes de
prosseguir — infra, integrações externas, padrões do projeto, e uma
checklist de dependências que não pode ficar com nada em aberto (agent
`architect`, escopo pré-decomposição, avaliando a visão do dev quando
houver) —, decompõe o PBI em tasks,
implementa e verifica cada task isoladamente (agentes
`implementer`/`verifier`), e, com tudo pronto, roda o `architect` de novo
— agora em escopo de revisão final, confrontando o diff real com a
decisão tomada no início e com os padrões do projeto, não só com o
critério de aceite. Só então abre o PR no padrão do time — nunca um por
task, sempre por repositório tocado (um só, ou dois — stage e main
draft — se o repositório usar esse fluxo) — e move o card para Testes.
O card **nunca** vai
para Done automaticamente: revisão e merge continuam sendo humanos.

Um PBI pequeno vira 1 task; um PBI grande vira várias — o processo é
sempre o mesmo, o padrão de qualidade não muda com o tamanho.

## Comandos

| Comando | O que faz |
|---|---|
| `/dev-toolkit:setup [projeto]` | 1x por repositório: provisiona o `CLAUDE.md` (Dev Flow Config), detectando test/lint/branch e consultando os status reais do Jira |
| `/dev-toolkit:tasks [projeto] [filtro]` | Lista os PBIs prontos para dev nos boards do repo (somente leitura) |
| `/dev-toolkit:refine [ID]` | Refinamento técnico do backlog em `status_ready`, antes do pickup: clareza do PBI, histórico do time (`docs/knowledge/`), avaliação de arquitetura (`architect`), diagrama (`/dev-toolkit:diagram`, se aplicável), e aponta pro Spec Kit se o repo usar. Sem argumento, roda sobre todo o backlog pronto |
| `/dev-toolkit:diagram [PBI/épico]` | Gera ou atualiza o diagrama de arquitetura (`.drawio`, ícones oficiais AWS4) via skill `aws-architecture-diagram` — prioriza analisar a IaC real do repositório, cai para descrever a partir do ADR quando ainda não há infra criada. Comando isolado, chamável direto ou a partir do `refine`/`work-task` |
| `/dev-toolkit:worktree <ID>` | **Opcional** — o `work-task` já isola cada PBI numa worktree sozinho (Fase 0); use este comando só se quiser preparar o ambiente com antecedência, sem começar o ciclo agora |
| `/dev-toolkit:work-task <ID>` | Executa o ciclo completo: lê o PBI, pergunta a visão de implementação do dev (ou segue sozinho, se ele preferir), assume o card, decompõe o PBI em tasks, implementa/verifica cada task isolada, roda a verificação agregada, faz a revisão final de arquitetura, abre **um PR por repositório tocado** (`feat/{ID}` — dois PRs, stage + main draft com tag, se `stage_branch` estiver configurado), espera o CI real ficar verde nos dois, promove o de main quando o de stage mergear, e só então move para Testes |
| `/dev-toolkit:triage [projeto]` | Somente leitura: lista PBIs/PRs que precisam de atenção humana (CI vermelho, ADR pendente, PBI parado). Pensado pra rodar via `/loop`, não faz parte do ciclo normal |
| `/dev-toolkit:review <PBI/épico>` | Revisão retroativa de arquitetura — mesma lógica da revisão final (Fase 9), mas roda em PBI/épico já em `status_testing` ou já concluído, fora de qualquer sessão ativa de `work-task`. Reconstrói o que foi implementado via branch ou histórico de commits, e oferece refletir o achado no board e gerar lição pro compound |
| `/dev-toolkit:compound [PBI]` | Extrai 1-3 lições aprendidas dos ciclos recentes (bloqueio recorrente, retrabalho) e grava em `docs/knowledge/` — mesma pasta do `pbi-toolkit` |

Três agentes especializados, invocados pelos comandos acima (não só pelo
`work-task`):

- **`architect`** — age em dois momentos do ciclo, invocado pelo `work-task` (Fase 3/Fase 9), pelo `refine` (pré-decomposição em batch) e pelo `review` (revisão final retroativa). Antes de qualquer task existir (escopo pré-decomposição), avalia infraestrutura como um **checklist**, não uma pergunta única — onde/como executa (serverless vs. container, com o trade-off de custo/cold start/duração), gatilho (sob demanda, agendado, evento), banco, cache, fila, evento/barramento, armazenamento de objeto/log, observability (com `dev-patterns` instalado, checa contra `python-observability-datadog-pattern`/`terraform-datadog-lambda-pattern` quando o repositório já usa Datadog), rede, segredo/criptografia — além de integrações externas (incluindo qual codebase já existente deveria hospedar uma capacidade nova, quando mais de um é candidato), padrões do projeto e composição com os PBIs irmãos do épico. Lista toda dependência identificada num checklist que não pode ficar com item "em aberto" — mas nem toda dependência de infra é bloqueio: criar um recurso seguindo um padrão já existente (`terraform-project-pattern`/`terraform-security-pattern`) vira task normal na decomposição, é trabalho do próprio ciclo; só bloqueia o que exige decisão de negócio, credencial nova, ou aprovação de outro time. Depois de tudo implementado (escopo revisão final), confronta o diff real (ou o histórico de commits, se rodado retroativamente pelo `review`) com a decisão tomada e com os padrões do repositório — não só se bateu o critério de aceite, mas se é a melhor estrutura disponível, e também relê o checklist de infra/codebase contra o próprio PBI (não só contra o que foi decidido antes) pra pegar categoria que nunca teve resposta, tipo gatilho de execução nunca decidido. Se qualquer dos dois momentos revelar escopo grande demais pra ser task ou ajuste de arquitetura pontual, sinaliza que aquilo pode precisar virar um PBI novo — quem decide e roda `/pbi-toolkit:quebrar-epico` (modo incremental, se o time também usar o `pbi-toolkit`) é o humano. Em nenhum dos dois momentos decide sozinho: propõe (rascunho de ADR, ou o desvio encontrado) e para o ciclo até um humano confirmar ou ajustar.
- **`implementer`** — implementa uma task em disciplina TDD red/green, numa worktree isolada.
- **`verifier`** — revisor adversarial; roda lint/test/type reais e nunca aceita alegação sem saída de comando. Age duas vezes: depois de cada task, e uma vez ao final contra todos os critérios de aceite do PBI consolidado. Com `dev-patterns` instalado, consulta explicitamente as skills de revisão do stack (`backend-code-review-conventions`/`frontend-code-review-conventions` + a geral) como parte do veredito, não como lente à parte — uma violação encontrada por elas pesa igual a qualquer outro problema e pode reprovar.

## Pré-requisitos (por dev, uma vez)

1. **Claude Code** instalado (`npm install -g @anthropic-ai/claude-code`).
2. **GitHub CLI** autenticado: `gh auth login`.
3. **Jira**: na primeira utilização, o MCP da Atlassian (embutido no plugin)
   vai pedir autenticação OAuth no navegador. Use `/mcp` dentro do Claude
   Code para verificar/refazer a autenticação.

## Instalação

```bash
# 1. Adicionar o marketplace (uma vez por dev)
claude plugin marketplace add BrunoSilvestre00/agent-plugins

# 2. Instalar o plugin
claude plugin install dev-toolkit@ai-plugins
```

Atualizações: basta o time dar push neste repo e cada dev rodar
`/plugin marketplace update ai-plugins` (ou reinstalar o plugin).

## Configuração por projeto (uma vez por repositório)

Rode `/dev-toolkit:setup [PROJ]` — ele detecta `test_command`/
`lint_command`/`base_branch` lendo o repositório e, se as tools da
Atlassian estiverem disponíveis, consulta os status reais do workflow do
Jira em vez de você digitar (e arriscar errar) os nomes exatos. Se o
repo já rodou `/pbi-toolkit:setup` antes, ele funde na mesma seção em
vez de duplicar.

Alternativa manual: copie
[`examples/CLAUDE.md.example`](examples/CLAUDE.md.example) e ajuste:

```markdown
## Dev Flow Config

- jira_projects: PROJ
- status_ready: Ready for Dev
- status_in_progress: In Progress
- status_testing: Testing
- base_branch: main
- test_command: npm test
- lint_command: npm run lint
```

Os nomes de status devem ser **exatamente** os do workflow do Jira do
projeto. Sem essa seção, os comandos param e sugerem `/dev-toolkit:setup`
— por design: o agente nunca adivinha em qual projeto/board está
operando.

### Como o board é escolhido

O repositório define o board: o dev abre o Claude Code dentro do repo do
projeto e o plugin opera apenas nos boards listados ali. Isso elimina o
risco de mover cards do projeto errado.

**Um repo, vários boards** (monorepo / múltiplas squads): liste as chaves
em `jira_projects: PLAT, MOB, PAY`. O `/tasks` agrega todos por padrão e
aceita filtro por projeto: `/dev-toolkit:tasks PAY`. O `work-task` valida
que o prefixo do ID (ex: `PAY-142`) pertence a um dos projetos configurados
e recusa IDs de projetos de outros repositórios.

A config antiga `jira_project` (singular) continua funcionando.

### Projetos full-stack (frontend + backend)

`/dev-toolkit:setup` detecta monorepo sozinho (mais de uma pasta com seu
próprio `package.json`/`pyproject.toml`) e já gera o `stacks:` com os
comandos certos, escopados como `cd <pasta> && <comando>` — mesmo idioma
pra qualquer linguagem. Configuração manual continua possível (exemplo
comentado em [`CLAUDE.md.example`](examples/CLAUDE.md.example)): cada
stack tem seu próprio `test_command`/`lint_command` e, opcionalmente,
`repo`/`local_path` quando vive em **outro repositório** (polyrepo) —
isso o `setup` não detecta sozinho, só pergunta se você mencionar.

O `work-task` identifica sozinho, pelos critérios de aceite do PBI, quais
stacks aquele PBI toca — e só pergunta ao dev se não conseguir decidir com
confiança. Uma PBI que toca só um stack se comporta exatamente como hoje.
Uma PBI que toca vários:

- **Monorepo** (stacks sem `repo`): continua **um PR só**, cada task
  decomposta já marcada com o stack a que pertence, para usar as
  convenções/skills e o `test_command`/`lint_command` certos.
- **Polyrepo** (algum stack com `repo`): vira **um PR por repositório
  efetivamente tocado**, cada um seguindo o mesmo ciclo (decompor →
  implementar → verificar) de forma independente, cruzando os PRs entre
  si e só movendo o card para Testes quando todos estiverem abertos.

**Dois stacks da mesma tecnologia, em repositórios diferentes** (ex.:
dois frontends React+TS, um de cada produto) funcionam sem problema —
cada `stack:` tem seu próprio `name`, e o `work-task` nunca escolhe por
categoria genérica de tecnologia: se mais de um stack bate na mesma
categoria, exige que o critério de aceite indique qual `name`
especificamente, e PARA pra perguntar se não estiver claro.

**PBI que descobre, durante a avaliação de arquitetura, que precisa de
um repositório ainda não configurado** (ex.: uma tela que escreve em
APIs de dois produtos diferentes, e o `architect` decide que um endpoint
novo deveria morar no codebase de outro produto, não no atual): o
`architect` (dimensão "Integrações externas") avalia explicitamente qual
codebase deveria hospedar a capacidade nova — nunca por padrão o
repositório onde o PBI nasceu — pesando cobertura de teste, quem é dono,
risco de deploy e custo de duplicar lógica. Confirmada a escolha, a Fase
3 do `work-task` expande a lista de stacks do PBI sozinha; se esse
repositório nem existe em `stacks:` ainda, PARA e pergunta como
configurar (`repo`/`local_path`) antes de prosseguir — sem adivinhar.
Continua sem precisar o dev abrir outro terminal: a mesma sessão, uma
vez configurado o stack, opera no diretório irmão como qualquer outro
polyrepo.

## Fluxo de uso no dia a dia

```bash
# Ver o que está disponível
/dev-toolkit:tasks

# Antes do planning/refinamento, sob demanda: ver o que precisa de
# atenção técnica antes de alguém puxar
/dev-toolkit:refine

# Trabalhar UM PBI na pasta atual
/dev-toolkit:work-task PROJ-142

# Trabalhar VÁRIOS em paralelo — sem passo extra: um terminal por PBI
# Terminal 1: cd neste repo, `claude`, e:
/dev-toolkit:work-task PROJ-142
# Terminal 2: mesmo repo, outro terminal, `claude`, e:
/dev-toolkit:work-task PROJ-155

# Sob demanda, fora do ciclo principal (ver seções próprias abaixo):
/dev-toolkit:diagram PROJ-142      # visualizar uma arquitetura proposta/existente
/dev-toolkit:review PROJ-142       # auditar arquitetura de algo já em teste/concluído
```

O `work-task` isola cada PBI numa worktree dedicada sozinho, na própria
Fase 0 — não precisa rodar `/dev-toolkit:worktree` antes; só abrir um
terminal por PBI e chamar `work-task` direto em cada um.
`/dev-toolkit:worktree` continua existindo pra quem quiser só preparar o
ambiente com antecedência, sem começar o ciclo na hora (ver seção
própria abaixo).

Recomendação prática: 2–3 PBIs em paralelo por dev. Acima disso o gargalo
vira a atenção humana para revisar e responder dúvidas dos agentes.

Dentro de um único `work-task`, a decomposição em tasks e o isolamento por
task acontecem automaticamente — assim como o isolamento do PBI inteiro
(Fase 0). O dev não precisa chamar `/worktree` em nenhum dos dois casos;
ele só existe pra quem quer preparar o ambiente com antecedência.

## Visão de implementação do dev (Fase 2)

Depois de ler o PBI (Fase 1) e antes de qualquer avaliação de arquitetura
ou decomposição em tasks, o `work-task` pergunta ao dev — sem propor
nenhuma abordagem antes: você quer descrever como enxerga a execução
deste PBI em alto nível, ou prefere que o agente decida sozinho? A ordem
importa: uma sugestão do agente ali vira âncora — o dev tende só a
confirmar em vez de pensar do zero, mesmo quando discordaria se tivesse
formado a própria opinião antes de ver a do agente.

Descrever a visão é sempre opcional, decidido PBI a PBI (não é uma
configuração — nada pra lembrar de ligar/desligar de antemão). Quando o
dev descreve, ela vira insumo do `architect` na avaliação de arquitetura
(que passa a reagir a essa abordagem específica, não a uma composição
genérica) e da decomposição em tasks, que a segue em vez de inventar uma
própria. Quando o dev prefere autonomia, o ciclo segue exatamente como
antes desta fase existir.

## Fluxo de PR: stage + main (opcional, por repositório)

Repositório sem `stage_branch` configurado (`## Dev Flow Config`):
fluxo de sempre, um PR por repositório, base `{base_branch}`.

Repositório **com** `stage_branch` configurado, a Fase 10 do
`work-task` abre **dois** PRs por repositório, a partir da mesma branch
(`feat/{ID}`):

- Um PR normal contra `{stage_branch}`.
- Um PR **draft** contra `{base_branch}` (main) — fica em draft até o
  PR de stage mergear.

Os dois levam a **mesma tag de release**. O nome é confirmado com o dev
já na Fase 10 (bump de versão é decisão de produto, o agente nunca
adivinha), mas a tag em si só é **criada na Fase 12**, no commit real
que o merge do PR de stage produzir — nunca na ponta da branch de
feature antes do merge, porque squash/merge commit/rebase mudam qual
commit é esse, e tagar cedo demais deixaria a tag inalcançável do
histórico depois. A Fase 11 espera CI verde nos dois PRs (draft roda CI
igual a PR normal). A Fase 12 monitora o PR de stage e, assim que ele
mergear, cria a tag e promove o de main pra pronto (`gh pr ready`) — o
card só vai pra Testes
depois disso.

## Refinamento técnico antes do pickup (opcional)

`/dev-toolkit:refine [ID]` roda ANTES de alguém assumir o PBI — pensado
pra rodar antes de uma reunião de planning/refinamento, não no meio do
`work-task`. Complementa o refinamento de produto que o `pbi-toolkit` já
faz (DoR, `[NEEDS CLARIFICATION]`) com cinco camadas de olhar técnico:

1. **Clareza do PBI** — mesma leitura da Fase 1 do `work-task`, mas em
   modo consultivo (vira pergunta, não PARE).
2. **Histórico do time** — cruza `docs/knowledge/` (as lições do
   `compound`) com o tema do PBI, viram perguntas específicas.
3. **Avaliação de arquitetura** — mesmo `architect`/mesma lógica da
   Fase 3 do `work-task`, só que em batch sobre o backlog pronto; se o
   time confirmar a decisão ali, o `work-task` de quem pegar depois
   reconhece e pula a Fase 3 sozinho. Se o achado for grande demais pra
   task, sinaliza opção de PBI novo (`pbi-toolkit`, modo incremental).
4. **Spec Kit** (se o repositório tiver `.specify/`) — aponta pra
   `/speckit.clarify` quando fizer sentido, nunca tenta conduzir por
   conta própria (é interativo por natureza).
5. **Diagrama de arquitetura** (se houver ADR) — oferece rodar
   `/dev-toolkit:diagram`, comando isolado que trata disponibilidade da
   skill, instalação opcional e modo (IaC real vs. brainstorm) por conta
   própria.

Sem argumento, roda sobre todo o backlog em `status_ready`; mais caro que
o `/triage` (chama o `architect` por PBI), por isso pensado pra rodar sob
demanda, não em intervalo curto de `/loop`.

`refine` nunca transiciona status de PBI e nunca chama o `work-task`
sozinho; só comenta no Jira, finaliza uma decisão de arquitetura ou gera
um diagrama com confirmação explícita do usuário — e nunca instala
plugin/marketplace por conta própria — mesma disciplina do
`triage`/`compound` acima.

## Diagrama de arquitetura (opcional, comando isolado)

`/dev-toolkit:diagram [PBI/épico]` gera ou atualiza um diagrama de
arquitetura via `aws-architecture-diagram` (skill do plugin oficial
`deploy-on-aws`, marketplace `awslabs/agent-plugins` — o substituto do
extinto `aws-diagram-mcp-server` da AWS; gera XML `.drawio` com ícones
oficiais AWS4, abre direto em diagrams.net/draw.io). É um comando
isolado, não uma lógica duplicada dentro de `refine`/`work-task` — os
dois só oferecem chamá-lo (`refine` na Camada 5, `work-task` na Fase 3
ao confirmar um ADR, e opcionalmente na Fase 9 depois de criar/alterar
IaC).

Prioriza sempre a IaC real do repositório quando existir (Modo A —
escaneia CDK/CloudFormation/Terraform de verdade), caindo pra descrever
a partir do ADR (Modo B — brainstorm) só quando a infra ainda não foi
criada — por isso a Fase 9 (depois da implementação) tende a gerar um
diagrama mais fiel ao que existe do que a Fase 3/`refine` (antes de
qualquer código).

Sem a skill instalada: menciona a instalação como opção — nunca instala
por conta própria — e oferece um diagrama Mermaid como alternativa sem
dependência nenhuma (só sem os ícones da AWS). Exige Python 3.9+ e o
pacote `defusedxml`; instalar o plugin traz junto outras 2 skills e 3 MCP
servers da AWS (instalação de plugin não é a-la-carte).

## Revisão retroativa de arquitetura (opcional, comando isolado)

`/dev-toolkit:review <PBI/épico>` roda a mesma revisão final que a
Fase 9 do `work-task` já faz, mas fora do ciclo ativo — pra PBI/épico já
em `status_testing` ou já concluído, quando não houve (ou é preciso
repetir) essa verificação depois que o trabalho saiu da sessão original.
Reconstrói o que foi implementado pela branch `feat/{ID}` se ainda
existir, ou pelo histórico de commits que referenciam o PBI na mensagem
(convenção que este toolkit já usa) — nunca adivinha se não conseguir
reconstruir, pergunta.

Com desvio encontrado, oferece duas coisas que a Fase 9 comum não
precisa (o PBI ali ainda está ao vivo): **refletir no board** —
comentário na issue com o achado, e pergunta separada se o usuário
também quer transicionar o status de volta (nunca faz isso sozinho) — e
**gerar lição pro compound** (mesmo mecanismo/schema do `compound`,
mesma disciplina de nunca gravar sem confirmação). Não é um gate de uso
único: pode rodar quantas vezes fizer sentido sobre o mesmo PBI/épico.

## Triagem e lições aprendidas (opcional)

Dois comandos fora do ciclo normal, inspirados em [loop
engineering](https://addyosmani.com/blog/loop-engineering/) — achados
que o ciclo automático não resolve sozinho viram inbox humano, e o
conhecimento acumulado fica registrado em vez de se perder entre
sessões:

```bash
# Rodar sob demanda, ou periodicamente via /loop:
/loop 30m /dev-toolkit:triage    # inbox: CI vermelho, ADR pendente, PBI parado,
                                 # PBI paralelo esperando resposta

# Ao fim de um PBI ou período, sob demanda:
/dev-toolkit:compound PROJ-142
```

Trabalhando vários PBIs em paralelo (um terminal por `work-task`)? Cada
um grava um marcador leve toda vez que PARA esperando resposta, em
qualquer fase — o `triage` escaneia `git worktree list` e reporta qual
worktree está esperando você, sem precisar checar terminal por
terminal. Limitação conhecida: isso só enxerga worktrees deste
repositório — um stack polyrepo (`repo`/`local_path`, clone separado)
não aparece nessa varredura.

`triage` é somente leitura (nunca transiciona card nem mexe em PR).
`compound` grava em `docs/knowledge/` só com sua confirmação — nunca
sozinho.

## Garantias de segurança do fluxo

O comando `work-task` opera com gates explícitos e regras invioláveis:

- **Nunca propõe uma abordagem técnica antes de perguntar a visão do dev**
  (Fase 2) — quem fala primeiro é o dev, ou ele pede explicitamente pra o
  agente decidir; evita que uma sugestão do agente vire âncora e o dev só
  confirme em vez de pensar do zero.
- Para e pergunta se o PBI (ou a decomposição em tasks) for ambíguo —
  não inventa requisitos nem forma de dividir o trabalho.
- Impacto de arquitetura (infra, integrações externas, padrões do
  projeto, ou pela composição com o épico) nunca é decidido pelo agente
  — só proposto; um humano confirma ou ajusta antes de qualquer task
  existir. Nenhuma dependência pode ficar "em aberto" nessa checklist —
  mas dependência que vira task de rotina (ex.: criar recurso de infra
  seguindo padrão existente) não exige essa confirmação humana, só a que
  precisa de decisão de negócio, credencial nova, ou aprovação de outro
  time.
- **Revisão final de arquitetura, não só critério de aceite**: depois de
  tudo implementado e a verificação agregada aprovada, o `architect` roda
  de novo contra o diff real — em todo PBI, mesmo os que a avaliação
  inicial marcou "sem impacto" — pra confirmar que o resultado ficou na
  melhor estrutura disponível e que nenhuma dependência nova surgiu sem
  passar pelo mesmo crivo. Também relê o checklist de infra/codebase
  contra o que o PBI exige, não só contra o que a Fase 3 perguntou na
  época — pega omissão (categoria nunca respondida, ex.: gatilho de
  execução nunca decidido), não só adição não anunciada; especialmente
  relevante no `/dev-toolkit:review` retroativo, pra PBI implementado
  antes de alguma dimensão do checklist existir. Desvio encontrado
  também para o ciclo até decisão humana.
- O PBI inteiro roda isolado numa worktree própria (Fase 0, automática)
  — o checkout de onde a sessão começou nunca é tocado, então não
  importa se ele já tinha mudança não commitada.
- Cada task é implementada e verificada isoladamente (`implementer` +
  `verifier`, em worktree própria) antes de ser mesclada de volta na
  branch do PBI — e o `verifier` exige a prova do **RED** (teste
  falhando antes da implementação), não só do GREEN final; alegação de
  TDD sem essa prova é tratada como problema.
- Lint e a suíte **inteira** de testes precisam passar antes do PR — e
  passam de novo, na branch consolidada do PBI, na verificação agregada
  da Fase 8, mesmo que cada task já tenha passado isoladamente.
- **CI de verdade, não só local**: depois do PR aberto, a Fase 11 espera
  o CI real do PR resolver antes de mover o card — verificação local
  passando não é suficiente, CI vermelho bloqueia a transição pra
  Testing. Com `stage_branch` configurado, os dois PRs (stage e main
  draft) precisam de CI verde.
- **Tag de release, sempre confirmada** — em repositório com
  `stage_branch`, a Fase 10 nunca cria/publica a tag sem o dev
  confirmar o número exato.
- **PR de main não sai de draft sozinho** — a Fase 12 só promove
  (`gh pr ready`) depois de checar de verdade que o PR de stage
  mergeou, nunca assume.
- Cada critério de aceite do PBI precisa de teste correspondente.
- **Um PBI, um PR por repositório** (dois, se `stage_branch`) — tasks
  internas nunca abrem PR nem são mescladas direto na branch base.
- Uma decisão de arquitetura tem **uma** fonte (o comentário no épico) —
  arquivo de repo, quando existir, é sempre um ponteiro, nunca uma cópia.
- **Proteção contra corrida entre PBIs irmãos**: antes de postar uma
  decisão de arquitetura confirmada no épico, o `work-task`/`refine`
  relê os comentários mais uma vez — se outro PBI do mesmo épico já
  postou uma decisão nesse intervalo (sessão em paralelo), não posta a
  sua, para e pede pra reconciliar com o usuário.
- Nunca: merge, push force, transição para Done, reescrita de histórico.

## Estrutura

```
ai-plugins/
├── .claude-plugin/
│   └── marketplace.json          # catálogo do marketplace do time
├── plugins/dev-toolkit/
│   ├── .claude-plugin/plugin.json
│   ├── .mcp.json                 # MCP da Atlassian (OAuth no 1º uso)
│   ├── agents/
│   │   ├── architect.md          # avalia impacto (pré-decomposição) e revisão final de design, nunca decide sozinho
│   │   ├── implementer.md        # implementa 1 task, TDD, worktree isolada
│   │   └── verifier.md           # revisor adversarial (por task e do PBI)
│   └── commands/
│       ├── setup.md              # provisiona o CLAUDE.md (Dev Flow Config)
│       ├── tasks.md
│       ├── refine.md             # refinamento técnico do backlog, antes do pickup
│       ├── diagram.md            # gera/atualiza diagrama de arquitetura (.drawio, AWS4)
│       ├── worktree.md           # opcional — work-task já isola sozinho (Fase 0)
│       ├── work-task.md
│       ├── triage.md             # inbox humano (CI/ADR/PBI parado), roda via /loop
│       ├── review.md             # revisão retroativa de arquitetura (PBI/épico já em teste/concluído)
│       └── compound.md           # lições aprendidas em docs/knowledge/
└── examples/
    └── CLAUDE.md.example         # config por projeto
```

Durante um `work-task`, o comando cria `.dev-flow/{PBI-ID}/tasks.md` na
branch do PBI — é a decomposição em tasks, versionada junto com o
código para dar rastreabilidade ao revisor do PR; não é código de
produto.

## Substituindo pelo MCP interno

Se preferirem usar o MCP interno do time em vez do MCP público da
Atlassian, basta trocar o conteúdo de `plugins/dev-toolkit/.mcp.json`
pelo endpoint interno. Os comandos referem-se às operações de forma
genérica (buscar issue, transicionar, comentar), então funcionam com
qualquer servidor que exponha essas capacidades. Vantagem do MCP interno:
centralizar regras do time (transições válidas, filtros padrão) no servidor.

## Versionamento

Semântico, no `plugin.json` e no `marketplace.json`. Mudanças no fluxo
(fases, gates, template de PR) = minor. Correções de texto = patch.
Mudanças que exigem reconfigurar os repositórios = major, com aviso no PR.
