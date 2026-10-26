# Changelog — backend-testing-pattern

## 0.1.1 (patch)

- Corrige dois exemplos frágeis: `pytest.raises(Exception, match=...)`
  virou o tipo específico (`TransicaoDeStatusInvalidaError`, sem match
  por string); `assert resultado is not None` virou assert de valor de
  campo real.

## 0.1.0 (minor)

- Versão inicial: fixtures, Mock/AsyncMock para dependência externa,
  teste explícito de transição de estado válida e inválida, checklist de
  conclusão.
