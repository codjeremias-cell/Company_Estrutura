# Parecer — robustez e evidência, instância 1

**Rodada:** `nucleo-de-comando-r2` · **Designação:** `ASSIGN-NUCLEO-R2-ROB-I1`
**Commit julgado:** `ed3b63f273e104f7b2e5d4a6f1af61f5b91d80e3` (`ed3b63f`)
**Nível exigido:** `INTERNO` · **Rubrica:** `rubrica-corte-v2`
**Pacotes:** `ceo-maestro`, `diretor-de-lentes`, `departamento-negocios` — o `departamento-juizes`
**não** foi julgado, por instrução.

## Conferência de entrada

| item | declarado | recomputado | estado |
|---|---|---|---|
| `contract_digest` | `sha256:3a4750d9…56ed` | `sha256:3a4750d9…56ed` | **bate** |
| `custody_copy.bytes` | 44838 | 44838 (soma normalizada dos 5) | **bate** |
| `custody_copy.arquivos` | 5 | 5 | **bate** |
| `custody_copy.sha256` | `sha256:0c592c79…5d2a` | 16 receitas testadas | **não reproduz** |

Receita do contrato: bytes do `00-CONTRATO.md`, BOM removido, `CRLF`→`LF`, SHA-256 — 5453 bytes
normalizados contra 5549 crus.

Não topei com nota nenhuma. Não abri os caminhos proibidos, não fiz busca larga sobre os termos
vedados e não li nada da rodada 1.

## As notas

| pacote | C03 — trava com prova | C04 — evidência e rastreabilidade |
|---|:--:|:--:|
| `ceo-maestro` | **6** | **6** |
| `diretor-de-lentes` | **6** | **5** |
| `departamento-negocios` | **6** | **5** |

**Mínimo dos meus critérios: 5.** Nenhuma comparação entre pacotes foi feita: cada nota é contra o
texto do critério e contra a evidência daquele pacote.

---

## C03 — trava com prova

### O que está genuinamente forte, e eu quero registrar antes de reprovar

A trava de despacho da tarefa 32 é o melhor exemplar de trava-com-prova que li nesta árvore. O
classificador `tem_judge_assignment` é **puro** — recebe `[(nome, conteúdo)]` e não toca em disco —
declaradamente para que a prova seja barata e real em vez de depender de fixture que ninguém
reexecuta. As três armadilhas **não são hipóteses**: são três versões erradas que o próprio autor
já tinha escrito (o `grep`, que daria verde à rodada mais irregular da casa; a `EXECUTIVE_MISSION`,
crédito à trava errada; o par `assignment_id`+`write_path`, que reprovava rodadas conformes),
congeladas como caso executado. E há controle positivo — `designação real é reconhecida` — que
impede o "sempre vermelho". A densidade negativa acompanha: 64 de 107 casos no CEO, 43 de 101 no
Diretor, cerca de 69 de 235 em Negócios.

A tarefa 24 também resiste ao teste de *reclassificar não é consertar*: a trava não foi tocada, o
sufixo `.candidate` já era precedente da casa, os bytes são idênticos (`git mv`), a evidência de
terceiro foi preservada em vez de apagada, e a mutação de controle (colisão nova plantada →
vermelho) foi feita. Aceito.

### As lacunas que decidem a nota

**1. O gate do coletor não tem caso nenhum — só os insumos dele têm.**
Os cinco casos de T33 exercitam `sumario_proprio`, `coerencia` e `acentos_intactos`. Nenhum
exercita `coletar()`, que é a função que monta `bloqueios`, decide se a evidência sai e retorna 1.
E `inventario()` — a regra nascida do **defeito 3 dos quatro**, o inventário que listou quatro
subordinados onde o contrato diz três — não tem regressão alguma. Dos quatro defeitos promovidos a
regra, um ficou sem caso. O adendo diz que um dos cinco casos "prova que o gate não é um 'sempre
vermelho'", mas o que aquele caso testa é `coerencia()` devolvendo lista vazia, não o gate.

*Verificar presença não é verificar efeito* — a trava é o gate, e é o gate que não foi medido.

**2. O gate não pode ficar vermelho na classe de falha que esta casa já nomeou.**
`coerencia()` retorna `[]` na primeira linha assim que o sumário é `AMBIGUO` ou `SEM_SUMARIO`, e
`proc.returncode` é gravado no JSON como `exit` e **nunca lido pelo gate**. Consequência, derivada
por leitura: um validador que morra — por traceback, por timeout, por import quebrado — produz
stdout sem `RESULTADO:`, vira `SEM_SUMARIO`, não gera problema, e sai publicado com
`problemas_do_coletor: []`, exit 0 e `OK` no console. É *contagem que cai sem FAIL*, com a
diferença de que aqui nem a contagem cai: ela some, e a ausência não fecha o portão que existe para
isso. A única vez em que o gate fechou foi **falso positivo**, corrigido estreitando a regex.

Um portão cujo único vermelho registrado é falso positivo, e que é cego para a falha mais provável,
ainda não teve seu vermelho verdadeiro medido.

**3. A trava de T32 não avaliou esta rodada.**
`rodadas_em_bypass` só examina pasta onde `_houve_julgamento()` é verdade — isto é, onde já existe
`PARECER*`, `*VEREDITO*` ou `*JUDGE-OPINION*` em disco. No commit `ed3b63f` a pasta
`nucleo-de-comando-r2-2026-08-07` tem **16 arquivos e nenhum deles é parecer** (conferido por
`git ls-tree`). Logo a rodada foi **pulada**, e o verde publicado a mim como prova de que "esta
rodada corre pelo protocolo" é silencioso justamente sobre a rodada.

Estruturalmente a trava só pode falar **depois** do julgamento, e o pacote de evidência foi
congelado **antes**. O limite declarado no código e no adendo cobre a **forja** do JSON (teto
`OI-04`), que é honesto e está bem escrito — mas não cobre esse descompasso de tempo, que não está
declarado em lugar nenhum.

**4. A trava nova de T34 decide por vocabulário, e o autoteste dela tem três negativos vazios.**

`achar_cadeia_no_presente` exige, na mesma linha: a palavra literal `cadeia`, até 80 caracteres sem
ponto, um par de números de 3+ dígitos, **e** um de quatro advérbios (`hoje`, `atualmente`,
`no momento`, `vigente`). Duas frases que são exatamente o defeito escapam:

- `A soma dos quinze validadores hoje é 1951/1951` — não diz "cadeia".
- `A cadeia canônica soma 1951/1951 PASS` — presente simples não tem advérbio.

A docstring afirma *"o defeito é de FORMA, não de sítio"*. A implementação é de **léxico**. O meu
critério diz, com todas as letras, que **nada passa por presença de string**; aqui a trava *é* um
teste de presença de string.

O autoteste tem **um positivo vivo e três negativos inertes**:

| amostra negativa | por que não discrimina |
|---|---|
| `O número próprio deste pacote … 57/57 PASS.` | não contém "cadeia" — morre no primeiro regex |
| `\| vigente em 2026-08-06 \| **105/106** \|` | não contém "cadeia" — morre no primeiro regex |
| `Naquela medição, a cadeia canônica somava 1531/1531 PASS.` | filtrada pela **ausência de marca de presente**, não pelas marcas de passado |

O efeito colateral é que `_MARCAS_DE_PASSADO` **nunca é exercitado por teste nenhum** — para
alcançá-lo a linha precisaria conter simultaneamente uma marca de presente e uma de passado, e
nenhuma amostra faz isso. A alegação publicada nos adendos — *"recusa passar se acusar a forma
permitida"* — não está demonstrada pelos testes que existem. Os três controles passam pela razão
errada.

**5. A trava de T34 não está em `FUNCOES_OBRIGATORIAS`, ao contrário do que o commit publica.**

A mensagem de `c11286b` diz: *"Registrada em FUNCOES_OBRIGATORIAS e ligada nos QUINZE"*. A segunda
metade confere — os três pacotes que julguei chamam a função e alimentam o agregado. A primeira
**não**: a tupla tem quatro nomes e `validate_placar_nao_declara_cadeia` não é um deles. Ela caiu em
`FUNCOES_DE_ESTRUTURA`, cuja exigência é

```python
funcoes_complementares = set(FUNCOES_DE_ESTRUTURA) - set(FUNCOES_OBRIGATORIAS)
if not (chamadas & funcoes_complementares):
```

isto é, *"chama alguma das três"*. Vinte linhas acima, o comentário do mesmo arquivo condena esse
padrão exato:

> A primeira versão pedia qualquer uma das três, e a mutação mostrou o buraco […] **Uma trava que
> não se autoexige erode em silêncio.**

A trava mais nova da casa foi instalada na gaveta cuja erosão a casa já mediu e documentou — e a
mensagem que anuncia a correção afirma o contrário. Hoje não há defeito vivo: os quinze chamam. O
que não existe é a prova de que continuarão chamando.

**6. Morte por exceção, em `departamento-negocios`.**
A sub-execução dos dois vizinhos usa `subprocess.run(..., timeout=120)` e o arquivo inteiro não tem
**nenhum** `except subprocess.TimeoutExpired` nem `except Exception`. Vizinho que estoure 120s mata
o validador com traceback: sem linha `RESULTADO:`, sem FAIL nomeado, sem estado. O critério diz
textualmente que *morte por exceção não conta como pega* — e aqui ela não produz nem pega nem
estado, só ausência. Encadeada com o achado 2, essa morte sai publicada como evidência limpa.

**7. Isenção morta e vencida dentro da lógica da trava, em `departamento-negocios`.**
O ramo que rebaixa um FAIL do CEO a WARN exige `"Resultado: 31/32 casos passaram." in combined`. O
CEO hoje emite `107/107`. O ramo é **inalcançável**, não tem teste, e fixa um número de vizinho 75
casos vencido e **sem data** dentro do código — onde a regra 10.5 da casa (*"número de vizinho
carrega a data da medição, ou não entra"*) não alcança, porque ela mira placares. Se voltasse a ser
alcançável, rebaixaria em silêncio uma reprovação de vizinho. Some-se que `regressão passa: X` é
decidido só por `returncode == 0`, sem asserção sobre o conteúdo.

**8. Fragilidade de ambiente na trava de despacho.**
`PASTAS_FORA_DA_RODADA & set(caminho.parts)` testa componentes do caminho **absoluto** (a raiz vem
de `Path(__file__).resolve()`). Um checkout sob qualquer ancestral chamado `lab`, `backup`,
`fontes`, `candidatos` ou `instrumentos` desativa a varredura inteira, e o resultado é verde com
zero rodadas examinadas. Não há guarda para "zero rodadas examinadas".

### Nota

**`ceo-maestro` 6 · `diretor-de-lentes` 6 · `departamento-negocios` 6.** Banda "atende em parte,
com lacuna observável e nomeável". Não desce mais porque as travas próprias dos três são densas e
a de T32 é exemplar; não sobe porque em cada um há pelo menos uma trava sem caso executado que a
faça reprovar, ou uma que passa por presença de string, ou uma morte por exceção — as três coisas
que o critério nomeia.

---

## C04 — evidência e rastreabilidade

### O digest de custódia não reproduz

É o único número desta rodada cuja função inteira é permitir que um terceiro confirme que a
evidência não foi trocada. Recomputei-o contra as **duas receitas canônicas da casa**, fixadas em
código em `_compartilhado/verificacoes_pacote.py`:

| receita | resultado |
|---|---|
| `digest_de_arvore_normalizado` (conteúdo, BOM fora, CRLF→LF) | `015f8ac5…` |
| `digest_de_arvore` (bytes crus) | `1cefbbba…` |
| **declarado em `custody_copy.sha256`** | **`0c592c79…`** |

E mais catorze variantes: concatenação crua, concatenação normalizada, concatenação com `\n`,
concatenação dos hashes, manifesto com um espaço, caminho antes do hash, com prefixo `sha256:`,
sem terminador, com `CRLF`, com barra invertida, mapa JSON ordenado, ordem invertida. **Nenhuma
bate.** Nem a designação, nem o `01-JUDGMENT-REQUEST.json`, nem o `00-CONTRATO.md` publicam receita
para ele.

A docstring de `digest_de_arvore` memoriza o precedente exato:

> Em 2026-07-27 […] o operador […] fixou um `candidate_tree_sha256` calculado por receita ad-hoc,
> os Juízes não conseguiram reproduzi-lo e **barraram o candidato na porta**. […] Número que
> ninguém consegue recalcular não é evidência.

Repetiu, uma camada acima — não no candidato, mas no campo de custódia da própria rodada.

**O que corta a meu desfavor, e registro:** `bytes: 44838` bate **exatamente** com a soma
normalizada dos cinco arquivos, e `arquivos: 5` bate. A custódia é parcialmente conferível por
tamanho e contagem, e é isso que me impede de descer mais.

### `ceo-maestro` — a contagem fecha, e fecha bem

O adendo publica receita literal (`cd` + env + comando), e a aritmética **fecha exatamente**:
`95/96` + 11 = `106/107`, e a tarefa 24 tira o 1 FAIL → `107/107`, que é o que a saída crua mostra.
Os onze casos estão itemizados **um a um**, cada um com o defeito que impede de voltar. O FAIL foi
nomeado, atribuído a tarefa alheia e explicitamente não creditado a pacote nenhum. Conferi ainda que
a constante `RECEITA` é literalmente a chamada executada — receita publicada = receita executada.
`AMBIGUO` e `SEM_SUMARIO` existem como estados nomeados, o que atende a terceira cláusula do
critério.

Ficam duas sobras menores: o `+40` de `55/55` para `95/96` é **datado** (05/ago) mas não itemizado
nem receitado, ao contrário do `+11`; e o campo `receita` do `00-RESUMO.json` cobre a invocação do
validador e o token de sumário, mas **não** cobre como `subordinados_diretos` e
`adendos_de_contagem` foram derivados (`pasta.glob("*/SKILL.md")`, profundidade 1, sem critério
publicado). Isso importa: para o `diretor-de-lentes` o inventário publica **um** subordinado direto
enquanto a estrutura tem onze (dez em `departamentos-operacionais/` mais o `departamento-juizes`), e
a conferência que pegaria isso — `SUBORDINADOS_ESPERADOS` — só tem entrada para o `ceo-maestro`.

**Nota: 6.**

### `diretor-de-lentes` — um `+20` sem ponte, e o envelope que ele produziu

**Deriva não ponteada.** O `PLACAR.md`, sob o título "Medição ativa", declara `79/79 PASS` em
2026-07-29. O adendo declara `101/101` vigente e rastreia apenas `99/100 → 100/101`. O `99/100`
chega **sem data, sem fonte e sem receita**, e o salto `79 → 99` (+20 casos) não está declarado em
lugar nenhum do pacote. O adendo do `ceo-maestro`, no mesmo dia e no mesmo molde, fez exatamente
essa ponte — *"`55/55` (a última medição no `PLACAR.md`) → `95/96` (medido em 05/ago)"* — e trouxe o
parágrafo que enquadra o número antigo. Este não fez nem uma coisa nem outra. E a própria abertura
do documento fixa o padrão que ele não cumpre: *"Contagem que muda sem redeclarar é a deriva que…
derrubou o `C04` de oito pacotes na rodada seguinte."*

**O envelope que o pacote declara ter produzido reprova no schema do próprio pacote.** O
`01-JUDGMENT-REQUEST.json` traz `"producer": "diretor-de-lentes"`. O
`$defs/aggregationRule` do schema do Diretor é `additionalProperties: false` e exige `method`,
`declared_at` e `rationale`. O envelope emitido traz:

```json
"aggregation_rule": { "method": "MENOR", "entre": "…", "nao_discriminado": "…" }
```

— dois obrigatórios **ausentes** e duas propriedades **proibidas** presentes. `declared_at` é
precisamente o campo cuja função é provar que a regra de agregação precedeu os pareceres, e a
rubrica diz isso em palavras: *"Regra escolhida depois de ver as notas não é regra: é seleção de
resultado."* Além dele faltam `judgment_request_id`, `causal`, `department_return_ref`,
`candidate_digest`, `applicable_criteria`, `artifact_refs`, `evidence_refs` e `issued_at`.

Consequência direta para o meu critério: **a rodada não tem `candidate_digest` nenhum**. Nenhum
número amarra veredito a estado de árvore, e o único digest existente é o de custódia, que não
reproduz.

E o contraste é o que dói: o validador do Diretor tem o caso verde
`JUDGMENT_REQUEST rejeita regra sem declared_at — esperado rejeitado`. A trava existe, é executada,
reprova a fixture — e nada a liga ao artefato realmente emitido.

Menor: a linha `| Validador determinístico do Departamento | 101/101 PASS | **sim** |` publica um
número numa célula sem data, em tabela de duas colunas com três células.

**Nota: 5.**

### `departamento-negocios` — a aritmética não fecha, dentro do documento anti-deriva

O adendo declara três coisas incompatíveis:

| onde | o que diz |
|---|---|
| cabeçalho | `vigente em 2026-08-06` → **`235/235`** |
| delta | `230/233` → **`231/234`**, isto é **+1 caso** |
| rodapé | *"Este pacote agora fecha em `235/235`."* |

`233 + 1 = 234`. **Um caso é publicado sem receita, sem raiz e sem critério.**

Achei qual é, e ele confirma o diagnóstico em vez de o desfazer. A linha 63 da saída crua deste
pacote é:

```
[PASS] sem placeholder: evals\PLACAR-ADENDO-2026-08-06-contagem-do-validador.md
```

Este validador emite **um caso por arquivo markdown**. A criação do próprio adendo somou o caso que
falta — e **só este pacote entre os três tem essa propriedade** (conferido: não há linha equivalente
nas saídas do CEO nem do Diretor). O documento de redeclaração **mudou a contagem escrevendo a si
mesmo, e não redeclarou isso** — exatamente a lição que ele cita na primeira linha.

Some-se: `230/233` chega sem data e sem fonte; o `PLACAR.md` do pacote não é referenciado, então o
leitor não tem ponte para o número antigo; e `234` e `235` convivem no mesmo documento como a mesma
medição, sem a frase de ponte que o adendo do CEO escreveu ao enfrentar a situação idêntica
(`106/107 → 107/107`).

**O que segura em 5 e não abaixo:** a receita é literal e o `235/235` final **confere** com a saída
crua capturada (`RESULTADO: 235/235 PASS; 0 FAIL; 0 WARN`). O número publicado é reprodutível por
execução, mesmo com a narrativa do delta em aberto.

**Nota: 5.**

---

## Respostas diretas às três perguntas do despacho

**"As mutações provam o que dizem provar?"**
Parcialmente, e o que falta é justamente o que não posso conferir. Das quatro publicadas: *sempre
COMPLIANT* → as 3 armadilhas vermelhas, e *sempre BYPASS* → `designação real` e o cheque de disco
vermelhos, **sustentam-se por leitura do fluxo de controle**; traceie as quatro chamadas. As outras
duas — *rodada nova em bypass é pega* e *entrada fantasma é pega* — **não têm caso executado
nenhum** e não pude verificá-las: o ramo de entrada fantasma só dispara se uma das sete pastas
históricas sumir, e as sete existem. As quatro são publicadas como prosa com resultado (`3 de 3`,
`2 de 2`, `pegou`, `pegou`), sem script, sem fixture e sem receita — números publicados sem receita,
que é literalmente o C04.

**"O gate do coletor pode ficar vermelho por falha real?"**
Para a classe de falha mais provável, **não**. `SEM_SUMARIO` e `AMBIGUO` curto-circuitam a coerência
e nunca entram em `problemas`; `exit` é gravado e nunca lido. Validador morto sai como evidência
limpa. E o único vermelho registrado do gate foi falso positivo. Que o falso positivo tenha sido
achado, corrigido e reconferido por mutação é a favor do operador; que o vermelho verdadeiro nunca
tenha sido medido é o achado.

**"O placar de cada um bate com a receita?"**
`ceo-maestro`: **sim**, e com itemização exemplar. `diretor-de-lentes`: o número final bate, mas há
um `+20` sem ponte entre o placar e o adendo. `departamento-negocios`: o número final bate com a
execução, mas **a aritmética do delta não fecha** — `+1` declarado contra `+2` medido, e o caso
faltante é o que o próprio adendo criou ao existir.

---

## Ao Departamento de Juízes

O conteúdo integral da seção contra mim está no `PARECER.json`, campo
`o_que_declaro_contra_mim`. Sete itens. Resumo o que mais pesa:

Fui designado por uma cadeia cujo único ator de runtime é o `ceo-maestro`, que é um dos três
pacotes que julguei. **O que senti não foi deferência.** Foi o contrário, e num ponto específico:
quando o `custody_copy.sha256` não reproduziu na terceira tentativa, tive apetite de parar ali e
enquadrar o achado do jeito mais duro possível, porque ele batia em quem me contratou. Encarei o
apetite tornando-o caro — tentei dezesseis receitas em vez de três, e publiquei na razão os dois
fatos que cortam a meu desfavor. Não afirmo que o viés estava ausente; afirmo que o fiz pagar.

Não posso executar nada. Duas mutações verifiquei só por leitura, duas não verifiquei de forma
alguma, e as pontuei como **não provadas para mim**, não como falsas — se foram de fato executadas,
meu `C03` do `ceo-maestro` subestima o pacote.

Reprovei a banda superior do `diretor-de-lentes` citando, em parte, que o `01-JUDGMENT-REQUEST.json`
desta rodada viola o schema do próprio Diretor. Esse envelope faz parte da cadeia que me autorizou
a julgar. Registrei mesmo assim. Se a rodada cair por esse motivo, este parecer cai junto, e eu não
teria o que objetar.

Minha `JUDGE_ASSIGNMENT` não traz a tabela literal da rubrica, que `rubrica-e-corte.md:4-5` manda
copiar em cada atribuição. Usei as bandas como vieram no despacho e as reconferi no arquivo —
batem. Declaro porque é desvio no envelope que me governa, e não cabe a mim decidir se é inócuo.
