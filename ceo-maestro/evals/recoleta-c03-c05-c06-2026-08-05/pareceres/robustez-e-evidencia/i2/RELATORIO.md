# Parecer — `robustez-e-evidencia`, instância 2 — `departamento-qa-usabilidade` × `C03`

- **Lente:** `robustez-e-evidencia` · **Instância:** 2 · **Rodada:** `recoleta-c03-c05-c06`
- **Commit julgado:** `ab5882cf09a95d841168fd52faf656ac55997287` (descendente do `4446786` do contrato)
- **Nível exigido:** `INTERNO` · **Emitido em:** 2026-08-05T23:45:03-03:00
- **Par julgado:** `departamento-qa-usabilidade` × `C03` — **um só**, nada mais.

## Nota

| par | nota |
|---|---:|
| `departamento-qa-usabilidade` × `C03` | **6** |

Banda `4–6`: **atende em parte, com lacuna observável e nomeável.**

## O critério, como o li

> **`C03` — Trava com prova.** Cada trava tem caso **executado** que a faz **reprovar**; nada passa
> por presença de string; **morte por exceção não conta como pega**.

Três exigências, e as tratei como três, não como uma média impressionista.

## O que o pacote atende — e atende bem

**1. Contraprova executada em volume real.** Das 122 linhas da saída crua, cerca de **49** são
reprovações executadas, não presença de string:

- **32 fixtures negativas** (`evals/validate_workflow.py:1591-1735`, saída crua linhas 52–83). Cada
  uma é mutação de **um ponto** sobre uma base cuja validade positiva é afirmada separadamente nas
  11 fixtures positivas (`:1572-1588`, saída crua 41–51). Isso importa: exclui o modo de falha em
  que a fixture já estava quebrada antes da mutação e o crédito vai para a trava errada.
- **12 mutações sobre a camada de recálculo** — grafo assignment→retorno→relatório, partição de
  borda, `derive_state` (`:1839-1982`, saída crua 94–101 e 103).
- **3 rejeições do consumidor** (`:2074-2087`, saída crua 115–117).

**2. O ponto mais forte da casa: o gate composto.** `:2058-2072` (saída crua 113–114) não aceita
"deu erro". Exige literalmente:

```python
check("gate composto bloqueia ocultação aceita pelo schema estrutural",
      not schema_only_errors and bool(bridge_errors), ...)
```

A mutação precisa **passar** no schema estrutural **e** ser pega pela ponte. Isso não credita a
trava por acidente: prova que ela acrescenta poder discriminante que o schema sozinho não tem. É a
forma que o critério pede, e o pacote a tem em dois casos.

**3. Morte por exceção está tratada, e explicitamente.** O validador converte `ImportError` em FAIL
nomeado em vez de morrer por traceback (`:126-144`), com o comentário que diz por quê. A saída crua
confirma: `traceback: false` (`saida-crua/00-RESUMO.json:123`). E as quatro travas globais que o
pacote chama (`:1465-1482`) vêm de um motor que **codifica a própria cláusula**:
`_compartilhado/verificacoes_estrutura.py:907-924` exige que `digest()` recuse com **classe de
exceção própria**, porque *"mutante que morre por exceção qualquer é mutante creditado errado — 7 de
11 saíram assim numa medição desta casa"*. E `:1239-1284` roda autoteste por regra, tratando exceção
como `DETECTOR_QUEBRADO`, nunca como pega.

## Os furos — por que não é 7

### Furo 1 — 12 dos 122 checks passam por presença literal de string, sem nenhum caso executado

`evals/validate_workflow.py:1414-1447`, saída crua linhas 13–24. Todos PASS. Todos deste feitio:

| linha | condição | o que alega provar |
|---|---|---|
| `:1419` | `RULES_LINK_DEPARTMENT in manager and ... in contract` | fonte normativa correta |
| `:1423` | `"não executar testes" in manager.lower()` | **o gerente orquestra e não executa** |
| `:1428` | `"departamento-juizes" in manager and "não atribui nota" in contract.lower()` | **preserva o gate dos Juízes** |
| `:1438` | `RULES_LINK_AGENT in text and ... in own_contract` | fonte normativa do agente |
| `:1442` | `"BLOCKED_BYPASS_ATTEMPT" in text and "QA_ASSIGNMENT" in own_contract` | **anti-bypass** |
| `:1446` | `"Não aciona:** ninguém" in text` | **agente é folha da árvore** |

Não são checks periféricos: são as **garantias contratuais** do pacote — as quatro coisas que ele
promete que não faz. E cada uma é verdadeira se e somente se a frase aparece no arquivo. Um
`SKILL.md` que contivesse a frase dentro de uma negação — *"a regra de não executar testes foi
revogada"* — continuaria verde. Nenhuma dessas 12 tem caso executado que a faça reprovar; nenhuma
tem mutação; nenhuma tem contraprova.

O critério não diz "poucas coisas passam por presença de string". Diz **nada**. Quatro famílias de
alegação normativa passam exatamente assim.

### Furo 2 — toda fixture negativa é aceita por `bool(errors)`, nunca por *qual* erro

`:1735`, `:1843`, `:2077` e irmãos: `check(f"fixture negativa rejeita {label}", bool(errors))`. O
rótulo nomeia uma trava; a condição só exige que **alguma** coisa tenha reclamado. Três casos em que
isso credita errado, verificáveis:

- **`:1671-1673`, "agente embute julgamento em texto livre"** — troca o objeto por
  `"APROVADO com nota 10"`. A recusa é **de tipo** (string onde o schema exige objeto), idêntica para
  `"qualquer coisa"`. Nenhuma trava anti-julgamento é exercitada.
- **`:1675-1677`, "julgamento no owner"** — recusado pelo **enum** `operationalOwner`
  (`schemas/departamento-qa-usabilidade.schema.json:95-105`), que dispara igual para
  `owner = "fulano"`. Vocabulário fechado é trava legítima; anti-julgamento é outra coisa.
- **`:1698-1700`, "relatório inclui nota"** (`bad["score"] = 9.5`) — recusado por
  `additionalProperties: false`, o **mesmo** mecanismo de "campo extra no plano" (`:1607`). A trava
  específica de nota existe — `FORBIDDEN_RESULT_KEYS`, `:1543-1550` — e **nunca é mutada**.

Não é morte por exceção. É a mesma doença que a cláusula nomeia: **crédito à trava que não disparou**.

### Furo 3 — nenhuma mutação do próprio validador

Nada no pacote prova que **apagar um check fica vermelho**. O motor compartilhado faz isso para os
detectores dele (`_compartilhado/verificacoes_estrutura.py:864-904` e `:1239-1284`, com fixture por
regra, detector-cego e grita-no-inocente). O pacote **herda** esse rigor em 4 dos seus 122 checks e
**não o pratica em nenhum dos outros 118**.

### Furo 4 — duas bases negativas sem verde independente

`:1718` e `:1725` mutam `consolidated(passed=2, ...)` cuja forma não-mutada nunca é afirmada verde
como fixture positiva. Se a base já produzisse erro de schema, a rejeição precederia a mutação.
Menor que os anteriores, mas é o mesmo mecanismo do furo 2.

### Furo 5 — "caso de origem real" é presença de rótulo

`:1488`: `any(case.get("origem") == "real" for case in cases)`. Uma alegação de **proveniência**
verificada pela presença da palavra `"real"` num campo. Presença de string de novo, agora sobre a
origem da evidência.

## O que descontei, e disse que descontei

O **`[FAIL]` da série global de ADR** (saída crua, linha 26 — número `020` duplicado por cópias de
laboratório em `ceo-maestro/evals/producao-honesta-2026-08-04/origem-independente-R1/lab/mech/{A,B}/`)
é **alheio a este pacote** e **não pesou na nota**. Sem ele o pacote está em 121/121 do próprio
escopo.

## Observação, não nota — o estado futuro da T27

O candidato da T27 (contagem exigida por código) **não está na árvore** e não o li. Se instala travas
que exigem a contagem declarada, elas melhorariam antes o `C04` (evidência) que o `C03`. Registro
como observação porque o contrato manda: **julguei o presente**.

## O que declaro contra mim

1. **Não executei nada.** Toda afirmação minha sobre o que a suíte *faria* sob mutação é leitura de
   código, não medida. Acuso o pacote de não provar que apagar um check fica vermelho — e eu também
   não provei.
2. **O "cerca de 49"** saiu de mapear linhas da saída crua contra funções do fonte, a olho. Pode
   variar 2–3 para mais ou menos. A nota não depende dele, mas o número não tem receita reexecutável.
3. **Li um "APROVADO" dentro do candidato antes de fixar a nota.** `evals/ADVERSARIAL-AUDIT.md:10` é
   autodeclaração do próprio pacote, datada de 2026-07-26 — não é nota de `C03` nem veredito de
   Juízes. Registro mesmo assim. Não mudou minha leitura: o que ela mede (9/9 e 10/10 no gate
   composto) é justamente a parte que eu já classificara como a mais forte, e nada nela toca os 12
   checks de string. Que um veredito more dentro do artefato julgado é, por si, sinal contra o
   pacote.
4. **`evals/PLACAR.md:5-8` aponta para `evals/julgamento-pacotes-2026-07-29/08-RESUMO.md`** — contexto
   proibido. **Vi o link e não abri.** Nenhuma nota de `C03` chegou aos meus olhos, em momento nenhum.
   Não rodei busca sobre `julgamento*`, `pareceres*` nem `rejulgamento*`.
5. **Hesitei entre 6 e 7,** e o que decidiu foi a letra do critério, não uma medida a mais. O volume
   e a qualidade de contraprova estão bem acima do piso da banda; um juiz que lesse *"nada passa por
   presença de string"* como princípio orientador, e não como requisito literal, daria 7 com
   honestidade. Meu 6 é a leitura estrita, e a distância entre 6 e 7 aqui é decisão de leitura do
   contrato, não fato observado a mais.
6. **Julguei `ab5882c`,** descendente do `4446786` do contrato. Não conferi diff arquivo a arquivo:
   não posso afirmar que a árvore do pacote é byte-idêntica à que o CEO executou.
7. **Não li o candidato da T27.**

## Fecho

`departamento-qa-usabilidade` × `C03` = **6**. Reprovações executadas existem, em volume, com uma
peça genuinamente discriminante (o gate composto) e sem morte por exceção creditada. Mas o critério
proíbe presença de string, e as quatro travas que sustentam o contrato do pacote — não executa, não
pontua, anti-bypass, folha da árvore — passam por presença de string e por mais nada. Isso não é
risco menor de acabamento: é defeito observado contra a letra do critério, nomeável e localizado.
