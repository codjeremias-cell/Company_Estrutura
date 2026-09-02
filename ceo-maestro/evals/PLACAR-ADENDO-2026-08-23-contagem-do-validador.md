# Adendo de contagem — `ceo-maestro`, 2026-08-23

> **Por que este arquivo existe.** O [`PLACAR.md`](PLACAR.md) e os adendos de
> [2026-08-06](PLACAR-ADENDO-2026-08-06-contagem-do-validador.md),
> [2026-08-07](PLACAR-ADENDO-2026-08-07-contagem-do-validador.md) e
> [2026-08-22](PLACAR-ADENDO-2026-08-22-contagem-do-validador.md) declaram números corretos **nas
> datas em que foram medidos**, e este adendo **não altera nenhum deles**. A receita devolve outro
> número hoje porque a tarefa 105 acrescentou seis casos. Redeclarar ao lado, por adendo datado e
> **no mesmo ato** que muda a contagem, é o que esta casa aprendeu depois que uma canonização somou
> 47 casos em 15 validadores e redeclarou em 1 — a deriva derrubou o `C04` de oito pacotes na
> rodada seguinte.

## A contagem vigente

| medição | resultado |
|---|---|
| vigente em 2026-08-07 | 147/147 |
| vigente em 2026-08-20 | 151/151 |
| vigente em 2026-08-22, após a tarefa 46 | 166/166 |
| **vigente em 2026-08-23, após a tarefa 105** | **172/172** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## O delta: 166 → 172 é +6, e os seis são da tarefa 105

| caso | o que planta | por quê |
|---|---|---|
| todo limite residual do envelope nomeia dono e condição de fechamento | a varredura das emissões reais da árvore | é o caso positivo: hoje ele fecha porque as 73 ressalvas congeladas estão **nomeadas**, não porque não existam |
| ressalva nova sem dono e sem condição é rejeitada na barreira | `"Ressalva em AUTH: fechar o achado e reexecutar a inspecao"` | é o achado #1 da tarefa 47 na sua forma pura |
| ressalva nova COM dono e SEM condição é rejeitada | `"… dono: ceo-maestro"` | a segunda metade do critério é a que o painel externo mediu como não atendida |
| ressalva nova COM condição e SEM dono é rejeitada | `"… fecha quando: a inspecao for reexecutada"` | condição sem dono é pendência de ninguém |
| ressalva com `dono:` só de pontuação é rejeitada | `"… dono: . fecha quando: reabrir a dimensao"` | foi o **buraco da primeira versão da trava**, pego por execução e não por leitura |
| ressalva nova COMPLETA passa na barreira | dono e condição com substância | o par que impede a trava de virar parede |

**Um caso por forma proibida, de propósito.** Caso que viola duas condições de uma vez continua
vermelho quando uma é neutralizada, e a mutação sai verde — é a regra que a rodada 7 do `OI6-01`
deixou escrita neste mesmo arquivo, para os quatro limites fixos.

## O que foi medido antes de escrever

| medida | valor |
|---|---:|
| emissões reais de `governanceReport` na árvore | 126 |
| entradas de `pending` nelas | 577 |
| entradas que são limite fixo (`R6`, `R9`, `R10`, `R11`) | 504 |
| entradas que são ressalva de rodada, **sem dono e sem condição** | 73 |
| entradas distintas dessas ressalvas (a dívida congelada) | 25 |
| emissões tocadas pela dívida | 26 |
| itens de pendência no `PLACAR.md` dos 16 pacotes | 72 |
| desses, sem dono ou sem condição | 0 |

As emissões de laboratório (`/candidatos/`, backup pré-canonização) e as fixtures ficaram fora da
conta, pelo mesmo critério estrutural que a tarefa 96 usou para separar pacote real de cópia de
campanha: 43 e 7, respectivamente.

**Defeito do meu primeiro instrumento, declarado.** A primeira varredura casou a **definição** do
`$defs/governanceReport` como se fosse emissão, e `description`, `type`, `items`, `minItems`,
`uniqueItems` e `allOf` entraram na medição como se fossem limites. A definição tem `pending` como
objeto, e iterar um objeto devolve as chaves. Corrigido exigindo que `pending` seja **lista** e
excluindo `/schemas/` — e é por isso que o número publicado aqui é 577 e não 583.
