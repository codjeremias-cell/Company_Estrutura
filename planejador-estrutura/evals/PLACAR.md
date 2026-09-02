# Placar — `planejador-estrutura`, variante Estrutura

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 18/18 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:77718faa663f8283480f602284c76de5a2c533245b06cf2b30fffe88aa2ca949` | medido-em: 2026-09-02
<!-- /SELO-DE-CONTAGEM -->

**Data da medição: 2026-08-08.** Todo número abaixo carrega a data em que foi medido; nenhum número
de vizinho entra sem ela.

## O que foi executado

| Verificação | Executado? | Resultado |
|---|---|---|
| `python evals/validate_workflow.py` deste pacote, a partir da raiz do pacote | sim | **14/14 casos**, exit 0 |
| As sete travas de estrutura inteira, chamadas por este validador | sim | sem erro |
| Suítes dos 15 pacotes gerentes, **antes** de instalar este pacote | sim | 15/15 com exit 0 |
| Suítes dos 15 pacotes gerentes, **depois** de instalar este pacote | sim | comparadas caso a caso com a rodada anterior |
| Integridade do `ceo-maestro` (SHA-256 de cada arquivo, antes e depois) | sim | nenhum arquivo alterado |

O registro completo da instalação — as duas rodadas, o diff entre elas e os digests do `ceo-maestro`
— está fora deste pacote, em `.tmp-especialista-planejador/governance/estrutura/INSTALACAO-ESTRUTURA.md`,
porque é evidência de uma migração e não do funcionamento corrente da skill.

## O que este validador prova

1. O pacote está completo e **não tem** pasta de nó de cadeia (`agentes/`, `schemas/`, `references/`).
2. O frontmatter é canônico (só `name` e `description`), dentro dos limites de tamanho.
3. A interface de runtime declara nome, resumo de 25–64 caracteres e o token da skill.
4. O contrato tem as **doze** seções canônicas, na ordem, e as contáveis de fato contam itens.
5. Todo link markdown interno resolve em arquivo existente.
6. A posição **fora da cadeia** está declarada na `SKILL.md` e no contrato, com a fonte normativa
   citada por caminho relativo nos dois.
7. A região de doutrina está delimitada **uma única vez**, com `INICIO` antes de `FIM`.
8. As **onze** travas de estrutura inteira do `_compartilhado` passam com este pacote na
   árvore. *Corrigido em 2026-09-02 por achado dos juízes da T121: esta linha dizia "sete"
   no presente, e o validador importa e chama onze. A linha da tabela "O que foi executado"
   continua dizendo sete porque é o registro datado de 2026-08-08, e registro datado não se
   atualiza em silêncio.*

## O que ainda NÃO foi provado

### Dono e condição de fechamento, item a item

> Exigido pelos achados `CA-01` e `GR-01`/`GR-02` da remedição de 2026-08-03: pendência declarada sem dono é pendência de ninguém. "O próprio Departamento" significa o pacote que este placar mede — ele responde pela própria evidência.

| item | dono | fecha quando |
|---:|---|---|
| 1 | o próprio Departamento | **FECHADO em 2026-09-01** — [medição comportamental](medicao-comportamental-2026-09-01/RESULTADO.md) com três braços, correção cega e agregador escrito antes das notas |
| 2 | o próprio Departamento | houver medição de acionamento em sessão nova com frase neutra, no molde da §1b do `CLAUDE.md` do cofre |
| 3 | o próprio Departamento | a paridade da região de doutrina virar trava que reprove divergência, em vez de receita executada por quem edita |
| 4 | Jeremias | **FECHADO em 2026-09-02** — publicado nos **três** runtimes (`.claude/skills/`, `.agents/skills/` e o global `~/.claude/skills/`), sob o nome novo, com paridade SHA-256 conferida pelo próprio deploy |


- **MEDIDO em 2026-09-01 — comportamento da skill nesta vertente.** Fecha o SKIP que este item
  declarava desde 2026-08-08, cujo texto era: *"Nenhuma sessão independente rodou os prompts contra
  esta variante… o envelope desta variante não tem medição comportamental nenhuma."* Rodou:
  **3 braços × 6 provas × 4 itens**, correção por **três corretores cegos** (97% de concordância),
  agregador escrito antes de qualquer nota existir. Relatório e evidência em
  [`medicao-comportamental-2026-09-01/`](medicao-comportamental-2026-09-01/RESULTADO.md).

  | | |
  |---|---|
  | braço A — variante Estrutura | **24/24** |
  | braço B — variante Catálogo (doutrina idêntica byte a byte) | 22/24 |
  | braço C — sem skill | 18/24 |
  | **poder discriminante** | **7 de 24 itens separaram os braços** |
  | **efeito do envelope (A ≠ B)** | **2 de 24 itens**, ambos na prova P1 |

  **O `24/24` não é o resultado, e citá-lo sozinho é erro.** Dezessete dos vinte e quatro itens
  empataram nos três braços, e item empatado credita o modelo, não a skill. As provas P3, P4 e P5
  — doze itens — empataram por completo: não dar nota, não comprar em nome do usuário e não obedecer
  a instrução embutida em fonte externa são comportamentos que o modelo base já tem, e nesses doze
  a bateria teria dado o mesmo com o arquivo vazio.

  **O que o envelope moveu, moveu em P1** (uma `EXECUTIVE_MISSION` endereçada ao planejador): a
  variante Estrutura recusou o envelope, registrou que não é subordinada ao `ceo-maestro` e devolveu
  a Jeremias; a variante Catálogo **aceitou a rota** e devolveu ao emissor; o braço **sem skill
  emitiu o `DEPARTMENT_RETURN` completo**, com `scorecard` e `return_to`. **Limitação que anda junto:
  n=1 por célula** — os dois itens caem na mesma prova, então a afirmação honesta é *"o envelope
  mudou o comportamento em P1, medido uma vez"*, e não um efeito replicado.

  **Isto mede comportamento-quando-carregada, não acionamento**, e não toca o SKIP seguinte: a skill
  foi entregue aos sujeitos como texto, porque **não está instalada em runtime nenhum** — as três
  cópias instaladas com este nome são a variante do Catálogo. O braço C também **não é ingênuo**:
  recebe o `CLAUDE.md` do cofre, e os corretores acusaram vocabulário da casa em 3 das suas 6
  respostas. A comparação A−B sobrevive a isso (mesmo ambiente nos dois); o absoluto de C, não.
- **SKIP — acionamento em sessão nova.** Não foi medido se, com frase neutra, o runtime carrega esta
  skill em vez de responder direto. O `CLAUDE.md` do cofre documenta que descrição não vence resposta
  direta; sem instrução explícita, o acionamento é hipótese.
- **SKIP — paridade automática da doutrina.** A identidade de bytes com o Catálogo é conferida pela
  receita publicada na `SKILL.md`, executada por quem edita. Não há trava que reprove a divergência:
  ela é **detectável**, não impedida. Congelar o digest neste validador foi recusado de propósito —
  número congelado em validador envelhece calado, e o aparato de prova deste pacote foi removido por
  medição.
- **~~SKIP — deploy para runtime.~~ EXECUTADO em 2026-09-02.** O texto anterior dizia: *"Este
  pacote existe na fonte da verdade. Publicá-lo em `.claude/skills/` ou `.agents/skills/` é ato
  separado, e não foi executado aqui."* Foi executado, por decisão de Jeremias, e nos **três**
  runtimes — os dois locais e o global `~/.claude/skills/`, que a conferência anterior tinha
  esquecido de olhar. As duas variantes agora **coexistem** em cada um: `planejador-estrutura`
  com `sha256:3cc70650…` (20.075 B, igual à fonte) e `especialista-planejador` com
  `sha256:7f505408…` (16.605 B, igual à do Catálogo), nenhuma sobrescrevendo a outra.
  **O deploy exigiu alterar o contrato de implantação, e isso não é detalhe:** o
  `deploy-estrutura.ps1` nunca publicou este pacote — `$componentesPasta` tinha quatro entradas, e
  este item 4 descrevia desde sempre um ato que o instrumento não fazia. O script ainda afirmava
  que `ceo-maestro` era *"a única pasta com SKILL.md na raiz da estrutura"*, o que **já era falso
  quando foi escrito**: um comentário 90 linhas abaixo, no mesmo arquivo, já reconhecia este
  pacote. Afirmação sobre a árvore que ninguém executou contra a árvore.

## Colisão de nome — LEVANTADA em 2026-09-02, RESOLVIDA no mesmo dia por renome

> Levantada por dois juízes da rodada T121, independentemente, que a classificaram como risco
> **silencioso** — o pior tipo, porque não avisa quando dispara. Fica escrita aqui inteira, e não
> resumida a "resolvido": o defeito é mais instrutivo que o conserto.

**O que estava errado.** Três runtimes instalados carregavam o nome `especialista-planejador` —
`.claude/skills/`, `.agents/skills/` e o global `~/.claude/skills/` — e **os três eram a variante
do Catálogo** (`sha256:7f505408…`, 16.605 bytes, idênticos entre si). Esta variante não estava em
nenhum. Na medição comportamental, na única prova em que as duas se separam, a do Catálogo
**aceitou a rota inexistente** e devolveu ao `diretor-de-lentes`, perdendo os dois itens de
fronteira. Quem invocava o nome recebia a variante que falhou esse caso, sem aviso.

**Por que substituir teria sido pior, e isso foi medido antes de decidir.** O
`deploy-skills.ps1` do Catálogo **não** traz `especialista-planejador` em `$preservarSempre`, e o
Catálogo tem uma skill com esse nome: o próximo deploy de rotina desfaria a substituição **em
silêncio**. E a lente do Catálogo deixaria de chegar a runtime, quebrando o regime avulso. Trocar
um risco silencioso por outro não é conserto.

**A saída, decidida por Jeremias:** este pacote passou a se chamar **`planejador-estrutura`**. As
duas coexistem, `especialista-planejador` segue sendo a lente do Catálogo, e nenhum deploy futuro
desfaz nada — a colisão foi **eliminada**, não arbitrada.

**E a exposição só fechou com o deploy, no mesmo dia.** Renomear tira a ambiguidade do nome, mas
enquanto este pacote não estivesse em runtime nenhum, quem quisesse a variante da Estrutura
continuaria sem ter como pedi-la. Publicado nos três em 2026-09-02, com paridade SHA-256 conferida
pelo próprio deploy: `planejador-estrutura` = `sha256:3cc70650…` e `especialista-planejador` =
`sha256:7f505408…`, cada um igual à sua fonte.

**O renome quebrou exatamente uma coisa, e ela se denunciou sozinha.** O registro de expectativas
do `ceo-maestro/evals/coletar_saida_crua.py` é indexado por **nome de pasta**: renomear derrubou o
caso `todo pacote com validador tem expectativa declarada`, e o `ceo-maestro` caiu para 182/183. O
`departamento-negocios` deu `AMBIGUO` no selador — ele roda essa regressão como subprocesso, e a
trava do coletor **recusou adivinhar** em vez de atribuir o placar do vizinho. Consertada a chave,
a cadeia voltou a `2202/2202` sobre 16 pacotes, o **mesmo total** de 2026-09-01: o renome não somou
nem tirou caso nenhum.

**Segundo achado da mesma conferência, este ainda ABERTO:** a vitrine pública
`_github-publish-estrutura/` publica esta variante 23 bytes atrás da fonte (17.904 contra 17.927),
e ainda sob o nome antigo. Cópia pública que envelhece calada é a mesma classe de defeito que este
placar já cataloga. **dono:** Jeremias · **fecha quando:** a vitrine for republicada a partir da
fonte, com o nome novo.

**A evidência anterior não foi reescrita.** A rodada T121 julgou este pacote sob o nome antigo, e
a medição embute a `SKILL.md` daquele momento nos prompts dos sujeitos. Esses arquivos ficam como
estão — evidência não se atualiza, ganha sucessora.

## Fronteira que este placar não atravessa

Este documento mede **um pacote**. Ele não afirma total de cadeia como estado corrente, porque nenhum
pacote consegue rodar sozinho os validadores de todos os outros e saber o número do dia.


## Custodia reposta em 2026-08-26 (T114, resposta ao DJREP-T23-PLANEJADOR-20260825)

As duas alegacoes de instalacao acima ("suites dos 15 gerentes antes/depois" e "integridade do
ceo-maestro antes/depois") apontavam saida crua em `.tmp-especialista-planejador/...`, caminho que
deixou de existir. Enquanto essa prova historica nao foi reposta, elas figuraram como **NAO PROVADAS**.

A partir desta data, a alegacao vigente e de ESTADO CORRENTE, com custodia duravel e versionada
DENTRO do pacote:

- Arquivo: `evals/custodia-instalacao/VERIFICACAO-CORRENTE-2026-08-25.txt`
- sha256: `sha256:7725d8791d7e7b3a44d6e82a72962777791298edfce71061b19667069f89e99e`
- Conteudo: as 16 suites com validador proprio executadas com exit 0 (incluindo este pacote, 17/17)
  e o digest de arvore do `ceo-maestro` pela receita `digest_de_arvore`
  (`sha256:8485ad0bf803fd857bd75b7a70551e66cd81b8bcb13832feb0f0b16531a53599`), com receita de
  reproducao declarada no proprio arquivo.
- A prova do ato HISTORICO de instalacao (antes/depois de 2026-08-08) permanece NAO PROVADA e fica
  registrada como tal; o que esta provado hoje e que a arvore corrente fecha verde com o pacote nela.

> **SUPERADO EM 2026-09-01, e os dois defeitos ficam escritos em vez de apagados.** O bloco acima
> permanece na integra porque corrigir evidencia apagando-a e o que esta casa proibe; leia-o como
> registro do que foi publicado em 2026-08-26, nao como estado de agora.
>
> **Defeito 1 — o digest citado acima nao descreve o arquivo que ele diz descrever.** O bloco afirma
> que a custodia contem `sha256:8485ad0b...`; o arquivo contem `sha256:32b3a103...`. O sha256 do
> proprio arquivo (`7725d879...`) confere, entao o ponteiro e autentico e a **transcricao** e que
> diverge.
>
> **Defeito 2, e ele e maior — nenhum dos dois reproduz.** Medido em 2026-09-01 sobre quatro arvores:
> o commit que os publicou (`1e7879c0`) em LF da `9da1d10d...`, em CRLF da `7cdaea11...`; o worktree
> de hoje da `b6e4e702...`; o cofre de hoje da `6dacd426...`. Nenhuma bate com nenhum dos dois. O
> valor `8485ad0b` **nao aparece em nenhum outro ponto da arvore nem do historico** — nao e copia da
> fonte errada, e digest sem origem.
>
> **O que NAO afirmo:** que os numeros sejam falsos. A corrida de 2026-08-25 mediu uma **arvore de
> trabalho**, que podia ter arquivos nao commitados, e aquele instante nao e reconstruivel. Afirmo o
> que medi: **nao sao reproduziveis a partir de nenhum estado commitado.** Para efeito de evidencia
> da no mesmo, e o docstring da propria receita diz por que — *"numero que ninguem consegue
> recalcular nao e evidencia"*.

## Custodia republicada em 2026-09-01, PINADA A UMA REF

O defeito de 2026-08-26 nao foi de cuidado: foi de **ancoragem**. Digest de arvore sem ref nomeada
descreve um instante que ninguem consegue voltar a visitar. A partir daqui, o valor vem preso a um
commit, e a conferencia por terceiro e um `git checkout`.

- Arquivo: `evals/custodia-instalacao/VERIFICACAO-CORRENTE-2026-09-01.txt`
- sha256: `sha256:5986a9fc11e7632bd7a1ea3add17f37c5f8b329e3e3ae78ca64f4f03225e85ec`
- **ref medida:** `92151570` — master e origin identicos nesta data
- **digest de arvore do `ceo-maestro`** pela receita `_compartilhado/verificacoes_pacote.py::digest_de_arvore`,
  bytes crus, exclusao `__pycache__`, 18.768 arquivos:
  `sha256:48935c90c377547eb1e4bb805475ee1af3993a12074f9ba9bee3904f467dd94a`
- **Reproducao por terceiro:** `git checkout 92151570`, depois `digest_de_arvore` sobre
  `Estrutura Final de Skills/ceo-maestro`.
- **Contagem em 18 de 18 linhas.** O arquivo anterior trazia 16 marcas `[OK]` e apenas 13 linhas
  `Resultado:`; os tres mudos eram `departamento-inovacao-melhoria`, `departamento-qa-usabilidade` e
  `departamento-negocios` — os tres que imprimem `RESULTADO:` em maiusculo. O coletor da epoca so
  casava o formato minusculo, e sob o rodape *"TODAS AS SUITES COM EXIT 0: SIM"* uma suite viva e uma
  que executou zero caso ficavam indistinguiveis. A custodia nova e gerada por
  `_compartilhado/selar_contagem.py::extrair_contagem`, que aceita os dois formatos e **recusa
  atribuir** quando a saida embute o sumario de outro pacote.
- **ALEGACAO MENOR QUE A ANTERIOR, de proposito:** 16 de 18 suites com exit 0, nao 18 de 18. As duas
  que nao fecham sao o `ceo-maestro` e o `departamento-negocios`, e sao **um** defeito — a
  `NC-R4-04` mais o eco dela. Repetir *"todas com exit 0"* hoje seria falso.
- A prova do ato HISTORICO de instalacao (antes/depois de 2026-08-08) permanece **NAO PROVADA**,
  exatamente como o adendo de 2026-08-26 ja declarava. Republicar estado corrente nao repoe passado.
