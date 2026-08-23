# Adendo de contagem — `departamento-juizes`, 2026-08-08 (ADR-024)

> **Por que este arquivo existe.** O [`PLACAR.md`](PLACAR.md) e os adendos anteriores declaram
> números corretos **nas datas em que foram medidos**, e este adendo **não altera nenhum deles**. A
> receita devolve outro número agora porque o ADR-024 acrescentou sete casos. Redeclarar ao lado,
> por adendo datado e **no mesmo ato** que muda a contagem, é o que esta casa aprendeu depois que
> uma canonização somou 47 casos em 15 validadores e redeclarou em 1.
>
> **Terceiro adendo de 2026-08-08.** Mesma data, atos diferentes: tarefa 42 fechou em 157, o
> ADR-023 em 162, este em 169.

## A contagem vigente

| medição | resultado |
|---|---|
| vigente em 2026-08-06 | 155/155 |
| vigente em 2026-08-08 (tarefa 42) | 157/157 |
| vigente em 2026-08-08 (ADR-023) | 162/162 |
| **vigente em 2026-08-08 (ADR-024)** | **169/169** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/departamento-juizes"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## De onde vêm os sete

Todos de `trava_isolamento_por_runtime`, que faz cumprir o
[ADR-024](../references/adr-024-isolamento-por-runtime.md):

| caso | espera | o que prova |
|---|---|---|
| raízes disjuntas e `write_path` dentro da própria raiz | válido | o caminho feliz não é barrado |
| raízes aninhadas | rejeitado | **a trava 1 passa aqui e esta pega** — os `write_path` seguem exclusivos |
| `write_path` fora da própria raiz | rejeitado | escrever fora do isolamento o desfaz |
| `pasta-compartilhada` declarada | rejeitado | declarar a ausência é auditável e continua não isolando |
| isolamento parcial na rodada | rejeitado | parcial é a pasta compartilhada com nome melhor |
| rodada que não declara isolamento | válido | o silêncio para as congeladas é deliberado |
| `arena/i1` não contém `arena/i12` | válido | contenção é por segmento, nunca por prefixo de texto |

## Prova de mutação — duas, porque há duas decisões a provar

**M1, trava desligada** (`return []` na primeira linha do corpo): derruba **exatamente os quatro
casos negativos** e deixa os três positivos verdes.

```
169/169  com a trava
165/169  com a trava desligada
```

**M2, contenção por prefixo de texto** (`_dentro_de` trocado por `str.startswith`): derruba
**exatamente um** caso, o de `arena/i1` × `arena/i12`.

```
169/169  com comparação por segmento
168/169  com comparação por prefixo
```

A M2 é a que importa para não vender rigor barato: sem ela, a comparação por segmento seria uma
escolha de estilo sem nada provando que ela evita alguma coisa. Com ela, está medido que o prefixo
produziria um falso positivo — reprovar rodada correta, que é o defeito que já apareceu nesta casa
quando um gate acusou `"NÃO"` e `"DECLARAÇÃO"` de mojibake.

## Cadeia, com data

Medida em **2026-08-08**, após esta mudança: **2022/2022 em 16 pacotes, zero FAIL, zero quebrados**.
O delta contra 2015 é **+7**, inteiro deste pacote — nenhum outro mudou.
