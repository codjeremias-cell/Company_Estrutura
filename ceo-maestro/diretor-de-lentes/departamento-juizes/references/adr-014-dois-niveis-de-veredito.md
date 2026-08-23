# ADR-014 — Dois níveis de veredito: `VALIDATED` e `ACEITO_USO_INTERNO`

- **Data:** 2026-07-28
- **Status:** aceito por decisão de Jeremias
- **Decisores:** Jeremias
- **Contexto normativo:** [ADR-002 — nota absoluta e modo duplo](adr-002-nota-absoluta-e-modo-duplo.md) ·
  [rubrica-e-corte.md](rubrica-e-corte.md) ·
  [FORWARD-TEST-JULGAMENTO.md](../../../evals/FORWARD-TEST-JULGAMENTO.md)

## Contexto

Em 2026-07-28 o gate julgou pela primeira vez, e o resultado tornou visível uma propriedade
que estava escrita mas nunca tinha sido exercida.

O `score` é **inteiro** de 0 a 10 por schema. O corte era `minimum_score >= 9,5`, pela
**menor** nota, sem compensação. Como não existe 9,5 numa escala inteira, o corte exigia
**10 em todos os critérios aplicáveis** — e a própria [rubrica](rubrica-e-corte.md) já
dizia isso, com todas as letras, declarando-o deliberado.

O primeiro candidato foi o `departamento-inovacao-melhoria`, apontado no
[plano](../../../../PLANO-DE-ACAO-2026-07-27.md) como **o mais conforme dos 15**. Resultado
medido: **sete notas 9 e uma 6**, `minimum_score: 6`, `verdict: REPROVED`.

O dado que decide este ADR não é o 6. É que **corrigir o 6 não faria o pacote passar**: as
outras sete notas são 9, e `9 < 9,5`. Na banda da rubrica, `9` significa *"excelente, sobra
um risco menor nomeado"*. Para atravessar, as oito óticas teriam de declarar, em oito
critérios, que procuraram risco e não acharam.

Se o pacote mais conforme não passa, nenhum dos 15 passa. E um gate que nunca carimba
degenera de dois jeitos conhecidos: ou tudo trava para sempre, ou alguém infla nota para
destravar — e aí o carimbo vira mentira. O segundo é pior, porque é invisível.

## Decisão

**1. Três vereditos, com faixa fixa.**

| `minimum_score` | Veredito | Banda |
|---:|---|---|
| **10** | `VALIDATED` | excelente sem risco nomeável |
| **7–9** | `ACEITO_USO_INTERNO` | polido, ou excelente com risco menor nomeado |
| **≤ 6** | `REPROVED` | cru ou quebrado |

`VALIDATED` **não foi afrouxado**: continua exigindo 10 em todos os critérios aplicáveis.
O que mudou foi passar a existir um veredito para o que a casa antes chamava de reprovado
sem distinguir de defeito.

**2. A régua não se move.** O mapeamento nota → veredito é fixo e não depende de quem
pediu, do prazo, do custo ou do destino. Régua que muda conforme o pedinte é o caminho
curto para a nota inflada.

**3. Quem varia é a exigência, e ela é declarada no envelope.** A `EXECUTIVE_MISSION` traz
`required_level`, o Diretor o propaga no `JUDGMENT_REQUEST`, e o gate do pedinte passa
quando o veredito **alcança** o exigido:

| `required_level` | Passa com |
|---|---|
| `PRODUCAO` | `VALIDATED` |
| `INTERNO` | `VALIDATED` ou `ACEITO_USO_INTERNO` |

O `required_level` **não é inferido**. Missão sem o campo é recusada antes do julgamento e deve
ser reemitida com o nível explícito; se o requisitante não autorizar outro nível, a reemissão
conservadora declara `PRODUCAO`. Falha fechada aqui significa não produzir veredito a partir de
contexto incompleto, e não preencher silenciosamente o campo ausente.

**4. `ACEITO_USO_INTERNO` não é entrega.** Ele libera uso interno e trabalho subsequente;
**não** autoriza publicação, exposição a terceiro, produção, nem é insumo válido para uma
`EXECUTIVE_SUBMISSION` com `required_level: PRODUCAO`. Quem o trata como validação plena
está violando este ADR, não interpretando-o.

**5. O que não muda.** Menor nota, nunca média. Sem arredondamento, sem ponderação, sem
compensação entre critérios. Critério sem nota continua **proibindo** qualquer veredito
positivo e abrindo lacuna. `n/a` verificável continua fora do mínimo. Escala continua
inteira.

## Consequências

**Ganho.** O gate volta a ser usável: passa a distinguir *"tem defeito"* de *"está bom, mas
não é impecável"* — distinção que existia na rubrica, em banda, e não existia no veredito.
E a informação que o julgamento produz deixa de ser binária.

**Custo.** Três schemas ganham um valor de enum; os contratos do CEO e do Diretor passam a
conferir `required_level`; e o `9,5` citado em 241 pontos da árvore vira referência
histórica onde for prosa, e regra corrigida onde for norma.

**Risco declarado — R-A14-1:** `ACEITO_USO_INTERNO` ser lido como "aprovado". A mitigação é
o nome, a decisão 4 e a checagem de `required_level` nos contratos. Nenhuma delas impede
que um leitor apressado veja "ACEITO" e pare de ler.

**Risco declarado — R-A14-2:** o enum passa a misturar idiomas — `VALIDATED`, `REPROVED` e
`ACEITO_USO_INTERNO` no mesmo campo. Foi decisão explícita de Jeremias, com a
inconsistência apontada antes da escolha. O custo é de leitura, não de comportamento.

**Não decidido aqui.** A escala do `departamento-negocios`, que opera com decimais (9,5 /
9,7) na régua interna dele, é outra régua e não foi tocada por este ADR. A divergência entre
as duas está registrada, não resolvida.
