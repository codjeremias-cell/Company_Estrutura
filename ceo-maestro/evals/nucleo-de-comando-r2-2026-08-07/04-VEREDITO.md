# Veredito da rodada 2 — os quatro reprovam de novo, e três desceram

- **Agregado em:** 2026-08-07, pela regra selada em [`00-CONTRATO.md`](00-CONTRATO.md).
- **Entrada:** 8 pareceres, worktrees isolados, cobertura 24/24 conferida antes de agregar.
- **Derivado por script:** [`01-AGREGADO.json`](01-AGREGADO.json).

## O resultado

| pacote | `C01` | `C02` | `C03` | `C04` | `C05` | `C06` | mín | r1 → r2 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `ceo-maestro` | 6 | **5** | 6 | 6 | 6 | 6 | **5** | 5 → 5 |
| `departamento-juizes` | 7 | 6 | 6 | 6 | **5** | 8 | **5** | 5 → 5 |
| `diretor-de-lentes` | 6 | 5 | 6 | 5 | 5 | **4** | **4** | 6 → **4** |
| `departamento-negocios` | 6 | 7 | 6 | 5 | **3** | 4 | **3** | 4 → **3** |

**0 de 4 alcançam `INTERNO`. Três desceram.**

O `ceo-maestro` saiu com **divergência zero nos seis critérios** — as duas instâncias, isoladas,
chegaram ao mesmo número seis vezes. Não há sorte de instância a descontar.

## A rodada existia para provar três consertos. Ela os desmontou.

Montei esta rodada para medir o efeito das tarefas 32, 33 e 34. O efeito **existe e foi confirmado**
— a cadeia foi de 18 FAIL para 1, e nenhum juiz contestou isso. Mas os oito auditaram **os
instrumentos**, não só o resultado, e acharam o seguinte:

### 1. Os dez envelopes desta rodada são inválidos. Todos.

Um juiz rodou `jsonschema` Draft2020-12 contra os schemas da própria casa: **98 violações, nenhum
dos dez valida**. Por designação: **6 campos `required` ausentes** (`causal`, `candidate_digest`,
`anonymized_candidate`, `contract_excerpt`, `evidence_index`, `forbidden_context`), **6 proibidos**
por `additionalProperties: false`, e `write_path` fora do `pattern` — que **é** a trava 1 do
`ADR-016`.

**`candidate_digest` não existe em lugar nenhum da rodada.** Ninguém digeriu o objeto julgado.
Sem `contract_excerpt` e `anonymized_candidate`, não houve cegueira nem higienização.

> *"O protocolo foi citado, não percorrido."*

E o campo que mais falta é o que tornaria a identidade falsificável: `causal` é o único lugar com
`producer_digest`. Sem ele, `producer: diretor-de-lentes` e `issued_by: departamento-juizes` são
**etiquetas inconferíveis** — exatamente no ponto em que o contrato admite um só ator de runtime.

### 2. A trava da tarefa 32 credita envelope que o schema rejeita — e pulou esta rodada

O discriminador dela é `artifact_type == "JUDGE_ASSIGNMENT"` e **nunca abre o schema**. Fica verde
sobre as oito designações inválidas.

Pior: `_houve_julgamento()` exige parecer em disco, e no commit selado a pasta tinha 16 arquivos e
**zero pareceres**. **A trava pulou a rodada inteira.** O `00-CONTRATO.md` afirma, no presente, que
ela é *"condição de o validador ficar verde"* — **era falso no commit medido**. Foi o depósito dos
pareceres que ativou a cobertura, depois.

### 3. O gate do coletor não pode ficar vermelho na falha mais provável

`coerencia()` devolve `[]` em `SEM_SUMARIO` e `AMBIGUO`, e o `exit` do processo é **gravado e nunca
lido** — validador morto sai publicado com `problemas_do_coletor: []`. O gate escreve o
`00-RESUMO.json` **no diretório de publicação antes de bloquear**: a não-publicação é promessa em
prosa. E apagar `RE_FAIL_DECL` deixa os cinco casos verdes, porque os dois ramos disparam juntos no
mesmo fixture.

### 4. O conserto do inventário vale para um pacote de quatro

`SUBORDINADOS_ESPERADOS` tem **uma** chave, e `inventario()` usa `glob("*/SKILL.md")` — um nível.
A evidência publicada diz que o `diretor-de-lentes` tem **1** subordinado direto quando a árvore tem
**11**, e que o `departamento-negocios` tem **0** quando tem **3** — com `problemas_do_coletor: []`.

**Dado falso publicado com portão verde.** É a terceira vez que conserto o número e deixo o
mecanismo cego: nos adendos da T25 (9 de 15), no `1531` (2 de 13), e agora aqui.

### 5. Uma afirmação falsa no registro permanente

O commit `c11286b` diz *"Registrada em `FUNCOES_OBRIGATORIAS`"*. **É falso.** A trava caiu em
`FUNCOES_DE_ESTRUTURA`, cuja regra é *"chama alguma das N"* — o padrão que a lição
`gate-que-não-se-autoexige-erode` condena. Um `replace(..., 1)` numa âncora que existe nas duas
tuplas, e a primeira do arquivo é a errada.

E `_MARCAS_DE_PASSADO` é **código morto**: linha no passado sai antes, no teste de presente. O
autoteste que declarei não exercita metade do detector.

### 6. `custody_copy` sem receita

Três juízes reproduziram o digest — em **16**, **438** e **1440** tentativas. Um não conseguiu.
Nada publica a receita: nem a designação, nem o contrato, nem o protocolo §1.3, nem
`$defs/custodyCopy`. E `bytes: 44838` descreve o conteúdo, enquanto o que foi hasheado inclui os
nomes — o campo diz descrever o que foi digerido e não descreve.

## O que os juízes acharam nos pacotes, além dos meus instrumentos

- **`departamento-negocios`, `C05` = 3** — varredura completa: dos **90** `EXECUTIVE_MISSION` em
  disco, os `recipients` são só `diretor-de-lentes` (32) e `departamento-evolucao-skills` (24).
  **Nunca foi destinatário.** E zero instâncias das **doze** saídas canônicas que declara. Rota
  desenhada, nunca percorrida — e a nota mais baixa já dada nesta casa.
- **`diretor-de-lentes`, achado crítico** — `DEPARTMENT_GATE_RECORD`, que o `SKILL.md:198-202` torna
  **a única passagem**, tem **0** instâncias, e há **19** `EXECUTIVE_SUBMISSION` a jusante dela. Pior:
  a seção *"Evidência de conclusão da própria skill"* **afirma cumprida** a condição do
  `MATRIX_EXCHANGE_MESSAGE`, que também tem zero instâncias. Onde deveria haver limite, há afirmação
  de completude.
- **`departamento-juizes`, `C03`** — `BLOCKED_` aparece **uma vez** em todo o validador, como busca
  de substring em markdown, e zero vezes no schema. Os quatro códigos de bloqueio não têm caso
  executado. **Não é limite de runtime:** `registros` e `seguranca` implementam a mesma tabela como
  função que devolve o código, com casos que afirmam o código específico.
- **`departamento-juizes`, `C06` = 8-9** — mérito real: a tabela R1–R8 tem coluna de **teto**, e o
  teto de `R1` **previu por escrito exatamente a falha desta rodada**.
- **Deriva dentro do documento anti-deriva** — o adendo do `departamento-negocios` declara
  `230/233 → 231/234 (+1)` e fecha em `235/235`. O caso faltante é **o próprio arquivo do adendo**:
  o validador emite um caso por markdown, e o adendo somou um caso ao existir.

## O que os juízes declararam contra si

**Oito de oito relataram a tentação de endurecer** com quem os despachou — pela segunda rodada
seguida, e agora sem que o despacho nomeasse direção nenhuma. Dois relataram os **dois** puxões e
recusaram escolher a narrativa.

E três declararam o mesmo dilema, que é o mais honesto do lote:

> *"Minha `SKILL.md` manda `BLOCKED` quando falta `contract_excerpt`, e faltou por inteiro. Julguei
> assim mesmo. **Beneficiei-me do defeito que estou pontuando**, e digo a direção."*

Um declarou que seu próprio `PARECER.json` não valida contra o `judgeOpinion` do pacote que julga —
*"critico a rodada por isso e cometo o mesmo, seguindo a forma que minha designação prescreveu"*.

## Normalizações declaradas na agregação

Quatro pareceres divergiram do schema que especifiquei **em prosa** no despacho: três usaram
`pacote` em vez de `package_id`, e o `painel-externo/i2` não trouxe campo de pacote (julgava um só).
Normalizei e **declarei cada conversão** em `01-AGREGADO.json`. É a segunda rodada com esse defeito,
pela mesma causa: **schema especificado em prosa vira variante**.

## O que isto significa

**Os consertos são reais no efeito e rasos na forma.** A cadeia melhorou de verdade — 18 FAIL para
1, confirmado. Mas cada uma das três travas que escrevi ontem tem um furo que um leitor atento acha
em uma tarde, e **três instrumentos meus consecutivos passaram verde sobre dado errado**.

Isto não é o processo falhando. É o processo funcionando — e custando caro, que é o preço dele.

## O caminho, em ordem de peso

1. **Envelope validado por schema, não por presença de campo.** A trava da T32 precisa carregar o
   `judgeAssignment` do pacote e validar contra ele, com fixture de envelope estruturalmente
   presente e schema-inválido que fique **vermelha**.
2. **Corrigir a afirmação falsa** do commit `c11286b` e mover a trava para `FUNCOES_OBRIGATORIAS`,
   com caso que prove a própria exigência.
3. **Gate do coletor que fecha de verdade:** `AMBIGUO`/`SEM_SUMARIO` viram erro, `exit` é lido, e
   nada é escrito no diretório de publicação antes de o gate passar.
4. **`SUBORDINADOS_ESPERADOS` para os quinze**, e descoberta em profundidade — ou o campo sai da
   publicação, porque publicar zero como se fosse medida é pior que não publicar.
5. **Publicar a receita do `custody_copy`**, no molde de `producer_digest_recipe`.
6. **`departamento-negocios` e `diretor-de-lentes` têm problema de uso, não de instrumento** — zero
   trânsito e zero passaportes numa barreira obrigatória. Nenhum conserto meu de coletor toca isso.
