---
name: backend-testing-pattern
description: pytest com fixtures, Mock/AsyncMock para dependências externas e teste explícito de transição de estado válida E inválida.
metadata:
  version: "0.1.1"
---

<!-- Diferente da lacuna de TDD do frontend: aqui o padrão de teste já é
     bom onde existe (fixtures, mocks, teste de transição inválida) — o
     problema é adoção, não qualidade. Poucos módulos têm teste; a maioria
     ainda não. Aplique este padrão a todo caso de uso/entidade novo, não
     só onde já existe. -->

# Padrão de teste (pytest, backend Python)

Use esta skill ao escrever o teste de um caso de uso, entidade ou
adapter novo — o teste deve existir antes de considerar a task pronta,
não é opcional mesmo que a cobertura geral do projeto ainda seja baixa.

## Estrutura: teste espelha o módulo, fixtures para os objetos comuns

```python
@pytest.fixture
def agregado():
    return MeuAgregado(id=1, status=MeuAgregadoStatus.CRIADO)


def test_confirmar_sucesso(agregado):
    agregado.confirmar()
    assert agregado.status == MeuAgregadoStatus.CONFIRMADO
```

## Dependência externa: sempre `Mock`/`AsyncMock`, nunca chamada real

Casos de uso recebem repositório/serviço injetado — no teste, injete um
mock, nunca deixe o teste bater num banco ou API de verdade:

```python
def test_meu_use_case():
    payment_gateway_service = AsyncMock(spec=MeuServico)
    payment_gateway_service.chamar.return_value = MeuServicoOutput(id="x", status="ok")

    use_case = MeuUseCase(meu_servico=payment_gateway_service)
    resultado = asyncio.run(use_case.execute(MeuUseCaseInput(...)))

    assert resultado.resultado == "ok"
    payment_gateway_service.chamar.assert_called_once_with(...)
```

`assert resultado is not None` sozinho não verifica quase nada — passa
mesmo se o use case devolver qualquer objeto errado. Assert no valor de
campo específico que o teste está realmente exercitando.

## Máquina de estado: teste a transição válida E a rejeitada

Todo `set_status`/transição guardada (`python-domain-entity-pattern`)
precisa de pelo menos dois testes: um confirmando que a transição
permitida funciona, outro confirmando que uma transição fora da lista
sempre levanta (nunca falha silenciosamente):

```python
def test_confirmar_invalido():
    agregado = MeuAgregado(status=MeuAgregadoStatus.CANCELADO)
    with pytest.raises(TransicaoDeStatusInvalidaError):
        agregado.set_status(MeuAgregadoStatus.CONFIRMADO)
```

`pytest.raises(Exception, match="...")` — tipo genérico + match por
string — é frágil: qualquer refactor de mensagem quebra o teste sem
mudar comportamento nenhum, e o teste passaria mesmo se um bug
completamente diferente levantasse uma exceção com texto parecido.
Capture o tipo específico que a entidade realmente levanta
(`python-domain-entity-pattern`), sem `match`.

Testar só o caminho feliz da máquina de estado é a lacuna mais comum
neste tipo de teste — a transição inválida é onde o bug de verdade
costuma aparecer depois.

## Checklist antes de considerar a task pronta

- [ ] Todo critério de aceite tem teste correspondente.
- [ ] Toda transição de estado nova tem teste da transição válida E da
      inválida.
- [ ] Nenhum teste depende de rede/banco real — tudo externo é mock.
- [ ] A suíte inteira roda e passa, não só o arquivo novo.

## O que NÃO fazer

- Testar só o caminho feliz de uma máquina de estado.
- Mock que so faz `return_value` sem checar `assert_called_with` — o
  teste passa mesmo se o use case parar de chamar a dependência do jeito
  certo.
- Teste batendo em serviço externo real (mesmo que "só às vezes").
- Adiar o teste "porque o resto do projeto também não tem" — cada
  módulo novo aumenta a cobertura, não repete a lacuna.
