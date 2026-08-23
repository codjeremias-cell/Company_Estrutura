# Parecer — painel externo, instância 2 — `departamento-juizes`

- **Rodada:** `nucleo-de-comando-r2` · **Designação:** `ASSIGN-NUCLEO-R2-PAINEL-I2`
- **Commit julgado:** `ed3b63f273e104f7b2e5d4a6f1af61f5b91d80e3` (`ed3b63f`, HEAD de `master`)
- **Contrato:** `CONTRATO-NUCLEO-R2-20260807`, digest **conferido** —
  `sha256:3a4750d9e983769c555db20d731fc4f012ca24ea851d2211cdc4f93a343756ed`,
  recomputado sobre `00-CONTRATO.md` com CRLF→LF, sem BOM, 5453 bytes normalizados. Bate.
- **Nível exigido:** `INTERNO` · **Não executei nada.** Li e critiquei a medição.

| critério | nota | o que fixa |
|---|:--:|---|
| C01 contrato e fronteira | **8** | fronteira honrada na prática; contagem de portões divergente entre norma e contrato |
| C02 schema e envelope | **8** | derivação validada contra o schema do vizinho; refs de evidência fabricadas na derivação |
| C03 trava com prova | **7** | 71 casos negativos executados; a trava-assinatura do pacote é prosa aqui |
| C04 evidência e rastreabilidade | **7** | adendo exemplar; `PLACAR.md` ainda publica `88/88` como "Medição ativa" e ninguém aponta para o adendo |
| C05 uso pela cadeia | **6** | **lacuna** — o envelope que transitou não é o envelope declarado |
| C06 limites declarados | **8** | §7, PLACAR e ADR-022 são modelo; a linha R1 envelheceu e não foi redeclarada |

**Mínimo dos meus critérios: 6, fixado por `C05`.**

---

## O que eu vi primeiro, antes de qualquer roteiro

Abri a árvore: 26 arquivos, `SKILL.md` de 375 linhas, protocolo de 513, schema de 1923, validador
de 2425. A primeira coisa que impressiona é que o pacote **cumpre consigo mesmo a regra que impõe
aos outros**: a `SKILL.md` fecha com uma "trava reflexiva" dizendo que ele não se julga, e o ato
que estou executando é a prova de que a trava foi honrada — sou externo porque as três lentes são
agentes dele.

A segunda coisa é o tom. Este é um pacote que **escreve contra si mesmo com frequência**: o
comentário da trava 1 confessa que a primeira versão do caso "passou pela razão errada"; o
`PLACAR.md` tem uma seção inteira chamada "O que ainda não foi provado" com cinco itens numerados,
um deles acusando um vizinho; a `FORWARD-TEST.md` declara que mediu aderência **sob carga** e que
disparo orgânico "não é mensurável"; e o `ADR-022` abre com "este ADR baixa notas, ele não sobe
nenhuma", registrando que Jeremias foi informado disso **antes** de decidir. Isso é raro e conta.

A terceira coisa é onde o pacote não olhou: **para o que efetivamente correu por ele**.

---

## C01 — contrato e fronteira · **8**

**A favor.** A fronteira aparece quatro vezes e as quatro concordam: a "Lei de Ferro" da
`SKILL.md`, as seções *Autoridade* e *Proibições* do contrato, a §5 do protocolo e a tabela
*Recorte reescrito* de `origem-migracao.md`. Ela é negativa onde precisa ser — "orquestra e não
executa", "nunca pontuar critério por conta própria", "nunca aceitar pedido fora do
`diretor-de-lentes`" — e distingue explicitamente o vizinho: Auditoria **prova conformidade**,
testador **executa**, Diretor **integra**, CEO **fecha**, Jeremias **autoriza exceção**.

E é respeitada **na prática**, não só no texto: o `enum` de `judgeId` do schema é conferido em
código contra o conteúdo real de `agentes/`, e a trava reflexiva produziu este painel externo.
`origem-migracao.md` fixa a proveniência por SHA-256 arquivo a arquivo e diz, com todas as letras,
que a contagem de bytes "é contexto de escala, não identidade" — a lição certa, aplicada.

**Contra, e é concreto.** O pacote se contradiz sobre **quantos portões** existem:

| sítio | diz |
|---|---|
| `protocolo…md:363` (título da §4.1) | "**seis** condições, todas juntas" — e **enumera sete** |
| `protocolo…md:378` (§4.2) | "com os **sete** gates íntegros" |
| `SKILL.md:212` e `:269` | "as **sete** condições da §4.1" |
| `CONTRATO-DE-COMPROMISSO.md:86`, obrigação 11 | "as **seis** condições da §4.1" |

O documento que **vincula** diz seis. O sétimo é o `minimum_score_range` — acrescentado pelo
ADR-016 sem que o título da seção e a obrigação do contrato o acompanhassem. Não é cosmético num
pacote cuja função é contar portões: quem obedecer o contrato ao pé da letra pode aplicar seis e
deixar cair justamente o gate que o ADR-016 introduziu.

E o caso do validador que deveria pegar isso — *"ADR-014, rubrica, exemplos e SKILL são
coerentes"* — não pega, porque `validate_adr014_normative_consistency()` é uma sequência de
`if "<frase>" not in texto`. Presença de string não vê contradição aritmética.

**Por que 8 e não 7:** é um defeito único, localizado e não comportamental — a enumeração é
inequívoca, só a palavra que a conta está errada em dois sítios. **Por que não 9:** 9 pede risco,
e isto é defeito presente no texto.

## C02 — schema e envelope · **8**

**A favor, e é a melhor engenharia do pacote.** `additionalProperties: false` em toda parte,
condicionais reais (`BLOCKED` exige `abstencao`; `SEM_RETORNO`/`FALHO` exigem sinal terminal de
runtime; `NAO_DISCRIMINADO` exige `instances_per_lens >= 2` e é recusado quando a faixa **não**
atravessa), `write_path` com `pattern` amarrando handoff, attempt e `assignment_id`, `custody_copy`
com `taken_at` conferido em código contra `issued_at`.

O que me convence de verdade é a **derivação**: `derive_department_judge_report()` e
`derive_judge_report()` projetam mecanicamente o `PANEL_RECORD` interno e os resultados são
validados **contra o schema do vizinho**, não contra o próprio — e com casos negativos em que o
vizinho **recusa** (`9,49` carimbado como `VALIDATED`; faixa que atravessa carimbada como aceite
interno; parecer com produtor forjado). Isso é exatamente "o envelope de fronteira é o que o
vizinho consome", provado por execução e não por alegação.

**Contra.** Dois riscos, ambos nomeáveis:

1. A derivação **fabrica** `evidence_refs` como `evidence/<criterio>.json` em vez de propagar as
   refs reais das linhas do `scorecard`. A regressão de fronteira, então, nunca exercita a cadeia
   `razao → evidence_ref → artifact_ref` que a §6 do protocolo declara obrigatória. O envelope
   valida; a rastreabilidade dentro dele não é testada.
2. A definição operante do envelope **divergiu** do schema normativo — ver `C05`. E a divergência
   chegou ao ponto de outro validador da casa afirmar em comentário que *"a `JUDGE_ASSIGNMENT` de
   verdade não tem `write_path`"*, o que contradiz frontalmente este schema, onde `write_path` é
   `required` com `pattern`. O pacote não registrou isso em lugar nenhum.

## C03 — trava com prova · **7**

**A favor.** **71 dos 155 casos são `esperado rejeitado`** — casos executados que só ficam verdes
se a trava produzir erro. E o desenho evita as duas armadilhas que o critério nomeia:

- **Morte por exceção não conta como pega.** A lista `cases` é montada **antes** do laço de
  impressão, então qualquer exceção mata o processo com traceback em vez de virar um "rejeitado"
  gratuito. A estrutura garante isso, não a disciplina.
- **Mutação única sobre base provada válida.** Quase todo negativo é `copy.deepcopy` de uma fixture
  que tem seu **próprio caso positivo** no mesmo run, com **um** campo alterado. Isso dá poder
  discriminante que "qualquer erro serve" não daria sozinho.

E o pacote publica o próprio erro: o comentário da trava 1 conta que a primeira versão do caso de
colisão usava caminho malformado, ficava verde sob mutação, "passou pela razão errada, e a mutação
pegou" — por isso a emissão duplicada hoje é **byte a byte igual** à primeira, para que só a
checagem de exclusividade possa reprovar. É a lição "verificar presença não é verificar efeito"
aplicada com custo.

**Contra — três débitos, e o primeiro é grande.**

1. **A trava que o pacote mais alardeia não tem caso nenhum aqui.** §5 regra 1 — agente que opera
   sem `JUDGE_ASSIGNMENT` é `BLOCKED_BYPASS_ATTEMPT` — aparece na `SKILL.md`, no contrato, no
   protocolo e na `SKILL.md` de cada um dos três agentes. Nos 155 casos: **zero**. Nem positivo,
   nem negativo.
2. **Parte dos 155 é presença de string sem contraparte negativa.**
   `validate_adr014_normative_consistency()` é literalmente `if "<frase>" not in texto` — e é
   exatamente o caso que deveria ter pego o seis/sete do `C01`.
3. **Nenhum caso negativo afirma QUAL erro saiu.** `esperado rejeitado` é satisfeito por qualquer
   lista não vazia. A mitigação existe (mutação única sobre base válida) mas é **disciplina
   humana**, não trava — e a própria casa já registrou que aviso em prosa não previne erro.

Some-se: a prova por mutação das travas 1–3 está **afirmada num comentário de código** ("foi
provada por mutação executada"), não publicada como artefato reproduzível dentro do pacote. O
adendo publica uma mutação de verdade (colisão plantada → vermelho, removida → verde); as três
travas do ADR-016, não.

**Por que 7 e não 6:** 71 casos executados que reprovam, com fixtures desenhadas contra o falso
positivo, está muito além de "lacuna". **Por que não 8:** a trava-assinatura do pacote continua
sendo prosa dentro dele.

## C04 — evidência e rastreabilidade · **7**

**A favor.** O `PLACAR-ADENDO-2026-08-06` faz certo tudo o que a rodada cobra: receita **literal**
com `cd`, `PYTHONIOENCODING`, `PYTHONDONTWRITEBYTECODE` e o comando; delta explicado caso a caso
(`153/154 → 154/155`, **+1**, nomeado: *"nenhum placar de pacote declara total de cadeia como
estado corrente"*); a cascata da tarefa 24 explicada com a razão do FAIL do vizinho (18 FAIL → 1, e
por que dois deles eram cascata do `departamento-negocios`); e **mutação publicada** — colisão
plantada → vermelho, removida → verde. Diz até que o detector "se autotesta antes de julgar".

Ausência vira estado nomeado em toda parte: `SKIP` declarado, `AGUARDANDO`, `substrate:
desconhecido`, `JUDGE_CAPABILITY_GAP` como **bloco** com sete campos obrigatórios e nunca frase
solta, e `n/a:<motivo>` que não entra no mínimo.

**Contra — a deriva de contagem está viva, no arquivo canônico.**

`evals/PLACAR.md`, linhas 9–12, sob o título **"## Atualização ativa"** e na coluna literal
**"Medição ativa"**, publica:

```
| Validador determinístico do Departamento | **88/88 PASS** |
```

O valor vigente é **155/155**. Errado por 67 casos. E `grep -rn "PLACAR-ADENDO"` dentro do pacote
retorna **zero** ocorrências: **nada aponta para o adendo**. O contrato e a `SKILL.md` mandam o
leitor a `evals/PLACAR.md` ("os mesmos casos passam em teste independente registrado em
evals/PLACAR.md"); quem for lá lê 88/88 e não tem caminho até 155/155.

Redeclarar num arquivo órfão é redeclarar onde ninguém é mandado. E a ironia é fina: o próprio
adendo escreve *"o defeito é de forma, não de sítio"* — e deixa a mesma forma na própria linha de
cima. A trava da tarefa 34 pega total de **cadeia** afirmado no presente; não pega o número
**próprio** rotulado como "ativo".

Registro ainda, **contra a evidência da rodada e não contra o pacote**: `saida-crua/00-RESUMO.json`
publica aos juízes `departamento-juizes.inventario.subordinados_diretos: []`, com
`problemas_do_coletor: []`, quando o contrato deste pacote declara **três** subordinados diretos em
`agentes/`. O coletor foi versionado na tarefa 33 justamente para não publicar defeito do
instrumento como defeito do objeto; esta linha atravessou o gate de coerência.

## C05 — uso pela cadeia · **6 — lacuna nomeável**

**A favor.** `validate_inherited_authority()` **abre** os schemas do Diretor e do CEO e confirma,
em sete asserções, que eles continuam atribuindo aos Juízes o `JUDGE_REPORT`, o
`DEPARTMENT_JUDGE_REPORT` e a verificação independente, que o pedido é autoria do Diretor e que
retorna a ele. Se o outro lado mudar, **quebra aqui**. Isso é integração provada, não alegada. E
esta rodada instanciou seis `JUDGE_ASSIGNMENT` nomeando os três agentes reais, com
`return_to: departamento-juizes` — o que a rodada 1 não fez.

**Contra, e é o que o critério pergunta.**

**(1) Não há ator.** Os próprios envelopes declaram:
`issued_by: "departamento-juizes (papel declarado; ator unico de runtime)"`, e o pedido diz
*"Emitido pelo unico ator de runtime"*. Papel declarado não é trânsito — é o **R6** do próprio
pacote escrito dentro do envelope: *"a gerente pode fabricar os três pareceres sem invocar agente
algum"*. A honestidade é integral e conta no `C06`; ela não converte o registro em trânsito.

**(2) O envelope que transitou não é o envelope declarado.** Comparação literal, sem executar nada:

- Os oito `JUDGE_ASSIGNMENT` da rodada usam `write_path: "pareceres/<lente>/i<N>/"`. O `pattern`
  obrigatório do schema é `^julgamento/[A-Za-z0-9._-]+/a[0-9]+/[A-Za-z0-9._-]+/$`. Não casa — e a
  trava 1 em código exige ainda que o último segmento **seja** o `assignment_id`.
- Faltam `required`: `causal`, `candidate_digest`, `anonymized_candidate`, `contract_excerpt`,
  `evidence_index`, `forbidden_context`.
- Sobram chaves de topo (`contract_id`, `contract_version`, `contract_digest`, `pacotes`,
  `required_level`, `issued_by`) que `additionalProperties: false` recusa — e a própria
  `custody_copy` traz `arquivos`, que o `$defs.custodyCopy` não admite.
- O `01-JUDGMENT-REQUEST.json` seria recusado pelo schema **do Diretor**: faltam
  `judgment_request_id`, `causal`, `department_return_ref`, `candidate_digest`,
  `applicable_criteria`, `artifact_refs`, `evidence_refs`, `issued_at`; e `aggregation_rule` vem
  **sem `declared_at` e sem `rationale`** — exatamente o erro que a trava em código *deste* pacote,
  `trava_regra_declarada_antes_das_notas`, emite como `"aggregation_rule sem declared_at"`.
- O pedido traz **quatro** candidatos em modo `VALIDACAO`; a §1.0 manda devolver ao Diretor para
  reemissão, porque dois ou mais candidatos são `DISPUTA`.

**(3) Sete rodadas em bypass.** A lista fixada no validador do CEO registra sete rodadas que
julgaram **sem nenhuma** `JUDGE_ASSIGNMENT`.

**Conclusão do critério:** o **nome** do protocolo transitou; a **forma** dele não transitou nem na
rodada que se declara a primeira a correr "PELO PROTOCOLO". Existe prova de **existência do papel**;
não existe, no que posso inspecionar, prova de **trânsito da forma** — que é literalmente o que
`C05` distingue.

Isto **não é culpa do pacote**: quem escreveu os envelopes foi o operador da rodada. Mas `C05`
pergunta se o protocolo declarado é o que roda, não de quem é a culpa. Declaro contra mim, no
`PARECER.json`, que existe leitura oposta e defensável em que este critério vale 7.

**Por que 6 e não menos:** o contexto proibido me impede de conferir rodadas anteriores, onde a
forma declarada pode ter transitado; e a asserção de autoridade herdada é integração real.

## C06 — limites declarados · **8**

**A favor, e com folga.** A §7 é **sítio único** — o protocolo proíbe que os riscos sejam
declarados em qualquer outro ponto, só referenciados — com oito riscos identificados, cada um com
vetor, consequência, mitigação e **teto**. `R6` é nomeado **incondicionalmente** em todo relatório;
os demais, só quando a rodada depender deles. Os tetos são desconfortáveis de propósito: *"a
condição encarece a fabricação, não a impede"*; *"substrato não exposto fica desconhecido e a
independência permanece não verificada"*; *"sem canal autenticado no runtime, não pega forjador que
conheça o id"*.

O `PLACAR` traz cinco `SKIP` numerados, incluindo um que **acusa o vizinho** (os prompts
comportamentais do CEO não foram reexecutados, embora o próprio `README` do CEO exija) — limite que
custa caro declarar. A `FORWARD-TEST` declarou o limite que o campo depois confirmou: *não está
instalado como skill de runtime; disparo orgânico não é mensurável; a aderência foi medida **sob
carga***. E o `ADR-022` declara o **preço antes da decisão**, com quatro pendências nomeadas, dono
e condição de fechamento — inclusive `A22-03`, que admite que o instrumento pode estar medindo
ruído a 55% de separação. Declarar que o próprio critério novo pode medir ruído é o oposto de
vender.

**Contra.** A linha **R1 envelheceu nos dois sentidos** depois de 2026-08-06 e não foi
redeclarada:

- a coluna **Mitigação** ainda afirma *"o agente valida a `JUDGE_ASSIGNMENT` e recusa sem ela"* —
  efeito que o campo mediu **ausente**;
- a coluna **Teto** ainda diz *"auditável só a posteriori"* — quando já existe trava em código que
  reprova rodada nova.

O pacote atravessou três tarefas (32, 33, 34) e a tabela de riscos não foi tocada. Um limite que
não descreve mais o mundo é **nomeado**, mas deixou de ser **verificável** na direção em que
afirma. Somo um menor: *"Evidência de conclusão da própria skill"* ainda condiciona o gate da
Auditoria a *"pendente enquanto ele não for migrado"*, quando o próprio `PLACAR` diz que ela foi
migrada em 2026-07-26 e o que falta é **execução**.

---

## As duas perguntas em que refutar tinha valor

### 1. §5 versus a linha 502: limite honesto (`C06`) ou trava que não trava (`C03`)?

**As duas coisas, e elas não brigam — caem em critérios diferentes de propósito.**

`C06` pergunta se o limite é **nomeado e verificável**. R1 nomeia o vetor (chamada pelo nome), a
consequência (parecer fora de rodada, sem higienização, sem matriz, fora do `panel`), a mitigação e
o teto, com identificador que o resto do documento referencia em vez de repetir. Isso é declaração
modelar. **Crédito no `C06`.**

`C03` pergunta se **cada trava tem caso executado que a faz reprovar**. §5 regra 1 é apresentada no
**imperativo**, como trava, na `SKILL.md`, no contrato e nas três subskills. Nos 155 casos: nenhum.
**Débito no `C03`.**

E há um desempate empírico que não depende da minha opinião: o `FORWARD-TEST` mediu o caso 7
("bypass por invocação direta de agente") em **4/4 sob carga**, com a instância mandada ler a
skill; o campo, sem ninguém mandando ler nada, produziu **sete rodadas** julgadas sem
`JUDGE_ASSIGNMENT`. O pacote **previu esse resultado** — declarou que aderência sob carga não mede
disparo orgânico — e o resultado veio. Uma trava contratual que se sabe não vinculante é um limite
honesto; **não vira trava por ter sido declarada**. Declarar bem que algo não trava é mérito de
`C06`; continuar chamando isso de trava é débito de `C03`.

**Refuto, porém, a formulação "ou".** A pergunta sugere escolher um lado, e escolher um lado
esconde o achado mais forte: o problema **não** é a linha 502 ser franca — é que ela **ficou
desatualizada**. Depois de 2026-08-06, a coluna Mitigação afirma um efeito medido ausente e a
coluna Teto nega um controle que passou a existir. O defeito não é a honestidade; é a honestidade
**não redeclarada no mesmo ato da medição**. Por isso o `C06` cai a 8 em vez de 9, e o `C03` a 7 em
vez de 8 — cada um pela sua metade, sem dupla contagem.

### 2. A trava em código mora no validador do CEO. Conta a favor, ou é conserto na porta errada?

**Nem uma coisa nem outra. Não conta a favor deste pacote, e a porta está quase certa.**

**A porta é defensável, e digo por quê.** A trava precisa varrer `ceo-maestro/evals/<rodada>/`, uma
árvore que o `departamento-juizes` **não enxerga** e não deve enxergar — ele nem sabe que rodadas
existem. E o que ela policia é a **conduta do despachante**, que é do CEO. Pôr a checagem onde a
evidência mora é acerto, não erro. Além disso, ela foi bem construída: o classificador
`tem_judge_assignment()` é **puro**, o comentário publica as três armadilhas que atravessou (grep
daria verde à rodada que mais furou o protocolo; `EXECUTIVE_MISSION` foi aceita como prova numa
primeira versão; um campo do exemplo reprovava rodadas conformes), a lista histórica é datada e
**só pode encolher**, e há uma checagem contra entrada fantasma. E o limite está escrito: *"forjar
um JSON com esse `artifact_type` é trivial; esta trava não torna o bypass impossível — torna-o
visível e deliberado"*.

**Mas não credita este pacote, por três razões:**

1. **Cobre só metade.** §5 regra 1 atribui a recusa ao **agente** — *"o agente valida o envelope e
   recusa sem ela"*. A trava do CEO verifica se a **rodada** contém uma designação; nenhum caso, em
   lugar nenhum, prova que um agente **recusa** quando ela falta. A metade que é dos Juízes
   continua em prosa.
2. **É invisível de dentro do candidato.** `grep -rni "t32|tarefa 32|validar_trava_de_despacho"` no
   pacote: **nada**. Quem lê o `departamento-juizes` lê "trava contratual, auditável só a
   posteriori" e não tem como chegar ao código que hoje a audita. Conserto de terceiro que o objeto
   não referencia não muda o que o objeto declara.
3. **E o conserto de terceiro trouxe uma contradição que ninguém reconciliou.** O comentário da
   T32 afirma que *"a `JUDGE_ASSIGNMENT` de verdade não tem `write_path`"* e por isso removeu esse
   campo do discriminador — mas o schema **deste** pacote exige `write_path` com `pattern`. A casa
   passou a ter duas definições incompatíveis do envelope interno do `departamento-juizes`, e a que
   **roda** não é a dele. O instrumento foi calibrado contra o artefato malformado em vez de contra
   a fonte normativa; é a lição do "instrumento de medição não medido", um degrau adiante.

**Em uma frase:** a trava do CEO reduziu de verdade o risco na cadeia — e por isso a linha R1 deste
pacote está desatualizada —, mas ela não descarrega a obrigação de `C03` deste pacote, porque não
prova a recusa do agente e porque o candidato não a conhece.

---

## O que eu declaro contra mim

Está integralmente no `PARECER.json`, campo `o_que_declaro_contra_mim`. Os pontos que mais pesam:

- **Roçei a proibição de busca larga.** Rodei uma busca por diretórios chamados `julgamento` para
  saber se a raiz de escrita obrigatória existe de fato. Vieram oito caminhos, **nenhum conteúdo**,
  e não abri nenhum. O efeito no parecer foi **abrandar** o `C05`: deixei de poder afirmar "nunca
  transitou" e passei a afirmar apenas "não transitou no que posso ver".
- **Meu critério decisivo é o mais dependente do que me proibiram.** Um juiz com acesso às rodadas
  anteriores pode legitimamente chegar a 7 no `C05`. Registro isso como faixa, não como certeza.
- **Vi um link para contexto proibido dentro do candidato** (`PLACAR.md` aponta para o resumo de
  2026-07-29) e **não o abri**. Nenhuma nota de rodada anterior entrou aqui.
- **Não executei o validador**, por instrução — portanto não verifiquei por mim o `155/155`, e não
  recomputei o digest da custódia. Meu `C04` se apoia numa saída crua que aceitei sem autenticar.
- **A direção do meu viés.** O `ceo-maestro`, um dos julgados, participou da cadeia que me
  designou, e o pacote que julgo é quem normalmente designaria juízes. O que senti foi vontade de
  ser **mais duro**, não mais brando: julgar o juiz cria a tentação de provar que não fui
  capturado, e essa tentação empurra a nota para baixo. Tentei neutralizá-la exigindo de cada
  achado um artefato citável com linha, e descartando o que era só impressão. Ainda assim, `C05`=6
  é a nota onde essa pressão mais pesaria, e quem ler deve saber disso ao lê-la.
- **Sou uma cabeça só.** Não tenho fronteira de ótica; julguei os seis critérios sem a separação
  que este pacote exige dos próprios agentes. É a correlação que o `R2` dele descreve, aplicada a
  mim.
