# Auditoria adversarial — Departamento de Inovação e Melhoria

## Estado

`EXECUTADA` — 2026-07-26, segunda rodada.

Instrumento: [`corpus_adversarial.py`](corpus_adversarial.py), executável.

```bash
PYTHONIOENCODING=utf-8 python evals/corpus_adversarial.py
```

## Rodada 1 — parecer independente (base)

Três auditorias independentes leram o pacote em modo somente leitura e
emitiram **REPROVADO PARA PROMOÇÃO**, sem P0.

| Frente | Resultado |
|---|---|
| governança e estrutura | reprovado — 8 bloqueadores normativos |
| schema e causalidade | **45 mutações, 39 escapes, 6 controles rejeitados** |
| contrato e não execução | 4 achados P1 e 4 P2 |

O diagnóstico central: o validador imprimia **59/59 PASS** e mesmo assim 39 de
45 mutações passavam. O schema tinha forma e quase nenhuma trava semântica, e
o validador não detectava as ausências normativas que a auditoria de
governança encontrava a olho.

## Rodada 2 — reexecução após as correções

Cada uma das 45 mutações da rodada 1 virou um caso executável, agrupado pelo
identificador do achado que a originou.

| Achado de origem | Mutações | Rejeitadas | Escapes |
|---|---:|---:|---:|
| P1-1 proveniência sem contexto confiável | 5 | 5 | 0 |
| P1-2 ponte sem reconciliação | 6 | 6 | 0 |
| P1-3 gates autoassertivos | 5 | 5 | 0 |
| P1-4 tecnologia sem PoC/reconciliação | 3 | 3 | 0 |
| P1-5 PDCA e prova externa sem envelope | 5 | 5 | 0 |
| P2-1 roster, assignment e capability gap | 4 | 4 | 0 |
| P2-2 saturação | 4 | 4 | 0 |
| P2-3 prioridade contra estado e gate | 2 | 2 | 0 |
| P2-4 recomendação de evolução | 2 | 2 | 0 |
| P2-5 julgamento e QA em texto livre | 4 | 4 | 0 |
| P2-6 `false == 0` em `test_summary` | 1 | 1 | 0 |
| C-P1-1 gerente fabrica análise | 1 | 1 | 0 |
| C-P1-2 assignment não preserva `mode` | 1 | 1 | 0 |
| C-P2-1 Evolução de Skills como destino direto | 1 | 1 | 0 |
| C-P2-2 Negócios sem autorização matricial | 1 | 1 | 0 |
| **Total** | **45** | **45** | **0** |

**Resultado: 45/45 rejeitadas; 0 escapes (P1=0, P2=0).**

Escapes de rodada 1 fechados: 39. Controles que já rejeitavam na rodada 1
continuam rejeitando: 6.

## Onde cada escape foi fechado

| Achado | Trava que passou a existir |
|---|---|
| P1-1 | contexto confiável derivado da `DEPARTMENT_MISSION` e autenticado por `department_mission_digest`/`plan_digest`/`assignment_digest` recalculados (`context_errors`, protocolo §2) |
| P1-2 | `chain_errors`: `accepted_*_refs` em `id@sha256:<digest>`, retorno ligado a assignment aceito, artefato/evidência/alegação/pendência com origem em retorno |
| P1-3 | `derive_gate_checks` recalcula o gate dos retornos; `blocking_pending_refs` obriga `BLOCKED`; alternativas com `uniqueItems` |
| P1-4 | `technology_errors`: `ADOPT` exige `evidence_reconciliation` executada, autenticada e `HYPOTHESIS_SUPPORTED` |
| P1-5 | `authenticatedEvidence` no schema — produtor externo enumerado, digest e `authorized_by: diretor-de-lentes` — mais `pdca_errors` |
| P2-1 | `contains {selected: true}` no roster; assignment só para agente selecionado; `if/then` capability↔agente no capability gap |
| P2-2 | `saturation_errors`: rodadas sequenciais, `opportunity_refs` do tamanho de `net_new_count`, partição sem repetição, união igual às `NEW` |
| P2-3 | `BLOCKED` se e somente se faixa `BLOCKED`; `NOW` exige gate completo |
| P2-4 | `evidence_refs` com `minItems: 1` e rota fixa terminando no CEO |
| P2-5 | `judgment_language_errors` varre todo texto de afirmação, isentando por nome os campos de declaração negativa |
| P2-6 | `type: integer` junto do `const: 0`, e checagem `isinstance(..., bool)` no Python |
| C-P1-1 | reconciliação retornos→relatório: a gerente não cita o que ninguém entregou |
| C-P1-2 | `mode` obrigatório em plano, assignment e retorno, conferido contra a missão |
| C-P2-1 | `departamento-evolucao-skills` removido de `recommended_recipient` e de `route`; rota de pedido fixada em dois saltos |
| C-P2-2 | `matrix_authorization` com `granted_by: ceo-maestro` exigida por `if/then` para o destino Negócios |

## O que esta auditoria **não** prova

Declarado aqui e não em prosa espalhada pelo pacote — os limites estruturais
estão em [`../references/protocolo-inovacao-melhoria.md`](../references/protocolo-inovacao-melhoria.md), §12.

1. **O corpus e o validador compartilham o motor.** `corpus_adversarial.py`
   importa `validate_workflow.py`. Ele prova que as travas fecham as **45
   mutações conhecidas**; não prova que não existe uma 46ª. Corresponde ao
   risco residual **R4**.
2. **Mutação conhecida não é adversário.** As 45 vieram de um parecer humano
   independente. Um leitor novo, com outro repertório, é a única forma de
   descobrir a classe que ninguém escreveu.
3. **Nada aqui prova comportamento em runtime.** O corpus valida artefatos e
   cadeias, não a decisão de um modelo carregando a skill. Essa camada é o
   [FORWARD-TEST.md](FORWARD-TEST.md), com o `SKIP` de ativação espontânea
   ainda aberto.
4. **A trava anti-julgamento é de vocabulário.** Julgamento afirmado em
   paráfrase, fora da lista de padrões, continua passando (**R7**).
5. **O gate derivado depende do insumo declarado pelo agente.** Ele impede a
   gerente de inventar o gate; não impede o agente de inventar o brief (**R4**).

## Próxima auditoria deve procurar

Bypass por invocação explícita; execução disfarçada de análise; nota, ranking
ou veredito em paráfrase que não casa com os padrões; saturação com escopo
declarado artificialmente estreito; `intake_basis` declarado na porta errada;
evidência externa com produtor plausível mas inexistente; divergência entre
relatório autenticado e `DEPARTMENT_RETURN`; e qualquer campo em que o
booleano declarado ainda não tenha derivação.
