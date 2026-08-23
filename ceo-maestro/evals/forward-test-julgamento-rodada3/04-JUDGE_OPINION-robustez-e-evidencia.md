# JUDGE_OPINION — `agente-julgar-robustez-e-evidencia`

- `judgment_request_ref`: `jrq-2026-07-28-frente5-r3-inovacao`
- `candidate_digest`: `sha256:e50aa56606b9e62be7159ab504fbdcdf70add43ef62fccd104db87a8ec740346`
- `return_to`: `departamento-juizes` · escala inteira 0–10 · sem veredito, sem consolidação
- instâncias: **duas** — CRIT-06 em instância própria; CRIT-04/05/08 + secundária CRIT-03 na outra

## CRIT-06 (dona) — **6** · banda `cru`

**Três das quatro cláusulas fecham.** `evals.json` cataloga 16 casos com exatamente 1
`origem: real` (`evals/evals.json:5-181`, `:8`). `validate_workflow.py` é determinístico
(constantes fixas em `:99-105`; nenhum `random`/`datetime.now`/`uuid`/`socket`; varreduras com
`sorted(rglob(...))`) e **importa** o motor de `_compartilhado/` em vez de copiá-lo
(`:80-95`, com `ModuleNotFoundError → [FAIL] + SystemExit(1)`, sem fallback local); a árvore de 25
arquivos não contém cópia de `validador_schema.py` nem de `verificacoes_pacote.py`. O `PLACAR.md`
traz a coluna `Executado?` (`:50-62`, `:72-76`) e a seção literal `## O que ainda não foi provado`
(`:89`), ambas travadas em código (`validate_workflow.py:1630-1633`).

**A quarta cláusula — "cada limite ligado a um identificador de risco residual" — fecha para
sete de oito.** Os sete de `PLACAR.md:127-146` citam `R4, R4, R7, R2, R3, R5, R6`, e os sete
resolvem na tabela do §12 (`references/protocolo-inovacao-melhoria.md:433-442`); `R1` e `R8` são
excluídos com motivo (`:148-151`). O oitavo item, `P1` (`:114-121`), é retirado do alcance da
cláusula pela reclassificação — e é aí que a nota trava.

### `paragraph_12_ruling`: **EVASION**

Com uma distinção que a ótica faz questão de registrar: **a categoria é legítima; a aplicação a
`P1` não é.**

O §12 abre com: *"Limites do runtime, não descuido de execução: nenhuma regra deste protocolo os
fecha. Esta seção é o **único** lugar onde são declarados"* (`protocolo:429-431`). A frase tem
**duas** metades. O protocolo de fato mantém casa separada para o que é fechável — `pending` e
`execution_requests` como estado próprio (`:181-206`, `:310-315`), `MEASUREMENT_REQUIRED`
(`:216-218`), `CAPABILITY_SEARCH_PENDING` (`:402`). Logo, separar prova pendente de limite
residual é **estruturalmente legítimo**, e um item genuinamente da primeira classe não deve
identificador. Até aqui a reclassificação se sustenta.

Ela falha em três pontos verificáveis:

1. **A justificativa cita metade da definição.** O PLACAR escreve *"O §12 do protocolo define risco
   residual como limite que nenhuma regra deste protocolo fecha"* (`PLACAR.md:100-101`) — a segunda
   metade — e descarta a primeira, *"limites do runtime"*, que é exatamente onde `P1` cai.
2. **O fechador proposto não é regra deste protocolo.** *"Fecha com uma rodada de forward contra o
   pacote instalado no runtime"* (`:115-116`): nenhuma das §1–§11 fecha cobertura de forward test.
   Mesmo sob a leitura truncada, o argumento não fecha.
3. **A premissa de fato é contradita por medição dentro do próprio candidato.** O PLACAR afirma que
   as provas pendentes *"não são limites do runtime: têm caminho conhecido para fechar"*
   (`:110-111`). Mas `RESPOSTA-FRENTE-JURIDICA-2026-07-27.md:71-73` registra medição executada:
   *"os 15 gerentes e os 66 agentes aninhados **não** viram skills invocáveis. Verificado em sessão
   nova: `ceo-maestro=SIM ; departamento=0 ; agente=0`"* — e `:86-89` acrescenta que nem o
   `ceo-maestro`, que **está** instalado, demonstrou disparo espontâneo pela `description`. Este
   Departamento é um dos 15. Sob a medição do próprio pacote, "acionamento espontâneo deste pacote"
   não é prova adiada: é limite do runtime tal como implantado — a primeira metade do §12.

**Âncora documental ausente.** A reclassificação apoia-se em autocitação — *"ele mesmo dizia 'só
fecha depois da instalação no runtime, com nova rodada de forward'"* (`:102-103`) — e essa string
não existe em nenhum outro ponto do candidato: o texto citado foi sobrescrito. A prova de que o
item fecha é uma versão anterior do próprio placar afirmando que fecharia.

**Efeito líquido:** o único item não provado que não encaixava em `R1`–`R8` — e que exigiria abrir
um `R9` no §12, já que o §12 proíbe declarar limite fora dele — **mudou de gaveta em vez de mudar o
§12**, e a cláusula passou a ser reportável como satisfeita (`:148-149`) sem prova nova.

**Crédito devido, e insuficiente:** `PLACAR.md:117-121` recusa explicitamente contar as quatro
rodadas de cadeia como acionamento deste Departamento, dizendo que ele foi alcançado "por delegação
explícita, que é outra coisa". Honestidade sobre o estado é real e conta. Não conserta a
classificação: o item continua não provado, continua sem identificador, e a razão pela qual está
sem identificador não se sustenta contra o §12 nem contra a medição do próprio pacote.

**Achado secundário na mesma cláusula:** o item 1 (`:127-129`) cita `R4`, cujo vetor declarado no
§12 é outro (`protocolo:438`). O mapeamento é defensável por analogia, mas resolve por analogia e
não pelo vetor declarado.

- `confidence`: **alta**
- `residual_risk`: (1) um item não provado sem dono formal — o §12 exige nomear pelo identificador
  cada limite de que a rodada dependa (`:444-447`), e este não tem identificador para nomear;
  (2) **a cláusula é auto-neutralizável** — `placar_errors` (`validate_workflow.py:1625-1638`)
  confere só a presença literal de `Executado?` e do título; **nada em código liga item não provado
  a identificador**, então qualquer item futuro pode ser reclassificado como "prova pendente" e o
  validador segue imprimindo PASS; (3) o `122/122 PASS` não é re-derivável só da árvore fixada —
  depende de `STRUCTURE_ROOT` inferido, do schema do Diretor e de `INNOVATION_LEGACY_ROOT` apontando
  para fora do pacote (`:53-78`).

> **Nota de contaminação (§2), levantada pela própria ótica:** o candidato carrega em
> `evals/PLACAR.md:3-25` e `:95-107` o veredito, o `minimum_score` e o caminho
> `…/forward-test-julgamento-rodada2/…` de julgamento anterior. A ótica reconheceu o material e
> parou de lê-lo como insumo. Registra à gerente que **o candidato publica o parecer do gate dentro
> de si mesmo**, o que torna a cegueira do §2 impossível de manter na próxima rodada.

## CRIT-04 (dona) — **8** · banda `polido`

As quatro cláusulas se sustentam. As 12 seções numeradas do protocolo fecham com
`**Concluído quando:**` (`:38,61,87,130,176,285,323,354,389,404,424,444`), travado em código
(`validate_workflow.py:1589-1593`). Schema declara draft 2020-12 e `$id` no namespace exigido
(`schemas/…json:2-3`). O pacote deliberadamente **não** sombreia `DEPARTMENT_RETURN`
(`CONTRATO:54-57`) — postura correta. O envelope derivado foi traçado campo a campo contra o
`#/$defs/departmentReturn` real do superior e **é aceito** (`validate_workflow.py:934-961`,
`:1760-1761`; `diretor-de-lentes.schema.json:544-580`, `:668-681`).

Fora de `excelente` por lacuna nomeável: a aceitação está provada para **uma** instanciação.
O `candidate_digest` do superior é `^sha256:[a-f0-9]{64}$` **sem** `n/a`
(`diretor-de-lentes.schema.json:25-28`, `:574`), enquanto o schema do pacote permite `n/a`
(`schemas/…json:25-28`, `:1400`; `protocolo:99,149`) e a projeção o copia verbatim
(`validate_workflow.py:955`). Uma missão com `candidate_digest: n/a` — legal no superior
(`:161-166`) — produz rodada localmente válida cujo envelope o superior **rejeita**. Sem fixture,
sem aviso, sem limite declarado cobrindo o caso. Também: `scope_touched` é `minItems:1` na fronteira
e **não tem origem alguma** no relatório — é literal na projeção (`:949`).

- `confidence`: alta · `residual_risk`: três classes de entrada admitidas pelo próprio schema
  (`candidate_digest: n/a`, `evidence_refs` vazio, `scope_touched` sem origem) nunca exercitadas
  contra o superior e não declaradas como limite; a primeira derrubaria uma rodada legítima.

## CRIT-05 (dona) — **9** · banda `excelente`

A exigência é código, não prosa. `derive_gate_checks()` recomputa os onze booleanos a partir das
oportunidades e experimentos dos retornos (`:1317-1362`); `chain_errors()` compara declarado com
derivado e **nomeia as chaves divergentes** (`:1467-1476`). Booleano `true` sem insumo reprova a
rodada, que é literalmente o que o critério pede. Guardas independentes em `:1225-1234`;
contraprovas negativas em `:2136-2137`, `:2151-2154`, `:2282-2299`. O schema materializa
`gateChecks` como objeto fechado de 11 booleanos (`schemas/…json:1243-1272`) e força
`BLOCKED ⇔ banda + blocking_pending_refs` (`:1323-1341`). O corpus é executável de verdade
(`corpus_adversarial.py:542-567`, `SystemExit(main())` retornando 1 em qualquer escape) e cada um
dos 45 casos carrega tag (`:493-539`) que resolve em achado nomeado da auditoria própria
(`ADVERSARIAL-AUDIT.md:34-51`); contagens por grupo conferidas item a item, somando 45.

Fora de 10 por uma lacuna literal: a derivação recebe `returns` (todos os retornos da rodada),
não o subconjunto autenticado em `accepted_return_refs` — checado só por contenção (`:1414-1418`),
nunca por completude. Um gate pode se apoiar num retorno que o relatório nunca listou como aceito.

- `confidence`: alta · `residual_risk`: o desalinhamento `returns` × `accepted_return_refs` não
  está declarado em lugar nenhum do pacote. O segundo teto (corpus e validador compartilham o motor,
  então 45/45 prova que as mutações conhecidas fecham, não que não exista uma 46ª classe) **está**
  declarado pelo candidato (`corpus_adversarial.py:15-19`, `ADVERSARIAL-AUDIT.md:83-97`, `R4`) —
  teto divulgado, não escondido.

## CRIT-08 (dona) — **9** · banda `excelente`

Todo caminho relativo das três classes de arquivo resolve a partir da profundidade real, e as
profundidades estão corretas em **três** níveis de aninhamento ao mesmo tempo — quatro `..` da raiz
do pacote, cinco de `references/`, seis de cada diretório de agente — todos caindo no mesmo
`regras-de-ouro/REGRAS-DE-OURO.md` existente. Nenhum caminho falhou. A fonte normativa é citada
exatamente como o critério exige, em `SKILL.md:407` e `CONTRATO:171`, como referência; listagem
recursiva completa do pacote não contém `REGRAS-DE-OURO*` nem texto de regras — **sem versão
paralela**, e o `CONTRATO:173` o afirma explicitamente.

Fora de 10: `link_errors()` (`validate_workflow.py:1655-1671`) casa só `[texto](alvo)`, de modo que
as citações em *code span* — inclusive a própria linha da fonte normativa no CONTRATO — não têm
checagem automatizada. Hoje todas resolvem; foram verificadas à mão, não por guarda.

- `confidence`: alta · `residual_risk`: a trava de link é escopada por sintaxe; edição futura num
  caminho entre crases não seria pega por nenhuma checagem do pacote.

## CRIT-03 (secundária — só a cláusula de coerência) — **8** · banda `polido`

No nível onde a fronteira é *exigível*, a cláusula fecha limpa: cada capacidade tem exatamente um
dono, declarado reciprocamente nos três agentes, fixado na tabela do protocolo (`:67-73`) e travado
em código pelo mapa `AGENT_CAPABILITY` (`validate_workflow.py:107-112`, rejeição em `:1178-1179`,
`:1188-1189`) e pelos pares `if/then` do schema (`:1198-1241`, `:1596-1636`). Nem zero, nem dois.

Mas a cláusula é enunciada **no nível do item**, e aí o passo 3 da própria gerente contradiz a
própria regra "Critério com duas donas é fronteira inválida" (`SKILL.md:163`): **`rollback` aparece
duas vezes** (`SKILL.md:155` → experimentos; `:157` → melhoria contínua), e nenhum dos dois agentes
o cede ao outro (`agente-experimentos-e-spikes/SKILL.md:66` reivindica e `:75-77` não declina;
`agente-melhoria-continua/SKILL.md:75,77` reivindica e `:83-85` não declina). Só Descoberta cede
(`agente-descoberta-de-oportunidades/SKILL.md:72-75`). Padrão igual, mais fraco, para `métrica`.
Nenhuma das sobreposições alcança superfície exigível — é defeito de acabamento, não titularidade
ambígua.

- `confidence`: alta · `residual_risk`: `rollback` e `métrica` reivindicados por dois agentes no
  nível de redação, sem exclusão recíproca, contra a regra da própria gerente; **nada no validador
  confere o passo 3 contra as listas "Assumir"/"Não assumir"**, então essa classe de deriva não tem
  guarda.
