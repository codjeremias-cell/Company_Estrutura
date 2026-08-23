# Modo DISPUTA — julgamento comparativo cego

Modo **secundário** do Departamento, herdado do pacote legado `lente-juizes`. Vale somente quando
o `diretor-de-lentes` submete **2 ou mais candidatos** disputando o mesmo contrato e pergunta qual
deles vence. O modo padrão continua sendo VALIDACAO
([protocolo-de-julgamento.md](protocolo-de-julgamento.md)); disputa não substitui gate: o vencedor
de uma disputa ainda precisa passar por VALIDACAO antes de integrar.

Tudo o que este arquivo não redefine vale como está no protocolo central: identidade (quarteto),
descoberta do time (§2, regra 1), lacunas (§1.5), anti-bypass (§5), rastreabilidade (§6) e riscos
residuais (§7). A rubrica é a mesma ([rubrica-e-corte.md](rubrica-e-corte.md)) — o que muda é o
**uso**: aqui a nota separa candidatos, não decide gate, e as faixas do ADR-014 **não se
aplicam**.

## 1. Quando o Departamento recusa a disputa

Devolver ao Diretor sem painel, com o motivo declarado, quando:

- houver **um único** candidato — não há disputa, e julgar um artefato isolado é VALIDACAO;
- a disputa for decidível por **critério objetivo verificável por comando** (o resultado é um
  número ou um binário, não um juízo): três agentes cegos para o que um comando decide é
  burocracia, não rigor;
- o insumo decisivo for **screenshot ou artefato visual**: a higienização deste modo trata texto e
  as três óticas não avaliam imagem;
- o pedido vier de qualquer origem que não seja o `diretor-de-lentes` (§5, regra 2 do protocolo).

## 2. Cegueira reforçada

Vale a §2 do protocolo, com três endurecimentos:

1. **Rótulos e sorteio por agente.** Atribuir `A`/`B`/`C`… e **sortear a ordem independentemente
   para cada agente**; ordem nunca reaproveitada "para facilitar a comparação". Guardar o mapa
   `label → candidate_ref` fora da atribuição, em artefato de auditoria pós-rodada, referenciado no
   handoff — nunca exposto ao agente durante a rodada.
2. **Autoria inseparável exclui o candidato.** Aqui a regra 3 do protocolo se inverte: se a marca
   de autoria só sai alterando o conteúdo julgado, o candidato **não é enviado** e sai da disputa —
   nenhum rótulo sorteado para ele — e abre lacuna nomeando-o. Restando **2 ou mais** íntegros, a
   rodada segue entre eles. Restando **1 ou 0**, não há disputa: nenhuma atribuição é emitida, e o
   handoff sai `status: BLOCKED` mantendo o campeão. Em VALIDACAO a marca residual só rebaixa a
   confiança; em DISPUTA ela decide a comparação, e por isso exclui.
3. **Paridade de evidência.** Antes do sorteio, comparar quanta evidência do `evidence_index`
   cobre cada candidato: oferta assimétrica — um com prova, outro sem — enviesa sem quebrar a
   cegueira de autoria. Registrar a assimetria em `pending`, nomeando o candidato favorecido e o
   desfalcado; a gerente **não fabrica** evidência para equilibrar.

## 3. Atribuição e parecer

A `JUDGE_ASSIGNMENT` do modo DISPUTA leva `mode: DISPUTA` e, no lugar de
`anonymized_candidate`, a lista rotulada:

```yaml
  anonymized_candidates: [ { label: "A", artifact_ref: "<path anônimo já higienizado>" } ]  # ORDEM SORTEADA POR AGENTE
  separation_threshold: 1        # espelho do pedido; a gerente nunca o altera
```

O `JUDGE_OPINION` do modo DISPUTA acrescenta, ao schema da §1.4 do protocolo:

```yaml
  winner: "A | B | … | EMPATE"   # rótulo, nunca nome real de candidato
  tied_labels: ["<label>"]       # OBRIGATÓRIO com winner: EMPATE e 3+ candidatos
  scores: [ { label: "A", criterion_id: "<id>", score: "<inteiro 0..10> | n/a:<motivo>" } ]  # um por (label × critério)
  enxertos: [ { from_label: "<origem>", what: "<trecho/decisão/técnica>", why: "<ganho observável>" } ]
```

`winner` deve ser rótulo presente em `anonymized_candidates` ou `EMPATE`; qualquer outro valor é
parecer fora do contrato, e também o é omitir `tied_labels` com `EMPATE` e 3+ candidatos — sem ele
a apuração não sabe quem empatou, logo não sabe quem disputa. Par (label × critério) ausente segue
fora do contrato; `n/a:<motivo>` declarado ≠ omissão.

## 4. Apuração do consenso

Apurar somente pareceres **válidos** (§3 do protocolo, mais `winner` em rótulo existente).
**Traduzir cada `winner` de rótulo para `candidate_ref` pelo mapa daquele agente antes de
comparar** — rótulos de agentes com ordens diferentes não se comparam. Aplicar a **primeira regra
que casar; nenhuma posterior é avaliada**:

1. **Zero parecer válido** → `DECISAO_DE_LIDERANCA`, com uma lacuna por ótica que faltou.
   `status: BLOCKED` só se nenhum envelope voltou de agente algum ou nenhuma atribuição foi emitida
   (§2, regra 2); tendo voltado envelope, `PARTIAL`, campeão mantido, causa em `pending`.
2. **Menos de 2 pareceres válidos** → `QUORUM_DEGRADADO`.
3. **Painel completo e todos os válidos no mesmo `winner`** → `CONSENSO_UNANIME`. **Painel
   completo** = as três óticas acionadas **e** com parecer válido. Uma só em `MISSING`, `INVALID`,
   `CONFLICTED`, `SEM_RETORNO`, `FALHO` ou abstenção **proíbe** o unânime: concordância entre os
   disponíveis nunca se escreve como unanimidade.
4. **Painel incompleto e todos os válidos (2 ou mais) no mesmo `winner`** → `CONSENSO_PARCIAL`,
   `status: PARTIAL`, com a causa do faltante nomeada e uma lacuna por ótica sem cobertura.
5. **Maioria dos válidos no mesmo `winner`** → `CONSENSO_MAIORIA`. Copiar razões e enxertos da
   minoria para `divergences` e `enxertos` **na forma original** — nunca resumir, reescrever,
   suavizar ou descartar a minoria.
6. **Nenhuma das anteriores** → `SEM_CONSENSO`.

`EMPATE` conta como **valor distinto**: winners `A`, `B` e `EMPATE` são três valores, nenhuma
maioria se forma → `SEM_CONSENSO`. Dois `EMPATE` só são o mesmo `winner` quando os `tied_labels`,
traduzidos para `candidate_ref`, formam **conjuntos idênticos**.

**Consenso resolvido em `EMPATE`** mantém o campeão: `winner: <champion_ref>`,
`champion_kept: true`, e o `decision_mode` permanece o consenso apurado — **nunca** vira
`DECISAO_DE_LIDERANCA`, porque houve consenso e a gerente só transcreve. Sem campeão declarado:
`winner: null`, `champion_kept: "n/a"`, `status: PARTIAL`, e a escolha volta ao Diretor.

`leadership_reason` nomeia a causa e nunca altera a regra que casou: `SEM_RETORNO` (não devolveu
ou não recebeu atribuição por `MISSING`/`INVALID`/`CONFLICTED`); `QUORUM_DEGRADADO` (devolveu fora
do contrato duas vezes, absteve-se ou devolveu `BLOCKED`); `SEM_CONSENSO` (casou a regra 6). **Um
único valor**, pela precedência fixa `SEM_RETORNO` > `QUORUM_DEGRADADO` > `SEM_CONSENSO`; as demais
causas vão para `divergences`. `confidence` **não pondera o voto**.

## 5. `DECISAO_DE_LIDERANCA`

A gerente decide **apenas** quando a apuração casar a regra 1, 2 ou 6. Havendo consenso (regras
3–5), ela transcreve e não decide.

1. **Só evidência existente.** Decidir exclusivamente sobre notas, razões e enxertos já produzidos
   pelos agentes, mais os artefatos referenciados. Proibido criar critério, reavaliar os candidatos
   por conta própria ou atuar como um quarto juiz secreto.
2. **Fail-closed por padrão.** Sem parecer válido que sustente a troca, manter o campeão. Sem
   campeão declarado, `winner: null` e a escolha volta ao Diretor.
3. **Piso para recomendar a troca:** no mínimo **2 pareceres válidos** sustentando o mesmo
   desafiante. Com 1 ou 0, o único desfecho é manter o campeão. Quando o runtime expõe tier, ao
   menos um dos dois é de `tier` igual ao mais alto do painel; `tier: desconhecido` em **todos** é
   ausência de dado, entra em `pending` nomeando R2 e não altera o piso.
4. **Precedência determinística.** Desempatar pela **ordem declarada dos critérios**: percorrer do
   primeiro ao último e parar no primeiro que **separe**. Comparar, em cada critério, a média
   aritmética das notas dos pareceres válidos de cada disputado. **Separa** quando a diferença for
   **≥ `separation_threshold`** (ausente = 1 ponto); abaixo disso não separa e passa ao critério
   seguinte, como no empate numérico. `n/a` em qualquer disputado também não separa. Esgotada a
   ordem sem separação, mantém-se o campeão. Proibido escolher o critério de desempate no momento
   da decisão.
5. **Declaração obrigatória.** Toda `DECISAO_DE_LIDERANCA` declara: o motivo
   (`leadership_reason`); quais agentes devolveram parecer válido e quais não; os critérios de
   desempate aplicados, na ordem literal; e a razão em uma frase verificável ancorada em
   `evidence_ref` de um agente.

## 6. `PANEL_HANDOFF` (departamento-juizes → diretor-de-lentes)

Um **único** artefato, e a mais ninguém. Abre pelo resumo em linguagem comum, que o Diretor lê
antes do YAML.

```yaml
PANEL_HANDOFF:
  resumo:                                 # OBRIGATÓRIO e no topo, inclusive em PARTIAL e BLOCKED
    recomendacao: "<uma frase: o que o painel recomenda e sobre qual candidato>"
    razao_mais_forte: "<a razão que mais sustenta + o evidence_ref → artifact_ref que a prova>"
    divergencia: "<o que a minoria sustentou e por quê, em uma frase> | nenhuma"
    enxertos: "<o que vale migrar de um candidato para o outro> | nenhum"
  return_to: "diretor-de-lentes"
  judgment_request_ref: "<id>"
  contract_id: "<id>"
  contract_version: <inteiro>
  contract_digest: "sha256:<digest>"
  rubric_ref: "rubrica-corte-v2"
  status: "COMPLETED | PARTIAL | BLOCKED"
  decision_mode: "CONSENSO_UNANIME | CONSENSO_PARCIAL | CONSENSO_MAIORIA | DECISAO_DE_LIDERANCA"
  leadership_reason: "SEM_CONSENSO | SEM_RETORNO | QUORUM_DEGRADADO | n/a"
  winner: "<candidate_ref real, desanonimizado> | null"   # RECOMENDAÇÃO, nunca a promoção em si
  champion_kept: true | false | "n/a"
  panel:
    - { judge_id: "<id>", lens: "<ótica>", status: "COMPLETED | BLOCKED | SEM_RETORNO | FALHO",
        winner: "<candidate_ref> | EMPATE | n/a", confidence: "alta | media | baixa | n/a",
        substrate: "<declarado pelo runtime> | desconhecido", tier: "<declarado> | desconhecido" }
  score_matrix:      # todo parecer válido, cada candidato disputado, cada critério percorrido até o que separou
    - { judge_id: "<id>", label: "A", candidate_ref: "<real, desanonimizado só após a apuração>",
        criterion_id: "<id>", score: "<inteiro 0..10 | n/a:<motivo>>" }
  divergences: ["<judge_id + winner divergente + razão original, literal>"]
  enxertos: ["<from candidate_ref + what + why>"]
  evidence_index: ["<evidence_ref → artifact_ref real; só o efetivamente usado>"]
  label_map_ref: "<artefato de auditoria pós-rodada | sha256:<digest do mapa canônico>>"
  capability_gaps: [ <blocos JUDGE_CAPABILITY_GAP completos; nunca lista de strings> ]
  valid_opinions: <nº de pareceres válidos usados na apuração>
  pending: ["<lacuna + dono + impacto>"]    # R6 nomeado sempre
  recommended_next_step: "<consultivo; quem decide é o Diretor>"
```

- **O handoff informa, não autoriza.** `winner` é a **recomendação** do painel;
  `champion_kept: true` diz que o painel **não achou base para recomendar a troca**, nunca que a
  troca foi barrada. Quem promove é o Diretor, e acima dele o CEO e Jeremias.
- **Resumo obrigatório**, inclusive em `PARTIAL` e `BLOCKED`: sem recomendação possível,
  `recomendacao` diz isso e a causa. O resumo **espelha** `winner`, `divergences` e `enxertos` e
  nunca acrescenta; contraditório com eles, o handoff não sai até corrigir.
- **`COMPLETED` exige processo, não só aritmética.** Só sai `COMPLETED` quando, para **cada**
  `judge_id` do `panel`, o registro de emissão da `JUDGE_ASSIGNMENT` resolve em artefato conferível
  **e** o `label_map_ref` resolve. Qualquer um que não resolva rebaixa para `PARTIAL`, com a falta
  nomeada em `pending` (R6).
- **Score incompleto não coroa desafiante.** `score_matrix` ausente ou parcial no **critério que
  separou** força `PARTIAL` e mantém o campeão; o desafiante só é recomendado com a matriz do
  critério decisivo completa.

**Concluído quando:** `decision_mode` e `winner` são reproduzíveis por terceiro a partir de
`panel[]`, `score_matrix[]`, `divergences[]` e da precedência 1–6, sem escolha entre regras; e o
handoff carrega `label_map_ref`, `capability_gaps` em blocos, `valid_opinions` e R6 em `pending`.
