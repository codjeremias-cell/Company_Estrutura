# Tarefa 10 — provas de nível produção: a premissa não se sustenta

- **work_item_id:** `TASK-10`
- **analisado em:** 2026-08-01
- **resultado:** **bloqueada**, com dependência medida e caminho declarado
- **nada foi alterado**

## O que a tarefa pedia

Produzir provas de nível `PRODUCAO` para os sete pacotes que a rodada 1 aceitou para uso interno:
C02 `evolucao-skills`, C07 `arquitetura-software`, C08 `auditoria-responsabilidades`,
C10 `desenvolvimento`, C11 `design-ux-ui`, C13 `registros`, C14 `seguranca`.

## Por que ela não pode começar

**Seis dos sete fecharam com `minimum_score` exatamente 7** — um ponto acima do corte que separa
`REPROVED` de `ACEITO_USO_INTERNO`. Só C14 fechou em 8.

| pacote | mínimo |
|---|---:|
| C02, C07, C08, C10, C11, C13 | **7** |
| C14 | 8 |

A medição de 2026-07-31 (tarefa 14) estabeleceu que **duas instâncias da mesma lente, sobre os
mesmos alvos, com a mesma rubrica e o mesmo snapshot, divergem até 3 pontos**, e que 3 de 8
vereditos mudaram de faixa conforme qual instância sobreviveu.

Um `7` medido por instância única não é distinguível de um `6`. **O aceite interno desses seis não
está estabelecido** — e produzir prova de produção para pacote cujo aceite interno é indeterminado
seria construir o segundo andar sobre fundação não verificada.

A varredura mecânica da tarefa 14 já havia listado esses julgamentos como leitura suspeita:
*"14 do julgamento dos 15 pacotes (sete fecharam exatamente em 7)"*.

## A segunda dependência, independente da primeira

Mesmo que a nota fosse firme, `PRODUCAO` exige veredito `VALIDATED`, que exige
`minimum_score = 10` **e** `governance_report COMPLIANT`.

Medido em 2026-08-01: `0` de `agente-*` resolvem como skill invocável contra 81 `SKILL.md`
aninhados; a Auditoria não consegue emitir `COMPLIANT`; **nenhum candidato fecha como validação
normal neste runtime**. É o achado que abriu a tarefa 15.

Portanto a tarefa 10 tem **duas** dependências duras, e nenhuma é retrabalho de pacote.

## O que precisa acontecer antes, em ordem

1. **Tarefa 15** — `COMPLIANT` alcançável sob porta única. Sem isso, `VALIDATED` é inatingível
   por construção, e a tarefa 10 é impossível por definição, não por dificuldade.
2. **Tarefa 14** — regra de agregação em vigor, com mais de uma instância por lente.
3. **Remedir os sete** sob a regra nova. O resultado esperado não é confirmação: pela faixa
   medida, é plausível que parte dos seis caia para `REPROVED` e parte suba, e que alguns saiam
   como `NAO_DISCRIMINADO`.
4. **Só então** definir o que falta a cada um para produção.

## O que a rodada 1 já disse que falta, e continua valendo

Do `08-RESUMO.md`, sobre os sete: *"continuam com melhorias obrigatórias antes de uma rodada de
produção: provas ponta a ponta, operações reais controladas, rollback e separação mais forte entre
declaração e execução."*

Essa lista permanece o insumo do passo 4 — ela não depende da nota. Mas transformá-la em plano por
pacote antes de saber quais pacotes de fato estão aceitos seria trabalho jogado fora para uma parte
deles.

## Decisão registrada

A tarefa fica **bloqueada** com motivo medido, não adiada por conveniência. Desbloqueia
automaticamente quando 15 e 14 fecharem e os sete forem remedidos.

Reduzir o escopo agora — por exemplo, produzir provas só para C14, que fechou em 8 — foi
considerado e **recusado**: 8 também está dentro da faixa de variância de 3 pontos, e um único
pacote não justifica abrir uma frente de produção com a régua ainda em conserto.
