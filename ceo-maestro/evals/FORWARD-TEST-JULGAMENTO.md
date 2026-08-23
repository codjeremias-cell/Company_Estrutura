# Forward test do gate — rota de julgamento

Frente 5 do [plano](../../PLANO-DE-ACAO-2026-07-27.md). Objetivo: **ao menos um pacote com
parecer emitido pela rota canônica**, para que a Estrutura deixe de estar formalmente não
julgada.

---

# Rodada 1 — 2026-07-27

Executor: sessão nova por `claude -p`, worktree isolado `Temp/f5r1`.
Candidato: `departamento-inovacao-melhoria` — 25 arquivos.
Orçamento: 25 min, 8 instâncias, profundidade 4. Fechou em **17,5 min**, US$ 5,39,
`exit=0`.

**Veredito: não há `JUDGE_REPORT`, não há nota — e o motivo é um erro do operador, não do
candidato nem do gate.**

## O que passou: a rota

O segundo objeto do teste funcionou inteiro.

- O **CEO** carregou, conferiu capacidades e emitiu **somente** `EXECUTIVE_MISSION` ao
  Diretor. Não pontuou, não arredondou, não falou com os Juízes.
- O **Diretor** derivou cinco critérios observáveis do contrato do próprio candidato —
  `C1-FIDELIDADE-CONTRATO`, `C2-BARREIRA-PROMOCAO`, `C3-BARREIRA-DEVOLUCAO`,
  `C4-RASTREABILIDADE-EVIDENCIA`, `C5-CADEIA-UNICA-E-FONTE-NORMATIVA` —, declarou o corte
  de `C6-ISOLAMENTO-DE-AGENTES` por orçamento, e emitiu `JUDGMENT_REQUEST`.
- Os **Juízes** percorreram a tabela de recebimento **antes** de abrir o candidato e
  devolveram `BLOCKED_CANDIDATE_MISMATCH`: nenhuma ótica acionada, nenhuma matriz de
  critérios montada, **nenhuma nota inventada para preencher relatório**.

O gate barrou na porta em vez de produzir número bonito. É exatamente o comportamento que
esta frente existia para provar — ainda que o motivo do bloqueio tenha sido meu.

## O que falhou: o digest que eu fixei

A missão fixou `candidate_tree_sha256: 3090cc80…cdc0dc`. Os Juízes tentaram três
convenções e nenhuma reproduziu o número.

| Item | Resultado |
|---|---|
| contagem de arquivos (25) | ✅ bate |
| `SKILL.md` sha256 | ✅ bate **exato** |
| `candidate_tree_sha256` | ❌ não reconcilia |

O `SKILL.md` bater prova que **não era o problema de fim de linha** — os bytes eram os
mesmos. Era a **composição**: eu calculei o digest de árvore com uma receita ad-hoc que
não existe escrita em lugar nenhum do cofre, e mandei conferir contra ela.

**É a repetição literal de uma lição que esta casa já tinha aprendido.** O `PLACAR.md` de
`departamento-registros`, de 2026-07-26, registra um digest de manifesto irreprodutível —
doze variantes testadas, nenhuma batendo — resolvido fixando **chave, comparador,
separador, terminador e codificação**. Eu li aquele documento nesta mesma sessão e repeti
o erro. *Número que ninguém consegue conferir não é evidência* valia para mim também.

## A ressalva que a rodada levantou, e que é decisão do Jeremias

O protocolo dos Juízes trata dois casos diferentes:

- digest **recomputado que diverge** do declarado → `BLOCKED_CANDIDATE_MISMATCH`;
- digest **não conferível** (convenção desconhecida) → `pending` declarado, reduz
  confiança, *"nunca uma conferência afirmada que não houve"*.

O caso era o segundo; os Juízes aplicaram o primeiro. Leitura defensável — mas significa
que, **enquanto não houvesse convenção de digest de árvore, nenhum dos 15 pacotes
atravessaria a porta**, por um motivo que não é do candidato. O julgamento deles não foi
sobreposto; a lacuna foi fechada na origem (abaixo).

## O que foi feito com o achado

A receita virou código, no `_compartilhado`: **`digest_de_arvore()`**, com a receita
inteira escrita na docstring — chave (caminho POSIX relativo), comparador (ordinal sobre a
chave), linha (`sha256sum`, hash antes do caminho, dois espaços), separador e terminador
(`\n`), codificação (UTF-8), e `__pycache__` fora.

Provada por **duas implementações independentes**, que é o padrão que o `PLACAR` de
Registros estabeleceu:

```text
python  digest_de_arvore(...)                          -> 1913add7…92e921
shell   find | LC_ALL=C sort | sha256sum | sha256sum   -> 1913add7…92e921
```

E travada no teste do motor, com cinco casos — determinismo, reprodução da receita da
docstring, CRLF mudando o número (deliberado), `__pycache__` ignorado, raiz ausente
falhando fechado. **Provada por mutação:** trocar **dois espaços por um** na receita leva
o teste de `exit=0` para `exit=1`.

Cadeia de validadores: 1560 → **1565**.

## Ledger

| | R1 |
|---|---|
| Rota canônica CEO → Diretor → Juízes | ✅ |
| Juízes recusaram sem inventar nota | ✅ |
| `JUDGE_REPORT` com nota por critério | ❌ — bloqueado na porta |
| Óticas em instância própria | 0 de 3 |
| Fechou no orçamento | ✅ 17,5 min de 25 |
| Causa do bloqueio | **erro do operador** — digest sem receita publicada |

**Pendente:** a rodada 2, com o candidato identificado por `digest_de_arvore()` — número
agora reproduzível por qualquer um.

---

# Rodada 2 — 2026-07-28

Executor: sessão nova por `claude -p`, worktree isolado `Temp/f5r2` no HEAD, para que o
`digest_de_arvore()` estivesse **dentro** do runtime que os Juízes usariam.
Mesmo candidato, mesma rota, mesmo orçamento. Um fator mudou: a identidade do candidato
passou a ser calculada pela receita pública — `1913add7…92e921`, reproduzida em Python e
em shell antes de emitir a missão.

**Veredito: o painel julgou. Há 14 notas com evidência. Não há `JUDGE_REPORT` — a rodada
foi cortada pelo relógio antes da consolidação.**

## A porta abriu

O bloqueio da rodada 1 não se repetiu: o digest reconciliou e o candidato foi aberto. A
cadeia produziu, na sequência canônica:

```text
01-EXECUTIVE_MISSION          CEO → Diretor
02-JUDGMENT_REQUEST           Diretor → Juízes
03-CRITERIA_MATRIX            Juízes: 8 critérios, cada um com ótica dona
04/05/06-JUDGE_ASSIGNMENT     Juízes → 3 óticas
08/09/10-JUDGE_OPINION        3 óticas, 14 notas no total
13-PANEL_RECORD (FINAL)       scores_recebidos = esperados nas três
```

Nenhuma ótica calculou corte ou veredito — `calculou_corte_ou_veredito: false` nas três.
Consolidar é ato da gerente, e elas respeitaram isso.

## As notas, e o 6

Treze notas **9** e uma **6**, em `CRIT-06` (evals com honestidade declarada), pela ótica
`robustez-e-evidencia`. A justificativa é literal e checável, e **eu a confirmei
independentemente**:

| Cláusula do critério | Estado |
|---|---|
| ≥ 12 casos, ao menos 1 de origem real | ✅ 16 casos, 1 `real` + 15 `sintetica` |
| validador determinístico que **importa** o motor, sem copiá-lo | ✅ linhas 80/82/86; nenhuma cópia no pacote |
| PLACAR com marcação de executado **e** cada limite ligado a um risco residual | ❌ **6 de 8** |

Os itens 2, 4, 5, 6, 7 e 8 da seção *"O que ainda não foi provado"* nomeiam `R4`, `R7`,
`R2`, `R3`, `R5` e `R6`. **Os itens 1 e 3 não carregam identificador nenhum.** Conferido
no arquivo: a leitura da ótica está correta.

E ela recusou compensar: *"não compenso com a força das outras duas cláusulas"* — que é a
regra da menor nota funcionando dentro de um único critério.

**A aritmética é visível, mas o veredito não é meu para emitir:** menor nota 6, corte 9,5.
Quem transforma isso em `REPROVADO` é o `departamento-juizes`, no `JUDGE_REPORT` que a
rodada não chegou a produzir. Registrar o número como se fosse o parecer seria
exatamente a fabricação que este gate existe para impedir.

## O desvio de rota, que é o achado estrutural

O contexto principal — o **CEO** — acionou cinco instâncias: o Diretor, os Juízes, **e as
três óticas**. As óticas deveriam ter sido acionadas pela instância dos Juízes, não pelo
CEO. A cadeia **achatou**: o topo alcançou dois níveis abaixo.

Compare com a rodada 3 da frente 4, onde o `departamento-arquitetura-software` acionou as
próprias óticas. Lá a hierarquia se manteve; aqui não. O que muda entre os dois casos é
material para a próxima rodada — não há evidência suficiente para dizer se foi pressão de
orçamento, se foi a forma da missão, ou se é propriedade do pacote dos Juízes.

## O que continua sem prova

1. **Não há `JUDGE_REPORT`** — quarta rodada consecutiva cortada pelo relógio, agora aos
   40 min de teto externo com orçamento de 25. O `PANEL_RECORD` fechou `FINAL`; a
   consolidação não saiu.
2. **Nenhum pacote tem parecer formal.** A frente 5 **não fechou**.
3. **O achado do CRIT-06 é acionável e não foi corrigido** — de propósito: consertar o
   candidato no meio do julgamento é viciar o gate. Fica como decisão do Jeremias.

## Ledger

---

# Rodadas 3 e 4 — 2026-07-28 · **o pacote atravessa o gate**

## Rodada 3 — o gate pegou o operador

Rejulgamento após a primeira tentativa de corrigir o `CRIT-06`. Veredito:
`REPROVED`, mínimo 6 — e o parecer sobre a **correção do operador** foi
**evasão**, com três razões verificadas fora da rodada, **todas procedentes**:

1. a justificativa citava **metade** da definição do §12 — *"**limites do
   runtime**, não descuido"* — e a metade omitida era onde o item caía;
2. a citação de apoio **não tinha referente**: a frase atribuída ao item aparecia
   uma única vez no arquivo, dentro da própria citação, porque o item fora
   reescrito;
3. a premissa era **contradita por medição dentro do candidato** — os 15 gerentes
   não são skills invocáveis (`departamento=0 ; agente=0`), logo não havia
   "caminho conhecido para fechar".

A ótica separou o legítimo do ilegítimo: a **categoria** "prova pendente × limite
residual" é válida; a **aplicação àquele item** não era. E a correção criou defeito
novo, medido: `PEND-CONTAMINACAO-PLACAR` — o candidato passou a publicar dentro de
si o parecer do gate, e o `CRIT-07` saiu com `confidence: media`, a única nota do
painel com confiança reduzida.

## O que foi feito entre as rodadas

- **`R9` no protocolo:** o vetor que faltava — acionamento espontâneo não é
  verificável em pacote não invocável. O item voltou à lista de limites citando-o.
- **A cláusula virou código:** `limites_ligados_a_risco_errors` exige um `R` por
  item, com o conjunto válido **lido do §12**, não listado no validador. Provado
  por mutação.
- **Descontaminação:** veredito, notas e crítica saíram do candidato.

## Rodada 4 — `ACEITO_USO_INTERNO`, mínimo 8, **alcança o `required_level`**

19 min, US$ 12,63, 5 instâncias de 6.

```yaml
minimum_score: 8
verdict: ACEITO_USO_INTERNO
required_level: INTERNO
alcanca_required_level: true
```

| Critério | R3 | R4 |
|---|---:|---:|
| CRIT-06 · evals honestos | 6 | **8** ↑ |
| CRIT-07 · não-julgamento | 9 | **8** ↓ |
| demais | 8–9 | 8–9 |

**A mesma ótica que reprovou como evasão inverteu o próprio parecer** e explicou a
diferença: a tentativa anterior *retirava* o item da seção; esta o devolveu com um
`R` que nomeia causa medida, efeito e **condição de fechamento externa e
falsificável**. Não é tautológica.

E achou o defeito seguinte, também do operador: `APROVADO PARA PROMOÇÃO` seguia no
placar — vocabulário que o **próprio pacote proíbe** (`\baprovad[oa]s?\b`), e que
escapa porque `judgment_language_errors` só percorre `dict`, nunca `.md`.

**A sugestão de estender a varredura aos `.md` foi recusada, com motivo:** a mesma
lista proíbe `PASS|FAIL|SKIP`, que `placar_errors` **exige** no placar. As duas
travas se contradiriam. O conserto foi mais fundo — a seção de autoveredito virou
**estado observável**, porque um pacote que se declara aprovado está fazendo o
autojulgamento que o ADR-002 proíbe, ainda que com outra palavra.

## Ledger das quatro rodadas

| | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Candidato aberto | ❌ | ✅ | ✅ | ✅ |
| `JUDGE_REPORT` | ❌ | ❌ | ✅ | ✅ |
| `minimum_score` | — | 6 | 6 | **8** |
| Veredito | — | — | `REPROVED` | **`ACEITO_USO_INTERNO`** |
| Alcança o pedido | — | — | não | **sim** |
| Custo | US$ 5,39 | — | US$ 14,58 | US$ 12,63 |

**O ciclo fechou:** defeito achado → corrigido na substância → travado em código →
rejulgado → aceito no nível pedido. E o gate reprovou o operador **duas vezes** no
caminho, o que é a evidência mais forte de que ele não é decorativo.

---

## Ledger das rodadas 1 e 2

| | R1 | R2 |
|---|---|---|
| Digest reconcilia | ❌ receita não publicada | ✅ `1913add7…` |
| Candidato aberto | não | **sim** |
| `CRITERIA_MATRIX` | não | **8 critérios com dona** |
| Óticas em instância própria | 0 de 3 | **3 de 3** |
| Notas com evidência | 0 | **14** |
| `JUDGE_REPORT` | ❌ | ❌ (timeout) |
| Rota | ✅ canônica | ⚠️ CEO acionou as óticas |

---

# Rodada 3 — 2026-07-28 · **a Estrutura tem seu primeiro parecer**

Escopo estreito de propósito: **só a consolidação**, a partir dos pareceres da rodada 2 —
que entraram identificados por SHA-256, versionados no repositório. Proibido reabrir
critério, reavaliar candidato, acionar ótica nova ou mudar nota; discordância vira
observação, porque **a nota é de quem a deu**.

Fechou em **9,3 min de 12** de orçamento, 42 turnos, US$ 3,06, `exit=0`.

## O parecer

`17-JUDGE_REPORT.yaml` · `sha256:7aabe4f9…d138c95` — digest recalculado fora da rodada,
**bate exato**.

| Critério | Nota | Ótica dona |
|---|---:|---|
| CRIT-01 · CRIT-02 · CRIT-03 | 9 · 9 · 9 | fidelidade-e-contrato |
| CRIT-04 · CRIT-05 | 9 · 9 | robustez-e-evidencia |
| **CRIT-06** | **6** | **robustez-e-evidencia** (banda *cru*) |
| CRIT-07 | 9 | fidelidade-e-contrato |
| CRIT-08 | 9 | robustez-e-evidencia |

```yaml
minimum_score: 6      # min(9,9,9,9,9,6,9,9)
verdict: REPROVED     # corte >= 9,5
```

**Nenhuma nota foi criada, mudada ou revista.** A linha do `CRIT-06` cita o parecer de
origem com digest — `09-JUDGE_OPINION-robustez.yaml sha256:cd9f4741…` —, o mesmo valor
calculado antes de a rodada começar. Na `CRIT-06` a ótica secundária deu 9 e está
registrada como **não prevalecendo**: a nota é da dona.

**8 de 8 critérios pontuados, `uncovered` vazio.** Logo a reprovação é por **defeito
observado**, não por lacuna de cobertura — a distinção que o ADR-002 exige.

## Duas condutas que valem registro

**O Diretor não cunhou um `JUDGMENT_REQUEST` novo, e explicou por quê.** O pedido da
rodada 2 continua vigente e já cobre a consolidação; um segundo pedido para o mesmo
candidato e a mesma rodada seria duplicado — e pedido novo é, por definição, pedido de
julgamento, o que a missão proibia. O envelope tem `additionalProperties: false` e nenhum
campo de modo: **não há como escrever nele "consolide, não julgue"**. A decisão está em
`15-RETOMADA-DIRETOR.md`, declarada em vez de escondida.

**Não saiu `EXECUTIVE_SUBMISSION`**, e a razão é a certa: ele exige `test_summary`,
`governance_report` e `audit_refs`, que não existem nesta rodada e nem deveriam — o escopo
proibia rodar teste. *"Preencher seria fabricar."*

## Estado do candidato

`REWORK` — que, pelo próprio `SKILL.md` do CEO, **não é estado terminal**. O que fechou foi
a missão de consolidação, não o candidato. Sem exceção, sem `LIMITATION_REPORT`.

## O que a frente entregou, e o que ela abriu

**Entregou:** o critério de pronto da Frente 5 — *"ao menos um pacote com parecer emitido
pela rota canônica, com nota registrada; e o placar dele deixa de dizer 'nunca passou pelo
gate'"*. O `PLACAR.md` do `departamento-inovacao-melhoria` abre com o parecer.

**Abriu:** o pacote apontado no plano como **o mais forte dos 15** tirou 6 no corte de 9,5.
Duas leituras convivem e a decisão é do Jeremias:

1. **O defeito é real e pequeno** — dois limites sem identificador de risco, conserto de
   duas linhas. Corrigir e rejulgar.
2. **A régua merece conversa.** A memória desta casa registra que revisão adversarial
   satura perto de 8,5, e o corte é 9,5. Se o pacote mais conforme reprova por uma cláusula
   de forma, o número 9,5 é o que precisa ser examinado — não o pacote.

As duas podem ser verdade ao mesmo tempo.

## Ledger final da Frente 5

| | R1 | R2 | R3 |
|---|---|---|---|
| Candidato aberto | ❌ | ✅ | ✅ |
| Notas com evidência | 0 | 14 | 14 (as mesmas) |
| `JUDGE_REPORT` | ❌ | ❌ | **✅ `REPROVED`, mínimo 6** |
| Fechou no orçamento | ✅ | ❌ 40 min | **✅ 9,3 de 12 min** |
| Custo | US$ 5,39 | — | US$ 3,06 |
