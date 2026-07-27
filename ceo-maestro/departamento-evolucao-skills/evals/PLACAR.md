# Placar — Departamento de Evolução de Skills

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **57/57 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. A cadeia canônica hoje soma **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../ORGANOGRAMA.md).
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

`SKIP` declarado com motivo:

1. **Forward comportamental — EXECUTADO; esta seção estava vencida.** Corrigido em 2026-07-26: o
   texto anterior afirmava que os 16 prompts não foram executados, mas o
   [FORWARD-TEST.md](FORWARD-TEST.md) registra **15 de 16 casos e 57/60 asserções PASS**, e a tabela
   mecânica desta mesma página já declarava a execução. A seção criada para não esconder ausência de
   prova estava negando prova existente.

   O que **de fato** continua aberto: **3 asserções falharam** (57 de 60) e **1 caso não rodou** (15
   de 16), sem inventário — precisam ser nomeados um a um antes de este item fechar. E a evidência é
   de **aderência**, não de **acionamento**: os prompts rodaram sob carga explícita, então nada aqui
   prova que a skill dispara sozinha pelos gatilhos declarados.
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
