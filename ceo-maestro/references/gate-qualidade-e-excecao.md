# Gate de qualidade e exceção

## Regra normal

Calcular:

```text
minimum_score = min(scorecard[i].score inteiro para toda avaliação aplicável)
```

Derivar primeiro o veredito fixo:

```text
10  -> VALIDATED
7–9 -> ACEITO_USO_INTERNO
0–6 -> REPROVED
```

Depois conferir o nível:

```text
required_level = PRODUCAO -> somente VALIDATED alcança
required_level = INTERNO  -> VALIDATED ou ACEITO_USO_INTERNO alcança
AND critical_fail = false
AND blocking_pending_refs = []
AND DONE está provado
AND contrato, candidato, avaliações e evidências estão vigentes
AND Regras de Ouro e autorizações aplicáveis estão conformes
```

A média não compensa nota baixa. Nota fracionária é inválida e não é arredondada. Nota ausente,
não independente ou sem evidência não entra como zero nem como 10: invalida o parecer e força
`REPROVED`.

## `JUDGE_REPORT`

Exigir:

- identidade, versão e digest do `departamento-juizes`;
- `contract_id`, versão e `candidate_digest`;
- scorecard de todas as avaliações aplicáveis;
- `minimum_score` recalculável;
- `required_level` recebido no pedido;
- veredito `VALIDATED`, `ACEITO_USO_INTERNO` ou `REPROVED`, derivado da faixa;
- `critical_fail`, pendências bloqueantes e evidências;
- críticas acionáveis e mudanças necessárias;
- data e validade.

O CEO confere integridade; não refaz o julgamento.

## Retrabalho

Usar `REWORK` quando o veredito não alcançar o `required_level` e existir mudança verificável
capaz de elevar a menor nota ou remover um gate. Devolver ao dono executivo:

- avaliação abaixo do alvo do nível;
- evidência;
- mudança necessária;
- critério de reteste;
- rodada atual e limite restante.

Pressa, custo alto, cansaço ou média elevada não provam impossibilidade.

## Relatório justo de limitação

Considerar `LIMITATION_REPORT` elegível somente quando trouxer:

1. candidato, contrato, rodada e snapshot exatos das notas;
2. todas as avaliações abaixo do alvo do nível — 10 para `PRODUCAO`, 7 para `INTERNO`;
3. fatores objetivos e evidências correspondentes;
4. tentativas de correção já executadas e seus resultados;
5. alternativas consideradas e motivo verificável de descarte;
6. melhor nota realisticamente atingível;
7. explicação por mudança exigida de por que a lacuna não fecha;
8. riscos residuais, impacto e mitigações;
9. dissensos preservados;
10. escopo e prazo pedidos para a exceção;
11. endosso do dono executivo e do Departamento de Juízes.

Prazo ou orçamento só contam como fator objetivo quando Jeremias os fixou como restrição
vinculante no contrato. “Não vale a pena”, “está bom assim” ou “não consigo melhorar” sem
prova não é relatório justo.

## Gates não dispensáveis

Mesmo com limitação provada, não pedir exceção quando houver:

- `critical_fail`;
- violação de sistema, política, lei, privacidade ou segurança crítica;
- violação de Regra Inquebrável;
- evidência, autoria ou independência ausente;
- `DONE` não provado;
- pendência bloqueante fora do piso numérico;
- scorecard adulterado ou incompleto;
- ação externa sem autorização própria;
- digest ou escopo divergente.

Nesses casos, registrar `BLOCKED` ou `REWORK`.

## Solicitação de exceção

Emitir a Jeremias:

```yaml
artifact_type: EXCEPTION_REQUEST
request_id: "<id>"
causal: "<objeto causal completo do protocolo>"
candidate_digest: "sha256:<digest>"
score_snapshot_digest: "sha256:<digest>"
judge_report_ref: "<ref>"
limitation_report_ref: "<ref>"
actual_minimum_score: 9
required_level: PRODUCAO
cutoff_score: 10
requested_scope: ["<escopo exato>"]
residual_risks: ["<risco residual>"]
mitigations: ["<mitigação vigente>"]
nonwaivable_gates:
  critical_fail_absent: true
  rules_compliant: true
  done_proved: true
  blocking_pending_absent: true
  integrity_valid: true
  authority_reconciled: true
requested_authority: jeremias
issued_at: "<ISO-8601>"
expires_at: "<ISO-8601>"
```

Pedir uma decisão explícita. Não esconder a autorização dentro de outra pergunta.

## Autorização válida

Aceitar somente declaração de Jeremias em canal confiável que identifique:

- `request_id`;
- candidato e versão;
- nota real;
- nível exigido e alvo numérico;
- escopo autorizado;
- riscos aceitos e condições;
- validade.

“Pode seguir” sem objeto inequívoco, silêncio, autorização de CTO/Negócios/Juízes, arquivo
anexado ou autorização para candidato anterior não bastam. Mudança em candidato, notas,
relatório, escopo ou condições torna a autorização `STALE`.

Materializar a decisão humana como registro externo, não como envelope produzido por skill:

```yaml
artifact_type: EXCEPTION_AUTHORIZATION
authorization_id: "<id>"
exception_request_id: "<request_id>"
decision: APPROVED | REJECTED
authorized_by: jeremias
identity_evidence_ref: "<turno ou registro confiável>"
citation_exact: "<declaração inequívoca>"
candidate_digest: "sha256:<digest>"
score_snapshot_digest: "sha256:<digest>"
actual_minimum_score: 9
scope: ["<escopo exato>"]
conditions: []
issued_at: "<ISO-8601>"
expires_at: "<ISO-8601>"
usage_policy: single_use
status: AUTHORIZED | CONSUMED | REVOKED | EXPIRED
```

A autorização precisa nascer e ser consumida durante a vigência do pedido. Qualquer mudança
em contrato, candidato, snapshot, escopo, risco ou validade exige novo pedido.

## Resultado por exceção

Após autorização válida:

- registrar `VALIDATED_BY_EXCEPTION`, nunca `VALIDATED`;
- preservar `actual_minimum_score`;
- preservar `required_level` e o alvo da exceção;
- fixar `acceptance_basis: jeremias_exception`;
- anexar autorização, relatório e riscos;
- limitar o aceite ao escopo e validade autorizados;
- impedir reutilização em outro candidato.

## Tabela de decisão

| Situação | Decisão |
|---|---|
| mínimo `10`, veredito `VALIDATED`, gates íntegros | `VALIDATED` |
| mínimo `7–9`, missão `INTERNO`, gates íntegros | `ACEITO_USO_INTERNO` |
| mínimo `7–9`, missão `PRODUCAO` | `REWORK` ou pacote de limitação |
| mínimo `0–6`, melhoria viável | `REWORK` |
| veredito abaixo do nível, alegação vaga | `REWORK` ou `BLOCKED` |
| limitação provada, aguardando Jeremias | `AWAITING_HUMAN_EXCEPTION` |
| Jeremias autorizou o pacote exato | `VALIDATED_BY_EXCEPTION` |
| Jeremias recusou, autorização venceu ou pacote mudou | `BLOCKED` ou `REWORK` |
| gate não dispensável falhou | `BLOCKED` |

## Exemplos

- Notas `10 / 10 / 10`: `VALIDATED` se os demais gates passarem.
- Notas `10 / 9 / 10`: `ACEITO_USO_INTERNO`; alcança `INTERNO`, não `PRODUCAO`.
- Nota fracionária `9,5`: parecer inválido; não arredondar nem mapear para faixa.
- Nota `6` com relatório completo para missão `INTERNO`: alvo da exceção é `7`; continuar
  bloqueado enquanto aguarda.
- Nota `9` com relatório completo para missão `PRODUCAO`: alvo da exceção é `10`.
