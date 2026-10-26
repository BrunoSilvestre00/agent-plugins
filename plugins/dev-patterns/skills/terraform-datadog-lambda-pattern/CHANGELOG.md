# Changelog — terraform-datadog-lambda-pattern

## 0.1.0 (minor)

- Versão inicial: extension + tracer layer, handler wrapado via
  `DD_LAMBDA_HANDLER`, chave via Secrets Manager, sampling por padrão
  (achado real: exemplo original não tinha nenhuma taxa configurada),
  exclusão de log boilerplate (`START`/`END`/`REPORT RequestId`).
