# Adendo de contagem — `departamento-negocios`, 2026-08-23

> **Por que este arquivo existe.** O [`PLACAR.md`](PLACAR.md) declara números corretos **na data em
> que foram medidos**, e este adendo **não altera nenhum deles**. A receita devolve outro número
> hoje porque a tarefa 105 acrescentou dois casos a este pacote. Redeclarar ao lado, por adendo
> datado e **no mesmo ato** que muda a contagem, é o que esta casa aprendeu depois que uma
> canonização somou 47 casos em 15 validadores e redeclarou em 1.

## A contagem vigente

| medição | resultado |
|---|---|
| vigente em 2026-08-22 | 238/238 |
| **vigente em 2026-08-23, após a tarefa 105** | **242/242** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro/departamento-negocios"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## O delta: 238 → 242 é +4, e só dois deles eu escrevi

**Dois vêm da auto-exigência, e dois vêm deste arquivo.** As travas de documentação deste pacote
geram um caso por arquivo — `sem placeholder:` e `link resolve:` —, e um adendo novo é um arquivo
novo. Registro o detalhe porque ele me custou um reselo: escrevi o adendo **depois** de rodar o
`selar_contagem.py`, o número selado saiu 240 contra os 242 vivos, e o selo teve de ser refeito.
Adendo entra **antes** do reselo.

| caso | o que ele exige |
|---|---|
| o validador do CEO exerce a varredura de limite residual (T105) | que `validate_limite_residual_tem_dono` seja chamada no `run()` do CEO **e** que o retorno alimente um caso — por AST, não por substring |
| a guarda viva do limite residual segue na barreira do CEO (T105) | que `achar_limite_sem_dono` continue dentro de `validate_governance_report`, onde quem chama a barreira direto passa |

## Por que estes dois casos moram AQUI, e não no validador do CEO

A prova de mutação da tarefa 105 mediu o buraco em vez de supô-lo. Removida a chamada da varredura
do `run()` do CEO, a bateria dele caía **apenas** no caso do selo de digest — o mesmo caso que
*qualquer* edição naquele arquivo derruba. Nada nomeava a varredura ausente, e um reselo devolveria
o verde com a trava fora do fluxo. O mutante ficou classificado como **INCONCLUSIVO**, não como
morto.

É `gate-que-nao-se-autoexige-erode` pela quarta vez nesta casa — as três anteriores foram as tarefas
27, 66 e 103 —, e o remédio é o mesmo: **o vigia não mora no arquivo que vigia**, senão sai junto na
mesma edição. Este pacote já lia `CEO_VALIDATOR_PATH` e já roda a regressão do CEO como subprocesso;
era o terceiro que a tarefa tinha à mão.

Com os dois casos instalados, o mesmo mutante passa a morrer por acusação **nomeada**:

```
[FAIL] o validador do CEO exerce a varredura de limite residual (T105):
       a chamada de validate_limite_residual_tem_dono sumiu do run() do CEO,
       ou o retorno dela deixou de alimentar um caso.
```

## Limite declarado deste par

`_chamada_alimenta_caso` decide por AST que o retorno vira argumento de um `.append` — é o terceiro
degrau da progressão desta casa (trava sem call site → call site por nome → chamada sem efeito).
Ela **não** distingue `cases.append` de outro `.append` qualquer, e ligação dinâmica continua
invisível para a AST, como já é teto declarado em `validate_trava_de_digest`. Preferimos a lacuna
nomeada à cobertura falsa.
