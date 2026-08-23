# Plano e missão — migração integral para o ADR-014

- **work_item_id:** `estado-tarefa-6`
- **missão:** `mission-adr014-2026-07-29`
- **autoridade de origem:** Jeremias — “ok, vamos seguir” / “podemos seguir”
- **dono executivo:** `diretor-de-lentes`
- **participação matricial:** `departamento-negocios`
- **gate independente:** `departamento-juizes`, somente pela rota do Diretor
- **nível exigido para esta mudança:** `PRODUCAO`
- **estado ao planejar:** `D_PLANNED`
- **decisão vinculante:** ADR-014, aceito por Jeremias em 2026-07-28

## INTENT

Fazer a cadeia inteira aplicar uma única regra externa de julgamento:

| `minimum_score` | `verdict` |
|---:|---|
| 10 | `VALIDATED` |
| 7–9 | `ACEITO_USO_INTERNO` |
| 0–6 | `REPROVED` |

`required_level: PRODUCAO` só é alcançado por `VALIDATED`.
`required_level: INTERNO` é alcançado por `VALIDATED` ou `ACEITO_USO_INTERNO`.
O nível nasce na `EXECUTIVE_MISSION`, é propagado sem alteração e volta ao fechamento.

## Escopo autorizado

1. Reconciliar as instruções vigentes da Estrutura (`AGENTS.md`, `ORGANOGRAMA.md` e guia).
2. Migrar CEO, Negócios, Diretor e Juízes em `SKILL.md`, contratos, referências e metadata.
3. Migrar os schemas e validadores determinísticos dos quatro pacotes.
4. Preservar a régua **interna e decimal** de Negócios em 9,5; somente o veredito externo cruza
   a fronteira.
5. Remover qualquer rota direta Negócios → Juízes; o Diretor é o único emissor e destinatário do
   julgamento.
6. Preservar registros históricos e seus digests; anexar nova medição em vez de reescrevê-los.
7. Implantar somente a partir da fonte de verdade nos runtimes Claude e Codex.

## Fora de escopo

- rejulgar os sete pacotes reprovados;
- corrigir as não conformidades próprias das tarefas 7, 8 e 9;
- produzir prova de nível produção para os sete pacotes aceitos internamente;
- alterar a decisão do ADR-014 ou a régua decimal interna de Negócios.

## Definition of Done

- `required_level` é obrigatório na missão, pedido, parecer, envelopes matriciais aplicáveis e
  decisão;
- todos os relatórios externos usam notas inteiras;
- fronteiras 6, 7, 9 e 10 passam nos níveis `INTERNO` e `PRODUCAO`;
- nota fracionária externa, nível ausente ou divergente e
  `ACEITO_USO_INTERNO + PRODUCAO` falham;
- falha crítica, cobertura ausente ou pendência bloqueante força `REPROVED`;
- nenhuma norma operacional vigente mantém o corte binário 9,5;
- os quatro validadores passam, a cadeia dos 15 pacotes passa e o delta de casos é explicado;
- os dois runtimes ficam idênticos à fonte;
- a Auditoria emite veredito explícito com evidência fresca.

## Baseline e hipótese de melhoria

**Baseline:** a última árvore medida fechou em **1532/1532**, mas os validadores atuais podem
ficar verdes enquanto schema e fixture discordam; `EXECUTIVE_MISSION` não exige
`required_level`; há consumidor binário de 9,5 nos quatro pacotes e a instrução hierárquica raiz
ainda ordena o corte antigo. Portanto, 1532 é referência de contagem, não prova do ADR-014.

**Hipótese falsificável:** se o nível exigido for um invariante causal e os validadores testarem a
semântica das fronteiras, então nenhuma combinação 6/7/9/10 poderá produzir veredito ou fechamento
incompatível nos dois níveis.

**Métrica:** zero caso incompatível aceito; 100% da matriz de oito combinações com resultado
esperado; 15/15 validadores sem `FAIL`/quebra; zero divergência fonte↔runtime.

**Rollback:** reverter o commit único desta migração; os registros históricos permanecem intactos
e os runtimes são regenerados da fonte anterior.

## RACI

| Frente | Responsável | Aprovador/fechamento | Consultado | Evidência |
|---|---|---|---|---|
| contrato executivo e schemas | `ceo-maestro` | Jeremias | Diretor | regressão do CEO |
| propagação técnica | `diretor-de-lentes` | CEO | Negócios | regressão do Diretor |
| fronteira comercial | `departamento-negocios` | CEO | Diretor | regressão de Negócios |
| faixa e veredito | `departamento-juizes` | Diretor | três óticas | regressão dos Juízes |
| conformidade | Auditoria | — | todos | relatório final |

## Capacidades verificadas antes do acionamento

| Capacidade | SKILL SHA-256 | Contrato SHA-256 |
|---|---|---|
| `diretor-de-lentes` | `b82d38507e373372b8bfa6db5601bce76a6103fcfccae2cf4fe9d8417f5dded3` | `290b6608f1902003ea572234ac7332e2ba3d3ff9373c309158f9d75f498f6b67` |
| `departamento-negocios` | `30c8a12c678cff288b52276bba6e1aabee7f1933e652d504a94c569de1c7ec5e` | `7fd9f9100c6d3613eba8dec288e8a1430ed73079ad55d10790b5db5f388c8baf` |
| `departamento-juizes` | `d266b0898092440591dfcc7d6fe01f34bb98432b868fa3e3f2ffeebc0cf7316d` | `b7ab8b49d800fe46a2d21b4b8a546f52d467d834e8e2ac6dd335b1c4d36ad431` |

Regras de Ouro verificadas em
`e307c4e784cfa29525b038504bc7ea6c598087e2527c07e33d3897958197eff6`.
