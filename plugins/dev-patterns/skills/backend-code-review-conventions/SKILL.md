---
name: backend-code-review-conventions
description: Checklist de revisão para PRs de backend neste padrão (Clean Architecture Python) — sinaliza violação de camada, use case sem registro no DI e lacunas de teste.
metadata:
  version: "0.2.0"
---

<!-- Use junto com a skill `code-review-conventions` deste mesmo plugin
     (prioridades gerais de review, formato de comentário) — esta aqui
     cobre só os pontos específicos deste padrão de arquitetura backend. -->

# Revisão de código backend (Clean Architecture Python)

Use esta skill ao revisar um PR de backend deste padrão, além das
prioridades gerais de `code-review-conventions`.

## Bloqueadores — violação de camada

- `domain/` importando qualquer coisa de `infrastructure/`ou`presentation/`
  — a entidade não pode saber que banco ou framework web existem.
- Entidade de domínio com `Column`/`relationship`/decorator de ORM
  direto nela, em vez de mapeamento imperativo separado (ver
  `python-repository-pattern`).
- Use case fazendo chamada HTTP/SQL diretamente em vez de delegar a um
  repositório/serviço injetado.
- Modelo/tipo específico de um provedor externo vazando para fora do
  módulo do adapter (ver `python-provider-adapter-pattern`).

## Bloqueadores — DI e ciclo de vida

- Caso de uso novo sem entrada correspondente no container de DI — sobe
  em teste unitário (instancia direto) mas quebra em runtime.
- Endpoint fazendo query/commit fora de `async with uow:`.
- Endpoint levantando exceção não tratada para um resultado de negócio
  esperado (deveria ser um status code explícito).
- Use case levantando `Exception`/`ValueError` cru para um resultado de
  negócio esperado (não encontrado, regra violada) em vez de uma
  exceção nomeada — sem isso o endpoint não consegue distinguir "não
  encontrado" (404) de um bug real (500) (ver `python-use-case-pattern`).
- `UnitOfWork.__aexit__` (ou equivalente) que não fecha a sessão em
  nenhum caminho — vaza conexão do pool a cada uso, mesmo sem exceção
  nenhuma (ver `python-repository-pattern`).

## Bloqueadores — estado e teste

- Setter de status sem guarda de transição (transição permitida a partir
  de qualquer estado).
- Máquina de estado nova ou alterada sem teste da transição inválida
  (só o caminho feliz coberto).
- Caso de uso, entidade ou adapter novo sem teste correspondente para o
  critério de aceite do PR.
- Segredo/token/chave de provedor hardcoded em qualquer arquivo.

## Bloqueadores — segurança

- Query montada por concatenação/f-string com dado de entrada em vez de
  query parametrizada (ORM/`bindparam`) — mesmo dentro do repositório.
  O padrão do time (SQLAlchemy Core/ORM via `select(...)`/`.where(...)`)
  já é seguro por padrão; qualquer SQL cru concatenando entrada do
  usuário é a exceção que quebra isso.
- Payload de webhook processado (não só logado) antes de verificar a
  assinatura do provedor (ver `python-provider-adapter-pattern`).
- Segredo/token/chave de provedor hardcoded em qualquer arquivo (já
  listado acima — repetido aqui porque é o achado de segurança mais
  comum).
- Dado sensível (documento, cartão, token) em log ou em mensagem de
  exceção que pode acabar em ferramenta de observability sem redação.
- Resposta de erro genérica vazando detalhe interno (stack trace,
  query, path de arquivo) pro cliente em vez de um `ResponseError`
  próprio.

## Bloqueadores — performance

- Chamada de API externa (`httpx`/`requests`) sem timeout explícito —
  uma dependência lenta/travada consome o worker indefinidamente.
- Query em loop (uma query por item de uma lista) em vez de uma query
  batch — candidato clássico de N+1.
- Endpoint de listagem sem paginação/limite — cresce sem teto conforme
  a tabela cresce.
- Sessão/conexão aberta fora do escopo de `async with uow:` (não fecha
  determinística, some no meio de uma requisição concorrente).

## Sugestões (não bloqueiam, mas vale comentar)

- Repositório com método que nenhum use case chama (candidato a remover).
- Lógica de decisão de evento (`if status == X: event = ...`) inline no
  use case em vez de via Factory/Provider (ver `python-domain-event-pattern`).
- Duplicação de lógica de chamada a serviço externo que já existe em
  outro adapter — sugerir consolidar.

## Quando aprovar

Aprove quando não restar `[blocker]` aberto e a suíte de testes/lint do
CI estiver verde.
