# Parecer — painel externo, instância 2 · `departamento-juizes`

- **Juiz:** `painel-externo`, instância **2**. Não pertenço à estrutura do alvo.
- **Rodada:** `nucleo-de-comando` · **nível exigido:** `INTERNO`
- **Commit julgado:** `412769f31ccb0cb636f85c41f56cf9c6f612b3c1` (`412769f`)
- **Árvore do contrato:** `ee916c6`. Conferi com `git diff --stat ee916c6 412769f` sobre o pacote-alvo:
  **nenhuma diferença**. O objeto que li é byte a byte o objeto que o contrato selou.
- **Executei:** nada. Proibido pelo contrato. O número vem do executor.
- **Mínimo dos meus seis critérios: 5.**

| critério | nota |
|---|---:|
| `C01` contrato e fronteira | **7** |
| `C02` schema e envelope | **7** |
| `C03` trava com prova | **6** |
| `C04` evidência e rastreabilidade | **6** |
| `C05` uso pela cadeia | **5** |
| `C06` limites declarados | **7** |

## O `[FAIL]` descontado

A saída crua traz `153/154`, com um `[FAIL]`: *série global de ADR é única em toda a estrutura* —
número `020` duplicado em duas cópias de laboratório sob
`ceo-maestro/evals/producao-honesta-2026-08-04/origem-independente-R1/lab/mech/{A,B}/`. É defeito de
outra frente, não deste pacote. **Descontei**, e registro o efeito: sem o desconto haveria uma falha
executada em aberto, e nenhuma das minhas seis notas mudaria, porque nenhum achado meu depende dela.

---

## A pergunta de fundo: ele prova o que afirma?

**Em parte, e a parte que falta é a que o define.**

Este Departamento escreveu a norma mais dura desta casa sobre prova. O `ADR-016` diz que régua com
folga maior que o degrau produz `NAO_DISCRIMINADO`, não decisão. O `ADR-022` declara, antes de
decidir, que o critério novo *"baixa notas, ele não sobe nenhuma"*. A §7 do protocolo declara oito
riscos residuais com **teto honesto** por vetor, inclusive o R6, que admite que a condição
*"encarece a fabricação, não a impede"*. Isso é raro e é real.

E então o pacote gastou seu orçamento de prova no lugar errado.

As três travas do `ADR-016` — caminho de escrita exclusivo, custódia antes do despacho, ausência de
arquivo não é morte de executor — receberam **cinco funções em código e ~25 casos executados**. São
travas de **contabilidade de orquestração**: impedem colisão de arquivo e redespacho por
impaciência. São boas, e uma delas é exemplar (§ abaixo).

A **§2 do protocolo** — cegueira, higienização, varredura de instrução, isolamento, independência —
tem **zero trava em código, zero caso, zero campo de envelope**. `grep` por
`higieniz|fingerprint|varredura|anonymized` no validador retorna uma única linha, e é uma string de
fixture (`validate_workflow.py:245`). O `Concluído quando` da §2 exige registro, por agente, de path
anônimo, digest recomputado na cópia, teste de independência, itens removidos, varredura nas duas
frentes e fingerprint residual. O `panelItem` tem sete campos, nenhum deles; o `assignmentRecord`
tem sete, nenhum deles; **os dois são `additionalProperties: false`**. A evidência que o protocolo
exige não está apenas ausente: **é proibida pelo schema**.

**O protocolo exige cegueira e isolamento como instrução, não como mecanismo.** É a resposta direta
à pergunta que me foi feita.

E o caso mais afiado disso é a trava reflexiva — *"não julga a si próprio, não julga entrega de que
participou"* —, que é a razão pela qual **eu existo**. O `R5` declara o limite e acerta o teto:
*"sem registro de autoria emitido fora do pedido, o conflito omitido é indetectável"*. Mas a mesma
linha afirma que **"o formato é validável"**. Não é: o `judgmentRequest` do Diretor tem catorze
campos obrigatórios e **nenhum** carrega os produtores declarados do candidato. O teste de
independência que a §2, regra 7, torna obrigatório **não tem canal de entrada no envelope**. Um
limite cuja mitigação publicada não existe.

### E a régua dele, tem folga medida?

**Não.** O `ADR-016` mediu a folga da régua aplicada **aos outros** — faixa de até 3 pontos entre
instâncias, três de oito vereditos decididos por qual instância sobreviveu a uma colisão. O
`ADR-022`, em `A22-03`, declara que o instrumento separa em **55% dos casos** e chama isso de "o
risco real deste ADR". Nenhuma medição da variância da régua **sobre este pacote** existe. O
Departamento sabe que réguas têm folga, escreveu a norma que obriga a declará-la, e nunca mediu a
própria. Eu, sendo instância única, também não a produzo.

---

## Os seis critérios

### `C01` — Contrato e fronteira · **7**

As três perguntas afiadas do critério são respondidas com **mecanismo**, não com promessa:

**Nota e veredito são exclusivos dele — travado.** `scorecardLine.judge_id` referencia
`$defs/judgeId`, cujo `enum` contém **somente os três agentes**
(`schemas/departamento-juizes.schema.json:88` e `:1082`), e o validador confere esse enum **contra as
pastas reais de `agentes/`** (`evals/validate_workflow.py:1210`). A gerente não consegue aparecer
como pontuadora num scorecard válido por schema. Do lado de fora, `validate_inherited_authority`
(`:1241`) lê os schemas do Diretor e do CEO e exige os `const` que atribuem `JUDGE_REPORT` e
`DEPARTMENT_JUDGE_REPORT` aos Juízes e o pedido ao Diretor.

**Não conserta o que julga.** Proibido em SKILL, contrato e protocolo §5.6, e **estruturalmente
impossível**: não existe tipo de artefato de saída que carregue candidato corrigido ou patch.

**Os três agentes são folhas.** Cada um declara `Não aciona: ninguém`
(`agentes/agente-julgar-robustez-e-evidencia/SKILL.md:160`), `return_to: departamento-juizes` e
fronteira exclusiva; o schema rejeita ótica trocada e retorno fora da gerente, em casos executados.

**Sobram dois riscos.** O primeiro é o `R5` acima. O segundo: **a fonte normativa se contradiz sobre
quantos gates um veredito positivo exige.**

| onde | diz |
|---|---|
| `protocolo-de-julgamento.md:363` | §4.1 — *"**seis** condições, todas juntas"* — **e lista sete** |
| `protocolo-de-julgamento.md:378` | *"Com os **sete** gates íntegros"* |
| `CONTRATO-DE-COMPROMISSO.md:86` | *"as **seis** condições da §4.1"* |
| `SKILL.md:212` e `:269` | *"as **sete** condições"* |

O sétimo (`minimum_score_range`) veio do `ADR-016` e a contagem foi atualizada **pela metade**.
Efeito prático baixo — a lista está enumerada no ponto de uso —, mas é exatamente a *"coerência
interna entre seções"* que o agente de robustez deste time é mandado caçar nos outros.

### `C02` — Schema e envelope · **7**

Não é schema decorativo: `$defs` com `if/then/allOf` codificando as faixas do `ADR-014` e do
`ADR-016`, `additionalProperties: false` em toda parte, e um achado que merece nome — o `pending` do
`PANEL_RECORD` é um array com `contains: {pattern: "R6"}` e `minContains: 1`. **O R6 nomeado
incondicionalmente é obrigação de schema, não conselho.**

O ponto mais forte é a fronteira: o `PANEL_RECORD` interno é **derivado** em
`DEPARTMENT_JUDGE_REPORT` e `JUDGE_REPORT` e validado **contra os schemas dos consumidores**
(`validate_workflow.py:592`, `:1709`), incluindo as variantes forjadas — faixa que atravessa o corte
carimbada como aceite interno — que os dois consumidores rejeitam (`:2387`). E
`validate_adr016_agreement` extrai o enum de métodos e o enum de veredito **dos três schemas** e
exige que coincidam (`:1101`): conferência derivada do artefato, não de lista escrita à mão.

**Dois riscos.** (1) O registro interno não consegue carregar a evidência da §2 — ver a seção acima;
com `additionalProperties: false`, ela não é só ausente, é **inadmissível**. (2) Metade da
conferência de coerência é **presença de string** (`:1136`, `:1147`: `"antes de qualquer parecer
existir" in protocolo`, `token in skill`). A prova de que essa metade não aperta é a contradição
seis/sete gates, que atravessa **os dois** validadores de coerência sem uma linha vermelha.

### `C03` — Trava com prova · **6**

**O que existe é de alta qualidade.** Cinco travas em código de verdade — `trava_caminho_exclusivo`,
`trava_ausencia_nao_prova_morte`, `trava_custodia_antes_do_despacho`,
`trava_regra_declarada_antes_das_notas`, `trava_forma_do_painel` (`:750` em diante) —, cada uma com
caso positivo **e** negativo executados. A aritmética do veredito é **recalculada em código**
(`decide_verdict`), nunca lida de campo declarado. Morte por exceção não é o modo de falha: o import
do motor compartilhado tem **dois braços** e imprime `[FAIL] OVERLAY_APLICADO_PELA_METADE` em vez de
morrer por traceback (`:85`) — e o resumo do executor confirma `traceback: false`.

O caso da trava 1 é o melhor que li nesta base (`:1943`):

> *"a emissão duplicada aqui é byte a byte igual à primeira: todas as outras checagens da trava
> passam, e só a de exclusividade pode reprovar. Um fixture com caminho malformado ficaria verde sob
> a mutação — foi assim que a primeira versão deste caso passou pela razão errada, e a mutação
> pegou."*

**Três lacunas.**

1. **As travas constitutivas não existem.** Cegueira, higienização, varredura de instrução e
   independência: zero trava, zero caso. O orçamento de prova foi para contabilidade de orquestração.
2. **"Nada passa por presença de string" é violado pelo próprio conjunto de casos.**
   `validate_adr014_normative_consistency` (`:1042`) é integralmente `in texto`, e os itens 3 a 8 de
   `validate_adr016_agreement` também. São **dois dos 154 casos publicados**.
3. **A mutação é alegada e não registrada.** `adr-016:100` e o comentário `:737` afirmam que *"cada
   uma foi provada por mutação executada"*. Nenhum artefato do pacote registra a rodada: sem data,
   sem qual trava foi desligada, sem quais casos ficaram vermelhos. O próprio ADR diz, na linha
   seguinte, que *"trava declarada e não provada não conta"*.

O arnês também compara **só booleano** válido/inválido (`:2404`): nenhum caso negativo afirma **qual**
erro disparou. A disciplina do comentário da trava 1 foi aplicada a um caso, não generalizada.

### `C04` — Evidência e rastreabilidade · **6**

**"Ausência vira estado nomeado" é o eixo mais bem resolvido do pacote.** `AGUARDANDO` como estado
próprio; `JUDGE_CAPABILITY_GAP` com sete campos obrigatórios e a regra de que bloco sem
`discovery_evidence` ou sem `impact` **vale como inexistente** (`protocolo:203`); `n/a` só com motivo
verificável; `pending` obrigando R6 por schema; o `PLACAR` listando cinco não-provados como `SKIP`
com motivo.

**Digest reproduz.** `conferir_digest_das_regras` confere a fonte normativa contra o valor declarado
em `ORIGEM.md`, sobre um motor que já aprendeu a recusar o SHA órfão. `origem-migracao.md:7` fixa a
proveniência do legado por SHA-256 arquivo a arquivo e diz, sozinho, que *"a contagem é contexto de
escala, não identidade"*. E há um caso deixado **fora** da lista de booleanos de propósito, para que
a falha carregue valor declarado, valor recomputado e receita (`:1904`) — exatamente o que o C04
pede.

**Mas "todo número publicado vem com receita" falha em três pontos.**

1. **O `PLACAR` publica um número vencido como corrente.** Sob o título **"Medição ativa"**:
   `Validador determinístico do Departamento — 88/88 PASS` (`evals/PLACAR.md:12`). A execução
   publicada nesta rodada dá **153/154** (`saida-crua/departamento-juizes.stdout.txt:157`). São
   **+66 casos sem uma linha de explicação**, e o inventário do executor confirma
   `adendo_de_contagem: false` (`00-RESUMO.json:84`). Três parágrafos acima, o próprio `PLACAR:36`
   cita a regra da casa — *"número de vizinho carrega a data da medição, ou não entra"* — e a aplica
   ao número do vizinho, **não ao próprio**.
2. **Dezoito casos comportamentais publicam falha sem receita**: colapsam em `"condição
   comportamental falhou"` (`:1901`) — deficiência que o código reconhece por escrito na linha
   seguinte e corrige para **um** caso.
3. **A prova por mutação não tem receita nem raiz** em lugar nenhum do pacote.

### `C05` — Uso pela cadeia · **5**

**O que está provado é a fronteira de envelope, e está bem provado.**
`validate_inherited_authority` (`:1235`) quebra aqui se um vizinho mudar o contrato do outro lado; os
envelopes produzidos são validados **contra o schema do consumidor**, não contra o próprio; e
`validate_adr016_agreement` cobra do `judgmentRequest` do Diretor os campos `instances_per_lens` e
`aggregation_rule`.

**O que não está provado é o próprio enunciado do critério.** Quatro observações:

1. **Não é invocável.** O pacote **não está instalado como skill de runtime** — declarado pelo
   próprio `FORWARD-TEST.md:29`.
2. **Esta rodada não atravessou o pacote.** O contrato selado registra que quem *"executa os
   validadores, publica a saída crua, sela este contrato, **despacha os juízes** e agrega o
   resultado"* é o `ceo-maestro` (`00-CONTRATO.md:40`). Não houve `JUDGMENT_REQUEST` do Diretor, nem
   `CRITERIA_MATRIX`, nem `JUDGE_ASSIGNMENT`, nem `write_path`, nem `custody_copy`. **As três travas
   do `ADR-016` não rodaram no único julgamento real disponível para observar** — e eu sou uma das
   emissões que deveriam tê-las exercido. A regra de agregação, essa sim, foi declarada antes de
   existir parecer, honrando o espírito do ADR — por decisão do contrato, não por mecanismo do pacote.
3. **A cobertura comportamental do `ADR-016` é zero.** O forward é de 2026-07-26 e cobre 15 dos 20
   casos válidos do catálogo atual; os cinco casos `OPERACAO` acrescentados em 2026-07-29 nunca
   rodaram. E `grep -c "NAO_DISCRIMINADO|instances_per_lens|aggregation_rule|write_path|custody_copy|AGUARDANDO"`
   no `evals.json` retorna **0**. O quarto veredito da casa existe só em prova mecânica.
4. **A colisão de fronteira que o próprio forward diagnosticou continua viva.** O
   `FORWARD-TEST.md:98` escreveu *"correção devida"* em 2026-07-26; hoje a description do
   `diretor-de-lentes` ainda reivindica *"pular gerente, dispensar Juízes… usar nota fracionária"*
   (`diretor-de-lentes/SKILL.md:3`) — e a description **desta** skill repete o mesmo padrão que o
   forward nomeou como causa (`SKILL.md:3`). O pacote diagnosticou a doença e ficou com ela.

### `C06` — Limites declarados · **7**

**É o eixo mais forte.** A §7 do protocolo é o **único** lugar onde os limites são declarados — o
resto do documento aponta para lá — e traz oito vetores com consequência, mitigação e **teto**
honesto, inclusive o R6 (*"encarece a fabricação, não a impede"*). O `ADR-016` declara três riscos
próprios, incluindo uma **hipótese direcional não testada** que fica registrada como frente seguinte
em vez de virar conclusão (`:164`), e uma consequência retroativa que **nomeia** a lista de
julgamentos suspeitos em vez de apagá-la. O `ADR-022:80` é o melhor formato da casa: quatro limites
em tabela **com dono e com condição de fechamento verificável** — e um parágrafo registrando que o
preço foi medido e informado a Jeremias **antes** da decisão (`:56`).

**Dois riscos menores.** (1) Dos treze limites declarados, só os quatro do `ADR-022` têm dono e
condição; os oito da §7 declaram **teto** — mais honesto que uma condição falsa, mas não é o que o
critério pede —, e dois limites operacionais (auditoria independente nunca executada,
`PLACAR:137`; a *"correção devida"* da colisão, `FORWARD-TEST:98`) não têm dono, não têm data e
continuam abertos desde 2026-07-26. (2) A mitigação do `R5` afirma o que o schema desmente.

---

## O que declaro contra mim

**A teia pesou, e num ponto específico.** Fui despachado pelo `ceo-maestro`, que é julgado nesta
mesma rodada, e meu alvo é o departamento que normalmente julgaria o `ceo-maestro`. Percebi em mim a
tentação **oposta** à que o contrato antecipa — não a de poupar quem me despachou, mas a de **provar
independência sendo duro com o alvo dele**. Reli o `C05` duas vezes por isso. Mantive **5**, e
registro que a minha nota mais baixa é justamente a que mais depende de uma observação **sobre a
rodada em que estou dentro**, escrita por quem me despachou.

**Contaminação declarada.** Não abri nenhum contexto proibido e não fiz busca larga. Topei com um
ponteiro em `PLACAR.md:32` para `../../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md` — que o
contrato nomeia como portador da nota de 29/jul **deste** pacote — e **parei na linha, sem seguir**.
Mas o `00-CONTRATO.md`, que fui mandado ler **primeiro**, traz nas linhas 10–15 a tabela das quatro
notas vigentes, **inclusive o `2` deste pacote**. Eu sabia a nota anterior antes de abrir o alvo.
Não a usei como âncora consciente, e minhas seis notas estão acima dela — mas não posso afirmar que
não me ancorou.

**Não sou tão externo quanto o rótulo.** Julguei o `departamento-juizes` com o vocabulário que ele
inventou: trava com prova, mutação, ausência como estado nomeado, régua com folga maior que o
degrau. Fui instruído a ler o protocolo dele como objeto e não herdá-lo, e não separei as duas
coisas por completo. Um painel realmente externo traria critérios de fora; eu apliquei os `C01`–`C06`
que este Departamento ajudou a formatar.

**Não executei nada.** Toda a minha avaliação de `C03` é sobre o **código** das travas e sobre o
**registro** da mutação — nunca sobre o comportamento delas. Se as cinco travas ficarem verdes quando
desligadas, meu **6** está generoso; se a mutação foi de fato executada e só não foi registrada, meu
**6** está duro pelo motivo certo e na dose errada. Não sei qual dos dois.

**Meu `C06` = 7 é o ponto mais discutível.** O critério pede *"dono e condição de fechamento
verificável"*, e oito dos treze limites declaram **teto**. Tratei teto como cumprimento porque
*"isto não fecha no runtime atual"* é uma afirmação verificável de não-fechamento. Um juiz igualmente
honesto leria a mesma evidência como **6**. Não muda o meu mínimo, que já é 5.

**Sou instância única de uma ótica que não existia antes desta rodada** — sem protocolo próprio, sem
rubrica calibrada, sem par com quem divergir dentro da minha própria ótica. Pela regra da própria
casa, nota de instância única perto do corte não decide. **Meu mínimo, 5, está a um ponto do corte 7
por baixo — e a dois do 7.** Se a instância 1 divergir para 7 ou mais em `C05`, a faixa atravessa o
corte, e o que o `ADR-016` manda nesse caso não é escolher a minha nota: é `NAO_DISCRIMINADO`.

**Não li tudo.** Li um agente inteiro e a estrutura dos outros dois; não abri os três
`agents/openai.yaml` nem dois dos três contratos de agente na íntegra. Divergência de fronteira que
só apareça nesses arquivos passou por mim.
