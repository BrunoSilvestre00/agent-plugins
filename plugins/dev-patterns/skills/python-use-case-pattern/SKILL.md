---
name: python-use-case-pattern
description: Um caso de uso por classe, dependências injetadas, único método execute(input)->output, registrado no container de DI.
version: 0.1.1
---

# Padrão de caso de uso (Python)

Use esta skill ao adicionar uma operação nova de aplicação (o que o
sistema faz, não como os dados são guardados nem como a UI chama isso).

## Uma classe, um método público

```python
from dataclasses import dataclass


@dataclass
class MeuUseCaseInput:
    algum_id: str
    algum_valor: int


@dataclass
class MeuUseCaseOutput:
    resultado: str


class MeuUseCase:
    def __init__(self, uow, meu_event_sender):
        self.uow = uow
        self.meu_event_sender = meu_event_sender

    async def execute(self, input: MeuUseCaseInput) -> MeuUseCaseOutput:
        agregado = await self.uow.meu_repository.get_by_id(input.algum_id)
        if agregado is None:
            raise AgregadoNaoEncontradoError(input.algum_id)

        agregado.confirmar()
        await self.uow.meu_repository.save(agregado)
        await self.uow.commit()

        event = MeuAgregadoEventFactoryProvider.get_event_factory(agregado.status)
        if event is not None:
            await self.meu_event_sender.publish(event.create(agregado), self.__class__.__name__)

        return MeuUseCaseOutput(resultado="ok")
```

- Dependências (repositórios via `uow`, serviços externos, event
  senders) entram no `__init__` — nunca instanciadas dentro do
  `execute()`.
- `Input`/`Output` são dataclasses simples, agrupadas por feature em
  `input.py`/`output.py` (várias inputs/outputs do mesmo módulo no mesmo
  arquivo, não um arquivo por classe).
- Um use case não chama outro use case como biblioteca de funções soltas
  — se precisa orquestrar outro fluxo, injete o outro use case como
  dependência (constructor), do mesmo jeito que injeta um repositório.

## Resultado de negócio esperado é uma exceção própria, nunca genérica

`AgregadoNaoEncontradoError` acima é uma exceção **específica do
domínio** (`class AgregadoNaoEncontradoError(Exception): ...`), nunca
`raise Exception(...)`/`raise ValueError(...)` cru. Isso é o que
permite ao endpoint (`python-api-endpoint-pattern`) capturar
especificamente essa exceção e responder com o status code certo (404)
— sem uma exceção nomeada, o endpoint só teria `except Exception`
genérico pra tudo, e "não encontrado" (esperado, deveria virar 404)
fica indistinguível de um bug de verdade (deveria virar 500 e ser
investigado). O use case levanta a exceção de domínio; quem decide o
HTTP status é o endpoint, nunca o use case.

## Registro no container de DI

Todo use case novo precisa de uma entrada `providers.Factory` no
container, com as dependências já resolvidas por nome:

```python
meu_use_case = providers.Factory(
    MeuUseCase,
    uow=uow,
    meu_event_sender=meu_event_sender,
)
```

Esquecer esse registro é o erro mais comum ao adicionar um use case —
o código compila e os testes unitários passam (porque instanciam a
classe direto), mas o endpoint/handler que depende do container quebra
em runtime. Confira isso antes de considerar a task pronta.

## O que NÃO fazer

- Use case fazendo `requests`/`httpx`/SQL direto em vez de delegar a um
  repositório ou serviço de infraestrutura injetado.
- Mais de um método público relevante na classe (`execute` e mais algum
  outro "helper" chamado de fora) — se precisa de dois fluxos, são dois
  use cases.
- Lógica de transição de estado feita no use case em vez de delegada à
  entidade (ver `python-domain-entity-pattern`).
- Esquecer o registro no container — sem isso, o use case não existe
  para o resto da aplicação.
- Levantar `Exception`/`ValueError` crus para um resultado de negócio
  esperado (não encontrado, regra violada) — o endpoint precisa de uma
  exceção nomeada pra distinguir isso de um bug real.
