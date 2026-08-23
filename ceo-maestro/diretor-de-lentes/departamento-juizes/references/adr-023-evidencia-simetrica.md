# ADR-023 — Evidência simétrica entre instâncias

- **Estado:** aceito em 2026-08-08
- **Depende de:** [adr-016-agregacao-entre-instancias.md](adr-016-agregacao-entre-instancias.md) ·
  [rubrica-e-corte.md](rubrica-e-corte.md) · [protocolo-de-julgamento.md](protocolo-de-julgamento.md)

## Contexto — o remédio do ADR-016 estava vazando pelo meio

O ADR-016 respondeu a uma medição de 2026-07-31: duas instâncias da mesma lente, sobre os mesmos
alvos e o mesmo snapshot, divergiram **até 3 pontos**, e **3 de 8 vereditos** dependeram de qual
instância sobreviveu. A decisão foi acrescentar instâncias e declarar a faixa: faixa que atravessa
o corte sai como `NAO_DISCRIMINADO`, nunca como veredito favorável.

Em 2026-08-04 a regra foi exercida em escala — nove departamentos, **6 instâncias, 54 pareceres** —
e o resultado foi **7 `NAO_DISCRIMINADO` de 9**, com divergência em **60% dos 40 pares**
(lente, critério). Um critério, o `C04`, atravessou o corte em **8 dos 9** pacotes.

Ao abrir a causa, ela não era a que o ADR-016 supunha. **Não era discordância: era evidência
assimétrica.** Uma instância acrescentou uma linha à fonte normativa e mediu quantos casos mudavam;
a outra não rodou esse experimento. A primeira enxergou um defeito que a segunda **não podia** ver.
A regra selada proíbe escolher a instância mais bem informada — e é certo que proíba —, mas então o
`NAO_DISCRIMINADO` daquela rodada não estava dizendo *"as duas discordam"*. Estava dizendo *"uma
cavou mais fundo"*.

A consequência prática é que o remédio do ADR-016, sozinho, **piora o custo sem melhorar a medida**:
acrescentar instâncias sobre evidência desigual multiplica o despacho e produz um veredito que não
alcança `required_level` nenhum. Uma rodada de três instâncias sobre sete pacotes custa vinte e um
despachos para colher "indeterminado".

## Decisão

### 1. A simetria é declarada na regra de agregação, antes de qualquer parecer existir

`aggregationRule` ganha `evidence_symmetry`, com três campos obrigatórios quando presente:

- `battery` — a lista fechada do que **toda** instância recebe já executado;
- `evidence_digest` — o digest daquela evidência;
- `declared_at` — o instante da declaração, que tem de ser **anterior** a toda emissão.

O campo é **opcional** no schema, e de propósito: as rodadas congeladas não o declaram, e reescrever
registro de rodada passada para ficar verde é falsificar evidência. Rodada que não declara simetria
segue sob o ADR-016 puro.

### 2. O digest viaja no envelope, não só na regra

`judgeAssignment` ganha `evidence_digest`. Quando a rodada declara simetria, **toda emissão** carrega
o digest, e ele tem de bater com o declarado.

Isso não é redundância. Em 2026-08-08, a receita do digest de custódia estava canonizada no schema,
correta e acessível — e **ausente do envelope**. O juiz despachado gastou **oito receitas plausíveis**
e emitiu um achado crítico contra uma custódia que conferia. Quem lê o envelope não lê o schema.

### 3. O extra é declarado, e costuma ser o achado da rodada

A `battery` fecha o piso, não o teto. Instância que rodar além dela **declara o extra**. O corolário
medido em 2026-08-04 é que, quando o `NAO_DISCRIMINADO` se concentra em **um** critério, o
experimento que só uma instância rodou costuma ser o achado mais valioso da rodada — e hoje ele
chega disfarçado de empate.

### 4. A trava é código, não parágrafo

`trava_evidencia_simetrica` recusa quatro coisas: emissão sem `evidence_digest` numa rodada que
declara simetria; digest divergente entre emissões da mesma rodada; bateria declarada **depois** da
emissão; e `evidence_symmetry` malformada. Cinco casos no validador — um positivo, três negativos e
um que prova o silêncio para rodadas congeladas.

Prova de mutação, executada em 2026-08-08: desligar a trava derruba **exatamente os três negativos**
(162 → 159) e deixa os dois positivos verdes. Verde no positivo não prova trava nenhuma.

## Alternativa recusada — subir o número de instâncias

Era o caminho óbvio depois de 2026-08-04: se 2 instâncias indeterminam, use 5. Recusada porque
**ataca o sintoma na direção errada**. Com evidência assimétrica, mais instâncias produzem mais
leituras desiguais, não uma leitura melhor — e o `NAO_DISCRIMINADO` resultante continua não
autorizando nada, agora mais caro. O número de instâncias mede **variância de julgamento**; só faz
sentido depois que a evidência é a mesma. Simetria primeiro, escala depois.

## Alternativa recusada — exigir o campo de todas as rodadas

Tornaria `evidence_symmetry` obrigatório em `aggregationRule` e reprovaria as rodadas congeladas.
Recusada pelo mesmo motivo que manteve `digest_recipe` opcional na tarefa 42: registro de rodada
passada não se reescreve para ficar verde. A fronteira é natural — quem declara, cumpre; quem não
declara, segue sob a regra anterior, e a diferença fica visível no envelope.
