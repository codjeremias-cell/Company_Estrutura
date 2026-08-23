# Origem da migração

Origem: `SKILL - Nova formula/maestro/comite-de-lentes/lente-dev-senior` — **37 arquivos**, com
três referências, duas rodadas de evals e três forwards escritos. Fundamentação adicional: a lente
canônica `dev-senior` e os **31 geradores de desenvolvimento** do catálogo.

## Fontes — estado em 2026-07-26

| Arquivo | SHA-256 (16) |
|---|---|
| `lente-dev-senior/SKILL.md` | `454c95f73414ef5f` |
| `lente-dev-senior/agents/openai.yaml` | `8e51ec9c36f5ea4f` |
| `lente-dev-senior/references/contratos.md` | `2e3e82fb51eada05` |
| `lente-dev-senior/references/modelo-operacional-do-time.md` | `41b64b0078f1e191` |
| `lente-dev-senior/references/rubrica-tecnica.md` | `45e3d8f883efb3d9` |
| `lente-dev-senior/evals/evals.json` | `06f525d3e987064c` |
| `lente-dev-senior/evals/placar-baseline.md` | `c3c8e35ab89420da` |

O pacote legado **permanece intacto**, com os 37 arquivos. Rollback manual, nunca fallback
automático.

## Preservado

- a **lei de comando** — missão só do superior, retorno só a ele, nenhuma lente acionada
  lateralmente;
- as **travas fail-closed** de entrada: sem objetivo, escopo, `DONE`, evidência e autoridade, a
  frente não abre;
- **um líder por mudança coerente**, e escrita sobreposta unida ou serializada;
- **governar sem executar** — a gerente não escreve, não roda, não mescla; quem executa são os
  agentes;
- a **política técnica** inteira do `modelo-operacional-do-time.md`: RO-01, escada de decisão,
  bordas, causa-raiz, otimização medida, Cerca de Chesterton;
- a **evidência de fechamento departamental**: prova fresca, produzida por executor, vinculada à
  missão;
- **hipótese nunca vira permissão** — ausência não é capacidade nem sucesso presumido.

## Reescrito

- **o time**: descoberta de capacidade em runtime → **oito agentes fixos**, cinco por track do
  acervo e três transversais (ADR-012, decisão 4);
- **os envelopes**: `WORK_PACKAGE` / `DEPARTMENT_RESULT` do legado → `DEV_TASK` / `DEV_RETURN` /
  `DEV_LEDGER`, com `causalHeader` de 15 campos e `producer` travado;
- **os marcadores**: `SUPOSIÇÃO:` e `ponytail:` eram convenção de comentário; viram **campo
  estruturado** no retorno, além do comentário no ponto exato (decisão 7);
- **os inegociáveis da escada**: eram prosa; viram **recusa de schema** (decisão 8);
- **a Regra dos Três**: era orientação; vira `fix_attempts >= 3` bloqueando a quarta tentativa
  (decisão 9);
- **o `test_summary`**: os outros Departamentos travam em `0/0/0`; aqui carrega número real
  (decisão 1).

## Não copiado — e por quê

- **O modo `JULGAR`** e toda a `rubrica-tecnica.md`: escala absoluta 0–10 com corte 9,5 é o
  `departamento-juizes` (ADR-002). Terceira vez que essa decisão se repete — Arquitetura e Design já
  a tomaram. Aqui é mais grave: julgar o próprio código é o conflito de interesse mais óbvio que
  existe.
- **`LOCAL_ROUND_REF` e a mecânica de rodada local do julgamento**: sem função sem o modo.
- **A descoberta de capacidade em runtime** (`CAPABILITY_GAP` por inspeção de catálogo): o time é
  declarado. O que ela dava de útil volta pela regra *gerador conduz, agente revisa*.
- **A decisão de pegada (degrau 3, skill nova)**: metadado do processo de criação da candidata
  legada, não contrato operacional.
- **Os evals em duas rodadas com batches e scores**: o pacote novo valida em Python sobre o motor
  compartilhado. O `placar-baseline.md` do legado **continua sendo a única medição comportamental
  existente deste domínio**, e ela é do legado, não deste pacote.

## Limite

Migração não é baseline. Nenhuma medição comparou este Departamento com a `lente-dev-senior` nos
mesmos cenários — e, como no Design, os dois instrumentos não são comparáveis: o legado media
orquestração com time descoberto, que este pacote deliberadamente não tem. Ver
[`evals/PLACAR.md`](../evals/PLACAR.md).
