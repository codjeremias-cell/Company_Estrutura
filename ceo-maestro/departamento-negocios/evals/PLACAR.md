# Placar de Validação — Departamento de Negócios

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 246/246 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:d00104430ea764831d784278ad1a3014f872203af9f08662e3084c8ba54648a5` | medido-em: 2026-09-02
<!-- /SELO-DE-CONTAGEM -->

## Passagem pelo gate

Este pacote foi submetido ao gate em 2026-07-29. Opiniões, notas, veredito e
histórico vivem fora do candidato, no
[resultado consolidado](../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md),
para não contaminar uma rodada futura com o próprio julgamento.

> **Reteste ADR-014 — 2026-07-29.** A migração do consumidor externo fechou em
> **226/226 PASS, 0 FAIL, 0 WARN**. O delta de **+56** sobre o baseline próprio `170/170` é
> composto por **+52 checks semânticos** — travas de `required_level`, propagação nos três
> envelopes, matriz `6/7/9/10 × INTERNO/PRODUCAO`, nota externa inteira, faixas de veredito,
> falha crítica/pendência bloqueante e integração atualizada com CEO e Diretor — e **+4 checks
> dinâmicos de links** ao ADR-014. A régua decimal interna
> `9,5`/`9,7` foi preservada; nenhum gate externo usa esse corte. O restante deste placar é
> registro histórico da rodada de 2026-07-26.

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **170/170 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. Naquela medição, a cadeia canônica somava **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

- **Data:** 2026-07-26
- **Pacote:** `departamento-negocios` + três agentes
- **Corte interno:** menor nota aplicável `>= 9.5`, sem média ou arredondamento

## Resultado final

| Gate | Resultado |
|---|---:|
| Validador determinístico do pacote | **170/170 PASS** |
| Forward comportamental combinado | **15/15 casos · 62/62 assertions** |
| Formato oficial das quatro skills | **4/4 PASS** |
| Regressão CEO Maestro | **32/32 PASS** |
| Regressão Diretor de Lentes | **49/49 PASS** |
| Regressão Departamento de Juízes | **61/61 PASS** |
| Falhas ou advertências abertas | **0** |

## Baseline comportamental pré-skill

Um agente sem acesso à implementação respondeu aos 15 casos de `evals.json`.

- Casos: **2 PASS · 11 PARCIAL · 2 FAIL**
- Assertions: **34/62 atendidas · 14 parciais · 14 falharam**

Lacunas predominantes:

- identidade e três agentes canônicos;
- `EXECUTIVE_MISSION`;
- missões e relatórios assinados;
- dissensos;
- mensagem matricial;
- retorno ao CEO sem matriz;
- lacuna formal de capacidade;
- separação entre score interno e `JUDGE_REPORT`;
- autoridade de exceção;
- `EXECUTIVE_SUBMISSION` correlacionada.

## Forward pós-skill

O primeiro ensaio produziu **13 PASS · 2 PARCIAL · 0 FAIL**. As duas omissões foram incorporadas ao formato mínimo de resposta e repetidas de modo focal, com **2/2 casos e 9/9 assertions PASS**.

Cobertura final combinada:

- casos: **15/15 PASS**;
- assertions: **62/62 PASS**;
- ativação da skill: **15/15**.

Detalhes em [FORWARD-TEST.md](FORWARD-TEST.md).

## Validação determinística

O `validate_workflow.py` fechou **170/170 PASS, 0 FAIL, 0 WARN**.

A bateria prova:

- estrutura, metadata, links e contratos;
- oito critérios com propriedade única e cobertura completa;
- exatamente três agentes, missões e relatórios;
- produtor causal igual ao agente contratado;
- scorecard com relatório-fonte por critério;
- menor score sem média ou arredondamento;
- repasse obrigatório de todo score abaixo do corte ao Diretor pela matriz;
- correlação do pacote de julgamento com intake, plano, relatórios, consolidação e scorecard;
- IDs únicos e referências exatas entre intake, plano, atribuições, missões, relatórios, consolidação e scorecard;
- rejeição de relatório obsoleto, reinício da rodada global e causalidade sem o pai imediato;
- vínculo semântico do retrabalho com gap, agente, critérios, tentativa, mudança, reteste e contrato;
- evidência do scorecard obrigatoriamente presente no relatório proprietário do critério;
- rejeição de critérios duplicados ou conflitantes em findings, scores recomendados e relatório de limitação;
- `MATRIX_EXCHANGE_MESSAGE` aceita pelo schema e pela função semântica do Diretor;
- rota `LIMITATION_VERIFICATION` abaixo do corte;
- `LIMITATION_REPORT` de Negócios aceito pelo schema e pela semântica do CEO;
- rejeição de limitação baseada somente no score interno;
- `EXECUTIVE_SUBMISSION` de Negócios aceita pelo CEO;
- rejeição de submissão sem autoridade, com parecer vencido ou candidato divergente;
- ausência de fallback operacional.
- permissões `deny-by-default`, sem ampliar escopo, ferramentas, recursos ou efeitos externos.

## Validação oficial

O `quick_validate.py` do `skill-creator` aprovou:

- `departamento-negocios`;
- `agente-estrategia-de-produto`;
- `agente-mercado-e-cliente`;
- `agente-viabilidade-e-monetizacao`.

Resultado: **4/4 válidas**.

## Regressões externas

- CEO Maestro: **32/32 PASS**.
- Diretor de Lentes: **49/49 PASS**.
- Departamento de Juízes: **61/61 PASS**.

Nenhum arquivo compartilhado foi alterado por esta frente.

## Auditorias independentes

A auditoria de fidelidade às cinco fontes terminou em **PASS** após:

- corrigir `CAPABILITY_GAP` para `BUSINESS_CAPABILITY_GAP`;
- preservar finanças pessoais fora do runtime;
- declarar lacunas contábil, fiscal e jurídica;
- confirmar hashes e `fallback_used: false`.

A auditoria arquitetural encontrou e orientou correções de matriz causal, scorecard parcial, cobertura causal, referências forjadas e exceção inatingível. Todas foram incorporadas e possuem regressão executável. O parecer final de promoção é registrado após a rechecagem independente do pacote corrigido.
