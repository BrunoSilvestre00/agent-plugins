# Changelog — python-api-endpoint-pattern

## 0.1.1 (patch)

- Corrige o exemplo, que checava `agregado is None` direto no endpoint
  em vez de delegar ao use case — inconsistente com
  `python-use-case-pattern`, que levanta uma exceção nomeada pra esse
  mesmo caso. Agora o endpoint chama o use case e captura
  `AgregadoNaoEncontradoError` num `except` específico, antes do
  `except Exception` genérico, pra 404 nunca virar 500 por acidente.

## 0.1.0 (minor)

- Versão inicial: router descoberto por convenção, ciclo de vida
  explícito da UoW (commit/rollback), resultado de negócio esperado como
  status code em vez de exceção, schema de resposta separado da
  entidade, disciplina extra de webhook (log antes, verificar assinatura
  antes de processar).
