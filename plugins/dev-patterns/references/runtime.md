# Execução em Claude Code e Codex

Leia estas regras antes do procedimento. Elas definem como os nomes simbólicos
e a delegação do procedimento funcionam no ambiente atual; não removem gates.

## Entrada e caminhos

- ENTRADA é o texto recebido depois da chamada da skill/comando. {ALVO} é o
  primeiro argumento (ID do Jira ou nome do projeto, conforme o procedimento).
  São marcadores de documentação, não variáveis de shell. Substitua pelos
  valores reais antes de criar caminhos ou executar comandos. Se faltar um
  argumento obrigatório, pergunte antes de qualquer alteração.
- Resolva links relativos a partir do arquivo que os contém, dentro do plugin
  instalado; arquivos do produto e `.dev-flow/` são relativos ao repositório
  ou worktree alvo. Não procure recursos do plugin no repositório consumidor.
- Chamadas como `dev-toolkit-setup` e `pbi-toolkit-compound` são nomes de
  skills. No Codex, use o nome qualificado exibido no catálogo, por exemplo
  `$dev-toolkit:dev-toolkit-setup`; o host acrescenta `plugin:` ao nome
  do SKILL.md. No Claude Code, use a skill
  do plugin ou o comando legado `/plugin:ação`. Só encaminhe para outro
  plugin se ele estiver disponível. Spec Kit e diagramas AWS são opcionais;
  confirme a entrada disponível no host antes de recomendar sua sintaxe.

## Configuração compartilhada

- Leia as instruções aplicáveis de AGENTS.md e CLAUDE.md, se existirem.
  ARQUIVO_CONFIG é o arquivo da raiz que já contém `## Dev Flow Config` ou
  `## PBI Config`. Reutilize essa seção nos dois agentes, sem copiá-la.
- Se ambos contiverem configuração, confira os valores: se divergirem,
  peça ao usuário escolher a fonte e resolva o conflito antes de prosseguir;
  se forem iguais, use AGENTS.md no Codex e CLAUDE.md no Claude Code.
- Se nenhum contiver a seção, prefira AGENTS.md no Codex e CLAUDE.md no
  Claude Code. Preserve as instruções existentes ao acrescentar a seção.
  ARQUIVO_CONFIG sempre deve virar o nome real no arquivo gerado, nunca
  ser gravado como nome literal. Um scaffold também deve seguir essa regra.

## Ferramentas e execução

- Use as ferramentas de arquivos, shell e interação disponíveis no host.
  Execute cada comando no diretório alvo explicitamente: um `cd` numa
  chamada anterior não garante o diretório da próxima chamada.
- Worktrees em diretórios irmãos e clones de outros repositórios podem
  precisar de acesso adicional. Respeite a sandbox e solicite o acesso pelo
  mecanismo do host quando necessário, sem desativar a proteção.
- Para Jira, use o MCP oficial da Atlassian incluído neste plugin quando
  presente, ou uma conexão oficial já disponível na sessão. Autentique pelo
  mecanismo de conexão/OAuth do host. Não presuma nomes fixos de tools nem
  recomende comandos de instalação de outro agente. Sem conexão, reporte
  a limitação e siga apenas as etapas locais que o procedimento permitir.
- `/loop` pertence ao Claude Code. No Codex, execute triage sob demanda ou
  use um agendador que o usuário já tenha configurado; não crie agendamentos
  automaticamente. Nunca simule uma espera/agendamento que não aconteceu.
