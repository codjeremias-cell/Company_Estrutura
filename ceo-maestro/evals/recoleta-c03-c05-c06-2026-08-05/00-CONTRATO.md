# Contrato — recoleta de `C03`, `C05` e `C06` nos quatro que ainda travam

- **Selado por:** `ceo-maestro`, em 2026-08-05, **antes** de qualquer parecer desta rodada.
- **Decidido por:** **Jeremias** — *"primeiro vamos atingir o mínimo e pôr em produção interna"*.
- **Árvore julgada:** commit **`4446786`**.
- **Nível exigido:** `INTERNO` (7–9 → `ACEITO_USO_INTERNO`).

## Escopo — só o que trava, e só onde trava

| pacote | critérios a remedir | dona |
|---|---|---|
| `departamento-arquitetura-dados` | `C05` | `experiencia-e-risco` |
| `departamento-desenvolvimento` | `C05` | `experiencia-e-risco` |
| `departamento-conteudo-marketing` | `C05`, `C06` | `experiencia-e-risco` |
| `departamento-qa-usabilidade` | `C03`, `C06` | `C03` → `robustez-e-evidencia` · `C06` → `experiencia-e-risco` |

**Os demais critérios não são remedidos.** Valem as faixas de 2026-08-04, e o `C04` de 2026-08-05.
Veredito de **régua mista**, com as três datas no registro — como nas rodadas anteriores.

Duas instâncias por lente, worktrees isolados.

## Os critérios, íntegros

- **`C03` — Trava com prova.** Cada trava tem caso **executado** que a faz **reprovar**; nada passa
  por presença de string; **morte por exceção não conta como pega**.
- **`C05` — Uso pela cadeia.** O pacote funciona quando acionado **pela cadeia**, não só no próprio
  fixture. A fronteira com os vizinhos é operável: o gerente sabe o que despachar, o agente sabe a
  quem responder, e o retorno cabe no envelope do vizinho. **Verde no próprio teste não prova que a
  cadeia atravessa.**
- **`C06` — Limites declarados.** O pacote diz o que **não** fecha, com **dono** e **condição de
  fechamento verificável**. Confissão que confessa o que passa e cala o que não passa é o defeito.

Definições íntegras em
[`../julgamento-nove-departamentos-2026-08-04/00-CONTRATO.md`](../julgamento-nove-departamentos-2026-08-04/00-CONTRATO.md).

## O que mudou na árvore desde a medição de 2026-08-04

1. **A canonização da T19** (2026-08-05): a checagem de digest deixou de ser tautológica em 10
   pacotes; cópias privadas de `digest()` foram removidas; identidade de candidato passou a ser por
   conteúdo (`ADR-021`).
2. **Os nove adendos de contagem** (tarefa 25): cada pacote redeclara a contagem vigente **ao lado**
   do `PLACAR.md`, que ficou intacto.
3. **Nada mais.** Nenhum `SKILL.md`, contrato, schema ou agente foi tocado.

**Pende, e não está na árvore:** o candidato da T27 (contagem exigida por código) **não foi
canonizado** — está julgado por ninguém. Se o `C03` do `qa-usabilidade` depender de trava que a T27
instala, isso é **estado futuro**, não presente: julgue o que está na árvore.

## Execução: o CEO é o executor

Saída crua dos quatro em [`saida-crua/`](saida-crua/), com `00-RESUMO.json`. Acompanha **inventário
por pacote** (agentes, references, schemas, adendo) porque `C05` e `C06` se leem **no pacote**, não
na saída do validador. Número que não existe ali vira `n/a` com motivo verificável.

**As lentes não executam.**

## Contexto proibido

- `../julgamento-nove-departamentos-2026-08-04/02-AGREGACAO-E-CORRECOES.md`, `julgamento/`,
  `rejulgamento-c04/` (todos os níveis) e `../../REGISTRO-DE-VEREDITOS.md` — **contêm as notas de
  `C03`, `C05` e `C06` que você vai remedir**.
- Os vereditos da T19 e o placar da T27.
- **Proibida busca larga sobre pastas `julgamento*`, `pareceres*` ou `rejulgamento*`** — três juízes
  já se contaminaram por fragmentos de `grep`, não por abrir arquivo. Se topar com nota, **pare e
  declare**.

## Schema do parecer — estrito, validado na coleta

```json
{"artifact_type":"JUDGE_OPINION","judge_id":"agente-julgar-<lente>","lens":"<lente>",
 "instancia":1,"round":"recoleta-c03-c05-c06",
 "created_at":"<ISO-8601 com fuso>","commit_julgado":"<hash completo>","required_level":"INTERNO",
 "scores":[{"package_id":"departamento-arquitetura-dados","criterion_id":"C05",
            "score":7,"razao":"...","evidencia":["caminho:linha"]}],
 "minimo_dos_meus_criterios":7,
 "confidence":"alta|media|baixa","por_que_essa_confianca":"...",
 "o_que_declaro_contra_mim":["..."]}
```

Uma entrada em `scores[]` **por par (pacote, critério) que lhe cabe** — nem mais, nem menos. Chave
divergente volta para reemissão (uma vez).

## Regras

Nota **inteira** 0–10 · `10` exige declarar que procurou o risco e não achou · evidência = caminho
com linha ou referência à saída crua · `n/a` só com motivo verificável · **nunca comparar um
departamento com outro** · o juiz não conserta nada · o **FAIL da série de ADR** (um por pacote,
cópias de laboratório de outra frente) **não é defeito destes quatro** — desconte e diga que
descontou.
