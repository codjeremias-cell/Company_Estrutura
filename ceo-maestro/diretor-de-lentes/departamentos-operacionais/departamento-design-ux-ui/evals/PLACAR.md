# Placar de migração — Departamento de Design UX/UI

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 121/121 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:ee4d09cba66a649a1a8eacd4646fc7708015611d45b2d16a71ffdcda35122214` | medido-em: 2026-08-22
<!-- /SELO-DE-CONTAGEM -->

## Passagem pelo gate

Este pacote foi submetido ao gate em 2026-07-29. Opiniões, notas, veredito e
histórico vivem fora do candidato, no
[resultado consolidado](../../../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md),
para não contaminar uma rodada futura com o próprio julgamento.

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **109/109 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. Naquela medição, a cadeia canônica somava **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

Data: 2026-07-26
Versão avaliada: 1.0.0
Escopo: migração de `SKILL - Nova formula/maestro/comite-de-lentes/lente-designer` (249 arquivos)
para `Estrutura Final de Skills/…/departamentos-operacionais/departamento-design-ux-ui`, com
fundamentação adicional na lente canônica `designer-ux-ui` e no catálogo Impeccable

## Resultado

| Verificação | Resultado | Executado? |
|---|---:|---|
| Validador determinístico do Departamento | 109/109 PASS | **sim** |
| Regressão do `departamento-arquitetura-dados` | 110/110 PASS | **sim** |
| Regressão do `departamento-arquitetura-software` | 70/70 PASS | **sim** |
| Regressão do `departamento-auditoria-responsabilidades` | 64/64 PASS | **sim** |
| Regressão do `departamento-juizes` | 61/61 PASS | **sim** |
| Regressão do `diretor-de-lentes` | 49/49 PASS | **sim** |
| Regressão do `ceo-maestro` | 32/32 PASS | **sim** |
| Motor compartilhado de schema | 55/55 PASS | **sim** |
| Cadeia integrada da estrutura | **1097/1097 PASS** | **sim** |
| Forward comportamental (16 prompts de `evals.json`) | **15/16 casos · 45/45 asserções · 0 contorno** | **sim** — [FORWARD-TEST.md](FORWARD-TEST.md) |
| Acionamento por roteamento cego (2 instâncias) | **16/16 idênticos · 12/16 para este Departamento** | **sim** — idem |
| Baseline do pacote legado | — | **NÃO — existe no legado, não foi reproduzido aqui** |
| Auditoria independente | — | **NÃO — pendente** |
| Parecer dos Juízes | — | **NÃO — pendente** |

```bash
python evals/validate_workflow.py
```

## O que o validador prova

**Pacote e vínculos (10 casos).** Arquivos obrigatórios e as cinco referências; `agentes/` com
exatamente os **sete** nomes canônicos; frontmatter com `description` entre aspas e ≤ 1024;
`SKILL.md` ≤ 500 linhas; `short_description` de 25–64; **posição na hierarquia conferida em
runtime**; fonte normativa no caminho relativo de cada nível; todos os links internos resolvendo;
`workerId` batendo com as pastas reais; e o `enum` das **nove dimensões** idêntico ao da referência.

**Travas do ADR-009 (5 casos).** O validador percorre o schema inteiro e falha se encontrar nome de
propriedade de **nota** (`score`, `minimum_score`, `verdict`, `rubrica`, `ranking`…), de **painel
comparativo** (`painel`, `blind`, `winner`, `provenance_seal`, `opaque_id`, `pairwise`…) ou de
**código** (`html`, `css`, `fxml`, `jsx`, `patch`…). Mais `producer` travado por `const` e
`test_summary.pass` travado em `0`.

**Artefatos aceitos (16).** `DESIGN_PLAN` em `PROJETO` e em `POLISH`, as sete `DESIGN_TASK` e os
sete `DESIGN_RETURN`, `DESIGN_CAPABILITY_GAP` e `DESIGN_LEDGER` com gate aprovado.

**Casos negativos — plano e Design Read (6).** `POLISH` sem superfície observável; `POLISH` com
superfície mas **sem nenhum sinal `OBSERVADO`**; sinal `OBSERVADO` sem localizador; sinal `HIPOTESE`
sem o risco; plano sem nenhum sinal; produtor forjado.

**Casos negativos — tarefa (5).** Capacidade trocada para o agente; acessibilidade emitida fora da
onda de verificação independente; `forbidden_context` sem a proibição de produzir código; tarefa
endereçada a agente de outro Departamento; retorno endereçado ao Diretor.

**Casos negativos — retorno (16).** **`ATENDIDO` sustentado por `REPORTED`** e por `UNAVAILABLE` —
as duas travas centrais do ADR-009 §8 —; `UNVERIFIED` com `UNAVAILABLE` (aceito, é legítimo);
`MEASURED` sem valor e método; `UNAVAILABLE` sem motivo; fluxo sem `VAZIO`, sem `ERRO` e sem nenhum
estado; a11y concluída sem nenhum critério medido; **anti-slop rodado sobre a própria saída**;
tokens sem token; adaptação sem primitiva nomeada; `BLOCKED` sem e com motivo; `NAO_APLICAVEL` sem
motivo específico; `PARCIAL` sem nomear o que falta.

**Casos negativos — livro-razão e gate visual (16).** **Dependência de implementação com o gate
`PENDING`** e com `REJECTED` — o mockup-first virado trava —; gate `PENDING` sem dependência
(aceito); aprovação sem ator nomeado e sem superfície revisável; `ENTREGUE` com a dimensão de fluxo
e estados `AUSENTE` e com a de a11y `AUSENTE`; oito dimensões; dimensão duplicada; sem registro de
emissão; com pendência pendurada; lacuna aberta sem bloquear e com bloqueio (aceito); teste
declarado como executado; retorno fora do Diretor; `INCOMPLETA` legítima.

**Fronteira com os consumidores (6).** O `DESIGN_LEDGER` é convertido em `DEPARTMENT_RETURN` e
validado **contra o schema do `diretor-de-lentes`** — não contra o próprio. O Diretor aceita o
envelope e rejeita autor divergente do produtor e retorno endereçado ao CEO. Mais três confirmações
do outro lado: o Diretor reconhece este Departamento em `operationalDepartment` e em
`knownCapability`, e **o modo `DISPUTA` continua existindo no schema dos Juízes** — a prova de que o
painel comparativo tem dono, e não é este.

**Regras recalculadas em código (24).** Sem consultar o campo declarado: a entrega fecha com as nove
dimensões cobertas e o gate aprovado, e **não fecha** com qualquer dimensão ausente; oito cobertas
não compensam a nona; não fecha com gate `PENDING`, sem registro de emissão ou com lacuna aberta;
`PARCIAL` não impede. Mais a mecânica do gate — aberto trava a dependência, aprovado libera, aberto
sem dependência não é violação — e a da evidência: `REPORTED` e `UNAVAILABLE` não sustentam
`ATENDIDO`, `MEASURED` sustenta, e `REPORTED` em `UNVERIFIED` é legítimo. E os três estados mínimos.

**Coerência do catálogo (5).** 16 casos, todos com `acionou`/`aderiu`, ao menos um de recusa por
fronteira; digests verificáveis.

## Defeito encontrado e corrigido

**A armadilha de profundidade, pela quarta vez.** Os links do ADR-009 para o ADR-006 e o ADR-008
saíram com `../` em vez de `../../`. Mesmo erro do ADR-003, do ADR-006 e do ADR-008 — agora com o
aviso escrito como **armadilha nº 1** do `GUIA-DE-EXPANSAO-E-MIGRACAO.md` desde a primeira
ocorrência.

Quatro repetições com o aviso presente é evidência suficiente para uma conclusão de processo: **o
aviso em prosa não previne esse erro. O `validate_links` o pega, todas as vezes.** A defesa que
funciona é mecânica, e a lição vale além deste caso — foi exatamente o mesmo raciocínio que levou o
ADR-009 a converter a taxonomia de evidência de orientação em prosa para condição de schema.

## O que ainda não foi provado

### Estado vigente das obrigações — conferido em 2026-08-08

> **Duas obrigações desta seção estavam declaradas como pendentes e não estão.** A campanha [`remedicao-dos-sete-2026-08-03`](../../../../evals/remedicao-dos-sete-2026-08-03/PLACAR.md) executou as duas sobre este pacote. O texto dos itens abaixo é registro da rodada em que foi escrito e fica como está; o estado corrente é este.

| obrigação | estado em 2026-08-08 | quem emitiu |
|---|---|---|
| Auditoria independente | **EXECUTADA** em 2026-08-03 · `governance_report` **NONCOMPLIANT** · **4 achados** nomeados, com dono e condição de correção | `departamento-auditoria-responsabilidades` |
| Parecer dos Juízes | **EMITIDO** em 2026-08-03 · veredito **REPROVED** · `minimum_score` **6**, faixa **6–7** · **6 de 8** critérios `NAO_DISCRIMINADO` | `departamento-juizes` |

> **A faixa atravessa o corte, e isso é o achado — não um detalhe.** Duas instâncias da mesma lente, sobre os mesmos bytes e com a mesma rubrica, divergiram em 54% dos pares na campanha. Onde a faixa cruza o 6/7, consertar "até passar" seria mirar num número que a régua não distingue. O aceite interno deste pacote **nunca esteve estabelecido**, e continua não estando.

### Dono e condição de fechamento, item a item

> Exigido pelos achados `CA-01` e `GR-01`/`GR-02` da mesma campanha: pendência declarada sem dono é pendência de ninguém. "O próprio Departamento" significa o pacote que este placar mede — ele responde pela própria evidência.

| item | dono | fecha quando |
|---:|---|---|
| 1 | — | já fechado no próprio texto, com data |
| 2 | o próprio Departamento | o baseline da `lente-designer` for reproduzido com instrumento comum, ou este item registrar a decisão de não comparar, com motivo |
| 3 | `departamento-auditoria-responsabilidades` e `departamento-juizes` | os dois emitirem sobre este pacote sem achado bloqueante e sem `REPROVED`. Ver o estado vigente acima — nenhum dos dois está pendente |
| 4 | o próprio Departamento | o valor de contraste for RECOMPUTADO pelo schema, e não aceito como declarado |
| 5 | o próprio Departamento | houver rubrica com concordância entre instâncias MEDIDA — a remedição de 2026-08-03 mediu 54% de divergência entre instâncias na casa |
| 6 | o próprio Departamento | houver âncora externa ao pacote que prove a emissão — runtime separado, assinatura fora da árvore ou terceiro que não compartilhe o processo. Depende das tarefas 50 e 57; nenhuma trava de dentro fecha isto |
| 7 | o próprio Departamento | a referência externa `pbakaus/impeccable` for PINADA por commit e digest, no molde da tarefa 36 em Conteúdo e Marketing |


`SKIP` declarado com motivo — prova executada > checklist, e sucesso simulado é violação (RI-04):

1. **Forward comportamental — EXECUTADO em 2026-07-26.** 18 instâncias independentes,
   [FORWARD-TEST.md](FORWARD-TEST.md): **15/16 casos, 45/45 asserções, zero contorno**, acionamento
   **16/16 idêntico** entre dois roteadores cegos. A Lei de Ferro segurou sob o pedido direto de
   "faz o código da tela". **Não medido:** disparo orgânico — o pacote não está instalado como skill
   de runtime. **Defeito de catálogo encontrado:** o caso 3 é inválido por especificação (afirma um
   anexo que não existe), então o catálogo tem 15 casos válidos, não 16.
2. **Baseline — este é o caso especial deste pacote.** A `lente-designer` **tem** baseline
   registrado (`evals/placar-baseline.md`, três rodadas de evals em `.mjs`). Ele **não foi
   reproduzido aqui**, e os dois instrumentos não são comparáveis: o legado media a orquestração com
   descoberta de executores, que este pacote deliberadamente não tem. Portanto **a afirmação "a
   migração melhora o comportamento" não só não foi medida — ela não é medível pelos instrumentos
   existentes** sem um catálogo comum novo. É a dívida mais concreta deste Departamento.
3. **Auditoria independente e parecer dos Juízes.** Pendentes.
4. **R2 — `MEASURED` depende de quem mede.** O schema exige valor e método; **não recomputa o
   valor**. Contraste declarado `5.2:1` com método plausível passa. Encarece a fabricação; não a
   impede.
5. **R3 — anti-slop é juízo, não métrica.** Os testes de 1ª e 2ª ordem são qualitativos. A separação
   de agentes reduz a autocomplacência; não a elimina.
6. **R5 — existência das ondas.** Um `DESIGN_LEDGER` coerente é reproduzível sem nenhuma
   `DESIGN_TASK` emitida.
7. **R6 — Impeccable é referência externa** (`pbakaus/impeccable`, Apache-2.0). Se ela mudar, este
   pacote não é notificado.

## Efeito sobre a estrutura

Com Design migrado, o `departamento-juizes` passa a ter um **segundo cliente para o modo `DISPUTA`**
— alternativas visuais chegando pelo Diretor. E o `departamento-desenvolvimento`, ainda ausente,
acumula agora dependências de três Departamentos: Arquitetura, Dados e Design.

O legado permanece **intacto**, com os 249 arquivos, o `placar-baseline.md` e as três rodadas de
evals — rollback manual, nunca fallback automático.
