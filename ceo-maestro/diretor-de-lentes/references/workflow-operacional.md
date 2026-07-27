# Workflow operacional do Diretor

## Cadeia e papéis

| Capacidade | Responsabilidade | Não pode |
|---|---|---|
| `ceo-maestro` | contratar, priorizar e decidir o fechamento | executar ou julgar |
| `diretor-de-lentes` | dirigir Departamentos, integrar e encaminhar | executar, julgar ou validar |
| `departamento-negocios` | estratégia, mercado e viabilidade comercial | comandar Departamentos |
| `departamento-juizes` | avaliar toda entrega e emitir veredito | executar ou corrigir |
| Departamentos operacionais | orquestrar o domínio e consolidar seus agentes | assumir outro domínio ou validar a si próprios |
| Agentes | executar a missão delimitada | ampliar escopo ou autoridade |

## Estados do ciclo do Diretor

Usar namespace `D_` para não confundir coordenação local com decisão do CEO:

```text
D_RECEIVED
  → D_CONTRACT_VERIFIED
  → D_CAPABILITIES_VERIFIED
  → D_PLANNED
  → D_DELEGATED
  → D_INTEGRATING
  → D_AWAITING_JUDGES
      ├── D_JUDGES_APPROVED → D_READY_FOR_CEO → D_SUBMITTED
      ├── D_JUDGES_REPROVED → D_REWORK → D_DELEGATED
      ├── D_LIMITATION_ASSEMBLY → D_LIMITATION_VERIFIED → D_SUBMITTED
      └── D_BLOCKED
```

Estados adicionais: `D_CANCELLED` e `D_LIMIT_REACHED_RETURNED`.

`D_SUBMITTED` prova apenas que o handoff do Diretor terminou. Não equivale a `VALIDATED`;
somente o CEO emite decisão executiva.

## Classificação obrigatória

Para cada Departamento operacional:

| Estado | Uso | Prova mínima |
|---|---|---|
| `ATUA` | possui entrega ou gate próprio | objetivo, missão e evidência |
| `CONSULTA` | responde ponto delimitado | pergunta, escopo e consumidor |
| `NAO_SE_APLICA` | domínio sem impacto | justificativa específica |
| `BLOQUEADO` | deveria atuar, mas falta capacidade/insumo | lacuna, impacto, dono e recuperação |

Juízes não entram nessa escolha: toda entrega materializada exige julgamento. Auditoria
`ATUA` antes de produto ou proposta final.

## Planejamento por dependência

1. Mapear critério de aceite → Departamento dono.
2. Mapear entrada → produtor → consumidor.
3. Separar frentes independentes das sequenciais.
4. Fixar uma barreira de integração.
5. Fixar uma barreira de julgamento para cada entrega e para o candidato integrado.
6. Nomear o único `consolidation_owner` quando Negócios participar.

Slots ou agentes livres não tornam duas frentes independentes. Dependência técnica,
decisão vinculante ou artefato compartilhado prevalece.

## Ciclo de retorno

Para cada `DEPARTMENT_RETURN`:

1. conferir `department_mission_id` e causalidade;
2. conferir que o produtor é o Departamento contratado;
3. conferir `scope_touched`, artefatos, digests, testes e evidências;
4. manter `PENDING` aberto e dissensos visíveis;
5. emitir `JUDGMENT_REQUEST`;
6. correlacionar missão, retorno, pedido e parecer em `DEPARTMENT_GATE_RECORD`;
7. aceitar o resultado para integração somente com decisão
   `ACCEPTED_FOR_INTEGRATION`;
8. em reprovação, emitir `REWORK_ORDER` sem corrigir a entrega.

Mudança no candidato invalida julgamento, auditoria e relatório de limitação anteriores.

## Missão mista com Negócios

- Se `consolidation_owner: diretor-de-lentes`, o Diretor integra a contribuição comercial
  assinada e emite uma única submissão.
- Se `consolidation_owner: departamento-negocios`, o Diretor devolve contribuição técnica
  assinada a Negócios; não cria submissão concorrente.
- Se o dono não estiver definido, a missão fica `D_BLOCKED`.

## Capacidade ausente

Para Departamento operacional ou Juízes ausente, emitir `DIRECTOR_CAPABILITY_GAP` e anexá-lo
a `BLOCKED_RETURN` ou `PROGRESS` ao CEO. O `CAPABILITY_GAP` executivo possui autoria
reservada ao CEO; o Diretor apenas fornece a evidência para que ele o materialize.

Prosseguir somente em trecho não afetado, reversível, autorizado e que não seja apresentado
como aceito.

## Análises não validantes

Quando `deliverable_type: analysis`, devolver a análise como `PROGRESS` correlacionado, com
artefatos e evidências, sem `EXECUTIVE_SUBMISSION` nem estado de validação. Se a análise
passar a ser proposta ou produto, o CEO deve versionar a missão e aplicar o gate completo.

## Critério de conclusão

O ciclo local termina quando o Diretor enviou ao CEO uma submissão íntegra, um relatório de
progresso, um bloqueio ou um pacote de limitação; nenhuma decisão executiva foi usurpada.
