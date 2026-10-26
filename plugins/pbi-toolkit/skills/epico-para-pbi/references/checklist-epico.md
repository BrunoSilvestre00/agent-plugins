# Checklist — Entendimento do épico

Antes de fatiar, estas perguntas precisam de resposta (do Jira, de documentos, do código ou da entrevista):

1. **Objetivo de negócio** — que resultado o épico persegue e como será medido (métrica-alvo)?
2. **Usuários/personas afetados** — quem usa, quem é impactado indiretamente?
3. **Escopo macro** — quais capacidades entram nesta iniciativa? O que explicitamente fica de fora ou para uma fase 2?
4. **Jornada mínima** — qual é o menor caminho fim-a-fim que já entrega valor (candidato ao primeiro PBI)?
5. **Restrições reais** — compliance/LGPD, sistemas legados obrigatórios, SLA, prazo regulatório, orçamento.
6. **Dependências externas** — outros times, fornecedores, APIs de terceiros, aprovações.
7. **Riscos e incertezas** — o que ainda não sabemos que pode mudar o corte (candidatos a spike)?
8. **Critério de pronto do épico** — como saberemos que o épico acabou (e não vira um saco sem fundo)?
9. **Dados** — este épico cria ou transforma um ativo de dados que merece PBI próprio, não só um efeito colateral de outro PBI? Considere: o modelo/schema do dado evolui e é visível pra quem consome (não é só uma tabela interna)? Existe qualidade/validação do dado como preocupação de negócio (dado ruim precisa ser filtrado/sinalizado, não só armazenado)? Existe retenção/expiração/ciclo de vida que precisa de decisão explícita (nunca deixe isso cair em "fora de escopo" sem registrar onde essa decisão vai ser tomada)? A métrica-alvo do item 1 precisa de uma capacidade própria de medição/relatório porque alguém toma uma decisão a partir dela, ou já existe uma ferramenta/dashboard que cobre isso? **Não é** "criar a tabela X" (isso é task, ver anti-padrão em `regras-fatiamento.md`) — é comportamento observável sobre o dado.

Registre as respostas num resumo curto — ele vira o `README.md` do diretório `docs/pbis/<epico>/` e o contexto compartilhado de todos os PBIs.
