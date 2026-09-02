# Placar — Departamento de Evolução de Skills

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 98/98 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:b73fa723bf27c9b3c5403c3ad6bf3ddf1c5c0165a051fc0bd22a1c63a4c55e9b` | medido-em: 2026-09-02
<!-- /SELO-DE-CONTAGEM -->

## Passagem pelo gate

Este pacote foi submetido ao gate em 2026-07-29. Opiniões, notas, veredito e
histórico vivem fora do candidato, no
[resultado consolidado](../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md),
para não contaminar uma rodada futura com o próprio julgamento.

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **57/57 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. Naquela medição, a cadeia canônica somava **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

Data: 2026-07-26
Versão avaliada: 1.0.0
Escopo: **skill nova** (não é migração), criada a pedido de Jeremias como terceiro par executivo do
`ceo-maestro`

## Resultado

| Verificação | Resultado | Executado? |
|---|---:|---|
| Validador determinístico da Evolução | 57/57 PASS | **sim** |
| Regressão do `ceo-maestro` (contrato alterado) | 32/32 PASS | **sim** |
| Regressão do `diretor-de-lentes` | 49/49 PASS | **sim** |
| Regressão do `departamento-juizes` | 61/61 PASS | **sim** |
| Regressão do `departamento-auditoria-responsabilidades` | 64/64 PASS | **sim** |
| Motor compartilhado de schema | 55/55 PASS | **sim** |
| Total mecânico | **317/317 PASS** | **sim** |
| Forward comportamental (15 casos válidos) | **15/15 casos · 57/60 asserções · 0 contorno** | **sim** — [FORWARD-TEST.md](FORWARD-TEST.md) |
| Piloto Fase 1 — medição do trio de fundação Java | **executada** | **sim** — [PILOTO-2026-07-26.md](PILOTO-2026-07-26.md) |
| Conserto do instrumento — 7 casos propostos | **proposta escrita** | não executada — [PROPOSTA-INSTRUMENTO-2026-07-26.md](PROPOSTA-INSTRUMENTO-2026-07-26.md) |
| Piloto Fase 2 — candidatos provados | — | **NÃO — exige execução nova** |
| Auditoria independente | — | **NÃO — pendente** |

```bash
python evals/validate_workflow.py
```

## O que o validador prova

**Pacote e vínculos (8 casos).** Arquivos da gerente e dos **quatro** agentes; `agentes/` com
exatamente os nomes canônicos; **posição sob `ceo-maestro/`** conferida em runtime — se alguém
mover este Departamento para debaixo do Diretor, o caso quebra; frontmatter, limites de tamanho,
`short_description` de 25–64; fonte normativa no caminho relativo de cada nível; todos os links
internos resolvendo; `workerId` batendo com as pastas reais.

**ADR-004 — sem promoção, nota ou vencedor (1 caso).** O validador percorre o schema inteiro e falha
se encontrar `score`, `nota`, `minimum_score`, `verdict`, `winner`, `promoted`, `promotion` ou
`selo` em qualquer profundidade. É a prova mecânica de que este Departamento produz e prova, mas não
seleciona nem promove.

**Contrato do CEO (1 caso, 8 asserções).** Confirma que `directExecutive`, o `producer` causal e o
`CAPABILITY_GAP` do CEO admitem este Departamento, que `recipients` aceita 3 destinatários, e que o
`AGENTS.md` o reconhece. E confirma o que **não** podia mudar: a nota continua sendo dos Juízes, a
exceção continua sendo de Jeremias e a decisão executiva continua sendo do CEO.

**Artefatos aceitos (10).** `EVOLUTION_PLAN`, duas `EVOLUTION_TASK`, os quatro `EVOLUTION_RETURN`
(um por `kind`), `CANDIDATE_SET`, `EVOLUTION_CAPABILITY_GAP` e `EVOLUTION_LEDGER`.

**Casos negativos — tarefa (6).** Capacidade trocada para o `kind`; tarefa de candidato sem gap;
tarefa de prova sem rótulos; prova com um rótulo só; `forbidden_context` sem a proibição de revelar
**quem escreveu**; retorno fora da gerente.

**Casos negativos — retorno (8).** Um candidato só; candidato que **cresce sem remover**; gem sem
saturação; licença desconhecida em degrau 3 (rejeitado) e em degrau 1 (aceito); quem prova
devolvendo candidato escrito; `BLOCKED` com e sem motivo; `acionou: N` com `aderiu: S`.

**Casos negativos — fronteira (3).** Dominado sem dominador nomeado; dominado com dominador
(aceito); fronteira com um único candidato — porque comparar exige dois.

**Casos negativos — livro-razão (6).** Proposta sem placar; proposta sem registro de emissão
(condição de R6); modo `AVALIACAO` devolvendo proposta; `AVALIACAO` devolvendo análise (aceito);
`pending` sem R6; retorno fora do CEO; produtor forjado.

**Fronteira de Pareto recalculada em código (13).** Sem consultar campo declarado: melhor em tudo
domina; pior em um caso **não** domina; empate não domina; caso em `skip` não entra na comparação;
a fronteira mantém os dois complementares; remove o dominado; **o candidato pior na média e melhor
em um caso permanece** (a defesa contra colapso de diversidade); fronteira de um elemento é
detectável; anti-sedimento aceita encolher, aceita crescer removendo o equivalente e rejeita crescer
sem remover; e quem escreve não prova.

## O que ainda não foi provado

### Estado vigente das obrigações — conferido em 2026-08-08

> **Duas obrigações desta seção estavam declaradas como pendentes e não estão.** A campanha [`remedicao-dos-sete-2026-08-03`](../../evals/remedicao-dos-sete-2026-08-03/PLACAR.md) executou as duas sobre este pacote. O texto dos itens abaixo é registro da rodada em que foi escrito e fica como está; o estado corrente é este.

| obrigação | estado em 2026-08-08 | quem emitiu |
|---|---|---|
| Auditoria independente | **EXECUTADA** em 2026-08-03 · `governance_report` **NONCOMPLIANT** · **5 achados** nomeados, com dono e condição de correção | `departamento-auditoria-responsabilidades` |
| Parecer dos Juízes | **EMITIDO** em 2026-08-03 · veredito **REPROVED** · `minimum_score` **6**, faixa **6–7** · **3 de 8** critérios `NAO_DISCRIMINADO` | `departamento-juizes` |

> **A faixa atravessa o corte, e isso é o achado — não um detalhe.** Duas instâncias da mesma lente, sobre os mesmos bytes e com a mesma rubrica, divergiram em 54% dos pares na campanha. Onde a faixa cruza o 6/7, consertar "até passar" seria mirar num número que a régua não distingue. O aceite interno deste pacote **nunca esteve estabelecido**, e continua não estando.

### Dono e condição de fechamento, item a item

> Exigido pelos achados `CA-01` e `GR-01`/`GR-02` da mesma campanha: pendência declarada sem dono é pendência de ninguém. "O próprio Departamento" significa o pacote que este placar mede — ele responde pela própria evidência.

| item | dono | fecha quando |
|---:|---|---|
| 1 | — | já fechado no próprio texto, com data |
| 2 | o próprio Departamento | a Fase 2 do piloto rodar sobre skill nova com instrumento que discrimine — o próprio piloto mediu que só 5 dos 9 casos separam, e `java-db-foundation` tem um único caso |
| 3 | `departamento-auditoria-responsabilidades` | um `AUDIT_RECEIPT` sobre este pacote fechar sem achado bloqueante. Ver o estado vigente acima |
| 4 | `departamento-registros` | a colheita de material rodar de fato pela entrada de aprendizagem, com `EVOLUTION_LEDGER` que a cite |
| 5 | o próprio Departamento | houver âncora externa ao pacote que prove a emissão — runtime separado, assinatura fora da árvore ou terceiro que não compartilhe o processo. Depende das tarefas 50 e 57; nenhuma trava de dentro fecha isto |


`SKIP` declarado com motivo:

1. **Forward comportamental — EXECUTADO; esta seção estava vencida.** Corrigido em 2026-07-26: o
   texto anterior afirmava que os 16 prompts não foram executados, mas o
   [FORWARD-TEST.md](FORWARD-TEST.md) registra **15 de 16 casos e 57/60 asserções PASS**, e a tabela
   mecânica desta mesma página já declarava a execução. A seção criada para não esconder ausência de
   prova estava negando prova existente.

   *Correção de 2026-07-27, segunda passada:* a primeira redação desta linha dizia que as 3
   asserções falhadas e o caso não rodado estavam "sem inventário". **Estavam inventariados** — o
   [FORWARD-TEST.md](FORWARD-TEST.md) nomeia os três casos e o motivo de cada um. O erro foi meu,
   ao corrigir a contradição anterior sem reler o forward.

   O que **de fato** continua aberto, com os casos já nomeados no forward — e aqui, ao contrário
   dos pacotes vizinhos, **as três são lacuna real de comportamento, não defeito do instrumento**:

   - **caso 2** — *"indica que a demanda pode nascer na inovação"*: ofereceu `MINERACAO` mas não
     nomeou o Departamento de Inovação;
   - **caso 3** — *"declara SKIP com motivo quando não há transcript"*: pediu o placar gravado em
     vez de declarar `SKIP`;
   - **caso 5** — *"exige o caso falhando antes e passando depois"*: exigiu o baseline sem
     explicitar o vermelho→verde.

   As três são candidatas a **fixture negativa permanente** no validador deste pacote: cada uma
   descreve um comportamento que o contrato exige e a skill não entregou. O **caso 1 é inválido
   por especificação**. E a evidência é de **aderência**, não de **acionamento**: os prompts
   rodaram sob carga explícita.
2. **Rodada real — Fase 1 executada, Fase 2 não.** O piloto
   [PILOTO-2026-07-26.md](PILOTO-2026-07-26.md) rodou a **medição** sobre os placares gravados da
   campanha C1 (2026-07-19) em três skills do track Java, e produziu um achado que muda a ordem do
   trabalho: **o instrumento de eval não tem poder de separação** — 5 dos 9 casos discriminam, e o
   `java-db-foundation` tem **um único** caso variável, o que torna a fronteira de Pareto
   aritmeticamente impossível ali. A hipótese central — fronteira + material destrava o teto de
   9,27 — **segue não testada**, e agora se sabe por quê: falta metade do instrumento, não o
   método. A Fase 2 (gerar candidatos e provar) exige execução nova, por instância independente.
3. **Auditoria independente.** Pendente, e este Departamento **não se audita** — nem se evolui.
4. **Entrada de aprendizagem — bloqueada no nascimento, desbloqueada em 2026-07-26.** Quando este
   placar foi escrito, `departamento-registros` não existia no caminho canônico, e toda rodada que
   dependesse de colheita abria `EVOLUTION_CAPABILITY_GAP`: o Departamento nasceu com uma das duas
   fontes de material indisponível. O `departamento-registros` **foi materializado em 2026-07-26**,
   com dono da natureza `aprendizagem` e caminho de relatório fixado — **a ausência de produtor
   deixou de valer**. O que continua **não provado** é o fluxo ponta a ponta: nenhum relatório foi
   requisitado através do CEO nem consumido por este Departamento.
5. **R6 — existência da rodada.** Um `EVOLUTION_LEDGER` coerente é reproduzível sem nenhuma
   `EVOLUTION_TASK` ter sido emitida. A condição de registro de emissão encarece a fabricação; não
   a impede.

## Alteração de contrato — atenção à frente de Negócios

Esta entrega **alterou o schema do CEO**, de forma aditiva: `directExecutive`, `causalHeader.producer`
e `capabilityGap.required_capability` ganharam `departamento-evolucao-skills`, e
`executiveMission.recipients` passou de `maxItems: 2` para `3`.

Se a frente que cuida da **lente de negócios** também estiver editando
`ceo-maestro/schemas/ceo-maestro.schema.json`, **estes são os quatro pontos a reconciliar** — as
duas frentes tocam exatamente os mesmos enums. O `AGENTS.md` também mudou, na linha da hierarquia.

## Envelope de fronteira (T87 r4, overlay cand-B)

Herda r3 cand-B. Acrescenta o mesmo fail-closed da MISSION que cand-A r4 e isenta `isolamento*/**/root/otica` na cobertura global, por caminho POSIX exato computado em `_excecoes_otica_de_isolamento`. Nao edita o modulo compartilhado vivo. Este overlay nao e promocao.
