# Origem e recorte da migração — Departamento de Arquitetura de Software

## Fonte legada

Origem lógica: `SKILL - Nova formula/maestro/comite-de-lentes/lente-arquiteto-software`.

Snapshot observado em 2026-07-26: **8 arquivos, 68.918 bytes**. Contagem é escala, não identidade;
a proveniência é fixada pelos hashes abaixo.

| Arquivo legado | SHA-256 |
|---|---|
| `SKILL.md` | `3b35a5de82341bd689e73e60c2639f5980ce3dc09ebba89128c5c19e9e78378c` |
| `references/modelo-operacional-do-time.md` | `a111cd769d5529faadccd844f14a624ec550bb1644180db3298c7160b1f27158` |
| `references/rubrica-arquitetural.md` | `f2ff263533727398472f24fb9922f17ad6d3776ff8adf469527cd65975274c8a` |
| `references/contratos.md` | `1972e82c6af91d88ddad7bb906319a1b15dccd55cf27c9bc48c25bb1cc6ed731` |
| `agents/openai.yaml` | `f1cbe2e005f547077ee3d8ec10b3782fd13b60f86459562b5d1ca2dfb8d40a61` |
| `evals/evals.json` | `e2cf55ff0f63ffca3938854f237debb6e45735f9f8eab0020140d6d225c691c8` |
| `evals/placar.md` | `c05daf3c84cb06c076b4336d1164aaf82e1c28d9692cc04ebf14f54d597d53ec` |
| `evals/evidencias/rodada-2026-07-25.md` | `0180b16af0401d5c0d22bcf94378d9c0e930f7f22f626d5b5a99e1aac028964e` |

**Fonte canônica consultada** (não copiada): `Catalogo-Skills-Unificado/skills/arquiteto-software/`,
mais as duas vizinhas `arquiteto-dados/` e `dev-senior/` — usadas para fixar a fronteira das três
lentes em [fronteiras-com-dados-e-desenvolvimento.md](fronteiras-com-dados-e-desenvolvimento.md).

## Recorte preservado

- o **modo produtor** inteiro: validar missão → descobrir capacidades → montar time por papéis →
  contratar e delegar → coordenar por dependências → integrar sem reautorar → gates locais → devolver;
- os **papéis por capacidade**, que viraram os seis agentes;
- as **ondas por dependência** (enquadramento → exploração → contratos → convergência → documentação),
  como ordem sugerida e não imposta;
- os **gates locais** — cobertura, opções, consistência, decisão, documentação, evidência — e a
  regra de que passar no gate local significa "apto ao gate", nunca "aprovado";
- **começar pelos drivers**; stack popular não substitui requisito;
- **2–3 opções, ou opção única com justificativa verificável**;
- **preferir a opção mais simples** que atenda drivers e maturidade operacional real;
- **preservar autoria, divergência e proveniência** ao integrar; consenso fabricado é falha;
- **ADR aceito é contrato vinculante**, com bloqueio da parte afetada e escalada;
- **separar fato, evidência, inferência e pendência**; nunca inventar capacidade, teste, métrica ou
  limite;
- `CAPABILITY_GAP` estruturado quando a capacidade não existir — nunca improvisar especialidade;
- as **oito dimensões** da rubrica, convertidas em cobertura.

## Recorte reescrito

| Legado | Novo | Por quê |
|---|---|---|
| dois modos: `GERENCIAR` e `JULGAR` | **só produção** | julgar é do `departamento-juizes` (ADR-002); dois julgadores = duas notas concorrentes |
| rubrica ponderada 0–10, corte 9,5, dimensão crítica ≥ 9,0 | **oito dimensões como cobertura**, sem nota | [ADR-006](adr-006-arquitetura-sem-julgamento-e-com-seis-agentes.md), decisão 2 |
| vetos, `REPROVADA`, `NÃO_JULGÁVEL` | — | vocabulário de gate, não de produção |
| `responsibility_ledger`, `PRODUCER_IDS`, `JUDGE_EXCLUSION`, `BLOQUEADO_AUTOJULGAMENTO` | — | existiam só para impedir autojulgamento; o princípio vive no `departamento-juizes` |
| time como **modelo de papéis** em referência | **seis agentes materializados**, com contrato próprio | o legado não tinha nenhum agente |
| três agentes propostos no organograma | **seis** | os três fundiam pares que o legado separa; ADR-006, decisão 3 |
| superior `comite-de-lentes`, retorno causal ao `maestro` | superior e retorno: `diretor-de-lentes` | nova hierarquia |
| `MISSION`/`architecture_management_result` próprios | `DEPARTMENT_MISSION` / `DEPARTMENT_RETURN` | envelopes do superior |
| `ROUND_BUDGET` local com `event_state` | rodada global do contrato, 1 a 10, do Diretor | o contador é do Diretor, não do Departamento |
| "três frentes concorrentes na mesma pasta", `write_lease` | — | resolvido pela árvore canônica: cada pacote tem a própria subárvore |
| fronteira com dados e código no texto | **fronteira mecânica**: sem campo de schema/índice/código no schema, com caso negativo | pedido explícito de Jeremias; texto não segura escorregão |

## Recorte não copiado

- `evals/placar.md`, `evals/evals.json` e `evals/evidencias/rodada-2026-07-25.md` **não foram
  promovidos**: medem a skill legada, com dois modos, rubrica e corte próprios. Ficam na fonte como
  evidência histórica.
- `references/contratos.md` (envelopes v2 próprios) não migrou: os envelopes de fronteira agora são
  do `diretor-de-lentes`, e os internos estão no schema deste pacote.

## Política de rollback

O pacote legado permanece **intacto**. É fonte histórica e rollback manual; nunca fallback
automático. O `diretor-de-lentes` não usa `lente-arquiteto-software` como equivalente deste
Departamento — ausência do canônico é `DIRECTOR_CAPABILITY_GAP`, não substituição silenciosa.
