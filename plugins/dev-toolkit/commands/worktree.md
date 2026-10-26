---
description: Cria (ou só prepara) um git worktree isolado para um PBI, sem começar a trabalhar ainda
argument-hint: "<JIRA-ID do PBI> (ex: PROJ-142)"
---

# Preparar worktree para trabalho paralelo (opcional)

PBI alvo: **$1**

**Não é mais pré-requisito do `/dev-toolkit:work-task`** — ele já
isola cada PBI numa worktree dedicada sozinho, na própria Fase 0 (o dev
só precisa abrir um terminal por PBI e chamar `/dev-toolkit:work-task
<ID>` direto em cada um). Este comando continua útil pra quem quer só
**preparar o ambiente com antecedência**, sem iniciar o ciclo agora
(ex.: deixar 3 worktrees prontas hoje de manhã pra trabalhar cada uma ao
longo do dia) — mesma lógica de isolamento, só que sem disparar o
`work-task` no final. (O `/dev-toolkit:work-task` também cria, por
conta própria, worktrees adicionais *dentro* do ciclo de um PBI — uma
por task — isso é outra coisa, não afeta este comando.)

## Instruções

1. Valide que `$1` foi informado. Se não, PARE e pergunte.
2. Leia `base_branch` na seção `## Dev Flow Config` do CLAUDE.md.
3. `git fetch origin` para garantir referências atualizadas.
4. Determine o diretório do worktree: irmão do repositório atual, com o
   nome `<repo>-<id-minúsculo>` (ex: `../meu-servico-proj-142`).
   Se o diretório já existir, PARE e informe o caminho — provavelmente a
   task já está em andamento lá.
5. Crie o worktree com a branch da task:
   `git worktree add <diretório> -b feat/$1 origin/{base_branch}`
   Se a branch `feat/$1` já existir, crie o worktree apontando para ela
   (sem `-b`) e avise o usuário.
6. Se o projeto tiver setup de dependências (ex: `npm install`,
   `poetry install` — verifique o CLAUDE.md), rode-o dentro do worktree.
7. Informe ao usuário:
   - O caminho do worktree criado
   - O próximo passo: "Abra um novo terminal, `cd <diretório>`, rode
     `claude` e execute `/dev-toolkit:work-task $1`."
   - Como limpar depois do merge: `git worktree remove <diretório>`

## Regras

- NÃO inicie o desenvolvimento neste comando. Ele apenas prepara o ambiente.
- NÃO transicione nenhum card do Jira aqui.
- NUNCA remova worktrees existentes sem instrução explícita do usuário.
