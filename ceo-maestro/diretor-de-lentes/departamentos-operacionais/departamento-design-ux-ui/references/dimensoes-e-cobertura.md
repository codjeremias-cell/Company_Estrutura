# As nove dimensões da superfície — como cobertura, não como nota

Herdadas da `rubrica-de-superficie.md` do legado. Aqui elas **não pontuam**: cada uma recebe um
estado de cobertura e um dono. Pontuar é do `departamento-juizes` (ADR-002).

## Estados

| Estado | Significa |
|---|---|
| `COBERTA` | respondida com evidência `OBSERVED`, `PRODUCED` ou `MEASURED` |
| `PARCIAL` | respondida em parte, com o que falta nomeado |
| `NAO_APLICAVEL` | não incide nesta superfície, **com motivo específico** |
| `AUSENTE` | incide e não foi respondida |

`NAO_APLICAVEL` genérico não vale. "Não se aplica" sem dizer por que esta superfície não tem
data-viz, por exemplo, é `AUSENTE` disfarçado.

## A tabela

| # | Dimensão | Dona | O que a fecha |
|---|---|---|---|
| 1 | Direção deliberada e anti-AI-slop | `agente-direcao-e-anti-slop` | Design Read declarado, direção ancorada em heurística/Lei de UX/dado, e os testes anti-slop de 1ª e 2ª ordem aplicados **sobre a saída de outro agente** |
| 2 | Fluxo, estados e transições | `agente-fluxo-estados-e-transicoes` | caminho ponta a ponta explicável sem o layout, mais **vazio, carregando e erro** como categorias próprias, com prevenção e recuperação |
| 3 | Acessibilidade mensurável | `agente-acessibilidade-medida` | valores **medidos**, não presumidos: contraste real anotado, tab order testada, alvo ≥ 24×24, foco não obscurecido, alternativa ao arrastar |
| 4 | Tipografia, espaço, cor e motion | `agente-linguagem-visual` | estratégia de cor escolhida antes das cores, OKLCH, medida de linha 65–75ch, razão de escala ≥ 1.25, ritmo de layout, motion sem animar layout |
| 5 | Nitidez | `agente-nitidez-e-adaptacao` | comportamento verificado nas densidades, escalas e zoom relevantes |
| 6 | Data-viz | `agente-dataviz` | gráfico escolhido pela **intenção** do dado, armadilhas do tipo declaradas, `data_contract` semântico antes do gráfico |
| 7 | Adaptação nativa por stack | `agente-nitidez-e-adaptacao` | primitivas reais do stack nomeadas; nenhum padrão web forçado em JavaFX/Flutter/nativo, nem padrão mobile em desktop sem motivo observado |
| 8 | Polish Pass operacional | **gerente** | quando a superfície já existe: Audit → Critique → Polish → Animate → Harden → Live, com superfície observável obrigatória |
| 9 | Evidência de conclusão | **gerente** | cada critério com evidência tipada; `UNVERIFIED` explícito onde não houve medição |

O `agente-design-system-e-tokens` não é dono de dimensão: ele produz o **contrato design↔código**
que atravessa 2, 3, 4, 5 e 7 — tokens semânticos de cor, tipografia, espaço, raio, sombra e motion.
Valor solto no lugar de token é achado dele, em qualquer dimensão.

## Regra de fechamento

A entrega fecha quando **toda dimensão aplicável** está `COBERTA` ou `PARCIAL` com o que falta
nomeado, e **nenhuma** está `AUSENTE`. Duas condições adicionais, herdadas do legado e agora
mecânicas:

1. **Estados nunca são adiados.** "Depois fazemos os estados/a11y" não é conclusão de design. A
   dimensão 2 `AUSENTE` bloqueia a entrega mesmo com todas as outras cobertas.
2. **Nada é sustentado por `REPORTED` ou `UNAVAILABLE`.** Critério declarado atendido com esse tipo
   de evidência é rejeitado pelo schema — é a versão dura de *nunca converta relatado em sucesso*.

## Por que estas nove, e não uma nota

A rubrica do legado somava pesos e cortava em 9,5 — um segundo aparelho de julgamento dentro de uma
estrutura que já tem o seu. O que se perdeu ao converter para cobertura foi a **compressão**: uma
nota diz "quase lá" em um número. O que se ganhou foi a **localização**: cobertura diz *qual*
dimensão está aberta, e o Diretor roteia o retrabalho para o agente dono em vez de devolver "8,7,
melhore".
