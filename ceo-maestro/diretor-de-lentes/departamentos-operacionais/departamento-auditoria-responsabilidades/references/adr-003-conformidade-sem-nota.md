# ADR-003 — Auditoria prova conformidade, não pontua

- **Data:** 2026-07-26
- **Status:** aceito por decisão de Jeremias
- **Decisores:** Jeremias
- **Contexto normativo:** [ADR-001 da hierarquia executiva](../../../../references/adr-001-hierarquia-executiva.md) ·
  [ADR-002 dos Juízes](../../../departamento-juizes/references/adr-002-nota-absoluta-e-modo-duplo.md)

## Contexto

A `lente-auditor-responsabilidades` legada pontuava. Ela reconciliava dez dimensões, dava `1`,
`0,5` ou `0` a cada uma, somava numa **nota absoluta de 0 a 10**, aplicava corte de 9,5 e emitia
`APROVADO | APROVADO_COM_RESSALVAS | REPROVADO`. A própria skill declarava: *"Essa nota é da lente,
nunca da `lente-juizes`."*

Três artefatos já aceitos contradizem isso:

1. O **ADR-002** moveu a nota absoluta para o Departamento de Juízes e deixou registrado que a
   Auditoria "perde a nota e mantém a prova", devendo nascer **sem scorecard próprio**.
2. O **schema do CEO** define o artefato da Auditoria como `governanceReport`, com
   `auditor_ref: "departamento-auditoria-responsabilidades"` e `verdict` restrito a
   **`COMPLIANT | NONCOMPLIANT`** — binário, sem campo de nota, com `violations` obrigatoriamente
   vazio em `COMPLIANT` e obrigatoriamente não vazio em `NONCOMPLIANT`.
3. O **ORGANOGRAMA** fixa a divisão: *"o Departamento de Auditoria fornece a prova de governança e
   conformidade; o Departamento de Juízes consolida as evidências e emite o veredito final."*

E um quarto artefato puxa na direção oposta: a **RI-05** exige que *"toda auditoria termina com
aprovado / aprovado com ressalvas / reprovado, com motivos e responsáveis nomeados"* — **três**
estados, não dois. Regra Inquebrável não se dispensa por conveniência de schema.

## Decisão

**1. A Auditoria não pontua.** A nota absoluta de 0 a 10, a soma das dez dimensões e o corte de 9,5
saem do contrato deste Departamento. Quem pontua e aplica o corte é o `departamento-juizes`. A
Auditoria produz **prova de conformidade**: dimensão por dimensão, com estado, evidência e
responsável.

**2. Três estados por dentro, dois na fronteira, mapeamento determinístico.** A RI-05 é cumprida
com o veredito de três estados vivendo no `AUDIT_LEDGER` interno e no retorno departamental; o
`GOVERNANCE_REPORT` que atravessa para o CEO carrega o binário derivado, sem escolha:

| Veredito interno (RI-05) | `GOVERNANCE_REPORT.verdict` | `violations[]` | Obrigação adicional |
|---|---|---|---|
| `REPROVADO` | `NONCOMPLIANT` | ≥ 1 — uma por dimensão `NAO_CONFORME` ou `NAO_PROVADO` | — |
| `APROVADO_COM_RESSALVAS` | `COMPLIANT` | vazio | **cada ressalva vira `pending` com dono, impacto e condição de fechamento**, propagado ao `DEPARTMENT_RETURN` |
| `APROVADO` | `COMPLIANT` | vazio | — |

**3. Ressalva que bloqueia não é ressalva.** Falha bloqueante de `AUTH`, escopo, `INTENT`, prova
fresca, `TWINS` ou RI/RO aplicável é `NAO_CONFORME`, e nenhum rótulo a rebaixa: mudar o nome não
muda o efeito do contrato. A ressalva existe para o achado **comprovadamente não bloqueante** — e,
mesmo assim, ela nunca fica só no texto do relatório: vira `pending` visível, porque tanto a
barreira do Diretor quanto o gate do CEO leem pendências, não prosa.

**4. As dez dimensões migram, com dona única.** Cada dimensão tem exatamente um agente dono, e duas
delas têm um segundo inspetor. Onde há dois, **o estado mais grave vence** — mesma lógica
fail-closed da menor nota dos Juízes, aplicada a estados em vez de números.

**5. Dossiê incompleto reprova; não vira "não consegui auditar".** Insumo bloqueante ausente torna
a dimensão `NAO_PROVADO`, o que leva a `REPROVADO` e a `NONCOMPLIANT`, com o que faltou **nomeado
na violação**. A Auditoria nunca devolve silêncio, adiamento ou pedido de nova missão no lugar de
um veredito: ausência de prova é ausência de conformidade.

**6. A Auditoria é Departamento operacional e sua entrega também é julgada.** Ela recebe
`DEPARTMENT_MISSION` do Diretor e devolve `DEPARTMENT_RETURN`, que segue ao `departamento-juizes`
como qualquer outro. Ali os Juízes julgam **a qualidade da auditoria** — cobertura das dimensões,
rastreabilidade, independência —, nunca o candidato auditado. Não há recursão: a Auditoria prova
conformidade do candidato; os Juízes pontuam o trabalho da Auditoria.

**7. A Auditoria não executa teste, e o retorno diz isso.** O `test_summary` do `DEPARTMENT_RETURN`
da Auditoria é sempre `pass: 0, fail: 0, skip: 0`. Ela **confere** relatórios de teste produzidos
por terceiros, e esses relatórios aparecem como evidência conferida — nunca como contagem própria.
Herdar a contagem de outro Departamento no próprio retorno seria apropriar-se de prova alheia.

## Consequências

- o CEO recebe exatamente o `governanceReport` que o schema dele já exigia, sem campo inventado;
- existe **um único número** sobre o candidato em toda a estrutura, o `minimum_score` dos Juízes;
- a RI-05 continua cumprida, e o terceiro estado ganha efeito real via `pending` em vez de virar
  rótulo decorativo;
- a Auditoria fica mais dura, não mais frouxa: sem nota, não há como um `0,5` diluir um achado —
  ou a dimensão conforma, ou vira violação, ou vira pendência nomeada;
- o corte de 9,5 deixa de aparecer duas vezes com significados diferentes;
- quem ler a skill legada vai encontrar uma nota que aqui não existe: a diferença está registrada
  em [origem-migracao.md](origem-migracao.md), recorte reescrito.

## Alternativas consideradas

- **Manter a nota 0–10 da Auditoria.** Descartada: criaria duas notas concorrentes sobre o mesmo
  candidato, em escalas incompatíveis (soma de dez dimensões versus menor nota por critério), e o
  CEO teria de escolher qual obedecer — exatamente a ambiguidade que o ADR-002 fechou.
- **Adotar só o binário e abandonar o terceiro estado.** Descartada: violaria a RI-05, que é
  Regra Inquebrável. Schema de consumidor não revoga governança.
- **Tratar toda ressalva como violação.** Descartada: transformaria qualquer observação menor em
  reprovação, e o efeito prático seria os auditores pararem de registrar ressalvas.
- **Deixar a ressalva apenas no texto do relatório.** Descartada: é lavagem. Nem a barreira do
  Diretor nem o gate do CEO leem prosa — os dois leem pendência bloqueante. Ressalva invisível ao
  gate é ressalva que não existe.
- **Fundir Auditoria e Juízes num só Departamento.** Descartada: quem produz a prova de
  conformidade passaria a pontuar a própria prova, e a independência entre provar e julgar —
  a razão de os dois existirem — desapareceria.
- **Deixar a Auditoria devolver "missão insuficiente" sem veredito.** Descartada: abriria a saída
  em que nada é reprovado porque nada foi provado, e um dossiê ruim viraria adiamento em vez de
  reprovação.
