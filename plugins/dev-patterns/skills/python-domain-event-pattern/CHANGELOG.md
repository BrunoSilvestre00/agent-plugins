# Changelog — python-domain-event-pattern

## 0.1.1 (patch)

- Corrige o exemplo de publicação dual-write, que não tinha
  try/except nenhum apesar do texto já dizer que falha no event store
  não deveria derrubar o fluxo. Adiciona o try/except (só em volta do
  store, nunca do bus) e uma nota explícita sobre o dual-write problem
  — falha no bus depois do commit não é coberta por isso, e para fluxo
  crítico o padrão de outbox transacional é a alternativa mais segura.

## 0.1.0 (minor)

- Versão inicial: `DomainEvent` base, evento por dataclass específica,
  Factory+Provider para escolher o evento pelo estado do agregado,
  publicação dual-write (bus + store) com método-por-evento no bus.
