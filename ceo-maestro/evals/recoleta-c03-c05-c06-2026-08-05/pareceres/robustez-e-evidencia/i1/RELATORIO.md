# Parecer — `robustez-e-evidencia`, instância 1 — `departamento-qa-usabilidade` × `C03`

- **Rodada:** `recoleta-c03-c05-c06` · **Nível exigido:** `INTERNO`
- **Commit julgado:** `ab5882cf09a95d841168fd52faf656ac55997287`
  (o `00-CONTRATO.md` nomeia `4446786`; conferi: é o **pai direto** deste HEAD, e o único delta é o
  commit que selou esta recoleta — a árvore do pacote é a mesma)
- **Emitido em:** 2026-08-05T23:47:50-03:00
- **Executei:** nada. A `SKILL.md`, linha 132, proíbe, e o desenho respeita — o CEO executou e
  publicou a saída crua. Tudo aqui é leitura e crítica.

## Nota

**`C03` = 6** — banda *cru*: atende em parte, com lacuna observável e nomeável.

## O descontado, antes de tudo

A saída crua fecha em **121/122**, com **um** `[FAIL]`: a série global de ADR, número `020`
duplicado por duas cópias de laboratório em
`ceo-maestro/evals/producao-honesta-2026-08-04/origem-independente-R1/lab/mech/{A,B}/`.
É evidência de outra frente. **Descontei**, e ela não tem peso nenhum nesta nota.

## O que o critério pede, cláusula por cláusula

> Cada trava tem caso **executado** que a faz **reprovar** · nada passa por **presença de string** ·
> **morte por exceção não conta como pega**.

| cláusula | veredito | por quê |
|---|---|---|
| morte por exceção | **cumprida, e bem** | ver abaixo |
| caso executado que reprova | **parcial** | grande cobertura, mas travas inteiras sem contraprova |
| nada por presença de string | **violada** | 13 checks passam por substring, sem caso que os reprove |

## O que está genuinamente bom — e não é pouco

1. **A cláusula da exceção é honrada de forma exemplar.** O motor devolve **lista de erros** e nunca
   levanta (`_compartilhado/validador_schema.py:284-390`), então nenhum mutante é creditado por
   morrer. E a única trava que se prova *por* exceção exige a **classe própria**
   `DigestDeFixtureRecusado`, recusando crédito a exceção genérica em texto explícito:
   *"mutante que morre por exceção qualquer é mutante creditado errado — 7 de 11 saíram assim numa
   medição desta casa"* (`_compartilhado/verificacoes_estrutura.py:912-915, 959-987`). É a cláusula
   do `C03` escrita em código.
2. **~46 casos negativos executados**, todos por **mutação de uma fixture positiva** — 33 em
   `evals/validate_workflow.py:1591-1735`, 11 de grafo e partição em `1839-1982`, 3 de fronteira em
   `2052-2087`. Não é teatro: são artefatos completos, alterados num campo, submetidos ao mesmo
   motor.
3. **As cinco travas globais que o pacote invoca se autotestam a cada chamada** —
   `_autoteste_da_cobertura` (`verificacoes_estrutura.py:608-643`), `_autoteste_da_trava_de_copia`
   (`864-904`), a bateria viva de `digest()` (`959-1001`). E o retorno de cada uma **precisa
   alimentar** o agregado de erros, senão `COBERTURA_SEM_EFEITO` acusa com arquivo e linha.
4. **A história adversarial registra os escapes**, não só os acertos: `evals/ADVERSARIAL-AUDIT.md:20-27`
   lista sete famílias frágeis na rodada 1 e cinco contraprovas que **ainda passavam** na rodada 2 —
   e cinco delas viraram caso executado (`N/A` mascarado → `1639`; cleanup parcial → `1904`; causal
   divergente → `1932`; julgamento no `owner` → `1676`; FAIL ligado a outro caso → `1970`). Escape
   convertido em caso é o oposto do portão tautológico.

## Os furos

### 1. O crédito não é atribuído — `bool(errors)` aceita qualquer erro

`validate_workflow.py:1733-1735`:

```python
for label, value in mutations:
    errors = valid_local(value)
    check(f"fixture negativa rejeita {label}", bool(errors))
```

O caso é creditado por **qualquer** erro do schema, nunca pelo erro da trava que o rótulo nomeia.
Mesmo padrão em `1841-1982` (`bool(artifact_graph_errors(...))`).

### 2. Há caso creditado a uma trava que **não existe**

`validate_workflow.py:1671-1673` troca `recommended_next_step` — um **objeto** — pela string
`"APROVADO com nota 10"`, e o check se chama *"agente embute julgamento em texto livre"*.
O que rejeita é o **type-check**: `validador_schema.py:321-323` retorna na hora que o tipo diverge.
Não existe nenhum padrão anti-julgamento no schema — varri as 1444 linhas por
`nota|APROVAD|VALIDATED|veredito|julg`: os únicos `pattern` do arquivo são `n/a`, dimensão de borda,
identificador e `sha256`. **O mesmo PASS sairia com a string `"x"`.** O rótulo vende uma trava que a
casa não tem.

O caso vizinho (`1675-1677`, `owner = "APROVADO com nota 10"`) é honesto: dispara o enum fechado
`operationalOwner`. Mas ali também o mecanismo é *whitelist de donos*, não detecção de julgamento —
qualquer dono fora da lista produz o mesmo verde.

### 3. Treze checks passam por presença de string, sem caso que os reprove

`validate_workflow.py:1417-1447` — doze checks da forma `"não executar testes" in manager.lower()`,
`"BLOCKED_BYPASS_ATTEMPT" in text`, `"Não aciona:** ninguém" in text`. Mais
`1986-1989`: *"schema do Diretor conhece o Departamento"* é `DEPARTMENT in json.dumps(DIRECTOR_SCHEMA)`
— substring sobre o **JSON inteiro serializado**, que passaria se o nome aparecesse só numa
`description`. São ~11% da bateria. `C03` proíbe isso na letra, e a lição da casa é a mesma:
verificar presença não é verificar efeito.

### 4. Travas sem nenhum caso que as faça reprovar

Nos cinco ramos condicionais de `qaConsolidatedReport`, contei **~21 de 33** restrições sem
contraprova: `confidence: const HIGH`, `defect_refs: maxItems 0`, `test_summary.critical_fail`,
`coverage_summary.failed/unverified/missing: const 0`, e o ramo `REWORK_REQUIRED` inteiro menos
`quality_state`.

Pior: **os ramos `NOT_PROVEN` e `BLOCKED` nunca chegam ao `valid_local`** — nem positiva nem
negativamente. O `partial_report` de `2022-2027` existe, mas só alimenta a ponte e o schema do
Diretor. Nos ramos por agente (`qaAssignment.allOf[2..3]`, `qaAgentReturn.allOf[1..2]`) só a
capacidade de `AGENTS[0]` tem mutação; as duas irmãs só aparecem em fixture positiva.

### 5. Mutações sobredeterminadas creditam a trava errada

`1718-1723` (*"READY promove SKIP"*) dispara pelo menos **quatro** regras independentes ao mesmo
tempo: `test_summary.skip: const 0`, `skip_reasons: maxItems 0`, `pending: maxItems 0` e
`coverage_summary.skipped: const 0`. Apague a regra de `skip` e o caso **continua verde** — logo essa
regra não tem caso que a isole. O caso de `pending` já é coberto sozinho em `1714-1716`.

### 6. E a técnica certa está no próprio pacote, usada em 2 de ~46 casos

`2058-2062` e `2068-2072` exigem `not schema_only_errors and bool(bridge_errors)` — provam que o
schema estrutural **aceitou** e que o portão composto **pegou**. É atribuição de verdade. O pacote
sabe fazer; só não fez nas outras quarenta e poucas.

## Por que 6 e não 7, por que 6 e não 5

**Não é 7** porque 7 exige *"atende o critério inteiro, sem defeito observado"*, e eu observei
defeito: caso creditado a trava inexistente, cláusula de presença de string violada na letra, e
travas inteiras sem contraprova. Isso não é acabamento — é caso não coberto e prova faltando, que é
a definição literal da banda 4–6.

**Não é 5** porque a bateria executada é grande, real, nasceu de escapes documentados, e a cláusula
mais difícil do critério — a da morte por exceção — está cumprida melhor aqui do que o critério pede.

## O futuro, registrado como observação e não como nota

A **T27** (travas exigindo a contagem declarada) **não está na árvore** e eu não a julguei. Registro
que **ela não consertaria isto**: meu achado é de atribuição de contraprova, não de contagem. Nenhuma
parte desta nota está esperando a T27 — não uso o futuro para explicar o presente.

## Contaminação

Não abri `02-AGREGACAO-E-CORRECOES.md`, `julgamento/`, `rejulgamento-c04/`,
`REGISTRO-DE-VEREDITOS.md`, nem os vereditos da T19/T27, e não rodei busca sobre pastas
`julgamento*`, `pareceres*` ou `rejulgamento*`. **Não topei com nota nenhuma de `C03`.**
O `PLACAR-ADENDO` e o `PLACAR.md` que li declaram contagem de validador, não nota de Juiz — e o
adendo diz por escrito que não altera nota nem veredito.

## O que declaro contra mim

Está integral no `PARECER.json`, campo `o_que_declaro_contra_mim`. O essencial:

1. **Não executei** — logo toda atribuição mutação→regra é **estática**. Meu achado mais forte
   depende de `validador_schema.py:321-323` retornar cedo no erro de tipo: eu li, não rodei.
2. A contagem *"~21 de 33"* é enumeração à mão; aceito ±2. O qualitativo (ramos `NOT_PROVEN`/`BLOCKED`
   nunca exercitados) vem de leitura integral das cinco funções `validate_*` e do `main()`.
3. **Minha nota fica um ponto abaixo do corte, e isso decide.** Considerei 7 e recusei; um juiz que
   leia *"nada passa por presença de string"* como restrita a travas de **comportamento** — poupando
   as 13 checagens documentais — chega em 7 legitimamente. É a divergência viva, e eu a exponho.
4. Não li `SKILL.md` nem `CONTRATO-DE-COMPROMISSO.md` por inteiro; trava de `C03` fora de `evals/` e
   `schemas/` eu não teria visto.
5. Minha primeira listagem resolveu na árvore **principal** (um `cd A || cd B` com `A` existente).
   Foram nomes de arquivo e contagem de linhas, refeitos no worktree — mas não provei igualdade byte
   a byte para aquela chamada.
6. Creditei ao pacote o rigor das travas globais, que é mérito do `_compartilhado` — o próprio adendo
   do pacote diz isso. Mérito do pacote é invocá-las **com efeito**, e isso é exigido por gate de
   vizinho, não por virtude própria.
