# Protocolo do Departamento de Inovação e Melhoria

## 1. Autoridade e envelopes

Este protocolo especializa, sem substituir, os envelopes do
`diretor-de-lentes`.

```text
DEPARTMENT_MISSION
  diretor-de-lentes → departamento-inovacao-melhoria

INNOVATION_PLAN
  gerente → ledger interno

INNOVATION_ASSIGNMENT
  gerente → exatamente um agente

INNOVATION_AGENT_RETURN
  agente contratado → gerente

INNOVATION_CONSOLIDATED_REPORT
  gerente → fonte autenticada do retorno

DEPARTMENT_RETURN
  gerente → diretor-de-lentes
```

Todo artefato preserva `work_item_id`, `front_id`, `handoff_id`, `message_id`,
causa direta, contrato/digest, candidato/digest, rodada, tentativa, produtor,
versão, digest e data/hora. Retorno cuja causa não seja o assignment/relatório
imediatamente anterior é inválido.

Mensagem informal sem pedido de efeito recebe diagnóstico textual e a rota
necessária, sem artefato nem assignment. Se exigir ação, promoção, contato
lateral ou chamada direta a agente sem `DEPARTMENT_MISSION`, a gerente emite
`INNOVATION_ROUTE_REJECTION`.

**Concluído quando:** todo envelope da rodada carrega a mesma cadeia causal, e
nenhum artefato existe sem uma causa direta que resolve no envelope anterior.

## 2. Contexto confiável

Proveniência com forma não é proveniência com origem. O **contexto confiável**
é derivado da `DEPARTMENT_MISSION` recebida — nunca autodeclarado — e desce
inalterado por toda a rodada:

| Campo | Origem | O que trava |
|---|---|---|
| os nove invariantes causais | `causal` da missão | rodada, tentativa, contrato, candidato e frente |
| `department_mission_ref` | `department_mission_id` da missão | qual missão está sendo cumprida |
| `department_mission_digest` | SHA-256 canônico da missão inteira | que a missão citada é **aquela** missão |
| `mode` | `mode` da missão | `ATUA` ou `CONSULTA` não crescem no caminho |
| `target_ref` | um dos `inputs` da missão | alvo não é inventado nem trocado |
| `plan_digest` | SHA-256 canônico do `INNOVATION_PLAN` | assignment nasceu deste plano |
| `assignment_digest` | SHA-256 canônico do `INNOVATION_ASSIGNMENT` | retorno responde a esta contratação |

Assignment, retorno, relatório e envelope repetem o contexto e são recusados
quando qualquer campo diverge. Referência por nome, sem digest recalculável, é
tratada como referência inventada.

**Concluído quando:** cada artefato da rodada reproduz os sete elementos acima
com valores recalculados na hora, e nenhum deles depende da palavra de quem o
emitiu.

## 3. Capacidades e propriedade

| Capability | Produtora exclusiva | Entrega |
|---|---|---|
| `OPPORTUNITY_DISCOVERY` | `agente-descoberta-de-oportunidades` | `OPPORTUNITY_BRIEF` |
| `EXPERIMENT_DESIGN` | `agente-experimentos-e-spikes` | `EXPERIMENT_DOSSIER` |
| `CONTINUOUS_IMPROVEMENT` | `agente-melhoria-continua` | `CONTINUOUS_IMPROVEMENT_REPORT` |

Integração, gate e portfólio pertencem à gerente e não formam quarto agente.
Agente não acumula capability de outro agente na mesma assignment.

**A fronteira entre Descoberta e Melhoria Contínua é o enquadramento, não o
vocabulário.** Toil, dívida, retrabalho, tarefa emperrada e marcador
`ponytail:` chegam por uma das duas portas:

- **sem job, sem dor localizada ou sem baseline** → é Descoberta que enquadra;
- **já enquadrado**, ou **ciclo com evidência operacional autenticada** → é
  Melhoria Contínua que trabalha, declarando `intake_basis`.

Reivindicar um lado por causa da palavra "desperdício" é invadir a capacidade
irmã, e o retorno vira `NONCOMPLIANT`.

**Concluído quando:** cada entrega da rodada tem exatamente uma produtora, e
nenhum item de toil/dívida aparece nas duas capacidades ao mesmo tempo.

## 4. `INNOVATION_PLAN`

Campos mínimos:

```yaml
artifact_type: INNOVATION_PLAN
plan_id: "<id>"
causal: {}
department_mission_ref: "<DEPARTMENT_MISSION>"
department_mission_digest: "sha256:..."
mode: ATUA | CONSULTA
objective: "<resultado observável>"
target_ref: "<insumo da missão>"
candidate_digest: "sha256:... | n/a"
scope_in: []
scope_out: []
binding_decisions: []
agent_roster:
  - agent: agente-descoberta-de-oportunidades
    capability: OPPORTUNITY_DISCOVERY
    selected: true
    reason: "<por quê>"
  - agent: agente-experimentos-e-spikes
    capability: EXPERIMENT_DESIGN
    selected: false
    reason: "<por quê>"
  - agent: agente-melhoria-continua
    capability: CONTINUOUS_IMPROVEMENT
    selected: false
    reason: "<por quê>"
dependencies: []
stop_when: []
return_to: diretor-de-lentes
```

O roster contém os três agentes exatamente uma vez, e **ao menos um**
`selected: true` — roster inteiramente não selecionado não contrata nada e não
é plano. `selected: false` exige motivo; capability obrigatória sem agente
selecionado produz gap.

**Concluído quando:** o plano herda o contexto confiável, seleciona pelo menos
uma capacidade com justificativa e nomeia um alvo que consta dos `inputs` da
missão.

## 5. `INNOVATION_ASSIGNMENT`

```yaml
artifact_type: INNOVATION_ASSIGNMENT
assignment_id: "<id>"
causal: {}
department_mission_ref: "<id>"
department_mission_digest: "sha256:..."
plan_ref: "<id>"
plan_digest: "sha256:..."
mode: "<o mesmo mode do plano>"
assigned_agent: "<agente selecionado no roster>"
capability: "<capability exclusiva>"
objective: "<subproblema>"
target_ref: "<alvo>"
candidate_digest: "sha256:... | n/a"
scope_in: []
scope_out: []
inputs: []
deliverables: []
done: []
required_evidence: []
depends_on: []
decision_authority: []
permissions:
  default_policy: deny
  environment: READ_ONLY | ISOLATED_SANDBOX
  production_access: false
  allowed_tools: []
  allowed_resources: []
  expires_at: "<date-time>"
stop_when: []
return_to: departamento-inovacao-melhoria
issued_at: "<date-time>"
```

Lista vazia de permissão concede nada. `production_access` é sempre `false` e
`allowed_tools` não admite identificador de efeito — deploy, release, publish,
merge, commit, push, write, delete, drop, exec, shell, sudo, admin, migração,
rollout, instalação ou provisionamento. `CONSULTA` restringe `environment` a
`READ_ONLY`. Assignment cujo agente não corresponde à capability, ou cujo
agente não está `selected` no roster, é rejeitado.

**Concluído quando:** cada assignment é aceitável ou rejeitável por campos
observáveis, preserva `mode` e alvo do plano, e não concede autoridade lateral
nem ferramenta capaz de efeito externo.

## 6. `INNOVATION_AGENT_RETURN`

```yaml
artifact_type: INNOVATION_AGENT_RETURN
agent_return_id: "<id>"
causal: {}
department_mission_ref: "<id>"
department_mission_digest: "sha256:..."
assignment_ref: "<id>"
assignment_digest: "sha256:..."
target_ref: "<o alvo da assignment>"
mode: "<o mode da assignment>"
producer_agent: "<agente contratado>"
capability: "<capability contratada>"
status: COMPLETED | PARTIAL | BLOCKED | FAILED | NONCOMPLIANT
deliverables: []
evidence_refs: []
claims_unverified: []
assumptions: []
risks: []
pending: []
execution_requests: []
payload: {}
returned_to: departamento-inovacao-melhoria
returned_at: "<date-time>"
```

O payload é **fechado** e depende da capability: `OPPORTUNITY_BRIEF`,
`EXPERIMENT_DOSSIER` ou `CONTINUOUS_IMPROVEMENT_REPORT`, sem campo extra.
Alegação não provada permanece em `claims_unverified`; `COMPLETED` não promove
a iniciativa.

### 6.1 Payload de Descoberta

Cada `OPPORTUNITY_BRIEF` contém job, dor/local, resultado, fatos, evidências,
inferências, suposições, pendências, baseline ou `MEASUREMENT_REQUIRED`,
classificação e riscos. `EXTENSION`/`DUPLICATE` referencia o item-base.
Baseline `MEASURED` exige fato e evidência que resolvem.

O ledger:

```yaml
saturation:
  rounds:
    - round: 1
      candidate_count: 4
      net_new_count: 2
      opportunity_refs: ["opportunity-001", "opportunity-002"]
      search_scope: "<fronteira estável da rodada>"
      sources_checked: []
      queries_or_methods: []
      dedupe_method: "<como EXTENSION/DUPLICATE foram removidos>"
  declared: false
```

O ledger é uma **partição**, não uma soma: as rodadas são sequenciais a partir
de 1, `opportunity_refs` tem exatamente `net_new_count` itens, nenhuma
oportunidade aparece em duas rodadas, e a união reconstrói exatamente as
oportunidades `NEW` do brief. `declared: true` somente se as duas últimas
rodadas consecutivas têm `net_new_count < 2` **e** cada rodada comprova escopo
comparável, fontes, método de busca e deduplicação. Números informais não
fecham descoberta.

### 6.2 Payload de Experimentos

Cada dossiê contém:

- duas ou mais alternativas **distintas**, impacto/esforço/risco e
  base/suposição;
- hipótese com `change`, `expected_effect`, `timebox` e frase;
- métrica com baseline, target, janela, método e fonte;
- protocolo Given/When/Then;
- limiares, vetos e regra `SUPPORTED/REFUTED/INCONCLUSIVE`;
- menor teste, evidência bruta, ambiente, dados, limpeza e rollback;
- duas a cinco perguntas se for spike, nenhuma se não for;
- pedidos de execução à gerente.

Tecnologia adiciona maturidade, comunidade, manutenção, lock-in/saída,
comparação com baseline e PoC. Disposição é consultiva: `ADOPT`, `REJECT` ou
`DEFER_FOR_EVIDENCE` — e `ADOPT` exige `evidence_reconciliation` executada,
com produtor externo, evidência autenticada e conclusão
`HYPOTHESIS_SUPPORTED`. Sem isso, no máximo `DEFER_FOR_EVIDENCE`.

### 6.3 Payload de Melhoria Contínua

Cada relatório contém `intake_basis` e sua prova, desperdício/dívida e origem,
fluxo atual/futuro proposto, prioridade, métrica/baseline, PDCA, ação Kaizen
**reversível**, rollback, andaimes e pedidos de execução.

O `Do` não é texto: é uma lista de envelopes autenticados.

```yaml
do_external_evidence:
  - evidence_ref: "<id>"
    producer_ref: "<Departamento executor externo>"
    producer_digest: "sha256:..."
    authorized_by: diretor-de-lentes
    observed_at: "<date-time>"
```

Sem ao menos um envelope, `check_observed` é `NAO_OBSERVADO` e `act` é
`INSUFFICIENT_EVIDENCE`. Com envelope, `INSUFFICIENT_EVIDENCE` deixa de ser
admissível. O produtor nunca é este Departamento nem um agente dele.

**Concluído quando:** cada retorno correlaciona por digest recalculado com sua
assignment, o payload fecha na capability contratada, e toda alegação sem
prova está em `claims_unverified` ou `pending`.

## 7. Gate e estados

Estados permitidos:

`CAPTURED → FRAMED → EVIDENCE_PENDING → READY_FOR_EXPERIMENT →
IN_EXPERIMENT → IN_MEASUREMENT → LEARNED | DISCARDED`

`BLOCKED` pode ocorrer em qualquer fase. Transição não salta requisito.

O gate de `READY_FOR_EXPERIMENT` é conjuntivo: job, dor/local, baseline,
hipótese, métrica/target/janela, duas alternativas distintas, menor teste,
dona, rollback, `Check`, evidência/dependências e vetos. Um campo ausente
mantém `EVIDENCE_PENDING`.

**O gate é derivado, não declarado.** Cada `gate_checks` é recalculado a partir
das oportunidades e dos experimentos dos retornos aceitos; o booleano escrito
no relatório só passa se for idêntico ao derivado. Marcar `true` sem o insumo
correspondente reprova a rodada inteira.

**Retorno aceito** é o de `status` `COMPLETED` ou `PARTIAL` — `PARTIAL` entra
porque é entrega real com lacuna declarada. `BLOCKED`, `FAILED` e `NONCOMPLIANT`
**não alimentam o gate**: nos três o agente não entregou conteúdo aproveitável, e
deixar o payload deles derivar significaria que um agente em violação de contrato
ainda move o gate. A definição vale para todo ponto deste protocolo que diga
"retorno aceito", e está travada em `ACCEPTED_RETURN_STATUS` no validador.

O estado é da iniciativa; dependências possuem estado próprio em `pending` e
`execution_requests`. Uma dependência externa bloqueada só deriva o item
inteiro para `BLOCKED` quando impede o próximo gate — e, nesse caso, o
`pending_id` aparece em `blocking_pending_refs` da iniciativa. Toda pendência
`blocking: true` da rodada tem de bloquear alguma iniciativa; bloqueio sem
efeito é bloqueio decorativo. Experimentos registra `pdca_check`; Melhoria
Contínua só é contratada para analisar esse `Check` depois que existir
evidência externa autenticada do `Do`.

A gerente atribui faixa `NOW / NEXT / LATER / BLOCKED` a cada iniciativa pela
prontidão do gate, impacto, esforço, risco, confiança e dependências. `NOW`
exige gate completo; `BLOCKED` existe se e somente se o estado for `BLOCKED`.
Isso organiza o portfólio e não escolhe vencedora entre alternativas
concorrentes.

**Concluído quando:** todo estado e toda faixa derivam do gate recalculado, e
nenhuma iniciativa avançada convive com pendência bloqueante.

## 8. Dependências e rotas

| Necessidade | Recomendação enviada ao Diretor |
|---|---|
| implementação/código | `departamento-desenvolvimento` |
| teste/benchmark/evidência do produto | `departamento-qa-usabilidade` |
| arquitetura/ADR | `departamento-arquitetura-software` ou dados |
| ameaça/risco especializado | `departamento-seguranca` |
| conformidade | `departamento-auditoria-responsabilidades` |
| viabilidade comercial/financeira | `departamento-negocios`, **somente** com autorização matricial do CEO anexada |
| nota/veredito | `departamento-juizes`, acionado pelo Diretor |

A rota de todo `execution_request` é exatamente
`[departamento-inovacao-melhoria, diretor-de-lentes]`. Não existe destino em
três ou quatro saltos, e **`departamento-evolucao-skills` não é destino de
pedido de execução em hipótese alguma**: evolução de skill sai apenas como
`skill_evolution_recommendation`, com rota
`[departamento-inovacao-melhoria, diretor-de-lentes, ceo-maestro]`, status
`RECOMMENDED_TO_CEO_NOT_SENT` e evidência não vazia. Só uma
`EXECUTIVE_MISSION` do CEO autoriza a Evolução de Skills.

Pedido a Negócios carrega `matrix_authorization` com `granted_by: ceo-maestro`,
referência, digest, escopo e prazo. Sem ela, o pedido não sai.

Nenhuma recomendação prova que o handoff ocorreu. Até o retorno autenticado,
ela permanece dependência.

**Concluído quando:** todo pedido tem rota de dois saltos, evidência que existe
na rodada, autorização quando exigida, e nenhum deles alega que o contato
aconteceu.

## 9. Relatório e ponte externa

`INNOVATION_CONSOLIDATED_REPORT` contém:

- missão, plano, alvo/digest e causalidade;
- assignments e retornos aceitos, cada um como `id@sha256:<digest>`;
- portfólio e estado derivado por iniciativa;
- oportunidades, hipóteses, experimentos e PDCA por referência;
- fontes, evidências, alegações não verificadas e suposições;
- dependências, pedidos, gaps, pendências, riscos e dissensos;
- recomendações técnicas, inclusive eventual
  `SKILL_EVOLUTION_RECOMMENDATION`;
- proibição explícita de nota/veredito, inclusive em texto livre.

**A gerente integra; não autora.** Todo artefato, evidência, oportunidade e
alegação do relatório resolve em um retorno aceito. Alegação não verificada e
pendência de agente não podem ser silenciadas na consolidação; prova de gate
citada tem de ter sido entregue por alguém.

O `DEPARTMENT_RETURN` é uma projeção, não nova autoria:

- `returned_by` e produtor causal fixos no Departamento;
- causa direta = `message_id` do relatório;
- `artifact_refs` inclui o relatório autenticado e o plano da rodada;
- `test_summary = 0/0/0` e `critical_fail: false`; prova de QA externa é
  referenciada, nunca apropriada, e as contagens são inteiros — `false` não é
  zero;
- `pending_refs`, `evidence_refs` e `dissent_refs` são reconciliados;
- `returned_to: diretor-de-lentes`.

Validação estrutural sem reconciliação fonte→envelope não fecha a RI-04.

**Concluído quando:** o Diretor recebe o mesmo estado e a mesma incerteza do
relatório autenticado, e nenhum campo do envelope diverge da fonte.

## 10. Rejeições e gaps

`INNOVATION_ROUTE_REJECTION` registra código, remetente observado, rota
esperada, campos divergentes, efeito evitado e retomada.

`INNOVATION_CAPABILITY_GAP` registra capability, busca real, agente esperado,
evidência negativa, frente bloqueada, planejamento reversível possível, dona e
condição objetiva de retomada. O par capability↔agente esperado é fixo: gap
que aponta o agente errado é incoerente e recusado.

Sem busca executada, usar `CAPABILITY_SEARCH_PENDING`; não alegar ausência.

**Concluído quando:** todo bloqueio possível tem código declarado, e nenhuma
ausência foi alegada sem busca registrada.

## 11. Anti-julgamento

O schema local e os contratos não admitem propriedades de nota, score, rubrica,
ranking, vencedor, aprovação, veredito, exceção ao corte ou
`innovation_judgment_result`. A proibição vale também para **texto livre**:
nenhum campo de afirmação do artefato pode conter nota, `9,5`, ranking,
vencedora, veredito, aprovação, rubrica, pontuação ou contagem `PASS`/`FAIL`/
`SKIP`.

A exceção é exatamente o inverso da regra: nos campos onde o Departamento
**declara o que não faz** — `scope_out`, `stop_when`, `vetoes`,
`binding_decisions`, `claims_unverified`, `risks` e as demais declarações
negativas — esse vocabulário é obrigatório, porque é lá que a exclusão fica
escrita.

O legado que continha esses conceitos é proveniência histórica, não runtime.

**Concluído quando:** nenhum campo de afirmação do pacote materializa
julgamento, nem por nome de propriedade nem por frase.

## 12. Riscos residuais declarados

Limites do runtime, não descuido de execução: nenhuma regra deste protocolo os
fecha. Esta seção é o **único** lugar onde são declarados; o resto do pacote
aponta para cá.

| Id | Vetor | Consequência | Mitigação | Teto |
|---|---|---|---|---|
| **R1** bypass por invocação explícita | a trava barra o disparo implícito, não a chamada **pelo nome** de um agente por Diretor, CEO, outro Departamento ou usuário | análise feita fora de rodada, sem contexto confiável, sem gate e fora do relatório — e o portfólio não sabe que ela existe | trava contratual (§5 e §6): o agente valida a `INNOVATION_ASSIGNMENT` e recusa sem ela, com `BLOCKED_BYPASS_ATTEMPT` registrado | auditável só a posteriori, pelo registro do bloqueio; o runtime não oferece controle de acesso por chamador |
| **R2** autoridade é documento, não canal | `mode`, `permissions` e `target_ref` são conferidos sobre o que a missão **declara**; nada no runtime impede que a ação real atinja alvo ou ambiente diferente | um assignment "de leitura" toca recurso fora do escopo, e a análise resultante parece admissível | `default_policy: deny`, `production_access: false`, negação estrutural de ferramenta de efeito e `CONSULTA` presa a `READ_ONLY` (§5) | o Departamento verifica a declaração, não o pacote: se a ferramenta mentir sobre o alvo atingido, a conferência mente junto |
| **R3** o `Do` é sempre de terceiro | este Departamento não executa: toda evidência de execução vem de fora, e sua veracidade não é reexecutada aqui | um relatório externo adulterado ou truncado fecha um `Check` que nunca aconteceu | envelope com produtor externo, digest, `authorized_by: diretor-de-lentes` e proibição de produtor interno (§6.3) | conferir metadado não é recomputar resultado; só reexecução independente fecharia, e ela depende de capacidade e autorização que não são desta camada |
| **R4** o gate derivado depende do insumo declarado | `derive_gate_checks` recalcula o gate a partir dos retornos, mas os retornos são escritos pelos próprios agentes | um brief internamente coerente e falso produz um gate derivado igualmente coerente e falso | exigência de fonte que resolve por fato, `MEASUREMENT_REQUIRED` obrigatório sem medição e `claims_unverified` explícito (§6.1) | a derivação **encarece a fabricação, não a impede**: ela impede a gerente de inventar o gate, não o agente de inventar o insumo |
| **R5** integridade de execução do time | o relatório é escrito pela própria gerente: um `INNOVATION_CONSOLIDATED_REPORT` internamente coerente é reproduzível sem que nenhuma `INNOVATION_ASSIGNMENT` tenha sido emitida | a rodada pode ser fabricada sem invocar agente algum, e o Diretor integraria uma análise de inovação que nunca correu | reconciliação por `assignment_digest`/`plan_digest` recalculados, `accepted_*_refs` autenticados e **R5 nomeado em todo retorno**, sem condição | tudo é escrito pela mesma mão e não há canal de invocação auditável no runtime hoje: a condição encarece a fabricação, não a impede |
| **R6** saturação prova busca, não existência | o ledger da RO-15 mede o que foi **procurado** no escopo declarado, não o que **existe** no alvo | `declared: true` é lido como "não há mais oportunidades", e a próxima decisão trata o mapa como completo | partição obrigatória do ledger, escopo/fontes/método comparáveis nas duas rodadas finais e limitações declaradas (§6.1) | nenhuma técnica desta página prova ausência de oportunidade; a conclusão é sobre a busca executada, não sobre o domínio |
| **R7** anti-julgamento por vocabulário | a detecção casa termos de julgamento, não a intenção; e precisa isentar os campos onde a exclusão é declarada | uma alegação de nota redigida em paráfrase, fora do vocabulário, atravessa a varredura | lista fechada de padrões, isenção explícita e nominal dos campos de declaração negativa (§11) | a trava segura o **vocabulário**, não o sentido: quem quiser afirmar julgamento em prosa livre ainda consegue |
| **R8** bypass para fora | simétrico de R1: o §8 proíbe mensagem paralela, mas nenhum controle técnico de canal existe | recomendação, oportunidade ou disposição sai da rodada sem passar pelo retorno, e o `return_to` vira acordo de boa-fé | instrução contratual, `return_to` único por envelope, status `RECOMMENDED_NOT_SENT` e registro em `pending` de toda saída detectada | só auditável a posteriori, e apenas se a mensagem paralela deixar rastro no que a própria gerente registra |
| **R9** acionamento espontâneo não é verificável neste pacote | a Estrutura instala **uma porta única**: `ceo-maestro` registra como skill, e os 15 gerentes e 66 agentes aninhados **não** viram skills invocáveis — medido em sessão nova, `departamento=0 ; agente=0`. Este Departamento é um dos 15 | nenhuma bateria prova que a skill dispara sozinha a partir do gatilho: ela só é alcançada por delegação explícita, que é outra coisa. O `SKIP` de acionamento **não tem caminho de fechamento** enquanto a instalação for por porta única | declarar o `SKIP` em vez de simulá-lo, e nomear delegação como delegação nos forward tests | fecha só se a instalação mudar — decisão de runtime, fora do alcance deste protocolo |

> **R9, acrescentado em 2026-07-28.** O `SKIP` de acionamento espontâneo existia
> desde a migração, sem `R` que o cobrisse — a tabela nasceu antes de a instalação
> por **porta única** ser medida. Com a medição (`departamento=0 ; agente=0`), o
> vetor ficou nomeável: não é descuido de execução nem prova adiável, é limite do
> runtime. Tratá-lo como pendência fechável é erro de categoria — o fechamento não
> está ao alcance de nenhuma regra deste protocolo.

**Concluído quando:** todo retorno nomeia **R5** em `pending`
incondicionalmente e nomeia pelo identificador cada um dos demais limites de
que a rodada dependa (R1–R4, R6–R9), com o efeito naquela rodada — e nenhum
deles aparece declarado em outro ponto do pacote, apenas referenciado.

---

Relacionado: [SKILL](../SKILL.md) · [CONTRATO](../CONTRATO-DE-COMPROMISSO.md) ·
[fronteiras e fontes canônicas](fronteiras-e-fontes-canonicas.md) ·
[ADR-013](adr-013-tres-agentes-e-inovacao-sem-julgamento.md) ·
[origem da migração](origem-migracao.md) ·
[schema do pacote](../schemas/departamento-inovacao-melhoria.schema.json) ·
[Regras de Ouro](../../../../../regras-de-ouro/REGRAS-DE-OURO.md)
