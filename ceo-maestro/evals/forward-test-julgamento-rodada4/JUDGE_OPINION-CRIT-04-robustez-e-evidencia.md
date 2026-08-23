# JUDGE_OPINION — CRIT-04 · ótica `robustez-e-evidencia`

- **Data:** 2026-07-28
- **Rodada:** 4 (forward test de julgamento)
- **Candidato:** `.claude/skills/ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-inovacao-melhoria`
- **`candidate_digest`:** `sha256:bbcae76833d7d54d051af903b7949e478272c720743cd176c1a0c1acc3fd4f58` (conferido pelo topo; **não recalculado** aqui)
- **Schema do superior confrontado:** `.claude/skills/ceo-maestro/diretor-de-lentes/schemas/diretor-de-lentes.schema.json`
- **Parecer anterior desta ótica:** rodada 3, CRIT-04 = **8** · banda `polido`
- **Escala:** 0–10 · ADR-014 (10 = `VALIDATED`; 7–9 = `ACEITO_USO_INTERNO`; ≤6 = `REPROVED`)

---

## Veredito

**CRIT-04 = 8 · banda `ACEITO_USO_INTERNO`.** As quatro cláusulas fecham. A mudança
da rodada (**R9** no §12) **não quebrou** a cláusula do fecho — mas introduziu um
defeito estrutural na própria tabela que a cláusula de rastreabilidade usa como
âncora, e o validador do pacote não o enxerga.

## Cláusula 1 — todo passo numerado fecha com o fecho literal

**Fecha. Contagem: 12 seções `## N.` × 12 fechos.**

| § | Heading | Fecho |
|---|---|---|
| 1 | `:3` | `:38` |
| 2 | `:41` | `:61` |
| 3 | `:65` | `:87` |
| 4 | `:90` | `:130` |
| 5 | `:134` | `:177` |
| 6 | `:181` | `:285` |
| 7 | `:289` | `:323` |
| 8 | `:326` | `:353` |
| 9 | `:357` | `:389` |
| 10 | `:392` | `:404` |
| 11 | `:407` | `:424` |
| 12 | `:427` | `:453` |

Travado em código: `evals/validate_workflow.py:1589-1593` parte o texto em `^## ` e
exige `"**Concluído quando:**"` em cada bloco. As subseções `### 6.1/6.2/6.3` não são
blocos `## ` e não têm fecho próprio — leitura consistente entre critério, arquivo e
validador.

**Divergência literal a registrar:** a forma no arquivo é `**Concluído quando:**` —
com acento e delimitadores de negrito. A string ASCII `Concluido quando:` do enunciado
do critério **não existe** em nenhuma linha do protocolo. Trato como normalização do
enunciado, não como achado; mas quem congelar o critério deve congelar a forma acentuada,
porque é ela que o validador exige.

**Reconferência da mudança (`+11` linhas, R9):** o acréscimo caiu **dentro** do §12, que
já tinha fecho, e o fecho foi atualizado de `(R1–R4, R6–R8)` para `(R1–R4, R6–R9)`
(`:455`). Nenhum parágrafo novo virou seção `## `. Cláusula intacta.

## Cláusula 2 — `$schema` e `$id`

**Fecha, literal.**

- `schemas/departamento-inovacao-melhoria.schema.json:2` → `"$schema": "https://json-schema.org/draft/2020-12/schema"`
- `:3` → `"$id": "https://skill-crowd.local/schemas/departamento-inovacao-melhoria.schema.json"`

## Cláusula 3 — referenciar a seção, não duplicar o schema

**Fecha, e é o ponto mais forte do critério.** Os três agentes citam a seção **pelo
número**, não o arquivo genérico:

- `agentes/agente-descoberta-de-oportunidades/SKILL.md:25-28` — "envelopes (§1), contexto confiável (§2), fronteira entre as capacidades (§3), assignment (§5), retorno e o payload de Descoberta com a RO-15 (§6 e §6.1), gate (§7) e riscos residuais (§12) vêm de lá, sem variação"
- `agentes/agente-experimentos-e-spikes/SKILL.md:24-27` — mesma forma, com `§6.2`
- `agentes/agente-melhoria-continua/SKILL.md:24-27` — mesma forma, com `§6.3`

`SKILL.md:53-68` manda ler o protocolo antes de planejar/delegar/integrar/devolver e
validar contra os **dois** schemas (o local e o do consumidor), por link. Varredura por
`required`/`additionalProperties`/`"type"`/`minItems` nas quatro `SKILL.md`: **zero
ocorrências**. Não há schema reescrito em prosa; os nomes de campo que aparecem
(`gate_checks`, `blocking_pending_refs`, `matrix_authorization`, `production_access`)
são referência de comportamento, não redeclaração de estrutura.

## Cláusula 4 — o envelope é aceito pelo schema REAL do superior

**Fecha para a instanciação exercitada — e só para ela.** Confronto campo a campo entre
a projeção `to_department_return()` (`validate_workflow.py:934-961`) e
`#/$defs/departmentReturn` do superior (`diretor-de-lentes.schema.json:544-580`),
`additionalProperties: false` dos dois lados:

| Campo | Superior exige | Projeção produz | Veredito |
|---|---|---|---|
| `artifact_type` | `const DEPARTMENT_RETURN` | idem (`:937`) | ok |
| `department_return_id` | `identifier` ≤128, sem `/@` | literal `department-return-innovation-001` (`:938`) | ok |
| `causal` | `causalHeader`, 15 chaves, fechado | spread do relatório + 4 overrides (`:939-945`) | ok, ver achado 3 |
| `department_mission_ref` | `identifier` | do relatório (`:946`) | ok, ver achado 3 |
| `returned_by` | `operationalDepartment` | `departamento-inovacao-melhoria` (`:947`) | ok |
| `state` | `const RETURNED` | idem (`:948`) | ok |
| `scope_touched` | `requiredStrings` ≥1 | **literal** (`:949`) | ok, ver achado 4 |
| `artifact_refs` | `requiredRefs` ≥1 | relatório autenticado + plano (`:950-953`) | ok |
| `evidence_refs` | `requiredRefs` **≥1** (`:38-43`, `:573`) | cópia do relatório (`:954`) | ok, ver achado 2 |
| `candidate_digest` | `digest` estrito, **sem `n/a`** (`:25-28`, `:574`) | verbatim do relatório (`:955`) | ok, ver achado 1 |
| `test_summary` | ints ≥0, `skip_reasons` livre, bool | `zeroTestSummary` 0/0/0 (`:956`) | ok, subconjunto |
| `pending_refs` / `dissent_refs` | `optionalRefs` | derivados (`:957-958`) | ok |
| `returned_to` | `const diretor-de-lentes` | idem (`:959`) | ok |
| `returned_at` | `date-time` | idem (`:960`) | ok |
| `producer` causal | `knownCapability` | forçado ao Departamento (`:943`) | ok |

Nenhum campo obrigatório do superior falta; nenhum campo extra viola o
`additionalProperties: false`. A validação real é chamada em
`bridge_errors()` (`:1501-1548`), contra
`director_schema["$defs"]["departmentReturn"]` (`:1516`) — o schema do superior de
verdade, não uma cópia —, com reconciliação fonte→envelope por campo (`:1520-1546`).
O pacote deliberadamente **não** define `DEPARTMENT_RETURN` no schema local, o que é a
postura correta: não sombreia o contrato do consumidor.

**O que impede o `excelente`:** a aceitação está provada para **uma** instanciação. O
schema local é estritamente **mais largo** que o do consumidor em quatro pontos, e
nenhum deles é exercitado nem declarado como limite.

---

## Achados

### 1 — `candidate_digest: n/a` é local-válido e superior-inválido *(carregado da rodada 3, intacto)*

- `schemas/departamento-inovacao-melhoria.schema.json:25-28` — `"pattern": "^(sha256:[a-f0-9]{64}|n/a)$"`
- `:1400` — `"candidate_digest": { "$ref": "#/$defs/digest" }` no `innovationConsolidatedReport`
- `diretor-de-lentes.schema.json:25-28` — `"pattern": "^sha256:[a-f0-9]{64}$"` · `:574` — `"candidate_digest": { "$ref": "#/$defs/digest" }`

A projeção copia verbatim (`validate_workflow.py:955`). Uma `DEPARTMENT_MISSION` sem
candidato — que o **próprio superior admite** no cabeçalho causal
(`diretor-de-lentes.schema.json:161-166`, `oneOf: digest | n/a`) — produz rodada
localmente válida cujo envelope o superior **rejeita**. Fixture única:
`CANDIDATE = "sha256:" + "b"*64` (`validate_workflow.py:102`), usada nas cinco
instanciações; **nenhuma** com `n/a`.

### 2 — `evidence_refs` vazio é local-válido e superior-inválido *(carregado, intacto)*

- local: `:1425` `"evidence_refs": { "$ref": "#/$defs/refList" }`; `refList` (`:44-48`) **não tem `minItems`**
- superior: `:573` `"evidence_refs": { "$ref": "#/$defs/requiredRefs" }`; `requiredRefs` (`:38-43`) tem `"minItems": 1`

Rodada em que nenhum agente produziu evidência (tudo em `claims_unverified`, cenário
que o próprio protocolo prevê em `§6`) é local-válida e derruba o envelope no superior.

### 3 — `identifier` e `round` locais são mais largos que os do consumidor *(novo nesta ótica; mesma classe do achado 1)*

- local `identifier` (`:14-19`): `maxLength 160`, pattern `^[A-Za-z0-9][A-Za-z0-9._:@/-]*$` — admite `/` e `@`
- superior `identifier` (`:19-24`): `maxLength 128`, pattern `^[A-Za-z0-9][A-Za-z0-9._:-]+$` — **não** admite `/` nem `@`
- local `causal.round` (`:111`): `{"type":"integer","minimum":1}`, sem teto
- superior `causal.round` (`:167-171`): `"minimum": 1, "maximum": 10`

Atravessam a fronteira como `identifier`: `department_mission_ref` e os 15 campos do
`causal`. Um `department_mission_ref` como `mission/2026-07/inovacao-001`, ou qualquer id
com `@`, ou uma 11ª rodada, passam no schema local e são recusados pelo superior. Mesma
forma de falha do achado 1, e mais provável de ocorrer na prática.

### 4 — `scope_touched` não tem origem na fonte *(carregado, intacto)*

`validate_workflow.py:949` — `"scope_touched": ["Fluxo de publicação."]`. O superior exige
`requiredStrings` ≥1 (`:571`), mas o campo é literal na projeção: não deriva de nenhum
campo do `INNOVATION_CONSOLIDATED_REPORT`, e `bridge_errors()` (`:1520-1546`) reconcilia
missão, candidato, causa, artefatos, evidências, pendências, dissensos e `test_summary` —
**nunca** `scope_touched`.

### 5 — a linha do R9 está **fora** da tabela de riscos *(NOVO — introduzido pela mudança desta rodada)*

`references/protocolo-inovacao-melhoria.md:442-444`:

```
442  | **R8** bypass para fora | ... |
443  (linha em branco)
444  | **R9** acionamento espontâneo não é verificável neste pacote | ... |
```

Em Markdown, a tabela **termina** na linha em branco de `:443`. A linha `:444`, sem
header e sem linha de separação própria, não é linha de tabela: renderiza como parágrafo
de texto com pipes literais. A tabela do §12 — cujo header é `| Id | Vetor | Consequência
| Mitigação | Teto |` (`:433`) — passa a exibir **oito** riscos, e o nono fica solto logo
abaixo dela. Confirmado no diff da rodada: o `+| **R9** …` foi inserido **depois** da
linha em branco que já fechava a tabela.

Isto **não quebra** nenhuma das quatro cláusulas do CRIT-04 — registro pela fronteira de
corretude técnica e rastreabilidade, porque a tabela do §12 é a âncora de que o fecho
`:453-456` depende ("nomeia pelo identificador cada um dos demais limites").

**E o validador não pega:**

- `protocol_errors()` (`:1605-1613`) conta linhas por `line.startswith("| **R") and line.count("|") >= 6`, ignorando continuidade de tabela → conta 9 e passa em `len(rows) < 4`;
- `placar_errors()` (`:1667`) lê os ids por `re.findall(r"\*\*(R\d+)\*\*", …)` em toda a seção → acha `**R9**` mesmo órfão, e ainda o acha no bloco de citação de `:446-451`.

Ou seja: a estrutura da tabela é exigida em prosa (§12: "Esta seção é o **único** lugar
onde são declarados") e conferida em código apenas por presença de string. Correção:
remover a linha em branco de `:443`, movendo o bloco `>` explicativo para depois da
tabela inteira.

---

## Registro de estado

Nenhum dos achados 1, 2 e 4 — levantados na rodada 3 — foi tratado nesta rodada. Varredura
por `candidate_digest`, `scope_touched` e `n/a` em `evals/PLACAR.md`,
`evals/ADVERSARIAL-AUDIT.md` e `evals/FORWARD-TEST.md`: **zero ocorrências**. A seção
`## O que ainda não foi provado` do `PLACAR.md` lista os mesmos 8 limites da rodada
anterior — o antigo `P1` agora carrega o identificador `R9` —, e **nenhum** deles cobre a
assimetria de fronteira entre os dois schemas. A nota se mantém em 8 por paridade: as
quatro cláusulas fecham com a mesma força de antes, o achado 5 é novo mas não toca
cláusula, e o achado 3 é a mesma forma de falha já precificada no 8 da rodada 3. **Sem
arredondar para cima e sem arredondar para baixo por defeito de acabamento.**

## Não executado

- **Python: negado nesta sessão.** `evals/validate_workflow.py` e `evals/corpus_adversarial.py` **não foram executados**. Não há contagem `PASS/FAIL` produzida por esta ótica; toda afirmação sobre o validador é **leitura de código**, não execução.
- **Validação de schema por biblioteca: `SKIP`.** Nenhum `jsonschema` rodou. O confronto campo a campo das cláusulas 2 e 4 foi feito **manualmente**, lendo os dois arquivos JSON e a função de projeção.
- **Digest do candidato: não recalculado** (aceito do topo, por instrução).
- **Renderização Markdown: não verificada em renderizador.** O achado 5 é derivado da regra de terminação de tabela do GFM aplicada ao texto do arquivo e confirmada pelo diff, não de captura visual.

---

```yaml
criterion_id: CRIT-04
owner_lens: robustez-e-evidencia
score: 8
banda: ACEITO_USO_INTERNO
veredito_do_criterio: >-
  As quatro clausulas fecham. 12 secoes numeradas x 12 fechos literais, travados
  em codigo; $schema draft 2020-12 e $id no namespace exigido; SKILL.md e os tres
  agentes referenciam a secao do protocolo por numero, sem duplicar schema; e o
  DEPARTMENT_RETURN derivado passa campo a campo no #/$defs/departmentReturn real
  do superior. A mudanca da rodada (R9) nao quebrou a clausula do fecho.
aceito_pelo_schema_do_superior:
  resposta: parcial
  motivo: >-
    Aceito para a unica instanciacao que o pacote constroi e valida (CANDIDATE
    fixo em validate_workflow.py:102). O schema local admite quatro classes de
    entrada que o superior recusa - candidate_digest 'n/a', evidence_refs vazio,
    identifier com '/' ou '@' ou >128 chars, round >10 - nenhuma exercitada por
    fixture, nenhuma declarada como limite residual.
achados:
  - id: 1
    tipo: fronteira-de-schema
    estado: carregado-da-rodada-3-intacto
    arquivo: schemas/departamento-inovacao-melhoria.schema.json:25-28
    citacao: '"pattern": "^(sha256:[a-f0-9]{64}|n/a)$"'
    confronto: diretor-de-lentes.schema.json:25-28 -> '"pattern": "^sha256:[a-f0-9]{64}$"' ; :574 candidate_digest
    efeito: >-
      Missao sem candidato, legal no proprio superior (:161-166), produz rodada
      local valida cujo envelope o superior rejeita. Copia verbatim em
      validate_workflow.py:955.
  - id: 2
    tipo: fronteira-de-schema
    estado: carregado-da-rodada-3-intacto
    arquivo: schemas/departamento-inovacao-melhoria.schema.json:1425
    citacao: '"evidence_refs": { "$ref": "#/$defs/refList" }'
    confronto: diretor-de-lentes.schema.json:573 requiredRefs ; :38-43 '"minItems": 1'
    efeito: rodada sem evidencia de agente e local-valida e derruba o envelope no superior.
  - id: 3
    tipo: fronteira-de-schema
    estado: novo-nesta-otica
    arquivo: schemas/departamento-inovacao-melhoria.schema.json:14-19
    citacao: '"maxLength": 160, "pattern": "^[A-Za-z0-9][A-Za-z0-9._:@/-]*$"'
    confronto: >-
      diretor-de-lentes.schema.json:19-24 -> '"maxLength": 128, "pattern":
      "^[A-Za-z0-9][A-Za-z0-9._:-]+$"' (sem '/' e sem '@') ; round local :111 sem
      teto contra :167-171 '"maximum": 10'
    efeito: >-
      department_mission_ref e os 15 ids do causal atravessam a fronteira como
      identifier; id com '/' ou '@' ou 11a rodada passam local e sao recusados
      pelo superior.
  - id: 4
    tipo: reconciliacao-ausente
    estado: carregado-da-rodada-3-intacto
    arquivo: evals/validate_workflow.py:949
    citacao: '"scope_touched": ["Fluxo de publicação."]'
    efeito: >-
      campo obrigatorio do superior (:571) e literal na projecao, sem origem no
      relatorio; bridge_errors (:1520-1546) reconcilia tudo menos ele.
  - id: 5
    tipo: estrutura-do-artefato
    estado: NOVO-introduzido-pela-mudanca-desta-rodada
    arquivo: references/protocolo-inovacao-melhoria.md:443-444
    citacao: >-
      linha 443 em branco, seguida de '| **R9** acionamento espontâneo não é
      verificável neste pacote | ...'
    efeito: >-
      a linha em branco encerra a tabela de :433; a linha do R9 nao e linha de
      tabela e renderiza como paragrafo com pipes literais. A tabela unica de
      riscos exibe 8, com o nono solto. Nao quebra clausula do CRIT-04.
    nao_detectado_por: >-
      protocol_errors :1605-1613 conta por startswith('| **R') sem exigir
      continuidade; placar_errors :1667 acha '**R9**' por regex em qualquer ponto
      da secao.
    correcao: remover a linha em branco de :443 e mover o bloco '>' de :446-451 para depois da tabela.
nao_executado:
  - "Python negado na sessao: validate_workflow.py e corpus_adversarial.py NAO executados; nenhuma contagem PASS/FAIL produzida por esta otica."
  - "Validacao de schema por biblioteca (jsonschema): SKIP. Clausulas 2 e 4 conferidas por leitura manual dos dois JSON e da funcao de projecao."
  - "Digest do candidato nao recalculado (aceito do topo, por instrucao)."
  - "Renderizacao Markdown nao verificada em renderizador; achado 5 derivado da regra de terminacao de tabela do GFM e confirmado pelo diff."
```
