# Parecer — experiência e risco, instância 1

- **Designação:** `ASSIGN-NUCLEO-R2-EXP-I1` · lente `experiencia-e-risco` · instância 1
- **Rodada:** `nucleo-de-comando-r2` · **modo** `VALIDACAO` · **rubrica** `rubrica-corte-v2`
- **Commit julgado:** `ed3b63f` (`feat(nucleo-r2): sela a rodada 2 do nucleo de comando, agora PELO PROTOCOLO`)
- **Nível exigido:** `INTERNO`
- **Meus critérios:** `C05` (uso pela cadeia) e `C06` (limites declarados), como dona, sobre
  `ceo-maestro`, `diretor-de-lentes` e `departamento-negocios`. **Não julguei** o
  `departamento-juizes`.

## Placar

| Pacote | `C05` | `C06` |
|---|---:|---:|
| `ceo-maestro` | **6** | **6** |
| `diretor-de-lentes` | **6** | **5** |
| `departamento-negocios` | **5** | **6** |

**Mínimo dos meus critérios: 5.** Todas as seis notas caem na banda **cru** — atende em parte,
com lacuna observável e nomeável. Nenhuma delas é "não atende": as três rotas existem, os três
contratos são sérios e as três baterias fecham em 100%. O que falta, faltou de um jeito que eu
consigo apontar com o dedo.

---

## Primeiro: os envelopes desta rodada são de verdade ou cerimônia?

Fui instruído a não aceitar a palavra de ninguém sobre isso. Conferi.

### O que **é de verdade** — e eu reproduzi

**O `contract_digest` bate exatamente.** Normalizei `00-CONTRATO.md` (sem BOM — conferi; CRLF→LF),
5549 bytes crus viram 5453 normalizados, e o SHA-256 sai
`3a4750d9e983769c555db20d731fc4f012ca24ea851d2211cdc4f93a343756ed`, idêntico ao declarado nas oito
designações e no `01-JUDGMENT-REQUEST.json`.

**A `custody_copy` bate exatamente, e foi tomada antes do despacho.** `bytes: 44838` é a soma dos
cinco arquivos de `saida-crua/` normalizados; `arquivos: 5` confere; e o `sha256` declarado
`0c592c79…` reproduz sob a receita "nome + conteúdo normalizado, por arquivo, em ordem alfabética".
`taken_at` 01:30 é estritamente anterior a `issued_at` 01:35 — a trava 3 do `ADR-016` cumprida na
letra.

**Isso não é pouco.** A custódia é real, o digest é genuíno, e a cronologia está certa. Registro
o crédito antes de cobrar.

### O que **é cerimônia** — e é grave

Uma ressalva sobre a própria custódia: **a receita do digest não está publicada em lugar nenhum**.
O `$defs/custodyCopy` exige `path`, `sha256`, `bytes`, `taken_at` — e nenhum campo de receita. Eu
só cheguei ao valor porque testei dez recipes. Terceiro sem as minhas dez tentativas reportaria
`NAO_REPRODUZIDO` e estaria sendo correto. O número é verdadeiro; a **verificabilidade por
terceiro** é que não está entregue.

E então o achado central desta rodada:

> **Nenhum dos dois envelopes desta rodada valida contra o schema que esta casa escreveu para ele.**

**A minha própria `JUDGE_ASSIGNMENT`, contra `$defs/judgeAssignment`** — 13 não conformidades:

- **6 campos `required` ausentes:** `causal`, `candidate_digest`, `anonymized_candidate`,
  `contract_excerpt`, `evidence_index`, `forbidden_context`.
- **6 campos presentes que `additionalProperties: false` proíbe:** `contract_id`,
  `contract_version`, `contract_digest`, `required_level`, `pacotes`, `issued_by`.
- **`write_path` viola o `pattern`.** O schema exige
  `^julgamento/<handoff>/a<N>/<assignment_id>/$`; o meu é `pareceres/experiencia-e-risco/i1/`.
  Esse pattern É a trava 1 do `ADR-016` — o formato "amarra as três coordenadas", e a minha versão
  não codifica `attempt`: uma segunda tentativa colidiria exatamente onde a trava existe para
  impedir.

**O `01-JUDGMENT-REQUEST.json`, contra `$defs/judgmentRequest`** — 16 não conformidades:

- **8 `required` ausentes:** `judgment_request_id`, `causal`, `department_return_ref`,
  `candidate_digest`, `applicable_criteria`, `artifact_refs`, `evidence_refs`, `issued_at`.
- **8 proibidos presentes:** `request_id`, `producer`, `mode`, `contract_id`, `contract_version`,
  `candidatos`, `custody_copy`, `nota_de_limite`.
- **`aggregation_rule` sem `declared_at` e sem `rationale`**, ambos `required`.

O `declared_at` não é formalidade. É a garantia do `ADR-016` contra escolher a regra depois de ver
as notas — *"regra escolhida depois de ver as notas não é regra: é seleção de resultado"*. O
contrato afirma isso em prosa ("Agregação — selada agora") e omite justamente o campo que a máquina
conferiria.

**E o pior detalhe:** a saída crua desta rodada imprime, verde, o caso que pegaria isso —
`[PASS] JUDGMENT_REQUEST rejeita regra sem declared_at — esperado rejeitado`. A trava está provada
em *fixture* e não é aplicada ao envelope de *produção*, porque **nada valida os envelopes da rodada
contra os schemas**. É o padrão que esta casa já registrou uma vez, reaparecendo um nível acima:
verificar a trava numa entrada sintética não é verificá-la no que de fato trafega.

**Veredito da pergunta:** os envelopes são **reais em substância e não conformes em forma**. Existem,
carregam digest que reproduz, custódia legítima e critérios literais — não são teatro. Mas a
afirmação "esta rodada corre PELO PROTOCOLO" é mais forte do que a evidência sustenta: ela corre
**pelo formato do protocolo**, não pelo protocolo validado.

---

## `C05` — Uso pela cadeia

### `ceo-maestro` — **6**

**A favor, e é forte.** A rota do CEO foi percorrida de verdade, muitas vezes. Contei em disco
**25 instâncias de `EXECUTIVE_MISSION`** e **6 de `EXECUTIVE_SUBMISSION`**, numeradas e
correlacionadas ao longo de nove rodadas em `compliant-porta-unica-2026-08-01`, com uma
`EXECUTIVE-MISSION-JULGAMENTO` dedicada por rodada (`08-`, `24-`, `38-`, `54-`, `81-`, `99-`,
`124-`, `145-`, `167-`). E o vizinho consome o envelope pelo **código real** do CEO, não pelo
desenho: a bateria de Negócios fecha com `EXECUTIVE_SUBMISSION de Negócios aceita pelo schema do
CEO` **e** `pela semântica do CEO`, mais `regressão passa: ceo-maestro`.

**A lacuna, e ela está exatamente onde dói.**

**Primeira: a rodada oferecida como prova de que a rota foi percorrida não contém a perna do CEO.**
Varri `nucleo-de-comando-r2-2026-08-07/` inteira: **zero `EXECUTIVE_MISSION`**. Os únicos arquivos
que citam o token são dois `.stdout.txt` dentro de `saida-crua/`, ecoando nomes de caso. O Diretor
emite o `JUDGMENT_REQUEST` sem missão a montante, e a participação do CEO existe apenas em prosa no
`00-CONTRATO.md`. Isso não é incapacidade — a mesma árvore mostra nove vezes como se faz.

**Segunda: a prova de máquina publicada não pôde ter avaliado esta rodada.** A linha
`[PASS] nenhuma rodada de julgamento nova sem JUDGE_ASSIGNMENT` vem de `validar_trava_de_despacho`,
que chama `rodadas_em_bypass`, que **pula toda pasta em que `_houve_julgamento()` é falso** — e esse
predicado só é verdadeiro quando existe arquivo `PARECER*`, `*VEREDITO*` ou `*JUDGE-OPINION*`. Na
custódia (01:30, cinco minutos antes do despacho) não existia nenhum, e não existia nenhum quando li
a pasta. A trava está **correta**; a afirmação do contrato — *"não é disciplina, é condição de o
validador ficar verde"* — é **prospectiva**, e o verde publicado não a sustenta.

> Ironia que registro porque é literal: **é o depósito deste parecer que ativa a cobertura da trava
> sobre esta rodada.** Antes dele, a rodada era invisível para a própria trava que ela cita como
> tendo passado.

**Terceira, menor:** o discriminador da trava é `artifact_type == "JUDGE_ASSIGNMENT"` e nada mais.
O próprio comentário declara isso. Provei que é verdade: um envelope que falha o próprio schema em
13 contagens continua satisfazendo a trava.

### `diretor-de-lentes` — **6**

**A favor.** Rota percorrida com volume: **9 `JUDGMENT_REQUEST`**, **20 `DEPARTMENT_MISSION`**,
**11 `DEPARTMENT_JUDGE_REPORT`**, mais `DIRECTOR_PLAN`, `DIRECTOR_CAPABILITY_GAP` e
`BLOCKED_RETURN` como instâncias reais. E consumo pelo vizinho, executado:
`MATRIX_EXCHANGE_MESSAGE aceita pelo schema do Diretor` **e** `pela semântica do Diretor`, mais
`regressão passa: diretor-de-lentes`.

**A lacuna.** A única instância canônica que o Diretor produziu **nesta rodada** é o
`01-JUDGMENT-REQUEST.json`, e ela falha o schema do próprio Diretor nas 16 contagens listadas acima
— incluindo o `declared_at` que o próprio validador dele prova saber cobrar. Além disso: o Diretor
declara `Receber missão executiva somente do ceo-maestro` (`SKILL.md:33`) e aqui operou **sem missão
a montante e sem `department_return_ref`**, sem declarar em lugar nenhum que o caso
"meta-julgamento dos próprios pacotes" cai fora do seu fluxo canônico.

Rota percorrida — com o envelope que o próprio schema da casa recusaria.

### `departamento-negocios` — **5**

**Este é o caso literal que o critério nomeia: rota declarada e nunca percorrida.**

O pacote declara doze saídas canônicas. Procurei instâncias materializadas de todas, na árvore
inteira: **zero**. Todo acerto do token vive dentro do próprio pacote — `SKILL.md`, contrato,
`references/`, schema, `evals.json` e *fixtures* do `validate_workflow.py` — mais ecos incidentais
em `stdout` de validador. Nenhuma `EXECUTIVE_MISSION` real jamais teve o Departamento como destino;
nas duas campanhas reais ele aparece só como **pacote contado**, nunca como **alvo de missão**.
**O Departamento nunca abriu uma rodada.**

O `FORWARD-TEST.md` declara 15/15 casos e 62/62 assertions, mas **o cru não foi depositado** —
`evals/` tem apenas `FORWARD-TEST.md`, `PLACAR*.md`, `evals.json` e `validate_workflow.py`, e as
"evidências comportamentais" são duas citações de uma linha. O próprio documento declara que mede
"aderência comportamental aos prompts".

**Crédito real, e por ele não desço mais.** É a prova de consumo pelo vizinho **mais forte que li
nesta rodada**. A bateria de 235 casos termina rodando o envelope pelo código alheio: `schema do
CEO` **e** `semântica do CEO` para `EXECUTIVE_SUBMISSION` e `LIMITATION_REPORT`; `schema do Diretor`
**e** `semântica do Diretor` para `MATRIX_EXCHANGE_MESSAGE`; mais as duas regressões completas. O
envelope é comprovadamente consumível pelos dois vizinhos.

A **forma** está provada. A **rota**, não. `C05` pede transito pelo nome, e transito é o que não há.

---

## `C06` — Limites declarados

### O que eu tomei como "limite nomeado e verificável"

Não inventei a régua: ela existe nesta casa e é cumprível. O padrão que usei como **definição** do
termo (não como linha de base de pontuação — declaro isso contra mim mais abaixo) é a seção
"Riscos residuais declarados" do protocolo dos Juízes: oito linhas, colunas
`Id / Vetor / Consequência / Mitigação / Teto`, lugar único de declaração para o documento todo, e
obrigação incondicional de nomear no relatório. E, mais duro ainda, o Departamento de Auditoria
transforma quatro limites em `const` de schema, de modo que **apagar o limite deixa a bateria
vermelha**.

Isso importa aqui por uma razão específica: **o validador do `ceo-maestro` roda oito casos que
reprovam o envelope de um vizinho por falta dos limites `R6`, `R9`, `R10` e `R11`.** O pacote
**impõe** limite declarado a outro. Vamos ver o que ele carrega.

### O limite que não fechou — a pergunta que me foi feita

> *"Declarar um limite que você não pode fechar conta como `C06` cumprido, ou é desculpa?"*

**Conta. Não é desculpa — e eu digo isso pela régua da própria casa.** O `R11` é literalmente
"TETO DO MÉTODO … não cabe no runtime atual", e é aceito como **limite declarado**, não como
evasão; a coluna `Teto` existe exatamente para o que nenhuma regra fecha. Um limite que você não
pode fechar é a forma mais pura de "onde falha e o que não sabe". Recusá-lo tornaria `C06`
impontuável para qualquer pacote honesto e premiaria o silêncio sobre a divulgação.

**Conferi o limite antes de aceitá-lo, e ele é verdadeiro:**

- `SKILL.md:52` — *"Não executar, corrigir, testar, pontuar ou fabricar evidência"* — **confere
  literalmente**.
- A proibição de chamar Juízes está em `:49-50` — *"não chamar Juízes, departamentos operacionais ou
  agentes diretamente"* — e **não** em `:42`, que é "Encaminhar toda frente técnica ou de produção ao
  `diretor-de-lentes`". Deslize de citação no contrato da rodada; **a substância está certa**.
- E a terceira cláusula eu verifiquei por fora: **não existe despachante além do CEO**. Na lista
  viva de skills desta sessão, a Estrutura aparece com **uma entrada só** — `ceo-maestro` — embora os
  `SKILL.md` aninhados existam no destino implantado. Nem o Diretor nem Negócios são invocáveis.

**Então por que a nota não é alta?** Porque o limite é honesto e **não é durável**. Ele mora no
`00-CONTRATO.md` e no `nota_de_limite` do pedido — dois arquivos que **morrem com a rodada**. Nada
em `SKILL.md`, no contrato ou no schema obriga a rodada seguinte a repeti-lo, e **nenhum validador
ficaria vermelho se ele sumisse**. É a diferença entre declarar um limite e *travá-lo*. A casa já
aprendeu essa lição na forma dura: aviso em prosa não previne erro; trave em código.

Ou seja: **não é desculpa, mas também não é `C06` cumprido.** É a distância entre 9 e 6.

### `ceo-maestro` — **6**

"O que **não** faz" está em nível alto e é **executado**, não só escrito: 12 Guardrails, 12
Proibições, "Não decide especialidade técnica, nota, veredito, conformidade nem prova", `NÃO` explícito
na `description` — com casos que reprovam de verdade (`bypass direto ao executor`, `gate autoafirmado
não esconde falha crítica`, `digest de regras autoafirmado é rejeitado`, `placar forjado é detectado`,
`autoridade errada não aprova`).

"Onde falha" e "o que não sabe" **não estão na superfície normativa do pacote**. Grepei `SKILL.md`,
`CONTRATO-DE-COMPROMISSO.md` e as seis `references/` por limite, risco residual, teto, não fecha,
ponto cego: **todos** os acertos são maquinaria para colher a limitação **de outrem** —
`LIMITATION_REPORT`, `residual_risks` do candidato, `CAPABILITY_GAP`, `LIMIT_REACHED`. O teto
`OI-04` **é dele** (assim declarado, com dono nomeado, em `producao-honesta-2026-08-04/PLACAR.md:165`)
e está escrito nos documentos **dos outros**.

Existe **um** limite próprio dentro do pacote, e é bom: o comentário
*"LIMITE DECLARADO: forjar um JSON com esse `artifact_type` é trivial. Esta trava não torna o bypass
impossível — torna-o VISÍVEL e DELIBERADO"*, em `evals/validate_workflow.py`. Eu **verifiquei que
ele está medido certo** — montei o diff e um envelope que falha o próprio schema em 13 contagens
ainda satisfaz a trava. Mas é comentário de código, cobre uma trava só, e nada exige sua presença.

### `diretor-de-lentes` — **5**

"O que não faz" está bem posto e conferido por trava: "orquestra; não executa, não julga e não
autoriza exceções"; "Impedir qualquer atalho `CEO → Departamento`, `Diretor → Agente` ou
`Negócios → Departamento`" — com casos verdes que reprovam.

Os **outros dois terços do critério estão vazios**. Varri `SKILL.md`, o contrato e as **sete**
`references/`: exatamente três acertos, e os três são sobre limite **alheio** — "literalmente os
limites do CEO", "conferir `LIMITATION_REPORT`", "risco residual aceito | CEO". Não há seção de
riscos residuais, não há teto, não há "o que eu não sei".

E há um desconhecido **vivo e nomeável** sobre o qual o pacote se cala: ele dirige dez Departamentos
operacionais mais os Juízes, e **nenhum deles é invocável no runtime** — o mesmo teto do ator único,
verificado por mim contra a lista viva. Nada no pacote menciona isso.

### `departamento-negocios` — **6**

"O que não faz" é o mais completo que li e o mais conferido por trava: lista "Você não pode" com 8
itens, 15 Proibições no contrato, `description` que termina em "Não use como consultor executor,
Juiz, CTO, decisor executivo nem substituto de aconselhamento financeiro regulado", e uma seção
"Entradas aceitas" que nomeia **cinco chamadores ilegítimos um a um** com o estado de falha
correspondente. E reprova de verdade: `rejeita JUDGE_REPORT produzido localmente`,
`rejeita EXECUTIVE_DECISION produzido localmente`, `rejeita EXCEPTION_REQUEST produzido localmente`,
`rejeita matriz para si próprio`, `rejeita fallback de capacidade`, `rejeita gerente fabricando
relatório`, `rejeita quarto agente`.

Há ainda **um limite próprio de domínio, nomeado e verificável**, que os outros não têm: "não
oferecer aconselhamento financeiro pessoal regulado" e "responsabilidade das alegações e limites
regulatórios" (`SKILL.md:119`). Isso é um "para o que eu não devo ser usado" de verdade, com modo de
falha concreto. E os estados de recusa são nomeados, não genéricos: `B_BLOCKED` e
`BUSINESS_CAPABILITY_GAP`, com gatilho declarado.

Falta o "onde falha". Não há riscos residuais, não há teto, e **o desconhecido mais consequente do
pacote fica calado**: ele nunca foi acionado, a régua interna de 9,5 nunca correu sobre uma proposta
real, e nada no pacote diz isso. Ironia registrada: `references/regua-de-avaliacao.md:37` exige que
a nota `10.0` traga "risco residual explicitado" — do candidato, sempre do candidato, nunca do
próprio Departamento.

---

## Contra mim

Está integralmente em `PARECER.json::o_que_declaro_contra_mim`, com nove itens. Os quatro que mais
pesam, em resumo:

1. **Provei uma ausência com busca filtrada.** O "zero instâncias `BUSINESS_*`" saiu de um grep com
   seis padrões de exclusão que **eu** escrevi para respeitar o contexto proibido. Filtro esconde. Se
   existir instância real dentro de qualquer um deles, o achado central sobre Negócios está errado e
   a nota está subestimada. Não verifiquei, e pelas regras não podia.
2. **Não executei nada** (proibido), então o achado da trava T32 é leitura de código mais listagem de
   diretório. É o raciocínio mais forte que fiz sem máquina, e por isso o mais frágil.
3. **Li notas que não eram minhas.** Ao grepar por "departamento-negocios" caí num relatório de
   julgamento de **outra** rodada, sobre **outro** candidato e **outro** critério
   (`C07-CONTAGEM-E-ARVORE`), com notas 8 e 9. Não está na minha lista de proibidos e não toca meus
   pacotes nem meus critérios — mas li nota alheia e declaro.
4. **A direção do meu viés foi dureza.** Fui instruído a não presumir a direção, então descrevo o
   que aconteceu: quando descobri que os envelopes desta rodada falham os próprios schemas, **eu quis
   que esse achado fosse decisivo**, e tive de me perguntar duas vezes se estava pontuando a *rodada*
   em vez dos *pacotes*. Também escrevi 7 para `ceo-maestro` `C05` e depois baixei para 6 por leitura
   literal da rubrica; não consigo separar com honestidade o quanto foi rigor e o quanto foi a mesma
   vontade de endurecer com quem me despachou. E o efeito mais concreto disso: **passei mais tempo
   procurando defeito na cadeia que me despachou do que no `departamento-negocios`, que não me
   despachou nada.** As seis notas não saem da mesma quantidade de esforço.
