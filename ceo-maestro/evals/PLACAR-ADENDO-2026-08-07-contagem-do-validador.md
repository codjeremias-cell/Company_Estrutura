# Adendo de contagem — `ceo-maestro`, 2026-08-07

> **Por que este arquivo existe.** O [`PLACAR.md`](PLACAR.md) ao lado e o
> [adendo de 2026-08-06](PLACAR-ADENDO-2026-08-06-contagem-do-validador.md) declaram números
> corretos **nas datas em que foram medidos**, e este adendo **não altera nenhum deles**. A receita
> devolve outro número hoje, porque as tarefas 40 e 41 acrescentaram casos. Redeclarar ao lado, por
> adendo datado e **no mesmo ato** que muda a contagem, é o que esta casa aprendeu depois que uma
> canonização somou 47 casos em 15 validadores e redeclarou em 1 — a deriva derrubou o `C04` de
> oito pacotes na rodada seguinte.

## A contagem vigente

| medição | resultado |
|---|---|
| vigente em 2026-08-06 | 107/107 |
| **vigente em 2026-08-07** | **147/147** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## O delta, decomposto — 107 → 147 é +40, e só 13 são desta frente

Número que sobe sem explicação é regressão igual a número que cai. Os quarenta casos têm duas
origens distintas, e elas foram **medidas**, não estimadas:

| origem | casos | como foi medido |
|---|---:|---|
| commit `0a23e1b` (base) | 107 | worktree destacado em `HEAD`, receita literal acima |
| frente concorrente, não commitada | **+27** | diferença entre o worktree em `HEAD` (107) e a árvore de trabalho no início desta sessão (134); o arquivo `evals/validate_workflow.py` estava modificado às 18:15 de 2026-08-07 |
| tarefas 40 e 41 (esta frente) | **+13** | os casos listados abaixo |
| **total vigente** | **147** | |

Os **+27** não são desta frente e não são reivindicados por ela; ficam nomeados porque uma
contagem sem delta explicado é a mesma armadilha que este adendo existe para impedir.

### A cadeia inteira

| medição | resultado |
|---|---|
| registrada em 2026-08-07 (antes desta frente) | 1950/1951 |
| **vigente em 2026-08-07, após as tarefas 40 e 41** | **1990/1991** |

O único `FAIL` continua sendo o mesmo, e não é desta frente: `departamento-conteudo-marketing`,
*"fontes legadas intactas e cópias exatas"* — a tarefa 36, ainda não iniciada. Os outros catorze
pacotes somam **1844** casos hoje, exatamente o mesmo que somavam quando a cadeia foi registrada em
1951 (1844 + 107 = 1951; 1844 + 147 = 1991). A conta fecha dos dois lados.

## Os 13 casos acrescentados

Todos exercitam o **instrumento de medição** — `evals/coletar_saida_crua.py` —, não o objeto
medido. Cada um nasceu de um defeito **confirmado por execução antes de qualquer linha ser
mudada**, e cada um tem uma mutação que o avermelha.

| # | caso | defeito que o originou |
|---:|---|---|
| 1 | ramo da DECLARAÇÃO acusa sozinho | os 5 casos antigos rodavam num fixture em que os dois ramos disparavam; matar `RE_FAIL_DECL` deixava tudo verde |
| 2 | ramo da CONTAGEM acusa sozinho | idem, do outro lado |
| 3 | sumário `SEM_SUMARIO` é problema | `coerencia()` devolvia `[]` e o gate ficava aberto |
| 4 | sumário `AMBIGUO` é problema | idem — e é o estado que o defeito de origem produz |
| 5 | sem sumário e `exit≠0` acusa validador morto | validador que morre saía como medição limpa |
| 6 | `exit=1` com sumário sem falha é contradição | `"exit"` era gravado e o `returncode` nunca comparado |
| 7 | `exit=0` com sumário com falha é contradição | idem |
| 8 | exit coerente não acusa nada | trava que só sabe acusar reprova evidência boa |
| 9 | todo pacote com validador tem expectativa | a tabela tinha 1 chave de 15 |
| 10 | busca segue as três formas de subordinação | `glob` de um nível publicava Diretor com 1 (tem 11) e 13 pacotes com `[]` |
| 11 | expectativa com âncora sumida é ÓRFÃ | expectativa que não aponta mais para o contrato parece conferida |
| 12 | gate fechado não deixa `00-RESUMO.json` | a não-publicação era promessa em prosa: o arquivo era escrito 14 linhas antes do gate |
| 13 | maiúscula acentuada não é mojibake | achado ao rodar nos quinze: "NÃO", "DECLARAÇÃO" e "SUPOSIÇÃO" fechavam o gate sobre saída íntegra |

## Prova de mutação — 8 de 8

Cada trava foi morta uma por vez, com o validador rodado a cada mutação, e exige-se que os casos
**nomeados** fiquem vermelhos. Trava que não avermelha nada não está provada.

| mutação | efeito | caso(s) que avermelharam |
|---|---|---|
| M1 | `RE_FAIL_DECL` nunca casa | 146/147 — ramo da DECLARAÇÃO |
| M2 | `coerencia()` volta a devolver `[]` em estado não determinado | 144/147 — os três casos de sumário |
| M3 | o exit volta a não ser lido | 145/147 — os dois casos de contradição de exit |
| M4 | busca volta a um nível | 146/147 — três formas de subordinação |
| M5 | uma chave sai da tabela | 146/147 — expectativa declarada |
| M6 | conferência da âncora desligada | 146/147 — âncora órfã |
| M7 | `00-RESUMO.json` volta a ser escrito antes do gate | 146/147 — publicação |
| M8 | classe de mojibake volta a engolir ASCII | 146/147 — maiúscula acentuada |

A árvore foi restaurada ao fim e o SHA-256 do arquivo conferido idêntico ao de antes
(`4639ba25ddd73169…`).

**Isolamento medido, e corrigido.** Na primeira passada a M3 avermelhava **também** o caso da
publicação, porque o pacote de mentira bloqueava só pela regra do exit. Um teste de publicação tem
de falar só sobre publicação: o fixture ganhou um segundo motivo independente de bloqueio, e a M3
passou a avermelhar exatamente os dois casos dela.

## O que este adendo NÃO afirma

- **Não afirma nota nem veredito.** Nota é exclusiva do `departamento-juizes`; este arquivo declara
  contagem e prova de mutação, nada mais. As tarefas 40 e 41 nasceram da rodada 2 do núcleo de
  comando, que reprovou os quatro pacotes — este conserto **não** reabre aquele veredito.
- **Não afirma que o coletor está correto**, só que oito defeitos nomeados deixaram de passar e que
  cada trava tem mutação que a avermelha. O limite conhecido: a expectativa do
  `diretor-de-lentes` é **aberta** — o contrato dele diz "`departamento-juizes` e os Departamentos
  operacionais", sem cardinal, então o total dele não é conferível contra o contrato. Só a presença
  dos Juízes e a procedência do resto são. Isso está declarado no próprio código, no campo `nota`.
- **Não altera a árvore canônica** de nenhum pacote além do `ceo-maestro`, e não promove candidato.
