# Placar — Departamento de Inovação e Melhoria

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 141/141 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:acf74d6acc16668995addd26b1d99ce21719a1bac6e7aa0066d3c7c0123ac9dd` | medido-em: 2026-09-02
<!-- /SELO-DE-CONTAGEM -->

## Passagem pelo gate

Este pacote **já foi submetido ao `departamento-juizes`** pela rota canônica — deixou de
estar formalmente não julgado. Os pareceres, as notas e o histórico de rodadas vivem **fora
deste pacote**, em [`ceo-maestro/evals/FORWARD-TEST-JULGAMENTO.md`](../../../../evals/FORWARD-TEST-JULGAMENTO.md).

**Por que não estão aqui.** Uma versão anterior deste placar reproduzia o veredito e a
crítica da rodada anterior. O efeito foi medido no julgamento seguinte: a superfície julgada
passou a conter o julgamento anterior sobre ela mesma, e uma das óticas devolveu o critério
afetado com **confiança reduzida**. Candidato que carrega o parecer do próprio gate contamina
a rodada seguinte. O placar registra **o que o pacote é**; o que o gate achou dele é do gate.

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

### Dono e condição de fechamento, item a item

> Exigido pelos achados `CA-01` e `GR-01`/`GR-02` da remedição de 2026-08-03: pendência declarada sem dono é pendência de ninguém. "O próprio Departamento" significa o pacote que este placar mede — ele responde pela própria evidência.

| item | dono | fecha quando |
|---:|---|---|
| 1 | o próprio Departamento | houver bateria que meça acionamento espontâneo por gatilho, e não só alcance por delegação explícita |
| 2 | o próprio Departamento | o corpus adversarial deixar de compartilhar o motor do validador — hoje ele prova que as 45 mutações conhecidas caem, nunca que não há uma 46ª classe |
| 3 | o próprio Departamento | houver conferência de MÉRITO do brief por instância que não o produziu; derivação impede a gerente de inventar, não impede o agente de errar coerentemente |
| 4 | o próprio Departamento | o anti-julgamento deixar de ser por lista de vocabulário — nota afirmada em paráfrase continua passando |
| 5 | o próprio Departamento | `mode`, permissões e alvo forem conferidos contra o que a ação de fato atingiu, e não contra o que ela declarou |
| 6 | o próprio Departamento | a prova externa for REEXECUTADA, e não apenas autenticada por produtor e digest |
| 7 | o próprio Departamento | houver âncora externa ao pacote que prove a emissão — runtime separado, assinatura fora da árvore ou terceiro que não compartilhe o processo. Depende das tarefas 50 e 57 |
| 8 | o próprio Departamento | a saturação for medida contra o domínio, e não contra o escopo procurado — `declared: true` fala da busca, nunca da existência |


Esta seção existe porque a rodada 2 mostrou que um placar só de verdes mente.
Nada abaixo é acusação de descuido: é o teto do que este pacote consegue
demonstrar hoje.

> **Ajuste de 2026-07-28.** Dois itens desta seção não citavam identificador de
> risco residual. O de comportamento de modelo era rótulo faltando — é matéria do
> **R4**. O de acionamento espontâneo não tinha `R` porque **nenhum existia** para
> o vetor dele: a Estrutura instala porta única, este Departamento não vira skill
> invocável, e portanto acionamento espontâneo não é mensurável aqui. O protocolo
> ganhou o **R9** para declarar esse limite, e o item passou a citá-lo.
>
> A ligação item↔`R` deixou de ser prosa: `placar_errors` a confere, lendo o
> conjunto válido do §12 do protocolo.

1. **Acionamento espontâneo — `SKIP` (**R9**).** Nenhuma bateria provou que
   **este pacote** dispara sozinho a partir do gatilho. Ele só é alcançado por
   **delegação explícita**, que é outra coisa: a Estrutura instala porta única, e
   os 15 gerentes não viram skills invocáveis. Não fecha enquanto a instalação
   for essa.
2. **O corpus adversarial compartilha o motor do validador (**R4**).** Ele prova
   que as 45 mutações conhecidas são rejeitadas; não prova ausência de uma 46ª
   classe.
3. **Comportamento de modelo não é schema (**R4**).** As travas validam artefatos
   e cadeias. Um agente que produz um brief internamente coerente e falso passa
   pelo gate derivado — a derivação impede a gerente de inventar, não o agente.
   É o vetor literal do R4: o gate deriva do insumo declarado, e o insumo é
   escrito pelo agente.
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

**Contagem:** **8 limites, os oito com identificador** — `R9`, `R4`, `R4`, `R7`,
`R2`, `R3`, `R5`, `R6`. O `R1` e o `R8`, de bypass, não incidem nesta rodada e
por isso não aparecem: limite que não incide não vira linha para engordar a
lista. **A ligação item↔`R` agora é conferida em código** (`placar_errors`), com
o conjunto válido lido do §12 do protocolo — não de uma lista no validador.

## Estado do pacote

**Mecânica executada, oito limites residuais declarados acima, nenhum bloqueador
P0/P1/P2 aberto.**

Este placar **não emite veredito sobre o próprio pacote** — nem positivo. Quem
julga é o `departamento-juizes`, e o ADR-002 proíbe autojulgamento; um pacote que
se declara aprovado está fazendo exatamente isso, ainda que com outra palavra. O
placar declara **estado observável**; o veredito é de quem tem contrato para
emiti-lo.

O `R9` não é pendência acionável: enquanto a Estrutura instalar **porta única**,
acionamento espontâneo deste Departamento não é mensurável. Fecha se a instalação
mudar — decisão de runtime, fora do alcance deste pacote.
