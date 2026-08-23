# ADR-019 — `ANALYSIS_RETURN` como retorno não final: análise informativa não emite status de validação

- **Data:** 2026-08-01
- **Status:** **EM VIGOR desde 2026-08-22**, por autorização de Jeremias.
  Até esta data era *proposto*, e o parágrafo abaixo registra exatamente **o que entrou** —
  porque promover o documento sem dizer o recorte seria publicar um registro que descreve
  outra coisa.
- **Proponente:** `departamento-evolucao-skills`, sob `EXECUTIVE_MISSION`
  `MISSION-T12-CONTRATO-ANALYSIS-20260731` do `ceo-maestro`
- **Decisor:** Jeremias
- **Rota escolhida:** opção **A** do `00-ANALISE-E-OPCOES.md`, escolhida por Jeremias em 2026-07-31
- **Candidato de origem:** `ceo-maestro/evals/contrato-analysis-2026-07-31/candidatos/`
  `cand-A2-analysis-return-rebase/` — e **não** o `cand-A`, que a linha original citava.
- **O que entrou em vigor, e o que NÃO entrou.** O que vigora é uma **fatia extraída** do
  candidato, não o overlay dele. Medido em 2026-08-22 com
  `_compartilhado/verificacoes_pacote.py::promocao_e_segura`: a base declarada do `cand-A2`
  batia em **zero de nove** alvos, e aplicar o overlay do `ceo-maestro` (+714 −1528 linhas)
  **apagaria oito travas** nascidas depois de 2026-08-03 — entre elas `forbidden_actors`,
  `_selo_confere_com_execucao` e `recusar_execucao_fora_da_fonte`.

  **Entrou:** o bloco `$defs/analysisReturn` no `ceo-maestro.schema.json` — autocontido, com
  os oito `$ref` que usa já existentes na árvore —, a fiação dele no `oneOf` da raiz, e seis
  casos no validador do CEO: um positivo, quatro negativos (um por trava desta decisão) e um
  de **alcance pela raiz**. Mutação **5 de 5**. `ceo-maestro` foi de 160 para 166 casos.

  **Não entrou:** as seções de `protocolo-de-handoff.md` e `SKILL.md` sobre `ANALYSIS_RETURN`,
  nem as alterações no pacote `departamento-evolucao-skills` — cujo schema, medido, é
  **idêntico** ao vivo e portanto nada tinha a acrescentar.
- **Contexto normativo:** [ADR-006 arquitetura sem julgamento](../diretor-de-lentes/departamentos-operacionais/departamento-arquitetura-software/references/adr-006-arquitetura-sem-julgamento-e-com-seis-agentes.md) ·
  [ADR-015 checagens por pacote e de estrutura inteira](../diretor-de-lentes/departamentos-operacionais/departamento-arquitetura-software/references/adr-015-checagens-por-pacote-e-de-estrutura-inteira.md) ·
  [ADR-001 hierarquia executiva](adr-001-hierarquia-executiva.md) ·
  [ADR-014 dois níveis de veredito](../diretor-de-lentes/departamento-juizes/references/adr-014-dois-niveis-de-veredito.md) ·
  [ADR-004 evolução no nível do CEO](../departamento-evolucao-skills/references/adr-004-evolucao-no-nivel-do-ceo.md)

## Contexto

O `departamento-evolucao-skills` tem três modos. Um deles, `AVALIACAO`, é especificado para **medir
e diagnosticar sem propor mudança** — e a especificação diz, com todas as letras, que a rodada não
gera candidato, **não dá nota e não chama os Juízes**.

Mas o único envelope que levava a saída dele ao CEO era a `EXECUTIVE_SUBMISSION`, cujo `required`
exige `judge_report` **e** `governance_report`, sem nenhum condicional. O modo estava especificado
para produzir algo que o contrato de entrega não conseguia transportar sem violar a especificação do
próprio produtor.

O workflow do CEO já dizia o mesmo por outro caminho: *"pedido puramente informativo, sem
produto/proposta → CEO responde ou roteia para análise — **não emitir status de validação**"*.

Uma correção anterior tinha sido aplicada **num lugar só**: `analysis` foi acrescentado ao enum de
`executiveSubmission.deliverable_type`, mas o `required` do mesmo envelope não mudou e nenhum
condicional foi criado. O `analysis` ficou **nomeável e não preenchível** — e o remendo abriu três
divergências novas em cima da original.

### As quatro divergências medidas

| # | Onde | Dizia | Contra |
|---|---|---|---|
| 1 | `schemas/ceo-maestro.schema.json` | `deliverable_type: [product, proposal, analysis]` | `references/protocolo-de-handoff.md:90`, que dizia `product \| proposal` |
| 2 | `SKILL.md:15` (Lei de Ferro) | *"aceitar como entrega final somente `product` ou `proposal`"* | o próprio schema, que aceitava `analysis` |
| 3 | `references/protocolo-de-handoff.md:89` | `submitted_by: diretor-de-lentes \| departamento-negocios` | o schema usa `directExecutive`, que **inclui** `departamento-evolucao-skills` desde o ADR-004 |
| 4 | `executiveSubmission.required` | `judge_report` e `governance_report` obrigatórios, sem condicional | a especificação do modo `AVALIACAO`, que não chama os Juízes |

A divergência 3 foi encontrada **independentemente** pela ótica de fidelidade no rejulgamento da
rodada 2, que a listou como mudança exigida em C01. Duas frentes separadas chegaram nela.

## Decisão

**Criar `ANALYSIS_RETURN` como retorno não final, ao lado de `PROGRESS`, `BLOCKED_RETURN` e
`CAPABILITY_GAP` — que já existem exatamente para isso — e devolver
`executiveSubmission.deliverable_type` a `product | proposal`.**

**1. `ANALYSIS_RETURN` não carrega veredito e não exige `judge_report` nem `governance_report`,
porque análise informativa não emite status de validação.** Essa é a razão inteira, e ela não é "é
mais fácil assim". Não há candidato para julgar, não há entrega para auditar e portanto não há o que
validar. Um envelope que exigisse parecer sobre uma medição poria os Juízes a pontuar algo que não é
candidato.

**2. A `EXECUTIVE_MISSION` continua podendo pedir `analysis`, e o `deliverable_type` dela decide o
envelope de volta.** A correspondência é fechada e não tem terceira combinação:

| Missão pediu | Volta em | Passa pelo gate? |
|---|---|---|
| `product`, `proposal` | `EXECUTIVE_SUBMISSION` | sim, com todos os gates |
| `analysis` | `ANALYSIS_RETURN` | **não** |

**3. A barreira de entrada do CEO passa a classificar antes de conferir.** `classify_executive_return`
devolve `FINAL`, `NAO_FINAL` ou `INVALIDO` a partir do `artifact_type`, e é chamada de dentro do
fluxo real — de `validate_submission` e, sobretudo, de `validate_decision_packet`, que é **onde a
decisão acontece**. Retorno não final falha fechado antes de qualquer nota ser lida.

**4. `ANALYSIS_RETURN` não pode virar porta dos fundos, e as travas são estruturais, não avisos.**
Cinco tentativas distintas de transportar produto ou proposta por ele, e o que barra cada uma:

| Tentativa | Trava | Onde |
|---|---|---|
| `content_type: product` ou `proposal` | `const: analysis` | schema + validador |
| pendurar `deliverable_type`, `judge_report`, `governance_report`, `candidate_digest`, `test_summary`, `limitation_report`, `exception_authorization`, `verdict`, `minimum_score` | `additionalProperties: false` e conferência **por presença de chave** | schema + validador |
| apontar para um candidato real | `causal.candidate_digest` fixo em `"n/a"` — análise não tem candidato | schema + validador |
| responder com análise a uma missão de produto/proposta | `executive_mission.deliverable_type` fixo em `analysis` | schema + validador |
| levar o envelope ao gate de qualidade | barreira de entrada, fail-closed | `validate_decision_packet` |

Nenhuma dessas travas é um booleano autoafirmado. `carries_verdict: false` foi **recusado** de
propósito: é exatamente o gate declarado que esta base já pagou para aprender a não aceitar. A
conferência é por **presença da chave**, que não se pode declarar de fora.

**5. Nenhum gate de `product` ou `proposal` é afrouxado.** `EXECUTIVE_SUBMISSION` continua exigindo
`JUDGE_REPORT` vigente e ligado ao mesmo candidato, `governance_report` conforme, `required_level`
preservado, menor nota inteira, faixa fixa do ADR-014 e todos os gates não renunciáveis. O caso
`"EXECUTIVE_SUBMISSION de produto continua alcançando o gate"` existe no validador para provar que o
caminho legítimo não foi tocado.

**6. O produtor declara o envelope, e o envelope é derivado.** O `EVOLUTION_LEDGER` do
`departamento-evolucao-skills` ganha `envelope`, amarrado por `if/then` ao `deliverable_type`:
`proposal → EXECUTIVE_SUBMISSION`, `analysis → ANALYSIS_RETURN`. Trocar um pelo outro é rejeitado no
schema do produtor **e** de novo na barreira do CEO. Duas camadas, porque a troca é justamente a
armadilha desta decisão.

## Consequências

**O que melhora**

- As quatro divergências deixam de existir, e schema, protocolo, Lei de Ferro e a especificação do
  produtor voltam a contar a mesma história — verificável por leitura direta e por
  `validate_contrato_de_analysis`, que **compara os três** em vez de conferir cada um sozinho.
- O modo `AVALIACAO` passa a ter envelope de destino sem violar a própria especificação.
- A barreira de entrada do CEO vira **uma função**, chamada de dois pontos do fluxo real, em vez de
  um `!=` de string repetido. Mutar a classificação fica vermelho nos dois lugares.
- `departamento-evolucao-skills` aparece em `submitted_by` no protocolo, alinhado ao ADR-004 e ao
  achado independente de C01.

**O que fica PIOR — e é o preço aceito**

- Um artefato novo no schema e no protocolo: mais superfície para manter em dia.
- A rota do `departamento-evolucao-skills` passa a ter **dois** retornos possíveis conforme o modo,
  e quem lê o pacote precisa saber qual. O `envelope` derivado no ledger existe para que essa
  escolha nunca seja livre.
- `validate_contrato_de_analysis` lê Markdown para comparar protocolo e `SKILL.md` com o schema.
  Leitura de documento é frágil por natureza; a mitigação foi **extrair o bloco da seção** e ler o
  campo YAML dentro dele, em vez de procurar substring solta no arquivo inteiro — que é como a
  divergência 3 sobreviveu tanto tempo à leitura humana.

## Alternativas consideradas e recusadas

**B — condicional dentro de `executiveSubmission`.** Manter `analysis` no enum e acrescentar um
`allOf` que dispense `judge_report` quando `deliverable_type` for `analysis`, preservando
`governance_report`.

*Recusada.* Enfraquece o envelope cuja função declarada é justamente transportar o gate: passaria a
existir um caminho, dentro do artefato de entrega, em que o parecer dos Juízes é opcional. E mantém
a divergência 2 — a Lei de Ferro teria de ser reescrita para admitir uma terceira entrega final.
Mudança menor no diff, maior no contrato.

**C — status quo.** `analysis` continua exigindo os dois gates.

*Recusada.* Obriga o modo `AVALIACAO` a chamar os Juízes, contradizendo a especificação do próprio
Departamento, e põe os Juízes a pontuar uma **medição** — que não é candidato. É o caminho que mais
empurra a incoerência para dentro da cadeia.

**D — `carries_verdict: false` como marcador do envelope.** Declarar no artefato que ele não carrega
veredito.

*Recusada.* Booleano autoafirmado não transforma falha em passe, e é gate declarado, não derivado.
A verificação por **presença de chave proibida** dá a mesma informação sem depender da honestidade
de quem emite.

## Prova

A decisão foi provada por **mutação executada**, não declarada — inclusive a mutação da própria
trava, para descartar teste que passa pela razão errada. O registro está em
`ceo-maestro/evals/contrato-analysis-2026-07-31/prova/`.

## Pendências

- **R6** — a existência das travas é verificável pelos validadores, mas a adesão do modelo em
  runtime ao passo 5 do `SKILL.md` não é: nenhuma trava obriga o CEO a *invocar* a barreira num
  turno real. Permanece medida por eval de comportamento, não por schema.
- ~~A promoção deste candidato à árvore viva é do CEO com Jeremias. Enquanto isso, o ADR é
  **proposto**.~~ **Cumprida em 2026-08-22:** Jeremias autorizou a fatia, ela foi aplicada e
  provada por mutação, e este ADR passou a viger. A pendência fica riscada e não apagada —
  registro que some não deixa ver que existiu.
- **ABERTA, e nasceu da própria promoção:** o contrato vigora e as **seções de protocolo**
  que o descrevem continuam fora da árvore viva. Mecanismo sem prosa que o explique é a
  metade oposta do defeito que esta casa persegue, e fecha quando a fatia seguinte entrar.
- **Renumerado de 018 para 019 em 2026-08-03, por identidade e não por mérito.** A reserva
  do 018 está registrada acima e foi feita em 2026-07-31, **3h12min antes** de o concorrente
  nascer; a condição de colisão foi declarada por escrito antes de ela ocorrer. Ela ocorreu: em
  2026-08-03 a tarefa 15 canonizou `adr-018-tres-eixos-por-trava.md` na árvore viva, e
  `validate_adr_series` varre a estrutura inteira — dois `adr-018-*.md` reprovam os quinze
  validadores por identidade, sem olhar o conteúdo de nenhum dos dois. Quem chegou primeiro
  não desempata uma série global: quem está na árvore viva desempata. Decisão de Jeremias,
  2026-08-03; o mérito deste ADR não foi tocado.
- **Endereço decidido em 2026-08-03: este ADR mora em `ceo-maestro/references/`.**
  Antes ele estava proposto em `departamento-arquitetura-software/references/`, que **não possui
  nenhum dos dez alvos** que esta decisão muda. O precedente da casa é que cada ADR mora no
  `references/` do pacote que **governa** a decisão — `adr-004` em Evolução, `adr-014` em Juízes,
  `adr-017` e `adr-018` em Auditoria, `adr-001-hierarquia-executiva` no próprio CEO. Esta decisão
  define `ANALYSIS_RETURN` como retorno não final no protocolo de envelope, e o protocolo de
  handoff vive em `ceo-maestro/references/protocolo-de-handoff.md`; os alvos estão em
  `ceo-maestro/` e em `departamento-evolucao-skills/`, e quem **consome** o envelope na barreira é
  o CEO. Decisão do `ceo-maestro`, mediando a divergência que o bloqueio anterior classificara
  como "não bloqueia por si; viaja junto" e a Auditoria classificara como BLOCKER (`AUD-T12R-05`).
  `departamento-arquitetura-software` não ganha nem perde nada com ela e não foi tocado.
