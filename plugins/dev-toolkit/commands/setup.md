---
description: Provisiona o repositório para o ciclo dev-toolkit (CLAUDE.md com Dev Flow Config)
argument-hint: "[chave(s) do projeto Jira, ex: PROJ ou PLAT, MOB]"
---

Provisione este repositório para o ciclo de desenvolvimento do time.

Entrada (pode estar vazia): $ARGUMENTS

## Passos

1. **CLAUDE.md**: verifique se existe na raiz.
   - Não existe → crie um mínimo: título com o nome do repo, 1 parágrafo de descrição (inferida do código/README) e a seção abaixo. Sugira ao usuário rodar `/init` depois para enriquecer o restante.
   - Existe com `## PBI Config` (o `pbi-toolkit` rodou primeiro) → NÃO crie uma seção nova. Renomeie o cabeçalho para `## Dev Flow Config` (mesma convenção compartilhada, ver README de ambos os plugins) e acrescente só as chaves abaixo que ainda faltam — nunca duplique `jira_projects`/`status_ready`, que o `pbi-toolkit` já deve ter preenchido.
   - Existe sem `## Dev Flow Config` nem `## PBI Config` → adicione a seção ao final, sem tocar no resto.
   - Existe com `## Dev Flow Config` já completa (todas as chaves abaixo presentes) → informe que já está configurado, mostre os valores atuais e pare (a menos que o usuário peça para alterar).

2. **Detecte monorepo antes de qualquer outra coisa**: liste os diretórios
   de primeiro nível que têm seu próprio `package.json` ou `pyproject.toml`
   (ex.: `backend/pyproject.toml` e `frontend/package.json`, ou vários
   `package.json` em pastas distintas).
   - **Zero ou um encontrado** (manifesto só na raiz, ou repositório de
     stack único): siga o passo 3 normalmente, sem `stacks:`.
   - **Mais de um encontrado**: é monorepo. Para CADA diretório
     candidato, detecte `test_command`/`lint_command` daquele diretório
     (mesma lógica do passo 3, mas lendo o `package.json`/`pyproject.toml`
     de dentro dele) e monte o comando como `cd <diretório> && <comando
     detectado>` — mesmo idioma pra qualquer linguagem/ferramenta, em vez
     de flag de escopo específica de cada uma. Apresente a lista de
     stacks detectados (nome = nome do diretório, `path`, `test_command`,
     `lint_command`) para o usuário confirmar ou corrigir antes de
     escrever.
   - **Stack em outro repositório (polyrepo)**: isso não dá pra detectar
     a partir daqui — só pergunte se o usuário mencionar. Se sim, peça
     `repo` (URL de clone) e confirme `local_path` (convenção: diretório
     irmão deste); o `test_command`/`lint_command` desse stack **não**
     leva `cd` (a execução já roda de dentro do outro repositório — ver
     Fase 5 do `work-task`).

3. **Detecte antes de perguntar** — nunca pergunte o que já dá pra descobrir sozinho lendo o repositório:
   - `test_command`/`lint_command`: `package.json` → `scripts.test`/`scripts.lint` (sugira `npm test`/`npm run lint`, ou `yarn test`/`yarn lint` se o repo já usa yarn — veja `packageManager`/`yarn.lock`); `pyproject.toml` → sugira `pytest`/`ruff check .` (ou `uv run pytest`/`uv run ruff check .` se houver `uv.lock`). Sem nada detectável, pergunte.
   - `base_branch`: leia o branch padrão do remoto (`git symbolic-ref refs/remotes/origin/HEAD` ou equivalente) em vez de assumir `main`.
   - `stage_branch` (opcional): verifique se existe uma branch remota
     com um nome comum de ambiente intermediário — `stage`, `staging`,
     `homolog`, `hml` (`git ls-remote --heads origin <nome>` pra cada
     um). Se achar alguma, sugira o nome exato encontrado como
     `stage_branch` — ativa o fluxo de dois PRs (stage + main draft) do
     `work-task`. Nenhuma dessas encontrada não significa que o
     repositório não tem ambiente de stage — só que o nome não é um dos
     comuns; **não pergunte e não invente** — só ofereça a chave se o
     usuário mencionar explicitamente
     que o time usa ambiente de stage.
   - Apresente cada valor detectado como sugestão a confirmar, não como fato — o usuário pode corrigir.

4. **Status do workflow do Jira**: use $ARGUMENTS como `jira_projects` se informado; senão pergunte (uma pergunta por vez). Se as tools da Atlassian estiverem disponíveis, consulte os status reais do workflow do(s) projeto(s) e sugira os nomes exatos de `status_ready`/`status_in_progress`/`status_testing` — **nunca invente nome de status**, um nome que não bate exatamente com o workflow do Jira quebra silenciosamente as transições depois. Sem tools da Atlassian, pergunte e avise que o nome precisa ser exato.

5. **Preencher a seção**:

   ```markdown
   ## Dev Flow Config

   - jira_projects: <KEYS>
   - status_ready: <status exato do workflow>
   - status_in_progress: <status exato do workflow>
   - status_testing: <status exato do workflow>
   - base_branch: <detectado>
   - stage_branch: <nome exato detectado (stage/staging/homolog/hml) — omitir a linha inteira se nenhuma dessas existir nem o usuário mencionar>
   - test_command: <detectado ou perguntado — omitir se monorepo com `stacks:`>
   - lint_command: <detectado ou perguntado — omitir se monorepo com `stacks:`>
   ```

   Se o passo 2 detectou monorepo (ou coletou um stack em polyrepo),
   acrescente `stacks:` de verdade (não comentado) com a lista já
   confirmada pelo usuário — formato de referência em
   `examples/CLAUDE.md.example`. Repositório de stack único não leva
   `stacks:` nenhum.

6. **Detecte Spec Kit (opcional, informativo)**: se existir `.specify/`
   na raiz deste repositório, avise ao final que `/dev-toolkit:refine` vai
   apontar pra `/speckit.clarify` quando fizer sentido, na camada de
   refinamento que já usa Spec Kit — não escreva nada na config por causa
   disso, é só um aviso, nunca uma instalação por conta própria.
7. Reporte o que foi criado/alterado e sugira commitar. **Não commite sem o usuário pedir.**

## Regras

- NÃO invente nome de status do Jira — errado aqui quebra `work-task` silenciosamente mais tarde.
- NÃO crie uma segunda seção de config se `## PBI Config` já existir — funda as duas.
- NÃO escreva `stacks:` sem o usuário confirmar a lista detectada — a detecção é sugestão, não fato.
- NÃO commite sem o usuário pedir.
