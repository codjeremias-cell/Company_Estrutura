# Placar de migração — Departamento de Registros

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **170/170 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. A cadeia canônica hoje soma **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

Data: 2026-07-26
Versão avaliada: 1.0.0
Escopo: migração de `SKILL - Nova formula/maestro/comite-de-lentes/orquestrador-registros`
para `Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-registros`

## Resultado

| Verificação | Resultado | Executado? |
|---|---:|---|
| Validador determinístico dos Registros | 170/170 PASS (83 positivos · 87 negativos) | **sim** |
| Teste do motor compartilhado (`_compartilhado`) | 55/55 PASS | **sim** |
| Regressão do validador da Auditoria | 64/64 PASS | **sim** |
| Regressão do validador do `departamento-juizes` | 61/61 PASS | **sim** |
| Regressão do validador do `diretor-de-lentes` | 49/49 PASS | **sim** |
| Regressão do validador do `ceo-maestro` | 32/32 PASS | **sim** |
| Total mecânico da cadeia | **430/430 PASS** | **sim** |
| Forward comportamental (16 prompts de `evals.json`) | — | **NÃO — pendente** |
| Baseline comportamental do pacote legado | — | **NÃO — pendente** |
| Acionamento por `description` em runtime | — | **NÃO — pendente** |
| Parecer do `departamento-juizes` sobre estes registros | — | **NÃO — pendente** |

Comandos executados, a partir da raiz da estrutura:

```bash
python "_compartilhado/teste_validador_schema.py"
python "ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-registros/evals/validate_workflow.py"
python "ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-auditoria-responsabilidades/evals/validate_workflow.py"
python "ceo-maestro/diretor-de-lentes/departamento-juizes/evals/validate_workflow.py"
python "ceo-maestro/diretor-de-lentes/evals/validate_workflow.py"
python "ceo-maestro/evals/validate_workflow.py"
```

As contagens de Registros, Auditoria, Juízes, CEO e motor compartilhado permanecem idênticas. O
Diretor passou de 48 para 49 casos pela integração aditiva de Conteúdo e Marketing; a regressão
continua íntegra. O motor compartilhado é **importado**, nunca copiado.

## O que o validador prova

**Pacote e vínculos (4 casos).** Arquivos obrigatórios da gerente e dos **quatro** agentes; `agentes/`
contendo exatamente os quatro nomes do ADR-005; posição sob `departamentos-operacionais/` conferida em
runtime; frontmatter só com `name`/`description`, nome igual ao da pasta, descrição ≤ 1024 caracteres,
`SKILL.md` ≤ 500 linhas e `short_description` entre 25 e 64 caracteres; fonte normativa única no
caminho relativo **de cada nível** (`../../../../` na gerente, `../../../../../../` nos agentes, com o
caminho do agente **proibido** na gerente); todos os links markdown internos resolvendo; e os vínculos
externos existindo em disco — inclusive o `mineracao-e-proveniencia.md` do consumidor do relatório.

**Forma do schema (1 caso).** `$defs` esperadas, todo `$ref` resolvendo, `workerId` e `capability`
batendo com as **pastas reais** de `agentes/`, as oito naturezas, os catorze gates e o ciclo de vida
idênticos às referências — e a conferência estrutural de que `existence` é campo de `destination`, não
de `writeTarget`.

**Autoridade herdada (1 caso).** O schema do Diretor **ainda** reserva `departamento-registros` como
Departamento operacional e produtor conhecido, trava `returned_by` e `causal.producer` no par deste
pacote, mantém `return_to`/`returned_to` no Diretor, mantém a nota com os Juízes e continua exigindo
`candidate_digest` — sem aceitar `source_digest` — no `causalHeader`. Se o outro lado mudar, quebra aqui.

**Exemplos normativos do protocolo (4 casos + 2 estruturais + 3 mutações negativas).** Cada bloco YAML das §1.1,
§1.2, §1.3 e §1.5 é **extraído do arquivo**, tem só os marcadores `<…>` e as uniões `A | B`
substituídos — todo literal do documento é preservado — e é validado contra o schema. As três mutações
provam que o bloco morde:

- a redação anterior da §1.1, com o quarteto no topo e sem `artifact_type` nem `causal`, é **rejeitada**;
- o exemplo da §1.2 sem `verification_mode` nos gates é **rejeitado**;
- o exemplo da §1.5 devolvendo o relatório à própria gerente é **rejeitado**.

**Artefatos internos aceitos (22 casos).** Cinco `ROUTING_DECISION` (pousada, handoff de memória,
recusa de fronteira, sem regra casada e fatia não atômica), cinco `RECORD_TASK` (uma por `kind`), três
`RECORD_RECEIPT`, `REGISTRY_CAPABILITY_GAP`, dois `CONSERVATION_LEDGER`, dois `LEARNING_REPORT` e
quatro `REGISTRY_LEDGER`.

**Casos negativos (87 no total).** Cada atalho que o contrato proíbe é rejeitado por construção:

- **roteamento (14):** natureza que não casa a regra decisora; memória durável gravada ou com escopo de
  escrita do Departamento; registro atômico sem regra; empate sem desempate nomeado; fatia não atômica
  com destino; pouso com existência não verificada, confinamento `unknown`, menos de cinco gates ou sem
  artefato real; convenção decidida por canal 3–4; bloqueio sem motivo; derivado sem fonte resolvida.
- **tarefa (14):** capacidade trocada; gravação sem alvo, com varredura em `FAIL` ou `NAO_VERIFICADO`;
  verificação com alvo de escrita ou com índice a tocar; colheita fora da capacidade dona; retorno fora
  da gerente; produtor forjado; `forbidden_context` incompleto ou sem a proibição de recibos irmãos;
  alvo fora da raiz confiável; varredura adiada sobre insumo já em mãos; e `existence` pendurada no
  `write_target`.
- **recibo (15):** concluído sem registro tocado; bloqueado sem motivo ou com escrita; varredura de
  autoria em `FAIL`/`NAO_VERIFICADO`; `PASS` sem reprodução executável ou com evidência que não
  sustenta; `FAIL` sem dono; independência mecânica sem comando ou em gate de juízo; `NAO_APLICAVEL`
  genérico; criado com baseline anterior; escrita à mão em artefato gerado; gate sem modo de
  verificação; devolução fora da gerente.
- **conservação (6):** fechado sem segunda contagem, com fatia não contabilizada, com `delta_final`
  diferente de zero, com invariante declarado falso ou sem nenhum registro; contagem selada sem
  artefato datado.
- **aprendizagem (8):** devolvido à própria gerente; canal paralelo ao consumidor; produzido para quem
  não encomendou; lição com campos do `gem` do consumidor; lição afirmada de memória; relatório vazio
  sem lacuna; varredura sem saturação e sem lacuna.
- **livro-razão (16):** concluído com gate em `FAIL` ou `NAO_VERIFICADO`, sobre contagem única, com
  lacuna aberta, sem registro de emissão de tarefa (R6) ou com dossiê faltante; lacuna sem o motivo
  parcial correspondente; `pending` sem R6; retorno fora do Diretor; parcial sem motivo; relatório de
  integridade com treze gates ou com gate repetido; degrau mínimo com sinal derrubado; recusa com
  efeito colateral divergente; relatório referenciado sem tarefa de colheita; painel com mais
  executores do que capacidades.
- **lacuna (3):** fechada pela própria gerente; dono fora do Diretor; sem conteúdo preservado.
- **fronteira (8):** ver abaixo.
- **exemplos normativos (3):** as três mutações já descritas.

**Fronteira com o consumidor (11 casos: 3 positivos e 8 negativos).** O `REGISTRY_LEDGER` interno é convertido **mecanicamente**
em `DEPARTMENT_RETURN` e validado contra o **schema do `diretor-de-lentes`**, nunca contra o próprio.
A conversão não é identidade: o `causalHeader` do Diretor exige `candidate_digest` e não conhece
`source_digest` — e há caso provando que **passar o cabeçalho interno sem converter é rejeitado**. O
Diretor também rejeita produtor forjado, retorno assinado por outro Departamento, retorno endereçado ao
CEO, livro-razão embutido como campo novo, retorno sem artefato, retorno sem digest de candidato e
missão que não veio dele.

**Aritmética e regras recalculadas em código (42 casos).** Nada é lido do campo declarado:

- os contadores do `CONSERVATION_LEDGER` são **recomputados** dos estados das entradas e comparados com
  os declarados; o mapa de estado para contador é conferido contra o `enum` do schema;
- os dois invariantes são recalculados, e um caso prova que **esquecer uma parcela da soma daria outro
  resultado** enquanto o campo declarado continuaria dizendo `true`;
- estado em trânsito não alimenta contador e impede o fechamento, mesmo com a soma coerente;
- `closed` é derivado: sem segunda contagem vira `single_count_unverified`; `delta_final != 0` vira
  `bloqueado_conservacao`; fatia não contabilizada não fecha;
- a admissibilidade da recontagem é recalculada: `independent_capability` exige executor distinto de
  quem decompôs; `sealed_prior_count` só vale no degrau mínimo **e** com a contagem datada antes da
  decomposição; a independência do gate só cai por método mecânico selado, e nunca em gate de juízo;
- o `status` da rodada é derivado das definições da §4 — catorze gates com prova concluem; um `FAIL`,
  um `NAO_VERIFICADO`, treze gates, lacuna aberta, registro em trânsito, contagem única ou ausência de
  registro de emissão derrubam para `PARTIAL`; material ausente é `BLOCKED`; e os `partial_reasons`
  saem ordenados por gravidade;
- a tabela de rejeição da §1.0 é reexecutada, inclusive a **regra central**: dossiê incompleto **não**
  bloqueia a rodada;
- a conversão de estado de descoberta para `panel[].status` cobre os sete casos, e todo estado sem
  tarefa emitida abre lacuna;
- o `test_summary` do retorno é `0/0/0`.

## Três defeitos de contrato conferidos nesta etapa

A fase anterior apontou três divergências entre a redação e o schema. Cada uma foi **reconferida no
arquivo** antes de qualquer edição, e as três já estavam conformes no pacote — nenhuma linha do
protocolo nem do schema precisou mudar. O que faltava era **teste**: sem caso, a conformidade de hoje
não sobrevive à próxima edição. Os três agora estão travados por caso executado.

| # | Divergência apontada | Estado conferido | Caso que a tranca |
|---|---|---|---|
| B1 | `return_to` do `LEARNING_REPORT` divergente entre a §1.5 e o `$defs/learningReport` | **não se confirma**: a §1.5 escreve `diretor-de-lentes` (linha 351) e o schema trava o mesmo `const`; o ADR-005, decisão 5, e o ADR-004 do consumidor sustentam o valor — o artefato é de Departamento, e Departamento tem **um** canal de retorno, com a referência subindo ao CEO pelo Diretor | `B1: §1.5 e schema alinhados no return_to` compara o valor **lido do documento** com o `const` do schema, e o §1.2 continua voltando à gerente; mais o negativo `o exemplo da §1.5 devolvendo o relatório à própria gerente` |
| B2 | os exemplos normativos das §1.1 e §1.2 não validariam contra o schema | **não se confirma**: a §1.1 já traz `artifact_type` e o bloco `causal` completo, e a §1.2 já traz `artifact_type` e `verification_mode` em cada gate | os quatro exemplos são extraídos do arquivo e validados; três mutações provam que o bloco morde, inclusive **a redação antiga da §1.1 reconstruída**, que é rejeitada |
| B3 | a prosa da §1.1 condicionaria a emissão a `existence` dentro de `write_target` | **não se confirma**: a §1.1 já diz, com todas as letras, que `existence` é campo de `destination` e que `write_target` não o tem | `B3: existence é campo de destination` confere a prosa e o schema nos dois sentidos, e o negativo `tarefa com existence pendurada no write_target` prova que o schema rejeita o campo |

Conferir e **não** editar foi decisão deliberada: mexer no que já está correto para "fechar o item"
produziria mudança sem defeito, e o guia trata contagem que muda sem mudança de contrato como
regressão.

## O que ainda não foi provado

Declarado como `SKIP`, com motivo — prova executada > checklist, e sucesso simulado é violação (RI-04):

1. **Forward comportamental.** Os **16 prompts** de `evals.json` **não** foram executados contra uma
   instância nova e independente. Nenhuma resposta foi produzida nem conferida. Não existe evidência de
   que a skill **aciona** pelos gatilhos declarados nem de que **adere** ao contrato sob pressão — só de
   que os artefatos são estruturalmente válidos e a aritmética fecha. **Nenhum `FORWARD-TEST.md` foi
   escrito**, e escrever um com respostas não produzidas seria fabricar resultado.
2. **Baseline do pacote legado.** O `orquestrador-registros` não foi avaliado contra os mesmos
   cenários. Que esta migração **melhora o comportamento** permanece não medido; o legado tem evals
   próprios, que medem outro gatilho e outra saída, e por isso não foram promovidos.
3. **Acionamento por `description`.** Não há prova de que a `description` do frontmatter faz a skill ser
   escolhida em runtime, nem de que as quatro subskills são descobertas por enumeração de `agentes/`.
   Isso só se mede executando, e não foi executado.
4. **Existência do time em runtime (R6).** O validador confere a **aritmética** e a **estrutura**, nunca
   a **execução**: um `REGISTRY_LEDGER` internamente coerente é reproduzível mesmo sem nenhuma
   `RECORD_TASK` emitida. A condição de `COMPLETED` exigir registro de emissão **encarece** a
   fabricação; não a impede.
5. **`test_summary` fabricado.** A regra "sempre `0/0/0`" é **contratual**, não estrutural: o
   `testSummary` do schema do Diretor aceitaria `pass: 14` sem reclamar. O validador prova que a
   conversão deste pacote emite zeros; não prova que outro emissor não mentiria.
6. **Escrita concorrente (R2), cobertura da varredura de segredo (R3) e confinamento dependente do
   runtime (R7).** São limites declarados na §7 do protocolo, e nenhuma regra deste pacote os fecha.
   Nada aqui foi executado contra um sistema de arquivos real: não houve escrita, junction, hash de
   arquivo de projeto nem varredura mecânica.
7. **Parecer do `departamento-juizes`.** A qualidade destes registros não foi julgada, e este
   Departamento **não julga a si próprio**.

## Dívidas de cascata — fase 5, percorrida em 2026-07-26

As seis dívidas que a fase anterior registrou foram percorridas no passo 10 do guia:

| # | Dívida | Estado | O que ficou |
|---:|---|---|---|
| 1 | `ORGANOGRAMA.md` com três agentes e o nome `agente-documentacao-e-aprendizados` | **FECHADA** | quatro agentes com os nomes reais; parágrafo do que o Departamento decidiu, com ponteiro ao ADR-005; pasta do pacote e a de runtime na árvore canônica; `## Estado desta etapa` atualizado |
| 2 | `SKILL.md` dizendo que `evals/` e o `PLACAR.md` são "ainda não existente[s]" | **FECHADA** | a seção *Evidência de conclusão* aponta este placar e nomeia o que **de fato** falta: a prova comportamental |
| 3 | `registros/relatorios/aprendizagem/` inexistente em disco | **FECHADA como contrato** | pasta criada na raiz, com `README.md` declarando dono, consumidor e a proibição de leitura direta. **Continua sem artefato**: nenhuma rodada gravou relatório |
| 4 | menção vencida no `protocolo-de-evolucao.md` | **FECHADA** | corrigida ali e no `evals/PLACAR.md` do `departamento-evolucao-skills`; a consequência do ADR-004 foi **preservada**, por ser registro datado de decisão |
| 5 | evals comportamentais do superior | **ABERTA — ver abaixo** | não reexecutados |
| 6 | digest do manifesto irreprodutível | **FECHADA** | receita com chave e comparador fixados; valor recalculado e republicado |

### 5 · Dívida herdada e não paga: evals comportamentais do CEO

O [`ceo-maestro/evals/README.md`](../../../../evals/README.md) declara que *"os prompts comportamentais
em `evals.json` complementam os testes determinísticos e devem ser reexecutados quando o Diretor,
Negócios ou Juízes forem migrados"*.

**Não foram reexecutados nesta frente, e nada aqui os substitui.** A regra nomeia três pacotes, mas a
entrada de um Departamento operacional novo muda o que o CEO enumera em runtime e tem o mesmo efeito
prático. O determinístico do CEO passou — 32/32 —, e determinístico **não** é comportamental. `SKIP`
declarado: prova executada > checklist, e sucesso simulado é violação (RI-04).

### 6 · Digest do manifesto — resolvido por receita determinística

O legado foi **relido inteiro** e está **intacto**: 154 arquivos, 1.320.436 bytes, e os **154** hashes
publicados em [`references/origem-migracao.md`](../references/origem-migracao.md) batem **um a um** —
nenhum arquivo a mais, nenhum a menos, nenhum hash divergente.

O que não fechava era só o digest do manifesto: a receita mandava `Sort-Object` sobre a **linha
inteira** já formatada, que começa pelo hash, enquanto a prosa dizia "ordenadas por caminho" — duas
ordenações no mesmo parágrafo, a segunda sob comparador insensível a caixa e dependente de cultura.
Doze variantes foram testadas e **nenhuma** reproduziu `7a6809ac…`.

**Desfecho:** a receita passou a fixar **chave** (o caminho relativo) e **comparador** (ordinal, byte a
byte), além de separador, terminador de linha e codificação; e o valor foi **recalculado** —
`2ddcc7f987bf539c17d44b75733770bd97ef1bffeef1d82a694de10c8f385df3` —, executado em **PowerShell e em
Python**, com resultado idêntico nas duas implementações. O valor antigo foi **retirado**, com a razão
registrada no lugar: número que ninguém consegue conferir não é evidência.

## Nota de regressão — o validador do Diretor foi de 48 para 49

Registro da atribuição, para que a leitura seguinte não confunda deriva com regressão.

A materialização deste pacote fechou com a cadeia em **429/429** — `_compartilhado` 55, Registros 169,
Auditoria 64, Juízes 61, Diretor **48**, CEO 32. Na reexecução do passo 10 o validador do Diretor
devolveu **49/49** e a cadeia, **430/430**, sem que nenhum arquivo do Diretor tivesse sido tocado por
esta frente.

**Causa identificada, e não é regressão daqui:** o caso extra é
`DEPARTMENT_RETURN de Conteúdo e Marketing`, acrescentado ao validador do Diretor pela frente do
`departamento-conteudo-marketing`, materializada em paralelo. Contagem que muda **sem** mudança de
contrato é regressão; aqui houve mudança de contrato — um Departamento a mais no `enum` do superior.
Os **169** deste pacote e as contagens de Auditoria (64), Juízes (61), CEO (32) e motor (55)
**não mudaram** entre as duas execuções.
