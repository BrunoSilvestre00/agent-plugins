---
name: python-provider-adapter-pattern
description: Port & adapter para integração com serviço externo — DTOs de entrada/saída genéricos, adapter concreto versionado, auditoria não-fatal, nunca segredo hardcoded.
version: 0.1.1
---

# Padrão de integração com serviço externo (port & adapter)

Use esta skill ao integrar com um provedor/serviço externo novo (gateway
de pagamento, serviço de terceiro, API externa qualquer).

## O port: DTOs genéricos, independentes do provedor

Defina a interface em termos do que a aplicação precisa, não do que o
provedor específico expõe:

```python
@dataclass
class MeuServicoInput:
    algum_campo: str


@dataclass
class MeuServicoOutput:
    id: str
    status: str
```

## O adapter: concreto, isolado, versionado

A implementação de um provedor específico vive na sua própria pasta,
versionada (`v1/`, `v2/`...) — se o provedor mudar de versão de API ou
você trocar de provedor, o resto da aplicação não sabe disso, só
conhece o port:

```
infrastructure/service/meu_servico/
  input.py                    # port: MeuServicoInput
  output.py                   # port: MeuServicoOutput
  provedor_x/
    v1/
      model/                  # modelos específicos da API do provedor
      service.py              # implementa o port usando o provedor
```

Tipos/modelos específicos do provedor **nunca** vazam para fora do
módulo do adapter — o use case só importa o `output.py` do port, nunca
`provedor_x.v1.model.response.XResponse`.

## Auditoria da chamada, sem quebrar o fluxo principal

Toda chamada de saída (request e response) deve ser logada para
auditoria — e uma falha ao logar **nunca** derruba a chamada real:

```python
def _log(self, request: dict, response: dict, action: str):
    try:
        self.provider_logger.log(json.dumps(request), f"{self.FOLDER}/request/{action}")
        self.provider_logger.log(json.dumps(response), f"{self.FOLDER}/response/{action}")
    except Exception as e:
        self.logger.error(f"Erro ao logar auditoria: {e}")
```

## Idempotência em chamada que muda estado

Toda chamada que cria/modifica algo do lado do provedor externo (não
uma leitura) envia uma chave de idempotência (ex.: o próprio ID da
operação de negócio) — evita duplicar o efeito em caso de retry.

## Timeout explícito, sempre

Todo cliente HTTP do adapter define timeout explícito — nunca o default
da biblioteca (que pode ser "esperar para sempre"):

```python
async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
    response = await client.post(url, json=data, headers=headers)
```

Sem timeout, um provedor externo lento ou travado consome o worker
(ou a conexão do pool, se a chamada acontecer dentro de `async with
uow:`) indefinidamente — sob carga concorrente isso esgota recursos
rápido, mesmo com o provedor voltando ao normal depois.

## O que NÃO fazer

- Modelo/tipo do provedor externo vazando para o use case ou pra fora do
  módulo do adapter.
- Falha de log de auditoria propagando exceção e derrubando a chamada
  real.
- Chamada que muda estado externo sem chave de idempotência.
- Cliente HTTP sem timeout explícito (default da biblioteca, que pode
  nunca expirar).
- Segredo/token/chave do provedor hardcoded em código — vem de
  configuração (variável de ambiente/secrets manager), nunca em texto
  puro no repositório.
