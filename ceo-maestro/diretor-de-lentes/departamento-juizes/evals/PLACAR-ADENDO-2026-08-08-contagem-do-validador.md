# Adendo de contagem — `departamento-juizes`, 2026-08-08

> **Por que este arquivo existe.** O [`PLACAR.md`](PLACAR.md) ao lado e o adendo de 2026-08-06
> declaram números corretos **nas datas em que foram medidos**, e este adendo **não altera nenhum
> deles**. A receita devolve outro número hoje porque a tarefa 42 acrescentou dois casos.
> Redeclarar ao lado, por adendo datado e **no mesmo ato** que muda a contagem, é o que esta casa
> aprendeu depois que uma canonização somou 47 casos em 15 validadores e redeclarou em 1.

## A contagem vigente

| medição | resultado |
|---|---|
| vigente em 2026-08-06 | 155/155 |
| **vigente em 2026-08-08** | **157/157** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/departamento-juizes"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## O delta: +2, e os dois são desta frente

| caso | o que trava |
|---|---|
| `a receita publicada do custody_copy reproduz as custódias em disco` | a receita é **executada** contra as 51 custódias reais; se deixar de reproduzir, o pacote fica vermelho |
| `a receita do custody_copy sabe reprovar (fixture nos dois sentidos)` | forma, ordem, normalização de EOL e semântica do `bytes`, cada uma com fixture própria |

### A cadeia inteira

| medição | resultado |
|---|---|
| vigente em 2026-08-08, após a tarefa 36 | 1993/1993 |
| **vigente em 2026-08-08, após a tarefa 42** | **1995/1995** |

Zero `FAIL`.

## A receita que faltava, e o que ela custou

Até hoje o `custody_copy` não tinha receita publicada em lugar nenhum — nem no
`$defs/custodyCopy`, nem na designação, nem no contrato, nem no protocolo §1.3. **Três juízes
reproduziram o digest em 16, 438 e 1440 tentativas; um não conseguiu.**

A receita, achada por reprodução contra as instâncias reais e agora normativa:

1. conteúdo lido **normalizado em LF**;
2. **arquivo** → `sha256` do conteúdo, `bytes` = tamanho do conteúdo;
3. **diretório** → `sha256` da concatenação de `caminho relativo POSIX + conteúdo`, na **ordem
   crescente do caminho relativo**; `bytes` = soma **apenas dos conteúdos**.

### As duas armadilhas, medidas

**`bytes` e `sha256` medem objetos diferentes** no caso diretório: o hash inclui os nomes, o
`bytes` não. Na instância real, `bytes` é 44838 e o blob hasheado é maior. Conferir um contra o
outro acusa divergência sem que nada esteja errado — é o que consome centenas de tentativas.

**O EOL decide.** A instância de arquivo reproduz `83782d15…` com 2453 bytes em LF e devolve
`cfd6c3d5…` com os 2522 bytes CRLF do checkout Windows. **Quem tinha `autocrlf` ligado não
conseguia reproduzir por motivo nenhum ligado a conteúdo** — é a explicação mais provável para o
juiz que falhou, e é a lição `digest-de-arquivo-nao-e-identidade` cobrando de novo. Normalizar
dentro da receita torna o digest independente de checkout.

## Prova de mutação — 4 de 4

| mutação | caso que avermelhou |
|---|---|
| M1 o nome sai da concatenação | 155/157 — autoteste |
| M2 a normalização LF é removida | 155/157 — reprodução contra o disco |
| M3 `bytes` passa a contar o blob hasheado | 155/157 — autoteste |
| M4 a ordenação por caminho é removida | 156/157 — autoteste |

Árvore restaurada com SHA-256 idêntico.

**A M4 só passou a discriminar depois de uma fixture nova, e a primeira passada foi verde.**
Remover o `sorted()` não mudava nada porque, na maioria das formas de árvore, o `rglob` já devolve
a ordem lexical — a ordem estava no código e **não era exercitada por nada**. A forma que
discrimina é um arquivo de raiz que ordena depois do conteúdo de um subdiretório: `rglob` devolve
`["z.txt", "a/b.txt"]` e o lexical é `["a/b.txt", "z.txt"]`. Sem essa fixture, a ordem seria uma
linha decorativa com aparência de trava.

## O que este adendo NÃO afirma

- **Não afirma nota nem veredito.** Nota é exclusiva do `departamento-juizes` enquanto órgão; este
  arquivo declara contagem e prova.
- **Não corrige as 51 custódias já emitidas.** O campo `digest_recipe` entrou no schema como
  **opcional** de propósito: exigi-lo invalidaria evidência congelada de campanha, e reescrever
  registro de rodada passada para ficar verde é falsificar evidência. Custódia nova declara;
  custódia antiga fica coberta pela receita normativa, que é conferida por execução.
- **Limite declarado:** a **base** do campo `path` continua não publicada — numa `JUDGMENT_REQUEST`
  ele parte da raiz do `ceo-maestro`, num parecer de outra campanha parte da pasta da campanha. O
  validador resolve por busca dos ancestrais e a ambiguidade fica registrada no código. Fechá-la é
  declarar a base no `$defs/artifactRef`, que é outra frente.
- **Cobertura real:** 51 custódias declaradas apontam para **2 alvos distintos** em disco. A trava
  reproduz esses dois; não há um terceiro alvo vivo para exercitar.
