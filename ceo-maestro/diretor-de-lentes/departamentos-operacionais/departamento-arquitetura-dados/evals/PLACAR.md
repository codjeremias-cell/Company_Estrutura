# Placar — Departamento de Arquitetura de Dados

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **114/114 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. A cadeia canônica hoje soma **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

Data: 2026-07-26
Versão avaliada: 1.0.0
Escopo: **skill nova** (não é migração — não existe `lente-arquiteto-dados` no legado), fundamentada
na lente canônica `arquiteto-dados`, nas Regras de Ouro e nas lições registradas em `Aprendizagem/`

## Resultado

| Verificação | Resultado | Executado? |
|---|---:|---|
| Validador determinístico do Departamento | 114/114 PASS | **sim** |
| Regressão do `departamento-arquitetura-software` | 70/70 PASS | **sim** |
| Regressão do `departamento-auditoria-responsabilidades` | 64/64 PASS | **sim** |
| Regressão do `departamento-juizes` | 61/61 PASS | **sim** |
| Regressão do `diretor-de-lentes` | 49/49 PASS | **sim** |
| Regressão do `ceo-maestro` | 32/32 PASS | **sim** |
| Regressão do `departamento-evolucao-skills` | 56/56 PASS | **sim** |
| Motor compartilhado de schema | 55/55 PASS | **sim** |
| Forward comportamental (16 prompts de `evals.json`) | **16/16 casos · 49/49 asserções · 0 contorno** | **sim** — [FORWARD-TEST.md](FORWARD-TEST.md) |
| Baseline da lente canônica nos mesmos cenários | — | **NÃO — pendente** |
| Auditoria independente | — | **NÃO — pendente** |
| Parecer dos Juízes | — | **NÃO — pendente** |

```bash
python evals/validate_workflow.py
```

## O que o validador prova

**Pacote e vínculos (8 casos).** Arquivos obrigatórios da gerente e as cinco referências; `agentes/`
com exatamente os **seis** nomes canônicos, cada um completo; frontmatter só com `name`/`description`,
description entre aspas e ≤ 1024 caracteres, `SKILL.md` ≤ 500 linhas; `short_description` de 25–64;
**posição na hierarquia conferida em runtime** — se alguém mover este Departamento para fora de
`departamentos-operacionais/`, o caso quebra; fonte normativa no caminho relativo **de cada nível**
(`../../../../` na gerente, `../../../../../../` nos agentes); todos os links markdown internos
resolvendo; e o `enum` de `workerId` batendo com as pastas reais.

**Travas mecânicas do ADR-008 (6 casos).** O validador percorre o schema inteiro e falha se
encontrar, em qualquer profundidade, nome de propriedade de **nota** (`score`, `nota`,
`minimum_score`, `verdict`, `rubrica`, `ranking`, `winner`…), de **código** (`codigo`, `patch`,
`query`, `sql`, `ddl`, `dao`, `repositorio`…) ou de **arquitetura macro** (`modulo`, `c4`,
`topologia`, `bounded_context`, `sincrono`…). Mais três travas por `const`: `producer` fixo neste
Departamento, `measured` fixo em `false` — R2, projeção nunca vira medição — e `immutability_ack`
fixo em `true`, que é a lição L1 virada regra de schema.

**Artefatos aceitos (16).** `DATA_PLAN` com e sem piso atendido, as seis `DATA_TASK` e os seis
`DATA_RETURN` (um por capacidade), `DATA_CAPABILITY_GAP` e `DATA_LEDGER` com o gate fechado.

**Casos negativos — plano (5).** Piso declarado atendido com duas perguntas; piso sem volumetria;
piso não atendido mas com onda emitida; produtor forjado por outro Departamento; plano devolvido
para fora do Departamento.

**Casos negativos — tarefa (6).** Capacidade trocada para o agente; modelagem emitida na onda da
persistência; `forbidden_context` sem a proibição de produzir código; `forbidden_context` vazio;
tarefa endereçada a agente de outro Departamento; retorno endereçado ao Diretor.

**Casos negativos — retorno (19).** Modelo concluído sem grão; grão sem significado; evolução sem
plano; escala sem justificativa; persistência sem evidência; perguntas com menos de três;
contratos sem contrato; `BLOCKED` sem e com motivo; **índice declarado como medido** (R2); índice
"por garantia"; cache sem e com invalidação; **fase destrutiva fora do `CONTRACT`**; plano sem
reconhecer a imutabilidade; fase sem rollback; **PII sem retenção** e PII com retenção e RLS;
dependência ao Desenvolvimento sem restrição anexada.

**Casos negativos — livro-razão e gate de saída (16).** `ENTREGUE` com cada um dos três itens
ausente; `closure` incompleto; sem grão; sem acesso justificado; sem plano de migração; **sem
registro de emissão** (R6); com lacuna aberta; com pendência pendurada; conflito arquitetural sem
escalação, contornado, e escalado corretamente; piso não atendido com entrega normal; livro-razão
declarando teste executado; entrega `INCOMPLETA` legítima; retorno fora do Diretor.

**Fronteira com o consumidor (7).** O `DATA_LEDGER` interno é convertido mecanicamente em
`DEPARTMENT_RETURN` e validado **contra o schema do `diretor-de-lentes`** — não contra o próprio. O
Diretor aceita o envelope convertido e rejeita autor divergente do produtor e retorno endereçado ao
CEO. Mais três confirmações do outro lado: o Diretor reconhece este Departamento em
`operationalDepartment` e em `knownCapability`, e o **`delegationTarget` da Arquitetura de Software
aponta para cá** — a dependência que ela emite agora tem destinatário real.

**Gate recalculado em código (21).** Sem consultar o campo `entrega` declarado: o gate fecha com os
três itens atendidos e **não fecha** com qualquer um ausente; dois atendidos não compensam o
terceiro; **dez acessos justificados não substituem o grão**; não fecha sem registro de emissão, com
lacuna aberta, com conflito arquitetural ou com o piso não atendido. Mais a aritmética das partes:
grão sem significado não conta como declarado; evolução sem rollback em uma fase, com destrutivo
fora do `CONTRACT`, sem versão livre ou com uma fase só não é reversível; e acesso "por garantia" ou
declarado como medido não é justificado.

**Coerência do catálogo (5).** O `evals.json` tem ao menos 12 casos, todos declarando `acionou` e
`aderiu`, com ao menos um caso de recusa por fronteira; e os digests das regras e do schema são
verificáveis.

## Defeitos encontrados e corrigidos durante a construção

Registrados porque o que impediu cada um de sair foi o **teste**, não o cuidado:

1. **O schema divergiu do padrão da casa.** A primeira versão definia um `departmentReturn` próprio,
   com forma inventada, colidindo em nome com o `DEPARTMENT_RETURN` real do Diretor — que tem 15
   campos completamente diferentes. Reescrito: aqui só existem artefatos **internos**, e a conversão
   para o envelope do Diretor acontece no validador, provada contra o schema do consumidor.
2. **A armadilha de profundidade, pela terceira vez.** Os links para o ADR-006 saíram com `../` em
   vez de `../../`. É o mesmo erro do ADR-003 e do ADR-006, agora repetido mesmo estando documentado
   como armadilha nº 1 do `GUIA-DE-EXPANSAO-E-MIGRACAO.md`. **O aviso escrito não preveniu; o
   `validate_links` pegou.** É evidência de que a defesa que funciona é mecânica.
3. **Contradição interna no schema.** `waves` exigia `minItems: 1` na base enquanto o ramo de piso
   não atendido exigia `maxItems: 0` — nenhum plano com piso ausente podia ser válido. O `minItems`
   foi movido para o ramo do piso atendido.
4. **`description` sem aspas** nos sete `SKILL.md`, contra a convenção que o motor compartilhado
   exige.

## O que ainda não foi provado

`SKIP` declarado com motivo — prova executada > checklist, e sucesso simulado é violação (RI-04):

1. **Forward comportamental — EXECUTADO em 2026-07-26.** 16 instâncias independentes,
   [FORWARD-TEST.md](FORWARD-TEST.md): **16/16 casos, 49/49 asserções, zero contorno**. Encontrou
   **dois defeitos**: a L5 existia só em prosa no schema (corrigido — `IN_TRANSACTION` agora exige
   `anti_dual_write: OUTBOX`, com três casos negativos novos) e uma citação de RO-W8 fabricada numa
   resposta (registrada, não corrigível no pacote). **Não medido:** disparo orgânico e acionamento
   por roteamento cego.
2. **Baseline da lente canônica.** A `arquiteto-dados` não foi avaliada contra os mesmos cenários.
   Que este Departamento **melhora o comportamento** permanece não medido; o que se sabe por leitura
   é que a canônica não produz os envelopes que o Diretor consome.
3. **Auditoria independente e parecer dos Juízes.** Ambos pendentes. Este Departamento não se audita
   nem se pontua.
4. **R6 — existência das ondas.** Um `DATA_LEDGER` internamente coerente é reproduzível sem que
   nenhuma `DATA_TASK` tenha sido emitida de verdade. Exigir o registro de emissão encarece a
   fabricação; não a impede.
5. **R1/R2 — o que este Departamento entrega é projeção.** Volumetria é premissa de quem pede e
   ganho de índice é lido em plano, não medido. O schema trava `measured` em `false` justamente para
   que ninguém possa declarar o contrário; isso impede a **afirmação** falsa, não substitui a
   medição.
6. **R7 — as lições são do stack conhecido.** L1–L7 vêm de Java/Spring, Supabase e Tauri. Em stack
   fora desses, valem como princípio e a transposição não foi verificada.

## Efeito sobre a estrutura

A dependência que o `departamento-arquitetura-software` emite com `delegationTarget:
departamento-arquitetura-dados` passa a ter **destinatário real** — antes apontava para o vazio. E a
fronteira entre as duas lentes irmãs fica coberta dos dois lados: o ADR-006 declara o que não é da
Arquitetura, e o [ADR-008](../references/adr-008-dados-skill-nova-e-seis-agentes.md) declara o
recíproco, com a `architectural_constraint` reconhecida como vinculante.

Continuam faltando os Departamentos operacionais restantes. Enquanto não existirem, as dependências
emitidas daqui para `departamento-desenvolvimento`, `departamento-seguranca` e
`departamento-qa-usabilidade` permanecem sem destinatário no caminho canônico.
