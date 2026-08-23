# Adendo de contagem — `departamento-auditoria-responsabilidades`, 2026-08-08 (tarefa 84)

> **Redeclaração no mesmo ato da mudança.** A tarefa 84 acrescentou **um caso** aos dezesseis
> validadores canônicos: `validate_travas_compartilhadas_com_efeito`. Este pacote foi a
> **testemunha** da prova de mutação, e é por isso que o adendo mora aqui.

## Contagem vigente

| medição | resultado |
|---|---|
| Validador determinístico da Auditoria | 177/177 PASS |
| **vigente em 2026-08-08** | **177/177** |

O número corrente e o digest do instrumento que o produziu vivem no **selo** no topo do
`evals/PLACAR.md`, regenerado por `_compartilhado/selar_contagem.py`. Este adendo registra o
**delta**; o selo é que responde por "qual é o número de hoje".

## O delta desta data

`175/175` → **`177/177`**. O `176` intermediário é da tarefa 71 (selo de contagem) e o `177` é
desta; nos dois pacotes que cobram negativos ≥ positivos, cada caso novo entrou com o par negativo,
então lá o delta é `+2` por tarefa.

## O buraco que esta tarefa fechou

`validate_nenhuma_trava_esta_inerte` varre apenas o `evals/validate_workflow.py` **do próprio
pacote**. O `_compartilhado/verificacoes_estrutura.py` — que hospeda as travas chamadas pelos
dezesseis — não era varrido por nada. **Medido em 2026-08-08:** fazer uma trava obrigatória
devolver `[]` sempre mantinha a bateria em 176/176; descartar o retorno do autoteste dela, idem; e
tirar o nome de `FUNCOES_OBRIGATORIAS` também.

**E não era defeito da trava nova.** Mutar `validate_placar_nao_declara_cadeia`, que é da tarefa 34
e alheia a esta frente, escapava igual. Valia para as cinco.

## Prova de mutação — 7 de 8, e o oitavo é o teto

| mutante | veredito |
|---|---|
| M1 selo apagado do placar do vizinho | PEGOU |
| M2 selo com digest de outra versão | PEGOU |
| M3 validador editado sem reselar | PEGOU |
| M4 trava obrigatória inerte | PEGOU |
| M5 autoteste da trava desligado | PEGOU |
| M6 trava fora de `FUNCOES_OBRIGATORIAS` | PEGOU |
| M7 trava **irmã** (tarefa 34) inerte | PEGOU |
| M8 o próprio vigia inerte | **ESCAPA — teto declarado** |

Duas correções nasceram de mutantes que escaparam antes da versão final, e as duas estão no código:

1. **M7 escapava** porque a varredura cobria só `FUNCOES_OBRIGATORIAS`, e a trava da tarefa 34 vive
   em `FUNCOES_DE_ESTRUTURA`. Cobertura pela pegada do conserto — o mesmo defeito que a
   `validate_fonte_normativa_conferida` já tinha registrado nesta casa. Agora varre as duas listas.
2. **M7 continuou escapando** depois disso, por outro motivo: gutar só o **caminho principal**
   (`return []` no fim, guardas de erro intactas) não caía em nenhuma das duas primeiras formas —
   ainda havia um `return` com conteúdo, e a função parecia viva. Entrou a terceira forma, medida
   sobre o módulo **antes** de ser adotada: nenhuma das nove funções varridas termina em lista
   vazia literal, então a regra não avermelha código legítimo.

## O TETO, publicado em vez de escondido

**M8 escapa por construção.** Quem confere as travas obrigatórias é uma delas, e o laço não fecha
de dentro: neutralizar `validate_travas_compartilhadas_com_efeito` não é pego por nada aqui. O
mesmo vale para apontar o `sys.path` a outra cópia do módulo — a conferência 5 da trava compara o
arquivo importado com o da árvore auditada, mas quem controla os dois controla a comparação.

Fechar isto exige **executor externo ao pacote**: é a tarefa 50 (CI externo) e a 57 (manifesto
verificável). O limite é da mesma natureza do `R11` do envelope desta Auditoria — está medido,
nomeado, e não se fecha com mais uma trava do lado de dentro. A prova de mutação carrega o M8 como
caso **esperado**, e ela reclama se algum dia ele parar de escapar sem que a declaração mude.
