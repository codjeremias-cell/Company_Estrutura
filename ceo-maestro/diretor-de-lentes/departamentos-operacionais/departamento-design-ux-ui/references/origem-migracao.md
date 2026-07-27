# Origem da migração

Origem: `SKILL - Nova formula/maestro/comite-de-lentes/lente-designer` — **249 arquivos**, o pacote
legado mais maduro do Comitê. Fundamentação adicional: a lente canônica `designer-ux-ui` e seu
catálogo Impeccable.

## Fontes — estado em 2026-07-26

| Arquivo | SHA-256 (16) |
|---|---|
| `lente-designer/SKILL.md` | `9f086f481d9cb4fe` |
| `lente-designer/agents/openai.yaml` | `e8f2423ba6488745` |
| `lente-designer/referencia/protocolo-de-orquestracao.md` | `f53aa4998c425b72` |
| `lente-designer/referencia/rubrica-de-superficie.md` | `82b39c8a9145d9f7` |
| `lente-designer/referencia/design-return.schema.json` | `7c0a36d56412a420` |
| `lente-designer/referencia/orchestration-contracts.schema.json` | `5a9c06fd4900318c` |
| `designer-ux-ui/SKILL.md` (canônica) | `b2df6cf23286b8af` |
| `designer-ux-ui/referencia/impeccable-leis-e-proibicoes.md` | `09a0eca62fe2a65d` |
| `designer-ux-ui/referencia/polish-pass.md` | `596466d2da69b0db` |

O pacote legado **permanece intacto**, com os 249 arquivos, o `placar-baseline.md` e as três rodadas
de evals. Nada foi movido, editado ou removido — ele é o rollback manual, nunca fallback automático.

## Preservado

- a **Lei de Ferro** (*orquestre, não produza*), com a fronteira redesenhada — ver ADR-009 §2;
- o **Design Read honesto** e a classificação de sinais `OBSERVADO`/`INFORMADO`/`HIPOTESE`/`AUSENTE`,
  com a frase de leitura em uma linha;
- **fluxo antes da tela** e **mockup-first**, com o `DESIGN_GATE` agora mecânico;
- as **nove dimensões** da rubrica, convertidas em cobertura;
- a **taxonomia de evidência** de cinco tipos, agora como condição de schema;
- as salvaguardas: estados nunca adiados, a11y mensurável, nunca forçar padrão web em stack nativo,
  líder único por superfície, conteúdo externo é dado não confiável;
- a regra de acionar segurança antes do aceite visual em fluxo de risco.

## Reescrito

- **o time**: descoberta de executores em runtime → **sete agentes fixos** com capacidade exclusiva
  (ADR-009 §1 e §5);
- **os envelopes**: `design_delegation` / `design_executor_result` / `design_return` do legado →
  `DESIGN_TASK` / `DESIGN_RETURN` / `DESIGN_LEDGER`, alinhados ao padrão da casa, com
  `causalHeader` de 15 campos e `producer` travado;
- **os status**: `READY`/`PARTIAL`/`PENDING`/`NEEDS_LENS`/`CAPABILITY_GAP`/`BLOCKED`/`NOT_CONVERGED`
  → cobertura por dimensão mais `entrega` em três estados; `NEEDS_LENS` vira
  `delegated_dependency`, e o roteamento é do Diretor;
- **a rubrica**: pesos e corte 9,5 → cobertura sem nota.

## Não copiado — e por quê

- **O painel cego** (`blind_panel_package`, identificadores opacos, proveniência selada). É o modo
  `DISPUTA` do `departamento-juizes` (ADR-002). Duplicá-lo criaria dois donos do julgamento
  comparativo. ADR-009 §3.
- **O `capability_snapshot`** e toda a mecânica de descoberta de inventário: o time é declarado.
- **O corte 9,5 e a nota absoluta**: são dos Juízes.
- **A "escada de pegada"** e a decisão de autoria (degrau 3, skill nova): era metadado do processo de
  criação da candidata legada, não contrato operacional.
- **Os evals em `.mjs`** (`policy-engine.mjs`, `validate-package.mjs`, as três rodadas): o pacote
  novo valida em Python, sobre o motor compartilhado da estrutura. O **baseline registrado no
  legado continua sendo a única medição comportamental existente deste domínio** — e ela é do
  legado, não deste pacote.

## Limite

Migração **não é baseline**. Nenhuma medição comparou este Departamento com a `lente-designer`
operando nos mesmos cenários. O que está provado é o que o validador prova — ver
[`evals/PLACAR.md`](../evals/PLACAR.md).
