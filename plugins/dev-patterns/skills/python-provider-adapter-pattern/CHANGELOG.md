# Changelog — python-provider-adapter-pattern

## 0.1.1 (patch)

- Adiciona seção de timeout explícito no cliente HTTP — gap real: o
  padrão não mencionava isso, apesar do código real do time já fazer
  (`httpx.Timeout(30.0)`). Sem timeout, dependência lenta/travada
  consome worker/conexão indefinidamente.

## 0.1.0 (minor)

- Versão inicial: port com DTOs genéricos, adapter concreto versionado
  por provedor, auditoria de request/response não-fatal, idempotência em
  chamada que muda estado, proibição de segredo hardcoded.
