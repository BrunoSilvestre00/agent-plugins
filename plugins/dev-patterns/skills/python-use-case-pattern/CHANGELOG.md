# Changelog — python-use-case-pattern

## 0.1.1 (patch)

- Corrige o exemplo, que levantava `Exception` crua pra um resultado de
  negócio esperado (não encontrado) — confirmado como padrão real em
  código de produção do time. Agora levanta uma exceção nomeada
  (`AgregadoNaoEncontradoError`), com nova seção explicando por que o
  endpoint precisa dessa distinção pra mapear 404 vs. 500 corretamente.

## 0.1.0 (minor)

- Versão inicial: uma classe por caso de uso, dependências injetadas no
  construtor, único `execute(input)->output`, Input/Output como
  dataclasses agrupadas por feature, registro obrigatório no container
  de DI.
