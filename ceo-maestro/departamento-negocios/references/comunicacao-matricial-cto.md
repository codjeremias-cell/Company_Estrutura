# Comunicação Matricial com o Diretor de Lentes

## 1. Natureza

`departamento-negocios` e `diretor-de-lentes` são pares. A matriz é um canal temporário autorizado pelo CEO, não uma subordinação.

## 2. Pré-condições cumulativas

A `EXECUTIVE_MISSION` precisa:

1. ser produzida pelo `ceo-maestro`;
2. listar os dois papéis em `recipients`;
3. declarar `matrix_exchange.allowed: true`;
4. delimitar `topics`, `read_scope` e `write_scope`;
5. fixar `consolidation_owner`.

Se uma condição falhar, não enviar mensagem direta. Emita `BUSINESS_RETURN` ao CEO pedindo missão revisada.

## 3. Envelope compatível

Use exatamente:

```yaml
artifact_type: MATRIX_EXCHANGE_MESSAGE
matrix_message_id: mx-...
causal:
  work_item_id: work-...
  front_id: front-...
  handoff_id: handoff-...
  message_id: message-...
  causation_message_ids: [message-gap-ou-julgamento-...]
  contract_id: contract-...
  contract_version: 1
  contract_digest: "sha256:<64 hex>"
  candidate_digest: n/a
  round: 1
  attempt: 1
  producer: departamento-negocios
  producer_version: 1.0.0
  producer_digest: "sha256:<64 hex>"
  created_at: "2026-07-26T12:00:00Z"
executive_mission_ref: mission-...
required_level: INTERNO
sender: departamento-negocios
recipient: diretor-de-lentes
topic: "..."
read_scope: ["..."]
write_scope: ["..."]
consolidation_owner: departamento-negocios
decision_requested: "..."
evidence_refs:
  - evidence-...
sent_at: "2026-07-26T12:00:00Z"
```

O emissor deve ser o produtor causal. `sender` e `recipient` precisam ser opostos. Os escopos, o
dono da consolidação e o `required_level` precisam coincidir com a missão. Nível ausente ou
divergente bloqueia.

O cabeçalho causal da mensagem preserva o contrato da `EXECUTIVE_MISSION`, inclusive `candidate_digest: n/a`. O digest real do candidato fica no `BUSINESS_JUDGMENT_PACKAGE` e nas evidências referenciadas; não substitui o digest causal da missão na mensagem matricial.

`causation_message_ids` aponta para o artefato que motivou a troca: `BUSINESS_GAP_REPORT` no tratamento abaixo do corte ou `BUSINESS_JUDGMENT_PACKAGE` no gate independente. Referenciar apenas a missão do CEO, sem o pai imediato, não basta.

## 4. Usos permitidos

- pedir avaliação de viabilidade técnica sem escolher solução;
- informar restrições, custo-alvo e critério de aceite;
- pedir tratamento de dependência técnica que reduziu o score;
- entregar `BUSINESS_JUDGMENT_PACKAGE` para o Diretor abrir o julgamento vigente;
- receber o veredito ou o estado técnico correlacionado, preservando o mesmo `required_level`.

## 5. Usos proibidos

- comandar Departamento ou agente do Diretor;
- escolher arquitetura, stack, banco ou provedor;
- ampliar escopo, orçamento ou risco aceito;
- falar de tópico fora da missão;
- mudar `consolidation_owner`;
- usar a matriz como autorização para efeito externo;
- enviar `JUDGMENT_REQUEST` aos Juízes.

## 6. Divergência

Quando Negócios e Diretor discordarem, registre as duas posições, evidências, impacto e decisão necessária. O proprietário da consolidação integra; decisão de prioridade, escopo, orçamento ou risco volta ao CEO.
