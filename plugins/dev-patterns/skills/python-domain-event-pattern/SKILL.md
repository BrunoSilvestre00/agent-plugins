---
name: python-domain-event-pattern
description: Eventos de domínio como dataclasses imutáveis, escolhidos por uma factory a partir do estado do agregado, publicados com dual-write (bus + store de auditoria).
metadata:
  version: "0.1.1"
---

# Padrão de evento de domínio (Python)

Use esta skill ao adicionar um evento novo que o sistema precisa emitir
quando um agregado muda de estado.

## Base do evento

```python
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class DomainEvent:
    aggregate_id: str

    def __post_init__(self):
        self.event_type = self.__class__.__name__
        self.occurred_on = datetime.now(timezone.utc)


@dataclass
class MeuAgregadoConfirmadoEvent(DomainEvent):
    valor: float
    status: str
```

Cada evento é uma dataclass específica por acontecimento notável do
domínio (`XConfirmadoEvent`, `XCanceladoEvent`...) — não um evento
genérico com um campo `type` e um payload solto.

## Factory + Provider: qual evento nasce de qual estado

Não decida "qual evento emitir" com um `if/elif` espalhado pelo use case.
Centralize num Provider que mapeia status → factory do evento
correspondente (Strategy/Abstract Factory):

```python
class MeuAgregadoConfirmadoEventFactory:
    def create(self, agregado: MeuAgregado) -> DomainEvent:
        return MeuAgregadoConfirmadoEvent(
            aggregate_id=str(agregado.id),
            valor=agregado.valor,
            status=agregado.status.value,
        )


class MeuAgregadoEventFactoryProvider:
    @staticmethod
    def get_event_factory(status: MeuAgregadoStatus):
        factories = {
            MeuAgregadoStatus.CONFIRMADO: MeuAgregadoConfirmadoEventFactory(),
        }
        return factories.get(status)
```

O use case só pergunta ao provider qual factory usar, constrói o evento e
publica — nunca monta o evento manualmente inline.

## Publicação: sempre dual-write (bus + store)

O "event sender" publica no bus (mensageria — o que outros serviços
consomem em tempo real) **e** grava num event store de auditoria
(histórico imutável, consultável depois). As duas coisas acontecem
juntas, sempre — nunca só uma:

```python
class MeuAgregadoEventSender:
    def __init__(self, event_bus, event_store, logger):
        self.event_bus = event_bus
        self.event_store = event_store
        self.logger = logger

    async def publish(self, event: DomainEvent, source: str) -> None:
        await self.event_bus.publish(event, source)
        try:
            await self.event_store.save_event(event)
        except Exception as e:
            self.logger.error(f"Erro ao gravar evento no store de auditoria: {e}")
```

O bus expõe **um método por tipo de evento** (`publish_agregado_confirmado`,
não um `publish(event)` genérico que decide por dentro) — fica explícito
no bus quais eventos existem, sem precisar ler o corpo do método pra
descobrir.

O `try/except` em volta só do `event_store` (nunca do `event_bus`) é
proposital: falha ao gravar auditoria não pode derrubar a publicação
real (mesma disciplina do `_log` de auditoria em
`python-provider-adapter-pattern`), mas isso é **best-effort, não
atômico** — nada aqui garante que bus e store fiquem consistentes entre
si (o clássico "dual-write problem": se o `event_bus.publish` falhar
depois do commit da mudança de estado, o evento nunca é publicado e
nada percebe, porque o commit já aconteceu). Pra um fluxo onde essa
inconsistência é inaceitável (ex.: evento que dispara cobrança em outro
serviço), considere o padrão de outbox transacional — grava o evento
na MESMA transação/commit do agregado, e um processo separado relê o
outbox e publica no bus com retry — em vez de publicar direto do use
case depois do commit já ter acontecido.

## O que NÃO fazer

- Montar o evento inline no use case com `if status == X: event = ...`.
- Um evento genérico com campo `type: str` em vez de uma dataclass por
  acontecimento.
- Publicar só no bus (ou só no store) — dual-write é a regra, não opcional.
- Falha ao gravar no event store derrubando o fluxo principal — logue e
  siga; auditoria não pode quebrar o caminho feliz.
