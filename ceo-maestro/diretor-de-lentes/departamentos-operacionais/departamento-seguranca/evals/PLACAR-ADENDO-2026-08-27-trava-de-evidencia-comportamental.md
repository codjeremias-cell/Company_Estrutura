# Adendo de contagem — 2026-08-27 — trava de evidência comportamental

**195 → 205 casos (+10).** Redeclarado no mesmo ato da mudança, como manda a regra da casa:
contagem que muda sem redeclaração vira deriva, e deriva de um pacote derruba o critério de
contagem dos vizinhos na rodada seguinte.

## O que mudou, e por quê

A trava da linha 1428 exigia que `acionou` e `aderiu` fossem **exatamente** `NAO_MEDIDO`, e
acusava qualquer outro valor com *"declara resultado comportamental não executado"*.

Ela existia para impedir que alguém escrevesse comportamento sem ter executado nada — e acertava
nisso. Só que cobrava o preço inteiro: quando a campanha
`MISSION-T71-SANEAMENTO-C13-C14-2026-08-27` finalmente executou os 14 casos contra instância
independente, com resposta crua preservada e conferida caso a caso, **a medição verdadeira também
não podia entrar**. Uma trava que barra a fabricação e a prova junto barra sobretudo a prova, porque
fabricar é o caso raro e medir é o caso que se quer.

**O que entra no lugar da proibição não é confiança: é recomputação.** Resultado diferente de
`NAO_MEDIDO` passa a exigir `evidencia` com o caminho da resposta crua e o seu `sha256`; o arquivo
precisa existir, morar dentro do pacote, e o digest precisa conferir contra os **bytes reais**, pela
função de produção `sha256_file`. Declaração sem lastro continua reprovando — que era, e segue
sendo, o ponto da trava.

## Os 10 casos

| # | caso | espera |
|---:|---|---|
| 1 | catálogo todo `NAO_MEDIDO` segue válido (retrocompatível) | válido |
| 2 | resultado medido com evidência que **recomputa** | válido |
| 3 | resultado medido **sem** evidência | rejeitado |
| 4 | evidência apontando arquivo inexistente | rejeitado |
| 5 | evidência cujo digest **não** recomputa | rejeitado |
| 6 | `acionou` fora do enum | rejeitado |
| 7 | evidência que **existe** mas mora fora do pacote | rejeitado |
| 8 | caminho com `..` que resolve **dentro** do pacote | rejeitado |
| 9 | evidência sem `medido_em` | rejeitado |
| 10 | `NAO_MEDIDO` que mesmo assim anexa evidência | rejeitado |

2 positivos, 8 negativos — a regra `negativos >= positivos` do passo 9 continua satisfeita
(96 · 109).

## Mutação: 7 de 8 mortos, com controle sobrevivente

| mutante | alvo | resultado |
|---|---|---|
| M1 | digest deixa de conferir | **morto** (FAILS=2) |
| M2 | evidência deixa de ser exigida | **morto** por crash |
| M3 | enum deixa de ser checado | **morto** (FAILS=2) |
| M4 | confinamento textual (`..`/absoluto) | **morto** (FAILS=2) |
| M4b | confinamento resolvido (`startswith`) | **SOBREVIVEU** — ver abaixo |
| M5 | existência do arquivo não checada | **morto** por crash |
| M6 | `medido_em` não exigido | **morto** (FAILS=2) |
| M7 | tudo tratado como `NAO_MEDIDO` | **morto** (FAILS=3) |
| **controle** | só o texto de uma mensagem | **sobreviveu**, como devia |

O controle sobreviver é o que separa bateria que discrimina de bateria que mata tudo.

## O sobrevivente, declarado e não escondido

**M4b não é morto por nenhum caso desta bateria.** O confinamento tem duas checagens — a textual
(`..` ou caminho absoluto) e a resolvida (`startswith` depois de `resolve()`) —, e **todos** os
casos de escape que sei escrever em texto são pegos pela primeira. A segunda existe para o que
texto não revela: junction, symlink, reparse point. Exercitá-la exigiria criar um reparse point no
Windows durante a bateria, o que é caro e frágil.

Fica como **defesa em profundidade não exercitada**, e não como cobertura. Ausência de evidência
permanece ausência.

## Dois erros meus nesta mudança, ambos achados pela própria mutação

1. **Dois casos rejeitavam pela razão errada.** O caso do enum (`"TALVEZ"` sem evidência) era
   barrado por *falta de evidência*, e o do confinamento (`../../../etc/passwd`) por *arquivo
   inexistente* — nenhum dos dois exercitava a trava que dizia exercitar. Os mutantes M3 e M4
   sobreviveram e revelaram isso. Consertei os **casos**, não as travas.
2. **Uma corrida de mutação foi morta por timeout antes de restaurar**, e na rodada seguinte eu
   copiei o arquivo **já mutado** como base — o sha256 "conferiu" contra o estado errado, e toda
   aquela tabela era inválida. Restaurei do git e refiz com a base selada por digest **antes** de
   cada mutante. O resultado publicado acima é o da corrida com base íntegra.
