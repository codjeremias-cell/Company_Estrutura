# Parecer — `robustez-e-evidencia`, instância 2 — núcleo de comando

- **Commit julgado:** `412769f31ccb0cb636f85c41f56cf9c6f612b3c1` (descendente de `ee916c6`, a árvore da saída crua).
- **Nível exigido:** `INTERNO`.
- **Escopo:** três pacotes × dois critérios. **Não** julguei `departamento-juizes`.
- **Não executei nada.** Li e critiquei a medição publicada, conforme a instrução.
- **Descontei** o FAIL da série de ADR (número 020 duplicado por cópias de laboratório de outra
  frente) nos seis pares. **Digo que descontei.** Sem esse desconto os três teriam FAIL aberto.

## Os seis pares

| pacote | critério | nota | razão em uma linha |
|---|---|---:|---|
| `ceo-maestro` | `C03` | **6** | meta-travas exemplares, mas uma trava inerte por construção (`anyOf`) sem nenhum caso que a exercite |
| `ceo-maestro` | `C04` | **5** | número publicado com raiz errada, evidência em mojibake, lista sem critério contra o próprio contrato, placar 41 casos atrás |
| `diretor-de-lentes` | `C03` | **7** | oráculo de veredito provado nos dois sentidos, schema sem palavra-chave inerte; sobra o risco de caso verde pelo erro errado |
| `diretor-de-lentes` | `C04` | **6** | disciplina de datar forte, mas a linha rotulada "Medição ativa" declara 79/79 e a receita devolve 100 |
| `departamento-negocios` | `C03` | **5** | anistia de FAIL decidida por presença de string, e inalcançável; duas travas com sujeito alheio |
| `departamento-negocios` | `C04` | **4** | número próprio errado, "0 falhas abertas" falso, contagem morta em código executável, saída sem raiz |

**Menor dos meus critérios: 4.**

---

## `ceo-maestro`

### `C03` — trava com prova — **6**

**A favor, e supera o critério.** A camada de meta-travas compartilhadas é o melhor que li nesta
árvore, e ataca de frente as duas armadilhas que o critério nomeia:

- `validate_trava_de_digest` afirma a **classe** da exceção levantada
  (`_compartilhado/verificacoes_estrutura.py:959-975`). Exceção genérica é reportada como
  `TRAVA_DIGEST_CLASSE_ERRADA`. Isso é literalmente "morte por exceção não conta como pega",
  implementado em código.
- `validate_sem_check_tautologico` carrega autoteste que exige que **cada regra dispare na sua
  própria fixture** e **não transborde** para as outras (`:1269-1300`). Esvaziar o detector deixa
  o módulo vermelho em toda chamada.
- O runner deriva `actual_valid = not errors` de listas **retornadas**
  (`ceo-maestro/evals/validate_workflow.py:3453-3468`): uma exceção aborta a corrida em vez de
  virar caso verde — coerente com `traceback: false` no inventário.
- Cada linha da saída declara a polaridade esperada ("— esperado válido/rejeitado"), o que é mais
  do que a maioria dos arreios oferece.

**Contra — uma trava que não pode disparar e que nenhum caso prova.**

`schemas/ceo-maestro.schema.json:1162-1198` expressa, dentro de `$defs.judgeReport`, a regra
"`REPROVED` exige `minimum_score ≤ 6` **ou** `critical_fail` **ou** pendência bloqueante" usando
**`anyOf`**. O motor compartilhado **não implementa `anyOf`** e o ignora **em silêncio** — está
escrito na própria docstring (`_compartilhado/validador_schema.py:14-18`) e confirmado por leitura
de `validate_schema` (`:284-390`), que não tem ramo para a palavra. O ramo `then` fica com uma
única chave que o motor não conhece, e `validate_schema` devolve lista vazia.

Confirmei que é a **única** ocorrência de palavra-chave não suportada em uso nas schemas de toda a
estrutura.

O invariante sobrevive por outro caminho: `external_verdict` o reconfere em código e
`validate_judge_report` compara o veredito declarado com o oráculo
(`ceo-maestro/evals/validate_workflow.py:650-655`). **Mas nenhum dos 96 casos o exercita.** Varri
as atribuições de `verdict` na suíte: os vereditos forjados são `ACEITO_USO_INTERNO` (`:2901`,
`:3189`) e `VALIDATED` (`:3406`). Não há um único `REPROVED` limpo com nota alta.

Isso importa porque a schema é a **fronteira**: pacotes vizinhos validam envelopes contra ela. Um
consumidor que valide um `JUDGE_REPORT` só pela schema aceita um `REPROVED` com nota 10, sem falha
crítica e sem pendência.

**Segundo achado, mais difuso.** Nenhum caso fixa **qual** erro disparou. `actual_valid = not
errors` aceita qualquer string. Um caso negativo pode continuar verde porque um erro diferente do
que ele diz provar disparou na mesma fixture. Não achei em lugar nenhum uma asserção sobre a
identidade do erro.

Trava presente no artefato normativo, inerte na execução e sem caso executado é "caso não coberto"
— lacuna observável e nomeável. Fica no topo da faixa de 4 a 6.

### `C04` — evidência e rastreabilidade — **5**

**A favor.** A cultura é real e em vários pontos supera o critério:

- Cada bloco do placar é datado e o documento recusa reescrever histórico
  (`ceo-maestro/evals/PLACAR.md:118-120`).
- A **mutação em memória** de `external_verdict` é publicada **com número**: 55/55 caiu para 49/55
  (`:146-151`). Isso é prova contra falso-verde, com método declarado.
- As quatro rodadas de acionamento em runtime trazem condição, turnos e SHA-256 por linha, e a
  rodada com prompt enviesado é **explicitamente desqualificada** como prova (`:79-90`).
- O campo `adendo_de_contagem: false` no inventário transforma **ausência em estado nomeado** —
  exatamente o que o critério pede.

**Contra — quatro defeitos na evidência efetivamente publicada nesta rodada.**

**1. Número publicado com a raiz errada.** `saida-crua/00-RESUMO.json:107` publica
`"sumario_proprio": "99/100"` para `departamento-negocios`. **Esse é o sumário do Diretor.**
O mecanismo é rastreável de ponta a ponta: o validador de Negócios executa os vizinhos por
`subprocess` e enxerta a saída deles sem delimitador
(`departamento-negocios/evals/validate_workflow.py:2321-2354`); a receita declarada pelo CEO é
"sumário = ÚLTIMO da saída" (`00-RESUMO.json:4`); e o último `Resultado:` da saída de Negócios é a
repetição final do Diretor (`departamento-negocios.stdout.txt:277`). O número próprio de Negócios
— `RESULTADO: 230/233 PASS; 3 FAIL; 0 WARN` — está no **mesmo arquivo capturado**, na linha 255.

Registro o que é justo: a lista `fails` de Negócios no resumo está **correta**, com os três FAIL. O
erro é só no campo, e o campo se chama "sumário **próprio**".

**2. A evidência publicada está corrompida.** Todo acento das quatro saídas e do próprio
`00-RESUMO.json` está em mojibake ("sÃ©rie", "Ã©", "â€"). A receita publicada declara
`PYTHONDONTWRITEBYTECODE=1` e **omite** `PYTHONIOENCODING=utf-8`, que a receita de regressão da
casa exige. Seguir a receita publicada não reproduz evidência legível, e o artefato mostra o dano.

**3. Lista publicada sem critério declarado, contra o próprio contrato.**
`00-RESUMO.json:29-34` atribui **quatro** `subordinados_diretos` ao `ceo-maestro`, incluindo
`departamento-juizes`. Mas `SKILL.md:41` diz "os tres pares executivos"; `SKILL.md:49` diz
expressamente "**não chamar Juízes**"; e `DIRECT_EXECUTIVES`, no próprio validador
(`evals/validate_workflow.py:55-59`), tem exatamente três. A receita não declara o critério da
lista, e o conteúdo contradiz a norma do pacote.

**4. Deriva de contagem.** O número próprio mais recente do placar é **55/55**
(`PLACAR.md:122-125`, "medição fresca de 2026-07-29"); a receita devolve **96** casos
(`ceo-maestro.stdout.txt:99`). Sem adendo. Atenua que a seção é datada; não atenua que nada no
placar diz qual é a contagem de hoje.

**5.** Registro, sem contar como defeito meu de leitura: o `00-CONTRATO.md` desta rodada vaza, nas
**linhas 10-15**, a tabela de notas de 2026-07-29 dos pacotes julgados. É vazamento do próprio CEO,
no primeiro arquivo que o despacho manda abrir.

O que o mantém fora da faixa de quebrado: os campos de receita, raiz e critério **existem e estão
declarados**, e o erro é integralmente recuperável a partir da saída crua publicada. Foi assim que
o achei. Isso é o que rastreabilidade serve para fazer.

---

## `diretor-de-lentes`

### `C03` — trava com prova — **7**

Cem casos executados, cada linha declarando a polaridade esperada
(`diretor-de-lentes/evals/validate_workflow.py:1789-1802`).

O que pesa a favor, e é específico:

- **O oráculo de veredito é exercitado nos dois sentidos**: "rejeita `REPROVED` limpo com mínimo
  9", "rejeita `ACEITO_USO_INTERNO` com mínimo 10", "rejeita `VALIDATED` com mínimo 9", "aceita
  `REPROVED` com mínimo 6" (`diretor-de-lentes.stdout.txt:46-49`).
- As travas de gate são provadas **contra a nota**: falha crítica e pendência bloqueante forçam
  `REPROVED` "mesmo com 10" (`:63-64`).
- As travas do `ADR-016` disparam nos dois sentidos, incluindo faixa que atravessa carimbada como
  aceite interno (`:37-45`).
- Varri as schemas de toda a estrutura por palavras-chave que o motor ignora em silêncio: a schema
  deste pacote **não usa nenhuma**. Não há aqui trava inerte por construção.
- Roda as três meta-travas com autoteste e a conferência da fonte normativa por digest (`:4-7`,
  `:101`).

**O único risco que nomeio:** o runner deriva `actual_valid = not errors` e nenhum caso fixa qual
erro disparou. Um caso negativo pode ficar verde por um erro diferente do que diz provar. Atende o
critério inteiro; sobra esse risco. Faixa 7–8, e fico em 7 porque o risco é sistêmico ao arreio,
não pontual.

### `C04` — evidência e rastreabilidade — **6**

**A favor, e em vários pontos supera:**

- O callout "**Marco histórico**" marca **todo** resultado de 2026-07-26 como evidência
  pré-`ADR-014` que "não descreve a regra vigente" (`PLACAR.md:23-26`). Isso é obsolescência
  virando estado nomeado — a forma mais difícil de acertar neste critério.
- A regra da casa sobre número de vizinho está citada e aplicada (`:35-37`), e cobre as linhas de
  vizinho da tabela de 2026-07-26.
- O delta é explicado **por conteúdo**, não só por número: "+26 casos" com a lista do que cobrem
  (`:14`, `:17-21`).
- A conferência da fonte normativa por digest tem receita **no código**
  (`_compartilhado/validador_schema.py:114-117`) e caso verde (`stdout:101`).
- A saída crua deste pacote é **limpa e autocontida**: o 99/100 que lhe foi atribuído é
  verificavelmente dele (`stdout:103`).

**Contra, e decisivo para a faixa:** há deriva de contagem exatamente na linha que se declara
corrente. A tabela é encabeçada "**Medição ativa**" e a linha "Validador determinístico do Diretor"
declara **79/79 PASS** (`PLACAR.md:10-12`). A receita hoje devolve **100** casos, e o inventário da
própria rodada registra `adendo_de_contagem: false` (`00-RESUMO.json:46`).

Número rotulado como **ativo** que a receita não devolve mais é defeito observado, não risco
residual. Por isso não alcança 7–8; a qualidade do resto o mantém no topo da faixa abaixo.

---

## `departamento-negocios`

### `C03` — trava com prova — **5**

**A favor.** A superfície negativa é grande e boa: cerca de 190 casos próprios, a maioria
"rejeita …", cobrindo refs forjadas, identidade causal desde o intake, IDs duplicados, digest
divergente e reuso de `message_id` (`departamento-negocios.stdout.txt:121-231`). Valida os próprios
envelopes contra a schema **e** a semântica reais dos vizinhos (`:220-231`). Roda as três
meta-travas com autoteste (`:43-46`).

**Contra — um golpe direto na proibição literal do critério.**

`evals/validate_workflow.py:2338-2348` rebaixa um FAIL de regressão a **WARN** quando a saída do
vizinho **contém** as strings `"adr-003-conformidade-sem-nota.md"` e
`"Resultado: 31/32 casos passaram."`. Isso é um desvio de reprovação decidido por **presença de
string** — o que o critério proíbe por nome.

E o ramo é **inalcançável hoje**: aquela receita devolve `95/96` (`ceo-maestro.stdout.txt:99`). É
uma anistia de falha que nenhum caso executado pode exercitar.

**Duas travas disparam sobre sujeito que o pacote não possui.** As checagens
`regressão passa: <vizinho>` (`:2321-2354`) convertem o exit code de outro processo em FAIL próprio,
sem conseguir distinguir "eu quebrei o vizinho" de "o vizinho está quebrado por conta própria".
Descontada a série de ADR em si — e eu a desconto —, o **desenho** continua sendo fato deste
pacote, e é o que produz os dois FAIL em `stdout:232` e `:243`.

**O arreio não declara polaridade.** `Results.check` imprime `[PASS] <nome>` e nada mais
(`:1296-1303`). A prova de que a trava disparou fica só no nome do caso.

### `C04` — evidência e rastreabilidade — **4**

**A favor, e é sincero:** a nota de reconciliação (`PLACAR.md:19-21`) nomeia a regra da casa
— "número de vizinho carrega a data da medição, ou não entra" — e admite que onze de quinze
placares declaravam para si um número menor que o real. Isso cobre honestamente as linhas de
vizinho (`:34-36`, `:112-114`).

**Contra.** A mesma nota que protege o vizinho **reafirma o próprio**, e o próprio está errado:

| o que o placar declara | onde | o que a receita devolve |
|---|---|---|
| `170/170 PASS` | `:31`, `:73` | `230/233 PASS; 3 FAIL` (`stdout:255`) |
| `226/226 PASS, 0 FAIL, 0 WARN` | `:11` | idem |
| `Falhas ou advertências abertas: 0` | `:37` | 3 FAIL |

Sem adendo (`00-RESUMO.json:117`). A linha do zero de falhas não está apenas velha: é
**afirmativamente falsa** contra a saída crua da própria rodada.

**Contagem morta embutida em código executável, não em prosa.** O ramo de anistia exige a string
literal `"Resultado: 31/32 casos passaram."` (`:2342`) — número que aquela receita não devolve mais.

**A saída não é delimitada.** `:2350-2354` enxerta `combined[-500:]` — os últimos 500 caracteres do
`stdout+stderr` de outro processo — dentro da própria lista de falhas, cortado no meio da palavra
("`eitado`", `stdout:232`). A cauda de cada vizinho, **inclusive o `Resultado:` dele**, aparece duas
vezes na transcrição (`stdout:233-241`, `244-252`, `258-266`, `269-277`).

O dano dessa escolha está medido nesta rodada: o último `Resultado:` da saída deste pacote é o do
Diretor, e foi ele que acabou publicado como sumário próprio.

Número próprio errado, zero de falhas falso, contagem morta em código e saída cuja raiz não se
recupera sem ler o fonte. Faixa 4–6, metade de baixo.

---

## O que confirmei e o que refutei

| achado recebido | veredito | fundamento |
|---|---|---|
| `anyOf` do `ceo-maestro` (`schema:1174`) é inerte | **confirmado, com correção** | Inerte, sim (`validador_schema.py:14-18`; sem ramo em `:284-390`). **Mas o invariante não fica aberto no caminho semântico** — `external_verdict` o reconfere (`validate_workflow.py:650-655`). A dica sugeria um buraco maior do que o que existe. O que **agravo**: nenhum dos 96 casos exercita a regra, então ela não tem efeito **nem** prova. |
| Negócios executa vizinhos por `subprocess` (`:2317-2334`), virando exit code alheio em FAIL próprio | **confirmado** | `:2321-2354`. Acrescento o que a dica não trazia: o ramo de anistia (`:2338-2348`) decide por **presença de string** e está preso a `"Resultado: 31/32"`, que a receita não devolve mais. |
| A saída de Negócios não é delimitada, e o `sumario_proprio` em `00-RESUMO.json:107` é o `99/100` do Diretor | **confirmado, com o mecanismo completo** | `combined[-500:]` em `:2353` + receita "último da saída" em `00-RESUMO.json:4` + a repetição do Diretor em `stdout:277`. O número próprio verdadeiro está em `stdout:255`: `230/233 PASS; 3 FAIL`. |

**Achados meus, que não vieram de dica:** o mojibake da evidência publicada e a omissão de
`PYTHONIOENCODING=utf-8` na receita; a lista de `subordinados_diretos` do CEO contradizendo
`SKILL.md:41`/`:49` e `DIRECT_EXECUTIVES`; a deriva de contagem nos três placares (55/55 → 96;
"Medição ativa" 79/79 → 100; 170/170 e "0 falhas" → 230/233 com 3 FAIL); e a ausência, na suíte do
CEO, de qualquer caso que forje um `REPROVED` limpo.

## O que declaro contra mim

1. **Senti a tentação oposta à esperada, exatamente como o despacho previu.** Ao fechar 6 e 5 para
   o `ceo-maestro` me peguei perguntando se estava sendo duro para provar independência de quem me
   despachou. Testei com a pergunta inversa — *daria esses números a um pacote que não me tivesse
   despachado?* — e só mantive os achados que sobreviveram com citação de arquivo e linha
   independente de quem enviou o despacho. A pressão foi real, e foi na direção da **severidade**.
2. **Fui contaminado pelas notas de 2026-07-29 antes de poder evitar.** O `00-CONTRATO.md` as traz
   nas linhas 10-15 e eu as li no primeiro arquivo que o despacho mandou abrir. Sei que os três
   pacotes que julgo carregavam 1, 1 e 5. É vazamento do próprio contrato, já declarado por outro
   juiz, mas me alcançou. O risco concreto é ancoragem por contraste — *"devem ter melhorado"* — e
   observo que meus seis números ficaram todos **acima ou iguais** aos vazados, que é exatamente o
   padrão que a ancoragem produziria. Formei cada nota a partir do artefato e só depois notei essa
   relação; **não consigo provar que a ordem foi essa.**
3. **Recebi três achados de terceiros junto com a tarefa, e confirmei os três.** Mitiguei abrindo
   primeiro os validadores, placares e schemas, e lendo a saída crua de ponta a ponta: cheguei ao
   problema de Negócios sozinho, ao notar as caudas duplicadas e a linha `RESULTADO: 230/233` antes
   de conferir a dica. Ainda assim, não refutei nenhum por inteiro, e isso merece ser dito. A única
   correção que oponho é a do `anyOf`, acima.
4. **Não executei nada, por instrução.** Tudo que digo sobre travas é leitura de código, e a lição
   desta casa é que mutação verde é pergunta, não aprovação — eu só pude fazer a pergunta pelo
   código. Em específico: afirmo que nenhum dos 96 casos do CEO forja um `REPROVED` limpo com nota
   alta com base em varredura das atribuições de `verdict`. Se existir um caso construído por outro
   caminho que eu não tenha alcançado, o `C03` do `ceo-maestro` sobe.
5. **Contei o total próprio de Negócios como 233 derivando das linhas da saída**, não executando o
   validador (linhas 1–232 mais a 243). A conta fecha e coincide com o `RESULTADO` impresso, mas é
   derivação minha sobre uma saída que eu mesmo apontei como mal delimitada.
6. **Descontei a série de ADR** nos seis pares, como o contrato manda, e digo que descontei. Sem
   esse desconto, os três teriam FAIL aberto na rodada e eu teria julgado outra coisa.
