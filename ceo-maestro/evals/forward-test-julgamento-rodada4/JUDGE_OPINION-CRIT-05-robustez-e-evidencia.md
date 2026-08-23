# JUDGE_OPINION — CRIT-05 · ótica `robustez-e-evidencia`

- data: **2026-07-28** · rodada 4
- `candidate_digest`: `sha256:bbcae76833d7d54d051af903b7949e478272c720743cd176c1a0c1acc3fd4f58`
  (conferido pelo topo; **não** recalculado aqui)
- candidato julgado: o **runtime** —
  `.claude/skills/ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-inovacao-melhoria`
- instância própria, critério único: **CRIT-05**
- `return_to`: `departamento-juizes` · nota inteira 0–10 · sem veredito consolidado

> **Limite de execução declarado.** Python não roda nesta sessão (permissão negada). Tudo abaixo
> é **leitura estática do código**. Onde o critério pede existência de trava executável, a leitura
> basta e a conclusão é firme. Onde a afirmação seria "a trava reprova de fato ao rodar", o
> resultado é **SKIP** — não foi executado nem `validate_workflow.py` nem `corpus_adversarial.py`.

## Nota — **9** · banda `ACEITO_USO_INTERNO`

## Cláusula 1 — recalcular `gate_checks` a partir dos retornos: **trava executável, com lacuna literal**

`derive_gate_checks()` recomputa os **onze** booleanos a partir das oportunidades e dos
experimentos contidos nos retornos, sem ler o que o relatório declarou
(`evals/validate_workflow.py:1317-1362`). É função, não frase: retorna um `dict` derivado do
insumo.

`chain_errors()` compara declarado × derivado e **nomeia as chaves divergentes**
(`:1467-1476`):

```python
derived = derive_gate_checks(reference, returns)
if item.get("gate_checks") != derived:
    ...
    f"portfólio {initiative}: gate declarado diverge do derivado em {divergent}"
```

**A lacuna é o adjetivo do critério.** O critério — e a prosa do próprio pacote — dizem
*"retornos **aceitos**"*. `SKILL.md:203-205`: *"recalcular cada verificação a partir das
oportunidades e dos experimentos dos **retornos aceitos**"*; `references/protocolo-inovacao-melhoria.md:303-306`
repete: *"recalculado a partir das oportunidades e dos experimentos dos **retornos aceitos**"*.
O código passa `returns` — **todos** os retornos da rodada — e não o subconjunto autenticado:

- `validate_workflow.py:1467` → `derive_gate_checks(reference, returns)`
- `accepted_return_refs` é conferido apenas por **contenção** (`:1414-1418`: o aceito tem de
  existir e ter digest válido), **nunca por completude**: nada exige que todo retorno que
  alimenta a derivação esteja na lista de aceitos.
- O mesmo vale para os conjuntos vizinhos: `opportunities` (`:1443-1447`), `delivered` e
  `evidence` (`:1433-1434`) são montados de **todos** os retornos. Logo um item de portfólio
  pode ter oportunidade, gate e `gate_source_refs` inteiramente apoiados num retorno que o
  relatório **nunca listou como aceito**, e nenhuma checagem do pacote acusa.

Cobrado na rodada 3 pela mesma ótica; **não foi mexido nesta rodada** (o diff da rodada tocou só
`placar_errors`, ver adiante) e **continua sem declaração** — a busca por `retornos aceitos` e
`accepted_return_refs` nos `.md` do pacote devolve apenas as duas linhas de prosa acima e
`protocolo:362`; nenhum limite residual (`R1`–`R9`) cobre o desalinhamento. O `R4` cobre outra
coisa: *"o gate derivado depende do insumo declarado"* — o agente inventar o brief, não a
derivação sair de retorno não aceito.

## Cláusula 2 — reprovar booleano que não bate com o insumo: **confirmada em código, com contraprova**

Não é só a comparação: existe **contraprova negativa** que constrói exatamente o cenário do
critério — todos os gates declarados `true` enquanto o insumo é removido do retorno
(`validate_workflow.py:2344-2357`):

```python
bundle["report"]["portfolio"][0]["gate_checks"] = {key: True for key in ...}
bundle["returns"][0]["payload"]["opportunities"][0]["baseline"] = {"status": "MEASUREMENT_REQUIRED", ...}
chain_negative.append(("cadeia rejeita gate declarado sem baseline real", bundle))
```

Mesmo par no corpus: `corpus_adversarial.py:146-157` (`m12`, baseline virada para
`MEASUREMENT_REQUIRED` **depois** de o relatório ter sido montado) e `:160-163` (`m13`, o
experimento passa a apontar outra oportunidade, derrubando de uma vez todas as chaves de origem
experimental). `m15` (`:172-176`) exercita `two_alternatives` por deduplicação — a derivação usa
um `set` de JSON canônico (`validate_workflow.py:1338-1340`), então duas alternativas idênticas
derivam `False`.

Guardas independentes de estado/faixa contra o gate em `:1225-1234` (`READY_FOR_EXPERIMENT`,
`IN_EXPERIMENT`, `IN_MEASUREMENT`, `LEARNED` e faixa `NOW` exigem `all(gates.values())`;
`EVIDENCE_PENDING` com gate completo reprova). No schema, `gateChecks` é objeto **fechado** de
11 booleanos com todos obrigatórios e `additionalProperties: false`
(`schemas/departamento-inovacao-melhoria.schema.json:1243-1272`), e `gate_checks`/`gate_source_refs`
são obrigatórios em `portfolioItem` (`:1276-1290`).

**Teto de cobertura, nomeado:** a fixture positiva monta `gate_checks` chamando a **própria**
`derive_gate_checks` (`validate_workflow.py:858`), então o caminho positivo prova consistência,
não semântica; quem prova semântica são as contraprovas. Elas cobrem `baseline` isolada,
`two_alternatives` isolada, `rollback` na direção inversa (`:2213-2216`) e o bloco experimental
inteiro via `m13`. As chaves de origem em oportunidade — `job`, `pain_location`,
`evidence_dependencies_vetoes` — não têm mutação individual.

**Não executado (SKIP):** que essas contraprovas de fato produzem erro ao rodar. A leitura mostra
o caminho de erro; a execução não foi feita.

## Cláusula 3 — corpus adversarial executável, casos derivados de achados nomeados: **confirmada**

`evals/corpus_adversarial.py` é executável de verdade: `raise SystemExit(main())` no rodapé
(`:566-567`) e `main()` retorna `1` se **qualquer** mutação escapar (`:563`), imprimindo escapes
por prioridade. Não é catálogo em prosa.

Os 45 casos carregam **tag de achado** na tupla (`:493-539`, forma
`("MUT-12", "P1-3", "gate completo sem baseline medida", m12)`), e as tags resolvem uma a uma na
tabela de origem da auditoria anterior — `evals/ADVERSARIAL-AUDIT.md:34-51`, quinze linhas de
`P1-1` a `C-P2-2` somando **45**. A auditoria é real e datada (`:5` — `EXECUTADA` em 2026-07-26,
segunda rodada), com o histórico do que gerou os casos: *"o validador imprimia **59/59 PASS** e
mesmo assim 39 de 45 mutações passavam"* (`:24-27`). A linha do meu critério tem dono nomeado:
`P1-3 gates autoassertivos` (`:38`), fechada por *"`derive_gate_checks` recalcula o gate dos
retornos"* (`:64`).

O teto próprio está **declarado pelo candidato**, não escondido: corpus e validador compartilham o
motor (`corpus_adversarial.py:15-19`; `ADVERSARIAL-AUDIT.md:83-86`), mapeado em `R4`.

**Não executado (SKIP):** o `45/45 rejeitadas, 0 escapes` de `PLACAR.md:46` e `ADVERSARIAL-AUDIT.md:53`.
É relato do candidato, não medição desta ótica.

## O que mudou nesta rodada, e o que isso vale para CRIT-05

O diff da rodada é pequeno e verificável: `git diff HEAD` no pacote mostra **três** arquivos —
`evals/PLACAR.md` (+60/-…), `evals/validate_workflow.py` (**+62, 0 remoções**) e
`references/protocolo-inovacao-melhoria.md` (+11). **`derive_gate_checks`, `chain_errors`,
`corpus_adversarial.py` e o schema não foram tocados**: a evidência das cláusulas 1–3 é a mesma
da rodada 3, reconferida linha a linha acima.

As +62 linhas são a função `limites_ligados_a_risco_errors` (`validate_workflow.py:1642-1700`),
chamada por `placar_errors` (`:1638`). **A afirmação se confirma na leitura**, e ela importa para
esta ótica porque é o mesmo padrão que o CRIT-05 exige — derivar em vez de autoafirmar:

- é **trava executável**: itera os itens da seção `## O que ainda não foi provado` e devolve erro
  por item sem identificador (`:1691-1693`) ou com `R` não declarado (`:1696-1699`);
- **o conjunto de `R` é lido do protocolo em runtime**, não é lista literal —
  **`validate_workflow.py:1667`**:
  `declarados = set(re.findall(r"\*\*(R\d+)\*\*", protocolo[match.end():]))`,
  sobre `PROTOCOL_PATH` (`:51`) a partir do heading de riscos residuais (`:1664`). Varri o
  validador: **não há lista literal de `R1`…`R9` em lugar nenhum** do arquivo.
- fecha o laço com `residual_errors`, que já exigia que os riscos sejam declarados em **um único**
  arquivo (`:1615-1621`).

Isso é crédito real e converge com o CRIT-05: a cláusula que a rodada anterior chamou de
auto-neutralizável passou a falhar alto. Não altera a nota deste critério porque não toca a
derivação do gate — registro como corroboração da doutrina, não como conserto da lacuna da
cláusula 1.

**Duas observações sobre a força da trava nova** (fronteira desta ótica: trava executável ×
aparência de trava):

1. O conjunto válido é derivado de **token em negrito na seção**, não de **linha da tabela de
   riscos**. Um `**R10**` escrito em prosa dentro do §12 já entraria no conjunto válido sem
   vetor, consequência, mitigação ou teto — e `residual_errors` só exige `len(rows) >= 4`
   (`:1610-1613`). A derivação é da fonte certa, com granularidade mais fraca do que a fonte
   permite.
2. Sintoma disso já está no arquivo: a linha do **R9** está separada da tabela por uma **linha em
   branco** (`references/protocolo-inovacao-melhoria.md:443` vazia, `:444` a linha do R9). Em
   markdown ela **não** faz parte da tabela; para a heurística de prefixo do validador, faz. Hoje
   o conteúdo está correto e completo — mas quem valida é o prefixo `| **R`, não a estrutura.

## Achados (arquivo:linha + citação literal)

| # | Onde | Citação | O que é |
|---|---|---|---|
| 1 | `evals/validate_workflow.py:1467` | `derived = derive_gate_checks(reference, returns)` | deriva de **todos** os retornos; o critério e a prosa do pacote dizem *retornos aceitos* |
| 2 | `SKILL.md:203-205` | "recalcular cada verificação a partir das oportunidades e dos experimentos dos **retornos aceitos**" | prosa que promete mais do que o código entrega |
| 3 | `references/protocolo-inovacao-melhoria.md:303-306` | "recalculado a partir das oportunidades e dos experimentos dos **retornos aceitos**" | mesma promessa, na fonte normativa do pacote |
| 4 | `evals/validate_workflow.py:1414-1418` | `if set(report.get("accepted_return_refs", [])) - expected_returns:` | contenção, nunca completude: retorno não aceito segue alimentando a derivação |
| 5 | `evals/validate_workflow.py:1667` | `declarados = set(re.findall(r"\*\*(R\d+)\*\*", protocolo[match.end():]))` | **a favor**: conjunto de `R` lido do protocolo, sem lista literal no validador |
| 6 | `evals/validate_workflow.py:2344-2357` | `("cadeia rejeita gate declarado sem baseline real", bundle)` | **a favor**: contraprova do booleano `true` sem insumo |
| 7 | `evals/corpus_adversarial.py:566-567` · `:493-539` | `raise SystemExit(main())` · `("MUT-12", "P1-3", ...)` | **a favor**: corpus executável com tags que resolvem em `ADVERSARIAL-AUDIT.md:34-51` |
| 8 | `references/protocolo-inovacao-melhoria.md:443-444` | linha vazia antes da linha do `R9` | linha do R9 fora da tabela em markdown; o validador a aceita por prefixo |

## Fechamento

- `criterion_id`: CRIT-05 · `owner_lens`: robustez-e-evidencia
- `score`: **9** · `banda`: `ACEITO_USO_INTERNO`
- `trava_executavel_confirmada`: **true** (existência, por leitura)
- `conjunto_R_lido_do_protocolo`: **true** — `evals/validate_workflow.py:1667`
- `confidence`: **alta** para existência das travas; **nenhuma** para comportamento em execução
- `residual_risk`: (1) `returns` × `accepted_return_refs` — o gate pode se apoiar em retorno que o
  relatório nunca aceitou; segue **sem conserto e sem declaração** em `R1`–`R9`, e agora contradiz
  a letra da própria `SKILL.md` e do próprio protocolo; (2) três das onze chaves derivadas
  (`job`, `pain_location`, `evidence_dependencies_vetoes`) sem mutação individual no corpus;
  (3) o `45/45` e o `122/122` são relatos do candidato, **não medidos aqui**; (4) a trava nova de
  `R` deriva de negrito na seção, não de linha de tabela.
- `nao_executado` (SKIP): `python evals/validate_workflow.py`; `python evals/corpus_adversarial.py`;
  qualquer afirmação de PASS/FAIL em runtime. Python indisponível nesta sessão por permissão negada.
