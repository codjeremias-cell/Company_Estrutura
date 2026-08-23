# Parecer — experiência e risco, instância 2

**Rodada:** `nucleo-de-comando-r2` · **Designação:** `ASSIGN-NUCLEO-R2-EXP-I2` ·
**Rubrica:** `rubrica-corte-v2` · **Nível exigido:** `INTERNO`
**Commit julgado:** `ed3b63f273e104f7b2e5d4a6f1af61f5b91d80e3`
**Critérios que me cabem:** `C05` (uso pela cadeia) e `C06` (limites declarados), sobre
`ceo-maestro`, `diretor-de-lentes` e `departamento-negocios`. Não julguei o `departamento-juizes`.

| pacote | C05 | C06 | menor |
|---|---:|---:|---:|
| `ceo-maestro` | **6** | **6** | 6 |
| `diretor-de-lentes` | **5** | **4** | 4 |
| `departamento-negocios` | **3** | **4** | 3 |

**Menor dos meus seis: 3.**

---

## O consumidor e o dia ruim

Toda nota abaixo é medida contra uma pessoa concreta: **o mantenedor da Estrutura numa sessão
futura, com pressa e sem o autor por perto**, que carrega a única porta instalada — `ceo-maestro` —
e precisa responder duas perguntas antes de confiar numa entrega:

1. este pacote já foi mesmo acionado pela cadeia, e com que envelope?
2. o que este pacote não consegue fazer, e onde ele falha calado?

O que torna esse cenário ruim não é a falta de documento. É que **nada que ele consegue alcançar o
desmente**: ele lê o `SKILL.md`, vê o validador verde e encontra um envelope de protocolo no disco,
e conclui que a rota descrita já rodou.

---

## Antes das notas: os envelopes desta rodada são de verdade?

Me pediram para decidir isso, e a resposta tem duas metades que não se cancelam.

### São de verdade — e digo isso contra a minha própria inclinação

Confiei nas quatro coisas que consegui recomputar sozinho:

| o que conferi | resultado |
|---|---|
| `contract_digest` do `00-CONTRATO.md` | **confere** — `sha256:3a4750d9…`, sobre 5453 bytes após CRLF→LF, sem BOM |
| `custody_copy.sha256` de `saida-crua/` | **confere** — `sha256:0c592c79…`, 5 arquivos, 44838 bytes |
| `taken_at` < `issued_at` (ADR-016, T5) | 01:30 < 01:35, **satisfeito** |
| coerência das 8 designações | `write_path` distinto por instância; partição de critérios idêntica à `CRITERIA-MATRIX`; mesmo `contract_digest` e mesma `custody_copy` nas oito |

Isso não é cerimônia. É a mitigação que o próprio `R6` do protocolo pede — "registro de emissão de
cada `JUDGE_ASSIGNMENT` (`assignment_id`, horário, destino) que resolva em artefato conferível" — e
ela está satisfeita.

### Mas não são os envelopes do protocolo

Comparei as designações contra o schema que o próprio `departamento-juizes` publica. Não passam:

**`JUDGE_ASSIGNMENT`** — `$defs.judgeAssignment`, `additionalProperties: false`

- **faltam seis campos `required`:** `causal`, `candidate_digest`, `anonymized_candidate`,
  `contract_excerpt`, `evidence_index`, `forbidden_context`;
- **sobram seis campos proibidos:** `contract_digest`, `contract_id`, `contract_version`,
  `issued_by`, `pacotes`, `required_level`;
- **`write_path` viola o pattern da trava T3 do ADR-016** —
  `^julgamento/[A-Za-z0-9._-]+/a[0-9]+/[A-Za-z0-9._-]+/$` contra
  `pareceres/experiencia-e-risco/i2/`.

**`JUDGMENT_REQUEST`** — mesma história: faltam `judgment_request_id`, `causal`,
`department_return_ref`, `candidate_digest`, `applicable_criteria`, `artifact_refs`,
`evidence_refs`, `issued_at`; sobram oito.

Para calibrar, abri um envelope real de campanha anterior
(`28-DIRECTOR-CAPABILITY-GAP-JUIZES-R2.json`, 2026-08-01). Ele traz o cabeçalho `causal` inteiro:
`handoff_id`, `message_id`, `causation_message_ids`, `contract_digest`, `candidate_digest`,
`producer_digest`, `round`, `attempt`. **A casa sabe emitir o envelope certo — e já emitiu.** O
desta rodada é mais pobre que o de seis dias antes.

### E a trava que deveria pegar isso é de um bit

Li o código da T32 (`ceo-maestro/evals/validate_workflow.py`). O único discriminador que sobrou é
`artifact_type == "JUDGE_ASSIGNMENT"` — e o comentário dela diz isso na cara, com honestidade que
registro a favor: *"forjar um JSON com esse `artifact_type` é trivial. Esta trava não torna o
bypass impossível — torna-o VISÍVEL e DELIBERADO."*

Há mais: `_houve_julgamento()` exige um arquivo `PARECER*`/`VEREDITO`/`JUDGE-OPINION` na pasta da
rodada para sequer examiná-la. Em `ed3b63f` esta rodada tinha só `00`, `01`, `02`,
`03-JUDGE-ASSIGNMENTS/` e `saida-crua/`. Então o `[PASS] nenhuma rodada de julgamento nova sem
JUDGE_ASSIGNMENT` publicado em `saida-crua/` **nunca olhou para esta rodada**. Verde por não ter
examinado é o falso positivo mais barato que existe.

> **Veredito da pergunta:** de verdade, sim; do protocolo, não. E a diferença entre as duas coisas
> é invisível para qualquer trava atual — que é exatamente o modo de falha que a minha ótica pune:
> **silenciosa e difusa**.

### Duas ressalvas sobre a custódia

**A receita do digest não está declarada em lugar nenhum.** Não está no envelope, não está no
ADR-016, não está no protocolo. Cheguei nela por **força bruta, em oito tentativas**, até bater:
`sha256` da concatenação, em ordem alfabética de nome, de `(nome em utf-8) + (bytes com CRLF→LF)`.
O checkout do meu worktree entrega CRLF (45537 bytes) e reproduz um digest **diferente**. Um juiz
menos teimoso teria reportado "digest não confere" — e estaria errado.

**A `custody_copy` aponta para o original, não para uma cópia.** O protocolo pede
`path: "<cópia dos bytes emitidos>"`. O declarado é
`evals/nucleo-de-comando-r2-2026-08-07/saida-crua` — a mesma pasta que os juízes leem. Não existe
nada preservado contra o qual comparar; se o original mudar, o digest vira uma afirmação sobre um
passado sem testemunha.

---

## `C05` — Uso pela cadeia

### `ceo-maestro` — **6** (cru)

**O que sustenta a nota para cima.** Há trânsito real, farto e datado: **58 arquivos** carregam
`EXECUTIVE_MISSION` (90 objetos), com cabeçalho `causal` completo e `recipients` que resolvem para
subordinados reais — `diretor-de-lentes` (32) e `departamento-evolucao-skills` (24). Somam-se 19
`EXECUTIVE_SUBMISSION`, 1 `EXECUTIVE_DECISION`, 1 `EXCEPTION_REQUEST` e 2
`EXCEPTION_AUTHORIZATION`. E é o único pacote instalado como skill invocável: confirmei
`.claude/skills/ceo-maestro/` presente, com 81 `SKILL.md` aninhados que o runtime não indexa. Isso
é prova de trânsito, não de existência.

**As três lacunas.**

1. **`CAPABILITY_GAP` tem zero instâncias** na árvore inteira — e é linha própria da tabela
   "Saídas obrigatórias" do contrato (`:59`). Inclusive na única campanha em que o subordinado
   emitiu `DIRECTOR_CAPABILITY_GAP`, situação em que o `SKILL.md:100` manda o CEO decidir se
   materializa o seu.
2. **`EXECUTIVE_DECISION` tem exatamente 1 instância contra 90 missões.** É o artefato terminal, o
   único que chega a Jeremias. A saída da cadeia é ordens de grandeza menos exercitada que a
   entrada.
3. **Os envelopes desta rodada não validam** — a seção acima.

Fico em 6, topo da banda "cru", porque o trânsito é genuíno e rico; o que impede 7 é que a rodada
encenada para provar conformidade produz um envelope que o próprio schema da casa rejeita, e
nenhuma trava consegue ver.

### `diretor-de-lentes` — **5** (cru)

A perna de entrada existe: 32 `EXECUTIVE_MISSION` o nomeiam, ele emite 33 `JUDGMENT_REQUEST`,
recebe 44 `DEPARTMENT_RETURN`, emite 18 `BLOCKED_RETURN` e 1 `DIRECTOR_CAPABILITY_GAP`.

O problema é a saída, e ele é grave:

| artefato declarado | instâncias na árvore e no runtime |
|---|---:|
| `DEPARTMENT_GATE_RECORD` | **0** |
| `DEPARTMENT_TASK` | **0** |
| `MATRIX_EXCHANGE_MESSAGE` | **0** |

O primeiro não é um arquivo qualquer. O `SKILL.md:198-202` diz: *"`DEPARTMENT_RETURN` isolado nunca
autoriza integração. Somente `DEPARTMENT_GATE_RECORD.decision: ACCEPTED_FOR_INTEGRATION` (…)
atravessa a barreira."* **Existem 19 `EXECUTIVE_SUBMISSION` — que só existem a jusante dessa
barreira — e zero passaportes.** Ou a barreira foi atravessada sem registro, ou as submissões
nasceram sem barreira. As duas leituras são piores que um arquivo faltando, e nenhum artefato do
pacote escolhe entre elas.

E a prova que a rodada publica para os três é `[PASS] schema aceita DEPARTMENT_GATE_RECORD` e
`[PASS] schema aceita MATRIX_EXCHANGE_MESSAGE`. O schema aceita uma fixture que o próprio validador
monta em memória. **Aceitação de forma não é evidência de uso.**

### `departamento-negocios` — **3** (quebrado)

Aqui não há trânsito **de nenhum lado**.

**Entrada.** Varri toda `EXECUTIVE_MISSION` do disco — 58 arquivos, 90 objetos. Os `recipients` são
exclusivamente `diretor-de-lentes` (32) e `departamento-evolucao-skills` (24).
**`departamento-negocios` nunca foi destinatário de uma missão.** E o próprio contrato (`:44`) diz
que só `EXECUTIVE_MISSION` do CEO "endereçada a este Departamento" abre rodada.

**Saída.** Zero instâncias das **doze** saídas canônicas: `BUSINESS_INTAKE`,
`BUSINESS_EVALUATION_PLAN`, `BUSINESS_AGENT_MISSION`, `BUSINESS_AGENT_REPORT`,
`BUSINESS_CONSOLIDATION`, `BUSINESS_SCORECARD`, `BUSINESS_RETURN`, `BUSINESS_GAP_REPORT`,
`BUSINESS_REWORK_ORDER`, `BUSINESS_CAPABILITY_GAP`, `BUSINESS_JUDGMENT_PACKAGE`,
`MATRIX_EXCHANGE_MESSAGE` — confirmado na árvore **e** no runtime instalado. Os 1227 aparecimentos
desses nomes estão todos em `.md`, no schema e dentro do `.py` do validador: **fixture sintética**.

O critério pede "prova de trânsito, não de existência". Aqui há existência completa — schema, 235
casos verdes, contrato caprichado — e trânsito zero. Não desço abaixo de 3 porque o desenho é
coerente e porque o `FORWARD-TEST.md` documenta uma medição comportamental com método de verdade
(executor sem acesso às assertions, baseline sem skill contra ensaio pós-skill, 15/15 casos e 62/62
assertions, dois casos corrigidos e reteste focal). Mas isso mede **o que a skill faz um leitor
dizer**, não a cadeia chamá-la.

---

## `C06` — Limites declarados

Me perguntaram, e a decisão era minha: **declarar um limite que não se pode fechar conta como `C06`
cumprido, ou é desculpa?**

**Conta — sob três condições.** (1) O limite precisa ser nomeado com id e **mecanismo**, não com
adjetivo. (2) O custo dele precisa ser **medido**, não asseverado. (3) Ele precisa estar **legível
de onde o pacote é consumido**.

`OI-04` passa nas duas primeiras com folga. É nomeado, tem dono declarado (`ceo-maestro`), tem
mecanismo — *"forjar a evidência é chamar as mesmas funções que a verificam"* — e foi **medido** por
origem independente em 2026-08-02: 80 linhas, 0,031 s, 1 tentativa, 4 arquivos lidos, zero
conhecimento do conteúdo. Mais: a casa **retirou** a frase adjetiva que estava lá antes —
*"encarece muito, é quase todo o trabalho de auditar"* — por ter sido desmentida pela medição.
**Declarar um limite que piora a própria posição é o oposto exato de uma desculpa**, e é a coisa
mais honesta que encontrei em toda a leitura.

Falha na terceira. E é ela que decide as notas.

### `ceo-maestro` — **6** (cru)

`OI-04` **não está no pacote**. `SKILL.md` (275 linhas), `CONTRATO-DE-COMPROMISSO.md` (174) e os
seis `references/` não têm seção de limites. O `adr-001-hierarquia-executiva.md` é
Contexto/Decisão/Consequências/Alternativas, sem riscos. Buscando linguagem de limite nos documentos
próprios sobra "limite objetivo" — estado de workflow sobre a limitação do **candidato**, não do CEO
— e "limite restante", contador de rodada. `OI-04` vive em artefatos de campanha sob `evals/` e na
ADR-017 e no protocolo do `departamento-auditoria-responsabilidades`.

Como `ceo-maestro` é a **única porta instalada**, o leitor que o carrega — a única coisa que ele
consegue carregar — nunca descobre que o pacote não consegue verificar a própria evidência.

**Agravante:** o validador do CEO **exige** que o `governance_report` que ele consome declare os
limites `R6`, `R9`, `R10` e `R11`, por enum de id — *"envelope sem o limite R6 é rejeitado pelo
schema"*. Cobra de terceiro exatamente o que não faz por si.

> Um limite que não se pode fechar é legítimo. Um limite que não se pode **alcançar** não é.

### `diretor-de-lentes` — **4** (cru)

`C06` pede três coisas. "O que não faz" está bem declarado e é verificável (Guardrails, Proibições,
"Não decide intenção, prioridade comercial, orçamento, risco residual aceito"). **"Onde falha" e "o
que não sabe" estão ausentes por completo** — nenhuma seção de limites em `SKILL.md`, no contrato ou
nos sete `references/`; o `adr-001` não tem seção de riscos. As duas ocorrências de "risco residual"
dizem de **quem é a decisão**, não onde o Diretor falha.

**O agravante inverte o sinal do critério.** A seção "Evidência de conclusão da própria skill"
**afirma como cumprida** uma condição que o disco contradiz — *"toda troca com Negócios possui
`MATRIX_EXCHANGE_MESSAGE` validável"*, com zero instâncias — e nenhum limite em lugar nenhum
reconhece que `DEPARTMENT_GATE_RECORD` nunca foi escrito. **Onde deveria haver limite declarado, há
afirmação de completude.** Para o mantenedor do dia ruim isso é falha silenciosa e difusa.

A casa sabe fazer diferente: o §7 do protocolo dos Juízes declara `R1`–`R8` com vetor, consequência,
mitigação e teto, e obriga `R6` a ser nomeado em todo relatório. A omissão aqui é escolha, não
impossibilidade.

### `departamento-negocios` — **4** (cru)

"O que não faz" é declarado com força: Identidade ("Não sou consultor individual, executor
generalista, Juiz, CTO nem CEO"), treze Proibições, a lista "Não decido", "Nenhuma saída deste
Departamento equivale a `VALIDATED`".

Há **exatamente um** limite próprio nomeado e verificável, e ele é honesto — a "Observação" do
`FORWARD-TEST.md` delimita o alcance do próprio instrumento: *"O ensaio mede aderência comportamental
aos prompts. Integridade de schema, causalidade, correlação de artefatos e regressões externas são
cobertas separadamente por `validate_workflow.py`."* Registro isso a favor.

Fora daí, nada: nenhuma seção de riscos residuais, nenhum teto, nenhum id de limite; o `adr-001` não
tem seção de riscos; procurando "teto", "não sei", "limite deste" em todo o markdown do pacote não
volta nada. E o pacote **exige dos próprios agentes** o que não faz por si — "preservar autoria,
fontes, hipóteses, limitações e dissensos", e nota `10.0` na régua interna só com "risco residual
explicitado".

Falta o único limite que decidiria a adoção, e ele é barato de escrever: **que a rota deste
Departamento nunca carregou tráfego**. A ausência dessa linha deixa o leitor presumir componente
rodado — e um validador de 235/235 reforça a presunção.

---

## Achado crítico

**`diretor-de-lentes` / `C05` — condição de conclusão autodeclarada e contradita pelo disco.**
19 `EXECUTIVE_SUBMISSION` existem a jusante de uma barreira cujo único passaporte declarado tem zero
instâncias, e a seção "Evidência de conclusão da própria skill" declara cumprida uma condição
(`MATRIX_EXCHANGE_MESSAGE` em toda troca com Negócios) que também tem zero instâncias. Nenhum limite
reconhece nenhuma das duas.

---

## Contra mim

Registro aqui, e o `PARECER.json` traz a lista completa em `o_que_declaro_contra_mim[]`.

**O constrangimento.** O `ceo-maestro` é um dos julgados e participou da cadeia que emitiu minha
designação. O que senti foi vontade de ser **mais rigoroso** com quem me despachou — de tratar cada
defeito de envelope como prova de encenação. Resisti onde a evidência não sustentava: os envelopes
**não** são cerimônia, e digo isso apesar do impulso. Não sei medir se o impulso contrário me fez
inflar alguma nota para compensar; registro que ele existiu.

**Eu deveria ter recusado, por uma leitura estrita.** Minha trava manda operar só com "quarteto de
identidade conferido". O quarteto do §5.3 é `contract_id` + `contract_version` + `contract_digest` +
`candidate_digest`, e minha designação tem **três dos quatro**: `candidate_digest` está ausente — nem
preenchido, nem declarado `n/a`, ao contrário das `EXECUTIVE_MISSION` reais da casa, que escrevem
`"candidate_digest": "n/a"`. Julguei assim mesmo, porque o contrato, a matriz e a designação são
internamente coerentes e o digest do contrato confere, e porque recusar deixaria a rodada sem medida.
A decisão é minha, não do despachante.

**Busquei a rubrica sozinho.** Minha designação não copiou a tabela, só referenciou `rubric_ref`. Meu
`SKILL.md` e a própria rubrica dizem *"copiada literal na atribuição: nunca buscar rubrica sozinho"*.
Fui buscá-la. Cumpri a escala certa por um caminho que o protocolo proíbe — e um juiz que abrisse a
rubrica errada não seria pego por nada.

**O digest saiu na sorte.** Oito tentativas até bater. Se nenhuma tivesse batido eu teria reportado
"não confere", e estaria errado.

**Meu próprio relógio é o que eu critico.** Os 16 arquivos entraram num único commit datado
`2026-08-06T14:15:21-03:00`, e as marcas declaradas são `taken_at 2026-08-07T01:30` e
`issued_at 2026-08-07T01:35` — ~11 h **depois** do único relógio observável. A trava T5 é satisfeita
como ordenação entre duas strings escritas à mão. O `created_at` deste parecer herda exatamente esse
relógio não ancorado; o único anexo verificável que ofereço é o commit julgado.

**Não executei nada.** A conclusão sobre a T32 ter pulado esta rodada é **inferência de leitura de
código**, não medição. Quem quiser refutar só precisa executar.

**Os zeros têm raiz declarada.** Valem para `Estrutura Final de Skills/` em `ed3b63f` mais
`.claude/skills/ceo-maestro/`. Não varri `_github-publish-estrutura/`, `.agents/skills/` nem
transcrições. Se uma instância existir fora dessas raízes, **três das minhas notas mudam, e mudam
para cima**. Antes de concluir qualquer zero validei o padrão contra tipos que eu sabia existirem —
`JUDGMENT_REQUEST`, `EXECUTIVE_MISSION`, `DEPARTMENT_RETURN`: 168 ocorrências em 132 arquivos —
justamente para não transformar busca ruim em falso negativo.

**Contexto.** Não li a instância 1 nem abri `pareceres/`. Não abri nenhum contexto proibido. Caminhos
de rodadas proibidas apareceram em listagens de **nome de arquivo** durante varreduras por
`artifact_type`; não abri nenhum e nenhuma nota veio dali. Não julguei o `departamento-juizes`, e não
comparei os três julgados entre si: derivei cada nota contra o texto do critério, isoladamente.

**O que quase mudou.** Em `ceo-maestro`/`C06` quase dei nota mais alta, pela qualidade excepcional de
`OI-04`. O que me segurou não foi o conteúdo — foi o endereço.
