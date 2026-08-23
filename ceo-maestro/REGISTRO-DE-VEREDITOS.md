# Registro de vereditos — Estrutura Final de Skills

> **Gerado em 2026-08-06.** Derivado dos pareceres em disco, não digitado.
> Receita no fim do arquivo.

## ⚠️ O que esta tabela é — e o que ela NÃO é

- **É** o veredito **vigente** de cada pacote, com a **data** em que foi medido e a **régua** que o
  produziu. Nada aqui é digitado à mão: sai dos `PARECERES.ndjson` e dos `PARECER.json`.
- **NÃO é** um retrato de hoje para todos. Alguns vereditos são de **2026-07-29** e nunca foram
  refeitos — a coluna *medido em* diz quais, e essa é a informação mais importante da tabela.
- **NÃO é** comparável com a nota do Catálogo. Régua diferente (inteira × fracionária), agregação
  diferente (MENOR × média/mediana) e objeto diferente (árvore de pacote × `SKILL.md`).
- **NÃO autoriza produção.** `PRODUCAO` exige `VALIDATED` (`minimum_score` 10), que **nunca**
  aconteceu nesta casa.

> Esta seção existe porque, em 2026-08-05, uma tabela de notas sem proveniência levou o CEO a
> concluir errado duas vezes sobre o estado do Catálogo. **Tabela de nota nasce com a receita ao
> lado, ou não nasce.**

## ✅ Aprovados — `ACEITO_USO_INTERNO`


| pacote | mín | medido em | régua |
|---|---:|---|---|
| `departamento-arquitetura-dados` | **7** | 2026-08-05 | mista: `C04` de 05/ago + cinco de 04/ago |
| `departamento-arquitetura-software` | **7** | 2026-08-05 | mista: `C04` de 05/ago + cinco de 04/ago |
| `departamento-auditoria-responsabilidades` | **7** | 2026-07-29 | oito critérios de 29/jul |
| `departamento-conteudo-marketing` | **7** | 2026-08-05 | mista: `C04` de 05/ago + cinco de 04/ago |
| `departamento-desenvolvimento` | **7** | 2026-08-05 | mista: `C04` de 05/ago + cinco de 04/ago |
| `departamento-design-ux-ui` | **7** | 2026-08-05 | mista: `C04` de 05/ago + cinco de 04/ago |
| `departamento-evolucao-skills` | **7** | 2026-07-29 | oito critérios de 29/jul |
| `departamento-inovacao-melhoria` | **7** | 2026-08-05 | mista: `C04` de 05/ago + cinco de 04/ago |
| `departamento-registros` | **7** | 2026-08-05 | mista: `C04` de 05/ago + cinco de 04/ago |
| `departamento-seguranca` | **7** | 2026-08-05 | mista: `C04` de 05/ago + cinco de 04/ago |

**10 de 15.**

## ☐ Não aprovados

### Travados em um ou dois critérios — `NAO_DISCRIMINADO`

| pacote | mín | trava em | medido em |
|---|---:|---|---|

### `REPROVED`

| pacote | mín | medido em |
|---|---:|---|
| `departamento-negocios` | **4** | 2026-08-06 |
| `ceo-maestro` | **5** | 2026-08-06 |
| `departamento-juizes` | **5** | 2026-08-06 |
| `departamento-qa-usabilidade` | **6** | 2026-08-05 |
| `diretor-de-lentes` | **6** | 2026-08-06 |

> **O núcleo de comando foi rejulgado em 2026-08-06, e os quatro reprovaram** — `departamento-negocios` 4, `ceo-maestro` 5, `departamento-juizes` 5, `diretor-de-lentes` 6.
> São `ceo-maestro`, `diretor-de-lentes`, `departamento-juizes` e `departamento-negocios`: os
> pacotes que **julgam, roteiam e decidem** nesta casa. Medidos pela régua que aplicam nos outros,
> **nenhum alcança o próprio nível mínimo**.
>
> Contra 2026-07-29: `ceo-maestro` 1→5, `diretor-de-lentes` 1→6, `departamento-juizes` 2→5 subiram
> sem atravessar o corte; `departamento-negocios` 5→4 **desceu** — e é o único dos quatro que não
> recebeu trabalho entre as duas medições.
>
> Veredito, achados e caminho em
> [`evals/nucleo-de-comando-2026-08-05/03-VEREDITO.md`](evals/nucleo-de-comando-2026-08-05/03-VEREDITO.md).
>
> **Incômodo declarado, não escondido:** os dez aprovados acima foram medidos por lentes que são
> agentes do `departamento-juizes`, que está reprovado. O `C05` = 5 dele é sobre **rota não
> percorrida** — o CEO despachou fora do protocolo —, não sobre juízo mal formado. Mas a frase
> "a nota dos dez foi produzida por um pacote reprovado" é verdadeira e fica registrada.

## Detalhe por critério — os treze remedidos


| pacote | C01 | C02 | C03 | C04 | C05 | C06 | mín | veredito | medido em |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `ceo-maestro` | 6 | 7 | 6 | 5 | 5 | 7 | **5** | REPROVED | 2026-08-06 |
| `departamento-juizes` | 7 | 7 | 6 | 6 | 5 | 7 | **5** | REPROVED | 2026-08-06 |
| `departamento-negocios` | 6 | 8 | 5 | 4 | 4 | 6 | **4** | REPROVED | 2026-08-06 |
| `diretor-de-lentes` | 8 | 9 | 7 | 6 | 7 | 7 | **6** | REPROVED | 2026-08-06 |
| `departamento-arquitetura-dados` | 8 | 8 | 7 | 7 | 7 | 7 | **7** | ACEITO_USO_INTERNO | 2026-08-05 |
| `departamento-arquitetura-software` | 9 | 9 | 7 | 7 | 7 | 8 | **7** | ACEITO_USO_INTERNO | 2026-08-05 |
| `departamento-conteudo-marketing` | 8 | 8 | 7 | 7 | 7 | 7 | **7** | ACEITO_USO_INTERNO | 2026-08-05 |
| `departamento-desenvolvimento` | 9 | 8 | 7 | 7 | 7 | 7 | **7** | ACEITO_USO_INTERNO | 2026-08-05 |
| `departamento-design-ux-ui` | 9 | 8 | 7 | 7 | 7 | 8 | **7** | ACEITO_USO_INTERNO | 2026-08-05 |
| `departamento-inovacao-melhoria` | 7 | 9 | 7 | 7 | 8 | 9 | **7** | ACEITO_USO_INTERNO | 2026-08-05 |
| `departamento-qa-usabilidade` | 8 | 9 | 6 | 7 | 8 | 7 | **6** | REPROVED | 2026-08-05 |
| `departamento-registros` | 9 | 9 | 7 | 7 | 7 | 9 | **7** | ACEITO_USO_INTERNO | 2026-08-05 |
| `departamento-seguranca` | 9 | 9 | 8 | 7 | 8 | 9 | **7** | ACEITO_USO_INTERNO | 2026-08-05 |

## Receita

- **Fonte do núcleo de comando (06/ago):** `nucleo-de-comando-2026-08-05/01-AGREGADO.json`, derivado
  dos 8 `PARECER.json` em `pareceres/<lente>/i{1,2}/` — 3 lentes × 2 instâncias + painel externo × 2,
  worktrees isolados, cobertura 24/24 conferida antes de agregar.
- **Fonte dos nove:** `julgamento-nove-departamentos-2026-08-04/julgamento/<lente>/i{1,2}/PARECERES.ndjson`
  (cinco critérios, 04/ago) + `rejulgamento-c04/pareceres-recoleta/i{1,2}/PARECER.json` (`C04`, 05/ago).
- **Fonte dos demais:** `julgamento-pacotes-2026-07-29/08-RESUMO.md`, scorecard consolidado.
- **Agregação:** MENOR entre as duas instâncias por critério; MENOR entre critérios; faixa que cruza
  o corte 7 vira `NAO_DISCRIMINADO` **apenas quando pode decidir** — havendo critério acordado abaixo
  do corte, há dominância e o veredito é o da banda (`ADR-016` + precedente `qa-usabilidade`, 05/ago).
- **Bandas:** 10 → `VALIDATED` · 7–9 → `ACEITO_USO_INTERNO` · ≤6 → `REPROVED` (`ADR-014`).
- **Critério de população:** os 15 pacotes com `evals/validate_workflow.py` próprio. Os 66
  agentes-folha não têm validador e não são julgados isoladamente — a unidade é o departamento.

**Gerado por script a partir dos artefatos.** Para regenerar, rode o gerador do CEO sobre a árvore;
qualquer divergência entre esta tabela e os pareceres é defeito desta tabela.
