# Achados da T29 que o CEO conferiu na fonte — para consertar DEPOIS da medição

> Escrito em 2026-08-06, com quatro juízes ainda lendo a árvore. **Nada aqui foi consertado
> ainda**, de propósito: mexer na árvore sob medição é alterar a evidência, e esta casa já
> perdeu três medições assim num único dia.

## 1. Deriva de contagem em tempo presente — 11 de 15 pacotes

`robustez-e-evidencia/i1` acusou no `ceo-maestro`. Conferido, e é maior: **11 dos 15 `PLACAR.md`**
declaram *"a cadeia canônica **hoje** soma **1531/1531 PASS**"*, enquanto a saída crua desta
mesma rodada tem FAIL nos quatro pacotes medidos.

| tempo verbal | pacotes |
|---|---:|
| **presente** (alegação corrente, falsa) | **11** |
| passado — *"Naquela medição, a cadeia canônica somava"* | 2 |
| sem a frase | 2 |

Os dois corrigidos são `diretor-de-lentes` e `departamento-juizes`.

> **O padrão é o conhecido:** a correção **existe**, foi aplicada em dois arquivos e **não
> propagou**. Conserto em prosa, sem trava que force os demais. É o
> `aviso-em-prosa-nao-previne-erro` pela quinta vez.

**Fora da Estrutura:** `CLAUDE.md:55`, na raiz do cofre, carrega o mesmo `1531/1531 PASS` como
estado corrente.

**Conserto correto (não é reescrever os 11):** derivar a frase, ou proibi-la. Um número de
**cadeia** dentro de um placar de **pacote** é o defeito — nenhum pacote consegue medir a cadeia,
então nenhum pode declará-la. A trava pertence ao validador, não ao texto.

## 2. Cobertura dos adendos de contagem — 9 de 15

| tem adendo | não tem |
|---|---|
| 9 dos 10 operacionais (falta `auditoria-responsabilidades`) | `ceo-maestro`, `diretor-de-lentes`, `departamento-juizes`, `departamento-negocios`, `departamento-evolucao-skills`, `departamento-auditoria-responsabilidades` |

Os adendos da T25 foram feitos para os nove que estavam sendo julgados. **Os seis restantes
ficaram porque não estavam na frente daquele dia** — que é exatamente como a deriva nasce.

## 3. Placar do `departamento-negocios` — confirmado

| onde | declara |
|---|---|
| `evals/PLACAR.md:11` | **`226/226 PASS, 0 FAIL, 0 WARN`** |
| saída crua desta rodada | **`RESULTADO: 230/233 PASS; 3 FAIL; 0 WARN`** |

Dos 3 FAIL, 1 é a série de ADR (alheia) e 2 são cascatas de sub-execução. Mas **`226` ≠ `230`**
independe disso: são **4 casos a mais** que a receita devolve e o placar nunca redeclarou.

## 4. Placar do `diretor-de-lentes` — confirmado, e a linha é a pior possível

`evals/PLACAR.md:10-12` traz a tabela sob o cabeçalho literal **`| Medição ativa | Resultado |`**,
e a célula diz **`79/79 PASS`**. A receita devolve **`99/100 casos passaram`**, com 1 FAIL.

> Não é um número velho num rodapé histórico. Está sob a palavra **"ativa"**.

## 5. Meu `00-RESUMO.json` — mecanismo rastreado até o fim

O juiz foi além do que eu tinha: o validador do `departamento-negocios` imprime `combined[-500:]`
do vizinho como detalhe de FAIL **e reimprime no rodapé**. Por isso a última linha `Resultado:`
do stream de Negócios é o `99/100` **do Diretor** — e minha receita (*"sumário = ÚLTIMO da
saída"*) capturou esse. O sumário próprio dele usa outro token (`RESULTADO:` em caixa alta) e
minha regex não o casava com prioridade.

O corte em 500 chars é também a origem da linha ilegível `regressão passa: ceo-maestro: eitado`.

**E o meu JSON se autocontradiz:** publica `3 FAIL` ao lado de `99/100`, que implica 1 falha.
Uma conferência de uma linha teria pego. Não fiz.

## 6. `anyOf` inerte — confirmado, e morto duas vezes

Além de o motor compartilhado não implementar `anyOf` (`_compartilhado/validador_schema.py:14-18`),
os três ramos são `properties` **sem `required`** — então o ramo `critical_fail` é vacuamente
verdadeiro para qualquer instância que omita o campo. Mesmo com `anyOf` implementado, não pegaria.
