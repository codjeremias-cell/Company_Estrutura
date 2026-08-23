# Adendo de contagem — departamento-registros

- **Data:** 2026-08-05 · **Emitido por:** `ceo-maestro`, tarefa 25.
- **Não reescreve o `PLACAR.md`.** O registro original fica intacto; este adendo **redeclara** a
  contagem vigente ao lado dele.

## Por que este adendo existe

A canonização da **T19** (2026-08-05, recibo
`../../../../evals/digest-que-nao-reprova-2026-08-04/51-RECIBO-DE-CANONIZACAO-T19.json`)
acrescentou casos ao validador deste pacote — a checagem de digest da fonte normativa deixou de ser
tautológica e passou a comparar o recomputado contra o declarado em `regras-de-ouro/ORIGEM.md`.

O `PLACAR.md` declara o número anterior à canonização. **Ele não está errado: está datado.** Este
adendo diz qual é o número de hoje, para que *"todo número publicado reproduz por receita, raiz e
critério"* volte a ser verdade sem apagar o registro.

## A contagem

| | valor |
|---|---|
| declarado no `PLACAR.md` (anterior à T19) | **170/170 PASS** |
| **vigente em 2026-08-05** | **173/174** |
| delta | **+4 casos** |

**Receita:** `python evals/validate_workflow.py`, executado **com o diretório de trabalho neste
pacote**, `PYTHONDONTWRITEBYTECODE=1`; o número é o **último** sumário da saída — o primeiro pode
ser eco de sub-execução, defeito medido pelos Juízes na T19.

**Raiz:** `Estrutura Final de Skills`, árvore viva pós-canonização da T19.

**Critério:** casos do validador próprio deste pacote. Não inclui motor compartilhado nem
regressões de vizinhos, que o `PLACAR.md` lista em linhas separadas e que **não** foram remedidas
aqui — continuam datadas.

## As falhas de hoje, declaradas

- `[FAIL] sÃ©rie global de ADR Ã© Ãºnica em toda a estrutura â€” esperado vÃ¡lido`

**A falha da série global de ADR não é defeito deste pacote:** ela acusa o número `020` duplicado
por duas cópias de laboratório deixadas em `ceo-maestro/evals/producao-honesta-2026-08-04/origem-independente-R1/lab/`,
evidência de outra frente. Está registrada como tarefa aberta com dono.

## O que este adendo NÃO faz

- Não altera nota nem veredito — isso é dos Juízes.
- Não remede o motor compartilhado nem as regressões de vizinhos.
- Não afirma que os casos novos passam por mérito deste pacote: eles vêm da trava canonizada na T19.
