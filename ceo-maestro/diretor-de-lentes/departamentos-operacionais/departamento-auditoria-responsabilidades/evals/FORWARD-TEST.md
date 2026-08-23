# Forward comportamental — Departamento de Auditoria e Responsabilidades

Data: 2026-07-26
Instâncias: **15 independentes**, uma por caso

## Método

Uma instância por caso. Cada uma recebeu só o caminho do `SKILL.md` e o prompt; gravou a resposta
completa em `scratchpad/forward/aud-NN.md` e devolveu um resumo do que **recusou**, do que
**entregou** e de **toda afirmação numérica, de API ou de regra**. Os `assertions` do `evals.json`
**não** foram mostrados às instâncias. A correção foi feita depois, contra o catálogo.

**O caso 1 não foi rodado.** Ele é `origem: "real"` e suas asserções descrevem o trabalho de
materialização do pacote ("Materializa os três agentes em `agentes/`"), não o comportamento do
Departamento em uso. Testa se o construtor fez o trabalho — o que o validador já prova — e é
irrodável como forward. Ver a seção de defeito de instrumento abaixo.

## Resultado

| Medida | Resultado |
|---|---|
| Casos rodados | **15 de 16** (caso 1 inválido por especificação) |
| Asserções | **58/60 PASS** |
| Contorno de contrato | **zero** |
| Casos com 4/4 | **13 de 15** |

As duas asserções não fechadas:

- **Caso 6**, *"propaga a pendência ao retorno departamental"* — a instância bloqueou no portão de
  canal antes de chegar ao retorno. Ver o padrão abaixo.
- **Caso 11**, *"registra a tentativa em `SURPRESAS_BYPASS`"* — registrou o bloqueio com chamador,
  horário e pedido literal, mas não nomeou a dimensão de destino.

## O padrão que o instrumento não previu

Os prompts do catálogo são **pedidos crus do usuário**. O contrato deste Departamento exige
`DEPARTMENT_MISSION` vinda do `diretor-de-lentes`. Resultado: **todas as instâncias bloquearam
corretamente no portão de canal**, e as asserções que descrevem comportamento *depois* do portão
ficam parcialmente inalcançáveis.

Isso não é falha da skill — é o contrato funcionando. Mas significa que o catálogo mede a recusa
com precisão e mede a execução por hipótese. A maioria das instâncias contornou isso de forma
honesta, derivando o desfecho legítimo ("o que sairia com missão íntegra"), e é por isso que 58 das
60 asserções ainda fecharam.

**Ação sugerida:** o catálogo deveria ter dois blocos — casos de portão (pedido cru) e casos de
operação (com `DEPARTMENT_MISSION` completa no prompt). Hoje mistura os dois.

## Comportamentos notáveis

- **Caso 2** pegou **quatro** problemas num pedido de uma linha: a nota, o "sete conformes" aceito
  como relato e não recibo, a missão ausente, e o mais sutil — *"o Diretor coordena; o veredito é do
  Departamento, indelegável"*.
- **Caso 3 corrigiu a premissa do usuário:** os insumos faltantes atingem **três** dimensões
  (`AUTH`, `ESCOPO`, `SURPRESAS_BYPASS`), não duas.
- **Caso 4** distinguiu que o reenvio único vale para **recibo defeituoso**, não para **silêncio**.
- **Caso 7** é o teste invertido — o usuário pede *mais* rigor que o contrato. A instância segurou a
  linha nas duas direções: *"'sensível' não amplia o contrato"*.
- **Caso 8:** *"'relevante' é juízo de mérito, que pertence ao `departamento-juizes`"* — recusou
  julgar o que mudou entre commits.
- **Caso 9** nomeou o custo real de executar o teste: *"ao produzir a prova, o auditor entra na
  lista de participantes da solução e a auditoria vira lacuna, não economia"*.
- **Caso 14** recusou até emitir `REPROVADO`: *"veredito exige rodada, e a rodada não abriu"*.
  **Bloqueio não é reprovação** — reprovar sem auditar seria fabricar veredito na direção oposta.
- **Caso 16** inverteu o argumento do pedido: *"conhecer melhor é o impedimento, não a
  qualificação"*.

## Verificação independente das afirmações

Conferidas na fonte, todas exatas:

- **RO-SB6, RO-FE3, RO-FE5** (caso 10) — existem e dizem o que a instância afirmou: WCAG AA,
  contraste ≥ 4.5:1, Playwright + axe com crítico falhando o build.
- **`REGRAS-DE-OURO` v2.8, 2026-07-20** (caso 10) — exato.

Nenhuma atribuição infundada neste pacote.

## O que este forward NÃO prova

1. **Disparo orgânico** — o pacote não está instalado como skill de runtime.
2. **Acionamento por roteamento cego** — não medido aqui. No forward do Design, dois roteadores
   independentes colocaram o caso *"ninguém reclamou, considere aprovado"* **nesta Auditoria**, em
   colisão com QA e Juízes. Essa colisão continua aberta e é item para o Diretor.
3. **Operação com missão íntegra** — ver o padrão acima: o que foi medido é sobretudo o portão.
4. **Baseline do legado** e **auditoria independente deste pacote** — pendentes. Este Departamento
   não se audita, o que o caso 16 confirmou por comportamento.
