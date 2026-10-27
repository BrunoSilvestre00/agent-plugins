---
name: python-domain-entity-pattern
description: Entidades de domínio como dataclasses Python puras, com transições de estado guardadas e sem acoplamento a ORM/framework.
metadata:
  version: "0.1.1"
---

# Padrão de entidade de domínio (Python)

Use esta skill ao criar ou alterar uma entidade de domínio (o núcleo do
negócio, não o modelo de persistência).

## A entidade é uma `@dataclass` pura

- Nenhum decorator de ORM, nenhuma dependência de `pydantic`/framework web
  na entidade — ela precisa ser importável e testável sem banco, sem
  FastAPI, sem nada além de `dataclasses`/`enum`/tipos padrão.
- Status/tipo como `Enum`, nunca string solta comparada por valor.
- Comportamento de negócio vive na entidade, não em funções soltas do
  use case — se a regra é "só posso pagar um pedido que está aguardando
  pagamento", isso é um método da entidade, não um `if` no use case.

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class MeuAgregadoStatus(Enum):
    CRIADO = "CRIADO"
    CONFIRMADO = "CONFIRMADO"
    CANCELADO = "CANCELADO"


@dataclass
class MeuAgregado:
    id: Optional[int] = None
    status: MeuAgregadoStatus = MeuAgregadoStatus.CRIADO
    created: datetime = field(default_factory=datetime.now)

    def confirmar(self):
        self.status = MeuAgregadoStatus.CONFIRMADO

    def cancelar(self):
        self.status = MeuAgregadoStatus.CANCELADO
```

## Transição de estado sempre guardada

Nunca deixe um setter genérico (`self.status = novo_status`) exposto sem
guarda. Centralize a transição num método que valida a partir de qual
status a mudança é permitida, e rejeite (levante exceção) qualquer
transição fora da lista:

```python
class TransicaoDeStatusInvalidaError(ValueError):
    pass


def set_status(self, status: MeuAgregadoStatus):
    transicoes = {
        MeuAgregadoStatus.CONFIRMADO: self.confirmar,
        MeuAgregadoStatus.CANCELADO: self.cancelar,
    }
    permitido_a_partir_de = {
        MeuAgregadoStatus.CONFIRMADO: [MeuAgregadoStatus.CRIADO],
        MeuAgregadoStatus.CANCELADO: [MeuAgregadoStatus.CONFIRMADO],
    }
    if status not in transicoes:
        raise TransicaoDeStatusInvalidaError(f"Status inválido: {status}")
    if self.status not in permitido_a_partir_de.get(status, []):
        raise TransicaoDeStatusInvalidaError(
            f"Não é possível ir de {self.status} para {status}"
        )
    transicoes[status]()
```

Rejeitar sempre levanta — nunca um `return` silencioso. Um `return` ali
faz o chamador achar que a transição aconteceu (nenhum erro, nenhum
retorno indicando falha) quando na verdade nada mudou; o bug só aparece
depois, longe de onde a causa real está. Uma exceção **própria**
(`TransicaoDeStatusInvalidaError`, não `ValueError`/`Exception` crus) é
o que permite ao chamador (use case ou endpoint) decidir o que fazer com
uma transição inválida especificamente — sem precisar inspecionar a
mensagem de erro pra saber o que aconteceu.

Toda entidade com máquina de estado precisa de um teste cobrindo **as
duas pontas**: a transição válida E a transição inválida rejeitada — ver
`backend-testing-pattern`.

## O que NÃO fazer

- Entidade herdando de `Base` do SQLAlchemy ou com `Column(...)` — isso é
  responsabilidade do mapeamento (`python-repository-pattern`), não da
  entidade.
- Setter de status sem guarda de transição.
- Transição inválida tratada com `return`/`pass` silencioso em vez de
  levantar — esconde a falha do chamador em vez de sinalizar.
- Levantar `ValueError`/`Exception` crus para uma regra de domínio —
  defina uma exceção própria (`XInvalidaError`), pra quem chama poder
  reagir ao caso específico sem inspecionar a mensagem.
- Lógica de negócio implementada no use case em vez de na entidade
  (ex.: `if pedido.status == X: pedido.status = Y` fora de um método
  nomeado da entidade).
- Comparar status por string (`status == "CONFIRMADO"`) em vez de `Enum`.
