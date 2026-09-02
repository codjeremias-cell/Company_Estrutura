# Rubrica `rubrica-corte-v2` e os dois níveis de veredito

Escala única de todo `score` de `JUDGE_OPINION` e de toda linha do `scorecard`. A gerente resolve
a rubrica **antes** de emitir a primeira `JUDGE_ASSIGNMENT` e copia esta tabela literal em cada
atribuição da rodada — agente nunca busca rubrica sozinho e nunca inventa escala.

> **v2, 2026-07-28.** A v1 tinha um corte único em `9,5`, que numa escala inteira significa **10
> em tudo**. O primeiro julgamento real mostrou o efeito: o pacote mais conforme dos 15 tirou sete
> `9` e um `6`, e **corrigir o 6 não o faria passar**. Um gate que nunca carimba trava tudo ou
> convida a inflar nota. A v2 mantém a exigência de `VALIDATED` intacta e acrescenta um veredito
> para o que fica no meio. Decisão em [ADR-014](adr-014-dois-niveis-de-veredito.md).

## Bandas

A nota mede o candidato **contra o critério declarado e observado**, nunca contra um ideal
abstrato e nunca contra o que outro Departamento entregou em outra rodada.

| Banda | Nota | O que significa naquele critério | Efeito no gate |
|---|---:|---|---|
| **quebrado** | 0–3 | não atende, ou atende com defeito que impede o uso; a evidência contradiz o candidato | `REPROVED`; costuma vir com `critical_findings` |
| **cru** | 4–6 | atende em parte, com lacuna observável e nomeável (caso não coberto, estado ausente, prova faltando) | `REPROVED` |
| **polido** | 7–8 | atende o critério inteiro, sem defeito observado; sobra risco menor ou acabamento | não atravessa para `VALIDATED`; **admite `ACEITO_USO_INTERNO`** |
| **excelente** | 9 | atende e supera, mas sobra **um risco menor nomeado** | não atravessa para `VALIDATED`; **admite `ACEITO_USO_INTERNO`** |
| **excelente** | 10 | atende e supera, e **não sobra risco nomeável** naquele critério | única nota que atravessa para `VALIDATED` |

**9 e 10 não são a mesma coisa.** `9` é excelente com um risco menor nomeado; `10` é excelente sem
risco nomeável naquele critério. Quem dá `10` declara, na razão, que procurou o risco e não achou —
`10` por ausência de análise é parecer fora do contrato.

## Os dois níveis

O veredito é um **fato sobre o candidato**, derivado da **menor** nota do `scorecard` aplicável:

| `minimum_score` | `verdict` |
|---:|---|
| **10** | `VALIDATED` |
| **7–9** | `ACEITO_USO_INTERNO` |
| **≤ 6** | `REPROVED` |

## Mais de uma instância por lente — a regra de agregação e o quarto veredito

> **ADR-016, 2026-07-31.** A tabela acima lê **um ponto**. Quando duas instâncias da mesma lente
> julgam o mesmo alvo, o que existe é uma **faixa**, e em 2026-07-31 ela chegou a **3 pontos** —
> três de oito vereditos dependeram de qual instância sobreviveu a uma colisão de arquivo. Decisão
> em [ADR-016](adr-016-agregacao-entre-instancias.md).

**A regra de combinação é declarada antes de qualquer parecer existir.** Ela chega no
`JUDGMENT_REQUEST`, em `aggregation_rule`, junto de `instances_per_lens`:

| `method` | Combina as instâncias da mesma lente por |
|---|---|
| `MENOR` | a menor consolidação entre as instâncias |
| `MEDIANA` | a mediana entre as consolidações das instâncias |
| `EMPATE_DECLARADO` | nenhuma: a divergência é preservada e sai como faixa |

`aggregation_rule.declared_at` precede **todo** `issued_at` de parecer da rodada. Regra escolhida
depois de ver as notas não é regra: é seleção de resultado.

**A regra combina instâncias da mesma lente e não toca a menor nota entre critérios.** `MEDIANA`
aqui é mediana entre leituras da **mesma** ótica sobre o **mesmo** critério — nunca entre critérios
diferentes. A proibição de média, mediana, ponderação, arredondamento e compensação **entre
critérios** continua exatamente como está na seção seguinte.

O relatório passa a declarar `minimum_score_range` (`lo`, `hi`). Com uma instância, `lo == hi ==
minimum_score` e nada muda. Com mais de uma, a faixa é o dado e o ponto é uma leitura dela.

| Faixa medida | `verdict` |
|---|---|
| `lo = hi = 10` | `VALIDATED` |
| `lo ≥ 7` e `hi ≤ 9` | `ACEITO_USO_INTERNO` |
| `hi ≤ 6` | `REPROVED` |
| **`lo ≤ 6` e `hi ≥ 7`**, ou **`lo` entre 7 e 9 e `hi = 10`** | **`NAO_DISCRIMINADO`** |

**`NAO_DISCRIMINADO` não é reprovação nem aceite, e não autoriza nada.** Ele diz que a faixa
atravessa o corte: a medida não separou. Exige `instances_per_lens ≥ 2` e os mesmos gates de
integridade de um veredito positivo — **falha crítica, lacuna de cobertura ou pendência bloqueante
mandam `REPROVED`, não empate técnico**. Carrega `criticisms` e `required_changes` não vazios, e o
que exige não é mudança no candidato: é **mais medida**.

| `required_level` | `NAO_DISCRIMINADO` alcança? |
|---|---|
| `PRODUCAO` | **não** |
| `INTERNO` | **não** |

**A régua não se move.** Este mapeamento não depende de quem pediu, do prazo, do custo ou do
destino do artefato. Régua que muda conforme o pedinte é o caminho curto para a nota inflada.

**Quem varia é a exigência de quem pede**, e ela vem declarada no envelope: a `EXECUTIVE_MISSION`
traz `required_level`, o Diretor o propaga no `JUDGMENT_REQUEST`, e o gate do pedinte passa quando
o veredito **alcança** o exigido.

| `required_level` | Passa com |
|---|---|
| `PRODUCAO` | `VALIDATED` |
| `INTERNO` | `VALIDATED` ou `ACEITO_USO_INTERNO` |

O `required_level` **não é inferido**. Missão sem o campo é recusada antes do julgamento e deve
ser reemitida com nível explícito; sem autorização para outro nível, a reemissão conservadora
declara `PRODUCAO`. Falha fechada não preenche silenciosamente contexto ausente.

**`ACEITO_USO_INTERNO` não é entrega.** Libera uso interno e trabalho subsequente; **não** autoriza
publicação, exposição a terceiro nem produção, e não serve de insumo a uma `EXECUTIVE_SUBMISSION`
com `required_level: PRODUCAO`.

## O corte, e o que continua proibido

- O mínimo é a **menor** nota do `scorecard` aplicável, **nunca a média**.
- **Proibido:** média, mediana, ponderação por `confidence`, arredondamento, compensação entre
  critérios e "nota de conjunto". `6,9` não vira `7`, e `9,4` não vira `10`.
- Critério com `score: "n/a:<motivo>"` verificável **não entra** no mínimo e fica registrado no
  `scorecard`; `n/a` sem motivo verificável é parecer fora do contrato.
- Critério **sem nota** (ótica ausente, critério sem dona, razão única descartada) não vira nota
  estimada: **proíbe qualquer veredito positivo** — `VALIDATED` e `ACEITO_USO_INTERNO` — e abre
  lacuna. Protocolo, §3, regra 5, e §4, regra 2.
- O `9,5` da v1 permanece na história como o corte que exigia 10 em tudo. Ele não é mais o corte;
  quem o citar como regra vigente está lendo documento vencido.

## Fração e escala

Todo `score` e todo `minimum_score` de `JUDGE_REPORT` ou `DEPARTMENT_JUDGE_REPORT` são **inteiros**
de 0 a 10. `9,5` ou `8,5` em um parecer está fora do contrato e volta pelo reenvio único
(protocolo, §3, regra 6) — assim toda nota cai numa banda nomeada e o `scorecard` permanece
legível. O Diretor não agrega nem tira média entre scorecards ou entre réguas heterogêneas: ele
propaga `verdict + required_level`. A régua decimal de Negócios permanece interna ao próprio
Departamento e nunca vira nota dos Juízes.

## Uso e registro

- Uma só rubrica por rodada. Duas em uso é pedido inválido.
- O relatório declara a rubrica efetivamente usada — `rubrica-corte-v2` — e o `required_level` que
  recebeu; sem esses dois registros a nota não é recalculável e o relatório está incompleto.
- Banda diferente entre dois critérios não se compensa: a menor manda.

**Concluído quando:** toda nota da rodada é inteira, cai numa banda nomeada, tem razão e
`evidence_ref` que resolvem, o `minimum_score` declarado é o mínimo verificável do `scorecard`, e o
`verdict` é o que a faixa determina para aquele mínimo — sem discricionariedade.
