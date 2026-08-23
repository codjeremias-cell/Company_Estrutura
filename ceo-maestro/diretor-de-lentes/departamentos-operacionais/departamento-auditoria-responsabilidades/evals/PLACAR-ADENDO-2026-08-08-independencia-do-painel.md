# Adendo de contagem — `departamento-auditoria-responsabilidades`, 2026-08-08

> **Redeclaração no mesmo ato da mudança.** A tarefa 71 acrescentou **cinco casos** a este
> validador e mexeu no **schema normativo do CEO**, que governa a barreira de todos os pacotes.
> Contagem que muda sem redeclarar é a deriva que, em 2026-08-05, derrubou o `C04` de oito pacotes
> na rodada seguinte. Aqui ela é redeclarada junto, e o efeito no vizinho está medido abaixo.

## Contagem vigente

| medição | resultado |
|---|---|
| Validador determinístico do Departamento | 175/175 PASS |
| **vigente em 2026-08-08** | **175/175** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-auditoria-responsabilidades"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## O delta desta data

`170/170` → **`175/175`**, isto é **+5 casos**:

| caso | trava |
|---|---|
| gate de independência do painel escrito no schema do CEO | `validate_ceo_gate_independencia` |
| o emissor real deriva a independência do painel | `validate_emissor_deriva_independencia` |
| ledger rejeita COMPLIANT com inspetor não independente | `validate_schema_gates` (`GATE_DA_INDEPENDENCIA`) |
| CEO rejeita COMPLIANT com painel não independente | cláusula nova de `governanceReport.allOf` |
| painel vazio não é independência | guarda do `all([])` nos dois derivadores |

`MINIMO_DE_CASOS` sobe de **155** para **160** no mesmo ato: piso que não acompanha o acréscimo
aceita, na rodada seguinte, que os cinco sumam sem vermelho nenhum.

## O achado que fechou

`FIND-REMED7-C08-CA-01`. A Barreira de saída deste contrato promete *"cada recibo usado é válido,
**independente** e rastreável"* como condição de veredito positivo, e **nenhuma cláusula lia
`panel[].independent`**: o campo era preenchido e jamais lido, então recibo não independente
fechava `COMPLIANT` do mesmo jeito. As três ocorrências de `independent` no validador eram
**fixture**; medindo agora, são **cinco** — 413 e 414 em `audit_receipt`, 687 em `audit_ledger`,
1975 e 1976 em `_rodada_minima`.

**A cláusula nasceu na camada do `AUDIT_LEDGER`**, e não no recibo nem só no envelope. Medido nas
três camadas antes de escrever: a promessa é quantificada sobre um conjunto, e o painel é o único
artefato que vê o conjunto; no recibo o campo tem de continuar **medido**, ou o schema volta a
premiar quem mente (rodada 9) — foi a declaração honesta `independent: false` nos três recibos do
C08 que expôs o mecanismo cego. O envelope do CEO recebe o **escalar derivado**, no mesmo par de
duas camadas que `candidate_identity_status` já usava.

## Prova de mutação — 7 de 7

| mutante | efeito |
|---|---|
| M1 ledger sem o gate de painel independente | 173/175 |
| M2 envelope do CEO sem a cláusula de independência | 173/175 |
| M3 cláusula do CEO rechaveada em `governance_verdict` | 173/175 |
| M4 derivador do validador sem o guarda do painel vazio | 174/175 |
| M5 emissor sem o guarda do painel vazio | 174/175 |
| M6 fixture do painel virada para `independent=False` | 171/175 |
| M7 emissor digita `INDEPENDENTE` em vez de chamar o derivador | 174/175 |

**M5 escapou na primeira corrida**, e é o achado mais útil desta frente: apagar o guarda do painel
vazio **dentro de `emitir_governanca.py`** mantinha a bateria em 174/174. Este validador
reimplementa a derivação e estava testando a **própria cópia**; a função que a operação chama não
era exercitada por caso algum. `validate_emissor_deriva_independencia` fechou os dois lados — a
função responde certo **e** o relatório a chama —, e M5 e M7 passaram a ficar vermelhos.

`all([])` é `True`: sem o guarda, um ledger sem inspetor nenhum sairia `INDEPENDENTE`. Ausência de
inspetor não é independência.

## Efeito no vizinho, medido

A mudança é no schema do CEO, então o raio não para neste pacote. Medido em 2026-08-08, após a
edição e antes do conserto: **`ceo-maestro` 147/148** — o caso *"o envelope da barreira valida
contra `$defs/governanceReport`"* caiu porque a fixture da barreira não trazia o campo novo. O
`departamento-negocios` acusou o mesmo por **eco**: ele reexecuta o CEO como regressão. Corrigida a
fixture do CEO, os dois voltaram: **`ceo-maestro` 148/148**, **`departamento-negocios` 235/235**.

Cadeia dos 16 pacotes reais medida na mesma corrida: **2027/2027, 0 quebrados**, contra
**2022/2022** medido em 2026-08-08 antes desta frente — delta **+5**, que são exatamente os cinco
casos acima.

## T83, fechada por consequência

A trava nova exige que **toda chave citada num `if` exista em `properties`**. A cláusula do
manifesto, acrescentada ao `governanceReport` na rodada 8, estava chaveada em `governance_verdict`
— nome do veredito no `AUDIT_LEDGER`, não neste objeto, que é `additionalProperties: false`. O `if`
nunca casava: `COMPLIANT` com `candidate_manifest_status: DIVERGENTE` **passava**, medido antes do
conserto. Corrigida para `verdict` no mesmo ato, porque enquanto violasse a trava a bateria ficaria
vermelha. Presença de cláusula não é alcance de cláusula.
