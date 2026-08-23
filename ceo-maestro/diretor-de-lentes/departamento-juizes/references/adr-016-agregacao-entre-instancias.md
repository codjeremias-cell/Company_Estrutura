# ADR-016 — Agregação entre instâncias, `NAO_DISCRIMINADO` e três travas de orquestração

- **Data:** 2026-07-31
- **Status:** proposta do `departamento-evolucao-skills`, sob `MISSION-T14-METODO-AGREGACAO-20260731`
- **Decisores:** `ceo-maestro` propõe a Jeremias; nota e veredito continuam exclusivos do `departamento-juizes`
- **Contexto normativo:** [ADR-014 — dois níveis de veredito](adr-014-dois-niveis-de-veredito.md) ·
  [ADR-002 — nota absoluta e modo duplo](adr-002-nota-absoluta-e-modo-duplo.md) ·
  [rubrica-e-corte.md](rubrica-e-corte.md) · [protocolo-de-julgamento.md](protocolo-de-julgamento.md)

## Contexto — a medição que obriga a decidir

Em 2026-07-31, por acidente de orquestração, **duas instâncias da mesma lente** julgaram os mesmos
oito alvos, com a mesma rubrica, sobre o mesmo snapshot de bytes. A medição está em
`ceo-maestro/evals/rejulgamento-rodada2-2026-07-31/09B-CONFERENCIA-DO-CEO-ADENDO-A2.md`.

| alvo | faixa entre instâncias | atravessa o corte 6/7? |
|---|---|---|
| C01 `ceo-maestro` | 6–7 | **sim** |
| C06 `departamento-arquitetura-dados` | 6–8 | **sim**, dois pontos |
| C09-A `c09-proibicao-absoluta` | 6–8 | **sim**, dois pontos |
| C03, C04, C09-B, C12-A, C12-B | 6–6, 7–7, 5–6, 6–6, 8–9 | não |

**Três de oito vereditos dependeram de qual instância sobreviveu a uma colisão de arquivo.** A
instância descartada foi escolhida por **proveniência** — quem escreveu primeiro —, não por mérito.
A regra "um artefato por `handoff_id` + `attempt`" está correta para integridade e é **arbitrária
para resultado**.

O que a medição prova não é que a rubrica está errada: é que **a régua tem folga maior que o degrau
que ela mede**. Na fronteira 6/7, onde o ADR-014 separa `REPROVED` de `ACEITO_USO_INTERNO`, a lente
não discrimina — e a casa nunca soube disso porque nunca havia rodado duas instâncias.

Na mesma rodada, três modos de falha de orquestração apareceram, e em todos a prevenção existente
era **prosa**:

1. concluir morte de executor por ausência de arquivo, e redespachar — **3 vezes**, criando o
   escritor duplicado que produziu a colisão;
2. painel emitido duas vezes para o mesmo `handoff_id`, sobre o mesmo caminho de escrita;
3. perda de bytes sem cópia de custódia — onde houve custódia (FID), a perda virou incidente
   contido; onde não houve (ROB), virou o dilema de remontar parecer a partir de nota derivada.

## Decisão

### 1. A regra de agregação é fixada no `JUDGMENT_REQUEST`, antes de qualquer parecer existir

`JUDGMENT_REQUEST` passa a exigir dois campos:

- `instances_per_lens` — inteiro de 1 a 5, quantas instâncias independentes da **mesma** lente
  rodam;
- `aggregation_rule` — `{ method, declared_at, rationale }`, com `method` em
  `MENOR | MEDIANA | EMPATE_DECLARADO`.

`declared_at` precede **todo** `issued_at` de parecer da rodada. A conferência é de código, não de
boa-fé: um `declared_at` posterior ao primeiro parecer invalida o pedido.

**A regra combina instâncias da mesma lente. Ela não toca a menor nota entre critérios.** A §3,
regra 4, do protocolo continua proibindo média, mediana, ponderação e compensação **entre
critérios**. O que a `MEDIANA` deste ADR admite é mediana entre as *consolidações* de instâncias da
mesma lente — três leituras do mesmo critério pela mesma ótica, não três critérios diferentes. Sem
essa separação a regra nova apagaria o ADR-002.

### 2. `NAO_DISCRIMINADO` é veredito, e não autoriza nada

Novo valor do enum de `verdict`, nos três schemas — Juízes, Diretor e CEO.

Sai quando, e somente quando, **todas** as condições valem juntas:

- `instances_per_lens >= 2`;
- `minimum_score_range` (`lo`, `hi`) **atravessa** um corte do ADR-014 — `lo <= 6 e hi >= 7`, ou
  `lo entre 7 e 9 e hi = 10`;
- os gates de integridade estão íntegros: `critical_fail: false`, sem pendência bloqueante, sem
  lacuna de cobertura, sem critério sem dona.

A última condição não é decoração. **Falha crítica, lacuna ou bloqueio mandam `REPROVED`, não empate
técnico** — quem falhou um gate não está indiscriminado, está reprovado. `NAO_DISCRIMINADO` é
reservado ao caso em que a única coisa que falta é **poder de resolução da medida**.

`NAO_DISCRIMINADO` **não alcança nenhum `required_level`**: nem `PRODUCAO`, nem `INTERNO`. Não é
reprovação, não é aceite, não autoriza produção, publicação, exposição a terceiro nem uso interno, e
não serve de insumo a `EXECUTIVE_SUBMISSION`. Ele carrega `criticisms` e `required_changes` não
vazios, e o que ele exige não é mudança no candidato: é **mais medida** — mais instâncias, ou a
regra de agregação que o pedinte escolher declarar antes.

### 3. A faixa vira campo obrigatório, e o ponto vira caso particular dela

`minimum_score_range` passa a ser obrigatório em `PANEL_RECORD`, `DEPARTMENT_JUDGE_REPORT` e
`JUDGE_REPORT`. Com uma instância, `lo == hi == minimum_score`, e nada muda no comportamento
anterior. Com mais de uma, a faixa é o dado e o ponto é uma leitura dela.

Consequência direta, travada em schema: **faixa que atravessa o corte nunca vira veredito
positivo.** `VALIDATED` exige `lo = hi = 10`; `ACEITO_USO_INTERNO` exige `lo >= 7` e `hi <= 9`.

### 4. Três travas de orquestração, em código

| Trava | Onde vive | O que impede |
|---|---|---|
| **T3 — caminho de escrita exclusivo por emissão** | `write_path` obrigatório na `JUDGE_ASSIGNMENT` e `destination` no registro, no formato `julgamento/<handoff>/a<attempt>/<assignment_id>/`; unicidade conferida em código | duas instâncias escrevendo no mesmo arquivo — a colisão que descartou uma das instâncias por proveniência |
| **T4 — proibição de concluir morte de executor por ausência de arquivo** | `AGUARDANDO` entra em `judgeStatus`; `SEM_RETORNO` e `FALHO` exigem `no_return_evidence` com `runtime_signal` em `EXECUTOR_ERROR` ou `TIMEOUT_DECLARADO`; `NENHUM` só admite `AGUARDANDO` | o redespacho por impaciência, que criou a segunda instância três vezes na mesma rodada |
| **T5 — cópia de custódia obrigatória com digest antes do despacho** | `custody_copy` (`path`, `sha256`, `bytes`, `taken_at`) obrigatória na `JUDGE_ASSIGNMENT` e no registro; `taken_at` estritamente anterior a `issued_at`, conferido em código | a perda de bytes sem cópia, que transformou incidente contido em parecer irrecuperável |

Cada uma tem **caso negativo próprio** no validador, e cada uma foi provada por **mutação
executada** — a própria trava desligada, e o validador ficando vermelho. Trava declarada e não
provada não conta; essa é a lição mais cara desta base.

### 5. O teto de 3 do `panel` sai, e é substituído por algo mais forte

`panel` tinha `maxItems: 3`, o que era a codificação de "três óticas". Com mais de uma instância por
lente, o teto passa a 15 (3 × 5) — e **isso seria um afrouxamento se ficasse só nisso**. O que
substitui o teto vive em código e é mais apertado: no máximo **3 lentes distintas**, e cada lente com
**exatamente** `instances_per_lens` entradas, numeradas `1..N` sem repetir. `maxItems: 3` aceitava
duas linhas da mesma lente e nenhuma da terceira; a trava nova não.

## Alternativa recusada — mover a faixa do ADR-014

A alternativa considerada e **recusada** foi alargar a banda do ADR-014: transformar `7–9` em `8–9`,
ou criar uma zona morta em torno de 6/7 onde nada é decidido.

Recusada por três razões:

1. **Não é o defeito medido.** A faixa separa o que a rubrica descreve em banda; o que falhou foi a
   **precisão da medida**, não o lugar do corte. Mover o corte com uma régua imprecisa apenas move o
   ponto onde a imprecisão morde — e a medição mostra divergência de até 3 pontos, que atravessa
   qualquer corte que se escolha.
2. **Esconde o dado em vez de registrá-lo.** Zona morta devolve `REPROVED` implícito para todo alvo
   ambíguo, e o consumidor não distingue "tem defeito" de "não deu para medir". A distinção que o
   ADR-014 criou entre defeito e acabamento seria perdida na fronteira, que é justamente onde ela
   importa.
3. **Fecharia a porta errada.** Com corte movido e uma instância só, dois julgamentos do mesmo
   pacote continuariam podendo divergir sem que ninguém soubesse. O problema não é onde o corte
   está: é que **uma instância não sustenta veredito na fronteira**, e nenhuma escolha de corte
   conserta isso.

A faixa do ADR-014 fica **intacta**. Este ADR não a discute.

**Alternativa também recusada, em segundo lugar:** manter a regra de agregação em prosa no
protocolo, sem campo no envelope. Recusada pelo histórico da própria casa — aviso em prosa não
preveniu erro documentado quatro vezes, e as três travas desta rodada existem exatamente porque a
prevenção anterior era texto.

## Consequências

**Ganho.** O veredito na fronteira passa a ser uma afirmação sobre o candidato **e** sobre a
qualidade da medida. Um painel com uma instância continua funcionando exatamente como antes, com
`lo == hi`; um painel com mais de uma passa a não poder carimbar o que não mediu.

**Custo.** Três schemas ganham campos obrigatórios; quatro validadores ganham fixtures e casos; e
`JUDGMENT_REQUEST`, `PANEL_RECORD`, `DEPARTMENT_JUDGE_REPORT` e `JUDGE_REPORT` passam a carregar
`instances_per_lens`, `aggregation_rule` e `minimum_score_range`.

**Consequência retroativa, declarada e não resolvida.** Todo julgamento anterior da Estrutura que
fechou **a um ponto do corte** com **uma instância por lente** volta a ser leitura suspeita. A lista
está em `ceo-maestro/evals/metodo-agregacao-2026-07-31/06-JULGAMENTOS-SUSPEITOS.md`. Isso **não**
exige rejulgar tudo; exige que a lista exista, esteja declarada e seja consultada antes de qualquer
promoção que dependa daqueles vereditos.

**Risco declarado — R-A16-1:** `NAO_DISCRIMINADO` ser lido como "quase passou". A mitigação é o
nome, a decisão 2 e o gate de `required_level`, que não o alcança em nenhum nível. Nenhuma delas
impede um leitor apressado de tratar empate técnico como aprovação pendente.

**Risco declarado — R-A16-2:** as três travas são conferidas sobre o que a própria gerente escreve.
`write_path` único no papel não prova arquivo único em disco, e `custody_copy` com digest não prova
que a cópia existe. Como em **R6**, a condição **encarece a fabricação, não a impede**. O que ela
fecha é o modo de falha observado — colisão e redespacho por descuido —, não o adversário.

**Risco declarado — R-A16-3:** a hipótese direcional de que **painel interno tende à generosidade**
não foi testada. As duas instâncias da lente de robustez divergiram **todas para cima**; as da lente
de fidelidade divergiram nas duas direções. Uma amostra de duas lentes não separa viés de variância.
Fica declarada como frente seguinte, com desenho próprio — **não abandonada**.

**Não decidido aqui.** Qual `method` cada rodada deve escolher. O ADR fixa que a escolha é
**declarada antes**, e que as três opções são legítimas; qual delas serve a qual tipo de julgamento
é decisão de quem pede, registrada no `rationale`.
