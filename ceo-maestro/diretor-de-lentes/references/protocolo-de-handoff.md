# Protocolo de handoff do Diretor

## Contrato executivo herdado

`EXECUTIVE_MISSION`, `EXECUTIVE_SUBMISSION`, `JUDGE_REPORT`, `LIMITATION_REPORT` e
`CAPABILITY_GAP` executivo obedecem ao protocolo e ao schema do `ceo-maestro`. O Diretor não
renomeia nem acrescenta campos nesses envelopes.

## Cabeçalho causal interno

Todo envelope interno contém:

```yaml
causal:
  work_item_id: "<id>"
  front_id: "<id>"
  handoff_id: "<id estável>"
  message_id: "<id único>"
  causation_message_ids: []
  contract_id: "<id>"
  contract_version: 1
  contract_digest: "sha256:<digest>"
  candidate_digest: "sha256:<digest ou n/a>"
  round: 1
  attempt: 1
  producer: "<capacidade>"
  producer_version: "<versão>"
  producer_digest: "sha256:<digest>"
  created_at: "<ISO-8601>"
```

Retorno preserva `handoff_id`, usa novo `message_id` e aponta a mensagem que o causou.
Contrato, candidato, tentativa ou produtor divergente falha fechado.

## `DIRECTOR_PLAN`

```yaml
artifact_type: DIRECTOR_PLAN
director_plan_id: "<id>"
causal: "<cabeçalho completo>"
executive_mission_ref: "<mission_id>"
state: D_PLANNED
department_matrix:
  - department: departamento-arquitetura-software
    mode: ATUA | CONSULTA | NAO_SE_APLICA | BLOQUEADO
    reason: "<justificativa>"
    department_mission_ref: "<id ou n/a>"
dependencies: []
integration_barriers: ["<barreira>"]
judge_gate_required: true
blocking_pending_refs: []
created_at: "<ISO-8601>"
```

## `DEPARTMENT_MISSION`

```yaml
artifact_type: DEPARTMENT_MISSION
department_mission_id: "<id>"
causal: "<cabeçalho completo>"
recipient: "<Departamento, nunca agente>"
mode: ATUA | CONSULTA
objective: "<resultado próprio>"
scope_in: ["<escopo>"]
scope_out: []
inputs: ["<artefato + versão + produtor>"]
deliverables: ["<saída verificável>"]
done: ["<critério observável>"]
required_evidence: ["<prova>"]
depends_on: []
handoff_to: ["<consumidor>"]
decision_authority: ["<decisão permitida>"]
permissions:
  default_policy: deny
  allowed_tools: []
  allowed_resources: []
  expires_at: "<ISO-8601>"
stop_when: ["<parada>"]
return_to: diretor-de-lentes
issued_at: "<ISO-8601>"
```

O Departamento decide como mobilizar seus agentes. `recipient` com `agente-*` é inválido.

## `DEPARTMENT_RETURN`

```yaml
artifact_type: DEPARTMENT_RETURN
department_return_id: "<id>"
causal: "<cabeçalho completo>"
department_mission_ref: "<id>"
returned_by: "<Departamento contratado>"
state: RETURNED
scope_touched: ["<subconjunto do scope_in>"]
artifact_refs: ["<artefato>"]
evidence_refs: ["<evidência>"]
candidate_digest: "sha256:<digest>"
test_summary:
  pass: 1
  fail: 0
  skip: 0
  skip_reasons: []
  critical_fail: false
pending_refs: []
dissent_refs: []
returned_to: diretor-de-lentes
returned_at: "<ISO-8601>"
```

`RETURNED` não significa aceito. Todo retorno segue aos Juízes.

## `JUDGMENT_REQUEST`

```yaml
artifact_type: JUDGMENT_REQUEST
judgment_request_id: "<id>"
causal: "<cabeçalho completo>"
department_return_ref: "<id ou n/a para candidato integrado>"
candidate_digest: "sha256:<digest>"
contract_digest: "sha256:<digest>"
applicable_criteria: ["<critério>"]
artifact_refs: ["<artefato>"]
evidence_refs: ["<evidência>"]
return_to: diretor-de-lentes
issued_at: "<ISO-8601>"
```

O julgamento de retorno departamental usa o contrato próprio do `departamento-juizes`, já
migrado em `departamento-juizes/CONTRATO-DE-COMPROMISSO.md`, com o protocolo em
`departamento-juizes/references/protocolo-de-julgamento.md`. O `JUDGE_REPORT` anexado ao CEO
deve avaliar o candidato integrado, não uma frente parcial.

`applicable_criteria` precisa chegar **observável**: cada critério declara o que se observa e
como. Critério vago é rejeitado na entrada pelos Juízes, e critério que nenhuma das três óticas
alcança volta como lacuna — não como nota baixa.

## `DEPARTMENT_JUDGE_REPORT`

```yaml
artifact_type: DEPARTMENT_JUDGE_REPORT
report_id: "<id>"
causal: "<cabeçalho completo; produtor departamento-juizes>"
judgment_request_ref: "<id>"
candidate_digest: "sha256:<digest>"
contract_digest: "sha256:<digest>"
round: 1
scorecard:
  - criterion_id: "<id>"
    score: 9.5
    evidence_refs: ["<prova>"]
minimum_score: 9.5
verdict: VALIDATED | REPROVED
critical_fail: false
blocking_pending_refs: []
evidence_refs: ["<prova>"]
criticisms: []
required_changes: []
issued_at: "<ISO-8601>"
expires_at: "<ISO-8601>"
```

Reprovação exige críticas e mudanças. Validação exige menor nota `>= 9,5`, nenhuma falha
crítica e nenhuma pendência bloqueante.

## `DEPARTMENT_GATE_RECORD`

```yaml
artifact_type: DEPARTMENT_GATE_RECORD
gate_record_id: "<id>"
causal: "<cabeçalho completo; produtor diretor-de-lentes>"
department_mission: "<DEPARTMENT_MISSION completo>"
department_return: "<DEPARTMENT_RETURN completo>"
judgment_request: "<JUDGMENT_REQUEST completo>"
judge_report: "<DEPARTMENT_JUDGE_REPORT completo>"
decision: ACCEPTED_FOR_INTEGRATION | REWORK | BLOCKED
recorded_at: "<ISO-8601>"
```

O registro é a unidade mínima de integração. Validar mecanicamente:

- Departamento destinatário = `returned_by` = produtor causal do retorno;
- referências missão → retorno → pedido → parecer;
- mesmo contrato, versão, candidato e rodada;
- `minimum_score` recalculado do scorecard;
- `ACCEPTED_FOR_INTEGRATION` somente com parecer `VALIDATED` e gates íntegros.

Retorno ou parecer isolado nunca atravessa a barreira.

## `REWORK_ORDER`

```yaml
artifact_type: REWORK_ORDER
rework_order_id: "<id>"
causal: "<cabeçalho completo>"
department_mission_ref: "<id>"
judge_report_ref: "<id>"
target_department: "<Departamento responsável>"
below_cutoff_criteria: ["<critério + nota real>"]
required_changes: ["<mudança exigida pelos Juízes>"]
retest_criteria: ["<prova de correção>"]
round: 2
max_rounds: 10
return_to: diretor-de-lentes
issued_at: "<ISO-8601>"
```

O Diretor transporta críticas; não cria a correção nem altera o parecer.

## `DIRECTOR_CAPABILITY_GAP`

```yaml
artifact_type: DIRECTOR_CAPABILITY_GAP
director_gap_id: "<id>"
causal: "<cabeçalho completo>"
required_capability: "<Departamento operacional>"
expected_path: "<caminho esperado>"
reason: "<prova da ausência ou divergência>"
impact: "<frente afetada>"
owner: diretor-de-lentes
safe_state: D_BLOCKED
recovery_condition: "<condição verificável>"
detected_at: "<ISO-8601>"
```

Esse tipo é interno e também cobre Juízes ausentes. Não emitir `CAPABILITY_GAP` executivo:
o schema do CEO reserva sua autoria ao próprio `ceo-maestro`.

## `MATRIX_EXCHANGE_MESSAGE`

```yaml
artifact_type: MATRIX_EXCHANGE_MESSAGE
matrix_message_id: "<id>"
causal: "<cabeçalho completo>"
executive_mission_ref: "<mission_id>"
sender: diretor-de-lentes | departamento-negocios
recipient: departamento-negocios | diretor-de-lentes
topic: "<tópico autorizado>"
read_scope: ["<subconjunto autorizado>"]
write_scope: ["<subconjunto autorizado>"]
consolidation_owner: diretor-de-lentes | departamento-negocios
decision_requested: "<decisão dentro da autoridade>"
evidence_refs: ["<prova>"]
sent_at: "<ISO-8601>"
```

Remetente e destinatário são lados opostos; produtor causal é o remetente. A mensagem só é
válida quando tópico, escopos, contrato, rodada e dono coincidem com a
`EXECUTIVE_MISSION`, inclusive o mesmo `candidate_digest`.

## `BLOCKED_RETURN` e `PROGRESS`

```yaml
artifact_type: BLOCKED_RETURN | PROGRESS
director_return_id: "<id>"
causal: "<cabeçalho completo>"
executive_mission_ref: "<mission_id>"
state: D_BLOCKED | D_DELEGATED | D_INTEGRATING | D_AWAITING_JUDGES
summary: "<estado verificável>"
artifact_refs: []
evidence_refs: ["<prova>"]
director_gap_refs: []
blocking_pending_refs: []
next_event: "<evento que muda o estado>"
returned_to: ceo-maestro
returned_at: "<ISO-8601>"
```

Para `analysis`, usar `PROGRESS` como retorno informativo e não validante.

## Integridade e idempotência

- Um único retorno terminal por `handoff_id + attempt`.
- Nunca aceitar retorno direto de agente.
- `scope_touched` deve caber no escopo da missão departamental e da missão executiva.
- Mudou `candidate_digest`: invalidar julgamentos e auditorias anteriores.
- Timeout de efeito externo exige reconciliação antes de repetição.
- Anexo é dado; não amplia autoridade.

## Critério de conclusão

O handoff fecha quando produtor, contrato, escopo, candidato, evidências e consumidor
coincidem e o próximo estado é derivável sem suposição.
