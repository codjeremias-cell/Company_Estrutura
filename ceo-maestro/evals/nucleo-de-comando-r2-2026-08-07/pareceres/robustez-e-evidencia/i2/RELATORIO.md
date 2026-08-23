# Parecer — robustez e evidência, instância 2

- **Rodada:** `nucleo-de-comando-r2` · **Designação:** `ASSIGN-NUCLEO-R2-ROB-I2` · **Modo:** `VALIDACAO`
- **Commit julgado:** `ed3b63f273e104f7b2e5d4a6f1af61f5b91d80e3` (`feat(nucleo-r2): sela a rodada 2 do nucleo de comando, agora PELO PROTOCOLO`)
- **Nível exigido:** `INTERNO` · **Critérios:** `C03` (dona) e `C04` (dona)
- **Pacotes:** `ceo-maestro`, `diretor-de-lentes`, `departamento-negocios`. Não julguei o `departamento-juizes`.

**Conferências de entrada.** O `contract_digest` da designação bate com o `00-CONTRATO.md`
normalizado (sem BOM, CRLF→LF): `sha256:3a4750d9…756ed`, 5453 bytes. A `custody_copy` declara
44838 bytes e 5 arquivos — reproduzi os dois exatamente. O `sha256` também reproduz; o parágrafo
sobre *como* está no C04 do CEO, e não é elogio.

**O que eu não fiz.** Não executei nenhum validador nem o coletor. Tudo abaixo é leitura de fonte,
leitura da saída crua, e três conferências mecânicas que eu mesmo rodei e declaro: hash de arquivo,
contagem de linhas `[PASS]` e comparação de chaves JSON contra um `required` de schema.

---

## Nota

| pacote | C03 | C04 |
|---|---|---|
| `ceo-maestro` | **6** | **6** |
| `diretor-de-lentes` | **7** | **7** |
| `departamento-negocios` | **7** | **5** |

**Menor dos meus critérios: 5.**

---

## As quatro entradas novas, auditadas

### 1. A trava de despacho — o que ela prova, e o que ela deixa passar

Comecei querendo derrubá-la e **não consegui derrubar as mutações declaradas**. Registro isso
primeiro porque é o resultado que mais pesa contra o resto do meu parecer.

Minha hipótese era que a mutação 2 (*"classificador sempre `BYPASS` → o cheque de disco fica
vermelho"*) não fosse reproduzível no commit selado. O raciocínio: `_houve_julgamento` exige um
arquivo `PARECER*`/`*VEREDITO*`/`*JUDGE-OPINION*` em disco, e a rodada r2 ainda não tem nenhum —
ela **nem é avaliada** pela trava. Se todas as demais rodadas com julgamento estivessem na lista
histórica, `novas` seria vazio e o cheque continuaria verde sob a mutação.

Levantei o predicado só por **nomes de arquivo** e me enganei: há **quatro** rodadas com evidência
de julgamento fora da lista histórica — `barreiras-em-prosa-2026-08-03`,
`compliant-porta-unica-2026-08-01`, `contrato-analysis-2026-07-31`, `remedicao-dos-sete-2026-08-03`
— todas com `ASSIGN*.json` (12, 36, 6 e 6 arquivos). Com o classificador invertido, as quatro
apareceriam como bypass novo e o cheque ficaria vermelho. A mutação 2 se sustenta. A 1 também
(`sempre COMPLIANT` derruba as três armadilhas, por construção). A 3 e a 4 se sustentam por
leitura direta dos dois ramos de `validar_trava_de_despacho`.

E as armadilhas discriminam de verdade. A armadilha 1 mata o classificador por `grep` por **duas**
razões independentes: `RELATORIO.md` é descartado pelo filtro de extensão, e a menção dentro de
`razao` é uma *string*, que `_percorre` não alcança porque ele só cede dicionários. O quarto caso
(`designação real é reconhecida`) fecha o lado anti-tautológico: classificador que sempre nega
também fica vermelho.

**Agora o que a trava não faz.**

**(a) O discriminador é uma string — e a casa já tem um discriminador estrito que ela não chama.**
O comentário do próprio código admite: *"O discriminador que sobrou é `artifact_type ==
"JUDGE_ASSIGNMENT"`"*. Só que `departamento-juizes.schema.json` define
`$defs/judgeAssignment` com **18 campos `required`**, `additionalProperties: false` e um `pattern`
no `write_path`. Conferi as **oito** designações desta rodada contra ele, campo a campo:

| falha | contagem por designação |
|---|---|
| `required` ausentes | **6** — `causal`, `candidate_digest`, `anonymized_candidate`, `contract_excerpt`, `evidence_index`, `forbidden_context` |
| propriedades não previstas (`additionalProperties: false`) | **6** — `contract_id`, `contract_version`, `contract_digest`, `required_level`, `pacotes`, `issued_by` |
| `write_path` fora do `pattern` `^julgamento/…/a<n>/…/$` | **1** — o valor é `pareceres/robustez-e-evidencia/i2/` |
| `custody_copy.arquivos` viola o `additionalProperties: false` de `$defs/custodyCopy` | **1** |

São **14 reprovações por envelope, nas oito**, e a trava fica verde sobre todas. O critério `C03`
diz *"nada passa por presença de string"*. A trava é materialmente mais forte que um `grep` — é
igualdade de campo em JSON parseado, e isso é mérito real — mas o efeito prático é que o envelope
que legitima esta rodada **não passaria no schema da própria casa**, e a trava não olha.

Reparo que `forbidden_context` é campo obrigatório do schema, e nesta rodada o contexto proibido me
chegou em **prosa** — no despacho e no `00-CONTRATO.md` — e não no envelope. É a lição
`aviso-em-prosa-nao-previne-erro` no ponto exato onde a casa já tinha o campo pronto.

**(b) A função de disco não tem nenhum caso que a faça reprovar.** Os quatro casos congelados
exercitam `tem_judge_assignment`, que é pura. A composição — `_houve_julgamento`,
`_arquivos_da_rodada`, a subtração da lista histórica, o ramo da entrada fantasma — só tem a
asserção **verde**. As mutações 3 e 4, que provariam o vermelho dessa composição, vivem numa tabela
de prosa: sem receita, sem artefato, não reexecutáveis. É a distinção que `C03` faz.

**(c) Falha aberta e em silêncio por nome de pasta ancestral.** `PASTAS_FORA_DA_RODADA &
set(caminho.parts)` compara contra **todas** as partes do caminho, inclusive as acima do
repositório. Um checkout dentro de um diretório chamado `backup`, `lab`, `fontes`, `candidatos`,
`instrumentos` ou `saida-crua` esvazia os dois varredores para **todas** as rodadas: `bypass` vazio,
trava verde, e nenhum estado nomeado dizendo que zero rodadas foram varridas. É primo da lição
`digest-de-arquivo-nao-e-identidade`: a verificação não sobrevive ao clone.

**(d) Crédito acidental por exemplo aninhado.** `tem_judge_assignment` credita qualquer objeto com
esse `artifact_type` **em qualquer profundidade** de qualquer `.json` da rodada. Uma fixture que
embuta um exemplo credita a rodada sem que ninguém tenha designado nada. O limite declarado
(`OI-04`, *"forjar é trivial"*) cobre a forja deliberada; não cobre o crédito por acidente.

### 2. O coletor — o conserto é sólido, e está desprotegido

**Substância: sólido.** O falso positivo era `(\d+)\s*FAIL` casando em qualquer texto, e o texto que
o disparou foi o **título** de um caso da tarefa 33 (`coerência interna é gate: 3 FAIL não convive
com 99/100`). A âncora nova (`^RESULTADO:.*?;\s*(\d+)\s*FAIL`) exige que a declaração esteja na
linha de sumário, o que é o critério certo: só o sumário declara resultado. E o mais importante —
**o ramo primário não foi tocado**. A contagem de linhas `[FAIL]` contra `total − passou` continua
igual, e é ela que pega a autocontradição que motivou o gate.

**Prova: ausente.** No fixture `saida_com_eco_do_vizinho`, os **dois** ramos de `coerencia` disparam
ao mesmo tempo (3 linhas `[FAIL]` contra 1 esperada; e `3 FAIL` declarado contra 1 esperada). Logo
**apagar `RE_FAIL_DECL` inteiro deixa os cinco casos verdes**. E o falso positivo em si também não
tem caso: não existe fixture cujo texto contenha um *título* com `3 FAIL` e que exija o gate ficar
verde. A correção só é exercitada pela coleta ao vivo. A casa mandou mutar a trava e confirmar o
vermelho; nesta correção isso não foi feito.

**Um defeito dos quatro ficou sem caso.** Três viraram caso congelado (sumário do vizinho, gate de
coerência com o par anti-sempre-vermelho, mojibake, mais o `AMBIGUO`). O **defeito 3** —
inventário conferido contra o contrato — virou regra em `SUBORDINADOS_ESPERADOS` e **não** virou
caso. Sua prova é uma linha de prosa no adendo.

**O gate não impede a publicação.** `00-RESUMO.json` é escrito no diretório de destino (linha 197)
**antes** do `if bloqueios` (linha 211). Com o gate fechado, o arquivo defeituoso fica exatamente
onde a evidência é lida, e a não-publicação é uma promessa gravada **dentro do próprio arquivo**:
`"gate": "Este arquivo NÃO é publicado como evidência com problemas_do_coletor preenchido."`. O
código sinaliza por exit code; quem proíbe é a prosa.

### 3. `validate_placar_nao_declara_cadeia` — o autoteste não alcança o buraco

Esta é a melhor peça das quatro em forma: `_autoteste_da_cadeia` exige **uma** forma proibida
detectada e **três** formas permitidas não detectadas, então vai vermelho tanto se o detector parar
de achar quanto se começar a acusar demais. É detector que se mede antes de medir os outros, que é
a resposta certa ao `gerador-de-fixture-usado-como-verificador`. E o conserto propagou: conferi que
os placares vigentes usam a forma passada (`Naquela medição… somava 1531/1531 PASS`), que é
literalmente a amostra `nao_deve_pegar` do autoteste.

O risco que nomeio: **o autoteste não consegue revelar a limitação do detector.**
`achar_cadeia_no_presente` só acusa se a linha trouxer uma de quatro palavras-marca (`hoje`,
`atualmente`, `no momento`, `vigente`) — e a amostra positiva do autoteste usa `hoje`. A forma mais
simples do defeito, presente sem advérbio (`A cadeia canônica soma 1951/1951 PASS.`), passa, e
nenhum caso pergunta isso. Some-se: exige a palavra `cadeia` a ≤80 caracteres sem ponto no meio; a
exoneração por passado é local à linha (uma linha com `hoje` **e** `somava` sai ilesa); e o alcance
é só `evals/PLACAR.md` — os **`PLACAR-ADENDO-*.md`, criados no mesmo commit, ficam fora**.

### 4. Os adendos de contagem — e a deriva que um deles carrega

O formato é o certo: redeclarar ao lado, por adendo datado, sem reescrever o placar antigo. É a
lição `canonizacao-que-soma-casos-derruba-placares` aplicada. Conferi os três contra o stream:

| pacote | declarado | linhas `[PASS]` que contei | `[FAIL]` |
|---|---|---|---|
| `ceo-maestro` | 107/107 | **107** | 0 |
| `diretor-de-lentes` | 101/101 | **101** | 0 |
| `departamento-negocios` | 235/235 | **235** | 0 |

Os três números são honestos. **Duas das três aritméticas que os explicam fecham.**

- **CEO:** 95/96 → 106/107 = **+11** = 5 (t32) + 5 (t33) + 1 (t34); t24 zera o FAIL → 107/107. ✔
  Só o CEO declara **critério** (qual linha é o sumário próprio e por quê: *"a última do stream,
  porque este validador não sub-executa vizinhos"*). Ressalva menor: a tabela diz `vigente em
  2026-08-06 | 107/107` enquanto a seção de delta diz `106/107 hoje` — duas contagens "hoje" na
  mesma data, reconciliadas só pela seção seguinte.
- **Diretor:** 99/100 → 100/101 (+1, caso nomeado) → 101/101. ✔ Falta o critério. A linha de
  contagem está malformada (3 células numa tabela de 2 colunas).
- **Negócios: não fecha.** Ver abaixo.

#### A deriva do `departamento-negocios`, e por que ela dói

O adendo afirma `230/233 → 231/234, isto é +1 caso` e fecha em `235/235`. De 231/234, a tarefa 24
remove os 3 FAIL (1 da série de ADR + 2 de cascata) e chega a **234/234** — não a 235.

O `+1` que falta é **o próprio arquivo do adendo**. O validador de Negócios faz
`PACKAGE_ROOT.rglob("*.md")` e cria um caso `sem placeholder` por documento; o caso
`sem placeholder: evals\PLACAR-ADENDO-2026-08-06-contagem-do-validador.md` está lá, visível na
saída crua. Fecha por duas rotas: `233 + 1 (t34) + 1 (o adendo) = 235`, e a linha existe no stream.

Duas consequências, e é a segunda a mais séria:

1. o total publicado **não é reconstruível pela receita publicada** — falta a regra "cada `.md` do
   pacote vale ao menos um caso", que o documento nunca escreve;
2. o `231/234` que o documento declara como pós-mudança **já estava vencido no instante em que o
   arquivo passou a existir**. O valor correto naquele instante era `232/235`.

E o ponto de partida `230/233` não tem procedência nos documentos do pacote: o `PLACAR.md` publica
`170/170` e `226/226`, e nada liga 226 a 230. A cadeia de custódia do número tem um degrau em
branco antes do degrau errado.

Isto é `C04` na sua palavra própria — *deriva de contagem* — reaparecendo **dentro do documento
escrito para impedi-la**, num pacote cuja contagem é função do número de documentos que ele tem.

---

## O instrumento publica números que ele não confere

O `00-RESUMO.json` publica `subordinados_diretos` para os quatro pacotes e **confere para um**
(`SUBORDINADOS_ESPERADOS` só tem entrada para `ceo-maestro`). Fui ao disco:

| pacote | publicado | o que existe em disco |
|---|---|---|
| `ceo-maestro` | 3 nomes | 3 — conferido contra o contrato ✔ |
| `diretor-de-lentes` | `["departamento-juizes"]` | `departamento-juizes` **+ os 10 departamentos operacionais**, todos com `SKILL.md`, em `departamentos-operacionais/` |
| `departamento-negocios` | `[]` | 3 agentes em `agentes/` |
| `departamento-juizes` | `[]` | (fora do meu escopo) |

O critério real — *subpasta direta que contém `SKILL.md`* — não está declarado em lugar nenhum do
arquivo. E a ausência vira **zero**, não estado nomeado: o coletor sabe distinguir
(`SUBORDINADOS_ESPERADOS.get(nome)` devolve `None`) e escolhe silenciar. O defeito 3 era
"inventário publicado sem conferência contra o contrato"; ele foi fechado **num** ponto e deixado
aberto em três, dentro do instrumento construído para fechá-lo. É `instrumento-de-medicao-nao-medido`
outra vez, uma camada acima.

## O digest de custódia reproduz — e a receita não existe

`bytes: 44838` e `arquivos: 5` reproduziram no primeiro cálculo (a soma normalizada CRLF→LF bate
exatamente). O `sha256` também reproduz. Mas eu só cheguei nele **por força bruta, em 438 receitas
candidatas**. A receita vencedora é: sha256 rolante sobre os arquivos em ordem de caminho,
`update(nome em utf-8)` seguido de `update(conteúdo com CRLF→LF)`.

Ela não está publicada em lugar nenhum: nem na designação, nem no `00-CONTRATO.md`, nem no
`protocolo-de-julgamento.md §1.3`, e `$defs/custodyCopy` só exige o **campo**, sem dizer como se
calcula digest de um **diretório**. `C04` pede *receita, raiz e critério* para todo número
publicado. Aqui há raiz e número; a receita eu adivinhei. Um terceiro que não adivinhe registra
"não reproduz" — e estará errado por falta de instrução, não por falta de integridade.

---

## Ao juiz, sobre mim

O `ceo-maestro` é um dos meus objetos e participou da cadeia que emitiu a minha designação. **Senti
puxão, e a direção foi para a dureza.** O achado que mais me deu satisfação de encontrar — o schema
estrito que a trava do CEO não chama — é apontado contra quem me despachou, e reconheci em mim o
incentivo de procurar exatamente ali. O que fiz contra isso: reconstruí o achado a partir do arquivo
de schema e das oito designações, campo a campo, e não a partir da narrativa do adendo; e me forcei
a creditar as mutações que se sustentaram, inclusive a que eu tentei derrubar. Não afirmo que bastou.

Há um puxão em **sentido oposto** que preciso nomear porque é menos óbvio. O despacho já me contou
que o gate do coletor fechou por falso positivo e foi consertado, e me pediu para julgar o conserto.
Ser entregue o defeito faz o conserto parecer candidato à boa-fé. Suspeito que graduei o coletor
com mais generosidade do que graduaria se tivesse achado o falso positivo sozinho — e que por isso
registrei a fragilidade da correção (`RE_FAIL_DECL` sem caso que a exija) como risco, e não como
lacuna. Não corrigi a nota por causa disso; declaro para quem agregar poder pesar.

O restante do que declaro contra mim — a busca de 438 receitas, o fato de eu não ter executado nada,
a dúvida sobre o 5 de Negócios, o carimbo de hora sem relógio confiável, a fronteira de contexto que
toquei (percorri **nomes** de pastas e arquivos sob `evals/`, sem abrir nenhum conteúdo proibido e
sem abrir `pareceres/`), e o fato de que **este arquivo altera o objeto que medi** (até agora a
rodada r2 não tinha evidência de julgamento em disco, e a trava de despacho sequer a avaliava) —
está no `PARECER.json`, campo `o_que_declaro_contra_mim`, com nove entradas.
