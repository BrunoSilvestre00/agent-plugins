---
name: terraform-datadog-lambda-pattern
description: Instrumentar uma AWS Lambda com Datadog via Terraform — extension + tracer layer, handler wrapado, chave via Secrets Manager, sampling por padrão, exclusão de log boilerplate.
metadata:
  version: "0.1.0"
---

# Instrumentar uma Lambda com Datadog (Terraform)

Use esta skill ao provisionar ou alterar uma AWS Lambda que precisa de
trace/log no Datadog.

## Extension + tracer layer, handler wrapado

O handler real da função nunca é referenciado direto no `handler` do
recurso — quem roda é o wrapper do Datadog, que carrega o handler real
via variável de ambiente:

```hcl
# Placeholder zip + lifecycle ignore_changes: ver terraform-project-pattern
# ("Lambda: Terraform provisiona a forma, o deploy entrega o código") —
# mesma disciplina aqui, não repetida.

resource "aws_lambda_function" "minha_funcao" {
  function_name = "${local.name_prefix}-minha-funcao"
  handler       = "datadog_lambda.handler.handler"
  runtime       = "python3.13"

  layers = [
    var.dd_extension_layer_arn,   # Datadog Lambda Extension
    var.dd_python313_layer_arn,   # tracer Python, versão casada com o runtime
  ]

  environment {
    variables = {
      DD_LAMBDA_HANDLER          = "presentation.lambdas.minha_funcao.handler.handler"
      DD_API_KEY_SECRET_ARN      = var.dd_api_key_secret_arn
      DD_SITE                    = var.dd_site
      DD_SERVICE                 = "meu-produto"
      DD_ENV                     = var.environment
      DD_TRACE_ENABLED           = "true"
      DD_SERVERLESS_LOGS_ENABLED = "true"
      DD_TRACE_SAMPLE_RATE       = "0.2"   # default cost-aware — ver seção de sampling
      DD_TAGS                    = "resource:minha-funcao"
    }
  }
}
```

As ARNs das layers são passadas por variável (sem `default`) — mudam
por região e por versão, quem sobe o `apply` informa o valor real,
igual a qualquer outro recurso já existente referenciado por variável
(`terraform-project-pattern`).

`DD_TAGS` é o mecanismo documentado do Datadog pra tag extra por
recurso (formato `chave:valor`, separado por vírgula se houver mais de
uma). Um projeto real do time usa uma variável `DD_RESOURCE_ATTRIBUTE`
pra isso — não é uma variável reconhecida pelo Datadog Lambda Layer;
se for migrar Terraform existente que a usa, confirme o efeito real
antes de assumir que ela faz o que o nome sugere.

## Sampling por padrão, mesmo em Lambda

`DD_TRACE_SAMPLE_RATE` (ou `DD_TRACE_SAMPLING_RULES` pra regras por
serviço) precisa estar presente **desde a primeira versão** — sem essa
variável, a tendência é capturar praticamente tudo, e o custo escala
com o volume de invocações. Só suba pra `1.0` com uma decisão
documentada (comentário no `.tf` explicando o motivo), a mesma
disciplina do lado da aplicação (`python-observability-datadog-pattern`)
— nunca um default silencioso.

`DD_CAPTURE_LAMBDA_PAYLOAD=true` aumenta o tamanho de cada span (o
payload do evento/resposta inteiro vira parte do span) — ligue só
quando precisar de fato inspecionar o payload pra debugar, não como
default. Achado real: um projeto do time liga isso incondicionalmente
em toda Lambda — vale revisitar função a função se o payload
realmente precisa estar no span, em vez de manter ligado em todas por
inércia.

## Chave da API: Secrets Manager, nunca hardcoded

Mesma disciplina de `terraform-security-pattern` pra qualquer segredo
de origem externa — nunca hardcoded, sempre referenciado por ARN.

```hcl
resource "aws_secretsmanager_secret" "datadog_api_key" {
  name = "${local.name_prefix}/datadog-api-key"
  tags = local.common_tags
}
```

`DD_API_KEY_SECRET_ARN` aponta pro ARN do secret — o extension busca o
valor em runtime; a chave em si nunca aparece em `.tf` nem em
`environment.variables` como texto puro.

## Log de alto volume, baixo valor: exclua na origem

Toda invocação de Lambda gera 3 linhas de boilerplate no CloudWatch
(`START`/`END`/`REPORT RequestId`) — alto volume, zero valor
diagnóstico. Exclua na configuração do forwarder/agent, não deixe
indexar:

```yaml
# datadog.yaml (config do Forwarder ou do Agent que processa os logs)
logs_config:
  processing_rules:
    - type: exclude_at_match
      name: exclude_start_and_end_logs
      pattern: (START|END|REPORT) RequestId
```

Retenção do CloudWatch em si pode ficar curta (ex.: 7 dias) — uma vez
o forwarding pro Datadog funcionando, ele é a cópia durável/consultável;
CloudWatch é só o buffer de origem.

## O que NÃO fazer

- Fazer deploy do código de uma Lambda sem também cablear a layer/env
  vars do Datadog — achado real: um conjunto de Lambdas tinha um
  arquivo de exclusão de log configurado, mas nenhuma dependência
  `datadog-lambda`/`ddtrace`, nenhuma layer, nenhuma variável `DD_*` —
  ou seja, log podia estar chegando, mas não existia trace nenhum.
  Layer e log-forwarding são duas coisas independentes; ter uma não
  implica ter a outra.
- Omitir `DD_TRACE_SAMPLE_RATE`/`DD_TRACE_SAMPLING_RULES` — omissão não
  é neutra, tende a capturar (quase) tudo por padrão.
- Chave de API em texto puro em qualquer arquivo versionado.
- `DD_CAPTURE_LAMBDA_PAYLOAD=true` como default em toda função, sem
  necessidade real de inspecionar payload.
