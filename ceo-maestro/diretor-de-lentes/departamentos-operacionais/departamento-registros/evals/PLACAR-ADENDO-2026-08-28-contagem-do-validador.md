# Adendo de contagem — `departamento-registros`, 2026-08-28

> **Por que este arquivo existe.** O [`PLACAR.md`](PLACAR.md) declara números corretos **na data em
> que foram medidos**, e este adendo **não altera nenhum deles**. A receita devolve outro número
> hoje porque a T71 instalou uma trava neste pacote. Redeclarar ao lado, por adendo datado e **no
> mesmo ato** que muda a contagem, é o que esta casa aprendeu depois que uma canonização somou 47
> casos em 15 validadores e redeclarou em 1.

## A contagem vigente

| medição | resultado |
|---|---|
| vigente em 2026-08-23, após a tarefa 97 | 184/184 |
| **vigente em 2026-08-28, após a T71** | **186/186** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-registros"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## O delta: 184 → 186 é +2

| caso | o que planta |
|---|---|
| a régua de leitura de `aderiu` e `acionou` mora no catálogo | o caso **positivo**: `validate_criterios_de_leitura` exige o bloco `criterios_de_leitura` no `evals.json`, com os campos de `aderiu` (`regra`, `conjuncao`, `parcial`) e de `acionou` (`regra`, `superficie_varrida`, `leitura_no_contexto`) |
| catálogo sem régua de leitura é recusado | o par **negativo**, exigido pela regra do passo 9 (negativos ≥ positivos). Passa um catálogo sem o bloco e cobra que a trava **acuse** |

## O defeito que a trava fecha, e por que declarar não bastava

O critério de leitura de `aderiu` e de `acionou` vivia no `FORWARD-TEST.md` **de quem mediu**, não
no catálogo. Foi apontado na rodada 1 de 2026-08-27 e **de novo** na rodada 2, sem fecho nas duas.
Enquanto a régua viaja no bolso do executor, dois medidores produzem placares diferentes sobre as
**mesmas respostas**, e a comparação entre rodadas deixa de significar alguma coisa.

O bloco `criterios_de_leitura` entrou no `evals.json` (versão 1.2.0 → 1.3.0) com o texto **idêntico**
ao praticado nas rodadas 1 e 2 — §1.2 e §1.3 do FORWARD-TEST. Não é critério novo: é o que já valeu,
movido do relatório para o catálogo.

**E declarar sem travar não resolveria.** Medido no mesmo dia, antes de instalar a trava: remover o
bloco inteiro do `evals.json` deixava a bateria **verde em 184/184**. O campo era documentação, não
norma — o padrão que esta casa já nomeou quatro vezes como *aviso em prosa não previne erro*.

## Prova de mutação — três mutantes, três mortos

Mutou-se o `evals.json`, **não** o validador: o selo de contagem confere o digest do *instrumento*,
então mutar o instrumento mataria o mutante pelo selo e não pela trava.

| mutante | o que altera | resultado | caso que reprovou |
|---|---|---|---|
| M1 | remove o bloco `criterios_de_leitura` inteiro | **morto** | `a régua de leitura de aderiu e acionou mora no catálogo` |
| M2 | mantém o bloco, remove `aderiu.parcial` | **morto** | idem — `criterios_de_leitura.aderiu.parcial` ausente ou vazio |
| M3 | mantém o campo, põe só espaços em `acionou.leitura_no_contexto` | **morto** | idem — `criterios_de_leitura.acionou.leitura_no_contexto` ausente ou vazio |

Os três foram mortos pelo caso **nomeado**, com a mensagem apontando o campo — não por efeito
colateral de outra trava.

## O que esta trava NÃO faz, declarado

Ela exige que a régua **exista e esteja completa**; não julga se a régua é boa. Trocar o conteúdo de
`aderiu.regra` por outra política passa na trava — e quebra a comparabilidade com as rodadas 1 e 2.
O próprio bloco diz isso em `_fonte`: quem trocar a regra deve dizê-lo no mesmo ato.
