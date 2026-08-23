# ADR-017 — Inspeção em papel sob porta única

- **Estado:** **aceito** — vinculante
- **Data:** 2026-08-01 · **decidido em:** 2026-08-03
- **Decidido por:** **Jeremias**, em 2026-08-03, ao autorizar a canonização do
  `cand-K-extracao-terminada-por-recomputacao` sob a **regra de parada** que ele fixou.
  A decisão é consciente do veredito: os Juízes emitiram **`REPROVED`, `minimum_score 4`,
  `critical_fail: false`** na rodada 9, e a canonização foi autorizada assim mesmo, **com os
  limites declarados** — o teto `OI-04`, que não fecha neste runtime; `R9`, `R10` e `R11`
  abertos; e o `A6`, pelo qual o método valia sobre 43 de 66 agentes até a tarefa 16 converter
  os outros 23. Registro em `ceo-maestro/evals/compliant-porta-unica-2026-08-01/179-FECHAMENTO-DA-TAREFA-15.md`
  e recibo em `180-RECIBO-DE-CANONIZACAO.json`.

  **Correção de um defeito de registro, declarada em vez de apagada.** Este cabeçalho esteve
  errado nas duas direções. Na rodada 1 dizia `aceito` e `Decidido por: Jeremias` enquanto o
  contrato dizia `proposta` — duas instâncias dos Juízes registraram a divergência, porque quem
  abrisse o arquivo trataria como lei fechada uma decisão ainda em julgamento. Depois passou a
  dizer `ninguém ainda` e **assim permaneceu enquanto o mecanismo que ele decide era canonizado
  e implantado nos dois runtimes** — lei em produção com autoridade declarada como inexistente.
  O segundo erro foi do `ceo-maestro`, apontado pelo inspetor de contrato-e-autoridade na
  auditoria da tarefa 10, e é o inverso exato do primeiro.
- **Contexto normativo:** [../../../../../regras-de-ouro/REGRAS-DE-OURO.md](../../../../../regras-de-ouro/REGRAS-DE-OURO.md)
- **Substitui:** nada. **Altera:** a unidade de inspeção e o `AUDIT_RECEIPT` do
  [protocolo de auditoria](protocolo-auditoria.md), §1.2, §1.6 e §2.

## Contexto

A Estrutura foi implantada como **porta única**: só `ceo-maestro` registra como skill
invocável. Medido em 2026-08-01, no runtime:

| medida | valor |
|---|---:|
| skills registradas em profundidade ≤2 | 58 |
| `SKILL.md` aninhados sob `ceo-maestro` | 81 |
| `agente-*` que resolvem como skill invocável | **0** |

Os três agentes inspetores da Auditoria existem em disco como contrato e **não são
alcançáveis**. O protocolo lia isso pela §1.6: `MISSING` → nenhuma `AUDIT_TASK` emitida →
`SEM_RETORNO` → `AUDIT_CAPABILITY_GAP` → as dez dimensões `NAO_PROVADO` → `REPROVADO` →
`NONCOMPLIANT`.

A barreira de saída do CEO exige `governance_report COMPLIANT`. Logo, sob porta única,
**nenhum candidato jamais fecha como validação normal**. O gate era insatisfazível por
construção, e isso foi medido em três frentes independentes: as duas attempts da tarefa 11
e o julgamento da tarefa 14.

A Auditoria **agiu certo** ao recusar. O defeito não era dela nem dos candidatos: o
requisito foi escrito para uma arquitetura de skills aninhadas invocáveis, e a Estrutura
foi implantada como porta única, deliberadamente.

## A armadilha que esta decisão tinha de evitar

Tornar o gate satisfazível **afrouxando-o** seria pior que deixá-lo quebrado. Havia uma
saída fácil e errada: aceitar que `COMPLIANT` significasse *a gerente afirma que
inspecionou*. Isso trocaria um gate insatisfazível por um gate decorativo — e o segundo é
pior, porque parece funcionar.

## Decisão

**Sob porta única, "agente" é o papel que a gerente desempenha lendo o contrato do agente.**
O `CONTRATO-DE-COMPROMISSO.md` do agente deixa de ser o *endereço de uma capacidade* e
passa a ser o **método** da inspeção.

Três consequências, todas mecânicas:

1. **O contrato do agente não muda.** As obrigações, as proibições e a barreira de saída
   continuam idênticas. Muda **quem executa**, não **o que é executado**. Nenhum dos três
   contratos de agente foi tocado por esta decisão — e isso é verificável por digest.

2. **O `AUDIT_RECEIPT` passa a exigir âncora.** O recibo antigo pedia `evidence_refs`:
   identificadores opacos como `"evidence-01"` que **nada** reabria. O novo pede
   `evidence_anchors` — arquivo, número de linha, citação literal e digest do arquivo. Um
   terceiro reabre o arquivo, vai à linha e compara. Âncora que não reabre não sustenta
   estado.

3. **A recusa fica intacta.** Dimensão sem inspeção executada continua `NAO_PROVADO`, e
   `NAO_PROVADO` continua bloqueando. A função `estado_efetivo` só **rebaixa** — nunca
   promove `NAO_PROVADO` a `CONFORME`. A direção única é o que impede que reclassificar
   vire conserto.

### Por que isto não é afrouxamento

A barra **subiu**. Comparação linha a linha do que era exigido para uma dimensão fechar
`CONFORME`:

| | antes | depois |
|---|---|---|
| identificador de evidência | exigido, opaco, nunca reaberto | continua exigido |
| arquivo real | não exigido | **exigido**, e reaberto em código |
| linha | não exigido | **exigido**, e conferida |
| citação literal | não exigido | **exigida**, ≥8 caracteres úteis, conferida contra a linha |
| digest do artefato ancorado | não exigido | **exigido**, e recomputado |
| método citado | não exigido | **exigido**: contrato do agente, por caminho e digest |
| prova de que o método foi lido | não exigido | **exigida**: contagens do contrato reconferidas |
| `NAO_APLICAVEL` | justificativa em prosa, ≥20 caracteres | prosa **e** âncora — mitiga R7 |
| registro de emissão (`assignments`) | exigido | **continua exigido, sem alteração** |

Nenhuma linha ficou mais fraca. Sete ficaram mais fortes. O gate ficou satisfazível porque
**deixou de depender de um recurso de runtime que não existe** e passou a depender de
trabalho verificável — não porque passou a aceitar menos.

### O que continua sendo `MISSING`

A porta única tirou a **invocabilidade** do agente, não o **contrato** dele. Portanto:

- contrato do agente **ausente em disco** → método `MISSING` → dimensões `NAO_PROVADO`;
- contrato presente mas **digest divergente** do declarado → método não conferido →
  `NAO_PROVADO`;
- contrato presente e lido, mas **sem âncora** na dimensão → `NAO_PROVADO`.

Ausência de evidência permanece ausência. É a regra central do Departamento, e ela não foi
tocada.

## Alternativa recusada — reexecutar noutro runtime

A outra saída era **reexecutar a rodada num runtime onde as capacidades aninhadas resolvam
como skill invocável**, deixando o requisito como está.

Recusada por três razões:

1. **Faz a Estrutura depender de um runtime que ela não tem.** A porta única é decisão
   deliberada e documentada, não acidente de implantação. Um gate que só fecha noutro lugar
   é um gate que não fecha.
2. **Adia o defeito sem corrigi-lo.** O `evidence_ref` opaco continuaria opaco; o recibo
   continuaria não reabrindo nada. Os três agentes invocáveis produziriam recibos igualmente
   inverificáveis, e o R6 continuaria valendo por inteiro. A lacuna de capacidade escondia um
   problema mais fundo — a prova que ninguém reabre — e resolvê-la por runtime deixaria esse
   problema intacto.
3. **Não é reproduzível como evidência.** Uma auditoria cujo veredito depende de qual
   runtime rodou não é auditoria: é sorte de ambiente. A âncora, ao contrário, reabre em
   qualquer lugar onde a árvore exista.

O modo `CAPACIDADE_INVOCAVEL` fica **declarado no schema** para o dia em que um runtime
resolver os agentes aninhados. Ele exige exatamente as mesmas âncoras: o modo descreve
**quem executou**, e nunca é desconto de prova.

## Alternativa recusada — assinar o recibo por confiança

Aceitar `review_chain.independent: true` como prova, já que é a gerente que escreve tudo de
qualquer forma. Recusada: é a definição literal da armadilha. `true` é um byte que qualquer
um digita; uma citação que reabre no arquivo certo, na linha certa, na versão certa, não é.

## Consequências

**Positivas.** O gate fecha fazendo o trabalho. A prova ficou reabrível por terceiro, e por
qualquer terceiro — não só por quem tem o runtime certo. A dimensão `EVIDENCIA` passou a ter
instrumento próprio em vez de depender do relato. `NAO_APLICAVEL` deixou de ser a saída
barata que R7 previa.

**Negativas, declaradas.**

1. **R6 continua valendo por inteiro, e a estimativa que estava aqui foi MEDIDA e caiu.**
   Tudo é escrito pela própria gerente. Este parágrafo dizia que a âncora *"encarece muito"*
   a fabricação, e que quem fabricasse âncoras válidas teria feito *"quase todo o trabalho de
   auditar"*. Em 2026-08-02 um executor independente mediu o custo real, no caso `OI-04`:
   **80 linhas de código, 0,031 s, 1 tentativa, 4 arquivos lidos, zero conhecimento do
   conteúdo auditado.** A âncora encarece **pouco**, e o número substitui o advérbio.
   Nenhum controle técnico de canal existe no runtime, e a rodada 5 parou de compensar isso
   com estimativa: o limite virou `R11`, viaja no envelope, e a alegação de `COMPLIANT` foi
   reduzida ao que o mecanismo faz.
2. **A âncora prova que um arquivo da raiz auditada foi reaberto na versão declarada — e
   só isso.** Ela **não** liga a dimensão ao artefato que deveria sustentá-la: a sonda `P2`
   do julgamento fechou `COMPLIANT` com `INTENT` ancorada num arquivo real sem relação com a
   dimensão. Pertinência e mérito continuam sendo dos Juízes (R5), e o limite é nomeado como
   `R9` em `pending`, em toda emissão — era `R8` até a rodada 3, e colidia com o
   `R8` do §7 do protocolo, que é bypass para fora. Um inspetor pode ancorar na linha certa e concluir
   errado — e pode ancorar no arquivo errado sem que o mecanismo perceba.
3. **A âncora envelhece com o arquivo.** Mudou o arquivo, muda o digest, e a âncora deixa de
   reabrir. Isso é deliberado — é assim que prova velha para de valer — mas obriga a
   reexecutar a inspeção quando o candidato muda, e isso custa.

## Verificação

- **A trava é chamada onde a decisão acontece.** O `GOVERNANCE_REPORT` é produzido por
  [`../scripts/emitir_governanca.py`](../scripts/emitir_governanca.py), que chama
  `verificar_inspecao_executada` **antes** de montar a matriz. Os estados que entram na
  matriz são os **efetivos**, saídos da trava, nunca os declarados no recibo.
- **O call site é conferido por FLUXO DE DADOS**, em
  `evals/validate_workflow.py::validate_call_site`. Conferir por **nome chamado** não bastou:
  na rodada 1, manter a chamada e descartar o retorno emitia `COMPLIANT` com zero âncoras e o
  validador ficava verde. Agora a conferência liga atribuição a uso — o valor devolvido pela
  trava tem de ser o que alimenta `montar_ledger`, e `governance_verdict`,
  `inspection_verification` e `candidate_identity` têm de descender dele. Trava que aceita
  "alguma checagem roda" não obriga a própria presença e erode em silêncio.
- **A instrução de uso publicada faz parte da trava** — ADR-018. O validador extrai as
  invocações que a `SKILL.md`, o protocolo e os ADR publicam, e **executa** a documentada com
  `candidate_digest` falso, exigindo que ela barre.
- **Provado por mutação**, não declarado. Ver
  `ceo-maestro/evals/compliant-porta-unica-2026-08-01/16-PROVA-DE-MUTACAO-R2.md`, e a rodada 1
  em `02-PROVA-DE-MUTACAO.md`.

## Fronteiras que esta decisão NÃO cruza

- **A porta única fica.** Transformar os 81 `SKILL.md` aninhados em skills invocáveis
  continua fora de escopo, e esta decisão não o pede.
- **A nota continua dos Juízes.** Nada aqui pontua (ADR-003 intacto).
- **A faixa do ADR-014 não foi tocada.**
- **O conjunto de dez dimensões não mudou.** Mudar dimensão exige ADR próprio, e este não é.
