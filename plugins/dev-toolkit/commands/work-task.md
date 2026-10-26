---
description: Desenvolve um PBI do Jira de ponta a ponta e abre UM PR por repositório tocado (feat/{PBI-ID})
argument-hint: "<JIRA-ID do PBI> (ex: PROJ-142)"
---

# Desenvolver um PBI de ponta a ponta

PBI alvo: **$1**

Você vai executar o ciclo completo de desenvolvimento deste PBI. A escrita
do épico/PBI (spec e critérios de aceite) é responsabilidade do PO e já
deve estar pronta no Jira antes deste comando rodar — este comando não
escreve nem reinterpreta escopo de produto, só o implementa.

O PBI pode virar 1 task ou 20, pode tocar um stack só ou vários (ex.:
backend e frontend) — o processo é sempre o mesmo. Tasks internas nunca
geram PR próprio: o PR é sempre no nível do PBI, um por repositório
efetivamente tocado (ver Fase 5 sobre stacks).

Siga as fases NA ORDEM. Cada fase tem um gate: se o gate falhar, PARE,
explique o problema ao usuário e aguarde instrução. Nunca pule um gate.

**Sempre que PARAR esperando resposta do usuário, em qualquer fase**:
grave (crie ou sobrescreva) `.dev-flow/$1/aguardando.md` com uma linha
curta — fase atual + resumo de 1 frase da pergunta pendente. Isso é o
que o `/dev-toolkit:triage` lê pra dar visão de quais PBIs, entre vários
rodando em paralelo (worktrees diferentes), estão parados esperando
você — sem esse marcador, o dev precisaria checar terminal por
terminal. Assim que o usuário responder e o comando continuar, apague o
arquivo (ou deixe a próxima escrita sobrescrever, se parar de novo logo
em seguida). Nunca deixe o marcador órfão depois que o PBI terminar
(Fase 13) ou for abandonado — apague ao concluir.

---

## Fase 0 — Configuração e pré-condições

1. Leia a seção `## Dev Flow Config` do CLAUDE.md deste repositório:
   - `jira_projects` (lista; retrocompatível com `jira_project` singular),
     `status_ready`, `status_in_progress`, `status_testing`
   - `base_branch` (ex: main)
   - `stage_branch` (opcional, ex: stage): se presente, a Fase 10 abre
     **dois** PRs por repositório (stage + main draft) em vez de um só —
     ver Fase 10. Sem essa chave, o repositório segue no fluxo de PR
     único de sempre, sem stage.
   - **Stacks**: se houver uma lista `stacks:`, cada entrada define um
     stack do produto (ex.: `backend`, `frontend`), com `path` (relativo
     a este repo; omitido ou `.` = o repo inteiro), `test_command` e
     `lint_command` próprios, e opcionalmente `repo`/`local_path` quando
     esse stack vive em **outro repositório** (polyrepo) — nesse caso
     `local_path` é onde ele deve estar clonado como diretório irmão
     deste. Se não houver `stacks:`, trate o repositório inteiro como um
     stack único, usando `test_command`/`lint_command` direto do Dev Flow
     Config (comportamento de hoje, sem mudança nenhuma).
   Se a seção não existir ou estiver incompleta, PARE e sugira
   `/dev-toolkit:setup` — ele detecta test/lint/branch sozinho e consulta
   os status reais do workflow do Jira em vez de o dev preencher na mão.
2. Verifique que `$1` foi informado e que seu prefixo (a chave antes do
   hífen, ex: `PAY` em `PAY-142`) está em `jira_projects`. Se o prefixo
   não estiver na lista, PARE: informe os projetos configurados neste
   repositório e NÃO prossiga — o PBI provavelmente pertence a outro
   repositório. Se `$1` estiver vazio, sugira `/dev-toolkit:tasks`.
3. **Isole este PBI numa worktree dedicada, automaticamente** — o dev
   não precisa rodar `/dev-toolkit:worktree` antes, só abrir um terminal
   por PBI e chamar este comando direto em cada um:
   - **Diretório atual já é essa worktree** (a branch atual já é
     `feat/$1`): nada a fazer, continue aqui.
   - **Já existe uma worktree pra este PBI em outro lugar** (`git
     worktree list --porcelain`, procure o bloco cujo `branch` seja
     `refs/heads/feat/$1` e extraia o `worktree <caminho>`
     correspondente — o formato porcelain evita ambiguidade de parsing
     que a saída tabular normal teria): informe o caminho e `cd` pra
     lá — o resto do ciclo roda de lá em diante (retomando trabalho de
     uma sessão anterior).
   - **Nenhuma das duas**: crie uma nova. Diretório irmão deste repo,
     nome `<repo>-<id-minúsculo>` (ex.: `../meu-servico-proj-142`); se
     esse caminho já existir e não for uma worktree git válida, PARE e
     informe o conflito — nunca sobrescreva. `git fetch origin`; depois
     `git worktree add <diretório> -b feat/$1 origin/{base_branch}`
     (sem `-b`, apontando pra branch existente, se `feat/$1` já existir
     sem worktree associada). Se o projeto tiver setup de dependências
     (`npm install`/`poetry install`/etc., conforme o `CLAUDE.md`), rode
     dentro da worktree nova. `cd` pra lá.
   - Daqui em diante, "este repositório" nas fases seguintes é a
     worktree, não o diretório onde a sessão começou — o checkout
     original fica intocado, por isso não importa se ele tinha mudança
     não commitada. Isto cobre só o stack local/atual; stacks remotos
     (`repo`/`local_path`, polyrepo) continuam resolvidos na Fase 5, sem
     mudança.
4. Verifique que `gh auth status` funciona. Se não, PARE e peça ao
   usuário para autenticar o GitHub CLI.

## Fase 1 — Ler, compreender e identificar os stacks do PBI

1. Busque o PBI $1 no Jira via MCP: descrição completa, critérios de
   aceite, comentários e links. **O Jira é a única fonte da verdade** —
   não procure spec em arquivos do repositório; se o PO precisou de
   contexto adicional, ele está na própria issue.
2. Se houver mais de um stack configurado (Fase 0), identifique quais
   este PBI realmente toca: cruze a linguagem dos critérios de aceite
   (menção a endpoint/API/modelo/migração → backend; menção a
   tela/componente/formulário/UI → frontend, por exemplo) com os stacks
   configurados. **Nunca escolha por categoria genérica de tecnologia**
   — a config `stacks:` não declara tecnologia explicitamente, então
   infira lendo o manifesto de cada stack (`package.json`/
   `pyproject.toml` no `path`/`local_path` dele); se mais de um stack
   configurado corresponder à mesma categoria (ex.: dois frontends
   React+TS em repositórios diferentes, um do produto atual e outro de
   outro produto), o critério de aceite precisa indicar qual
   `name`/repositório específico, não só "é frontend". Se
   não conseguir decidir com confiança — inclusive quando dois ou mais
   stacks batem na mesma categoria sem indicação clara de qual —, PARE
   e pergunte ao usuário quais stacks este PBI envolve — não adivinhe
   por proximidade ou ordem de configuração, isso decide quantos PRs vão
   existir.
3. **Gate de compreensão**: escreva um resumo de 5-10 linhas do que será
   feito, listando os critérios de aceite como checklist e, se houver
   mais de um stack configurado, os stacks identificados. Se QUALQUER
   critério for ambíguo, contraditório, tecnicamente inviável, ou se o
   PBI não tiver critério de aceite algum, PARE e pergunte ao usuário.
   NÃO invente requisitos. NÃO assuma comportamento não especificado —
   comportamento não especificado é pergunta, não decisão.

## Fase 2 — Visão de implementação do dev

1. Apresente o resumo da Fase 1 (critérios de aceite como checklist,
   stacks identificados) — **sem propor nenhuma abordagem técnica
   ainda** — e PARE, perguntando: "Você quer descrever como enxerga a
   execução deste PBI em alto nível (padrão a seguir, módulo a estender
   vs. criar do zero, etc.), ou prefere que eu avalie a arquitetura e
   decomponha sozinho?" — nunca proponha uma abordagem antes de
   perguntar; quem fala primeiro é o dev, ou ele pede explicitamente pra
   você decidir. Isto existe porque uma sugestão sua ali vira âncora — o
   dev tende a só confirmar em vez de pensar do zero, mesmo quando
   discordaria se tivesse formado a própria opinião antes. Mesma
   disciplina de "PARE e grave `.dev-flow/$1/aguardando.md`" de qualquer
   outra fase (ver preâmbulo no topo deste arquivo) enquanto espera a
   resposta.
2. **Se o dev descrever uma visão**: registre-a, curta e em alto nível
   (não é spec de código, é intenção de abordagem — ex.: "estender o
   serviço X" vs. "criar um novo endpoint", "reusar o padrão Y"). Vira
   insumo da Fase 3 (o `architect` avalia especificamente essa
   abordagem, não uma composição genérica) e da Fase 6 (a decomposição
   em tasks segue essa visão). Se algo na visão do dev parecer
   tecnicamente inviável ou contraditório com os critérios de aceite,
   não corrija por conta própria — aponte o conflito e pergunte, mesma
   disciplina do gate de compreensão da Fase 1.
3. **Se o dev pedir autonomia** ("pode seguir sozinho", "decide você",
   ou equivalente): siga direto para a Fase 3 sem mais perguntas — mesmo
   comportamento de antes desta fase existir. Não é obrigatório ter
   visão pra todo PBI; a escolha é do dev, a cada PBI, não um padrão
   configurável de antemão.
4. **A visão do dev, quando houver**, é gravada como preâmbulo em
   `.dev-flow/$1/tasks.md` no mesmo momento em que a Fase 5 grava
   "Dependências identificadas na Fase 3" (assim que a primeira branch
   deste PBI for criada) — sobrevive à sessão inteira, mesmo com vários
   stacks entre esta fase e a Fase 6.

## Fase 3 — Avaliação de arquitetura

Roda ANTES de tocar o board — se isto bloquear, o card nunca chega a
ficar em "in progress" falsamente enquanto espera uma decisão humana.

1. Busque o épico pai do PBI $1 no Jira. Se o PBI não tiver épico pai,
   pule esta fase inteira (sem épico, não há composição possível) e vá
   para a Fase 4.
2. Procure, nos comentários do épico, um já registrado com o marcador
   `## Decisão de Arquitetura`. Se existir e, pela leitura do seu
   conteúdo, ele plausivelmente já cobrir o escopo deste PBI, siga
   direto para a Fase 4 — não invoque o agent, não repita a análise.
3. Senão, invoque o agent `architect` com escopo **pré-decomposição**,
   passando: os critérios de aceite deste PBI, os títulos + critérios
   de aceite de todos os PBIs irmãos do mesmo épico (busca no Jira;
   leitura rasa dos irmãos, não o spec inteiro de cada um), e a **visão
   de implementação do dev da Fase 2, se houver** — o `architect` avalia
   especificamente essa abordagem (não uma composição genérica) contra
   infra/integrações/padrões/composição, e pode discordar dela como
   discordaria de qualquer proposta.
4. Veredito do `architect`: ele avalia explicitamente infra, integrações
   externas, padrões do projeto e composição do épico — nunca só "parece
   grande ou pequeno" — e lista toda dependência identificada num
   checklist próprio, nunca deixando nenhuma sem resposta.
   - **SEM IMPACTO** (nenhuma dimensão exige decisão/padrão novo, nenhuma
     dependência que só humano resolve — item que virou task de rotina,
     tipo criar recurso de infra seguindo padrão existente, não conta) →
     siga para a Fase 4, sem mais fricção; se houver dependência marcada
     "vira task", ela só é registrada pra Fase 6 incluir a task
     correspondente, sem precisar de confirmação humana aqui.
   - **IMPACTO** (isolado ou cumulativo) **ou dependência em aberto** →
     PARE. Apresente ao usuário o rascunho de ADR completo (título,
     status, contexto, dimensões avaliadas, decisão proposta,
     alternativas consideradas, consequências, dependências
     identificadas, repositórios afetados — template completo do agent
     `architect`) e peça confirmação/ajuste **de cada dependência em
     aberto**, uma a uma — nunca prossiga com uma decisão de arquitetura
     ou uma dependência sem resposta explícita do humano. Isto vale a
     mesma disciplina de "PARE e pergunte" das Fases 1 e 6.
5. **Se algum item da checklist referenciar um stack específico `<X>`**
   — seja uma dependência de infra "RESOLVIDA (vira task, stack <X>)",
   seja uma decisão de "qual codebase hospeda" (dimensão 2 do
   `architect`) que apontou um stack diferente dos já identificados —:
   confira se `<X>` está entre os stacks que a Fase 1 identificou como
   tocados por este PBI.
   - Já está: nada a fazer aqui, a Fase 5/6 desse stack já vai processar
     a task normalmente.
   - Não está, mas `<X>` existe em `stacks:` (Fase 0): **adicione `<X>` à
     lista de stacks envolvidos deste PBI agora** — ele passa a fazer
     parte do ciclo (ganha sua própria passagem pelas Fases 5 a 11),
     mesmo que os critérios de aceite não mencionassem isso
     explicitamente. Informe o usuário dessa adição antes de seguir.
   - `<X>` não existe em `stacks:` nenhum: PARE e pergunte ao usuário
     como proceder — configurar o stack agora (`/dev-toolkit:setup`,
     com `repo`/`local_path` se for outro repositório), apontar outro
     codebase, ou tratar como dependência em aberto. Nunca crie uma
     task num stack que não existe na configuração.
6. **Antes de postar a decisão confirmada** (só chega aqui vindo da
   branch IMPACTO/dependência-em-aberto do passo 4, já com aprovação
   humana): releia os comentários do épico MAIS UMA VEZ — nunca confie
   só na leitura do passo 2. PBIs irmãos do mesmo épico podem estar
   rodando esta mesma Fase 3 em paralelo (worktrees/sessões diferentes);
   se outro comentário `## Decisão de Arquitetura` já apareceu nesse
   intervalo, PARE — não poste a sua. Apresente o conflito ao usuário
   (o que o irmão decidiu, o que você tinha decidido) e peça pra
   reconciliar antes de prosseguir. Sem comentário novo, siga
   normalmente.
7. Comente no **ÉPICO** (nunca no PBI individual) o ADR completo e
   aprovado, começando o comentário com o marcador `## Decisão de
   Arquitetura` — é esse marcador que a Fase 3 de PBIs futuros deste
   épico vai procurar no passo 2.
8. **Opcional**: ofereça rodar `/dev-toolkit:diagram <épico>` (a chave do
   épico pai encontrada no passo 1) pra visualizar a decisão
   recém-confirmada e linkar o resultado no mesmo
   comentário do épico. Esse comando isolado trata disponibilidade da
   skill, instalação opcional e fallback — não duplique nada disso aqui.
   Puramente opcional; siga sem ele se o usuário não quiser.
9. Para cada repositório listado em "Repositórios afetados" que já usar
   a convenção `docs/adr/` (verifique se a pasta existe naquele repo —
   nunca crie a convenção num repo que não tem): crie lá um arquivo
   stub, nunca uma cópia do conteúdo inteiro:

   ```markdown
   # ADR-00X — <título curto>

   Decisão completa: <link do comentário no épico correspondente>
   Repositórios afetados por esta decisão: <lista>
   ```

   O stub deste repositório entra no mesmo commit/PR do PBI que está
   rodando agora, se for um dos repositórios que este PBI toca.
10. Só agora siga para a Fase 4.

## Fase 4 — Assumir o PBI no board

1. Atribua a issue $1 ao usuário atual.
2. Transicione a issue para o status `{status_in_progress}`.
3. Se a transição falhar (workflow do Jira não permite), PARE e informe —
   provavelmente o card não está no status esperado e outra pessoa pode
   estar trabalhando nele.

## Fase 5 — Preparar a(s) branch(es) do PBI

Repita as Fases 5 a 11 abaixo **uma vez para cada stack identificado na
Fase 1, mais qualquer stack que a Fase 3 tenha adicionado** (dependência
"RESOLVIDA (vira task, stack <X>)" — de infra ou de "qual codebase
hospeda" — num stack que os critérios de aceite não mencionavam) —
sempre na mesma sessão, um de cada vez. Dois stacks que vivem
no mesmo repositório (sem `repo` configurado) compartilham a MESMA
branch/PR; um stack com `repo` configurado (polyrepo) ganha sua própria
branch/PR nesse outro repositório. **A Fase 12 não entra nesse
repita** — ela roda só UMA VEZ, depois que TODOS os stacks/repositórios
já completaram sua própria Fase 5 a 11 (PR aberto, CI verde); ela olha
pra todos de uma vez, nunca um só, mesmo que os PRs de cada
repositório tenham sido abertos em momentos diferentes do loop.

1. Para um stack **local** (sem `repo` configurado, incluindo o caso de
   stack único): opere na worktree que a Fase 0 já criou/reconheceu —
   nada a fazer aqui além de continuar nela.
2. Para um stack **remoto** (com `repo`/`local_path` configurado):
   verifique se `local_path` existe como diretório irmão. Se não existir,
   PARE e informe o comando de clone necessário — nunca clone sozinho sem
   o dev confirmar. Se existir, todas as próximas fases para este stack
   rodam dentro desse diretório, exatamente com a mesma disciplina.
3. Em cada repositório **remoto** envolvido (`git fetch origin`
   primeiro): crie a branch `feat/$1` a partir de `{base_branch}` — a
   ÚNICA branch daquele repositório que vai virar PR para este PBI. O
   repositório local já teve isso resolvido na Fase 0, não repita aqui.
   Se dois stacks remotos compartilham repositório, é a mesma branch
   para os dois — não crie duas.
   - Se a branch já existir local ou remotamente (fora do caso já
     coberto pela Fase 0), PARE e pergunte ao usuário se deve continuar
     nela ou recriá-la. Nunca delete ou faça force-push por conta
     própria.
4. **Se a Fase 3 identificou alguma dependência "RESOLVIDA (vira
   task)"** — de qualquer dimensão, não só infra: também vale pra "qual
   codebase hospeda" (dimensão 2) —: assim que a PRIMEIRA branch deste
   PBI for criada (o primeiro repositório/stack processado, não
   necessariamente o dono da dependência), grave-a imediatamente em
   `.dev-flow/$1/tasks.md` como um preâmbulo (`## Dependências
   identificadas na Fase 3`, listando cada item, o stack a que pertence,
   e o tipo — infra ou codebase-placement) e commit — mesmo antes da
   Fase 6 rodar formalmente pra aquele stack. Depender só da memória da
   conversa até a Fase 6 do stack certo é frágil quando há vários stacks
   (cada um com sua própria Fase 5 a 11 completa, incluindo espera de CI)
   entre a Fase 3 e o stack que realmente precisa da task; gravar cedo
   evita perder o item numa sessão longa. A Fase 6 do stack correspondente
   lê esse preâmbulo e o formaliza em task de verdade (T00N).
5. **Se a Fase 2 registrou uma visão de implementação do dev**: no mesmo
   momento do passo anterior (primeira branch deste PBI criada), grave-a
   também em `.dev-flow/$1/tasks.md` como preâmbulo próprio (`## Visão de
   implementação do dev`) e commit junto — mesmo registro durável, mesmo
   motivo: não depender da memória da conversa até a Fase 6 rodar pra
   cada stack.

## Fase 6 — Decompor o PBI em tasks (por stack)

1. Em cada repositório envolvido, explore o codebase o suficiente para
   entender que camadas/módulos o PBI toca ali e como o repositório
   costuma estruturar mudanças parecidas — inclusive suas convenções
   próprias de arquitetura/skills, que podem ser diferentes das de outro
   stack (ex.: convenções de backend são diferentes das de frontend). Se
   `.dev-flow/$1/tasks.md` tiver o preâmbulo "Visão de implementação do
   dev" (Fase 2), a decomposição segue essa abordagem — não proponha uma
   diferente sem antes apontar a divergência ao usuário.
2. Quebre os critérios de aceite relevantes **daquele stack** em tasks
   (T001, T002, ...), cada uma com: descrição objetiva, arquivos/módulos
   prováveis, e a qual critério(s) de aceite ela atende. Uma task = uma
   unidade de trabalho que um único `implementer` executa sem colidir
   com outra em arquivo. Se um stack tiver mais de um `path` configurado
   dentro do mesmo repositório (monorepo), marque a qual `path`/stack
   cada task pertence — isso decide quais skills e qual
   `test_command`/`lint_command` o `implementer` e a Fase 8 usam para ela.
   Se `.dev-flow/$1/tasks.md` já tiver o preâmbulo "Dependências
   identificadas na Fase 3" (gravado na Fase 5) com item deste stack,
   formalize-o aqui como task de verdade, no stack indicado — usando
   `terraform-project-pattern`/`terraform-security-pattern` **só se o
   item for de infra de verdade** (criar a IaC é trabalho deste ciclo,
   não algo que fica faltando por fora); se o item for uma decisão de
   "qual codebase hospeda" (dimensão 2), implemente com as convenções
   normais daquele stack (as skills de `dev-patterns` que já se
   aplicariam a qualquer task ali, sem Terraform envolvido). Sem
   preâmbulo mas com dependência "RESOLVIDA (vira task)" ainda fresca na
   sua memória desta sessão (PBI de stack único, sem gap entre Fase 3 e
   aqui), inclua a task do mesmo jeito.
3. Se a própria decomposição for ambígua (mais de uma forma razoável de
   dividir, com consequências técnicas diferentes), PARE e pergunte —
   mesma disciplina da Fase 1.
4. Registre a decomposição em `.dev-flow/$1/tasks.md`, dentro de cada
   repositório envolvido (checklist `- [ ] T001 (stack) ...`) e commit na
   branch `feat/$1` daquele repositório: `chore($1): decompõe PBI em
   tasks`. **Mantenha os preâmbulos "Dependências identificadas na Fase
   3" e "Visão de implementação do dev" da Fase 5, se existirem** — não
   apague nem substitua nenhum dos dois, só acrescente a task formalizada
   logo abaixo deles. Esses preâmbulos são o registro durável da
   checklist do `architect` e da visão do dev, em arquivo, não só na
   memória da conversa — é ele que a Fase 9 vai ler pra saber o que já
   estava previsto. Esse arquivo é rastreabilidade do ciclo, não código do
   produto — fica no PR para o revisor ver o raciocínio da quebra.

## Fase 7 — Implementar cada task, isolada

Para cada task NÃO concluída de `.dev-flow/$1/tasks.md` (dentro do
repositório daquele stack), respeitando dependências entre tasks (tasks
sem colisão de arquivo podem rodar juntas, no máximo 3 por vez):

1. Crie uma worktree isolada ramificada de `feat/$1` **daquele
   repositório** (nunca de `{base_branch}` diretamente): branch
   `tmp/$1/T0NN`, diretório irmão do repositório (`../<repo>-$1-t0nn`,
   minúsculo).
2. Invoque o agent `implementer` nessa worktree, passando: a task, o(s)
   critério(s) de aceite que ela cobre, o caminho de `feat/$1`, e — se o
   repositório tiver mais de um stack/path — qual stack esta task é e
   quais convenções/skills usar.
3. Ao final, invoque o agent `verifier` com escopo "task": o diff da
   worktree contra `feat/$1`, e o critério de aceite correspondente.
   - REPROVADO ou APROVADO COM RESSALVAS relevante → volta ao
     `implementer` (máx. 2 rodadas). Se não convergir, marque a task como
     bloqueada em `.dev-flow/$1/tasks.md` e siga para a próxima elegível
     — não insista.
   - APROVADO → mescle `tmp/$1/T0NN` de volta em `feat/$1` (a mesclagem é
     sempre sequencial, mesmo quando a implementação rodou em paralelo,
     para não haver corrida na ponta da branch), remova a branch/worktree
     temporária, marque `[x]` na task com o hash do commit.

## Fase 8 — Verificação agregada por repositório (gate obrigatório)

Em cada repositório envolvido, só depois de TODAS as tasks elegíveis
daquele repositório concluídas (ou explicitamente bloqueadas e
reportadas):

1. Rode o `lint_command`/`test_command` de CADA stack cujo `path` tenha
   arquivo alterado no diff daquele repositório — a suíte INTEIRA de cada
   um desses stacks deve passar, incluindo o que nenhuma task tocou
   diretamente. Stack cujo `path` não teve nada alterado pode ser pulado
   (ex.: PBI só de backend não precisa rodar a suíte do frontend, mesmo
   que ambos estejam configurados no mesmo repositório).
2. Invoque o agent `verifier` com escopo "PBI neste repositório": `git
   diff {base_branch}...feat/$1` (deste repositório) contra os critérios
   de aceite atribuídos aos stacks presentes aqui — não a soma dos
   resumos de cada task. Ele deve confirmar que a parte do PBI feita
   neste repositório está coerente — sem debug esquecido, segredos,
   arquivos fora de escopo, TODOs sem justificativa.
3. Se algum critério de aceite atribuído a este repositório não estiver
   coberto, volte à Fase 6 ou 7 (pode faltar task, não só ajuste) — nunca
   abra o PR com ressalva não resolvida.

## Fase 9 — Revisão final de arquitetura (gate obrigatório)

A Fase 8 verifica critério de aceite e qualidade de teste — não design.
A Fase 3 avaliou o PBI ANTES de existir código; esta fase avalia o
resultado real DEPOIS de tudo implementado, porque a implementação pode
divergir do que foi decidido (ou parecia "sem impacto" no início) mesmo
com a Fase 8 aprovada. Roda em TODO PBI, não só nos que a Fase 3 flagou.

Em cada repositório envolvido:

1. Antes de invocar o agent, releia o preâmbulo "Dependências
   identificadas na Fase 3" em `.dev-flow/$1/tasks.md`, se ele existir —
   é o registro durável da checklist, não confie só na memória da
   conversa até aqui, principalmente se muitas tasks/stacks rodaram
   entre a Fase 3 e agora. **Pelo mesmo motivo, rebusque o PBI $1 no
   Jira via MCP agora** (descrição completa e critérios de aceite) —
   não reaproveite só o que ficou na memória da conversa desde a Fase 1;
   o Jira é a única fonte da verdade (mesma disciplina da Fase 1), e o
   check de omissão do `architect` precisa dos critérios de aceite
   completos e corretos, não de um resumo desatualizado de várias fases
   atrás.
2. Invoque o agent `architect` com escopo **revisão final**, passando:
   **os critérios de aceite completos do PBI** (rebuscados no passo
   anterior — necessário pro check de omissão do `architect`, que cruza
   o que o PBI/sua métrica exige contra o diff, não só contra o que a
   Fase 3 perguntou), `git diff {base_branch}...feat/$1`, a checklist de
   dependências completa da Fase 3 **sempre que ela existir** (com ou
   sem ADR — um item marcado RESOLVIDA (vira task) também conta, mesmo
   sem decisão de
   arquitetura formal; releia o preâmbulo do passo anterior se a memória
   da conversa não bastar), a decisão de arquitetura da Fase 3 (se
   houve — o texto completo, não só "houve ou não"), e o relatório da
   verificação agregada da Fase 8.
3. Veredito:
   - **SEM DESVIO** → siga para a Fase 10.
   - **DESVIO ENCONTRADO** → PARE. Apresente ao usuário o que o
     `architect` achou (o que diverge, onde, por que importa) e peça
     decisão: ajustar a implementação (volta à Fase 7), formalizar como
     decisão de arquitetura nova (volta à Fase 3 pra registrar o ADR
     retroativamente, seguindo o mesmo processo de aprovação), extrair
     parte do escopo pra um PBI novo (se o `architect` sinalizou que
     parte disso merecia ser PBI próprio — o usuário decide se roda
     `/pbi-toolkit:quebrar-epico <épico>`, modo incremental, e o que fica
     neste PBI vs. no novo), ou o usuário aceitar o desvio conscientemente
     e registrar a justificativa no corpo do PR (seção "Decisões e
     trade-offs" da Fase 10). Nunca decida por conta própria qual das
     opções vale.
4. **Opcional, com SEM DESVIO**: se este PBI criou ou alterou IaC (task
   "vira task" da Fase 6, ou qualquer mudança em Terraform/CDK/
   CloudFormation), ofereça rodar `/dev-toolkit:diagram <épico>` — agora
   a infra existe de verdade no código, então o comando prefere o
   Modo A (análise da IaC real) em vez de só narrar a partir do ADR,
   dando um diagrama fiel ao que foi construído, não só ao que foi
   proposto na Fase 3. Puramente opcional, nunca instale nada por conta
   própria.

## Fase 10 — Abrir o(s) PR(s) (por repositório tocado)

Em cada repositório envolvido:

1. Push da branch: `git push -u origin feat/$1`.
2. **Sem `stage_branch` configurado**: siga o fluxo de sempre — um único
   PR, via `gh pr create`, base `{base_branch}`, sem tag, corpo na
   estrutura compartilhada abaixo (seção "Tag": "nenhuma"). Pule os
   passos 3 a 6 abaixo.
3. **Com `stage_branch` configurado**: **planeje** (ainda não crie) a
   tag da release. `git fetch origin --tags` primeiro, sempre — mesmo
   que a Fase 0 já tenha dado fetch nesta sessão, o describe abaixo
   precisa do estado mais recente de verdade, principalmente se este
   PBI foi retomado de uma sessão anterior. Rode `git describe --tags
   --abbrev=0 origin/{base_branch}` pra achar a última tag alcançável a
   partir de main — sem tag nenhuma no histórico (primeiro release
   deste fluxo), trate como se a "atual" fosse `v0.0.0`. PARE e
   apresente ao usuário: a tag atual encontrada (ou "nenhuma, será a
   primeira") e uma sugestão de próxima (incremento de patch por
   default) — **peça confirmação do número exato**; bump de versão
   (patch/minor/major) é decisão de produto, nunca adivinhe. **Não crie
   a tag agora** — ela só é criada na Fase 12, no commit real que o
   merge do PR de stage produzir (squash, merge commit ou rebase mudam
   qual commit isso é; tagar a ponta de `feat/$1` agora criaria uma tag
   que o merge deixaria inalcançável do histórico de stage/main). O
   nome já confirmado aqui é usado nos dois PRs como "tag prevista".
4. Abra o PR de **stage**: `gh pr create`, base `{stage_branch}`, head
   `feat/$1`, título `feat($1): <resumo>`, corpo na estrutura abaixo
   (seção "Tag" citando o nome confirmado no passo 3, com "(criada após
   o merge deste PR, na Fase 12)").
5. Abra o PR de **main**, como **draft**: `gh pr create --draft`, base
   `{base_branch}`, head `feat/$1` (a MESMA branch — não crie uma
   segunda), mesmo título/corpo do PR de stage, mais uma linha no topo:
   `⏳ Aguardando merge do PR de stage (#<número>) antes de sair de
   draft — ver Fase 12.`
6. Grave o número dos dois PRs + o nome da tag planejada em
   `.dev-flow/$1/tasks.md`, como preâmbulo (`## PRs abertos`, um bloco
   por repositório: link do PR de stage, link do PR de main, tag
   planejada, status "aguardando merge de stage") — é o que a Fase 12
   lê pra saber o que monitorar, sem depender só da memória da
   conversa, e essencial se este PBI tocar mais de um repositório.

Corpo do PR — mesma estrutura em qualquer caso (com ou sem
`stage_branch`; stage e main, quando os dois existem, são idênticos
exceto a linha de aviso do passo 5):

     ```
     ## O que foi feito
     <resumo objetivo da parte do PBI feita NESTE repositório, 3-6 linhas>

     ## Critérios de aceite
     - [x] <critério 1 atribuído a este repositório>
     - [x] <critério 2 atribuído a este repositório>

     ## Tasks implementadas
     - [x] T001 <descrição curta>
     - [x] T002 <descrição curta>

     ## Como testar
     <passos concretos para o QA/revisor>

     ## Decisões e trade-offs
     <decisões técnicas relevantes tomadas durante a implementação —
     se a Fase 3 registrou uma decisão de arquitetura nova pra este PBI,
     linke o comentário no épico aqui>

     ## Outras partes desta PBI
     <se houver mais de um repositório envolvido, link do(s) outro(s)
     PR(s); "nenhuma" se este for o único>

     ## Tag
     <tag prevista + "(criada após o merge deste PR, na Fase 12)", se
     houver stage_branch configurado; "nenhuma" senão>

     ## Task
     <link para o PBI $1 no Jira>
     ```

## Fase 11 — Aguardar o CI real do PR (gate obrigatório)

A verificação local da Fase 8 não substitui o CI de verdade — ele roda
num ambiente diferente (secrets, matriz de versões, paralelismo) e pode
falhar por motivo que o ambiente local não reproduz. Nunca declare o
PBI pronto só com base na verificação local.

Em cada repositório envolvido, em cada PR aberto na Fase 10 (o único
PR, ou os dois — stage e main — se `stage_branch` estiver configurado;
CI de draft roda igual a CI de PR normal, não pule o do main achando
que draft dispensa isso):

1. Rode `gh pr checks <PR> --watch` (ou repita `gh pr checks` em
   intervalos, se `--watch` não estiver disponível) até os checks
   resolverem.
2. Sem nenhum check de CI configurado neste repositório: siga direto
   para a Fase 12 — não há o que esperar.
3. Todos os checks verdes (nos dois PRs, se houver dois): siga para a
   Fase 12.
4. Algum check vermelho, em qualquer um dos PRs: PARE. NÃO transicione
   o card. Reporte ao usuário qual check falhou (nome + link do log,
   citando qual PR) e pergunte se deve corrigir e re-push (volta à Fase
   7/8 pra ajustar a task/o PBI) ou se o usuário prefere decidir outra
   coisa. Nunca prossiga com CI vermelho em hipótese alguma. Como as
   duas branches são a mesma (`feat/$1`), um re-push corrige o CI dos
   dois PRs de uma vez.
5. Checks pendentes por tempo excessivo (fila de runner lenta, retry
   automático que não conclui): depois de um tempo razoável de espera,
   PARE e pergunte ao usuário se deve continuar esperando ou verificar
   manualmente — nunca trave a sessão esperando indefinidamente.

## Fase 12 — Aguardar o merge do PR de stage e promover o PR de main

Roda **uma única vez**, depois que TODOS os stacks/repositórios já
percorreram sua própria Fase 5 a 11 (ver nota na abertura da Fase 5) —
nunca dentro do loop por stack, e nunca uma vez por repositório. Só
roda se PELO MENOS UM repositório envolvido tem `stage_branch`
configurado (dois PRs abertos na Fase 10 para ele) — repositório sem
`stage_branch` não participa desta fase. Se NENHUM repositório
envolvido tem `stage_branch`, pule a fase inteira e vá direto para a
Fase 13.

Trate **cada repositório com os dois PRs de forma independente** —
numa PBI que toca vários repositórios, o PR de stage de um pode
mergear antes do outro; nunca deixe o repositório mais lento bloquear
a promoção do que já está pronto, e nunca pare no primeiro repositório
pendente sem checar os demais primeiro.

1. Releia `.dev-flow/$1/tasks.md` de CADA repositório envolvido
   (preâmbulo "PRs abertos" da Fase 10) se a memória da conversa não
   bastar — é o registro durável de quais PRs/tag monitorar em cada um.
2. **Para cada repositório com os dois PRs, sem exceção** (percorra
   todos antes de decidir se para ou segue): se o status gravado no
   passo 1 já é "promovido" (retomada de uma sessão anterior que já
   processou este repositório), pule pro próximo sem chamar `gh` de
   novo — reprocessar criaria uma tag duplicada (erro) e comentário
   repetido no PR. Senão, verifique o status do PR de stage (`gh pr
   view <PR-stage> --json state,mergedAt,mergeCommit`).
   - **Ainda aberto (não mergeado)**: marque este repositório como
     pendente e siga pro próximo — não pare ainda.
   - **Mergeado**: crie a tag planejada na Fase 10 **no commit real do
     merge** (`mergeCommit.oid` da resposta acima — o commit que de
     fato existe em `{stage_branch}`, correto com squash, merge commit
     ou rebase): `git fetch origin {stage_branch} && git tag <tag>
     <mergeCommit.oid> && git push origin <tag>`. Promova o PR de main
     de draft pra pronto: `gh pr ready <PR-main>`. Comente no PR de
     main linkando o PR de stage mergeado e a tag criada. Atualize o
     status deste repositório em `.dev-flow/$1/tasks.md` pra
     "promovido".
3. **Depois de percorrer todos os repositórios**: se restou algum
   pendente, PARE — isso não é uma pergunta esperando resposta, é
   status externo (alguém ainda precisa revisar/mergear aquele PR de
   stage). Grave em `.dev-flow/$1/aguardando.md` a lista de
   repositórios pendentes com o link de cada PR de stage, e informe ao
   usuário quais repositórios já foram promovidos e quais ainda faltam.
   Não trave a sessão indefinidamente esperando — encerrar aqui é uma
   parada válida, retomável rodando `work-task` de novo depois (a
   releitura do passo 1 garante que o que já foi promovido não é
   reprocessado). Sem nenhum pendente, siga para a Fase 13.

## Fase 13 — Atualizar o board e reportar

1. Só depois que TODOS os repositórios envolvidos tiverem seu(s) PR(s)
   aberto(s), o CI (Fases 10 e 11 completas em cada um) tiver terminado
   sem check vermelho, e — em repositório com `stage_branch` — a Fase
   12 tiver promovido o PR de main: transicione o PBI $1 para
   `{status_testing}`.
2. **Se algum repositório remoto ainda não pôde ser concluído nesta
   sessão, algum CI ainda estiver vermelho/pendente, ou algum
   repositório com `stage_branch` ainda não teve o PR de main
   promovido**: NÃO transicione ainda — comente no Jira quais PRs já
   existem, quais faltam, o status do CI de cada um, e quais
   repositórios ainda esperam merge do PR de stage. Isto NÃO é uma
   pergunta esperando resposta do usuário (é status de algo externo —
   CI, outro repositório, merge de stage — não uma decisão pendente; se
   algum deles exigiu decisão de verdade, isso já foi um PARE próprio,
   na Fase 11 ou 12, com seu próprio marcador). Ainda assim, rode o
   passo 5 abaixo antes de encerrar esta
   fase — não pule a limpeza do marcador só porque este caminho é
   parcial.
3. Sem o caso do passo 2: comente na issue com o(s) link(s) de todo(s)
   o(s) PR(s) aberto(s).
4. Apresente ao usuário o relatório final:
   - Link de cada PR (com o repositório correspondente) e do PBI
   - Checklist de critérios de aceite e de tasks, por repositório
   - Decisões tomadas e pontos que merecem atenção na revisão
   - Tasks bloqueadas, se houver, e por quê
   - Riscos conhecidos ou débitos deixados (se houver)
   - Se a Fase 0 criou uma worktree pra este PBI: mencione o comando de
     limpeza (`git worktree remove <diretório>`) como sugestão — **nunca
     remova a worktree por conta própria**, é só informação; o dev pode
     querer voltar nela pra revisar antes do merge.
5. **Sempre, em qualquer um dos caminhos acima** (sucesso do passo 1 ou
   parcial do passo 2): apague `.dev-flow/$1/aguardando.md` se existir.
   Chegar até aqui significa que nenhuma pergunta de verdade ficou sem
   resposta nesta sessão — o que resta (CI pendente, repositório
   faltando) é status externo, já visível por outros meios (Fase 11, o
   comentário do passo 2), não uma pergunta que o marcador precise
   sinalizar.

---

## Regras invioláveis

- NUNCA proponha uma abordagem técnica antes de perguntar a visão de
  implementação do dev, na Fase 2 — quem fala primeiro é o dev, ou ele
  pede explicitamente pra você decidir; uma sugestão sua ali vira âncora.
- NUNCA abra PR de task individual — só o PBI (por repositório tocado)
  tem PR.
- NUNCA mescle uma branch de task direto em `{base_branch}` — sempre
  passa por `feat/$1` primeiro, no repositório correto.
- NUNCA pule a verificação agregada da Fase 8 em nenhum repositório
  envolvido, mesmo com todas as tasks individualmente aprovadas.
- NUNCA clone um repositório remoto (stack em polyrepo) sem confirmação
  explícita do usuário.
- NUNCA decida uma mudança de arquitetura sozinho (Fase 3 ou Fase 9) — o
  `architect` propõe, um humano confirma ou ajusta, sempre.
- NUNCA copie o conteúdo inteiro de um ADR num arquivo de repositório —
  o comentário no épico é a única fonte; um arquivo de repo é sempre um
  stub que aponta pra ele.
- NUNCA avance da Fase 3 com dependência marcada "EM ABERTO" no checklist
  do `architect` — cada uma exige resposta explícita do humano antes de
  seguir, mesmo que pareça pequena.
- NUNCA pule a revisão final de arquitetura da Fase 9 em nenhum
  repositório envolvido, mesmo em PBI que a Fase 3 marcou "SEM IMPACTO" —
  a implementação real pode divergir do que foi decidido ou do que
  parecia sem risco no início.
- NUNCA transicione o card para "Testing" com PR pendente, CI
  vermelho/não verificado, ou (em repositório com `stage_branch`) o PR
  de main ainda em draft esperando o de stage (Fase 11/12); NUNCA para
  "Done"/"Concluído" em hipótese alguma — o limite é `{status_testing}`.
- NUNCA confirme o nome de uma tag de release (Fase 10) sem
  apresentar o número exato ao usuário para confirmação — bump de
  versão é decisão de produto, nunca adivinhe. NUNCA crie a tag na
  ponta de `feat/$1` antes do merge (Fase 12 cria no commit real do
  merge, nunca antes) — squash/merge commit/rebase mudam qual commit é
  esse, e uma tag na branch de feature vira órfã do histórico depois.
- NUNCA promova o PR de main de draft pra pronto (Fase 12) sem
  confirmar que o PR de stage foi de fato mergeado — checar o status
  real via `gh`, nunca assumir.
- NUNCA aceite a saída de teste do `implementer` sem a prova do RED
  (teste falhando antes da implementação) — só o GREEN final não basta.
- NUNCA faça merge de nenhum PR, mesmo que os checks passem.
- NUNCA faça `git push --force`, delete branches ou reescreva histórico
  compartilhado, em nenhum repositório.
- NUNCA commite segredos, tokens ou credenciais.
- NUNCA marque um critério de aceite ou task como atendido sem teste ou
  verificação real.
- NUNCA instale plugin/marketplace nenhum por conta própria (ex.: a
  skill de diagrama opcional da Fase 3) — só mencione a opção, o usuário
  decide e instala.
- NUNCA remova uma worktree (a que a Fase 0 criou, ou qualquer outra) sem
  confirmação explícita do usuário — mencione o comando, nunca rode
  sozinho.
- Em caso de dúvida entre parar e improvisar: PARE e pergunte.
