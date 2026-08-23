# Adendo ao PLACAR — contagem vigente do validador (T19, rodada 3)

- **Data:** 2026-08-05
- **Origem:** `MISSION-DIGEST-QUE-NAO-REPROVA-R3-FINAL-20260805` (tarefa 19, rodada 3),
  candidato `cand-digest-comparado-r3`.
- **Por que um ADENDO e não uma edição:** o `PLACAR.md` deste pacote é registro de rodada
  encerrada, e **registro de rodada encerrada não se toca**. A rodada 2 da T19 reescreveu a
  linha de contagem dentro do próprio `PLACAR.md` (122 → 125) e o julgamento apontou a
  contradição — o item 9 da lista da própria rodada 2 dizia que registro não se reescreve.
  A partir desta rodada, a contagem vigente é redeclarada AO LADO, neste arquivo, e o
  validador lê `PLACAR-ADENDO-*.md` em ordem lexicográfica de nome (a data abre o nome),
  prevalecendo a última redeclaração encontrada. A linha original do `PLACAR.md` permanece
  intacta como registro da rodada em que foi escrita.

## Contagem vigente

O candidato da T19 acrescenta três casos ao validador deste pacote — as três travas de
estrutura (`validate_trava_de_digest`, `validate_sem_check_tautologico`,
`validate_fonte_normativa_conferida`), inseridas no idioma do próprio validador. A contagem
declarada acompanha:

| Item | Estado | Executável hoje? |
|---|---|---|
| Validador determinístico do Departamento | 125/125 PASS | **sim** |

- **Receita do número:** `len(cases) + 1` do próprio `evals/validate_workflow.py` com o
  overlay da T19 aplicado — 122 casos da rodada encerrada + 3 travas de estrutura. O
  validador confere este número contra a contagem real a cada execução, e reprova se
  divergirem.
- **Vale sobre:** a árvore com o candidato `cand-digest-comparado-r3` aplicado. Sem o
  candidato, vale a linha do `PLACAR.md` (122/122), e este adendo não casa com a contagem
  real — o que é o comportamento correto: adendo de candidato não adotado não descreve a
  árvore viva.
