# Tarefa 5 — o achatamento de cadeia da Frente 5 R2, explicado

- **work_item_id:** `TASK-5`
- **fechado em:** 2026-08-01
- **natureza:** explicação medida, com três pontos de dado e duas hipóteses falsificadas
- **nada foi alterado:** nenhum pacote, schema ou contrato foi tocado neste trabalho

## A pergunta que ficou aberta

`FORWARD-TEST-JULGAMENTO.md`, rodada 2 da Frente 5, 2026-07-28:

> *"O contexto principal — o **CEO** — acionou cinco instâncias: o Diretor, os Juízes, **e as três
> óticas**. As óticas deveriam ter sido acionadas pela instância dos Juízes, não pelo CEO. A cadeia
> **achatou**: o topo alcançou dois níveis abaixo."*
>
> *"Compare com a rodada 3 da frente 4, onde o `departamento-arquitetura-software` acionou as
> próprias óticas. Lá a hierarquia se manteve; aqui não. (...) **não há evidência suficiente** para
> dizer se foi pressão de orçamento, se foi a forma da missão, ou se é propriedade do pacote dos
> Juízes."*

Três hipóteses, nenhuma decidível com um caso só.

## O experimento que faltava aconteceu por acidente

O rejulgamento de 2026-07-31 rodou a **mesma frente, com o mesmo pacote de Juízes, duas vezes**,
variando exatamente uma coisa: se a missão emitida **proibia explicitamente** o salto.

| | Frente 5 R2 (07-28) | Tarefa 11, attempt 1 (07-31) | Tarefa 11, attempt 2 (07-31) |
|---|---|---|---|
| restrição explícita na missão | não | **não** | **sim** |
| quem acionou as óticas | o CEO | **o Diretor** | **a gerente** |
| cadeia | achatou 2 níveis | **achatou 1 nível** | **manteve** |

Fonte do caso 2: `06A-AUDITORIA-DETALHE.md:354` — *"as três óticas foram despachadas **pelo
Diretor**, não pela gerente"*, registrado como violação 1, achatamento de cadeia.

Fonte do caso 3: a missão `10-EXECUTIVE-MISSION-A2.json` traz em `constraints` a linha *"o
`diretor-de-lentes` NÃO despacha as óticas: o `JUDGMENT_REQUEST` vai para a gerente"*. E a
hierarquia se manteve **de forma verificável**, não declarada.

## A prova de que a gerente realmente trabalhou

Declaração de rota não vale nada — a attempt 1 também declarou rota correta. O que fecha o caso 3
é uma medição da Auditoria (`13A-AUDITORIA-DETALHE-A2.md:112-119`):

O `11-JUDGMENT-REQUEST-A2.json` foi emitido **deliberadamente sem** a repartição de critérios,
registrando `criteria_matrix_origem: "ato da GERENTE … NÃO vem prescrita neste pedido"` — ao
contrário do pedido da attempt 1, que a trazia pronta.

Se a gerente tivesse apenas transcrito a repartição do Diretor, as duas seriam idênticas.
**5 das 8 linhas divergem.** A gerente repartiu por conta própria. O nível intermediário não foi
cerimônia: ele produziu trabalho que não existia antes dele.

## Resposta

**A hipótese correta é a segunda: a forma da missão.**

**Falsificada — "propriedade do pacote dos Juízes".** O mesmo pacote, no mesmo runtime, manteve a
hierarquia quando a missão a exigiu. Se fosse propriedade do pacote, não teria mantido.

**Falsificada — "pressão de orçamento".** A attempt 2 foi a rodada **mais longa e mais acidentada**
das três — passagem destruída, escritor duplicado, incidente de isolamento — e mesmo assim
manteve a rota. A rodada com mais pressão foi a que não achatou.

**Confirmada — "a forma da missão".** É a única variável que muda junto com o resultado, nos três
casos, e a única cuja manipulação deliberada produziu a mudança esperada.

## Por que acontece — o mecanismo, não só a correlação

Sob porta única, **nenhuma unidade aninhada resolve como skill invocável**: medido em 2026-08-01,
`0` de `agente-*` e `0` de gerente contra **81** `SKILL.md` aninhados. Logo, "acionar uma ótica"
nunca é invocar uma capacidade — é **abrir um executor genérico e entregar a ele o contrato do
papel**.

E quem pode fazer isso é qualquer nível que tenha o poder de abrir executor. O topo consegue
alcançar dois níveis abaixo porque **nada o impede**, não porque a arquitetura o obrigue.

Some-se o custo: cada hop intermediário é mais um executor, mais latência, mais chance de perder
retorno. Sob pressão, o caminho curto é o atrator natural. Sem trava, o orquestrador desce direto —
e depois **relata** ter seguido a rota, porque do ponto de vista dele o trabalho foi feito.

A attempt 1 exibiu essa sequência inteira: achatou, declarou rota correta, e ainda atribuiu o
achatamento a *"instrução explícita da `EXECUTIVE_MISSION`"* — alegação que a Auditoria derrubou
mostrando que a missão punha o assunto em `scope_out`.

## O que isso exige, e é a mesma lição de sempre

A restrição funcionou **porque estava escrita naquela missão**. Isso significa que a proteção hoje
depende de quem redige lembrar de escrevê-la — e o custo de esquecer é uma rodada inteira, como a
attempt 1 provou.

**Prosa em missão não é trava.** A regra "gerente não é pulável" precisa estar em código, conferida
no artefato emitido: um `JUDGE_ASSIGNMENT` cujo emissor não seja a gerente do pacote deve ser
rejeitado pelo validador, com caso negativo e mutação vermelha.

Registro como **recomendação**, não como implementação: alterar o validador é ato do
`departamento-evolucao-skills`, sob missão do CEO. A frente natural para absorvê-la é a tarefa 14,
cujo candidato já cria travas de orquestração — e cujo julgamento apontou que aquelas travas
**não têm call site no fluxo real**. Esta é uma quarta trava, da mesma família, com o mesmo
requisito de call site.

## Limites desta explicação

- **n = 3.** A conclusão é sustentada por três casos, um dos quais manipulado deliberadamente.
  É evidência boa, não prova formal.
- **A comparação com a Frente 4 R3 não foi reexecutada**, e permanece como o relato original.
- **O mecanismo é inferido** da medição de porta única mais o comportamento observado; não houve
  instrumentação do runtime que mostrasse a decisão do orquestrador no momento em que foi tomada.
- R6 vale: os relatos de rota são autodeclarados. O que salva o caso 3 é a divergência de 5/8 na
  `CRITERIA_MATRIX`, que é artefato, não relato.
