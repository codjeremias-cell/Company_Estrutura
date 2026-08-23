# Adendo de contagem — `ceo-maestro`, 2026-08-06

> **Por que este arquivo existe.** O [`PLACAR.md`](PLACAR.md) ao lado declara `33/33` e `55/55`,
> números corretos **nas datas em que foram medidos** e que este adendo **não altera**. A receita
> devolve outro número hoje. Redeclarar ao lado, por adendo datado, é o que esta casa aprendeu
> depois que uma canonização somou 47 casos em 15 validadores e redeclarou em 1 — a deriva derrubou
> o `C04` de oito pacotes na rodada seguinte.

## A contagem vigente

| medição | resultado |
|---|---|
| **vigente em 2026-08-06** | **107/107** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

O sumário próprio deste pacote é a linha `Resultado: n/m casos passaram.` — **a última do stream**,
porque este validador **não sub-executa vizinhos**. (O `departamento-negocios` sub-executa, e por
isso a mesma regra aplicada lá colhe o número do vizinho. Está registrado na tarefa 33.)

## O `1 FAIL`, nomeado

`série global de ADR é única em toda a estrutura` — acusa o **ADR-020 duplicado** por duas cópias
de laboratório de outra frente, em `evals/producao-honesta-2026-08-04/origem-independente-R1/lab/`.

**Não é defeito deste pacote**, é a tarefa 24 do estado. Ele aparece em **todos** os 15 validadores
pelo mesmo motivo, e nenhuma rodada de julgamento o creditou a pacote nenhum.

## O delta desta data: `+11` casos, em três frentes

`55/55` (a última medição no `PLACAR.md`) → `95/96` (medido em 05/ago) → **`106/107`** hoje.
O `+11` de hoje: **5 da tarefa 32**, **5 da tarefa 33** e **1 da tarefa 34**.

### Tarefa 33 — o instrumento de medição entra na suíte

Cinco casos que reexecutam o **coletor de saída crua** a cada rodada. Existem porque, nesta mesma
data, o CEO publicou a oito juízes uma evidência com **quatro defeitos, todos do coletor e nenhum
do objeto medido** — e os juízes acharam os quatro, o CEO nenhum:

| caso | o defeito que ele impede de voltar |
|---|---|
| `coletor colhe o sumário PRÓPRIO, não o do vizinho ecoado` | a receita *"sumário = último da saída"* publicou o `99/100` do Diretor como sendo de Negócios |
| `coerência interna é gate: 3 FAIL não convive com 99/100` | o `00-RESUMO.json` publicou os dois lado a lado; `99/100` implica 1 falha |
| `coerência interna não acusa número correto` | prova que o gate não é um "sempre vermelho" |
| `ambiguidade de sumário vira estado nomeado, nunca palpite` | dois sumários no mesmo dialeto viram `AMBIGUO`, não chute |
| `mojibake na saída capturada é detectado` | `PYTHONIOENCODING` no filho sem `encoding="utf-8"` no pai corrompeu todos os acentos das quatro saídas |

O quarto defeito — inventário listando **quatro** subordinados diretos onde o contrato diz **três**,
incluindo o `departamento-juizes` que o `SKILL.md:49` proíbe o CEO de chamar — virou conferência
dentro do próprio coletor, contra `SUBORDINADOS_ESPERADOS`.

**Prova de mutação do coletor:** restaurando a regra antiga, o `departamento-negocios` volta a
devolver `99/100` (do vizinho) em vez de `230/233` (o próprio); o gate de coerência pega a
autocontradição; a saída corrompida é detectada; e a expectativa errada de inventário é acusada.

### Tarefa 32 — a trava de despacho

Os outros cinco fazem reprovar a rodada de julgamento que nasce sem `JUDGE_ASSIGNMENT`:

| caso | o que trava |
|---|---|
| `nenhuma rodada de julgamento nova sem JUDGE_ASSIGNMENT` | o cheque real, derivado do disco |
| `armadilha 1 — citar JUDGE_ASSIGNMENT em prosa não é ter sido designado` | mutação congelada |
| `armadilha 2 — EXECUTIVE_MISSION não substitui JUDGE_ASSIGNMENT` | mutação congelada |
| `armadilha 3 — citar assignment_id não prova designação` | mutação congelada |
| `designação real é reconhecida` | prova que a trava não reprova quem cumpriu |

**As três armadilhas não são hipóteses.** São as três versões erradas do meu próprio classificador,
medidas em 2026-08-06 e congeladas para não voltarem:

1. `grep "JUDGE_ASSIGNMENT"` daria **verde** à rodada que mais furou o protocolo — ela cita a
   palavra 14 vezes, **todas denunciando a própria ausência**.
2. `EXECUTIVE_MISSION` foi aceita como prova. É envelope de CEO→executivo, não de gerente→juiz.
3. O par `assignment_id`+`write_path` veio do **exemplo** do protocolo, não da forma real do
   artefato — a `JUDGE_ASSIGNMENT` de verdade não tem `write_path`, e exigi-lo **reprovava rodadas
   conformes**.

## Prova de mutação — quatro, todas vermelhas quando deviam

| mutação | esperado | resultado |
|---|---|---|
| classificador sempre `COMPLIANT` | as 3 armadilhas ficam vermelhas | **3 de 3** |
| classificador sempre `BYPASS` | `designação real` e o cheque de disco ficam vermelhos | **2 de 2** |
| aparece **rodada nova** em bypass | o cheque de disco fica vermelho | **pegou** |
| entrada **fantasma** na exceção histórica | erro nomeado | **pegou** |

E a mesma rodada nova, **com** a designação, libera — a trava não é um "sempre vermelho".

## O que esta trava NÃO faz — limite declarado

Forjar um JSON com `artifact_type: "JUDGE_ASSIGNMENT"` é trivial. **A trava não torna o bypass
impossível; torna-o visível e deliberado.** É o mesmo teto `OI-04` já nomeado nesta casa: forjar a
evidência é chamar as mesmas funções que a verificam.

E ela **não corrige as sete rodadas históricas** que julgaram sem designação — essas ficam pinadas
como exceção datada em `BYPASS_HISTORICO_2026_08_06`, uma lista que **só pode encolher**. Rodada
nova em bypass reprova, porque não está lá.

## Adendo do mesmo dia — tarefa 24 fechada

As duas cópias de `adr-020` em `origem-independente-R1/lab/mech/{A,B}/` ganharam o sufixo
`.md.candidate`, que **já era o precedente da casa** (quatro cópias em `evolucao-skills` o usam).
Elas colidiam entre si e produziam **um FAIL em cada um dos quinze validadores**.

**Efeito na cadeia: 18 FAIL → 1.** Os 15 da série de ADR saíram, e com eles os **2 do
`departamento-negocios`**, que eram cascata: ele sub-executa o CEO e o Diretor, e o exit code sujo
deles virava FAIL próprio.

**A trava não foi tocada.** Conferido por mutação: colisão nova plantada → vermelho; removida →
verde. Os arquivos é que deixaram de se declarar decisões, que é o que sempre foram.

**Este pacote agora fecha em `107/107`.**
