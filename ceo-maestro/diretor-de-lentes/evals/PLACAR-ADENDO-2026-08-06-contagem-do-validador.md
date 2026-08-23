# Adendo de contagem — `diretor-de-lentes`, 2026-08-06

> **Redeclaração no mesmo ato da mudança.** A tarefa 34 acrescentou **um caso** a cada um dos
> quinze validadores: a trava que impede um `PLACAR.md` de pacote de declarar o total da **cadeia**
> como estado corrente. Contagem que muda sem redeclarar é a deriva que, em 2026-08-05, derrubou o
> `C04` de oito pacotes na rodada seguinte. Aqui ela é redeclarada junto.

## Contagem vigente

| medição | resultado |
|---|---|
| Validador determinístico do Departamento | 101/101 PASS | **sim** |
| **vigente em 2026-08-06** | **101/101** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro/diretor-de-lentes"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## O delta desta data

`99/100` → **`100/101`**, isto é **+1 caso**:
`nenhum placar de pacote declara total de cadeia como estado corrente`.

**Por que a trava existe.** Em 2026-08-06 mediu-se que **11 dos 15** `PLACAR.md` diziam *"a cadeia
canônica **hoje** soma 1531/1531 PASS"* enquanto a rodada daquele dia tinha FAIL em quatro pacotes.
**Dois placares já haviam sido corrigidos** para o passado — e a correção **não propagou** para os
outros onze. Conserto em prosa, num arquivo, sem trava que force os demais.

O defeito é de **forma**, não de sítio: um número que só a cadeia inteira produz, afirmado no
presente, dentro de um documento que mede **um pacote**. Nenhum pacote consegue rodar os quinze
validadores, então nenhum pode saber o total de hoje. Citar no **passado, com data**, continua
legítimo — vira registro histórico.

O detector **se autotesta** antes de julgar: recusa passar se não pegar a forma proibida, e recusa
passar se acusar a forma permitida.



## Adendo do mesmo dia — tarefa 24 fechada

As duas cópias de `adr-020` em `origem-independente-R1/lab/mech/{A,B}/` ganharam o sufixo
`.md.candidate`, que **já era o precedente da casa** (quatro cópias em `evolucao-skills` o usam).
Elas colidiam entre si e produziam **um FAIL em cada um dos quinze validadores**.

**Efeito na cadeia: 18 FAIL → 1.** Os 15 da série de ADR saíram, e com eles os **2 do
`departamento-negocios`**, que eram cascata: ele sub-executa o CEO e o Diretor, e o exit code sujo
deles virava FAIL próprio.

**A trava não foi tocada.** Conferido por mutação: colisão nova plantada → vermelho; removida →
verde. Os arquivos é que deixaram de se declarar decisões, que é o que sempre foram.

**Este pacote agora fecha em `101/101`.**
