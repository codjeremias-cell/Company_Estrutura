# Placar de migração — Departamento de Auditoria e Responsabilidades

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 180/180 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:6b0874485d9db707e53a3fccbb889d0a80b7268210d21689e9ed3fec62b8b387` | medido-em: 2026-09-02
<!-- /SELO-DE-CONTAGEM -->

## Passagem pelo gate

Este pacote foi submetido ao gate em 2026-07-29. Opiniões, notas, veredito e
histórico vivem fora do candidato, no
[resultado consolidado](../../../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md),
para não contaminar uma rodada futura com o próprio julgamento.

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **65/65 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. Naquela medição, a cadeia canônica somava **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

Data: 2026-07-26
Versão avaliada: 1.0.0
Escopo: migração de `SKILL - Nova formula/maestro/comite-de-lentes/lente-auditor-responsabilidades`
para `Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-auditoria-responsabilidades`

## Resultado

| Verificação | Resultado | Executado? |
|---|---:|---|
| Validador determinístico da Auditoria | 65/65 PASS | **sim** |
| Regressão do validador do `departamento-juizes` | 61/61 PASS | **sim** |
| Regressão do validador do `diretor-de-lentes` | 49/49 PASS | **sim** |
| Regressão do validador do `ceo-maestro` | 32/32 PASS | **sim** |
| Total mecânico dos quatro pacotes | **206/206 PASS** | **sim** |
| Forward comportamental (15 casos válidos) | **15/15 casos · 58/60 asserções · 0 contorno** | **sim** — [FORWARD-TEST.md](FORWARD-TEST.md) |
| Baseline comportamental do pacote legado | — | **NÃO — pendente** |
| Auditoria independente do contrato | — | **NÃO — pendente** |

Comando executado, a partir da raiz do pacote:

```bash
python evals/validate_workflow.py
```

## O que o validador prova

**Pacote e vínculos (8 casos).** Arquivos obrigatórios da gerente e dos três agentes; `agentes/`
contendo exatamente os três nomes do organograma; **posição sob `departamentos-operacionais/`**
conferida em runtime; frontmatter com apenas `name`/`description`, nome igual ao da pasta,
descrição ≤ 1024 caracteres e `SKILL.md` ≤ 500 linhas; `short_description` entre 25 e 64
caracteres; fonte normativa única no caminho relativo correto **de cada nível** (`../../../../`
na gerente, `../../../../../../` nos agentes); **todos** os links markdown internos resolvendo;
`$ref` do schema resolvendo; `enum` de `auditorId` batendo com as pastas reais; e as **dez
dimensões** do schema idênticas às da referência.

> O verificador de links pegou dois links quebrados no ADR-003 na primeira execução — exatamente a
> armadilha nº 1 do `GUIA-DE-EXPANSAO-E-MIGRACAO.md`: Departamento operacional está um nível mais
> fundo que `departamento-juizes`. Corrigidos antes de fechar o pacote.

**ADR-003 — nenhum campo de nota (1 caso).** O validador percorre o schema inteiro e falha se
encontrar `score`, `nota`, `minimum_score`, `absolute_score`, `scorecard` ou `cut_score` em
qualquer profundidade. É a prova mecânica de que a nota saiu deste Departamento.

**Autoridades herdadas (1 caso, 9 asserções).** Lê os schemas do Diretor e do CEO e confirma que o
`governanceReport` continua sendo autoria desta Auditoria, que seu `verdict` continua **binário**
(`COMPLIANT`/`NONCOMPLIANT`) e sem campo de nota, que o `judgeReport` continua sendo dos Juízes, que
só Jeremias autoriza exceção, e que o Diretor reconhece este Departamento como operacional. Se o
outro lado mudar, este caso quebra aqui.

**Artefatos internos aceitos (7 casos).** As três `AUDIT_TASK` (uma por capacidade),
`AUDIT_RECEIPT`, `CONFORMITY_MATRIX`, `AUDIT_CAPABILITY_GAP` e `AUDIT_LEDGER`.

**Casos negativos — tarefa (5).** Capacidade trocada para o agente; custódia com
`access_mode: read-write`; emissão com conflito de independência; `forbidden_context` sem a
proibição explícita de conclusão esperada; retorno fora da gerente.

**Casos negativos — recibo (7).** Estado fora dos cinco; `NAO_APLICAVEL` genérico; `CONFORME` sem
evidência; `NAO_PROVADO` sem evidência (aceito, é legítimo); `BLOCKED` com motivo (aceito);
`BLOCKED` sem motivo; achado `BLOCKER` rebaixado para `blocking: false`.

**Casos negativos — matriz (2).** Nove dimensões em vez de dez; dimensão duplicada.

**Casos negativos — livro-razão (11).** `COMPLIANT` com violação registrada; `NONCOMPLIANT` sem
violação; binário divergente do veredito interno; `APROVADO_COM_RESSALVAS` sem ressalva registrada;
`APROVADO` com ressalva pendurada; veredito positivo com lacuna aberta; veredito positivo com
dossiê incompleto; veredito positivo sem registro de emissão (condição de R6); `pending` sem R6;
retorno fora do Diretor. Mais os dois positivos legítimos — `REPROVADO` com violação e
`APROVADO_COM_RESSALVAS` com ressalva.

**Fronteira com os consumidores (7).** O `AUDIT_LEDGER` interno é convertido mecanicamente em
`GOVERNANCE_REPORT` e em `DEPARTMENT_RETURN`, e cada um é validado **contra o schema do
consumidor** — não contra o próprio. O CEO aceita os dois vereditos legítimos e rejeita `COMPLIANT`
com violação, `NONCOMPLIANT` sem violação e relatório **com campo de nota**; o Diretor aceita o
retorno e rejeita produtor forjado.

**Consolidação e veredito recalculados em código (16).** Sem consultar o campo declarado: o estado
**mais grave** vence entre dois inspetores; `NAO_PROVADO` vence `RESSALVA`; `CONFORME` vence
`NAO_APLICAVEL`; dez conformes aprovam; uma ressalva aprova com ressalvas; **uma** não conformidade
reprova; **um** não provado reprova como não conformidade; nove conformes **não compensam** uma
bloqueada; a tradução binária é determinística; os **três** estados internos da RI-05 existem; cada
dimensão bloqueada vira exatamente uma violação; cada ressalva vira pendência **com dono**; e o
`test_summary` do retorno é `0/0/0` — a Auditoria não executa teste.

## O que ainda não foi provado

### Estado vigente das obrigações — conferido em 2026-08-08

> **A auditoria independente e o parecer dos Juízes não estão pendentes.** A campanha [`remedicao-dos-sete-2026-08-03`](../../../../evals/remedicao-dos-sete-2026-08-03/PLACAR.md) executou as duas sobre este pacote. O texto dos itens abaixo é registro da rodada em que foi escrito e fica como está.

| obrigação | estado em 2026-08-08 | quem emitiu |
|---|---|---|
| Auditoria independente | **EXECUTADA** em 2026-08-03 · `governance_report` **NONCOMPLIANT** · **6 achados** nomeados | `departamento-auditoria-responsabilidades`, por instância externa a este pacote |
| Parecer dos Juízes | **EMITIDO** em 2026-08-03 · **REPROVED** · **falha crítica nomeada** · `minimum_score` **5**, faixa **5–5** · **3 de 8** critérios `NAO_DISCRIMINADO` | `departamento-juizes` |

> **Este é o único dos sete cuja faixa fecha firme** (`lo = hi`). Nos outros seis ela atravessa o corte 6/7, e foi por isso que o conserto começou por aqui: não depende de esperar régua melhor.

### Dono e condição de fechamento, item a item

> Exigido pelos achados `CA-01` e `GR-01`/`GR-02` da remedição de 2026-08-03: pendência declarada sem dono é pendência de ninguém. "O próprio Departamento" significa o pacote que este placar mede — ele responde pela própria evidência.

| item | dono | fecha quando |
|---:|---|---|
| 1 | — | já fechado no próprio texto, com data |
| 2 | o próprio Departamento | a `lente-auditor-responsabilidades` for avaliada nos mesmos cenários, ou este item registrar a decisão de não comparar, com motivo |
| 3 | `diretor-de-lentes` | o Diretor designar instância externa para auditar este pacote — ele não se audita, e por isso o dono do fechamento não pode ser ele mesmo |
| 4 | o próprio Departamento | houver âncora externa ao pacote que prove a emissão — runtime separado, assinatura fora da árvore ou terceiro que não compartilhe o processo. Depende das tarefas 50 e 57 |
| 5 | o próprio Departamento | a procedência da evidência for recomputável além do digest, ou o limite `R4` for aceito explicitamente, com dono e data |


Declarado como `SKIP` com motivo — prova executada > checklist, e sucesso simulado é violação
(RI-04):

1. **Forward comportamental — EXECUTADO; esta seção estava vencida.** Corrigido em 2026-07-26: o
   texto anterior afirmava que os 16 prompts **não** foram executados, mas o
   [FORWARD-TEST.md](FORWARD-TEST.md) registra **15 de 16 casos e 58/60 asserções PASS**, e a tabela
   mecânica desta mesma página já declarava a execução. A seção criada para não esconder ausência de
   prova estava negando prova existente.

   *Correção de 2026-07-27, segunda passada:* a primeira redação desta linha dizia que as 2
   asserções falhadas e o caso não rodado "não estavam inventariados". **Estavam** — o
   [FORWARD-TEST.md](FORWARD-TEST.md) traz a seção "O padrão que o instrumento não previu", com o
   diagnóstico e uma ação sugerida. O erro foi meu, ao corrigir a contradição anterior sem reler o
   forward.

   O que **de fato** continua aberto, já diagnosticado no forward: as **2 asserções são defeito do
   instrumento**, não da skill. Os prompts do catálogo são pedidos crus do usuário, e o contrato
   deste Departamento exige `DEPARTMENT_MISSION` vinda do `diretor-de-lentes` — então todas as
   instâncias bloquearam corretamente no portão de canal, e as asserções que descrevem
   comportamento *depois* do portão ficam parcialmente inalcançáveis. O forward é explícito: *"não
   é falha da skill — é o contrato funcionando"*. O **caso 1 é inválido por especificação**.

   A ação sugerida pelo próprio forward é separar o catálogo em **casos de portão** (pedido cru) e
   **casos de operação** (com `DEPARTMENT_MISSION` completa no prompt). Hoje mistura os dois — e o
   mesmo padrão aparece em mais quatro pacotes; ver o achado sistêmico no
   `PLANO-DE-ACAO-2026-07-27.md`, frente 2. O **acionamento** segue sem prova: os prompts rodaram
   sob carga explícita, então está medida a aderência ao contrato, não o disparo espontâneo.
2. **Baseline do pacote legado.** A `lente-auditor-responsabilidades` não foi avaliada contra os
   mesmos cenários. O que está provado por leitura de schema é que o legado produz uma nota que o
   `governanceReport` do CEO não tem onde receber; que a migração **melhora o comportamento**
   permanece não medido.
3. **Auditoria independente deste pacote.** Continua pendente, e agora por um motivo específico:
   **este Departamento não audita a si próprio**. Quem o auditar tem de ser instância externa, e o
   `departamento-juizes` julga a qualidade da auditoria, não a conformidade do próprio auditor.
4. **Existência do painel auditor em runtime (R6).** O validador confere a **matriz** e a
   **estrutura**, nunca a **execução**: um `AUDIT_LEDGER` internamente coerente é reproduzível mesmo
   sem nenhuma `AUDIT_TASK` emitida. A condição de veredito positivo exigir registro de emissão
   encarece a fabricação; não a impede.
5. **Custódia autodeclarada (R4).** `collected_by`, `collected_at` e `handed_at` são escritos por
   quem entrega a evidência. Só o digest é recomputável. Procedência declarada não é procedência
   provada, e nenhuma regra deste pacote fecha isso.

## Efeito sobre a estrutura

Com a Auditoria migrada, a `EXECUTIVE_SUBMISSION` do CEO passa a ter os **dois** insumos que seu
schema exige: `governance_report` (deste Departamento) e `judge_report` (dos Juízes). Antes, o
`governance_report` não tinha produtor no caminho canônico.

Continuam faltando **quem produza as demais classes de entrega**: os oito Departamentos
operacionais restantes. Enquanto não existirem, o Diretor segue falhando fechado com
`DIRECTOR_CAPABILITY_GAP` para cada frente aplicável, e o pacote legado permanece intacto como
rollback manual — nunca como fallback automático.
