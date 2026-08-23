# JUDGE_OPINION — CRIT-08 — ótica robustez-e-evidencia

- **Data do julgamento:** 2026-07-28
- **Critério:** CRIT-08 (LINKS, PROFUNDIDADE E FONTE NORMATIVA)
- **Candidato:** `.claude/skills/ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-inovacao-melhoria` (runtime)
- **Digest do pacote (conferido pelo topo, não recalculado aqui):**
  `bbcae76833d7d54d051af903b7949e478272c720743cd176c1a0c1acc3fd4f58`
- **Raiz da Estrutura no runtime:** `.claude/skills/`
- **Método:** extração de todo token com aparência de caminho nos arquivos em escopo,
  resolução a partir da profundidade real do arquivo **citante** (não da raiz do pacote),
  e prova de existência por `ls` do alvo normalizado.

---

## 1. Veredito

**Nota 10 / 10 — VALIDATED.**

Os 23 caminhos no escopo literal do critério resolvem para arquivo ou diretório existente.
A fonte normativa é única, correta e apenas referenciada. Não há versão paralela das
Regras de Ouro dentro do pacote. Nenhuma falha objetiva encontrada.

---

## 2. Aritmética de profundidade — o ponto central do critério

O pacote cita a fonte normativa a partir de **três profundidades distintas**, e as três
estão certas. Este era o modo mais provável de falhar, e o pacote não falhou:

| Arquivo citante | Profundidade abaixo de `.claude/skills/` | `../` citados | Resolve em |
|---|---|---|---|
| `SKILL.md`, `CONTRATO-DE-COMPROMISSO.md` (raiz do pacote) | 4 | `../../../../` | `.claude/skills/regras-de-ouro/REGRAS-DE-OURO.md` ✅ |
| `references/protocolo-inovacao-melhoria.md` | 5 | `../../../../../` | idem ✅ |
| `agentes/*/SKILL.md` e `agentes/*/CONTRATO-DE-COMPROMISSO.md` | 6 | `../../../../../../` | idem ✅ |

Contagem de segmentos a partir da raiz: `ceo-maestro`(1) / `diretor-de-lentes`(2) /
`departamentos-operacionais`(3) / `departamento-inovacao-melhoria`(4) / `agentes`(5) /
`agente-X`(6). Cada citante usa exatamente o número de saltos da sua própria posição.

**Reforço encontrado (não exigido pelo critério, mas relevante para a minha ótica):** o
mesmo salto está travado em código, e concorda com a prosa. Em
`evals/validate_workflow.py:57`:

```python
STRUCTURE_ROOT = PACKAGE_ROOT.parents[3]
...
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"
```

`parents[3]` a partir da raiz do pacote é o mesmo alvo dos `../../../../` do Markdown.
Prosa e validador não divergem — a profundidade não é só documentada, é conferida.
Isto atende ao padrão "trave em código, não em texto".

---

## 3. Caminhos conferidos — escopo literal do critério (23/23 OK)

### 3.1 `SKILL.md` (raiz do pacote) — 9

| Linha | Caminho citado | Resultado |
|---|---|---|
| 32, 98 | `agentes/` (diretório) | OK |
| 48 | `CONTRATO-DE-COMPROMISSO.md` | OK |
| 54 | `references/protocolo-inovacao-melhoria.md` | OK |
| 57 | `references/fronteiras-e-fontes-canonicas.md` | OK |
| 59 | `references/origem-migracao.md` | OK |
| 62 | `references/adr-013-tres-agentes-e-inovacao-sem-julgamento.md` | OK |
| 66 | `schemas/departamento-inovacao-melhoria.schema.json` | OK |
| 68 | `../../schemas/diretor-de-lentes.schema.json` | OK — cai em `ceo-maestro/diretor-de-lentes/schemas/` |
| 407 | `../../../../regras-de-ouro/REGRAS-DE-OURO.md` | OK |

### 3.2 `CONTRATO-DE-COMPROMISSO.md` (raiz do pacote) — 2

| Linha | Caminho citado | Resultado |
|---|---|---|
| 55 | `schemas/departamento-inovacao-melhoria.schema.json` | OK |
| 171 | `../../../../regras-de-ouro/REGRAS-DE-OURO.md` | OK |

### 3.3 `agentes/agente-descoberta-de-oportunidades/SKILL.md` — 4

| Linha | Caminho citado | Resultado |
|---|---|---|
| 23 | `CONTRATO-DE-COMPROMISSO.md` | OK |
| 25 | `../../references/protocolo-inovacao-melhoria.md` | OK |
| 31 | `../../references/adr-013-tres-agentes-e-inovacao-sem-julgamento.md` | OK |
| 196 | `../../../../../../regras-de-ouro/REGRAS-DE-OURO.md` | OK |

### 3.4 `agentes/agente-experimentos-e-spikes/SKILL.md` — 4

| Linha | Caminho citado | Resultado |
|---|---|---|
| 22 | `CONTRATO-DE-COMPROMISSO.md` | OK |
| 24 | `../../references/protocolo-inovacao-melhoria.md` | OK |
| 30 | `../../references/adr-013-tres-agentes-e-inovacao-sem-julgamento.md` | OK |
| 221 | `../../../../../../regras-de-ouro/REGRAS-DE-OURO.md` | OK |

### 3.5 `agentes/agente-melhoria-continua/SKILL.md` — 4

| Linha | Caminho citado | Resultado |
|---|---|---|
| 22 | `CONTRATO-DE-COMPROMISSO.md` | OK |
| 24 | `../../references/protocolo-inovacao-melhoria.md` | OK |
| 30 | `../../references/adr-013-tres-agentes-e-inovacao-sem-julgamento.md` | OK |
| 205 | `../../../../../../regras-de-ouro/REGRAS-DE-OURO.md` | OK |

**Quebrados no escopo literal: 0.**

---

## 4. Fora do texto literal do critério — registrado, não penalizado

O critério nomeia `SKILL.md`, `CONTRATO-DE-COMPROMISSO.md` e as `SKILL.md` dos agentes.
Os itens abaixo ficam fora dessa lista; confiro e registro sem efeito na nota.

### 4.1 `agentes/*/CONTRATO-DE-COMPROMISSO.md` — 6 caminhos, 6 OK

- `agente-descoberta-de-oportunidades/CONTRATO-DE-COMPROMISSO.md:103` e `:107`
- `agente-experimentos-e-spikes/CONTRATO-DE-COMPROMISSO.md:111` e `:115`
- `agente-melhoria-continua/CONTRATO-DE-COMPROMISSO.md:118` e `:122`

Todos citam `../../../../../../regras-de-ouro/REGRAS-DE-OURO.md` e
`../../references/protocolo-inovacao-melhoria.md`. Profundidade correta, alvos existentes.

### 4.2 `references/protocolo-inovacao-melhoria.md` — arquivo alterado nesta rodada

O acréscimo do **R9** (linhas 444–451, datado 2026-07-28) **não introduziu nenhum caminho
relativo novo**. Ele referencia apenas seções (`§`) e a medição `departamento=0 ; agente=0`.
Nada a conferir de link no delta.

Os 7 caminhos do rodapé "Relacionado" (linhas 460–465) foram conferidos e resolvem:

| Caminho | Resultado |
|---|---|
| `../SKILL.md` | OK |
| `../CONTRATO-DE-COMPROMISSO.md` | OK |
| `fronteiras-e-fontes-canonicas.md` | OK |
| `adr-013-tres-agentes-e-inovacao-sem-julgamento.md` | OK |
| `origem-migracao.md` | OK |
| `../schemas/departamento-inovacao-melhoria.schema.json` | OK |
| `../../../../../regras-de-ouro/REGRAS-DE-OURO.md` | OK (5 saltos, correto de `references/`) |

### 4.3 `references/fronteiras-e-fontes-canonicas.md` — tabela de proveniência

A tabela "Fontes internas consultadas" (linhas 20–26) lista 7 caminhos do **Catálogo**
(`Catalogo-Skills-Unificado/...`). São referências **relativas à raiz do cofre**, não à
profundidade do pacote, e são registro de proveniência de migração — não declaração de
fonte normativa vigente. Verifiquei os 7 contra o cofre: **os 7 existem**.

Como a minha fronteira é "referência que não sustenta o que alega", testei o mais forte
deles — o único que cita Regras de Ouro:

- Alegado: `Catalogo-Skills-Unificado/REGRAS-DE-OURO.md`, SHA-256
  `06341DB894EF2CCCA12315B902CC5D09A76D1421ADE01898C0DC2BB514CA0E73`
- Recalculado nesta checagem: `06341DB894EF2CCCA12315B902CC5D09A76D1421ADE01898C0DC2BB514CA0E73`
- **Confere.** A alegação → evidência → artefato real fecha.

---

## 5. Fonte normativa — `fonte_normativa_ok: true`

1. **Caminho exigido pelo critério:** `../../../../regras-de-ouro/REGRAS-DE-OURO.md`.
   É exatamente o que `SKILL.md:407` e `CONTRATO-DE-COMPROMISSO.md:171` citam, e resolve
   em `.claude/skills/regras-de-ouro/REGRAS-DE-OURO.md` (21.761 bytes, presente).
2. **Referenciada, não copiada.** As 31 ocorrências de `RI-0x` / `RO-x` / "Regras de Ouro"
   no pacote (12 arquivos) são todas **menção nominal ou link** — nomeiam a regra e apontam
   para o arquivo. Nenhuma reproduz o texto normativo.
3. **Sem versão paralela dentro do pacote.** Confirmado por `ls`: não existe
   `departamento-inovacao-melhoria/regras-de-ouro/` nem
   `departamento-inovacao-melhoria/REGRAS-DE-OURO.md`. O inventário completo do pacote
   (24 arquivos) não contém nenhum arquivo de regras.
4. A citação do `Catalogo-Skills-Unificado/REGRAS-DE-OURO.md` em §4.3 **não** constitui
   fonte normativa concorrente: está sob o título "Fontes internas consultadas", em tempo
   passado, com digest — é proveniência da migração, e o cofre já documenta que a cópia da
   Estrutura é a adaptação organizacional daquela. Não vejo aqui duas normas vigentes.

---

## 6. Observações sem efeito na nota

- **Agentes não citam schema.** Nenhuma `agentes/*/SKILL.md` cita
  `schemas/...schema.json`; chegam ao schema pelo protocolo. Não é link quebrado — é
  ausência de citação, fora do texto do CRIT-08. Registro apenas como nota de cobertura.
- **Fragilidade latente de digest (não incide aqui).** A tabela de §4.3 ancora proveniência
  em SHA-256 de arquivo. Neste checkout o hash bate; num clone com normalização de EOL
  diferente ele mudaria sem que o conteúdo normativo mudasse. É risco conhecido de
  identidade-por-digest, não falha de link, e o CRIT-08 não o cobre. Fica registrado para
  quem cuidar de proveniência.
- **`LEGACY_ROOT` do validador** (`validate_workflow.py:67-74`) aponta para
  `STRUCTURE_ROOT.parent / "SKILL - Nova formula" / ...`, inexistente no runtime, mas é
  sobrescrevível por `INNOVATION_LEGACY_ROOT`. É caminho de eval, não caminho citado em
  `SKILL.md`/contrato/agente — fora do CRIT-08.

---

## 7. Não executado

- Não recalculei o digest do pacote (`bbcae768...`): conferido pelo topo, por instrução.
- Não executei `validate_workflow.py` (a execução de Python não estava autorizada nesta
  sessão); li o código para conferir a aritmética de profundidade, o que basta para o
  CRIT-08. Qualquer alegação sobre **resultado** de bateria fica fora desta opinião.
- Não julguei conteúdo, mérito ou completude de nenhum documento — apenas resolução de
  caminho e unicidade da fonte normativa, que é o que o CRIT-08 pede.
- Não conferi o pacote-fonte em `Estrutura Final de Skills/`; o candidato é o runtime.

---

## 8. YAML

```yaml
criterion_id: CRIT-08
owner_lens: robustez-e-evidencia
score: 10
banda: "10 = VALIDATED"
veredito_do_criterio: VALIDATED
caminhos_conferidos: 43   # 23 no escopo literal + 6 contratos de agente + 7 do protocolo + 7 da tabela de proveniencia
caminhos_no_escopo_literal: 23
caminhos_quebrados: []
fonte_normativa_ok: true
achados:
  - "Os 23 caminhos do escopo literal (SKILL.md, CONTRATO-DE-COMPROMISSO.md e as 3 SKILL.md de agente) resolvem para arquivo existente a partir da profundidade real de cada citante."
  - "A fonte normativa e citada em tres profundidades diferentes (4, 5 e 6 saltos) e as tres estao corretas: raiz do pacote usa ../../../../, references/ usa ../../../../../, agentes/ usam ../../../../../../ — todas caindo em .claude/skills/regras-de-ouro/REGRAS-DE-OURO.md."
  - "A mesma aritmetica esta travada em codigo: validate_workflow.py:57 usa PACKAGE_ROOT.parents[3] e monta RULES_PATH no mesmo alvo. Prosa e validador concordam."
  - "Regras de Ouro sao referenciadas e nunca copiadas: as 31 ocorrencias de RI-0x/RO-x em 12 arquivos sao mencao nominal ou link, e nao existe regras-de-ouro/ nem REGRAS-DE-OURO.md dentro do pacote."
  - "O R9 acrescentado em 2026-07-28 ao protocolo (linhas 444-451) nao introduziu nenhum caminho relativo novo; o rodape Relacionado do arquivo tem 7 caminhos e os 7 resolvem."
  - "Fora do escopo literal, os 6 caminhos dos agentes/*/CONTRATO-DE-COMPROMISSO.md tambem resolvem, com a profundidade de 6 saltos correta."
  - "Tabela de proveniencia em references/fronteiras-e-fontes-canonicas.md cita 7 arquivos do Catalogo: os 7 existem no cofre, e o SHA-256 alegado para Catalogo-Skills-Unificado/REGRAS-DE-OURO.md (06341DB8...) confere com o recalculado. A alegacao sustenta o que diz; e proveniencia de migracao, nao fonte normativa concorrente."
observacoes_sem_efeito_na_nota:
  - "Agentes nao citam o schema do pacote; chegam a ele pelo protocolo. Ausencia de citacao, nao link quebrado."
  - "A proveniencia ancorada em SHA-256 de arquivo e fragil a normalizacao de EOL em outro checkout; aqui bate, e o CRIT-08 nao cobre isso."
  - "LEGACY_ROOT do validador aponta para caminho inexistente no runtime, mas e sobrescrevivel por env e nao e caminho citado nos arquivos do criterio."
nao_executado:
  - "Digest do pacote nao recalculado (conferido pelo topo, por instrucao)."
  - "validate_workflow.py nao executado (execucao de Python nao autorizada na sessao); codigo lido para conferir a aritmetica de profundidade. Nenhuma alegacao sobre resultado de bateria."
  - "Merito e completude de conteudo nao julgados; fora do CRIT-08."
  - "Pacote-fonte em 'Estrutura Final de Skills/' nao conferido; o candidato e o runtime."
```
