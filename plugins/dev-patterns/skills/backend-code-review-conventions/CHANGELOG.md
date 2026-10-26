# Changelog — backend-code-review-conventions

## 0.2.0 (minor)

- Adiciona duas seções de bloqueadores que não existiam em nenhuma
  skill de review do plugin: segurança (query parametrizada, webhook
  antes de verificar assinatura, dado sensível em log) e performance
  (timeout de chamada externa, N+1, paginação, sessão vazando). Também
  adiciona bloqueador de use case levantando exceção crua e de
  `__aexit__` sem fechar sessão, espelhando as correções feitas nas
  skills de padrão correspondentes.

## 0.1.0 (minor)

- Versão inicial: bloqueadores de violação de camada, DI/ciclo de vida
  da UoW, estado/teste, e sugestões não-bloqueantes.
