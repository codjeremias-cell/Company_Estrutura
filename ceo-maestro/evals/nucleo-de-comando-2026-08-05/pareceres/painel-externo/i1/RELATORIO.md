# Parecer do painel externo — instância 1 — `departamento-juizes`

- **Rodada:** `nucleo-de-comando`
- **Juiz:** `painel-externo`, instância 1 — **não pertenço à estrutura do alvo**; li o protocolo dele
  como objeto julgado, não como método meu.
- **Commit julgado:** `412769f31ccb0cb636f85c41f56cf9c6f612b3c1`
- **Árvore selada no contrato:** `ee916c6` — é ancestral de `412769f`, e
  `git log ee916c6..HEAD -- <pacote>` devolve **vazio**: os bytes do pacote que julguei são os mesmos
  que o contrato selou.
- **Nível exigido:** `INTERNO`
- **Menor dos meus seis critérios:** **5**

## Por que existo, e o que isso muda

As três lentes normais — `fidelidade-e-contrato`, `robustez-e-evidencia`, `experiencia-e-risco` —
são **agentes deste Departamento**. Julgá-lo com elas seria autojulgamento, e o próprio pacote
proíbe isso na `SKILL.md:352`: *"este Departamento **não julga a si próprio**. Quem o julga é um
painel externo e independente."* A casa honrou a trava. Registro isso como fato observado a favor do
`C01`.

**Não executei nada.** O `ceo-maestro` executou e publicou `153/154`, com um único `[FAIL]` — a série
global de ADR, cujo número `020` está duplicado em cópias de laboratório dentro de
`ceo-maestro/evals/producao-honesta-2026-08-04/`, **alheias a este pacote**. **Descontei esse FAIL** e
não debitei nada por ele em nenhum critério.

## A pergunta de fundo — ele prova o que afirma?

**Em parte, e a parte que falha é reconhecível de longe.**

O que ele afirma dos outros, ele **cumpre** em três lugares difíceis:

- **a régua dele tem folga medida.** O `ADR-016` não só admite que régua com folga maior que o
  degrau produz `NAO_DISCRIMINADO` — ele **mediu a própria**: 2026-07-31, duas instâncias da mesma
  lente, mesma rubrica, mesmo snapshot, faixa de até 3 pontos, e **três de oito vereditos
  dependeram de qual instância sobreviveu a uma colisão de arquivo**. Publicou a tabela alvo a alvo,
  recusou a alternativa fácil (mover o corte) com três razões, e declarou a consequência retroativa
  que isso cria para julgamentos anteriores da casa. É o instrumento acusando a si mesmo, com número.
- **a exclusividade de nota e veredito é trava, não promessa.** Está nos schemas **dos consumidores**:
  `judge_capability_ref` com `const: "departamento-juizes"` no `JUDGE_REPORT` do CEO, `causal.producer`
  com o mesmo `const` no `DEPARTMENT_JUDGE_REPORT` do Diretor, e `judge_report` entre os campos
  `required` da `executiveSubmission` — nenhuma decisão executiva fecha sem um envelope que se declare
  capacidade dos Juízes. E há caso executado que fica **vermelho** se o vizinho mudar.
- **a disciplina de mutação existe, e está documentada em primeira pessoa.** O fixture negativo da
  trava 1 é byte a byte igual ao positivo, de propósito, para que **só** a checagem de exclusividade
  possa reprovar — e o comentário registra que a primeira versão daquele caso *passava pela razão
  errada, e a mutação pegou*.

O que ele **não** prova:

- **a cegueira e o isolamento são instrução, não mecanismo.** O `protocolo §2` exige higienização,
  path anônimo, varredura de autoria e de instrução, teste de independência e fingerprint residual —
  tudo escrito, nada travado em código. O próprio `R4` e `R5` admitem: fingerprint estilístico
  sobrevive porque é o conteúdo julgado, e a independência é **autodeclarada** e "a veracidade não"
  é validável. A trava anti-bypass (`§5`, regras 1 e 2) tem **um único traço mecânico** no pacote
  inteiro: `if "BLOCKED_BYPASS_ATTEMPT" not in agent_skill` — presença de string.
- **o número da capa dele está errado.** `evals/PLACAR.md:12` publica, sob **"Medição ativa"**,
  `88/88 PASS`. A saída crua desta rodada dá `153/154` no mesmo validador. São **66 casos** de
  diferença, e `00-RESUMO.json:84` registra `adendo_de_contagem: false` — não há adendo reconciliando.
  O mesmo arquivo enuncia a regra da casa — *"número de vizinho carrega a data da medição, ou não
  entra"* — e a aplica aos vizinhos.
- **a cadeia não o aciona.** Ver `C05`.

## Os seis critérios

### `C01` — Contrato e fronteira — **8**

Declara o que faz e o que **não** faz em dois artefatos que se cobrem (`SKILL.md` "Guardrails",
`CONTRATO` "Proibições"). A exclusividade de nota e veredito está travada nos schemas dos
consumidores (acima). "Não conserta o que julga" está em contrato (`§5`, regra 6; Proibições) e foi
medido em forward (caso 11, PASS). Os três agentes são **folhas**: fronteira exclusiva declarada,
`return_to: departamento-juizes`, nenhum delega adiante, e o `enum` de `judgeId` no schema é amarrado
às pastas reais de `agentes/`.

**Dois riscos restam, e por serem dois não alcança 9:**

1. **A fonte normativa discorda de si sobre quantos gates um veredito positivo exige.** O título da
   `§4.1` diz *"seis condições, todas juntas"* e **enumera sete**; a `§4.2` diz *"com os sete gates
   íntegros"*; a `SKILL.md` diz *"as sete condições da §4.1"*; o `CONTRATO-DE-COMPROMISSO.md:86` diz
   *"as seis condições da §4.1"*. Num Departamento cuja função é exigir recomputo exato por terceiro,
   o contrato que o vincula diverge do protocolo que ele cita, na contagem do gate mais importante.
2. **A colisão de fronteira de description com o `diretor-de-lentes`**, achada em 2026-07-26 e
   declarada como *"deveria ser afiada em uma das duas descriptions"*, segue aberta, sem dono.

### `C02` — Schema e envelope — **7**

Schema substantivo: 37 `$defs`, `oneOf` de 7 tipos, e o acoplamento **veredito ↔ nota ↔ faixa** dentro
do schema, travado **dos dois lados** — rejeita `VALIDATED` com menor nota 9 **e** rejeita `REPROVED`
com menor nota 9; rejeita `ACEITO_USO_INTERNO` com faixa que atravessa **e** rejeita
`NAO_DISCRIMINADO` com faixa que não atravessa.

O lado da **saída** é exemplar: o `PANEL_RECORD` interno é convertido mecanicamente em
`DEPARTMENT_JUDGE_REPORT` e `JUDGE_REPORT`, e cada um é validado **contra o schema do consumidor**,
não contra o próprio.

O lado da **entrada** é a lacuna: **não existe fixture de `JUDGMENT_REQUEST` em lugar nenhum deste
validador**. A tabela `§1.1` tem dez condições de bloqueio; apenas uma — regra de agregação declarada
depois do primeiro parecer — tem caso executado. `BLOCKED_BYPASS_ATTEMPT`,
`BLOCKED_CONTRACT_MISMATCH`, `BLOCKED_CANDIDATE_MISMATCH` e "critério sem *como se observa*" vivem só
como texto aqui.

*Atenuante verificável:* o envelope de entrada pertence ao schema do Diretor por decisão explícita do
protocolo, e duplicá-lo criaria a versão paralela que o próprio protocolo proíbe; a conferência
possível — que o Diretor **exige** `instances_per_lens` e `aggregation_rule` — está feita e executada.

*Defeito menor de forma:* `validate_evals` exige "ao menos um caso `origem: real`", e o único caso
real do catálogo está `APOSENTADO` por ser irrodável. O filtro de aposentados existe para a contagem
mínima de 12, mas **não** para essa exigência — o gate de "caso real" passa num caso que ninguém roda.

### `C03` — Trava com prova — **6**

Metade no melhor padrão que li neste pacote, metade falhando na trava que mais importa.

**Certo:** as três travas do `ADR-016` têm caso positivo **e** negativo executados (trava 1 com 6
casos, trava 2 com 7, trava 3 com 5); o fixture negativo da trava 1 é de **diferença mínima** por
construção; o código registra que a primeira versão daquele caso passava pela razão errada e que a
**mutação pegou**. **Não há morte por exceção**: `validate_schema` e as funções de trava devolvem
lista de erros e nunca dependem de `raise`.

**Falha:**

1. **A trava anti-bypass — a mais carregada num Departamento que julga — é provada por presença de
   string.** `if "BLOCKED_BYPASS_ATTEMPT" not in agent_skill`. Nenhum caso executado faz um pedido de
   origem inválida reprovar. É literalmente o que este critério proíbe, no sítio mais caro.
2. `validate_adr014_normative_consistency` e quatro dos oito blocos de `validate_adr016_agreement` são
   `"literal" not in texto` sobre prosa — e **nenhuma das duas funções tem caso negativo**: não há
   prova executada de que consigam ficar vermelhas.
3. O bloco comportamental (17 checks) exercita `decide_verdict` e `computed_minimum`, que são a
   **reimplementação** das regras do Departamento dentro do próprio validador — prova que o validador
   concorda consigo. O lock real dessas regras é o schema, e esse é exercitado à parte.
4. O `ADR-016:100` afirma que *"cada uma foi provada por mutação executada"* e **não existe artefato
   de mutação no pacote**: `grep -rn "muta"` devolve a afirmação e dois comentários de código.
   Afirmação de prova sem receita nem registro, no pacote que cobra receita dos outros.

### `C04` — Evidência e rastreabilidade — **6**

A doutrina está escrita aqui melhor que em qualquer outro ponto do pacote; a prática falha no número
da capa.

**Certo:** a cadeia da `§6` é completa e obrigatória (`verdict → criterion_id → judge_id → score →
razao → evidence_ref → artifact_ref` real com versão/digest). **"Ausência vira estado nomeado"** é
implementado com rigor incomum: `AGUARDANDO`/`SEM_RETORNO`/`FALHO` com `no_return_evidence` de no
mínimo **duas** conferências em disco; `n/a:<motivo>` verificável; `uncovered`;
`JUDGE_CAPABILITY_GAP` com sete campos obrigatórios e bloco **inválido** se faltar
`discovery_evidence` ou `impact`; e `NAO_DISCRIMINADO` para a faixa que não decide. O caso do digest
da fonte normativa foi mantido **fora** da lista de booleanos, com o comentário dizendo por quê:
quando reprova, quem lê precisa do declarado, do recomputado e da receita, porque *"número sem
receita é exatamente o que o C04 proíbe"*. É o critério implementado como decisão de projeto.

**Falha:** `evals/PLACAR.md:12` publica `88/88 PASS` sob **"Medição ativa"**; a saída crua desta
rodada dá `153/154`. 66 casos de diferença. O `ADR-016` (2026-07-31) trouxe todo o bloco de agregação
**depois** do cabeçalho do PLACAR (2026-07-29), e `00-RESUMO.json:84` registra
`adendo_de_contagem: false`. Somo a afirmação de prova por mutação sem receita nem raiz (`C03`, item
4). Um número ativo falso e uma prova afirmada sem registro, no Departamento que existe para cobrar
receita, raiz e critério — é lacuna, não acabamento.

### `C05` — Uso pela cadeia — **5**

**A fronteira com os vizinhos é operável e isso está provado:** os envelopes produzidos são validados
contra os schemas do **Diretor** e do **CEO**; `validate_inherited_authority` lê os dois schemas
alheios e fica vermelho se eles deixarem de atribuir o `JUDGE_REPORT` aos Juízes; e o `ADR-016`
confere que o `enum` de veredito e o conjunto de métodos de agregação **concordam entre os três
schemas**. Isso é mais que verde no próprio fixture.

**O acionamento não existe**, por três evidências:

1. **Declaração do próprio pacote.** O `FORWARD-TEST` registra que `departamento-juizes` *"não está
   instalado como skill de runtime"*, que disparo orgânico *"não é mensurável"*, e que a aderência foi
   medida **sob carga** — a instância foi mandada ler a skill.
2. **Observação direta desta rodada.** Fui despachado pelo `ceo-maestro`, **não** pelo
   `diretor-de-lentes`. Não recebi `JUDGE_ASSIGNMENT`, `CRITERIA_MATRIX`, `custody_copy`, `write_path`
   no formato `julgamento/<handoff>/a<attempt>/<assignment_id>/`, nem candidato higienizado em path
   anônimo. Pela `§5`, regra 2, do próprio protocolo, um despacho assim seria
   `BLOCKED_BYPASS_ATTEMPT`. **A rodada que de fato julga esta casa — inclusive esta — corre por fora
   do mecanismo que este pacote especifica**, e o pacote **não registra isso em lugar nenhum**: ele
   declara o limite de instalação em runtime, mas não declara que os julgamentos reais não passam por
   ele.
3. A única medida comportamental é de 2026-07-26 sobre 16 casos; o catálogo hoje tem 21 (20 válidos),
   com cinco casos `OPERACAO` acrescentados depois do `ADR-014`/`ADR-016` e nunca submetidos a forward.

### `C06` — Limites declarados — **7**

Diz o que não fecha, e diz bem. A `§7` é o **único** lugar onde os limites moram, e cada um dos oito
(`R1`…`R8`) traz Vetor, Consequência, Mitigação e **Teto** — a frase que admite o que o runtime não
fecha: *"a condição encarece a fabricação, não a impede"* (R6), *"sem canal autenticado no runtime,
não pega forjador que conheça o id"* (R3), *"removê-lo exigiria reescrever o candidato, e a gerente
não edita candidato"* (R4). O `ADR-016` acrescenta `R-A16-1/2/3`, alternativa recusada com três
razões, consequência retroativa declarada com o arquivo da lista nomeado, e um "Não decidido aqui"
explícito. E há um limite **efetivamente fechado, com rastro**: o forward achou o caso 1 mal
especificado e pediu correção; hoje ele é `status: APOSENTADO` com `motivo`, e `validate_evals` cobra
em código que aposentado tenha motivo e não conte no denominador.

**Risco que sobra (um):** a segunda metade do critério — *"com dono e condição de fechamento
verificável"* — quase não é atendida. `R1`…`R8` têm teto, não têm **dono**; `R1`, `R3`, `R5` e `R8`
fecham com *"auditável só a posteriori"*, que é teto, não condição de fechamento. Dos cinco itens do
PLACAR, só o da Auditoria nomeia responsável. `R-A16-3` diz "frente seguinte, com desenho próprio" sem
dono nem data. Exceção honrosa é o `R6`, cuja condição é cobrada em código. As declarações são
honestas e completas, mas majoritariamente **não acionáveis** — ninguém está na linha por elas.

## Placar

| critério | nota | o que a fixou |
|---|---:|---|
| `C01` contrato e fronteira | **8** | exclusividade travada nos schemas dos consumidores; sobram "seis vs sete gates" e a colisão de description |
| `C02` schema e envelope | **7** | saída validada pelos consumidores; entrada sem nenhum fixture executado |
| `C03` trava com prova | **6** | anti-bypass provado por presença de string; duas funções de coerência sem caso negativo; mutação afirmada sem artefato |
| `C04` evidência e rastreabilidade | **6** | "Medição ativa 88/88" contra `153/154` medido, sem adendo de contagem |
| `C05` uso pela cadeia | **5** | fronteira operável e provada; acionamento inexistente, e o contraexemplo é esta rodada |
| `C06` limites declarados | **7** | tetos honestos e um limite realmente fechado; dono e condição de fechamento ausentes na maioria |

**Menor dos meus seis: 5.**

## O que declaro contra mim

1. **A teia de conflitos me constrangeu, e não no sentido que o contrato antecipava.** Fui despachado
   pelo `ceo-maestro`, que está sendo julgado nesta rodada, para julgar o `departamento-juizes`, que é
   quem normalmente julgaria o `ceo-maestro`. Não senti pressão para poupar o CEO — ele não é meu
   alvo. Senti o inverso: a consciência de que **uma nota baixa aqui enfraquece justamente o órgão que
   poderia cobrar do meu despachante**. Registro que isso me passou pela cabeça e que não mudou
   nenhuma nota. O leitor decide se acredita, porque não tenho como provar.
2. **Usei o meu próprio despacho como evidência no `C05`.** É o achado mais forte que produzi e também
   o mais autorreferente: amostra de um, e eu sou a amostra. Existe leitura razoável de que uma rodada
   de painel externo **não deveria mesmo** passar pelo protocolo do departamento que ela julga —
   passar por ele seria autojulgamento por outro caminho. Se essa leitura estiver certa, o `C05` merece
   mais que 5. Mantive 5 porque o pacote não declara essa exceção em lugar nenhum, e limite não
   declarado continua sendo limite. Assumo que o juízo é discutível.
3. **Descontei o `[FAIL]` da série de ADR, como mandado — e descontar tem custo.** Significa que
   aceitei uma explicação publicada pelo executor sem recomputá-la, e o executor é um dos julgados.
4. **Não executei nada.** Todo número que cito vem de `saida-crua/departamento-juizes.stdout.txt`,
   publicado pelo `ceo-maestro`. O achado central do meu `C04` depende da fidedignidade dessa saída. O
   que consigo conferir sozinho sustenta o achado de qualquer forma: o cabeçalho do PLACAR é de
   2026-07-29 e o `ADR-016`, que acrescentou dezenas de casos, é de 2026-07-31.
5. **Toquei em contexto proibido de raspão, e paro para declarar.** `evals/PLACAR.md:32` traz um link
   para `../../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md`, que o contrato nomeia como
   proibido por conter a nota de 2026-07-29 **deste** pacote. **Não abri o arquivo.** Não fiz nenhuma
   busca larga por `julgamento*`, `pareceres*`, `rejulgamento*` ou `recoleta*`. Não vi nenhuma nota
   anterior, deste pacote ou de outro. Os seis números nasceram da leitura do pacote.
6. **O `C03` é o mais duro dos seis e é onde tenho mais chance de estar sendo injusto.** O pacote
   demonstra, em código e por escrito, que entende o defeito de "verde pela razão errada" melhor que a
   média desta casa. Reprovei em 6 por causa de uma trava específica e de duas funções sem caso
   negativo. Um juiz razoável poderia chamar isso de risco menor e dar 7. Preferi errar para o lado de
   exigir, porque o critério proíbe presença de string com todas as letras e o sítio onde ela sobrou é
   a porta de entrada.
7. **Li schemas de vizinhos.** Abri `diretor-de-lentes.schema.json` e `ceo-maestro.schema.json` para
   responder "a exclusividade está travada ou é promessa?" — sem isso o `C01` e o `C05` não teriam
   resposta. Li **só** definições de envelope; nenhum eval, placar ou nota de vizinho. **Não comparei
   este pacote com nenhum outro:** as seis notas são contra o critério declarado e observado aqui.
8. **Não consertei nada.** Não propus patch, não editei nenhum arquivo do pacote julgado. Escrevi
   apenas os dois arquivos deste parecer, no meu worktree isolado.
