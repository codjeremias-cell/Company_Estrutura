# Veredito da recoleta `C03`/`C05`/`C06` — três aprovados, um reprovado

- **Agregado por:** `ceo-maestro`, em 2026-08-05, pela regra selada em
  [`00-CONTRATO.md`](00-CONTRATO.md), fixada antes de qualquer parecer.
- **Entrada:** 4 pareceres (2 lentes × 2 instâncias), worktrees isolados, schema estrito, zero `n/a`.
- **Régua mista:** `C03`/`C05`/`C06` desta rodada + `C04` da recoleta de 2026-08-05 + os demais de
  2026-08-04. **Três datas no registro.**

## O que a recoleta mediu

| pacote | crit. | i1 | i2 | MENOR | |
|---|---|---:|---:|---:|---|
| `arquitetura-dados` | `C05` | 7 | 8 | **7** | na faixa |
| `conteudo-marketing` | `C05` | 7 | 8 | **7** | na faixa |
| `conteudo-marketing` | `C06` | 7 | 8 | **7** | na faixa |
| `desenvolvimento` | `C05` | 8 | 7 | **7** | na faixa |
| `qa-usabilidade` | `C06` | 8 | 7 | **7** | na faixa |
| `qa-usabilidade` | **`C03`** | **6** | **6** | **6** | **acordo abaixo do corte** |

**Cinco dos seis pares na faixa `INTERNO`. Zero faixas cruzando o corte** — as instâncias
concordaram em todos os seis.

## O veredito

| pacote | `C01` | `C02` | `C03` | `C04` | `C05` | `C06` | mín | veredito |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `departamento-desenvolvimento` | 9 | 8 | 7 | 7 | 7 | 7 | **7** | **`ACEITO_USO_INTERNO`** |
| `departamento-arquitetura-dados` | 8 | 8 | 7 | 7 | 7 | 7 | **7** | **`ACEITO_USO_INTERNO`** |
| `departamento-conteudo-marketing` | 8 | 8 | 7 | 7 | 7 | 7 | **7** | **`ACEITO_USO_INTERNO`** |
| `departamento-qa-usabilidade` | 8 | 9 | **6** | 7 | 8 | 7 | 6 | **`REPROVED`** |

**`REPROVED`, não `NAO_DISCRIMINADO`:** o `C03` saiu **6 nas duas instâncias, sem divergência**.
Dominância — nenhuma resolução dos outros critérios levanta o mínimo.

## Por que o `C03` do `qa-usabilidade` não fecha

As duas instâncias chegaram lá por caminhos independentes e apontaram o mesmo:

**1. Garantia contratual verificada por presença de string** — 12 a 13 checks, ~11% da bateria:

```python
"não executar testes" in manager.lower()
"departamento-juizes" in manager and "não atribui nota" in contract.lower()
```

Conferido pelo CEO na fonte. Um `SKILL.md` com a frase dentro de uma negação continua verde. O
`C03` diz, na letra, que **nada** passa por presença de string — e o que passa aqui são as garantias
de que **o gerente não executa e não atribui nota**.

**2. Contraprova creditada à trava errada.** Toda fixture negativa é aceita por `bool(errors)`, nunca
por *qual* erro. Três mislabels demonstrados: *"embute julgamento em texto livre"* morre por
**type-check**; *"relatório inclui nota"* morre por `additionalProperties:false` — **enquanto a
trava específica de nota nunca é mutada**.

> Não é morte por exceção. É **crédito à trava que não disparou** — um degrau novo na progressão que
> esta casa já documentou: trava sem call site → call site por nome → retorno descartado → efeito
> por nome de agregador → **caso vermelho creditado à trava errada**.

**O conserto não precisa de invenção:** a técnica certa já existe no pacote — *"o schema aceitou **e**
o portão composto pegou"* — e foi usada em **2 de ~46 casos**.

## O achado estrutural, que vale para os quatro

> **Nenhum dos quatro valida uma missão de ENTRADA contra o envelope do vizinho.**
> A fronteira está provada numa direção só: todos provam que o **retorno** cabe no consumidor;
> nenhum prova que **entende o que recebe**.

Caso concreto, conferido pelo CEO: o `arquitetura-dados` declara em **três** lugares
(`protocolo-de-dados.md:10` e `:71`, `CONTRATO-DE-COMPROMISSO.md:44`) que a `DEPARTMENT_MISSION` traz
`architectural_constraint` — campo que **não existe** no `departmentMission` do Diretor, que é
`additionalProperties: false`. A restrição vinculante só viaja como prosa.

E a `i2` achou que o `to_department_return` do mesmo pacote monta o envelope **sem**
`delegated_dependencies` e com `pending_refs: []` fixo, mesmo com dependência preenchida no ledger.

## O que os juízes declararam contra si

- **Uma julgou `ab5882c` quando o contrato selou `4446786`** e declarou: *"não troquei de árvore para
  o número bater — mas se a intenção era medir `4446786`, as cinco notas saíram de árvore diferente
  da contratada, e essa decisão é do CEO."* **Decisão do CEO:** `ab5882c` é filho direto de
  `4446786` e o único delta é o commit que selou esta própria recoleta — a árvore dos pacotes é
  idêntica. **As notas valem.**
- *"`arquitetura-dados` e `conteudo-marketing` estavam em **9** até eu achar o segundo risco em cada
  um; a fronteira 8/9 depende de quanto cavei, não de regra estável."*
- *"Achei o defeito do `arquitetura-dados` porque fui abrir o converter do pacote que **já ia para
  nota alta**; apliquei o mesmo escrutínio aos outros depois, não antes."*
- *"acuso o pacote de não provar que apagar um check fica vermelho — **e eu também não provei**."*
- As duas de `robustez` expuseram a mesma fronteira sem combinar: quem ler *"nada passa por presença
  de string"* como restrito a travas de **comportamento** chega em 7 legitimamente.

## Estado da Estrutura após esta rodada

**10 aprovados de 15**, contra 7 antes. Restam cinco: `qa-usabilidade` (`C03` = 6, caminho conhecido)
e os quatro do **núcleo de comando** — `ceo-maestro`, `diretor-de-lentes`, `departamento-juizes` e
`departamento-negocios` —, todos com nota de **2026-07-29** e **nunca rejulgados**.
