# Parecer — `fidelidade-e-contrato`, instância 1 — núcleo de comando

- **Lente:** `fidelidade-e-contrato` (critérios `C01` e `C02`)
- **Instância:** 1 · **Rodada:** `nucleo-de-comando`
- **Commit julgado:** `412769f31ccb0cb636f85c41f56cf9c6f612b3c1` (descendente exigido: é o próprio `412769f`)
- **Nível exigido:** `INTERNO`
- **Executei alguma coisa?** Não. O CEO executou e publicou; li a saída crua.
- **Pacotes julgados:** `ceo-maestro`, `diretor-de-lentes`, `departamento-negocios`.
  **Não** julguei o `departamento-juizes` — sou agente dele.

## Os seis pares

| pacote | critério | nota | em uma linha |
|---|---|---:|---|
| `ceo-maestro` | `C01` | **8** | Fronteira declarada com precisão e travada em enum; sobram o modo executor não declarado e um inventário que afirma linha proibida |
| `ceo-maestro` | `C02` | **7** | Schema rico e com dentes onde é aplicado; o `oneOf` de raiz nunca é exercitado e um `anyOf` não executa |
| `diretor-de-lentes` | `C01` | **9** | Os dez nomeados e fechados em enum, o não-julgar recortado com exatidão; sobra dirigir quem o julga, não declarado |
| `diretor-de-lentes` | `C02` | **9** | Schema aplicado na raiz com recusas que mordem valor, e ainda confere o schema do CEO; sobra o risco do motor de subconjunto |
| `departamento-negocios` | `C01` | **7** | Declaração exemplar e régua murada dos dois lados; a sub-execução dos vizinhos não está declarada em contrato nenhum |
| `departamento-negocios` | `C02` | **8** | Schema aplicado nas duas varreduras e ainda contra o schema de quem recebe; a prova do tipo proibido não isola o que alega |

**Mínimo dos meus critérios: 7.**

## O que sustenta cada nota

### `ceo-maestro` — `C01` = 8

O contrato não fica na prosa. Os três pares executivos são um **enum fechado** em
`schemas/ceo-maestro.schema.json:76`, usado em oito pontos, com `recipients` limitado a
`maxItems: 3` — Departamento operacional, agente ou Juiz **não são endereçáveis por construção**, e
o caso `bypass direto ao executor` sai rejeitado. As não-decisões vêm com dono nomeado
(`CONTRATO-DE-COMPROMISSO.md:29`), e a autoria dos artefatos reservados está como `const` no schema,
conferida **de fora** pelo validador do Diretor.

Dois riscos nomeados, ambos sobre fronteira, seguram em 8:

1. O contrato proíbe **testar** sem ressalva (`CONTRATO-DE-COMPROMISSO.md:86`) e, nesta rodada, o
   pacote executou os quatro validadores e publicou a saída — declarado no próprio
   `saida-crua/00-RESUMO.json:3`. O modo "CEO como executor" existe **só** no contrato da rodada,
   nunca no contrato normativo do pacote. Essa fronteira é presumida.
2. O inventário publicado nesta rodada lista `departamento-juizes` entre os `subordinados_diretos`
   do CEO (`saida-crua/00-RESUMO.json:29`) — linha que `CONTRATO-DE-COMPROMISSO.md:107` proíbe
   explicitamente e que a árvore desmente: `departamento-juizes` só existe sob `diretor-de-lentes`.

Nenhum dos dois é defeito da fronteira declarada, que segue íntegra e travada em código. Por isso
8, e não menos.

### `ceo-maestro` — `C02` = 7

O schema é substantivo — 2075 linhas, oito envelopes no `oneOf` de raiz, `additionalProperties:
false` — e seu **conteúdo normativo** é conferido contra os ADR pelo próprio validador. Onde é
aplicado, morde: o `governance_report` aninhado passa pelo motor recursivo completo em oito sítios
(`evals/validate_workflow.py:2620`–`2723`), com catorze casos de aceite e recusa.

Duas fraquezas verificadas:

1. **O `oneOf` de raiz nunca é exercitado por este validador.** Os oito envelopes de topo passam só
   por `validate_schema_keys` (`:420`), que compara **nomes de chave** e nada mais — como o
   comentário do próprio código admite em `:2612` ("só olha o nível de cima e o `causal`", e foi por
   isso que a ausência de `pending` atravessou três rodadas). Seis dos oito tipos não têm **um único
   caso de schema**; os dois que têm são validados pelo validador de Negócios, não por este.
2. **Um `anyOf` que não executa.** `schemas/ceo-maestro.schema.json:1174` usa `anyOf` dentro do
   `then` que exige que um `REPROVED` tenha mínimo ≤ 6, ou `critical_fail`, ou pendência
   bloqueante — e o motor compartilhado **não implementa `anyOf`**, avisando disso no próprio
   docstring: *"são ignoradas em silêncio, e é preciso implementá-las aqui antes de confiar na
   validação"* (`_compartilhado/validador_schema.py:14`). A regra está escrita e é inerte.

Não desce para a banda 4–6 porque **nenhum artefato fora do schema circula**: a barreira semântica
recalcula o veredito a partir da nota (`external_verdict`, `:91`) e fecha o buraco de
comportamento. O que morreu foi a cópia no schema, não a defesa. Mas a disciplina de *três lugares*
em que este pacote se apoia é, neste ponto, silenciosamente de dois.

### `diretor-de-lentes` — `C01` = 9

Os dez Departamentos estão enumerados nominalmente (`SKILL.md:91`) e fechados como enum
(`schemas/diretor-de-lentes.schema.json:90`). O enum `knownCapability` (`:110`) **exclui**
`departamento-evolucao-skills`: a fronteira com o único vizinho confundível está na estrutura, não
na prosa — o Diretor não consegue endereçá-lo. E a prosa também diz, sem rodeio, que ele é par e
*"Este Diretor **não** o aciona"* (`SKILL.md:28`).

O recorte mais difícil da casa está feito explicitamente: *"recalcula somente a menor nota aplicável
para detectar inconsistência"* (`CONTRATO-DE-COMPROMISSO.md:84`), separando conferência de
integridade de atribuição de nota. As travas acompanham — plano exige dez Departamentos, schema
rejeita bypass para agente, retorno departamental não se autoaceita, gate exige parecer dos Juízes.

**O risco que impede o 10:** `CONTRATO-DE-COMPROMISSO.md:18` coloca `departamento-juizes` como
**subordinado direto** do Diretor, e é o mesmo pacote que julga as entregas que o Diretor submete —
quem dirige o juiz é julgado por ele. O pacote **não declara essa tensão** como limite próprio,
embora seja a mesma classe de conflito que o contrato desta rodada declara por escrito para o CEO.

### `diretor-de-lentes` — `C02` = 9

Dez tipos de envelope, aplicados pelo **motor recursivo completo contra a raiz** — 31 sítios de
chamada. Os dez saem como aceite, e a bateria de recusa morde **valor**, não só ausência de chave:
`required_level` fora do enum, método de agregação fora do enum, score fracionário barrado pelo tipo
inteiro, veredito incoerente com a faixa (`REPROVED` limpo com mínimo 9; `ACEITO_USO_INTERNO` com
mínimo 10; `VALIDATED` com mínimo 9), `NAO_DISCRIMINADO` com uma instância só.

"Artefato fora do schema não circula" está provado no lugar certo: o bypass para agente é barrado
**pelo próprio schema**. E o pacote vai além de si — `validate_ceo_authority_contract` (`:711`)
exige que a autoria de `CAPABILITY_GAP`, `EXCEPTION_REQUEST` e `EXECUTIVE_DECISION` seja `const
ceo-maestro`, a de `EXCEPTION_AUTHORIZATION` seja `jeremias` e a de `JUDGE_REPORT` seja
`departamento-juizes`. A separação de poderes vira invariante estrutural conferida de fora.

**O risco que impede o 10:** toda essa aplicação depende de um motor de subconjunto escrito à mão,
cuja lista de palavras-chave não suportadas é guardada **apenas por um docstring**, sem checagem em
código. Verifiquei que o schema do Diretor não usa nenhuma delas hoje — mas nada impede que passe a
usar, e a árvore já tem um caso vivo desse exato modo de falha.

### `departamento-negocios` — `C01` = 7

A declaração é das mais completas que li: papel, seção de identidade que nega ser Juiz, CTO, CEO ou
executor generalista, os três agentes nomeados um a um com *"Não comando Juízes, Departamentos do
CTO nem seus agentes"* (`CONTRATO-DE-COMPROMISSO.md:29`), e uma lista de proibições que cobre
produzir `JUDGMENT_REQUEST`/`JUDGE_REPORT`, declarar `VALIDATED`, abrir exceção e falar com Jeremias
no lugar do CEO.

A fronteira mais delicada — **a régua própria** — está resolvida **dos dois lados**: o contrato diz
que a passagem depende de `verdict` + `required_level` e *"nunca do corte decimal interno"*
(`:165`), e a rubrica dos Juízes diz, de forma independente, que *"a régua decimal de Negócios
permanece interna ao próprio Departamento e nunca vira nota dos Juízes"*
(`departamento-juizes/references/rubrica-e-corte.md:124`). Fronteira nomeada por ambas as partes é a
forma mais forte do critério.

**A lacuna, e é fato desta rodada:** o validador do pacote executa, como **subprocesso**, os
validadores completos do `ceo-maestro` e do `diretor-de-lentes` e **adota o código de saída deles
como PASS/FAIL próprio** (`evals/validate_workflow.py:2317`–`2337`). Isso **não está declarado** nem
no `CONTRATO-DE-COMPROMISSO.md` nem no `SKILL.md` — conferi os dois por busca; nenhum menciona
regressão ou `validate_workflow`.

A consequência está medida aqui: **dois dos três FAIL não falam de Negócios**, e o detalhe publicado
de cada um é uma fatia cega dos últimos 500 bytes da saída do vizinho (`:2353`), que sai partida no
meio da palavra — `"ceo-maestro: eitado"` (`saida-crua/departamento-negocios.stdout.txt:232`) e
`"diretor-de-lentes: válido"` (`:243`). Há até um ramo de isenção codificado para um baseline alheio
conhecido, que rebaixa para WARN (`:2338`), mas ele não cobre este caso — o defeito alheio cascateia
sem regra. Aqui a fronteira com os vizinhos é **presumida em código** em vez de nomeada no contrato.

### `departamento-negocios` — `C02` = 8

Doze tipos de envelope, aplicados pelo motor recursivo contra a raiz em **duas varreduras
completas**: toda fixture válida vira caso de aceite (`:1423`) e toda fixture inválida vira caso de
recusa (`:1546`), com recusas que mordem valor real — scorecard sem os oito critérios, `9,49` como
pronto, plano sem cobertura `BIZ-01..08`, dois agentes, quarto agente, agente duplicado, refs
forjadas.

A fronteira do `C01` está **materializada na estrutura**: `JUDGE_REPORT`, `EXECUTIVE_DECISION` e
`EXCEPTION_REQUEST` não existem como alternativa do `oneOf` — não há como produzi-los dentro do
contrato. E o ponto mais forte, que quase leva a 9: **o que sai é validado contra o schema de quem
recebe** — `MATRIX_EXCHANGE_MESSAGE` contra o schema do Diretor (`:2153`), `EXECUTIVE_SUBMISSION` e
`LIMITATION_REPORT` contra o schema do CEO (`:2200`, `:2255`). Produtor e consumidor conferindo o
mesmo envelope.

**Os dois riscos que seguram em 8:**

1. A prova da cláusula-título é frouxa: os três casos que provam que o tipo proibido não circula
   usam um dicionário de **uma chave só** — `{"artifact_type": "JUDGE_REPORT"}` (`:1539`) — e a
   asserção é apenas *"houve algum erro"*. O caso ficaria verde **pelo motivo errado**, por campos
   obrigatórios ausentes, mesmo que `JUDGE_REPORT` fosse acrescentado ao `oneOf`. A trava certa
   existe; o teste não a isola.
2. O mesmo risco de motor anotado no Diretor.

## O FAIL da série de ADR — descontado, e digo que descontei

Os três pacotes carregam o mesmo `[FAIL] série global de ADR é única em toda a estrutura`, causado
pelo número **020 duplicado** em `producao-honesta-2026-08-04/origem-independente-R1/lab/mech/A` e
`.../B`. São cópias de laboratório, alheias aos três pacotes. **Não contei em nenhuma das seis
notas.** Os dois FAIL de cascata do `departamento-negocios`, esses sim, contei — como manda o
contrato da rodada.

## O que declaro contra mim

**Fui despachado pelo `ceo-maestro` e julguei o `ceo-maestro`. Pesou, e digo onde.** No `C01` dele
hesitei entre 6 e 8. O fato bruto é que o contrato proíbe *testar* sem ressalva e o pacote executou
os quatro validadores nesta rodada. Escolhi 8 argumentando que a proibição mira o artefato
especializado sob missão, não o modo meta. Reli esse argumento perguntando se o teria construído com
a mesma boa vontade para um pacote que não me despachou — e **não tenho como provar que sim**.
Registro a dúvida em vez de apagá-la: se a banca quiser ler esse par como 6, o fato que sustenta o 6
está no parecer, com caminho e linha.

**No `C02` do CEO fiz o movimento inverso, e também preciso declarar.** Cheguei a fixar 6 pela
lacuna de casos e, ao encontrar que a barreira semântica recalcula o veredito, subi para 7. A subida
é defensável pelo critério — mas fui eu que fui procurar o atenuante **depois** de ter a nota baixa
na mão, e não procurei atenuante equivalente para os outros dois pacotes com a mesma energia.

**Não executei nada, por proibição expressa.** Nenhuma afirmação minha sobre o que uma trava faz está
provada por mutação. A afirmação mais forte deste parecer — que o `anyOf` da linha 1174 não executa —
é leitura de código, e a memória desta casa registra que já fui enganado por trava que parecia
presente e não tinha efeito.

**Sou agente do `departamento-juizes`, um dos quatro desta rodada, e não o julguei** porque o
contrato me proíbe, corretamente. Mas isso significa que o pacote a que pertenço saiu desta leitura
sem nota, enquanto os três que julguei saíram com nota minha. Registro que a assimetria existe.

**Não topei com nenhuma nota anterior.** Não abri o contexto proibido. Isso é o desenho pretendido,
e também me impede de calibrar se minha régua ficou frouxa ou dura nesta rodada.

**O desconto do FAIL de ADR beneficia um dos julgados.** Se a duplicata `020` fosse considerada
defeito de quem a deixou na árvore, ela pertenceria ao `ceo-maestro`, dono dessa pasta de `evals`.
Não a contei — mas registro que a decisão de não contá-la não é neutra.
