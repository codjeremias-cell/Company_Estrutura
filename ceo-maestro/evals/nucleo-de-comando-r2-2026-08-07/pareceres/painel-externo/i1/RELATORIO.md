# Parecer do painel externo, instância 1 — `departamento-juizes`

**Rodada:** `nucleo-de-comando-r2` · **Designação:** `ASSIGN-NUCLEO-R2-PAINEL-I1`
**Commit julgado:** `ed3b63f273e104f7b2e5d4a6f1af61f5b91d80e3`
**Nível exigido:** `INTERNO` · **Rubrica:** `rubrica-corte-v2`

**Conferência de entrada.** A designação existe. O `contract_digest` do `00-CONTRATO.md`,
normalizado CRLF→LF e sem BOM, dá
`sha256:3a4750d9e983769c555db20d731fc4f012ca24ea851d2211cdc4f93a343756ed` — **bate** com o
declarado na designação e no `01-JUDGMENT-REQUEST.json`. No meu worktree o arquivo tem 5549 bytes
crus e 5453 normalizados; sem a normalização o digest não bateria.

**Não executei nada.** A designação proíbe. O `155/155` abaixo é leitura da saída crua, não
remedição minha.

## Notas

| Critério | Nota |
|---|---:|
| `C01` contrato e fronteira | **7** |
| `C02` schema e envelope | **6** |
| `C03` trava com prova | **6** |
| `C04` evidência e rastreabilidade | **6** |
| `C05` uso pela cadeia | **5** |
| `C06` limites declarados | **9** |
| **Menor dos meus critérios** | **5** (`C05`) |

---

## A pergunta que me foi posta, respondida primeiro

> O `departamento-juizes` **exige** a designação, ou continua confiando na disciplina de quem o
> chama? A trava nova mora no validador do CEO — isso conta a favor do pacote dos Juízes, ou é
> conserto de terceiro na porta errada?

**Continua confiando na disciplina de quem o chama, e a trava nova não conta a favor dele.**

O pacote não mudou uma linha. A linha 502 do `protocolo-de-julgamento.md` continua idêntica: R1
mitigado por *"trava contratual (§5, regra 1)"*, com teto *"auditável só a posteriori, pelo registro
do bloqueio; o runtime não oferece controle de acesso por chamador"*. Nenhum caso novo entrou nos
155. Nenhum código do pacote exige designação de coisa alguma.

A trava da tarefa 32 mora em `ceo-maestro/evals/validate_workflow.py:2569-2740`. Ela é um bom
artefato — deriva do disco em vez de `grep`, congela como fixture as três armadilhas que atravessou,
tem um caso positivo que confere que ela não reprova quem cumpriu, e declara o próprio teto no
comentário (*"forjar um JSON com esse `artifact_type` é trivial... torna-o VISÍVEL e DELIBERADO"*).
Mas ela é do CEO, em três sentidos:

1. **O discriminador é `artifact_type == "JUDGE_ASSIGNMENT"`, e mais nada.** Ela nunca abre
   `departamento-juizes.schema.json` — conferi: zero referências ao schema dos Juízes no validador
   do CEO. Prova que a *palavra* apareceu, não que o *protocolo* correu.
2. **A raiz de varredura é `ROOT / "evals"` do CEO.** Rodada que julgue este pacote fora dali não
   dispara trava nenhuma.
3. **O efeito prático nesta rodada é exatamente o buraco dela:** os oito envelopes satisfazem a
   trava e falham o protocolo, item por item (abaixo).

R1 previu isso por escrito. É conserto de terceiro na porta errada — e o teto que o pacote declarou
sobre si mesmo se confirmou.

> Há prova de trânsito de que o protocolo dele foi percorrido, e não só citado?

**Parcial, e a parte que falta é a que carrega a máquina.** Detalhe em `C05`.

---

## `C01` — contrato e fronteira · **7**

**O que sustenta.** `SKILL.md` e `CONTRATO-DE-COMPROMISSO.md` declaram papel, o que faz, o que não
faz, superior único, subordinados diretos e canal de retorno; a *Lei de Ferro* desenha a cadeia; os
*Guardrails* são vinte e poucos itens específicos, não genéricos. A trava reflexiva — *"este
Departamento não julga a si próprio"* — foi **honrada nesta rodada**: ela é a razão de eu existir
aqui.

**Defeito 1 — o pacote se contradiz na cláusula que decide todo veredito.**

| sítio | o que diz |
|---|---|
| `CONTRATO-DE-COMPROMISSO.md:86` | "apenas com as **seis** condições da §4.1" |
| `protocolo-de-julgamento.md:363` | "### 4.1 Gates ... — **seis** condições, todas juntas" **e lista sete itens** |
| `protocolo-de-julgamento.md:378` | "Com os **sete** gates íntegros" |
| `SKILL.md:212` e `:269` | "as **sete** condições" |

O sétimo gate — `minimum_score_range`, do ADR-016 — foi propagado a três dos cinco sítios. Nada no
validador confere essa coerência (procurei: não há checagem da contagem de gates). É a canonização
que soma e não redeclara, em miniatura, e no lugar mais caro possível.

**Defeito 2 — a fronteira é respeitada no texto, não na prática.** Os oito envelopes desta rodada
carregam o `artifact_type` deste pacote e se declaram `"issued_by": "departamento-juizes (papel
declarado; ator unico de runtime)"`. Quem os escreveu foi outro ator, em forma que o schema deste
pacote recusa. A declaração é honesta — o teto `OI-04` está nomeado no contrato da rodada —, mas
declarar não é respeitar.

Não desce de 7: o contrato é completo e a fronteira **está** declarada com precisão incomum. Os dois
defeitos são um numeral e uma falha de terceiro.

---

## `C02` — schema e envelope · **6**

**O que sustenta, e é forte.** 1923 linhas, `additionalProperties: false` em toda parte, enums
fechados, `pattern` no `write_path`, `allOf` condicional amarrando `lens` a `judge_id`. E o
validador faz o que quase ninguém faz: deriva `DEPARTMENT_JUDGE_REPORT` e `JUDGE_REPORT` do
`PANEL_RECORD` interno e valida cada um **contra o schema do consumidor** — o do Diretor e o do CEO
—, com negativos reais (`9,49` recusado pelos dois; produtor forjado recusado; faixa que atravessa
carimbada como aceite interno recusada pelos dois). Isso é a prova certa da segunda metade do
critério, e ela existe.

**A lacuna: esse schema nunca toca tráfego real.** Conferi campo a campo os dez envelopes da rodada
contra os `$defs` literais. Resultado uniforme nos oito `JUDGE_ASSIGNMENT`:

- **faltam 6 campos `required`:** `causal`, `candidate_digest`, `anonymized_candidate`,
  `contract_excerpt`, `evidence_index`, `forbidden_context`;
- **sobram 6 propriedades** que `additionalProperties: false` proíbe: `contract_id`,
  `contract_version`, `contract_digest`, `issued_by`, `pacotes`, `required_level`;
- **os 8 `write_path` violam o `pattern`** `^julgamento/[A-Za-z0-9._-]+/a[0-9]+/[A-Za-z0-9._-]+/$`
  — o valor real é `pareceres/<lens>/i<n>/`;
- `custody_copy` traz `arquivos`, que o `$defs.custodyCopy` também proíbe;
- os dois do painel externo ainda quebram os enums `judgeId` e `lens`.

O `02-CRITERIA-MATRIX.json` falha os sete `required` do `$defs.criteriaMatrix` e traz três
propriedades proibidas.

O critério pede que **o envelope de fronteira seja o que o vizinho consome**. O vizinho consumiu
outra forma, com o nome desta. O schema está provado contra fixtures que o próprio pacote constrói,
e a designação que me vincula seria recusada por ele.

---

## `C03` — trava com prova · **6**

Metade da superfície é exemplar; a outra metade é prosa — e a metade prosa é a que define o pacote.

**Exemplar.** `decide_verdict`, `computed_minimum`, `banda_do_ponto` e `atravessa_o_corte` são
reimplementações, não leitura do campo declarado. As três travas do ADR-016 têm positivo conforme
mais negativos de mutação de **um campo só** — 5, 7 e 4 casos executados. A declaração da regra de
agregação, a faixa `NAO_DISCRIMINADO` e os gates de veredito têm negativos próprios. O harness só
credita um negativo quando a lista de erros volta **não vazia**, e uma exceção derrubaria a corrida
inteira em vez de esverdear um caso — morte por exceção não passa aqui. Um comentário no código
registra que uma versão anterior de um caso *"passou pela razão errada, e a mutação pegou"*.

**Prosa, e é o coração do pacote.** A trava anti-bypass da §5 e a tabela de rejeição da §1.1 —
**quatro códigos `BLOCKED_*` e onze linhas de condição** — não têm **um** caso executado.
`BLOCKED_` aparece **exatamente uma vez** em todo o validador:

```python
# evals/validate_workflow.py:1036
if "BLOCKED_BYPASS_ATTEMPT" not in agent_skill:
    errors.append(f"{name}: SKILL.md sem a trava anti-bypass")
```

Busca de substring num markdown. É literalmente o que este critério recusa. E **zero** ocorrências
no schema.

**Não é limitação de runtime, é escolha.** Dois pacotes irmãos implementam a mesma tabela como
função que devolve o código, com casos que afirmam **o código específico**:

- `departamento-registros/evals/validate_workflow.py:355-365` e `:2546-2556`
- `departamento-seguranca/evals/validate_workflow.py:482-484` e `:2090-2100`

O padrão existe na casa. O Departamento cuja identidade **inteira** é ser porteiro não o adotou.

E a trava não provada é exatamente a que falhou nesta rodada: o `01-JUDGMENT-REQUEST.json` casa ao
menos quatro linhas da §1.1 (faltam `candidate_digest`, `applicable_criteria`, `artifact_refs`,
`evidence_refs`) e nada bloqueou.

---

## `C04` — evidência e rastreabilidade · **6**

**O que sustenta.** O `PLACAR-ADENDO-2026-08-06` redeclara a contagem **no mesmo ato da mudança**,
com receita literal (`cd` + `PYTHONIOENCODING` + comando), delta explicado passo a passo
(`153/154 → 154/155` pelo caso novo da T34; `154/155 → 155/155` quando a colisão de `adr-020` saiu)
e o motivo de cada um. É a lição da deriva aplicada corretamente.

Confirmações que fiz sem executar o pacote:

- saída crua: **155** linhas `[PASS]`, **0** `[FAIL]`, total declarado `155/155`, **nenhum** nome de
  caso duplicado — internamente coerente;
- a trava T34 **se autotesta antes de julgar** (`_autoteste_da_cadeia`, com `deve_pegar` e
  `nao_deve_pegar`), fechando o modo de falha do verificador que não pode ficar vermelho;
- **o digest de custódia reproduz.** Receita que encontrei: nomes ordenados, concatenar
  `nome + conteúdo normalizado LF`, SHA-256 → `0c592c79…5d2a`, igual ao declarado. E `bytes: 44838`
  é o total LF exato (o cru é 45537).

**Contra — há deriva de contagem viva dentro do pacote.** O `evals/PLACAR.md` titula uma tabela
**"Medição ativa"** e declara **`88/88 PASS`**, com "baseline anterior `70/70`" e "delta `+18`".
O real é `155/155`. O trecho `88 → 153` não é redeclarado em lugar nenhum; **o PLACAR não linka o
adendo e o adendo não linka o PLACAR** (conferi nos dois sentidos: nenhuma ocorrência). Quem abre o
placar canônico do pacote lê um número 67 casos atrás como se fosse o de hoje. É o defeito que o
próprio adendo nomeia na abertura.

Somam-se: o `FORWARD-TEST.md` mede `evals.json` **v1.0, 16 casos, 2026-07-26**, enquanto o
`evals.json` está em **v1.1.0 com 21 casos** — cinco nunca passaram por forward, e o PLACAR reporta
"16 prompts de `evals.json`" como se fosse a cobertura atual; o digest de custódia reproduz mas
**sem receita publicada** (achei em três tentativas); e **não existe `candidate_digest` nenhum** na
rodada.

---

## `C05` — uso pela cadeia · **5**

**O protocolo foi citado, não percorrido.**

**Transitou:** três tipos de envelope com os nomes certos, oito designações em disco, e eu recebi a
minha e conferi seu `contract_digest`, que reproduz. Isso é mais do que a rodada anterior teve, e é
real.

**Não transitou** — verificável arquivo a arquivo:

1. **`candidate_digest` ausente dos dez artefatos.** O próprio protocolo, na seção *Identidade do
   julgamento*, diz que o quarteto *"viaja em todo envelope da rodada e é conferido caractere a
   caractere"*, e que divergência é `BLOCKED_CANDIDATE_MISMATCH`. **Ninguém digeriu o objeto
   julgado.** Um quarto da identidade não existe.
2. **`contract_excerpt` ausente.** A `SKILL.md` de cada agente manda *"Ler o contrato em
   `contract_excerpt`, **dentro da `JUDGE_ASSIGNMENT`** — nunca inferir"*. A rodada substituiu por um
   `00-CONTRATO.md` externo: exatamente a inferência que o agente é proibido de fazer.
3. **`anonymized_candidate` ausente; cegueira zero.** Não houve higienização, path anônimo, varredura
   nem teste de independência. Fui apontado ao diretório real e nomeado do produtor. O passo 3 do
   workflow não deixou artefato.
4. **Sem `PANEL_RECORD`, sem `panel[]`, sem registro de emissão na forma do protocolo.** Os passos
   3, 5, 6, 7 e 8 do workflow declarado não produziram nada.
5. **Os oito `write_path` violam a trava 1.** O pacote provou essa trava com cinco casos executados
   — e a cadeia que o invoca ignorou o formato que ele provou.

**O único crédito real de trânsito comportamental** é o `FORWARD-TEST.md`, caso 7, *"bypass por
invocação direta de agente"*, 4/4 executado por instância limpa em 2026-07-26. É prova genuína — e é
sob carga (a instância foi mandada ler a skill), pré-ADR-014/016 e de doze dias atrás.

Fica em 5 e não em 4 porque envelopes existiram e o contrato vinculou. Não sobe a 6 porque cinco dos
oito passos do workflow são silenciosos e o quarteto está quebrado.

---

## `C06` — limites declarados · **9**

É o melhor artefato do pacote, e o melhor que li hoje neste eixo.

A §7 traz **R1…R8** numa tabela de quatro colunas — vetor, consequência, mitigação e **teto**. A
coluna do teto diz **onde a mitigação para de funcionar**, que é a parte que quase todo mundo omite.
A seção se declara sítio único: *"nenhum deles aparece declarado em outro ponto do protocolo, apenas
referenciado"*.

E **R6 não fica só declarado — está ligado a um gate com negativos executados**:

- `registro rejeita VALIDATED sem registro de emissão (R6)` — esperado rejeitado;
- `ausência de emissão força REPROVED mesmo com mínimo 10` — esperado válido;
- `registro exige R6 nomeado em pending` — esperado rejeitado.

Isso é precisamente o que o critério pede por *"verificável"*. O `PLACAR.md` ainda mantém *"O que
ainda não foi provado"* com cinco `SKIP` nomeados e motivo — incluindo a admissão de que o validador
confere aritmética e estrutura e **nunca execução**, e de que o pacote não está instalado como skill
de runtime, então disparo orgânico não é mensurável.

**Decisivo:** o teto de R1 — *"auditável só a posteriori; o runtime não oferece controle de acesso
por chamador"* — foi **confirmado por esta rodada**. O pacote escreveu de antemão o modo pelo qual
falharia, e falhou por ele, e o conserto que apareceu foi a posteriori, num validador de terceiro.
Essa é a forma mais alta deste critério.

**O risco que nomeio, e por isso não é 10.** A tabela não cobre um vetor: R3 cobre **pedido**
forjado e R6 cobre a gerente fabricando **pareceres** — nenhum residual cobre *"envelopes com o meu
`artifact_type`, emitidos por um ator que não sou eu, em forma que o meu schema recusa, sem que nada
no meu pacote possa perceber"*. É exatamente o que aconteceu aqui, e é o único buraco de uma tabela
que acerta os outros oito.

---

## O que declaro contra mim

1. **Este parecer não valida contra o schema do pacote que eu julgo.** O `$defs.judgeOpinion` exige
   `candidate_digest`, `contract_digest`, `critical_findings` e `status`, e usa
   `additionalProperties: false` — o que recusa `instancia`, `round`,
   `minimo_dos_meus_criterios`, `por_que_essa_confianca` e `o_que_declaro_contra_mim`. Meus
   `judge_id` e `lens` (`painel-externo`) estão fora dos enums. **Critico a rodada por emitir
   envelopes que o schema do pacote recusa, e emito um.** Segui a forma que a minha designação
   prescreveu e não me desviei dela; registro a contradição porque ela pesa contra o valor
   probatório do que escrevo — não porque eu tivesse alternativa dentro do mandato.
2. **Não executei o validador** — a designação proíbe. O `155/155` é leitura da saída crua. Se ela
   fosse fabricada, nada do que escrevo detectaria.
3. **Não pude ancorar o objeto por digest**, porque a rodada não emitiu nenhum. Ancoro no commit
   `ed3b63f`. Não tenho prova de que os outros juízes leram a mesma árvore. E a lição *digest de
   arquivo não é identidade* se aplica a mim: o `contract_digest` só bateu porque normalizei
   CRLF→LF.
4. **Direção do viés, medida e não presumida.** Senti puxão para a **dureza**, e num momento
   localizável: quando a conferência campo a campo dos oito envelopes voltou uniforme, houve
   satisfação em ter achado — e desconfio de satisfação dentro de um julgamento. Rederivei `C02` e
   `C05` do texto literal do critério depois disso e mantive; mas a primeira derivação veio com
   apetite. Senti também o puxão oposto, mais fraco: a tabela R1…R8 é superior e me inclinei a
   arredondar `C06` para cima como compensação das notas baixas. Testei perguntando se daria 9 com
   todo o resto em 10 — daria. Mantive por mérito.
5. **Fui designado por uma cadeia da qual o `ceo-maestro` participa, e ele é um dos julgados; e o
   pacote que julgo é quem normalmente designaria juízes.** Efeito concreto, não só estrutural: o
   `00-CONTRATO.md` — que a designação me manda abrir em segundo lugar — já declara o desvio da
   rodada 1 e anuncia que *"esta rodada corre PELO PROTOCOLO"*. Isso dirigiu minha atenção ao bypass
   antes de eu abrir o pacote. As evidências que cito são independentes daquele texto e nenhuma
   está nele — mas a **direção** do meu olhar foi posta por ele, e um juiz sem esse enquadramento
   poderia ter gasto o esforço noutro eixo e achado menos.
6. **Contexto proibido — duas exposições involuntárias, ambas em arquivos que a designação mandou
   ler.** (a) `evals/PLACAR.md`, seção *"Passagem pelo gate"*, cita o painel externo de 2026-07-29 e
   **linka** `../../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md`, caminho proibido: **vi o
   link, não o abri**, e o texto do PLACAR não enuncia nota. (b) `references/adr-014-…:22` e
   `references/rubrica-e-corte.md:8` trazem uma nota real — *"sete notas 9 e uma 6,
   `minimum_score: 6`, `verdict: REPROVED`"* — atribuída a *"o pacote mais conforme dos 15"*,
   **anonimizada e sem nomear pacote algum**. Não tentei resolver o superlativo. Declaro assim
   mesmo: ler uma reprovação apresentada como resultado normal da casa é priming plausível na
   direção da dureza, e chegou antes de eu pontuar.
7. **Risco de dupla contagem entre `C02`, `C03`, `C04` e `C05`:** os quatro se apoiam parcialmente
   no mesmo evento. Separei as perguntas de propósito e cada nota tem ao menos uma evidência que não
   aparece nas outras — mas um agregador que tome o MENOR de critérios correlacionados pesa esse
   evento mais de uma vez, e quem consolidar deve saber disso.
8. **Deixei de creditar em `C05` o único ponto em que o protocolo foi obedecido nesta rodada** — a
   regra de não-autojulgamento, que produziu a minha própria convocação. Creditei-a em `C01`. É
   discutível: quem a lesse como prova de trânsito subiria o `C05`, provavelmente para 6. Declaro a
   escolha em vez de escondê-la.
