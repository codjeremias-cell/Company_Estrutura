# Contrato executivo — T16 · reconciliação dos bloqueadores

- `contract_id`: `CTR-T16-RECONCILIACAO-BLOCKERS-2026-08-07`
- `contract_version`: `1`
- `human_owner`: `Jeremias`
- `executive_owner`: `ceo-maestro`
- `producer`: `diretor-de-lentes`
- `required_level`: `INTERNO`

## INTENT

Reabrir a frente das 23 barreiras de saída convertidas para lista e reconciliar
os dois bloqueadores de governança registrados na campanha histórica de 2026-08-03:
missão do Diretor inválida contra o próprio schema e `candidate_digest` que mede a
declaração, não a árvore do candidato.

## SCOPE_IN

- campanha histórica `ceo-maestro/evals/barreiras-em-prosa-2026-08-03`;
- contrato e 23 barreiras de saída que fundamentam a T16;
- schemas e protocolos canônicos usados pelos envelopes do Diretor, Auditoria e Juízes;
- candidato isolado, provas e retornos dentro de `ceo-maestro/evals/t16-reconciliacao-2026-08-07`.

## SCOPE_OUT

- escrita nos 23 contratos canônicos durante a prova;
- alteração de T38 ou T39;
- T40, T41, T42 e T43;
- estado, memória, promoção, nota ou escolha de vencedor pelo CEO;
- apagar, reescrever ou substituir qualquer evidência histórica de 2026-08-03.

## DONE

1. A missão do Diretor e os envelopes produzidos na nova onda validam contra os schemas canônicos.
2. O candidato isolado usa `candidate_digest` da árvore pela receita canônica e mantém `manifest_digest` separado quando necessário.
3. A prova independente reconfirma a conversão das 23 barreiras, a fidelidade e os casos de regressão, mantendo os limites já observados.
4. Auditoria e Juízes recebem artefatos correlacionados somente se a cadeia anterior estiver íntegra; ausência de capacidade permanece bloqueio nomeado.
5. Nenhuma escrita canônica ou promoção ocorre antes de `JUDGE_REPORT` e decisão executiva.

## RESTRIÇÕES

- O Diretor orquestra e não executa a especialidade diretamente.
- Quem escreve o candidato não pode provar o mesmo candidato.
- Auditoria prova conformidade e não pontua; Juízes pontuam e emitem veredito.
- A campanha histórica é somente leitura e permanece como evidência de origem.
- T38 e T39 continuam pendências independentes, sem compensação entre frentes.
