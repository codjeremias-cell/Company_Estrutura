# Workflow de Avaliação de Proposta

## 1. Máquina de estados

| Estado | Condição de entrada | Próxima saída permitida |
|---|---|---|
| `B_RECEIVED` | `EXECUTIVE_MISSION` recebida | validar contrato |
| `B_CONTRACT_VERIFIED` | produtor, destinatário, escopo e causalidade válidos | triar |
| `B_TRIAGED` | entrada classificada e lacunas registradas | planejar ou bloquear |
| `B_PLANNED` | plano íntegro com três atribuições | delegar |
| `B_DELEGATED` | três missões emitidas | aguardar relatórios |
| `B_CONSOLIDATING` | três relatórios válidos | integrar e pontuar |
| `B_NEEDS_CTO` | menor score interno abaixo de `9.5` e matriz autorizada | repassar ao Diretor para tratativa |
| `B_INTERNAL_REWORK` | Diretor devolveu tratativa para a frente interna | emitir retrabalho |
| `B_LIMITATION_REVIEW` | remediações esgotadas e limitação objetiva sustentada | enviar pacote de verificação ao Diretor |
| `B_AWAITING_LIMITATION_VERIFICATION` | Diretor abriu a verificação com os Juízes | aguardar parecer independente |
| `B_LIMITATION_VERIFIED` | Juízes confirmaram impossibilidade e score final abaixo de `9.5` | emitir `LIMITATION_REPORT` ao CEO |
| `B_READY_FOR_JUDGMENT` | menor score interno pelo menos `9.5` | montar pacote de julgamento |
| `B_AWAITING_JUDGMENT` | pacote entregue ao Diretor pela matriz | aguardar veredito vigente |
| `B_READY_FOR_EXECUTIVE_DECISION` | todos os gates aprovados | submeter ao CEO |
| `B_BLOCKED` | entrada, capacidade, evidência, autorização ou gate ausente | devolver ao CEO |

Nenhum estado interno se chama `VALIDATED` ou `REPROVED`.

## 2. Sequência

```text
EXECUTIVE_MISSION
  -> BUSINESS_INTAKE
  -> BUSINESS_EVALUATION_PLAN
  -> 3 x BUSINESS_AGENT_MISSION
  -> 3 x BUSINESS_AGENT_REPORT
  -> BUSINESS_CONSOLIDATION
  -> BUSINESS_SCORECARD
       < 9,5 -> BUSINESS_GAP_REPORT -> Diretor pela matriz
                                      -> retrabalho interno / técnico / CEO
      >= 9,5 -> BUSINESS_JUDGMENT_PACKAGE / STANDARD_JUDGMENT
                 -> Diretor -> Juízes -> Diretor -> JUDGE_REPORT
                 -> Auditoria + testes -> EXECUTIVE_SUBMISSION -> CEO
       < 9,5 e impossibilidade objetiva após tratamento
              -> BUSINESS_JUDGMENT_PACKAGE / LIMITATION_VERIFICATION
              -> Diretor -> Juízes -> Diretor
              -> JUDGE_REPORT < 9,5 + VERIFIED_IMPOSSIBILITY
              -> LIMITATION_REPORT -> CEO
```

## 3. Intake

O gerente verifica, sem executar descoberta:

1. identidade e versão da proposta;
2. problema e consequência de não resolvê-lo;
3. público e tarefa do cliente;
4. proposta de valor;
5. escopo `MVP`, `Depois` e `Fora`;
6. receita, preço e custos conhecidos;
7. evidências, fontes e datas;
8. restrições, riscos e decisões vinculantes;
9. tópicos que dependem de outro Departamento.

Ausência que altera a decisão gera perguntas ou bloqueio. Ausência não material pode virar hipótese com dono, métrica e prazo.

## 4. Planejamento e delegação

O plano contém exatamente os três agentes canônicos. Cada missão:

- deriva da mesma `EXECUTIVE_MISSION`;
- define fronteira e critérios próprios;
- aponta as referências de entrada;
- exige fontes primárias ou dados reais quando disponíveis;
- define como declarar desconhecido, hipótese e `not_applicable`;
- fixa `return_to: departamento-negocios`;
- preserva a rodada global e usa `attempt` para repetição local.

CEO e Diretor não chamam esses agentes diretamente. Tentativa de bypass gera `B_BLOCKED`.

## 5. Consolidação

O gerente não escreve uma conclusão especializada nova. Ele:

1. confere identidade, autoria e evidência dos três relatórios;
2. monta uma matriz de dependências e divergências;
3. devolve inconsistências ao agente de origem;
4. preserva opinião minoritária e risco residual;
5. cria `BUSINESS_CONSOLIDATION` com síntese rastreável;
6. atribui o score interno com participação do time, sem substituir suas evidências.

Uma mudança no candidato, contrato ou digest invalida pareceres anteriores afetados.

Antes de pontuar, valide a cadeia completa: IDs únicos, referências exatas entre os artefatos, mesma identidade causal, tentativa vigente e evidências existentes no relatório proprietário de cada critério. Qualquer divergência mantém o fluxo bloqueado.

## 6. Retrabalho

Todo item abaixo de `9.5` possui:

- `criterion_id`;
- score real;
- causa;
- evidência;
- impacto;
- mudança exigida;
- dono;
- critério de reteste;
- `attempt`.

Antes de emitir a ordem, valide semanticamente contra o gap: `gap_report_ref`, `target_agent`, `criterion_ids`, mudança exigida, critério de reteste, identidade causal e `attempt = gap.attempt + 1`. O schema isolado não substitui essa verificação cruzada.

O gerente reabre apenas as frentes afetadas, mas recalcula a menor nota sobre o scorecard completo e vigente. Não reinicia a rodada executiva.

Antes do retrabalho, todo score abaixo de `9.5` é repassado ao Diretor por matriz autorizada. O Diretor segue a tratativa e devolve o encaminhamento correlacionado; se a correção for interna, o gerente então emite `BUSINESS_REWORK_ORDER`. Sem matriz, o CEO recebe `B_BLOCKED` e precisa revisar a missão.

## 7. Gate independente

A nota interna serve para impedir submissão imatura. O veredito vem dos Juízes.

Enquanto os Juízes aceitarem pedido somente do Diretor:

- Negócios prepara, mas não produz, `JUDGMENT_REQUEST`;
- o Diretor é o broker contratual;
- a comunicação ocorre apenas em matriz autorizada;
- sem essa autorização, o CEO precisa revisar a missão;
- o veredito retorna pelo Diretor e deve referenciar o mesmo candidato e contrato.

Uma limitação objetiva tem rota própria. O pacote abaixo de `9.5` só atravessa com `purpose: LIMITATION_VERIFICATION`, evidências dos fatores objetivos e remediações tentadas. Depois do parecer independente, Negócios pode emitir `LIMITATION_REPORT` conforme o schema do CEO. Sem `JUDGE_REPORT` abaixo do corte e `VERIFIED_IMPOSSIBILITY`, esse artefato é proibido.

## 8. Conclusão

A entrega só chega ao CEO quando os cinco gates estiverem simultaneamente verdadeiros:

1. integridade dos três agentes;
2. `business_internal_minimum_score >= 9.5`;
3. testes obrigatórios sem falha;
4. Auditoria conforme;
5. `JUDGE_REPORT` vigente e aprovado.

O Departamento então emite `EXECUTIVE_SUBMISSION`, nunca decisão executiva.
