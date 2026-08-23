# Placar de migração — Departamento de Segurança

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 193/193 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:a6eaaa8d96c4ecdf0c6d1076ac3bb4603748f75ddf7ee7313ed8c09a88c9305f` | medido-em: 2026-08-22
<!-- /SELO-DE-CONTAGEM -->

## Passagem pelo gate

Este pacote foi submetido ao gate em 2026-07-29. Opiniões, notas, veredito e
histórico vivem fora do candidato, no
[resultado consolidado](../../../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md),
para não contaminar uma rodada futura com o próprio julgamento.

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **184/184 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. Naquela medição, a cadeia canônica somava **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

Data: 2026-07-26
Versão avaliada: 1.0.0
Escopo: fase de evals (passo 9 da [GUIA-DE-EXPANSAO-E-MIGRACAO.md](../../../../../GUIA-DE-EXPANSAO-E-MIGRACAO.md))
do pacote `ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-seguranca` —
profundidade 4, oito agentes na profundidade 6.

## Resultado

| Verificação | Resultado | Executado? |
|---|---:|---|
| Validador determinístico da Segurança | **184/184 PASS** (84 positivos · 100 negativos) | **sim** |
| Teste do motor compartilhado (`_compartilhado`) | 61/61 PASS | **sim** |
| Regressão — `departamento-desenvolvimento` | 105/105 PASS | **sim** |
| Regressão — `departamento-registros` | 170/170 PASS | **sim** |
| Regressão — `departamento-qa-usabilidade` | 117/117 PASS | **sim** |
| Regressão — `departamento-arquitetura-dados` | 114/114 PASS | **sim** |
| Regressão — `departamento-design-ux-ui` | 109/109 PASS | **sim** |
| Regressão — `departamento-arquitetura-software` | 72/72 PASS | **sim** |
| Regressão — `departamento-auditoria-responsabilidades` | 65/65 PASS | **sim** |
| Regressão — `departamento-conteudo-marketing` | 39/39 PASS | **sim** |
| Regressão — `departamento-negocios` | 170/170 PASS | **sim** |
| Regressão — `departamento-evolucao-skills` | 57/57 PASS | **sim** |
| Regressão — `departamento-juizes` | 62/62 PASS | **sim** |
| Regressão — `diretor-de-lentes` | 50/50 PASS | **sim** |
| Regressão — `ceo-maestro` | 33/33 PASS | **sim** |
| Regressão — `departamento-inovacao-melhoria` *(entrou por frente paralela durante esta cascata; rodada 2 daquele pacote — hoje 122/122, ver nota acima)* | 59/59 PASS | **sim** |
| **Total mecânico da cadeia comparável à linha de base** (motor + 14 validadores) | **1408/1408 PASS** | **sim** |
| **Total mecânico observado agora** (motor + 15 validadores, já com Inovação) | **1467/1467 PASS** | **sim** |
| Integridade do legado, recalculada no passo 10 | 154 arquivos · 956.235 bytes · digest `d92607a3fa32f80c44b9a9b18bfce20b16a7c8b69bc5d0756b24754fc3ad1d83` **idêntico** | **sim** |

> **Receita do digest acima, acrescentada em 2026-08-22 (tarefa 102).** Até esta data ele era publicado **só truncado** (`d92607a3…1d83`) e sem como reproduzir: o objeto da alegação não está no pacote — os arquivos legados vivem **fora da Estrutura**, e o validador do pacote não carrega manifesto de legado. Quem lesse a linha não tinha o que executar.
>
> `_compartilhado/verificacoes_pacote.py::digest_de_arvore` sobre `SKILL - Nova formula/maestro/comite-de-lentes/lente-especialista-seguranca`, a partir da raiz do cofre. **Reexecutado em 2026-08-22: 154 arquivos, 956.235 bytes e o mesmo valor** — o número sempre esteve certo; o que faltava era poder conferi-lo.
>
> Aqueles bytes são **congelados por `.gitattributes`** (`"SKILL - Nova formula/maestro/comite-de-lentes/**" -text`), então cru e normalizado dão o mesmo valor — conferido nos dois. É o mesmo desfecho que o `departamento-registros` deu ao digest dele, que foi achado irreprodutível, teve a receita fixada e o valor republicado por inteiro.
| Forward comportamental (15 prompts de [evals.json](evals.json)) | — | **NÃO — pendente** |
| Baseline comportamental do pacote legado `lente-especialista-seguranca` | — | **NÃO — pendente** |
| Acionamento por `description` em runtime | — | **NÃO — pendente** |
| Parecer do `departamento-juizes` sobre esta entrega | — | **NÃO — pendente** |

Comandos executados, a partir da raiz da estrutura:

```bash
python "_compartilhado/teste_validador_schema.py"
for f in $(find . -name "validate_workflow.py" | sort); do python "$f"; done
```

O motor compartilhado é **importado**, nunca copiado: este validador não define nenhuma função de
`validador_schema.py` ou de `verificacoes_pacote.py`, e uma guarda de `ModuleNotFoundError` faz a
ausência do motor falhar legível, com `exit 1`, em vez de despejar traceback.

## As três regras inegociáveis, e onde cada uma está

**1 · Casos negativos ≥ casos positivos.** 100 negativos contra 84 positivos. A regra não está só na
prosa: o validador conta os dois no fim e **reprova a si mesmo** se a proporção inverter.

**2 · Validado contra o schema do consumidor.** O `SECURITY_LEDGER` interno é convertido
**mecanicamente** em `DEPARTMENT_RETURN` e validado contra
[`schemas/diretor-de-lentes.schema.json`](../../../schemas/diretor-de-lentes.schema.json), nunca
contra o próprio. A conversão **não é identidade**: o `causalHeader` do Diretor exige
`candidate_digest` e **não conhece** `target_digest`, e há caso negativo provando que passar o
cabeçalho interno sem converter é rejeitado. O Diretor também rejeita retorno assinado por outro
Departamento, retorno endereçado ao CEO, retorno sem evidência, ledger embutido como campo novo,
nota acrescentada ao envelope, estado diferente de `RETURNED`, missão que não veio dele e missão em
modo que não delega.

**3 · Recalculado em código, sem ler o campo declarado.** Nenhuma regra de bloqueio é conferida por
presença de string:

- os **cinco gatilhos** são derivados dos achados (`derive_triggers`) e comparados com
  `blocking_triggers`;
- a **recomendação de risco** é derivada dos gatilhos (`derive_recommendation`) e comparada com
  `risk_recommendation`;
- os **contadores de achado aberto** são recomputados dos achados (`count_open_findings`), com
  `suspected` e `closed` fora da conta;
- a **validade da autorização** é recalculada pelas nove condições da §3 (`authorization_valid`),
  **sem** consultar o campo `validity` — e há caso em que a autorização se declara `valid` e a janela
  já expirou;
- a **admissibilidade** de cada evidência é recalculada pelas duas listas da §4
  (`evidence_verdict`) e comparada com o veredito declarado;
- o **status da rodada** (`derive_ledger_status`) e o **`test_summary`** (`derive_test_summary`) são
  derivados, não lidos.

**A conta errada tem caso próprio.** Três deles:

| Conta errada | O que ela devolveria | O que a conta certa devolve |
|---|---|---|
| ignorar o crítico ao contar achados abertos | `LIBERAR` | `BLOQUEAR` |
| converter os dez gates locais em dez `pass` | `test_summary.pass = 10` | `pass = 0` — gate local não é teste |
| contar onze áreas com agente dona | 11 donas exclusivas | 10 — `ai_llm` é transversal |

## O que o validador prova

**Pacote e vínculos (5 casos).** Arquivos obrigatórios da gerente e dos oito agentes; `agentes/` com
**exatamente** as oito pastas canônicas do ADR-010; posição sob `departamentos-operacionais/` e sob
`diretor-de-lentes/` conferida em runtime; frontmatter só com `name`/`description`, `description`
≤ 1024, `SKILL.md` ≤ 500 linhas e `short_description` entre 25 e 64; fonte normativa única no caminho
relativo **de cada nível** — `../../../../` na gerente, `../../../../../../` nos agentes, com o
caminho do agente **proibido** na gerente e vice-versa; todo link markdown interno resolvendo; e a
série global de ADR única em toda a estrutura, inclusive contra frentes paralelas.

**Forma do schema (1 caso).** As `$defs` esperadas existem, todo `$ref` resolve, e os `enum` batem
com a realidade: `agentIdentity` = as **pastas reais** de `agentes/`; `coverageArea` = as onze áreas
da referência; `securityRole` = as oito funções; `gateId` = os dez gates da §4; `blockingTrigger` =
os cinco gatilhos da §5. Confere ainda que `coverageEntry.owner` aceita a **gerente** — é isso que
torna `ai_llm` representável sem agente dona.

**Ausência de nota (1 caso).** Nenhum nome de propriedade do schema, em qualquer profundidade, está
no conjunto proibido (`score`, `nota`, `peso`, `corte`, `veredito`, `ranking`, …); **toda** `$def` de
objeto declara `additionalProperties: false`, então um campo de nota não pode ser acrescentado sem
quebrar o schema; e o texto do schema não menciona escala. Três negativos confirmam por execução:
ledger com `score`, achado com `score` e o próprio `DEPARTMENT_RETURN` com `score` são rejeitados —
este último pelo schema do **Diretor**.

**Autoridade herdada (1 caso).** O schema do Diretor **ainda** reserva `departamento-seguranca` em
`operationalDepartment` e em `knownCapability`, trava o par `returned_by` + `causal.producer` neste
Departamento, mantém `return_to`/`returned_to` no Diretor, mantém a nota com os Juízes e continua
exigindo `candidate_digest` sem aceitar `target_digest`. Se o outro lado mudar, quebra aqui.

**Conflito de interesse (6 casos).** `role: EVIDENCE` só é emitido para o `agente-prova-e-reteste` e
`role: DETECTION_RESPONSE` só para o `agente-deteccao-e-resposta` — os dois negativos existem;
`ruled_by` é `const` no julgador de prova, e delegar a admissibilidade a outro é rejeitado; segredo
possivelmente válido sem `responder_agent` é rejeitado; **e o achado de segredo `valid`/`unknown`
cujo `owner_agent` é o próprio `agente-deteccao-e-resposta` — descobriu e conteve — é rejeitado pelo
schema**, com o erro atribuível (`$.owner_agent: valor proibido por not`). O `evidence_conflict`
(quem produziu o achado não certifica a prova de fechamento dele) continua sendo regra recalculada em
código, porque cruza dois artefatos e o schema não o alcança sozinho; o `secret_conflict` permanece
em código como segunda barreira, agora redundante com o schema por escolha.

**Cobertura — a tarefa 0 (1 caso + 5 recalculados).** A dona de cada área **não é digitada** no
validador: é extraída da tabela §1 de
[cobertura-e-admissibilidade.md](../references/cobertura-e-admissibilidade.md). O caso prova que as
onze áreas da tabela são as onze do schema, que **dez** têm agente dona, que `ai_llm` está declarada
**transversal**, que as oito capacidades têm ao menos uma área e que a `SKILL.md` não exige mais dona
de agente para as onze. As regras recalculadas provam que pôr uma agente como dona de `ai_llm` é
inválido, que a gerente não é dona de área de especialidade, que trocar a dona de uma área pela irmã
é inválido e que a conta de donas exclusivas dá **dez**, não onze.

**Fixtures positivas (20 casos).** Uma `SECURITY_TASK` estática por função (8), a tarefa ativa com
autorização completa, contribuição concluída, parcial com `SKIP` e com lacuna de capacidade, achado
crítico confirmado, achado fechado com reteste, achado de segredo aberto e fechado com o ciclo
completo, evidência de fonte admissível, evidência de `SKIP` declarada inadmissível, atestado com
proveniência e custódia, lacuna aberta, e os três ledgers — o que bloqueia, o sem gatilho e o
parcial. Todas validadas contra o schema **inteiro**, o que prova de quebra que o `oneOf` da raiz
discrimina os seis artefatos.

**Casos negativos (99).** Cada um é validado contra a `$def` do próprio artefato, para que a
rejeição seja atribuível à regra pretendida — validar contra o `oneOf` da raiz devolveria sempre
"0 alternativas" e esconderia o motivo:

- **tarefa (19):** produtor forjado; agente fora do time; `ATIVA` sem autorização, contra produção ou
  dado real, com `validity: invalid`, na onda 0, sem condição de parada, sem contato de emergência e
  com janela irresolvível; `ESTATICA` carregando autorização; prova delegada a quem não julga
  admissibilidade; contenção de segredo delegada a quem o descobriu; retorno ao Diretor contornando a
  gerente; sem área, com área inexistente, sem `forbidden_context`, sem fronteira ao irmão, em onda
  inexistente e em rodada fora do limite de dez;
- **contribuição (7):** `COMPLETED` com `SKIP` ou com área `NAO_AVALIADO`; lacuna sem pendência;
  retorno fora da gerente; sem área declarada; `NAO_APLICAVEL` sem ativo nem fluxo; agente fora do
  time;
- **achado (14):** confirmado sem evidência admissível; segredo possivelmente válido descoberto e
  contido pelo mesmo agente; fechado sem reteste, com reteste `fail` ou
  com reteste sem evidência; segredo fechado sem revogação e rotação, sem incidente e sem
  responsável; risco aceito sem autoridade; campo de nota; dono fora do time; severidade e confiança
  inventadas; controle observado vazio;
- **evidência (14):** `SKIP` como prova; teste ativo sem autorização; atestado sozinho em alegação
  crítica; inadmissível sem motivo; admissível com motivo; inadmissível sustentando crítico;
  ferramenta sem versão; admissibilidade decidida por quem não julga; atestado com proveniência não
  verificada e com chave revogada; sem versão do alvo; motivo fora da tabela; classificação fora do
  enum; sem limites de coleta;
- **lacuna (5):** fechada sem evidência; escalada para fora do Diretor; estado seguro diferente de
  `BLOQUEADO`; sem impacto; função fora das oito;
- **ledger (30):** saída positiva com gatilho; ressalva como meio-termo para crítico; crítico sem o
  gatilho listado; fail-open com saída positiva e sem o gatilho listado; atividade ativa não
  autorizada concluída; `COMPLETED` com gate em `FAIL`, com gate `NAO_VERIFICADO`, sem registro de
  emissão (R6), com `SKIP` aberto, com lacuna aberta e com exclusão explícita não vazia; sem R6;
  nove gates; gate repetido; campo de nota; auto-aprovação; gate geral emitido; autoridade de
  julgamento avocada; devolução fora do Diretor; `coverage_map` sem `ai_llm`; `COBERTO` sem
  evidência; `NAO_APLICAVEL` sem ativo nem fluxo; estado de cobertura inventado; gatilho fora dos
  cinco; recomendação fora do enum; sem onda e com onda inexistente; gate em `FAIL` sem dono da
  correção; sem motivo da recomendação;
- **fronteira (11):** listados na regra 2, acima.

## Tarefa 0 — a contradição de contrato corrigida

**O defeito.** A `SKILL.md` mandava, em *Descobrir o time real* (passo 4) e no workflow (passo 2),
"confirmar uma dona única por área do `coverage_map`" e "atribuir cada uma das onze áreas do
`coverage_map` à **agente dona**", e o portão de saída cobrava "onze áreas com dona única". Mas
`ai_llm` (dimensão 10) é **transversal por decisão do ADR-010, decisão 6**: não tem — e **não pode
ter** — agente dona, e o estado dela é consolidado pela gerente a partir do que cada irmão cobriu.
Lido ao pé da letra, o gate exigia uma dona que o ADR **proíbe** existir.

**Conferido nos três arquivos antes de editar.**

| Arquivo | O que diz |
|---|---|
| [cobertura-e-admissibilidade.md](../references/cobertura-e-admissibilidade.md) §1 | a tabela das doze dimensões dá dona de agente a dez áreas e marca a dimensão 10 como **transversal (§3)** |
| [cobertura-e-admissibilidade.md](../references/cobertura-e-admissibilidade.md) §3 | "a dimensão 10 não tem agente próprio (ADR-010, decisão 6)"; "o estado de `ai_llm` no mapa é consolidado pela gerente" |
| [ADR-010](../references/adr-010-seguranca-sem-julgamento-e-time-por-funcao.md), decisão 6 | "IA/LLM é transversal e obrigatório, **não é agente**"; a alternativa de criar um nono agente foi rejeitada por disputar recorte com cada irmão |
| os oito `agentes/*/SKILL.md` | os oito repetem "a dimensão 10 é transversal" e puxam o aspecto para a **própria** fronteira; nenhum se declara dono da área |

**A correção**, só na `SKILL.md` (fronteira desta etapa), em cinco pontos: *Descobrir o time real*
(cabeçalho e passo 4, que agora nomeia a exceção e diz que exigir dona para `ai_llm` **é violar** o
ADR), o "Concluído quando" da mesma seção, o passo 2 do workflow e o seu "Concluído quando", o
portão de saída e o formato de devolução. A fórmula adotada é **"dez áreas com agente dona única,
mais `ai_llm` consolidada pela gerente"**.

**O caso de teste** é `cobertura: dez áreas com dona única + ai_llm transversal (tarefa 0)`, mais
cinco condições recalculadas. Ele não confere prosa por amostragem: **lê a tabela da referência** e
deriva dela a conta, de modo que uma edição futura que volte a exigir onze donas exclusivas quebra o
validador — na referência ou na `SKILL.md`, tanto faz.

**O que ficou fora da fronteira — e foi fechado na cascata (2026-07-26).** Duas ocorrências de "onze
áreas com dona" sobreviviam fora da `SKILL.md` e ficaram declaradas como dívida de redação. A cascata
do passo 10 as alinhou à fórmula corrigida:

| Onde | Antes | Agora |
|---|---|---|
| [CONTRATO-DE-COMPROMISSO.md](../CONTRATO-DE-COMPROMISSO.md), obrigação 3 | "Recortar o domínio nas onze áreas, com **uma** dona por área e nenhuma área sem dona" | "Recortar o domínio nas onze áreas: **dez com agente dona única**, mais `ai_llm` **consolidada pela gerente** por ser transversal (ADR-010, decisão 6)…" |
| `agents/openai.yaml`, `default_prompt` | "cobrir as onze áreas com dona única" | "cobrir as dez áreas com agente dona única mais `ai_llm` consolidada pela gerente" |

O `short_description` do pacote **não** foi tocado e continua em 34 caracteres — dentro de 25–64,
conferido pelo `validate_metadata()`. O validador **não** cobre a redação destas duas frases por
amostragem de string; o que ele cobre é a **conta** derivada da tabela §1 da referência, que dá dez
donas exclusivas e não onze. Dizer que ele cobre a prosa seria o gate tautológico que o passo 9 proíbe.

## O que ainda não foi provado

### Estado vigente das obrigações — conferido em 2026-08-08

> **Duas obrigações desta seção estavam declaradas como pendentes e não estão.** A campanha [`remedicao-dos-sete-2026-08-03`](../../../../evals/remedicao-dos-sete-2026-08-03/PLACAR.md) executou as duas sobre este pacote. O texto dos itens abaixo é registro da rodada em que foi escrito e fica como está; o estado corrente é este.

| obrigação | estado em 2026-08-08 | quem emitiu |
|---|---|---|
| Auditoria independente | **EXECUTADA** em 2026-08-03 · `governance_report` **NONCOMPLIANT** · **3 achados** nomeados, com dono e condição de correção | `departamento-auditoria-responsabilidades` |
| Parecer dos Juízes | **EMITIDO** em 2026-08-03 · veredito **REPROVED** · `minimum_score` **6**, faixa **6–8** · **2 de 8** critérios `NAO_DISCRIMINADO` | `departamento-juizes` |

> **A faixa atravessa o corte, e isso é o achado — não um detalhe.** Duas instâncias da mesma lente, sobre os mesmos bytes e com a mesma rubrica, divergiram em 54% dos pares na campanha. Onde a faixa cruza o 6/7, consertar "até passar" seria mirar num número que a régua não distingue. O aceite interno deste pacote **nunca esteve estabelecido**, e continua não estando.
> **E há um limite nesta leitura, declarado pela própria campanha:** a árvore viva mudou durante a medição, e para este pacote o objeto julgado é o da **custódia** — o `candidate_digest` do `JUDGMENT_REQUEST` já não reproduz contra o disco. Isso não invalida a nota; invalida a pretensão de que ela descreva o pacote de agora.

### Dono e condição de fechamento, item a item

> Exigido pelos achados `CA-01` e `GR-01`/`GR-02` da mesma campanha: pendência declarada sem dono é pendência de ninguém. "O próprio Departamento" significa o pacote que este placar mede — ele responde pela própria evidência.

| item | dono | fecha quando |
|---:|---|---|
| 1 | o próprio Departamento | os 15 prompts forem executados contra instância nova e independente, com resposta produzida e conferida |
| 2 | o próprio Departamento | a `lente-especialista-seguranca` for avaliada nos mesmos cenários, ou este item registrar a decisão de não comparar, com motivo |
| 3 | o próprio Departamento | houver medição de acionamento em sessão nova com frase neutra, no molde da §1b do `CLAUDE.md` do cofre |
| 4 | o próprio Departamento | houver âncora externa ao pacote que prove a emissão — runtime separado, assinatura fora da árvore ou terceiro que não compartilhe o processo. Depende das tarefas 50 e 57; nenhuma trava de dentro fecha isto |
| 5 | — | já fechado no próprio texto, com data |
| 6 | o próprio Departamento | cada risco residual da §8 do protocolo tiver regra que o feche, ou for reclassificado como limite aceito, com dono e data |
| 7 | `diretor-de-lentes` | o `testSummary` do schema do Diretor proibir por FORMA o valor que hoje só o contrato proíbe |
| 8 | `ceo-maestro` | os prompts comportamentais do `ceo-maestro/evals/README.md` forem reexecutados após a entrada deste Departamento |
| 9 | `departamento-juizes` | um veredito novo dos Juízes suceder o de 2026-08-03. Ver o estado vigente acima |
| 10 | — | já fechado no próprio texto, com data |


Declarado como `SKIP`, com motivo — prova executada > checklist, e sucesso simulado é violação
(RI-04):

1. **Forward comportamental.** Os **15 prompts** de [evals.json](evals.json) **não** foram executados
   contra nenhuma instância nova e independente. Nenhuma resposta foi produzida e nenhuma foi
   conferida. Não há evidência de que a skill **aciona** pelos gatilhos declarados, nem de que
   **adere** ao contrato sob a pressão do atalho — só de que os artefatos são estruturalmente válidos
   e a aritmética fecha. **Nenhum `FORWARD-TEST.md` foi escrito**, e escrevê-lo com respostas que
   ninguém produziu seria fabricar resultado. Todo caso do catálogo carrega `acionou: NAO_MEDIDO` e
   `aderiu: NAO_MEDIDO`, e o validador **reprova** se algum declarar outra coisa.
2. **Baseline do pacote legado.** A `lente-especialista-seguranca` não foi avaliada contra os mesmos
   cenários. Que esta migração **melhora o comportamento** permanece não medido. Os evals do legado
   não foram promovidos: medem outro gatilho e outra saída.
3. **Acionamento por `description` em runtime.** Não há prova de que a `description` do frontmatter
   faz esta skill ser escolhida, nem de que os oito agentes são descobertos por enumeração de
   `agentes/`. Isso só se mede executando, e não foi executado.
4. **Existência do time em runtime (R6).** O validador confere **estrutura** e **aritmética**, nunca
   **execução**: um `SECURITY_LEDGER` internamente coerente é reproduzível sem que nenhuma
   `SECURITY_TASK` tenha sido emitida. Exigir `task_issuance_records` para `COMPLETED` **encarece** a
   fabricação; não a impede — é o teto declarado do próprio R6.
5. ~~**Conflito de interesse do segredo, no schema.**~~ **FECHADO em 2026-07-26, na cascata do passo
   10.** O `securityFinding` ganhou um `if/then` próprio: com `secret_response.secret_validity` em
   `valid`/`unknown`, o `owner_agent` é proibido de ser `agente-deteccao-e-resposta`. A trava deixou
   de viver só na regra recalculada (`secret_conflict`) e na prosa do ADR-010, decisão 5. O caso
   negativo `segredo possivelmente válido descoberto e contido pelo mesmo agente` prova a rejeição, e
   o erro é atribuível à regra pretendida (`$.owner_agent: valor proibido por not`), não a um efeito
   colateral. **Teto declarado:** o schema fecha o caso do **mesmo agente** nos dois papéis dentro de
   **um** achado; ele não alcança conluio entre dois agentes distintos, nem a certificação cruzada
   entre artefatos — essa continua sendo a regra recalculada `evidence_conflict`.
6. **Riscos residuais R1–R5, R7 e R8.** São limites de runtime declarados na §8 do
   [protocolo](../references/protocolo-seguranca.md), e nenhuma regra deste pacote os fecha: bypass
   por invocação explícita pelo nome (R1), autorização que é documento e não canal (R2), validade de
   segredo não testável (R3), instrução embutida por paráfrase (R4), prova de terceiro não
   reexecutada (R5), ausência de achado que não é ausência de vulnerabilidade (R7) e bypass para fora
   (R8). Nada aqui foi executado contra sistema real: nenhum scan, nenhum reteste, nenhuma
   ferramenta.
7. **`test_summary` fabricado.** A regra "gate local não é teste" é **contratual**. O `testSummary`
   do schema do Diretor aceitaria `pass: 10` sem reclamar. O validador prova que a conversão **deste**
   pacote emite `0/0/0`; não prova que outro emissor não mentiria.
8. **Evals comportamentais do superior.** O `ceo-maestro/evals/README.md` manda reexecutar os prompts
   comportamentais quando Diretor, Negócios ou Juízes forem migrados. A entrada de um Departamento
   operacional novo tem o mesmo efeito prático e **não** foram reexecutados nesta frente. O
   determinístico do CEO passou — 33/33 —, e determinístico **não** é comportamental.
9. **Parecer do `departamento-juizes`.** A qualidade desta entrega não foi julgada, e este
   Departamento **não julga a si próprio** (`report_self_approval: prohibited`,
   `judgment_authority: departamento-juizes`, ambos `const` no schema).
10. ~~**Cascata da fase 5.**~~ **EXECUTADA em 2026-07-26.** O `ORGANOGRAMA.md` passou a contar o
    estado verdadeiro — estado da migração com `[x]`, item 5 com os **oito** nomes reais no lugar dos
    três propostos (`agente-privacidade-e-compliance` **nunca existiu como pasta**), parágrafo
    *Migrado em 2026-07-26*, árvore canônica com a pasta real, linha do mapeamento de nomes e
    `## Estado desta etapa`. As menções vencidas foram varridas e tratadas: `SKILL.md` e
    `origem-migracao.md` deste pacote diziam que `agents/`, `agentes/` e `evals/` "ainda não existem";
    `diretor-de-lentes/references/origem-migracao.md` listava `lente-especialista-seguranca` como
    origem ainda apenas legada; e o `PLACAR.md` da Arquitetura de Software dizia que os dois vizinhos
    não existiam. As duas ocorrências de redação da tarefa 0 foram alinhadas (tabela acima). O passo 4
    do [guia](../../../../../GUIA-DE-EXPANSAO-E-MIGRACAO.md) trocou a lista manual de "qual ADR é de
    quem" por um ponteiro para o `validate_adr_series` do `_compartilhado`. **Continua aberta** a
    seção 7 do guia (ordem das próximas frentes), que ainda não riscou Segurança nem Desenvolvimento
    — fora da fronteira de escrita desta cascata.

## Regressão da cadeia — deltas e atribuição

Contagem que muda **sem** mudança de contrato é regressão. Todos os deltas abaixo têm mudança de
contrato identificada, e **nenhum** vem desta frente: fora da `SKILL.md` do próprio Departamento e do
`evals/`, esta frente não escreveu em arquivo algum.

| Pacote | Baseline registrado | Agora | Δ | Atribuição |
|---|---:|---:|---:|---|
| motor `_compartilhado` | 55 | **61** | +6 | seis casos novos do `validate_adr_series`, adicionado ao motor por outra frente |
| `departamento-desenvolvimento` | — | **105** | novo | pacote materializado em paralelo, sem baseline anterior |
| `departamento-registros` | 169 | **170** | +1 | caso da série global de ADR |
| `departamento-qa-usabilidade` | 116 | **117** | +1 | caso da série global de ADR |
| `departamento-arquitetura-dados` | 114 | **114** | 0 | já nasceu com o caso da série de ADR |
| `departamento-design-ux-ui` | 108 | **109** | +1 | caso da série global de ADR |
| `departamento-arquitetura-software` | 70 | **72** | +2 | caso da série de ADR **+** caso novo de gabaritos de `delegated_dependency`, da própria frente da Arquitetura |
| `departamento-auditoria-responsabilidades` | 64 | **65** | +1 | caso da série global de ADR |
| `departamento-conteudo-marketing` | 38 | **39** | +1 | caso da série global de ADR |
| `departamento-negocios` | 169 | **170** | +1 | caso da série global de ADR |
| `departamento-evolucao-skills` | 56 | **57** | +1 | caso da série global de ADR |
| `departamento-juizes` | 61 | **62** | +1 | caso da série global de ADR |
| `diretor-de-lentes` | 49 | **50** | +1 | caso da série global de ADR |
| `ceo-maestro` | 32 | **33** | +1 | caso da série global de ADR |
| `departamento-seguranca` | — | **183** | novo | este pacote |

**Releitura da cascata (passo 10, 2026-07-26).** Todos os quinze validadores foram redescobertos por
`find . -name "validate_workflow.py" | sort` e reexecutados junto com o teste do motor. Catorze
devolveram **exatamente** a contagem acima; o único delta é o deste pacote:

| Pacote | Antes da cascata | Depois | Δ | Atribuição |
|---|---:|---:|---:|---|
| `departamento-seguranca` | 183 | **184** | **+1** | **desta frente**: mudança de contrato declarada — o `if/then` novo no `securityFinding` (ADR-010, decisão 5) e o caso negativo que o prova |
| todos os outros 13 + motor | — | **idênticos** | 0 | nenhum delta; nenhuma atribuição necessária |
| `departamento-inovacao-melhoria` | — | **59** | **pacote novo** | **não é desta frente**: a pasta não existia no início desta cascata (`find` inicial devolveu 14 validadores) e apareceu com ADR-013, três agentes e `evals/` completos, materializada por frente paralela |

Cadeia comparável à linha de base: **1408/1408 PASS**. Observada agora, já com Inovação:
**1467/1467 PASS**. Delta sem mudança de contrato seria regressão; o único delta em pacote existente
tem contrato, está declarado aqui e no item 5 de *O que ainda não foi provado*.

Os `+1` foram conferidos no diff de cada validador: a linha acrescentada é sempre
`case("série global de ADR é única em toda a estrutura", True, validate_adr_series(STRUCTURE_ROOT))`.
O `+2` da Arquitetura de Software foi conferido do mesmo modo e traz, além dela, um segundo
`cases.append` de gabaritos de dependência delegada.

**Instabilidade observada e resolvida.** Numa execução intermediária o
`departamento-desenvolvimento` devolveu 104/105; três execuções seguintes devolveram 105/105 sem que
nada fosse alterado por esta frente. A causa é escrita concorrente: aquele pacote estava sendo
materializado em paralelo enquanto a cadeia rodava. O número registrado acima é o da leitura estável.

## Fonte normativa

[../../../../../regras-de-ouro/REGRAS-DE-OURO.md](../../../../../regras-de-ouro/REGRAS-DE-OURO.md)
— fonte única. Relacionado: [SKILL](../SKILL.md) · [CONTRATO](../CONTRATO-DE-COMPROMISSO.md) ·
[protocolo](../references/protocolo-seguranca.md) ·
[cobertura e admissibilidade](../references/cobertura-e-admissibilidade.md) ·
[ADR-010](../references/adr-010-seguranca-sem-julgamento-e-time-por-funcao.md) ·
[origem da migração](../references/origem-migracao.md) ·
[schema do pacote](../schemas/departamento-seguranca.schema.json) ·
[catálogo de evals](evals.json) · [validador](validate_workflow.py)
