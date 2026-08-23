# Adendo de contagem — `departamento-juizes`, 2026-08-08 (ADR-023)

> **Por que este arquivo existe.** O [`PLACAR.md`](PLACAR.md) e os adendos de 2026-08-06 e de
> 2026-08-08 declaram números corretos **nas datas em que foram medidos**, e este adendo **não
> altera nenhum deles**. A receita devolve outro número agora porque o ADR-023 acrescentou cinco
> casos. Redeclarar ao lado, por adendo datado e **no mesmo ato** que muda a contagem, é o que esta
> casa aprendeu depois que uma canonização somou 47 casos em 15 validadores e redeclarou em 1 — a
> deriva derrubou o C04 de oito pacotes na rodada seguinte.
>
> **Este é o segundo adendo de 2026-08-08.** O anterior (`...-contagem-do-validador.md`) fechou em
> 157 pela tarefa 42; este parte de 157 e vai a 162. Mesma data, atos diferentes.

## A contagem vigente

| medição | resultado |
|---|---|
| vigente em 2026-08-06 | 155/155 |
| vigente em 2026-08-08 (tarefa 42) | 157/157 |
| **vigente em 2026-08-08 (ADR-023)** | **162/162** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/departamento-juizes"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## De onde vêm os cinco

Todos de `trava_evidencia_simetrica`, que faz cumprir o
[ADR-023](../references/adr-023-evidencia-simetrica.md):

| caso | espera | o que prova |
|---|---|---|
| aceita rodada em que toda emissão carrega o mesmo digest | válido | o caminho feliz não é barrado |
| rejeita emissão sem `evidence_digest` quando a rodada declara simetria | rejeitado | a regra não fica só na regra |
| rejeita digest divergente entre emissões da mesma rodada | rejeitado | evidência assimétrica em flagrante |
| rejeita bateria que roda **depois** do despacho | rejeitado | bateria posterior é evidência de uma só |
| não exige nada de rodada que não declara simetria | válido | o silêncio para as congeladas é deliberado |

## Prova de mutação, executada nesta rodada

Desligar a trava — `return []` na primeira linha do corpo — derruba **exatamente os três casos
negativos** e deixa os dois positivos verdes:

```
162/162  com a trava
159/162  com a trava desligada
```

Os dois positivos permanecerem verdes é o resultado correto, não uma falha da prova: eles não
dependem de a trava disparar. Verde no positivo nunca provou trava nenhuma.

## Cadeia, com data

Medida em **2026-08-08**, após esta mudança: **2015/2015 em 16 pacotes, zero FAIL, zero quebrados**.
O delta contra a medição anterior de 2010 é **+5**, e é inteiro deste pacote — nenhum outro mudou.

Duas ressalvas de método sobre esse número, porque coletor não medido já enganou esta casa:

1. O contador só conta **validador de pacote** — pasta com `SKILL.md` e `CONTRATO-DE-COMPROMISSO.md`
   ao lado do `evals/`. A primeira versão varreu por glob e colheu mais de trinta cópias de
   laboratório dentro de pastas de evidência de campanha.
2. Convivem **dois formatos de sumário** na casa (`Resultado: N/N casos passaram.` e
   `RESULTADO: N/N PASS; 0 FAIL; 0 WARN`). A primeira versão só via o primeiro e marcou três pacotes
   como quebrados, o que teria publicado **1521** em vez de 2015.
