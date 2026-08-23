# LOTE 2 — Skills e agentes: anatomia, contrato, empacotamento

**Data da medição:** 2026-08-04
**Ferramenta:** `WebFetch` sobre `raw.githubusercontent.com` e `api.github.com/repos/<owner>/<repo>/contents/<path>`
(a API de conteúdo *lista diretório*, o que o enunciado supunha impossível — foi ela que permitiu achar
`evals/`, `hooks/` e `scripts/lib/` do addyosmani, que o README não cita).
**Escopo:** 15 repositórios. **Lidos com sucesso:** 15. **Lidos parcialmente:** 4 (declarados no fim).

Buracos-alvo, para referência interna do documento:
**B1** anatomia · **B2** descoberta e acionamento · **B3** empacotamento e distribuição ·
**B4** limite legível por máquina · **B5** documentação que dirige ao erro · **B6** composição ·
**B7** método de codificar julgamento subjetivo.

---

## 0. Convergência entre autores independentes

Convergência é o sinal mais forte deste lote. Contagens abaixo só incluem repositórios onde eu **li o
artefato**, não onde o README afirmava algo.

| Convenção | Repos que a praticam | Contagem |
|---|---|---|
| Arquivo único obrigatório `SKILL.md` com frontmatter YAML | addyosmani, mattpocock, levnikolaevich, mukul975, ZeroPointRepo, charlie947, leonxlnx, resemble-ai, nutlope, blader, jakubkrehel, composio, AMAP-ML | **13 de 15** |
| Frontmatter mínimo = `name` + `description`, e só | addyosmani, mattpocock, levnikolaevich, composio, resemble-ai, jakubkrehel, leonxlnx | **7** |
| `name` obrigatoriamente **igual ao nome do diretório** | addyosmani (`skill-lint.js`), levnikolaevich (`AGENTS.md`), AMAP-ML (`_SAFE_NAME_RE`) | **3** |
| Gatilho vive **dentro** da `description`, em cláusula "Use when" | addyosmani (validado por regex), mattpocock, levnikolaevich, mukul975, ZeroPointRepo, charlie947, jakubkrehel | **7** |
| **Limite negativo** dentro da mesma `description` ("Not for…", near-negative) | ZeroPointRepo, levnikolaevich, jakubkrehel (parcial), leonxlnx (no corpo) | **4** |
| Instalação por `npx skills add <owner>/<repo>` | addyosmani, composio, mattpocock, mukul975, ZeroPointRepo, leonxlnx, nutlope, blader, jakubkrehel, resemble-ai | **10 de 15** |
| Campo `version` semver no próprio artefato | mukul975 (`version: '1.0'`), blader (`metadata.version`), nutlope (`version: 1.1.0`), ZeroPointRepo (`version: "1.5.0"`), nextlevelbuilder (`skill.json`), addyosmani (`plugin.json`) | **6** |
| Nenhum digest/hash no contrato da skill publicada | 14 de 15 (única exceção: AMAP-ML) | **14** |

**Leitura para a Estrutura:** o ecossistema convergiu num contrato *minúsculo* — um arquivo, dois campos.
Nada aqui se parece com as 12 seções do `CONTRATO-DE-COMPROMISSO.md`. Mas dois repositórios
(**addyosmani** e **levnikolaevich**) provam que dá para **exigir estrutura por código** em cima desse
mínimo, e um deles (**addyosmani**) é o único do lote que **mede** se a skill é escolhida.

---

## 1. `addyosmani/agent-skills` — o achado mais forte do lote

### O que existe

**Anatomia normativa em documento + validador que a executa.**
`docs/skill-anatomy.md` (https://raw.githubusercontent.com/addyosmani/agent-skills/main/docs/skill-anatomy.md)
declara: frontmatter obrigatório `name` (lowercase-hífen, **igual ao diretório**) e `description`
(máx. **1024 caracteres**, precisa dizer *o que faz* **e** "one or more clear 'Use when' trigger
conditions"); único arquivo obrigatório `skills/<skill-name>/SKILL.md`; teto de **500 linhas**;
material de referência acima de 100 linhas sai para arquivo à parte; skill **não pode** duplicar
checklist compartilhado — isso vive em `references/` na raiz. E o documento se autolimita:
*"The frontmatter contract above is required. The section layout below is a recommended pattern, not a
rigid template."*

**O validador — `scripts/lib/skill-lint.js`**
(https://raw.githubusercontent.com/addyosmani/agent-skills/main/scripts/lib/skill-lint.js), chamado por
`scripts/validate-skills.js`. Regras que ele impõe em código, não em prosa:
- diretório casa `/^[a-z0-9]+(-[a-z0-9]+)*$/` → `"Directory name '${dirName}' is not lowercase-hyphen-separated"`;
- `description` ≤ `MAX_DESCRIPTION_LENGTH` (1024) → `"Description is ${fm.description.length} chars — exceeds the ${MAX_DESCRIPTION_LENGTH}-char limit"`;
- **a `description` precisa conter gatilho positivo**, casando `/\buse (this )?when\b|\buse (before|after|during)\b/i`, e **não vale só a forma negada** (`do not use`, `never use`) → `"Description has no 'when to use' trigger — add a \"Use when …\" clause"`;
- cinco seções obrigatórias: `## Overview`, `## When to Use`, `## Common Rationalizations`, `## Red Flags`, `## Verification` → `"Missing required section: ${aliases[0]}"`;
- **isenção é allowlist explícita, não flag autodeclarada**: `type: meta` ou `exempt: sections` só passam se o nome estiver em `SECTION_EXEMPT_SKILLS` dentro do validador → `"Frontmatter declares 'type: meta' or 'exempt: sections' but '${dirName}' is not in the validator's SECTION_EXEMPT_SKILLS allowlist."`;
- referência cruzada a skill inexistente vira aviso: `"Dead cross-reference: \`${ref}\` is not a known skill"`.

**A eval de descoberta — `evals/`**
(https://raw.githubusercontent.com/addyosmani/agent-skills/main/evals/README.md). Três tiers: T1
estrutura, T2 **roteamento e distinção entre descrições**, T3 comportamento com execução real.
Formato do caso, um JSON por skill em `evals/cases/<skill-name>.json`: `skill_name`;
`trigger.positive[]` com `prompt` e `top_k` (padrão 3); `trigger.negative[]` com `prompt` e **`owner`**
— o nome da skill que *deveria* ganhar aquele prompt; `evals[]` com `id`, `prompt`, `expected_output`,
`files[]` (fixtures reais em `evals/fixtures/`), `expectations[]` e `kind` (`execution` | `dialogue`).
Caso real lido inteiro:
https://raw.githubusercontent.com/addyosmani/agent-skills/main/evals/cases/code-review-and-quality.json
— positivo *"Review this pull request before I merge it"*, negativo *"Deploy this to production now"*
com `owner: "shipping-and-launch"`.
**Métrica com corte numérico:** *trigger rank-1 rate* = fração dos prompts positivos em que a skill dona
fica em **primeiro**, não apenas no top-k. **CI exige ≥ 80%; a baseline medida é 86%.** Colisão de
similaridade entre `description`s: **erro em ≥ 75%, aviso em ≥ 50%**.
Comandos: `node scripts/run-evals.js` (T2) e `node scripts/run-evals.js --behavioral <skill-name>` (T3).
`CONTRIBUTING.md` fecha o ciclo: toda skill nova precisa de `evals/cases/<skill-name>.json` com **≥3
gatilhos positivos, ≥2 negativos (com `owner` quando der) e ≥1 eval comportamental**.

**O acionamento — hook, não descrição.** `hooks/hooks.json`
(https://raw.githubusercontent.com/addyosmani/agent-skills/main/hooks/hooks.json) registra um único
evento `SessionStart` que roda `hooks/session-start.sh`; o script injeta no contexto um payload
`{"priority":"IMPORTANT","message":"agent-skills loaded. Use the skill discovery flowchart to find the
right skill for your task.\n\n[conteúdo de using-agent-skills/SKILL.md]"}` — ou seja, **empurra a
meta-skill inteira para dentro da sessão em vez de esperar que o runtime a descubra.**
E o `AGENTS.md` (https://raw.githubusercontent.com/addyosmani/agent-skills/main/AGENTS.md) manda em
imperativo: *"If a task matches a skill, you MUST invoke it"*, *"Never implement directly if a skill
applies"*, *"For every request: 1. Determine if any skill applies (even 1% chance) 2. Invoke the
appropriate skill using the `skill` tool 3. Follow the skill workflow strictly"*.

**Prova exigida.** `references/definition-of-done.md`
(https://raw.githubusercontent.com/addyosmani/agent-skills/main/references/definition-of-done.md):
*"Code runs and behaves as intended, verified at runtime, not just compiled or typechecked"*;
*"New behavior is covered by tests that fail without the change and pass with it"*;
*"The human has reviewed and approved before merge or deploy"*; e recusa explícita do autorrelato
*"It's done, I just haven't run it yet"*.

### A que buracos se aplica, e como usar aqui

- **B2 (o mais importante).** Isto é o *instrumento* que a Estrutura não tem. A medição do cofre
  ("skill instalada com o gatilho na `description` não dispara; só carregou quando o CLAUDE.md mandou
  invocar") foi feita **uma vez, por observação de transcrição**. Aqui existe um harness que roda a
  mesma pergunta em regime: N prompts positivos por skill, N negativos com dono declarado, e uma
  taxa com piso de CI. Porte direto: um `evals/cases/ceo-maestro.json` com `trigger.positive[]`
  (as frases neutras já usadas nas quatro rodadas de 2026-07-27) e `trigger.negative[]` com
  `owner` apontando para as skills do **Catálogo** que competem — `orquestrador-fable`,
  `auditor-responsabilidades`, `spec-projeto-completo`. Isso transforma "a rota saiu certa" em
  *rank-1 rate contra 76 concorrentes*, com número datado e regressão detectável.
- **B2, segunda metade.** O par `hooks.json` + `AGENTS.md` imperativo é a mesma descoberta do cofre,
  feita por outro autor e **automatizada**: eles não confiam no `CLAUDE.md` sendo lido, injetam a
  meta-skill num `SessionStart`. Se a porta única precisa mesmo carregar, o hook é mais forte que a
  instrução em prosa — e é testável (`hooks/session-start-test.sh`, que o `CONTRIBUTING.md` obriga a
  rodar, com saída esperada `"session-start JSON payload OK"`).
- **B1.** `SECTION_EXEMPT_SKILLS` resolve um problema que a casa conhece: **isenção declarada pelo
  próprio artefato é autoisenção**. Aqui a skill pode escrever `exempt: sections` no frontmatter e o
  validador **reprova mesmo assim**, a menos que o nome esteja na allowlist *dentro do código do
  validador*. É exatamente a lição "gate declarado vira gate derivado" implementada por terceiro.
- **B5.** A colisão de `description` com erro em ≥75% de similaridade é a versão automatizada de
  "duas skills que dizem a mesma coisa mandam o operador na porta errada".

### O que não serve

O layout de seções recomendado (`Overview / When to Use / Core Process / Common Rationalizations /
Red Flags / Verification`) é **conselho de conteúdo para um leitor-modelo**, não contrato de
responsabilidade: não há dono, não há fronteira exclusiva, não há custódia de evidência. As cinco
seções que o linter exige são presença de heading — o linter **não** verifica que `## Verification`
contenha evidência executável. É o mesmo "verificar presença não é verificar efeito" que o cofre já
mediu três vezes. Importe o mecanismo (allowlist, regex de gatilho, rank-1 rate), não a lista de
seções.

---

## 2. `mattpocock/skills` — invocação declarada como campo, e a ADR de distribuição

### O que existe

**`disable-model-invocation: true`** — um terceiro campo de frontmatter, além de `name` e
`description`, lido verbatim em dois arquivos:
https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/writing-great-skills/SKILL.md
e https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/wayfinder/SKILL.md .
A regra: skill **model-invoked** omite o campo e precisa de "rich trigger phrasing" na `description`;
skill **user-invoked** põe `true`, e com isso **a `description` sai do alcance do modelo**, reduzindo
carga de contexto. Regra de composição explícita: *user-invoked pode invocar model-invoked, nunca
outra user-invoked*.

Regras de redação da `writing-great-skills`: front-load da palavra-líder na `description`;
**"one trigger per branch"** — não repetir o mesmo ramo com sinônimos; cortar do `description` a
identidade que já está no corpo. Hierarquia de informação em três níveis: passos no próprio
`SKILL.md` (com critério de conclusão verificável), referência no `SKILL.md`, e referência externa
"pushed out of `SKILL.md` into a separate file". Antipadrões nomeados: duplicação e sedimento;
**no-ops que falham o teste de mudança de comportamento**; e *"Negation backfires; prompt the
positive instead"*.

**Roteamento explícito** na `wayfinder`: tickets de research → subagente `/research`; protótipo →
`/prototype`; decisão → `/grilling` + `/domain-modeling`; task → checklist para o humano.

**ADR de distribuição** —
https://raw.githubusercontent.com/mattpocock/skills/main/.agents/adr/0002-ship-as-a-claude-code-plugin.md .
A restrição concreta: o manifesto do Claude Code aceita **vários caminhos explícitos**; o do Codex
aceita **uma string só** e descobre recursivamente tudo abaixo — o que arrastaria as pastas
`deprecated/`, `personal/` e `in-progress/` para dentro do pacote. Decisão: publicar plugin nativo só
para Claude, curado; manter `skills.sh` como fallback universal; adiar o plugin Codex.
Invariante declarada: *"Every promoted skill requires explicit listing in the plugin manifest — no
automatic discovery"*, e a versão em `.claude-plugin/plugin.json` tem de ser sincronizada com a de
`package.json` no release.

### A que buracos se aplica

- **B2.** `disable-model-invocation` é o campo que a Estrutura precisaria e não tem: hoje a porta
  única depende de *não existir* `SKILL.md` nos 15 gerentes e 66 agentes para que não virem skills
  invocáveis. Isso é uma trava por **ausência de arquivo** — frágil, e some no primeiro deploy que
  copiar demais. Um campo positivo ("esta skill não é invocável pelo modelo") é auditável por schema
  e sobrevive à cópia. A regra "user-invoked nunca chama user-invoked" é literalmente a regra da casa
  "agente é folha e só fala com a própria gerente", expressa em uma linha de frontmatter.
- **B3.** *"no automatic discovery"* é o argumento contra deploy por espelho automático — e o cofre já
  sangrou nisso ("o espelho apagava skill de outra frente até o commit a5797da"). Manifesto explícito
  de skills promovidas é a contramedida que outro autor adotou pela mesma razão.
- **B1.** *"Negation backfires; prompt the positive instead"* colide de frente com o desenho da casa,
  onde a fronteira negativa ("NÃO acione para…") é central. Vale como hipótese a testar, não como
  verdade: o mesmo lote traz 4 repositórios que fazem o oposto e põem a negativa na `description`.

### O que não serve

Não li nenhum validador neste repo — as regras de `writing-great-skills` são prosa normativa. Pelo
padrão do cofre ("aviso em prosa não previne erro", repetido 4×), isso é exatamente o regime que
falha. Importe os *campos*; não importe a confiança de que o texto basta.

---

## 3. `levnikolaevich/claude-code-skills` — o único com regra de alocação de índice e CI de paridade

### O que existe

`AGENTS.md` (https://raw.githubusercontent.com/levnikolaevich/claude-code-skills/master/AGENTS.md):

- **Alocação de índice.** Índice de dois dígitos: o primeiro identifica o plugin (1–7 hoje), o segundo
  a skill dentro dele (0–9). *"Allocate the next unused index inside the relevant plugin. A new plugin
  receives the next unused leading digit."* Plugin capado em nove skills indexadas; a décima exige
  plugin novo salvo aprovação explícita de migração.
- **Frontmatter travado no mínimo:** *"Keep YAML frontmatter to `name` and `description`."* Nome da
  pasta == campo `name`. A `description` deve definir a **fronteira de gatilho** — o que faz, quando
  usar e *"important near-negative cases"* — em **≤ 200 caracteres**.
- **Independência dura:** *"Keep each skill standalone. It must not require another skill, MCP server,
  task tracker, separately installed coordinator or worker, or shared runtime."* Skills se comunicam
  **só por documentos no repositório**; chamada direta entre skills é proibida.
- Caminho canônico único: `plugins/<plugin>/skills/<skill>/SKILL.md`, com `.codex-plugin/plugin.json`
  por plugin e dois catálogos, `.claude-plugin/marketplace.json` e `.agents/plugins/marketplace.json`.
- **Versão só sobe a pedido explícito** — edição comum não bumpa versão.

**CI real** — https://raw.githubusercontent.com/levnikolaevich/claude-code-skills/master/.github/workflows/validate.yml :
job `validate` em `ubuntu-latest`, timeout 10min, Node 24, instala
`@anthropic-ai/claude-code@2.1.207` **pinado por versão exata**, roda
`claude plugin validate . --strict`, e um passo PowerShell que confere **paridade entre os dois
catálogos** (mesmos nomes, mesma ordem, mesmos caminhos de manifesto), presença de `license`,
`homepage`, `repository`, SemVer, `SKILL.md` existente **entre 100 e 200 linhas**, ausência de nome de
skill duplicado, e ausência do diretório MCP aposentado.

O README declara o que o projeto **deliberadamente não tem**: *"MCP servers, orchestration hierarchy,
distributed shared resources, generated skill copies, or evaluation harness."*

### A que buracos se aplica

- **B1 / B3.** A regra de alocação de índice é a resposta de outro autor ao problema que o cofre
  registrou como *"gate de maximalidade proíbe o futuro"*: a norma aqui é **próximo índice não usado
  dentro do plugin**, com teto de 9 e escape declarado — unicidade sem exigir maximalidade, e com
  caminho legal para crescer.
- **B3.** "Instalar `claude-code` **pinado em `2.1.207`** para validar" é o antídoto direto de
  "contagem que cai sem FAIL": se o validador flutua, o número flutua sem que nada tenha mudado.
  A cadeia da Estrutura roda 1531/1531 PASS com validadores Python locais — pinar a versão do
  interpretador/ferramenta no CI é barato e fecha essa porta.
- **B3.** A conferência de **paridade entre dois catálogos** é o mesmo problema do cofre com
  `.claude/skills/` e `.agents/skills/`, resolvido por passo de CI que falha na divergência — não por
  `-SomenteVerificar` rodado à mão.
- **B4.** `description` ≤200 caracteres **incluindo near-negatives** é a versão econômica do limite
  legível: obriga o autor a gastar orçamento escasso na fronteira.

### O que não serve

Duas coisas, e uma delas é achado de **B5**:

1. O `AGENTS.md` manda, no checklist de publicação, rodar `quick_validate.py` para cada skill e
   `validate_plugin.py` para cada plugin. **Não encontrei nenhum dos dois** — a raiz do repositório
   (https://api.github.com/repos/levnikolaevich/claude-code-skills/contents/) tem `.agents`,
   `.claude-plugin`, `.github`, `plugins`, `site` e cinco arquivos soltos, sem pasta `scripts`; e
   `.github/` contém apenas `workflows/`. O `validate.yml` **não chama nenhum dos dois scripts** — ele
   roda `claude plugin validate` e PowerShell inline. Não fiz busca exaustiva dentro de `plugins/` e
   `site/`, então não afirmo que não existem; afirmo que **o caminho que o documento manda rodar não
   está onde o documento sugere, e o CI não os executa.** É o padrão "documentação que dirige ao
   erro" pego em campo, em repositório de terceiro: o mantenedor que seguir o checklist ao pé da
   letra roda um comando que falha, e o CI verde não o denuncia.
2. `CLAUDE.md` do repo é uma linha: *"Claude Code Instructions"* + `@AGENTS.md`
   (https://raw.githubusercontent.com/levnikolaevich/claude-code-skills/master/CLAUDE.md). Indireção
   pura. Não replicar: o cofre já sabe que `AGENTS.md` ambíguo custa caro.

---

## 4. `mukul975/Anthropic-Cybersecurity-Skills` — o frontmatter mais rico do lote, e uma contradição medida

### O que existe

Frontmatter lido **verbatim** num skill real
(https://raw.githubusercontent.com/mukul975/Anthropic-Cybersecurity-Skills/main/skills/analyzing-dns-logs-for-exfiltration/SKILL.md):

```yaml
name: analyzing-dns-logs-for-exfiltration
description: 'Analyzes DNS query logs to detect data exfiltration ... Use when SOC teams need to ...'
domain: cybersecurity
subdomain: soc-operations
tags: [soc, dns, exfiltration, dns-tunneling, dga, c2-detection, splunk, threat-detection]
version: '1.0'
author: mahipal
license: Apache-2.0
atlas_techniques: [AML.T0024, AML.T0056, AML.T0086]
nist_csf: [DE.CM-01, DE.AE-02, RS.MA-01, DE.AE-06]
mitre_attack: [T1048.003, T1071.004, T1567]
```

Layout por skill: `SKILL.md` + `references/standards.md` + `references/workflows.md` + `scripts/` +
`assets/`. O README (https://raw.githubusercontent.com/mukul975/Anthropic-Cybersecurity-Skills/main/README.md)
declara **817 skills**, cobertura por framework com denominador explícito ("805 of 817" para ATT&CK,
"804 of 817" para NIST CSF), validação dos IDs contra a biblioteca `mitreattack-python` e contra o
STIX bundle upstream, e uma declaração de escopo negativo forte:
*"This project is not a collection of scripts or checklists"* + cláusula de uso autorizado
("Only use against systems you own or have explicit written permission to test").

### A que buracos se aplica

- **B1 / B4.** É o único do lote que põe **mapeamento normativo verificável dentro do frontmatter**:
  `mitre_attack`, `nist_csf`, `atlas_techniques` são IDs de norma externa, conferíveis por máquina
  contra uma fonte upstream. Análogo direto para a Estrutura: um campo `regras_de_ouro: [RI-06, RO-10]`
  no frontmatter do `SKILL.md`, validável contra
  `Estrutura Final de Skills/regras-de-ouro/REGRAS-DE-OURO.md`. Hoje os 81 contratos **citam a norma
  por caminho relativo em prosa**; um array de IDs conferível transforma "o contrato menciona" em
  "o contrato declara quais, e o validador confirma que existem".
- **B3.** `version`, `author` e `license` no próprio `SKILL.md` — a identidade viaja com o artefato, não
  num manifesto separado que pode se descolar.

### O que não serve — e um achado de B5

O README afirma que o corpo de cada skill tem quatro seções: *When to Use, Prerequisites, Workflow,
**Verification***. No skill que li, as seções são: `When to Use`, `Prerequisites`, `Workflow`,
`Key Concepts`, `Tools & Systems`, `Common Scenarios`, `Output Format`. **Não há seção `Verification`.**
Amostra n=1, então não generalizo para as 817 — mas para o propósito deste garimpo basta: **a
anatomia declarada no README não é imposta por nada.** Confirma a regra da casa (a estrutura normativa
tem de morar dentro do validador, não no README) e desqualifica este repo como fonte de método de
verificação. Também: 817 skills sem eval harness é volume, não garantia — e a `description` de cada uma
compete com as outras 816 no mesmo índice, exatamente o mecanismo que a rodada 3 do cofre isolou.

---

## 5. `AMAP-ML/SkillClaw` — o único com digest, e o único com validação de skill por replay

### O que existe

**Digest de bundle** — `skillclaw/skill_bundle.py`
(https://raw.githubusercontent.com/AMAP-ML/SkillClaw/main/skillclaw/skill_bundle.py):
`_BUNDLE_ENTRYPOINT = "SKILL.md"` é obrigatório para o bundle ser válido. Cada arquivo vira um record
`{"path", "sha256", "size"}`. `bundle_tree_sha256()` produz **um digest único da árvore**, hasheando em
sequência caminho normalizado + SHA-256 do arquivo + tamanho. `normalize_bundle_rel_path()` converte
`\` em `/` e rejeita `..`, `.` e caminho vazio (anti-traversal). Ignora `.DS_Store`, `.git`,
`__pycache__`, `.pyc`/`.pyo`.

**Identidade** — `skillclaw/skill_manager.py`
(https://raw.githubusercontent.com/AMAP-ML/SkillClaw/main/skillclaw/skill_manager.py):
`name` validado por `_SAFE_NAME_RE = r"^[a-z][a-z0-9-]{1,63}$"`; `id` = `sha256(name)[:12]` —
**identidade derivada do nome, não do conteúdo**; `_CORE_FM_KEYS = {"name","description","metadata","category"}`
e todo campo fora desse conjunto é preservado em `"_extra_frontmatter"` para round-trip sem perda.
Não há versionamento local nem `meta.json`: há um contador `generation`, um `_skills_fingerprint`
`(realpath, mtime_ns, size)` para detectar edição externa, e estatísticas de uso em `skill_stats.json`
(`inject_count`, `positive_count`, `negative_count`, `effectiveness`, `last_injected_at`).

**Validação de skill candidata por replay** — `skillclaw/validation_worker.py`
(https://raw.githubusercontent.com/AMAP-ML/SkillClaw/main/skillclaw/validation_worker.py):
roda até 3 casos de replay comparando **skill candidata contra a skill vigente (baseline)**, pontua com
`prm_scorer`, e emite `"decision"` ∈ {`"accept"`, `"reject"`} com `"score"`, `"threshold"`
(`job.get("min_score", 0.75)`), `"reason"`, `"replay_summary"` (`case_count`, `baseline_mean_score`,
`candidate_mean_score`) e `"checks"`. Regra de aceite dupla: `candidate_mean >= threshold` **E**
`candidate_mean >= baseline_mean`.
`skillclaw/prm_scorer.py` é o juiz: prompt de +1/-1/0 ("helpful / unhelpful / unclear"), `prm_m = 3`
votos paralelos, temperature `0.6`, empate → `0.0`.

Versionamento remoto em `skillclaw/nacos_versions.py`: `_SEMVER_RE = ^(\d+)\.(\d+)\.(\d+)$` ou
`_V_VERSION_RE = ^v(\d+)$`, ponteiro `"latest"` em labels, próxima versão por incremento de patch.
**Sem digest** nessa camada.

### A que buracos se aplica

- **B3 / B4 — o achado mais alinhado à casa.** `bundle_tree_sha256()` é o mecanismo que a Estrutura já
  quis e sangrou: a conferência de capacidade por SHA-256 do CEO **não sobrevive a um clone**, porque
  EOL do checkout muda o hash. O SkillClaw resolve *metade*: normaliza o **separador de caminho**
  (`\`→`/`), o que mata o problema Windows/Unix de path. Mas o SHA-256 é sobre os **bytes do arquivo**
  — então **EOL continua mudando o digest** (inferência minha a partir do que li, não texto do repo).
  O que dá para importar hoje: (a) hashear a **árvore**, não arquivo a arquivo — um digest só para o
  pacote inteiro; (b) normalizar path antes de hashear; (c) excluir explicitamente `.git`,
  `__pycache__`, `.DS_Store` do digest, coisa que o cofre não faz.
- **B2, com número.** `skill_stats.json` com `inject_count`, `positive_count`, `negative_count` e
  `effectiveness` é telemetria de acionamento *em produção* — mede se a skill foi injetada e se ajudou.
  A Estrutura não tem nenhum contador do gênero.
- **B7 / evolução de skills.** O `validation_worker` é a resposta de outro autor à pergunta que o
  `departamento-evolucao-skills` faz: *a skill nova é melhor que a vigente?* Resposta: **replay contra
  baseline com dupla condição**, não nota absoluta. E o `prm_scorer` usa **3 votos e empate→0**, que é
  a contramedida direta do achado do cofre "nota de instância única não decide" (até 3 pontos de
  diferença entre instâncias da mesma lente; perto do corte, `NAO_DISCRIMINADO` — aqui, `0.0`).

### O que não serve

`id = sha256(name)[:12]` é hash **do nome**, não do conteúdo: identifica, não autentica. Não usar como
prova de integridade. E o `prm_scorer` é um juiz LLM com prompt de uma linha — muito abaixo do rigor
que a casa exige dos Juízes; importe o **protocolo** (baseline, m votos, empate neutro, dupla
condição), não o juiz.

---

## 6. `nutlope/hallmark` — o melhor exemplo de julgamento subjetivo virado gate binário numerado

### O que existe

`skills/hallmark/SKILL.md`
(https://raw.githubusercontent.com/nutlope/hallmark/main/skills/hallmark/SKILL.md), frontmatter
`name: hallmark`, `description`, `version: 1.1.0`.

**58 gates numerados, binários, citáveis por número.** Exemplos verbatim:
- gate 34 — *"no horizontal scroll + root `overflow-x: clip` on both `html` and `body`, never `hidden`"*
- gate 38a — *"Italic headers forbidden; carry emphasis via weight, accent colour, or underline"*
- gate 46 — métricas inventadas banidas ("+47 % conversion", "trusted by 50,000+ teams")
- gate 47 — *"Re-drawn UI chrome forbidden"* (barra de navegador falsa, moldura de celular)
- gate 48 — improvisação de token no meio do render banida; toda cor/fonte referencia token nomeado
- gate 54 — *"Tag-left / heading-right two-column pattern banned outright"*

**Constantes numéricas** em vez de adjetivos: headline ≤7 palavras / ≤50 caracteres; ≤3 primitivas de
microinteração por página; reduced-motion colapsa para ≤150ms; foco visível com contraste ≥3:1 e
**nunca animado**; tooltip 800ms no hover, 0ms no foco; verificação obrigatória em 320/375/414/768px.

**Autocrítica pré-emissão com carimbo no artefato.** Antes de devolver, pontua 6 eixos —
Philosophy, Hierarchy, Execution, Specificity, Restraint, Variety — de 1 a 5; **qualquer eixo <3
obriga revisão**; e as seis notas são **estampadas no topo do artefato**:
`/* Hallmark · pre-emit critique: P5 H4 E5 S4 R5 V5 */`.

**Divulgação progressiva com ordem imposta.** Quatro tiers de carregamento: eager (arquivo de gênero,
spec do tema), index-then-pick (`macrostructures.md` → carrega só `macrostructures/<NN-slug>.md`),
load-per-build (`typography.md`, `color.md`, `motion.md`, `anti-patterns.md`…), conditional
(`microinteractions.md`, `responsive.md`, `custom-theme.md`), e **load-at-end**: `slop-test.md` só no
passo 7. Regra explícita: *"Do not pre-load the full slop-test file before Step 7"* — o modelo **não
pode ver os critérios enquanto produz**, só quando é avaliado.

Memória de projeto em `.hallmark/log.json`: últimas 3–5 entradas alimentam diversificação, arquivo
podado em 20 entradas.

### A que buracos se aplica

- **B7 — o método.** Julgamento estético vira 58 asserções binárias com número estável. Número estável
  é o ponto: um achado pode dizer "violou gate 47" e isso é rastreável, contestável e diffável entre
  versões. É o mesmo movimento que a casa faz com RI/RO, aplicado a um domínio que "todo mundo sabe
  que é subjetivo".
- **B7 / B4.** **"Do not pre-load the slop-test before Step 7"** é a contramedida contra o gate
  tautológico que o cofre catalogou: se o produtor lê o critério enquanto produz, ele otimiza para o
  critério e o teste passa pela razão errada. Separação temporal produtor↔critério, imposta por
  ordem de carregamento. Aplicação direta na Estrutura: **o pacote julgado não deve carregar o
  `schemas/` dos Juízes antes de produzir**.
- **B4.** O carimbo `/* Hallmark · pre-emit critique: P5 H4 ... */` faz o **limite viajar dentro do
  artefato que o consumidor lê** — é exatamente a exigência da casa, resolvida com um comentário CSS
  de 50 bytes. E a lista "Do not" (13 itens, incluindo *"Do not delete production files/routes without
  explicit user approval"* e *"Do not emit `design.md` without attestation in URL mode"*) é limite
  operacional dentro do próprio `SKILL.md`.
- **B6.** Os quatro tiers de carregamento são um modelo de composição barato: em vez de 66 agentes
  como skills, um índice slim + carga sob demanda do arquivo escolhido.

### O que não serve

`version: 1.1.0` no frontmatter e nenhum digest — não há como provar qual conteúdo corresponde a 1.1.0.
E a autocrítica é **autoavaliada pelo mesmo agente que produziu**: viola a regra da casa de que nota é
ato exclusivo dos Juízes. Importe o **carimbo** e a **separação temporal**; a nota continua sendo de
terceiro.

---

## 7. `blader/humanizer` — catálogo de tells com estrutura fixa e regra anti-fabricação

### O que existe

https://raw.githubusercontent.com/blader/humanizer/main/SKILL.md — frontmatter `name: humanizer`,
`description` multilinha que **já enumera os padrões detectados**, `license: MIT`,
`metadata: {version: "2.9.1"}`.

**33 padrões, todos no mesmo formato de quatro campos:** título numerado → *"Words to watch"* (lista de
indicadores) → *"Problem"* (por que sinaliza IA) → *"Before"* → *"After"*. Ancorados numa fonte externa
citada: o guia "Signs of AI writing" da Wikipédia. Exemplos: padrão 8 é evitação de cópula
("serves as / stands as / marks / represents" no lugar de "is"); padrão 14 exige que a reescrita final
**não contenha nenhum travessão** (`—` ou `–`).

**Regra anti-fabricação, verbatim:** *"Never invent facts - The rewrite must not contain any fact, name,
number, date, quote, or citation that isn't in the source text."*

**Seção de falsos positivos declarados:** gramática perfeita sozinha, registro misto, prosa sem graça,
vocabulário formal, abertura em estilo de carta, palavra de transição isolada, afirmação sem fonte —
nenhum desses conta. Regra de agregação: **procurar aglomerados de tells, nunca tell isolado**.
Fluxo de dois passes: auditoria "obviously AI generated" antes da reescrita final.

### A que buracos se aplica

- **B7.** É o formato de achado mais próximo do que a Auditoria da casa produz: indicador observável →
  por que é problema → estado atual → estado corrigido. Quatro campos, zero adjetivo. Portável direto
  para o formato de achado da `departamento-auditoria-responsabilidades`.
- **B7, o achado real.** A **seção de falsos positivos** é o que quase nenhum repo do lote tem: o
  artefato declara **o que NÃO conta como evidência**. Isso é o antídoto de "reclassificar não é
  consertar" e de instrumento que acusa por ruído. Somado à regra de aglomerado (nunca tell isolado),
  é uma política de limiar de evidência escrita dentro do artefato que o executor lê.
- **B4.** *"Never invent facts"* é o "ausência de evidência permanece ausência" da casa, dito para um
  domínio de texto. Uma frase, dentro do artefato.

### O que não serve

Não há rubrica numérica nem gate executável — só exemplos before/after. É reconhecimento de padrão por
leitura, e o cofre já mediu que verificador de string ≠ prova de comportamento. Importe a **forma do
achado** e a **lista de falsos positivos**; não importe a ideia de que 33 exemplos bastam para reprovar.

---

## 8. `jakubkrehel/make-interfaces-feel-better` — o contrato de saída de revisão mais completo do lote

### O que existe

https://raw.githubusercontent.com/jakubkrehel/make-interfaces-feel-better/main/skills/make-interfaces-feel-better/SKILL.md
— frontmatter `name` + `description` (com lista longa de gatilhos literais, inclusive
*"make it feel better"* e *"feels off"*).

**Contrato de achado — 5 campos obrigatórios:** `Severity` (`HIGH` = bloqueia acessibilidade/uso,
`MEDIUM` = problema perceptível, `LOW` = polimento isolado, **só em modo full**), `Location`
(arquivo:linha ou identificador de componente), `Before`, `After`, `Why` (princípio violado + impacto
no usuário).

**Veredito de três valores, derivado da severidade, não escolhido:**
`Block` (existe `HIGH` não resolvido) · `Needs changes` (só `MEDIUM`/`LOW`) · `Approve` (nenhum achado
acionável).

**Seções obrigatórias do relatório:** tabela de *evidência inspecionada* cobrindo as cinco categorias do
Quick Reference; achados agrupados por princípio; **1–3 candidatos rejeitados em modo `quick`, 2–5 em
modo `full`**; log de verificação; e o veredito **com os checks não verificados listados**.

**Limiares numéricos** em vez de adjetivo: área de toque 44×44px (mobile) / 40×40px (desktop denso);
escala de press **exatamente `0.96`, nunca abaixo de `0.95`**; stagger ~100ms; animação de ícone
scale `0.25`→`1`, opacity `0`→`1`, blur `4px`→`0`; duração `0.3s` com `bounce: 0`; outline de imagem
`1px` a `0.1` de opacidade.

Referências separadas por assunto no mesmo diretório: `typography.md`, `surfaces.md`, `animations.md`,
`icons.md`, `performance.md`. Instrução de instalação manual: *copiar o diretório inteiro* para
preservar os links relativos.

### A que buracos se aplica

- **B4 — o achado mais forte deste repo.** Duas exigências que a Estrutura deveria copiar hoje:
  **(a) "candidatos rejeitados" com contagem mínima obrigatória** (1–3 / 2–5) — obriga o revisor a
  provar que olhou e descartou, o que é o oposto de "não achei nada"; e **(b) o veredito tem de listar
  os checks NÃO verificados.** Isso é "ausência de evidência permanece ausência" **materializada
  dentro do artefato de saída**, com contagem — e é diretamente auditável por schema.
- **B7.** Veredito **derivado** da severidade máxima (`HIGH` presente ⇒ `Block`), não escolhido pelo
  autor. É a regra da casa "veredito não mora dentro do artefato julgado" resolvida pela via
  aritmética: o revisor classifica achados, a função calcula o veredito.
- **B1.** É o exemplo mais próximo de um "contrato" no sentido da casa — mas expresso como **contrato
  de saída** (o que o artefato produzido deve conter), não como contrato de compromisso do executor.
  Deslocamento útil: talvez parte das 12 seções do `CONTRATO-DE-COMPROMISSO.md` renda mais como
  schema do output do que como declaração do executor.

### O que não serve

Nenhuma seção declara o que a skill **recusa** mudar — a fronteira é só por gatilho positivo. E os
limiares (`0.96`, 44px, 100ms) estão em prosa markdown, sem validador. Sem código, é a mesma armadilha
já catalogada.

---

## 9. `leonxlnx/taste-skill` — dials como parâmetro declarado + escopo negativo explícito

### O que existe

https://raw.githubusercontent.com/leonxlnx/taste-skill/main/skills/taste-skill/SKILL.md — frontmatter
`name: design-taste-frontend` + `description` (note: **o `name` do frontmatter difere do nome do
diretório `taste-skill`** — exatamente o que o linter do addyosmani reprovaria).

**Três dials 1–10 declaradas no topo do arquivo:** `DESIGN_VARIANCE` (simetria→assimetria),
`MOTION_INTENSITY` (estático→coreografado), `VISUAL_DENSITY` (galeria→cockpit). Baseline `8 / 6 / 4`.
As dials **governam decisões downstream**: p.ex. reduced-motion vira obrigatório quando
`MOTION_INTENSITY > 3`.

**Escopo negativo dentro do artefato:** *"Not for dashboards, data tables, or multi-step product UI."*
Lista completa do que não cobre: dashboards, tabelas de dados, painéis admin, formulários multi-etapa,
editores de código, mobile nativo, UI colaborativa em tempo real.

**Pre-Flight Check (Seção 14): matriz mecânica pass/fail** — qualquer caixa reprovada torna a saída
incompleta. Condições que são **Pre-Flight Fail** por nome: intenção de CTA duplicada; animação sem
justificativa declarada.
**Passo 0 — Brief Inference:** antes de qualquer código, declarar em voz alta
*"Reading this as: [page kind] for [audience], with a [vibe] language, leaning toward [system]"*.
Banimento absoluto de travessão (Seção 9.G). Lista de "AI tells" banidos por padrão (gradiente roxo,
Inter como default, nomes genéricos "John Doe", números falso-perfeitos 99,99%, SVG feito à mão).

### A que buracos se aplica

- **B4.** O escopo negativo é **uma lista, dentro do `SKILL.md`, do que a skill não faz** — legível e
  extraível. Convergência com ZeroPointRepo (que põe a mesma coisa na `description`).
- **B7.** As dials são o mecanismo mais interessante: em vez de tentar definir "bom gosto", parametrizam
  o eixo e **declaram o valor usado**. Aplicação na Estrutura: `EXECUTIVE_MISSION` poderia carregar
  dials explícitas — rigor de auditoria, tolerância a INDETERMINADO, profundidade de evidência —
  registradas com a missão em vez de negociadas por conversa.
- **B2.** O passo 0 (declarar a leitura do briefing antes de agir) é uma barreira de entrada barata,
  e é o que o CEO já faz ao recusar missão com alvo genérico. Convergência independente.

### O que não serve

Mismatch `name` × diretório é defeito, não modelo. E as três dials são lidas por um LLM a partir de
markdown — não há schema, não há default checado, não há validador. Parametrizar sem validar deixa o
parâmetro derivar em silêncio.

---

## 10. `resemble-ai/detect-skill` — bandas de score e a proibição de veredito sem evidência

> Nota: o repositório usa branch **`master`**, não `main`. `main/README.md` e `main/SKILL.md` deram 404.

### O que existe

https://raw.githubusercontent.com/resemble-ai/detect-skill/master/SKILL.md — frontmatter
`name: resemble-detect` + `description`. Arquivo único.

**Bandas numéricas com veredito textual fixo:**

| Faixa | Veredito |
|---|---|
| 0.0–0.3 | "Strong indication of authentic/real media" |
| 0.3–0.5 | **"Inconclusive — recommend additional analysis"** |
| 0.5–0.7 | "Likely synthetic — flag for review" |
| 0.7–1.0 | "High confidence synthetic/AI-generated" |

**Princípio inegociável, em caixa alta:** *"NEVER DECLARE MEDIA AS REAL OR FAKE WITHOUT A COMPLETED
DETECTION RESULT."* Toda afirmação exige um job concluído devolvendo `label`, `score` e
`status: "completed"`.

**Red Flags / antipadrões nomeados:** declarar autenticidade sem detecção concluída; ignorar
`status` (`processing` não gera veredito; `failed` tem de ser reportado); **reportar `label` sem o
`score`** — *"a `fake` at 0.51 differs fundamentally from 0.95"*; enviar `file`, `url` e `media_token`
juntos (mutuamente exclusivos); polling sub-segundo; pedir Detect Intelligence antes da conclusão
(retorna `422`); imprimir bearer token.
**Limite de reivindicação:** o agente **nunca** deve afirmar que o resultado constitui prova absoluta,
evidência legal ou determinação final.

### A que buracos se aplica

- **B4 — porte imediato.** Três coisas que a casa já quer e aqui estão em cinco linhas dentro do
  artefato: (1) **banda explícita de INCONCLUSIVO** (0.3–0.5) como resultado de primeira classe, não
  como falha — o `NAO_DISCRIMINADO`/`INDETERMINADO` da casa, com faixa numérica; (2) **veredito
  proibido sem execução concluída**, checado por campo (`status: "completed"`), que é a regra
  "SKIP declarado, nunca um 'passou' fingido" com o campo que a prova; (3) **teto de reivindicação
  declarado** — "não é prova legal" — dentro do arquivo que o consumidor lê.
- **B7.** *"reportar `label` sem `score` é antipadrão"* é regra de método valiosa: o veredito **nunca**
  viaja sem a medida que o gerou. Aplicável literalmente ao relatório dos Juízes.

### O que não serve

Nada sobre empacotamento, versão ou digest — é um `SKILL.md` solto. E as bandas são do fornecedor da
API, não derivadas nem justificadas no arquivo.

---

## 11. `charlie947/social-media-skills` — cascata por artefato compartilhado e rubrica de 5×10

### O que existe

17 skills em `skills/<nome>/` (https://api.github.com/repos/charlie947/social-media-skills/contents/skills).

**A fundação — `voice-builder`**
(https://raw.githubusercontent.com/charlie947/social-media-skills/main/skills/voice-builder/SKILL.md):
frontmatter `name` + `description`, e a `description` **declara os artefatos de saída**:
*"Always produces two files (about-me.md and voice.md) saved into the project root."* Estruturas fixas:
`about-me.md` (<300 palavras: Name and role, Audience, Topic pillars, Point of view, Brand promise,
**Off limits**) e `voice.md` (<500 palavras: Who I sound like, Tone, Sentence rhythm, Hook patterns,
How I open, How I close, Signature phrases, **Off-limits**, **What this voice never does**).

**"Absence patterns", verbatim:** *"Words, punctuation, or constructions absent from every sample. Only
list items the samples clearly avoid."* — com evidência contada: *"no em dashes (0 of 5 samples)"*.

**A rubrica — `post-scorer`**
(https://raw.githubusercontent.com/charlie947/social-media-skills/main/skills/post-scorer/SKILL.md):
5 dimensões × 1–10 = **50 pontos**: Hook strength, Voice match, Value density, Structure and format,
Publish readiness. Cada dimensão é ancorada em dado do próprio usuário (top 10% dos posts dele), não em
boa prática genérica. **Degradação declarada em 3 níveis**: histórico cacheado do usuário → benchmarks
externos (Charlie Hills) → boas práticas genéricas. Regra final: *"Every fix must cite specific
data — never generic advice."*

### A que buracos se aplica

- **B6 — o modelo de composição mais barato do lote.** 17 skills se compõem **sem se chamar**: uma
  produz dois arquivos em local convencionado, as outras 16 leem. É a mesma decisão do
  levnikolaevich ("skills communicate only through documents") vista de outro ângulo, e **dois autores
  independentes convergiram nela**. Para os 66 agentes-folha da Estrutura, isso é a alternativa a
  fazê-los skills: fronteira exclusiva mantida por *quem escreve qual arquivo*, e não por
  quem pode chamar quem.
- **B4.** `voice.md` tem seção literal **"What this voice never does"**, e `about-me.md` tem
  **"Off limits"** — o limite é uma seção nomeada do artefato, não prosa.
- **B7.** As **absence patterns** são metodologicamente o achado: em vez de descrever o estilo pelo que
  ele é (subjetivo), descrevem pelo que ele **nunca contém**, com **contagem de amostras** ("0 de 5").
  Negativo verificável bate positivo interpretável. Direto para a Auditoria.
- **B7.** A degradação em 3 níveis com obrigação de citar a fonte do dado é a versão de conteúdo do
  "SKIP declarado": quando não há histórico, a skill **diz** que caiu para genérico.

### O que não serve

A rubrica de 50 pontos é atribuída por LLM sem calibração, sem múltiplas instâncias e sem faixa de
indeterminação — o cofre já mediu que instância única não decide perto do corte. E não há corte
declarado (o que acontece com 34/50?). Importe absence patterns e degradação declarada; a nota não.

---

## 12. `nextlevelbuilder/ui-ux-pro-max-skill` — manifesto de distribuição multiplataforma

### O que existe

`skill.json` na raiz (https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main/skill.json),
**lido verbatim**: `name`, `displayName`, `description`, `version: "2.11.0"`, `author`, `license`,
`homepage`, `repository`, `keywords[]`, **`platforms[]` com 19 runtimes nomeados** (claude, cursor,
windsurf, copilot, kiro, roocode, kilocode, codex, qoder, gemini, trae, opencode, continue, codebuddy,
droid, warp, augment, antigravity, openclaw) e `"install": "npx ui-ux-pro-max-cli init --ai {{platform}}"`
— comando de instalação **parametrizado pela plataforma, dentro do manifesto**.
Raiz tem `.releaserc.json` (semantic-release), `.claude-plugin/`, `cli/`, `src/`, `stack/`, `projects/`.

Do README (https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main/README.md):
motor de decisão com 161 regras por indústria, cada uma com Recommended Pattern, Style Priority
(ranqueada por **BM25**), Color Mood, Typography Mood, Key Effects e **Anti-Patterns** explícitos
("AI purple/pink gradients for banking"); dados em CSV + scripts Python **stdlib apenas, offline, sem
chamada de rede**; e uma "PRE-DELIVERY CHECKLIST" com itens binários (sem emoji como ícone,
`cursor-pointer` em clicável, transições 150–300ms, contraste ≥4.5:1, `prefers-reduced-motion`,
breakpoints 375/768/1024/1440px).

### A que buracos se aplica

- **B3.** `skill.json` com `version` + `platforms[]` + `install` parametrizado é o manifesto que a
  Estrutura não tem. Hoje o deploy do cofre é um `.ps1` com `-Runtime Ambos`; a lista de runtimes está
  no script, não num manifesto declarativo versionado junto com o pacote. Inverter isso torna a
  paridade `.claude/` × `.agents/` conferível **a partir do dado**, não a partir do código do deploy.
- **B7.** BM25 para ranquear estilo por consulta é a única técnica de *recuperação determinística* do
  lote — recomendação sem LLM no caminho crítico, reprodutível. Casa com a tese de
  `assistente-deterministico`.

### O que não serve — e um achado de B5

O README descreve uma arquitetura de persistência `design-system/MASTER.md` + `pages/<page>.md` com
override por página. **Fui verificar em `projects/healthcare-dashboard` e a pasta contém um único
arquivo: `index.html`**
(https://api.github.com/repos/nextlevelbuilder/ui-ux-pro-max-skill/contents/projects/healthcare-dashboard).
`design-system/MASTER.md` deu 404 lá. As três pastas de `projects/` são `healthcare-dashboard`,
`portfolio-dark`, `saas-landing`. Ou seja: **o padrão MASTER+overrides está documentado no README e não
está demonstrado no exemplo que o enunciado mandou olhar.** Não afirmo que o padrão não exista em
outro lugar do repo; afirmo que o exemplo não o contém. Mesmo defeito do mukul975 — README como fonte
da verdade sem nada que o obrigue.

---

## 13. `composio-community/skills` — geração de arquivo consolidado a partir de fontes por regra

### O que existe

https://raw.githubusercontent.com/composio-community/skills/main/skills/composio/SKILL.md — frontmatter
`name: composio`, `description`, **`tags: [composio, tool-router, agents, mcp, tools, api, automation, cli]`**.
Estrutura em três peças: `SKILL.md` (visão + ponteiros), `rules/*.md` (regras individuais) e
**`AGENTS.md` gerado automaticamente** por `scripts/build-agents.cjs` (`npm run build:agents`), com
`scripts/watch-agents.cjs` para rebuild em watch. Divulgação progressiva por bifurcação de caso de uso:
caminho CLI → `rules/composio-cli.md`; caminho SDK → `rules/building-with-composio.md`.
Segundo o README, cada arquivo de `rules/` exige frontmatter com `title`, **`impact` (CRITICAL|HIGH|MEDIUM|LOW)**,
`description` e `tags[]`; o build injeta índice e "impact badges".

### A que buracos se aplica

- **B1 / B3.** O campo **`impact` com 4 níveis no frontmatter de cada regra** é a coisa mais próxima de
  severidade normativa por arquivo neste lote. Se as RI/RO da casa fossem arquivos individuais com
  `impact`, o `AGENTS.md` de topo poderia ser **gerado** com badge de severidade, em vez de mantido à
  mão — e a divergência entre a norma e o resumo (hoje `Regras de Ouro e Inquebráveis.md` é
  "resumo-atalho" mantido manualmente) deixaria de ser possível.
- **B5.** Artefato **derivado** (`AGENTS.md` gerado) elimina a classe de erro em que o resumo e a
  fonte discordam. Isso é o mesmo princípio de `TAREFAS.md` como view de `estado.json` — e vale a
  pena estendê-lo à norma.

### O que não serve / não li

Não li nenhum arquivo de `rules/` — os campos `title`/`impact`/`description`/`tags` vêm **só do
README**, não de um arquivo de regra que eu tenha aberto. Também não li `build-agents.cjs`. Não há
versionamento, manifesto de índice nem CI declarados no README. Trate `impact` como *ideia lida*, não
como *campo verificado*.

---

## 14. `ZeroPointRepo/youtube-skills` — frontmatter operacional: dependências e limite na própria description

### O que existe

https://raw.githubusercontent.com/ZeroPointRepo/youtube-skills/main/skills/youtube-full/SKILL.md,
frontmatter lido verbatim — o mais operacional do lote:

```yaml
name: youtube-full
description: "Use when YouTube is or could be relevant — even if not mentioned: pasted video/channel/playlist
  links, video IDs, @handles, ... Not for uploads, account management, or written-source-only research."
version: "1.5.0"
user-invocable: true
compatibility: Requires internet access to reach transcriptapi.com. No additional runtimes or dependencies needed.
required_environment_variables:
  - name: TRANSCRIPT_API_KEY
    prompt: Your TranscriptAPI key (starts with sk_)
    help: Free account at https://transcriptapi.com — 100 credits, no card required.
    required_for: all API requests
metadata: {"openclaw":{...,"requires":{"env":["TRANSCRIPT_API_KEY"]}},"hermes":{"tags":[...],"category":"media"}}
```

### A que buracos se aplica

- **B4 — o melhor exemplo do lote.** O limite viaja **na mesma frase do gatilho**:
  *"Not for uploads, account management, or written-source-only research."* Não é seção separada que o
  runtime descarta ao indexar — é o **mesmo campo** que o runtime lê para decidir. Se a casa quer que o
  limite chegue a quem escolhe, tem de estar onde a escolha é feita.
- **B1.** `required_environment_variables[]` com sub-campos (`name`, `prompt`, `help`, `required_for`) é
  **pré-condição declarada em estrutura**, não em prosa — a máquina sabe o que falta e sabe o que
  perguntar. A Estrutura tem pré-condições (o `EXECUTIVE_MISSION`, o relatório vigente dos Juízes) e as
  descreve em texto; este é o formato para declará-las.
- **B1.** `compatibility` como campo curto e literal ("requer internet; sem outras dependências") é
  fronteira de ambiente em uma linha.
- **B3.** `metadata` como **mapa por runtime** (`openclaw`, `hermes`) resolve multiplataforma sem
  fragmentar o arquivo — um `SKILL.md`, N runtimes.

### O que não serve

`description` de ~90 palavras num só campo é agressiva na disputa por atenção; sem eval (que este repo
não tem) não há como saber se ajuda ou se canibaliza vizinhos. O modelo de crédito pago e o fluxo de
OTP por e-mail são irrelevantes aqui.

---

## 15. `kepano/defuddle` — não é skill; serve por analogia de método

### O que existe

https://raw.githubusercontent.com/kepano/defuddle/main/README.md — biblioteca npm de extração de
conteúdo (origem: Obsidian Web Clipper). Heurísticas nomeadas como opções: `removeLowScoring`
(pontua blocos não-conteúdo, tipo navegação e listas de link), `removeExactSelectors` /
`removePartialSelectors`, `removeHiddenElements`, `removeSmallImages`, e uso dos **estilos mobile** da
página como pista do que é supérfluo. Retorno estruturado com `parseTime`, `wordCount`, `metaTags`,
`schemaOrgData`, `debug`. Três bundles: `defuddle` (core, sem dependências), `defuddle/full`,
`defuddle/node`. Posicionamento declarado contra o Readability: *"more forgiving, removes fewer
uncertain elements"*.

### A que buracos se aplica

- **B7, por analogia.** Duas ideias transferíveis: (1) **remover o certo, preservar o incerto** —
  política de erro assimétrica declarada, que é a postura correta de uma Auditoria (na dúvida, o
  achado fica, marcado como incerto, em vez de ser descartado); (2) **`debug` e `parseTime` no retorno**
  — o resultado carrega o rastro de como foi produzido.
- **B3.** Bundles em camadas (`core` sem dependência / `full` / `node`) é o análogo de
  divulgação progressiva aplicado ao **pacote**, não ao texto.

### O que não serve

Não tem `SKILL.md`, frontmatter, gatilho nem contrato — não é skill. Nada de B1–B6 aqui. O README avisa
*"Beware! Defuddle is very much a work in progress!"* e não declara limites. Não li o código de
scoring, então **não afirmo nada sobre como a pontuação é calculada** além dos nomes das opções.

---

## 16. O que eu NÃO consegui ler (declarado)

- **`composio-community/skills`:** nenhum arquivo de `rules/*.md`; `scripts/build-agents.cjs` não lido.
  Os campos `title`/`impact`/`description`/`tags` vêm do README, não de arquivo verificado.
- **`levnikolaevich/claude-code-skills`:** `quick_validate.py` e `validate_plugin.py`, citados no
  checklist do `AGENTS.md`, **não localizados** na raiz nem em `.github/`. Não busquei dentro de
  `plugins/` e `site/`.
- **`nextlevelbuilder/ui-ux-pro-max-skill`:** `design-system/MASTER.md` do `healthcare-dashboard`
  não existe (404); a pasta tem só `index.html`. Não li `src/`, `cli/` nem os CSV/scripts Python.
- **`mukul975/Anthropic-Cybersecurity-Skills`:** amostrei **1** das 817 skills. A ausência da seção
  `Verification` vale para essa amostra, não para o conjunto.
- **`kepano/defuddle`:** só o README; o algoritmo de scoring não foi lido.
- **`AMAP-ML/SkillClaw`:** li 4 dos 25 módulos (`skill_bundle`, `skill_manager`, `prm_scorer`,
  `validation_worker`); não li `protocols/`, `skill_hub.py` nem `evolve_server/`.
- **`resemble-ai/detect-skill`:** branch é `master`; `main/` retorna 404 — registrado para quem repetir
  a medição.

---

## 17. Os três achados mais fortes

1. **`addyosmani/agent-skills` transformou "a skill dispara?" em métrica com piso de CI.**
   `evals/cases/<skill>.json` com `trigger.positive[].top_k`, `trigger.negative[].owner`, **rank-1 rate
   com mínimo de 80% e baseline 86%**, e erro de colisão quando duas `description` passam de 75% de
   similaridade. Somado ao `SessionStart` hook que injeta a meta-skill e ao `AGENTS.md` imperativo
   (*"you MUST invoke it"*, *"Never implement directly if a skill applies"*), é a versão instrumentada
   da descoberta que o cofre fez por observação em 2026-07-27. Porte prioritário.
   URLs: `evals/README.md`, `evals/cases/code-review-and-quality.json`, `scripts/lib/skill-lint.js`,
   `hooks/hooks.json`, `AGENTS.md`.

2. **`jakubkrehel` + `resemble-ai` + `nutlope` resolvem, juntos, o limite legível por máquina (B4).**
   jakubkrehel: veredito **derivado** da severidade máxima (`HIGH`⇒`Block`), **1–3 / 2–5 candidatos
   rejeitados obrigatórios**, e o veredito tem de **listar os checks não verificados**.
   resemble-ai: banda **0.3–0.5 = "Inconclusive"** como resultado de primeira classe, veredito proibido
   sem `status: "completed"`, e teto de reivindicação declarado ("não é prova legal").
   nutlope: o limite **carimbado dentro do artefato** (`/* Hallmark · pre-emit critique: P5 H4 E5 S4 R5 V5 */`)
   e a regra *"do not pre-load the slop-test before Step 7"* — o produtor não vê o critério enquanto
   produz, que é a trava contra o gate tautológico.

3. **Composição sem chamada: dois autores independentes chegaram à mesma regra.**
   levnikolaevich (`AGENTS.md`): *"It must not require another skill... Skills communicate only through
   documents"*; charlie947: `voice-builder` escreve `about-me.md` + `voice.md` na raiz e as outras 16
   skills leem. Para os 66 agentes-folha da Estrutura, isto é a alternativa a torná-los invocáveis: a
   fronteira exclusiva passa a ser **quem escreve qual arquivo**, não quem pode chamar quem — e vira
   auditável por diff. Complemento: `mattpocock` declara o mesmo limite como **campo**
   (`disable-model-invocation: true`, com a regra "user-invoked nunca chama user-invoked"), o que é
   mais robusto que a trava atual da casa, que depende de **não existir** `SKILL.md` nos 81 pacotes.
