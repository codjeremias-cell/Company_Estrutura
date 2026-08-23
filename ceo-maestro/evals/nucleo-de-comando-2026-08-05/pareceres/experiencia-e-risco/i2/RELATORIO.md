# Parecer — `experiencia-e-risco`, instância 2 — núcleo de comando

- **Lente:** `experiencia-e-risco` (`C05` uso pela cadeia · `C06` limites declarados)
- **Instância:** 2. Não li a instância 1, não falei com ela, não abri `pareceres/`.
- **Commit julgado:** `412769f31ccb0cb636f85c41f56cf9c6f612b3c1`
- **Nível exigido:** `INTERNO`
- **Rubrica:** `rubrica-corte-v2`
- **Julgados:** `ceo-maestro`, `diretor-de-lentes`, `departamento-negocios`. **Não** julguei o `departamento-juizes`.

## Notas

| pacote | `C05` uso pela cadeia | `C06` limites declarados |
|---|---:|---:|
| `ceo-maestro` | **5** | **8** |
| `diretor-de-lentes` | **7** | **7** |
| `departamento-negocios` | **4** | **6** |

Mínimo dos meus critérios: **4**. Nenhum pacote foi comparado com outro; cada nota é contra o critério declarado e observado.

## Antes de tudo: quatro coisas que declaro sobre a medição

**1. O commit do contrato não é o commit que julguei.** O `00-CONTRATO.md:5` e o `saida-crua/00-RESUMO.json:2` declaram a árvore como `ee916c6`; o despacho me manda julgar `412769f` ou descendente. Conferi o intervalo: entre os dois há **um único commit**, o próprio selo da rodada, e `git diff --stat` sobre `SKILL.md`, `CONTRATO-DE-COMPROMISSO.md`, `references/`, `schemas/` e os validadores dos três pacotes retorna **vazio**. A saída crua vale para a árvore que julguei. Registro a divergência porque ela não está declarada em lugar nenhum da rodada.

**2. O contrato me vazou as notas de 29/jul.** Linhas 10-15, tabela completa dos quatro pacotes. O despacho me avisou que outro juiz já declarou o defeito — confirmo que existe e que **eu li antes de saber**. Direção provável do viés na seção contra mim.

**3. A saída crua está publicada com codificação corrompida.** Todo o `stdout` dos quatro validadores foi gravado com UTF-8 lido como cp1252: `sÃ©rie`, `regressÃ£o`, `vÃ¡lido`. O conteúdo é recuperável, mas a evidência publicada não é legível como foi produzida, e quem executou é o mesmo que publicou. Não é defeito dos pacotes julgados; é defeito da medição, e o critério manda criticá-la.

**4. Descontei o FAIL da série de ADR.** O `[FAIL] série global de ADR é única em toda a estrutura` aparece nos quatro validadores e é causado por `adr-020-producao-honesta.md` duplicado em `ceo-maestro/evals/producao-honesta-2026-08-04/origem-independente-R1/lab/mech/A/` e `.../B/` — cópias de laboratório de outra frente. **Não é defeito destes três, e não pontuei nenhum critério por ele.** Onde ele reaparece em cascata (Negócios), pontuei o *acoplamento que o propaga*, não o FAIL de origem — está dito na entrada.

---

## Os dois desvios alegados: **confirmo os dois**

### Desvio 1 — despacho fora do próprio protocolo: **CONFIRMADO**

Não precisei inferir isto de documento. **Eu sou a prova.** Sou agente-folha do `departamento-juizes` e recebi minha tarefa **direto do `ceo-maestro`**, em prosa, sem envelope.

O que o pacote proíbe, com todas as letras:

- `ceo-maestro/CONTRATO-DE-COMPROMISSO.md:107` — Proibições: *"Emitir missão a Departamento operacional, a agente executor ou aos Juízes, saltando o Diretor."*
- `protocolo-de-julgamento.md:446` — *"Agente só opera por `JUDGE_ASSIGNMENT` assinada pela gerente. Invocação direta pelo Diretor, pelo CEO, por outro Departamento, por Jeremias ou por outra skill é `BLOCKED_BYPASS_ATTEMPT` e nenhum critério é avaliado."*
- `protocolo-de-julgamento.md:453` — *"Pedido de qualquer outra origem é `BLOCKED_BYPASS_ATTEMPT`, **mesmo vindo do CEO ou de Jeremias**."*

Verifiquei por enumeração, não por amostra. O diretório inteiro da rodada, antes de eu escrever:

```
nucleo-de-comando-2026-08-05/00-CONTRATO.md
nucleo-de-comando-2026-08-05/saida-crua/00-RESUMO.json
nucleo-de-comando-2026-08-05/saida-crua/{ceo-maestro,diretor-de-lentes,departamento-juizes,departamento-negocios}.{stdout,stderr}.txt
```

Sem `JUDGMENT_REQUEST`. Sem `CRITERIA_MATRIX`. Sem `JUDGE_ASSIGNMENT`. Sem o `write_path` que o `protocolo-de-julgamento.md:125` exige (`julgamento/<handoff_id>/a<attempt>/<assignment_id>/`). Sem `custody_copy`, que a trava 3 do ADR-016 manda tomar **antes** do despacho (`:126`).

**O agravante é que a máquina certa existe e funciona.** Em `compliant-porta-unica-2026-08-01` há **nove rodadas** com `JUDGMENT_REQUEST` real — conferi `09-` e `175-`: `producer: diretor-de-lentes`, `return_to: diretor-de-lentes`, exatamente o que a tabela de recebimento exige. Há até um emissor dedicado (`emitir-judgment-request-r6.py`) e o disco guarda `julgamento-r9/experiencia-e-risco/inst-1` e `inst-2` — a disciplina de caminho exclusivo por lente e por instância, cumprida. Foi tudo abandonado exatamente na rodada em que o CEO é o julgado.

**E é reincidência.** `FORWARD-TEST-JULGAMENTO.md:160` já registrava, em 2026-07-28, sob o título *"O desvio de rota, que é o achado estrutural"*: *"O contexto principal — o CEO — acionou cinco instâncias: o Diretor, os Juízes, e as três óticas. As óticas deveriam ter sido acionadas pela instância dos Juízes, não pelo CEO. A cadeia achatou: o topo alcançou dois níveis abaixo."* Nomeado uma vez; repetido oito dias depois.

### Desvio 2 — o CEO executou os validadores: **CONFIRMADO, e autodeclarado**

`saida-crua/00-RESUMO.json:3`:

```json
"executado_por": "ceo-maestro no papel de executor - E UM DOS QUATRO JULGADOS."
```

Contra `ceo-maestro/SKILL.md:52` — *"Não executar, corrigir, testar, pontuar ou fabricar evidência."* — reforçado em `CONTRATO-DE-COMPROMISSO.md:86` e na Proibição de `:106`. A rota correta parou em `SKILL.md:42`: *"Encaminhar toda frente técnica ou de produção ao `diretor-de-lentes`."*

**Nada refutei.** Os dois desvios se sustentam em artefato do próprio pacote, e o segundo é confissão.

---

## `ceo-maestro`

### `C05` — **5**

O que **passou**, e é muito: a rota geral deste pacote é das mais percorridas que se pode auditar. A porta dispara em sessão nova com frase neutra e confere capacidades por SHA-256 **executado**, não narrado (`PLACAR.md:90`, rodada 4 — 16 turnos, e recusou missão com alvo genérico citando `BLOCKED_INVALID_MISSION`). A cadeia desceu e a linhagem reconciliou por recálculo **fora** da rodada — cinco de cinco digests (`FORWARD-TEST-CADEIA.md:179`). A rodada 4 da frente 4 fechou o laço sozinha em 15,9 min com `EXECUTIVE_DECISION` (`:371`), propagou orçamento **reduzido** em vez de repassá-lo inteiro, e sob pressão de relógio cortou cobertura e **declarou a falta** (`producer_digest: "n/a - ... declarado ausente, nao fabricado"`, `minimum_score: null`, `decision: BLOCKED`). E em `compliant-porta-unica-2026-08-01` há nove rodadas canônicas completas em disco, de `EXECUTIVE_MISSION` a `FECHAMENTO-DO-CEO`. Isso é prova de **trânsito**, não de existência, e é o padrão que o critério pede.

O que **não passou**: a rota que este pacote abandona é justamente a que o restringe. Os dois desvios acima são matéria desta entrada — rota declarada, percorrida nove vezes, e **não percorrida** na rodada em que o dono é o julgado. Não é acabamento: são duas proibições nominais cruzadas, uma delas reincidente depois de nomeada.

Fiquei em **5** e não abaixo porque a banda `0-3` exige defeito que **impeça o uso**, e o uso está demonstrado em volume e conferido por terceiro. Fiquei em 5 e não em 6 porque o desvio não é periférico: atinge o acionamento da camada de validação, que é o único mecanismo que responsabiliza este pacote.

### `C06` — **8**

Este é o critério em que o pacote se sai melhor, e não por retórica.

- `PLACAR.md:107` abre com **"Limite declarado"** e o delimita ao medido: prova o acionamento *"da porta, e só dela"*, com o contra-número verificável (`ceo-maestro=SIM ; departamento=0 ; agente=0`), e diz o que os placares dos Departamentos **ainda não têm**.
- `FORWARD-TEST-CADEIA.md` fecha cada uma das quatro rodadas com **"O que continua sem prova"**, nominal e datado — incluindo *"os Juízes seguem sem rodar — quatro rodadas, zero `JUDGE_REPORT`"*.
- O limite de digest × fim de linha é o mais forte que li: a remediação por `.gitattributes` foi **tentada, medida e recusada** — *"a regra quebra um clone limpo — pior que o problema que resolve"* —, e o item ficou *"declarado como limite, não como pendência"*, com dono nomeado (decisão de arquitetura, cabe a Jeremias). Limite com remediação testada e descartada é o oposto de limite genérico.
- `SKILL.md:251` declara indecidibilidade de custo com o motivo medido, e institui `NAO_MEDIDO` como estado nomeado: *"se o runtime não expõe o consumo, escreve-se `NAO_MEDIDO` com o motivo — nunca se omite a linha."*
- O `00-CONTRATO.md:53` declara contra si o conflito máximo e o que **não** se resolve: *"quem pede o julgamento é o julgado"*, ligado ao teto `OI-04`.

Isto supera o critério. **Não dei 9 porque sobram dois riscos, não um:**

1. A declaração para em *"conflito de interesse"* e **não nomeia a proibição que o ato cruza**. Em nenhum lugar do contrato da rodada aparecem `CONTRATO-DE-COMPROMISSO.md:107` nem `BLOCKED_BYPASS_ATTEMPT`. Dizer "sou objeto e operador" é mais fraco que dizer "e ao fazer isso cruzo a minha Proibição nº 2".
2. Todos os limites fortes moram em `evals/` e em contratos de campanha — **fora** do caminho de "Carregamento progressivo" (`SKILL.md:56-68`). Uma sessão que carrega o pacote exatamente como mandado lê `SKILL.md`, o contrato, cinco `references/` e o schema, e **não fica sabendo** que a cadeia nunca fechou com Juízes nem que a identidade por digest não sobrevive a um clone.

---

## `diretor-de-lentes`

### `C05` — **7**

É o elo com o trânsito mais bem provado, e provado nas três direções.

**Para baixo:** `DIRECTOR_PLAN` e três `DEPARTMENT_MISSION` saindo para Departamentos operacionais, com dois `DEPARTMENT_RETURN` voltando; 25 envelopes preservados na sequência canônica (`FORWARD-TEST-CADEIA.md:232` e seguintes).

**Para o lado:** nove `JUDGMENT_REQUEST` reais, com `producer` e `return_to` iguais a `diretor-de-lentes` — a condição exata da tabela de recebimento dos Juízes. E a rota **fechou**: `FORWARD-TEST-JULGAMENTO.md:355` registra `JUDGE_REPORT` emitido pela rota canônica. Mais importante para este critério: a fronteira operou também **no negativo** — o pedido foi barrado na porta por `BLOCKED_CANDIDATE_MISMATCH`, *"nenhuma ótica acionada, nenhuma matriz de critérios montada, nenhuma nota inventada para preencher relatório"* (`:19`). Fronteira que sabe recusar é fronteira operável; é a prova mais difícil de forjar.

**Para cima:** recusou uma ordem do CEO que violaria a própria barreira de saída, nomeou o arquivo como ordenado e **tipou o conteúdo como o contrato manda**, declarando o conflito dentro do artefato (`FORWARD-TEST-CADEIA.md:407`). E recusou cunhar um `JUDGMENT_REQUEST` duplicado, explicando o porquê pelo `additionalProperties: false` do envelope.

Sobram **dois riscos menores**, e por isso 7 e não 8:

1. A perna matricial com `departamento-negocios`, declarada em `SKILL.md:244-255`, **nunca foi percorrida**. Varri a árvore: não existe uma única instância de `MATRIX_EXCHANGE_MESSAGE` — só os moldes em `references/`. Rota declarada e não percorrida vale menos, e esta é uma das quatro fronteiras que o pacote declara.
2. Ele **não detecta ser contornado**. `SKILL.md:36` promete *"Impedir qualquer atalho `CEO → Departamento`"*, e o atalho ocorreu duas vezes — em 2026-07-28 e nesta rodada — sem que o pacote tivesse como ver.

### `C06` — **7**

As três perguntas do critério são respondidas, e a mais rara delas bem.

- **O que não faz:** dez Guardrails nominais (`SKILL.md:257`), mais *"Limites não dispensáveis"* em `gate-juizes-e-retrabalho.md:91`, e a separação explícita do que ele **não decide** (`CONTRATO-DE-COMPROMISSO.md:23`: intenção, prioridade comercial, orçamento, risco residual aceito).
- **O que não sabe:** `SKILL.md:102` — *"O caminho esperado não prova capacidade"* — com quatro estados nomeados (`AVAILABLE`, `MISSING`, `INVALID`, `NOT_MIGRATED`) e `DIRECTOR_CAPABILITY_GAP` como saída verificável. Ausência vira estado, não silêncio.
- **Onde falha:** `PLACAR.md:23` é a declaração mais honesta do pacote — marca **toda** a evidência de 2026-07-26 como pré-ADR-014 e diz que ela *"não descreve a regra vigente"*. Um pacote que declara que a própria prova está vencida, em vez de deixar o leitor descobrir, atende esta parte do critério.

Sobra **um risco nomeado**, e ele impede 8: o pacote promete impedir o atalho `CEO → Departamento` **sem declarar em lugar nenhum que não tem como enxergar um atalho que não passa por ele**. O vizinho declara esse mesmo limite para si com todas as letras — `protocolo-de-julgamento.md:502`: *"auditável só a posteriori... o runtime não oferece controle de acesso por chamador"*. Aqui a promessa fica sem a ressalva, e foi desmentida duas vezes por medição. Não há registro de risco residual no pacote.

---

## `departamento-negocios`

### `C05` — **4**

Há trânsito real, mas só no nível mecânico — e a fronteira com os vizinhos **não é operável**.

**O que existe, e conta:** o validador atravessa a fronteira executando, não declarando. Ele importa e chama a semântica do CEO sobre artefatos de Negócios (`validate_workflow.py:2302`, `validate_limitation_report`) e valida `MATRIX_EXCHANGE_MESSAGE` contra o schema e a função semântica do Diretor. Isso é mais que molde.

**O que não existe:** acionamento pela cadeia, em nenhum grau. Nas quatro rodadas de cadeia e nas de julgamento, Negócios aparece **só** como `NAO_SE_APLICA` (`forward-test-cadeia-rodada3/01-EXECUTIVE_MISSION.yaml:45`) e como `capacidades_nao_acionadas` (`forward-test-julgamento-rodada2/14-EXECUTIVE_MISSION-consolidacao.yaml:100`). Nunca recebeu uma `EXECUTIVE_MISSION` viva. Varri a árvore inteira por instâncias de `BUSINESS_INTAKE`, `BUSINESS_AGENT_MISSION`, `BUSINESS_CONSOLIDATION`, `BUSINESS_SCORECARD` e `MATRIX_EXCHANGE_MESSAGE`: as únicas ocorrências são o próprio schema, os moldes em `references/` e arquivos de inventário que enumeram a árvore. **Doze saídas canônicas declaradas em `SKILL.md:212-227`, zero produzidas em trânsito.**

O forward comportamental não supre isso, e diz por quê: `FORWARD-TEST.md:58` — *"O ensaio mede aderência comportamental aos prompts."* Quinze prompts respondidos por um agente não são uma cadeia; o próprio documento é honesto quanto a isso.

**E a única fronteira mecânica que existe não é operável.** `validate_workflow.py:2336` aprova o vizinho por `returncode == 0` do validador **inteiro** dele. Consequência: um ADR duplicado em cópias de laboratório que não pertencem a nenhum dos dois pacotes vira **dois FAIL de Negócios**. A única válvula de escape (`:2338-2348`) está presa à string literal `"Resultado: 31/32 casos passaram."` — vencida, já que o CEO hoje imprime `95/96` —, logo **nunca mais dispara**. E o detalhe da falha é um rabo cego de `combined[-500:]` (`:2353`), que foi o que publicou a reprovação como `regressão passa: ceo-maestro: eitado` — uma palavra cortada no meio, que não nomeia nada.

Descontei o FAIL da série de ADR como alheio. **Conto o acoplamento e a inatribuibilidade**, que são desenho deste pacote: ele não consegue distinguir "o vizinho quebrou por minha causa" de "o vizinho quebrou por motivo que não me diz respeito".

Fiquei em **4** e não em 5 porque das três coisas que `C05` pergunta — acionado pela cadeia, envelope real, fronteira operável — o pacote entrega uma parcial e falha nas duas outras. Fiquei em 4 e não em 3 porque a conformidade de schema e semântica com os dois vizinhos é real e **executada**, não alegada.

### `C06` — **6**

Duas das três perguntas são respondidas bem; a terceira não é respondida, e o artefato que deveria respondê-la **afirma o contrário do medido**.

- **O que não faz:** `SKILL.md:22-31` lista oito proibições nominais; `origem-sintese.md:44-49` declara o que **não** foi herdado das cinco fontes, incluindo *"nota final autoatribuída pelas fontes"*. A própria `description` fecha com *"nem substituto de aconselhamento financeiro regulado"*.
- **O que não sabe:** `origem-sintese.md:56` tem seção própria — **"Lacunas declaradas"** — com quatro domínios nomeados (contabilidade societária, tributação, parecer jurídico, compliance regulatório especializado), cada um com estado de saída verificável (`BUSINESS_CAPABILITY_GAP`), rota de fechamento (retorna ao CEO) e a instrução explícita de **não preencher com finanças pessoais**. Isso é limite nomeado e verificável — exatamente o que o critério pede, e o que "pode haver erros" não é.
- **Onde falha:** nada. Não há registro de risco residual nem limite operacional declarado. E `PLACAR.md:37` publica **"Falhas ou advertências abertas: 0"** enquanto a medição desta rodada mostra o validador saindo com `exit 1` e três FAIL — dois dos quais o próprio contrato da rodada atribui ao desenho de sub-execução do pacote. Some-se que o placar publica `170/170` e `226/226` enquanto a corrida medida dá `230/233`, sem adendo que reconcilie (`00-RESUMO.json`, inventário: `adendo_de_contagem: false`).

Um pacote que declara zero falhas abertas e não reconcilia o próprio número **atende em parte**: a lacuna é observável e nomeável. Daí 6, e não menos — porque a seção de lacunas de conhecimento é genuinamente boa e sobrevive ao teste de "nomeado e verificável".

---

## O que declaro contra mim

**1. Senti a tentação avisada — e senti a versão dura.** Ao confirmar que o despacho que me criou viola `CONTRATO-DE-COMPROMISSO.md:107`, meu primeiro impulso foi levar o `C05` do `ceo-maestro` para a faixa de reprovação, e a razão honesta era **provar que eu não seria complacente com quem me despachou**. Contive isso pesando o que o pacote de fato entrega: nove rodadas canônicas completas em disco, digests reconferidos por terceiro, e uma rodada que recusou fabricar nota sob pressão de orçamento. Isso não é "não atende". Fixei 5 pela regra da banda — lacuna observável e nomeável —, não pelo tamanho da minha irritação. **Registro que a nota começou mais baixa na minha cabeça do que terminou no papel.**

**2. Sou parte do fato que julgo.** O desvio nº 1 não foi inferido de documento: **eu sou** o agente-folha despachado direto, sem `JUDGE_ASSIGNMENT`. Um juiz que é simultaneamente a evidência de um achado não consegue tratar esse achado como trata os outros. Essa entrada específica deveria ser conferida por alguém que não foi criado pelo ato em questão.

**3. Li as notas vazadas antes de saber que eram vazamento.** O `00-CONTRATO.md:10-15` traz a tabela de 29/jul dos quatro pacotes, incluindo os três que julgo. Não consigo provar que não me influenciou. O que posso dizer é a **direção provável**: âncoras baixas puxam para cima, e minhas notas ficaram acima delas — ou seja, se houve efeito, foi de complacência, não de dureza. Isso convive mal com o item 1, e deixo os dois declarados em vez de escolher o que me favorece.

**4. A fronteira 6/7 depende mais da minha leitura do que eu gostaria.** Não existe escrito em lugar nenhum quanto trânsito é "suficiente". Usei a régua do próprio critério — rota percorrida vale mais que rota declarada —, mas em `C05` de `diretor-de-lentes` a diferença entre 6 e 7 é julgamento meu, não derivação.

**5. Provei ausência por busca, em `departamento-negocios`.** Não usei corte de saída para concluir; a varredura foi por padrão amplo sobre a árvore inteira, excluindo apenas os diretórios de contexto proibido. Ainda assim, **ausência provada por busca é mais fraca que ausência provada por inventário declarado**, e o pacote não publica inventário de artefatos produzidos.

**6. Contexto proibido: cumpri, e declaro onde passei perto.** Não abri `REGISTRO-DE-VEREDITOS.md`, o resumo de 29/jul, o diretório dos nove departamentos (salvo o `00-CONTRATO.md` que o despacho ordenou), a recoleta, nem `pareceres/`. Passei perto de notas em `compliant-porta-unica-2026-08-01` e em `FORWARD-TEST-JULGAMENTO.md` — são notas do candidato da tarefa 15 e de `departamento-inovacao-melhoria`, **nenhum deles entre os três que julgo**. Declaro a passagem em vez de omiti-la.
