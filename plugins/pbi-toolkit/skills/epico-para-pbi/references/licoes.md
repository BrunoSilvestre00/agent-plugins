# Lições aprendidas (docs/knowledge/)

Mecanismo de compounding do time: cada ciclo de refinamento grava o que aprendeu, e o próximo ciclo começa lendo. Arquivos markdown versionados no git, um por lição.

## Formato do arquivo

`docs/knowledge/<slug-da-licao>.md`

```markdown
---
tipo: insight | armadilha | convencao | estimativa
tags: [pagamentos, integracao-x, fatiamento]
confianca: alta | media | baixa
criado: AAAA-MM-DD
fonte: <épico/PBI de origem, ex.: PROJ-123 / docs/pbis/pix/>
substitui: <slug de lição anterior, se esta a contradiz — opcional>
---

# <Título afirmativo em 1 linha>

<2-6 frases: o que aprendemos, em que contexto vale, e o que fazer diferente.
Concreto e acionável — "integração com o gateway Y sempre exige homologação
deles, reserve 2 semanas" e não "integrações são difíceis".>
```

## Regras de escrita

1. **1 a 3 lições por ciclo, no máximo.** Lição demais vira ruído que ninguém lê — capture só o que mudaria uma decisão futura.
2. **Acionável ou não entra**: a lição deve completar a frase "da próxima vez, faça/considere X". Desabafo não é lição.
3. **Cheque contradições antes de gravar**: procure em `docs/knowledge/` lições sobre as mesmas tags. Se a nova contradiz uma antiga, confirme com o usuário qual vale, marque `substitui:` na nova e mova a antiga para `docs/knowledge/arquivadas/`.
4. **Valide com o usuário** o texto de cada lição antes de gravar.
5. **Confiança honesta**: `alta` só com evidência repetida (aconteceu 2+ vezes ou tem dado); um caso isolado é `media` ou `baixa`.

## Como as lições são consumidas (passo 1 do fluxo principal)

Antes de entrevistar o usuário sobre um épico, busque em `docs/knowledge/` (grep por tags/termos do épico). Para cada lição relevante encontrada:
- **Use como resposta-padrão**: em vez de perguntar do zero, apresente ("Temos uma lição registrada: <resumo> [fonte]. Vale para este épico?").
- **Cite a lição no README do épico** em `docs/pbis/<epico>/README.md`, na seção "Lições consideradas".
- Lições com `confianca: baixa` entram como pergunta, nunca como premissa.

Se `docs/knowledge/` não existir, siga normalmente — ela nasce no primeiro `/pbi-toolkit:compound`.
