# <Nome do Projeto>

<Descrição curta do projeto, arquitetura e convenções de código.>

## Dev Flow Config

Configuração compartilhada pelos plugins `dev-toolkit` e `pbi-toolkit`
(cada um lê só as chaves que usa — instalar um sem o outro é normal).
Ajuste por projeto.

- jira_projects: PROJ
  # Vários boards no mesmo repo? Liste as chaves: PLAT, MOB, PAY
- status_ready: Ready for Dev
- status_in_progress: In Progress
- status_testing: Testing
- base_branch: main
# - stage_branch: stage
#   # Opcional. Com essa chave, o work-task abre DOIS PRs por
#   # repositório (stage + main como draft) em vez de um só, com tag de
#   # release nos dois; o PR de main sai de draft quando o de stage
#   # mergear. Sem essa chave, fluxo de PR único de sempre, sem stage.
- test_command: npm test
- lint_command: npm run lint
# Usadas só pelo pbi-toolkit (opcionais — omita se não instalado):
- issue_type_pbi: História
- issue_type_epico: Épico

# Projeto com um stack só (a maioria): pare por aqui, o bloco acima basta.
#
# Projeto full-stack (frontend + backend) — descomente e ajuste `stacks`.
# `dev-toolkit-setup` detecta monorepo (mais de uma pasta com seu
# próprio package.json/pyproject.toml) e já gera isso sozinho — só
# precisa escrever na mão se preferir configurar manualmente, ou se um
# dos stacks vive em outro repositório (polyrepo, sem como detectar
# automaticamente a partir daqui).
#
# Convenção de escopo do comando: sempre `cd <path> && <comando>` — o
# mesmo idioma pra qualquer linguagem/ferramenta, em vez de decorar a
# flag de escopo específica de cada uma (--prefix do npm, etc.). Uma PBI
# que tocar mais de um stack pode virar mais de um PR (um por
# repositório efetivamente tocado); veja o README do plugin.
#
# Se `stacks:` existir, `test_command`/`lint_command` da raiz acima
# (linhas 17-18) deixam de valer — cada stack tem o seu. Os dois
# exemplos de `frontend` abaixo são ALTERNATIVOS (monorepo OU polyrepo),
# nunca os dois juntos — escolha o que bate com a topologia real.
#
# stacks:
#   - name: backend
#     path: backend/            # monorepo: caminho relativo a este repo
#     test_command: cd backend && uv run pytest
#     lint_command: cd backend && uv run ruff check .
#   - name: frontend                              # (monorepo)
#     path: frontend/           # ainda monorepo: outro caminho, mesmo repo
#     test_command: cd frontend && yarn test
#     lint_command: cd frontend && yarn lint
#   - name: frontend                              # (polyrepo — alternativa ao de cima, não some junto)
#     repo: git@github.com:org/frontend-repo.git   # polyrepo: outro repo
#     local_path: ../frontend-repo                  # onde clonar como irmão
#     test_command: yarn test
#     lint_command: yarn lint

## Convenções deste repositório

- <Como o código é organizado: camadas, pastas, padrões>
- <Framework de testes e onde ficam os testes>
- <Regras de estilo além do lint>
- <Qualquer coisa que um dev novo precisaria saber antes de abrir PR>
