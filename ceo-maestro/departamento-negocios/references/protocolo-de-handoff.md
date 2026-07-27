# Protocolo de Handoff

## 1. Envelope causal

Todo artefato próprio contém:

- `artifact_type`;
- identificador próprio;
- `causal` com `work_item_id`, `front_id`, `handoff_id`, `message_id`, `causation_message_ids`, `contract_id`, `contract_version`, `contract_digest`, `candidate_digest`, `round`, `attempt`, `producer`, versão/digest do produtor e `created_at`;
- referência à missão e ao candidato nos campos próprios do artefato, fora de `causal`;
- referência ao artefato imediatamente anterior;
- `created_at`;
- `return_to` quando houver destinatário.

O produtor causal deve coincidir com o emissor. Digest, candidato, contrato e rodada não podem mudar silenciosamente.

### Invariantes de integridade da cadeia

- cada `message_id`, `agent_mission_id` e `agent_report_id` é único dentro da cadeia;
- `causation_message_ids` inclui o `message_id` do artefato imediatamente anterior;
- `plan.intake_ref`, `assignment.mission_ref`, `mission.plan_ref`, `report.assignment_ref`, `consolidation.plan_ref` e `scorecard.consolidation_ref` apontam para os artefatos reais;
- intake, plano, missões, relatórios, consolidação e scorecard preservam `work_item_id`, `front_id`, `handoff_id`, contrato, candidato, rodada e tentativa;
- o relatório usa a mesma tentativa da missão; relatório obsoleto é rejeitado;
- `BUSINESS_REWORK_ORDER` referencia o gap real, preserva seu dono, critérios, mudança, reteste e contrato, e avança exatamente uma tentativa;
- os três relatórios e a consolidação cobrem `BIZ-01..BIZ-08` exatamente uma vez, conforme a propriedade canônica;
- toda evidência do scorecard existe no relatório-fonte do critério; referência inventada bloqueia;
- a `EXECUTIVE_MISSION` preserva `candidate_digest: n/a`, mas contrato e rodada global continuam iguais no fluxo de Negócios.

## 2. Artefatos e autoridade

| Artefato | Produzido por | Destino |
|---|---|---|
| `BUSINESS_INTAKE` | `departamento-negocios` | registro interno |
| `BUSINESS_EVALUATION_PLAN` | `departamento-negocios` | time interno |
| `BUSINESS_AGENT_MISSION` | `departamento-negocios` | um agente canônico |
| `BUSINESS_AGENT_REPORT` | agente designado | `departamento-negocios` |
| `BUSINESS_CONSOLIDATION` | `departamento-negocios` | registro interno |
| `BUSINESS_SCORECARD` | `departamento-negocios` | gate interno |
| `BUSINESS_GAP_REPORT` | `departamento-negocios` | agente, Diretor ou CEO conforme a causa |
| `BUSINESS_CAPABILITY_GAP` | `departamento-negocios` | CEO |
| `BUSINESS_JUDGMENT_PACKAGE` | `departamento-negocios` | Diretor, por matriz autorizada |
| `MATRIX_EXCHANGE_MESSAGE` | Negócios ou Diretor | o outro par |
| `LIMITATION_REPORT` | `departamento-negocios`, após verificação dos Juízes | CEO |
| `BUSINESS_RETURN` | `departamento-negocios` | CEO |
| `EXECUTIVE_SUBMISSION` | `departamento-negocios` | CEO |

`JUDGMENT_REQUEST` pertence ao Diretor; `JUDGE_REPORT` pertence aos Juízes; `EXECUTIVE_DECISION` e `EXCEPTION_REQUEST` pertencem ao CEO. O `LIMITATION_REPORT` de Negócios usa a nota final dos Juízes, nunca o score interno.

Independentemente da causa, um score interno abaixo de `9.5` é primeiro comunicado ao Diretor por `MATRIX_EXCHANGE_MESSAGE` autorizada. A causa define quem corrige; não elimina esse repasse. Sem autorização matricial, o retorno vai ao CEO para revisão da missão.

## 3. Retorno legível

Antes do envelope estruturado, apresente:

1. estado atual;
2. menor score interno e critério limitante, quando existir;
3. evidência determinante;
4. próxima ação;
5. autoridade responsável;
6. bloqueios e riscos.
7. relatórios causalmente assinados e gates ainda necessários;
8. autoria, fonte, período e contexto de alegações externas.

O resumo espelha o envelope; se houver divergência, corrija antes de enviar.

## 4. Bypass e falha fechada

Bloqueie quando:

- a missão não vier do CEO;
- um agente for chamado sem missão do Departamento;
- faltar um dos três agentes ou relatórios;
- o produtor do relatório divergir do agente;
- fonte ou número não for rastreável;
- houver tentativa de usar skill-fonte ou pasta legada como fallback;
- a rota ao Diretor não estiver autorizada;
- o veredito referir-se a outro candidato ou contrato;
- pedirem `VALIDATED`, exceção ou decisão executiva ao Departamento.

O retorno deve informar causa observada, impacto, evidência e condição concreta de recuperação.

## 5. Idempotência

Reprocessar o mesmo artefato com o mesmo digest não cria nova conclusão. Mudança material cria novo digest e invalida scores ou pareceres afetados. `attempt` cresce apenas no retrabalho local; `round` continua sendo a rodada recebida do CEO.
