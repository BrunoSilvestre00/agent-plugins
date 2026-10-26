# Changelog — python-domain-entity-pattern

## 0.1.1 (patch)

- Corrige o exemplo de `set_status`, que contradizia a própria regra
  do texto: dizia "rejeite (levante exceção)" mas o código fazia
  `return` silencioso numa transição inválida. Agora levanta uma
  exceção própria (`TransicaoDeStatusInvalidaError`), não um
  `ValueError` cru.

## 0.1.0 (minor)

- Versão inicial: entidade como dataclass pura, status via Enum,
  transição de estado guardada (rejeita transição inválida), o que não
  fazer (herança de ORM, setter sem guarda, comparação por string).
