# ADR-024 — Isolamento por runtime, não por recusa do agente

- **Estado:** aceito em 2026-08-08
- **Depende de:** [adr-016-agregacao-entre-instancias.md](adr-016-agregacao-entre-instancias.md) ·
  [adr-023-evidencia-simetrica.md](adr-023-evidencia-simetrica.md) ·
  [protocolo-de-julgamento.md](protocolo-de-julgamento.md)

## Contexto — a independência funcionou por honestidade, não por mecanismo

Em 2026-08-04, seis instâncias de juiz (3 lentes × 2) foram despachadas em paralelo, com a regra de
agregação selada antes de qualquer parecer. Uma delas declarou, no próprio parecer:

> *"O diretório temporário é compartilhado com a instância 2: encontrei um gerador de parecer dela
> e **não o abri**. A independência dependeu da minha recusa, não de isolamento do runtime."*

O ADR-016 já trazia a trava T3 — `write_path` exclusivo por emissão, unicidade conferida em código.
Ela é correta e **não cobre este caso**: T3 impede **colisão de escrita**; o que foi medido foi
**leitura**. O arquivo da outra instância estava alcançável, e a rodada inteira apoiou-se na
honestidade de quem o encontrou.

Isso importa porque a independência entre instâncias é **o que faz a regra de agregação valer
alguma coisa**. Sem ela, a `MENOR` entre duas leituras não é a menor entre duas medições
independentes — é a menor entre duas leituras que podem ter se visto.

## Decisão

### 1. `judgeAssignment` ganha `isolation`, com raiz exclusiva por instância

Dois campos obrigatórios quando presente: `mode` (`worktree` ou `pasta-compartilhada`) e `root`.

`pasta-compartilhada` existe de propósito, e não é um atalho: serve para uma rodada **declarar que
não isolou**, em vez de omitir. A trava recusa a rodada do mesmo jeito — mas ausência declarada é
auditável, e ausência omitida não é.

O campo é **opcional** no schema, pela mesma razão que manteve `digest_recipe` (tarefa 42) e
`evidence_symmetry` (ADR-023) opcionais: as rodadas congeladas não o declaram, e reescrever registro
passado para ficar verde é falsificar evidência.

### 2. A trava recusa quatro coisas, e uma delas a T3 deixa passar

| recusa | por quê |
|---|---|
| raízes **não disjuntas** entre emissões | uma instância enxerga a pasta da outra — **a T3 passa aqui**, porque os `write_path` seguem exclusivos |
| `write_path` fora da própria raiz | escrever fora do isolamento o desfaz |
| `pasta-compartilhada` declarada | declarar a ausência é auditável e continua não isolando |
| isolamento **parcial** na rodada | rodada isola ou não isola; parcial é a pasta compartilhada de volta com nome melhor |

### 3. Contenção é por segmento de caminho, nunca por prefixo de texto

`arena/i1` **não** contém `arena/i12`. Comparar por prefixo de texto acusaria a segunda como dentro
da primeira e reprovaria uma rodada correta — falso positivo com cara de rigor, que esta casa já
mediu quando um gate acusou `"NÃO"` e `"DECLARAÇÃO"` de mojibake.

Prova de mutação executada em 2026-08-08: trocar a comparação por segmento por
`str.startswith` derruba **exatamente** esse caso (169 → 168) e nenhum outro. A comparação carrega
peso; não é enfeite.

## O que este ADR **não** resolve, e fica declarado

Na mesma rodada de 2026-08-04, outra instância **executou validadores — o que a `SKILL.md` da
própria lente proíbe** — porque o despacho mandou executar. Obedeceu a quem despachou, violou o
próprio contrato, e declarou o desvio. Rendeu os melhores achados do dia, e as duas regras seguem
escritas e se contradizendo.

Esse conflito é **de quem despacha**, não do agente: ou o contrato muda por candidato julgado, ou o
despacho para de pedir o que o contrato proíbe. Não se resolve pedindo ao agente que escolha qual
das duas ordens obedecer.

Não foi mecanizado aqui porque "o despacho ordena execução" não é detectável a partir do envelope —
a instrução não viaja nele em forma verificável. Fica como **limite declarado** e frente própria, e
não como trava que eu pudesse alegar ter fechado.

## Alternativa recusada — instruir o juiz a não olhar

Foi o que a rodada de 2026-08-04 fez na prática, e funcionou — uma vez, por honestidade de quem
achou o arquivo. É a mesma família de `aviso-em-prosa-nao-previne-erro` e de trava sem call site: a
regra existe, e nada a faz valer. Independência que depende de recusa não é independência; é sorte
com boa reputação.
