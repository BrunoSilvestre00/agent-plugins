# Regras de fatiamento (épico → PBIs)

## Princípios

1. **Fatias verticais**: cada PBI atravessa a jornada e entrega comportamento observável fim-a-fim. Nunca fatie por camada ("PBI do backend", "PBI do frontend") — camada é task, e task é do `/speckit.tasks`.
2. **INVEST**: independente (dependências mínimas e explícitas), negociável, valioso, estimável, pequeno (cabe em 1 sprint), testável (dá para escrever Gherkin).
3. **Primeiro PBI = caminho mínimo**: a menor jornada fim-a-fim que já funciona (walking skeleton). Os demais incrementam.
4. **6 a 8 PBIs no máximo por épico**. Passou disso, provavelmente são dois épicos — diga isso ao usuário.
5. **Incerteza vira spike**, não PBI inchado: se algo impede escrever critérios de aceite, proponha um PBI de spike com entregável escrito (documento de decisão) e timebox.

## Padrões de corte (use o que se aplicar)

- **Por passo da jornada**: cadastrar → pagar → acompanhar → cancelar.
- **Por regra de negócio**: versão simples primeiro (à vista), variações depois (parcelado, cupom).
- **Por variação de entrada/plataforma**: um método de pagamento por PBI; web antes de mobile.
- **Por caso feliz vs. tratamento de erros**: fluxo principal primeiro, recuperações/estornos depois — desde que o caso feliz sozinho ainda seja aceitável em produção (atrás de flag, se preciso).
- **Por segmento de usuário**: cliente novo antes de migração da base.
- **Por qualidade incremental**: funcional primeiro, performance/escala como PBI próprio SÓ se houver critério mensurável.
- **Por ciclo de vida do dado**: quando o épico cria/acumula um ativo de dados (`checklist-epico.md`, item 9), o caminho mínimo cobre só a captura; qualidade/validação, retenção/expiração, e medição/relatório da métrica-alvo **só viram PBI próprio se aplicável a este épico** (mesmo teste do item 9: já existe ferramenta/dashboard/processo que cobre? então não é PBI novo) — cada um com comportamento observável (dado ruim é filtrado, dado velho expira, alguém que decide algo consegue consultar a métrica), nunca "fora de escopo" sem dono registrado em algum PBI ou item "fora deste épico". Quando não aplicável, absorva o critério na PBI de captura em vez de criar uma PBI só pra isso. Respeita o teto do princípio 4: se captura + as sub-dimensões aplicáveis passarem de 6–8 PBIs somado ao resto do corte, é sinal de que virou dois épicos, não motivo pra relaxar o teto. Diferente do anti-padrão "PBI de camada técnica" abaixo: não é "criar a tabela X", é o comportamento que o dado precisa ter — e "medição/relatório" em particular só é PBI se alguém toma uma decisão a partir dela (não "expor a métrica", que é o próprio "endpoint Y" do anti-padrão).

## Anti-padrões (rejeite e explique)

- PBI de camada técnica ("criar tabela X", "endpoint Y") — isso é task do Spec Kit.
- PBI "guarda-chuva" com mais de um objetivo de valor.
- PBI sem comportamento observável ("melhorar arquitetura") sem métrica.
- Cadeia longa de dependências (PBI 5 depende de 4 que depende de 3...) — reordene ou refatie.

## Apresentação da proposta (antes de detalhar)

```
Épico: <nome / chave Jira>
Proposta de fatiamento (N PBIs):
01. [Área] Título — valor em 1 frase. (depende de: —)
02. [Área] Título — valor em 1 frase. (depende de: 01)
...
Racional do corte: <2-3 frases: padrão usado e por quê>
Fora deste épico: <o que ficou de fora e onde vive>
```

A numeração vira o prefixo `NN-` dos arquivos em `docs/pbis/<epico>/`.
