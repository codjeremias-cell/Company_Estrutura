# Régua Interna de Avaliação de Negócios

## 1. Natureza

Esta régua mede prontidão interna. Não é a rubrica dos Juízes e não produz veredito final.

Ela permanece decimal por decisão explícita do
[ADR-014](../../diretor-de-lentes/departamento-juizes/references/adr-014-dois-niveis-de-veredito.md).
Não use `9,5` para interpretar `JUDGE_REPORT`: o gate externo usa nota inteira, `verdict` e
`required_level`.

Cada critério aplicável recebe score decimal de `0` a `10`, sem arredondamento. O resultado é:

```text
business_internal_minimum_score = min(score dos critérios aplicáveis)
```

`9.49` reprova; `9.50` passa. Média, mediana, pesos compensatórios e confiança não alteram o corte.

Os oito critérios aparecem sempre no scorecard, inclusive quando algum for `not_applicable`. Cada entrada carrega `source_report_refs` do agente proprietário. Sem relatório-fonte não há score.

## 2. Critérios

| ID | Critério | Evidência mínima | Frente primária |
|---|---|---|---|
| `BIZ-01` | Problema e cliente comprovados | dor/tarefa, segmento, fontes e lacunas | Mercado e Cliente |
| `BIZ-02` | Proposta de valor e diferenciação | alternativas, benefício, trade-offs e posição | Estratégia de Produto |
| `BIZ-03` | Escopo e requisitos verificáveis | MVP/Depois/Fora, aceite e não funcionais relevantes | Estratégia de Produto |
| `BIZ-04` | Mercado e concorrência | pesquisa datada, concorrentes/alternativas e saturação | Mercado e Cliente |
| `BIZ-05` | Aquisição, ativação e retenção | canal, hipótese, métrica, prazo e riscos editoriais | Mercado e Cliente |
| `BIZ-06` | Monetização e preço | modelo, disposição a pagar, cenários e justificativa | Viabilidade e Monetização |
| `BIZ-07` | Economia unitária e viabilidade | fórmulas, premissas, CAC/LTV/churn/payback/custos aplicáveis | Viabilidade e Monetização |
| `BIZ-08` | Riscos, alegações e limites | risco, mitigação, fonte de claims e guardrail regulatório | As três frentes |

## 3. Âncoras

- `10.0`: completo, rastreável, sem lacuna material; risco residual explicitado.
- `9.5–9.99`: atende integralmente ao critério; melhoria restante não altera decisão nem segurança.
- `8.0–9.49`: evidência ou coerência insuficiente; retrabalho obrigatório.
- `5.0–7.99`: lacuna material, premissa frágil ou risco sem tratamento.
- `0–4.99`: ausente, contraditório, fabricado, proibido ou não verificável.

Não atribua automaticamente `10`. Justifique a distância até o estado ideal.

## 4. Regras de evidência

- fato, hipótese, opinião e recomendação aparecem separados;
- número contém fórmula, premissas, período, unidade e fonte;
- dado sensível ao tempo inclui data de consulta;
- concorrentes e preços são reais quando alegados;
- pesquisa declara método, amostra, limitações e saturação conforme RO-15;
- afirmação de marketing tem origem e contexto;
- não existe promessa de retorno ou resultado garantido;
- questão financeira regulada exige profissional habilitado quando aplicável;
- `not_applicable` contém razão verificável e não oculta risco.

## 5. Tratamento obrigatório abaixo do corte

Para cada critério abaixo de `9.5`, registre:

```yaml
criterion_id: BIZ-00
score: 0.0
cause: "..."
evidence_refs: ["..."]
source_report_refs: ["report-..."]
impact: "..."
required_change: "..."
treatment_owner: "..."
retest_criterion: "..."
attempt: 1
```

Se a causa for técnica, Negócios expressa necessidade, restrição, custo e critério de aceite; o Diretor decide o encaminhamento técnico.

## 6. Integridade editorial e financeira

As práticas vindas das skills de riqueza são apenas guardrails:

- rigor numérico e cenários;
- diagnóstico antes de recomendação;
- plano em fases e atualização por diferença;
- fonte para estatística e alegação;
- nenhuma promessa garantida.

Não importar aconselhamento de patrimônio pessoal, coaching de riqueza ou recomendação individual de investimento.
