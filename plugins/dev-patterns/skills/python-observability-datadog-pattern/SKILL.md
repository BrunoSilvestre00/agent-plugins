---
name: python-observability-datadog-pattern
description: Instrumentação Datadog (ddtrace) de um serviço Python — auto-instrumentação por exclusão nomeada nunca por allowlist, sampling por padrão com exceção documentada para caminho crítico, logs estruturados correlacionados ao trace.
version: 0.1.0
---

# Instrumentação Datadog (ddtrace) de um serviço Python

Use esta skill ao instrumentar (ou revisar a instrumentação de) um
serviço Python — API síncrona/assíncrona ou worker — com APM do
Datadog.

## Auto-instrumentação: `patch_all` com exclusão nomeada, nunca allowlist

`patch(fastapi=True)` (ou equivalente, citando só o framework web) é um
**allowlist estreito**: qualquer integração que a chamada não citar —
o cliente HTTP das chamadas de saída, o driver do banco, o cache —
fica **sem span nenhum**, silenciosamente, sem erro nenhum indicando
isso. Achado real: um serviço com `patch(fastapi=True)` só tinha spans
da própria API — a chamada de saída pro gateway de pagamento (via
`httpx`) e as queries do banco (via `asyncpg`/SQLAlchemy) nunca
apareceram no APM, apesar de serem exatamente as duas dependências mais
importantes de observar num serviço de pagamento.

```python
# ERRADO — allowlist estreito: tudo que não for citado fica invisível,
# e nada avisa que ficou de fora
from ddtrace import patch
patch(fastapi=True)

# CERTO — instrumenta tudo por padrão; exclusão é decisão explícita e
# nomeada, não omissão
from ddtrace import patch_all
patch_all(boto=False, botocore=False, grpc=False, redis=False)
```

Exclua só o que for genuinamente ruidoso ou de baixo valor
diagnóstico pro seu serviço (ex.: `redis` se for só cache de leitura
sem lógica de negócio nele) — nunca exclua por padrão o cliente HTTP
de chamadas de saída nem o driver de banco, que são normalmente as
integrações que mais importa observar.

## Sampling por padrão — 100% é exceção documentada, não default

Capturar tudo (`sample_rate=1.0`) tem custo real de indexação que
cresce com o volume. O padrão é uma taxa moderada pro serviço e uma
taxa bem baixa pra chamadas de infra de alto volume/baixo valor
diagnóstico — **100% só quando for uma decisão consciente pra um
caminho de negócio crítico** (ex.: um serviço de pagamento), e essa
decisão precisa estar documentada no código, não ser um default
silencioso.

```python
from ddtrace import tracer
from ddtrace.sampler import DatadogSampler, SamplingRule

rules = [
    # Caminho crítico (ex.: gateway de pagamento): captura completa —
    # decisão consciente do time, registrada aqui, não um default.
    SamplingRule(sample_rate=1.0, service='meu-servico-critico'),
    # Serviço em geral: taxa moderada.
    SamplingRule(sample_rate=0.2000, service='meu-servico'),
    # Chamadas de infra de alto volume, baixo valor diagnóstico.
    SamplingRule(sample_rate=0.0001, service='aws.s3'),
    SamplingRule(sample_rate=0.0001, service='aws.sqs'),
]
tracer.configure(sampler=DatadogSampler(rules=rules))
```

Alternativa mais simples, sem código (útil quando o serviço não tem um
ponto único de configuração do tracer): `DD_TRACE_SAMPLE_RATE` ou
`DD_TRACE_SAMPLING_RULES` via variável de ambiente — mesma disciplina,
default cost-aware, override documentado pra exceção.

## Logs estruturados, correlacionados ao trace

Log em JSON (não texto livre) e `DD_LOGS_INJECTION=true` (o ddtrace
injeta `dd.trace_id`/`dd.span_id` no registro de log automaticamente)
— sem isso, log e trace não se cruzam no Datadog, e investigar um
incidente vira alternar entre duas ferramentas sem conseguir ligar um
ao outro. Achado real: um serviço do time já tem um formatter JSON
pronto, mas ele nunca é o handler realmente ligado (o handler ativo usa
um formatter de texto livre à parte), e a correlação existente é por
`request_id` próprio, não por `dd.trace_id`/`dd.span_id` — ou seja, o
serviço tem log estruturado e trace, mas não tem os dois cruzados; é
exatamente a lacuna que esta seção existe pra fechar, não uma descrição
do que já funciona hoje.

```python
LOGGING = {
    'version': 1,
    'formatters': {
        'json': {
            'format': (
                '{"time":"%(asctime)s","level":"%(levelname)s",'
                '"logger":"%(name)s","message":"%(message)s",'
                '"dd.trace_id":"%(dd.trace_id)s","dd.span_id":"%(dd.span_id)s"}'
            ),
        },
    },
    'handlers': {'console': {'class': 'logging.StreamHandler', 'formatter': 'json'}},
    'loggers': {'': {'handlers': ['console'], 'level': '${LOG_LEVEL}'}},
}
```

Log estruturado verboso (nível DEBUG, campos extras) fica atrás de uma
env var explícita, nunca ligado por padrão em todo ambiente — o mesmo
raciocínio de custo do sampling se aplica a volume de log.

## Unified service tagging

`DD_SERVICE`/`DD_ENV`/`DD_VERSION` consistentes entre trace, log e
métrica — sem isso, o Datadog não consegue cruzar as três telemetrias
do mesmo deploy. `DD_VERSION` normalmente vem do CI (ex.: SHA curto do
commit passado como build arg), não hardcoded no código.

## O que NÃO fazer

- `patch(<framework>=True)` como única instrumentação — allowlist
  estreito que esconde silenciosamente as integrações mais importantes
  (cliente HTTP de saída, driver de banco) sem nenhum erro indicando
  a lacuna.
- Sampling 100% como default do serviço, sem uma linha explicando por
  que aquele caminho é crítico o suficiente pra justificar o custo.
- Log estruturado verboso ligado incondicionalmente em todo ambiente,
  sem uma env var de opt-in.
- Chave de API do Datadog hardcoded em código ou arquivo versionado —
  vem de configuração/secret manager, nunca em texto puro.
