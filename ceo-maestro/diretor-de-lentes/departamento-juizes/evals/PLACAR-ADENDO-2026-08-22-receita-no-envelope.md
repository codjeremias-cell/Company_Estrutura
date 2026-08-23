# Adendo de contagem — `departamento-juizes`, 2026-08-22

> **Por que este arquivo existe.** O [`PLACAR.md`](PLACAR.md) declara um número correto **na data
> em que foi medido**, e este adendo **não o altera**. A receita devolve outro número hoje porque a
> tarefa 66 acrescentou dois casos. Redeclarar ao lado, por adendo datado e **no mesmo ato** que
> muda a contagem, é o que esta casa aprendeu depois que uma canonização somou 47 casos em 15
> validadores e redeclarou em 1 — a deriva derrubou o `C04` de oito pacotes na rodada seguinte.

## A contagem vigente

| medição | resultado |
|---|---|
| vigente em 2026-08-20 | 172/172 |
| **vigente em 2026-08-22, após a tarefa 66** | **174/174** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/departamento-juizes"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

O `ceo-maestro` também se moveu — **154 → 155** —, e o caso que entrou lá é a auto-exigência
desta trava. O adendo dele é
[`PLACAR-ADENDO-2026-08-22-contagem-do-validador.md`](../../../evals/PLACAR-ADENDO-2026-08-22-contagem-do-validador.md).

## O delta: 172 → 174 é +2

| origem | casos | o que exercita |
|---|---:|---|
| base vigente em 2026-08-20 | 172 | a casa estava sem FAIL |
| tarefa 66 — a trava | **+1** | todo `custody_copy` gravado carrega a receita, salvo dívida nomeada |
| tarefa 66 — a catraca | **+1** | a comparação sabe reprovar nos **dois** sentidos |
| **total vigente** | **174** | |

## O que a tarefa 66 conserta, e por que não pelo caminho que ela previa

A tarefa 42 canonizou a receita do digest no schema. **No dia seguinte**, um juiz real gastou
**oito tentativas** adivinhando o digest de uma designação — porque o envelope que ele recebeu não
a trazia. Na véspera, três juízes tinham gastado **16, 438 e 1440**, e um não conseguira.

A lição é um degrau que `aviso-em-prosa-nao-previne-erro` não cobria: a receita estava normativa,
acessível e **ausente de onde importava**. **Quem lê o envelope não lê o schema.**

### A hipótese registrada em 2026-08-08 estava errada, e o experimento diz por quê

O `estado.json` registrava: *"tornar `digest_recipe` OBRIGATÓRIO no `$defs/custodyCopy` para
envelope novo, sem invalidar as 53 instâncias congeladas — provavelmente uma trava no emissor, não
no schema"*. O medo era o custo sobre o registro congelado.

Medido por experimento em 2026-08-22, com baseline verde e restauração conferida por SHA-256: pôr
`digest_recipe` em `$defs/custodyCopy.required` derruba **dezesseis casos** — catorze aqui e dois
no CEO — e **nenhum deles é registro congelado**. São todos **fixtures** de envelope válido.

O achado que o experimento produziu é maior que a hipótese: os **52** `custody_copy` reais em disco
**não são validados por schema nenhum hoje**. A rota do schema custava dezesseis casos e **não
alcançava o artefato que o juiz efetivamente lê**. Fazer só isso repetiria a lição da própria
tarefa um degrau acima — o schema exigiria a receita, e nada conferiria se algum envelope real
cumpriu.

Por isso a trava varre o **disco**, reusando `_custodias_em_disco()` da tarefa 42, que já enumera
toda custódia real.

### A dívida histórica viaja nomeada

**52 ocorrências em 24 arquivos**, todas de campanhas de **2026-08-07 e 2026-08-08** — nenhuma
posterior à descoberta do defeito. É isso que torna o teto uma **dívida fechada**, não um
orçamento.

No molde da tarefa 94: cada arquivo com a sua contagem, o teto **derivado** da soma
(`TETO_CUSTODIA_SEM_RECEITA = sum(...)`, nunca digitado), e catraca nos **dois** sentidos —
ocorrência nova reprova, e dívida que encolheu reprova **pedindo para baixar o número no mesmo
ato**.

Reescrever os 52 seria falsificar registro. Escondê-los atrás de um inteiro solto seria a *chave de
limites regressível* que a tarefa 100 existe para consertar.

## Prova de mutação — 8 de 8

| mutação | efeito | causa que avermelhou |
|---|---|---|
| M1 | a regra "ocorrência nova reprova" é desligada | 172/174 — `ocorrência NOVA` |
| M2 | a catraca ao contrário é desligada | 172/174 — `baixar o teto` |
| M3 | uma entrada some da dívida | 172/174 — `ENVELOPE NOVO SEM RECEITA`, pela **árvore real** |
| M4 | entrada fantasma na dívida | 172/174 — `DÍVIDA ENCOLHEU`, pela **árvore real** |
| M5 | o varredor devolve vazio | 172/174 — `DÍVIDA ENCOLHEU` |
| M6 | o teste do campo some | 172/174 — `ENVELOPE NOVO SEM RECEITA` |
| M7 | a chamada sai do `run()` | **sobreviveu na 1ª rodada**; morto após o conserto — `RECEITA_NO_ENVELOPE_AUSENTE` |
| M8 | o próprio vigia fica cego | 153/155 no CEO — `RECEITA_NO_ENVELOPE_AUSENTE` |

Baseline **verde** antes de cada rodada, e os arquivos restaurados byte a byte, conferidos por
SHA-256.

**M3 e M4 são os que mais valem, e não por serem mais difíceis:** eles não passam pelo autoteste —
cobram a **árvore real**. São a prova de que a trava lê o disco em vez de conversar com as próprias
amostras, que é o defeito `teste-que-exercita-a-reimplementacao` desta casa. A função pura
(`_comparar_com_divida`) foi extraída **antes** de o autoteste ser escrito, e não depois: escrever
o autoteste primeiro fez esta casa reimplementar a comparação **três vezes num só dia**.

**As amostras do autoteste são sintéticas de propósito.** A árvore real está em dia com a dívida,
logo ela não contém nem o caso "nasceu uma nova" nem o caso "a dívida encolheu". Mutante que só a
árvore real exercita sobrevive — o padrão já custou quatro rodadas nesta casa.

### O M7 não ficou declarado: ficou consertado

Na primeira rodada, remover a chamada do `run()` devolvia **172/173 com zero FAIL fora do selo** —
nada nomeava a trava ausente, e só a contagem se movia. É `gate-que-nao-se-autoexige-erode` pela
**terceira vez nesta semana** (tarefas 55, 27, e esta).

A auto-exigência mora no validador do **CEO**, não no dos Juízes, e a escolha é medida:
`mute-a-trava-alheia-nao-a-sua` — vigia que vive no mesmo arquivo que vigia sai junto na mesma
edição. De lá, apagar a trava exige editar **dois pacotes** e saber que o segundo existe.

**M8 mediu o vigia contra si mesmo** e achou uma propriedade boa: cegá-lo **não** é rota de fuga —
ele passa a acusar, porque "não encontrei a chamada" e "a chamada não existe" são o mesmo estado.
Falha fechada.

## O que este adendo NÃO afirma

- **Não afirma nota nem veredito.** Nota é exclusiva do `departamento-juizes` como órgão, e este é
  um artefato de contagem.
- **Não afirma que envelope não gravado está coberto.** Limite declarado: a trava alcança envelope
  **em disco**. Envelope construído em memória e entregue sem passar pelo disco não passa por aqui
  — e a rota do schema, que alcançaria esse caso, foi medida acima como cara e cega ao caso real.
- **Não afirma que a mensagem do M8 nomeia o culpado certo.** Com o vigia cego, o erro acusa os
  Juízes quando o defeito é do vigia. Fecha na direção segura, e a imprecisão fica registrada.
- **Não reescreveu nenhum dos 52 registros congelados**, e a designação despachada em 2026-08-08
  continua preservada como registro.
