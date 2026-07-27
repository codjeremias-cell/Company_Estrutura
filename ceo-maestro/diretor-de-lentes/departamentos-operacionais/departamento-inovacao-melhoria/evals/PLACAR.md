# Placar — Departamento de Inovação e Melhoria

## Escopo

Migração do legado `orquestrador-inovacao-melhoria` para Departamento
operacional com três agentes, sem autojulgamento.

Data do placar: **2026-07-26**, rodada 3 (pós-correção dos bloqueadores).

## Baseline

- Legado: 22 arquivos, 101.022 bytes, sem agentes/schema/validador.
- Manifesto legado salvo: estava desatualizado em `SKILL.md` e
  `references/contratos.md`; o manifesto vivo foi congelado em
  [`../references/origem-migracao.md`](../references/origem-migracao.md).
- Validações históricas do legado: não comparáveis ao pacote vivo.
- Rodada 2 deste pacote: validador **59/59 PASS** e, ao mesmo tempo, corpus
  adversarial com **39 escapes em 45 mutações**. É a razão de este placar ter
  a coluna `Executado?` e a seção final: verde não é prova.

## Placar mecânico

Todos os comandos abaixo foram rodados na raiz do pacote, com
`PYTHONIOENCODING=utf-8`.

| bateria | Executado? | comando | resultado |
|---|---|---|---|
| pacote, metadata e frontmatter | sim | `python evals/validate_workflow.py` | PASS — 4 skills, 4 `openai.yaml`, limites de linha e descrição |
| estrutura normativa (seções, tokens, protocolo, placar) | sim | `python evals/validate_workflow.py` | PASS — 12 seções na gerente, 11 por agente, 6 tokens por Skill, `Concluído quando:` em 12/12 seções do protocolo |
| schema e semântica | sim | `python evals/validate_workflow.py` | PASS — 11 fixtures positivas + relatório |
| negativos de artefato | sim | `python evals/validate_workflow.py` | PASS — 54 fixtures negativas, todas rejeitadas |
| contraprovas de cadeia | sim | `python evals/validate_workflow.py` | PASS — 20 rodadas fabricadas, todas rejeitadas |
| ponte com o schema do Diretor | sim | `python evals/validate_workflow.py` | PASS — missão aceita pelo schema real; 5 contraprovas de ponte rejeitadas |
| corpus adversarial (45 mutações) | sim | `python evals/corpus_adversarial.py` | PASS — **45/45 rejeitadas, 0 escapes (P1=0, P2=0)** |
| integridade do legado | sim | `python evals/validate_workflow.py` | PASS — 22/22 hashes e 101.022 bytes |
| série global de ADR | sim | `python evals/validate_workflow.py` | PASS — ADR-013 livre e é o próximo número |
| validador do `skill-creator` | sim | `PYTHONUTF8=1 python .../quick_validate.py <pasta>` | PASS — 4/4 (`Skill is valid!`) |
| regressões da cadeia canônica | sim | `python evals/validate_workflow.py` de cada pacote | ver [`../references/origem-migracao.md`](../references/origem-migracao.md) |

**Total do validador local: 122/122 PASS; 0 FAIL.**

## Evals comportamentais

Instrumento: [`evals.json`](evals.json), 16 casos — 1 real e 15 sintéticos, 64
assertions. Os prompts não nomeiam a skill. Execução registrada em
[FORWARD-TEST.md](FORWARD-TEST.md).

| origem | casos | Executado? | acionou | aderiu | estado |
|---|---:|---|---:|---:|---|
| real | 1 | sim | SKIP | 1/1 | PASS com ressalva de carga |
| sintética | 15 | sim | SKIP | 15/15 | PASS com ressalva de carga |

**16/16 casos PASS · 64/64 assertions PASS.**

`acionou: SKIP` é honesto e deliberado: as três instâncias independentes
receberam o pacote por **carga explícita de caminho**, porque a candidata ainda
não estava instalada no runtime. Aderência foi medida; **acionamento
espontâneo não foi**.

## Auditoria adversarial

Parecer executado em [ADVERSARIAL-AUDIT.md](ADVERSARIAL-AUDIT.md):
45 mutações, 45 rejeitadas, 0 escapes.

## O que ainda não foi provado

Esta seção existe porque a rodada 2 mostrou que um placar só de verdes mente.
Nada abaixo é acusação de descuido: é o teto do que este pacote consegue
demonstrar hoje.

1. **Acionamento espontâneo — `SKIP`.** Nenhuma bateria provou que a skill
   dispara sozinha a partir do gatilho, sem carga por caminho. Só fecha depois
   da instalação no runtime, com nova rodada de forward.
2. **O corpus adversarial compartilha o motor do validador.** Ele prova que as
   45 mutações conhecidas são rejeitadas; não prova ausência de uma 46ª classe.
   Risco residual **R4** do protocolo.
3. **Comportamento de modelo não é schema.** As travas validam artefatos e
   cadeias. Um agente que produz um brief internamente coerente e falso passa
   pelo gate derivado — a derivação impede a gerente de inventar, não o agente.
4. **Anti-julgamento é por vocabulário (**R7**).** Nota, ranking ou veredito
   afirmados em paráfrase, fora da lista de padrões, continuam passando.
5. **`mode`, permissões e alvo são conferidos como declaração (**R2**).** Nada
   no runtime impede que a ação real atinja alvo ou ambiente diferente do
   declarado.
6. **Prova externa não é reexecutada (**R3**).** O envelope autenticado do
   `Do` confere produtor, digest e autorização; não roda o teste de novo.
7. **A rodada pode ser fabricada pela própria gerente (**R5**).** Reconciliação
   por digest encarece a fabricação; não a impede, porque tudo é escrito pela
   mesma mão e não há canal de invocação auditável no runtime de hoje.
8. **Saturação prova busca, não existência (**R6**).** `declared: true` fala do
   escopo procurado, nunca do domínio.

## Decisão

`APROVADO PARA PROMOÇÃO`, com os oito limites acima declarados e nenhum
bloqueador P0/P1/P2 aberto.

O item 1 é a única pendência acionável: reabrir o forward para medir
acionamento espontâneo depois que o pacote estiver instalado no runtime.
