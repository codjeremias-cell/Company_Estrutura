# Protocolo do Departamento de Arquitetura de Dados

Como a demanda entra, atravessa os seis agentes e volta ao Diretor. Fonte normativa única:
[`REGRAS-DE-OURO.md`](../../../../../regras-de-ouro/REGRAS-DE-OURO.md).

## Envelopes

| Envelope | De → Para | Papel |
|---|---|---|
| `DEPARTMENT_MISSION` | Diretor → gerente | a demanda; pode trazer `architectural_constraint` |
| `DATA_PLAN` | gerente (interno) | ondas, agentes acionados e o que cada um responde |
| `DATA_TASK` | gerente → agente | uma capacidade, um agente, com `forbidden_context` |
| `DATA_RETURN` | agente → gerente | a resposta daquela ótica, com evidência |
| `DATA_LEDGER` | gerente (interno) | consolidação e verificação dos três itens do gate de saída |
| `DEPARTMENT_RETURN` | gerente → Diretor | o que o Diretor consome; `pass`/`fail` sempre `0` |
| `DATA_CAPABILITY_GAP` | gerente → Diretor | falha fechada: piso não atendido, ou conflito com a Arquitetura |

O `causalHeader.producer` é travado por `const` em `departamento-arquitetura-dados`. Retorno com
produtor de outro Departamento é rejeitado pelo schema — não por convenção.

O `DEPARTMENT_RETURN` **não é definido aqui**: ele pertence ao schema do `diretor-de-lentes`, e é
lá que a estrutura dele é validada. O que este Departamento produz é o `DATA_LEDGER`, convertido
mecanicamente no envelope que o Diretor consome — é o mesmo padrão dos Juízes e da Auditoria, e é o
que impede este pacote de declarar um contrato de fronteira que o consumidor não reconhece.

## Ondas

**Onda 0 — admissão.** A gerente confere o **piso**: ≥ 3 perguntas do negócio e volumetria em ordem
de grandeza ([gates](gates-e-licoes-de-producao.md)). Não atendido → `DATA_CAPABILITY_GAP` apontando
`requisitos-descoberta`, e a frente **não abre**. Confere também se a missão pertence a este
Departamento ([fronteiras](fronteiras-do-departamento.md)); se for de vizinho, devolve sem produzir.

**Onda 1 — perguntas e volumetria.** `agente-perguntas-e-volumetria` transforma o piso em insumo
utilizável: cada pergunta com frequência, latência aceitável e volume; e o veredito **OLTP ou OLAP**
(ou os dois, com fronteira declarada). Nada segue sem isso.

**Onda 2 — persistência.** `agente-escolha-de-persistencia` decide o motor **por evidência da
onda 1**. Relacional é o default; cada desvio precisa de justificativa ligada a um padrão de acesso
concreto. Declara o engine único dev = prod (L2) e, se houver poliglota, onde fica a fronteira e
quem reconcilia.

**Onda 3 — modelo e grão.** `agente-modelo-e-grao` produz entidades, chaves, cardinalidades,
normalização e **o grão de cada tabela/coleção** — o que uma linha representa. Declara a estratégia
de histórico (SCD, temporal, soft delete) e a fronteira transacional onde a escrita for multi-passo
(L3). **Agente distinto do da onda 2** — ver ADR-008, decisão 3.

**Onda 4 — em paralelo, sobre o modelo pronto.**

- `agente-evolucao-e-migracao`: plano expand/contract com rollback por fase e a versão livre
  declarada; migração aplicada é imutável (L1). **Agente distinto do da onda 3.**
- `agente-escala-e-acesso`: índices, partição, replicação e cache, **cada um amarrado a um padrão de
  acesso da onda 1**. Índice sem acesso que o justifique não entra.
- `agente-contratos-e-integridade`: contrato de dados com o consumidor, constraints com o fluxo de
  erro correspondente (L4), CDC/outbox contra dual-write, ponto de disparo relativo ao commit (L5),
  classificação de PII com retenção, e política de RLS quando a stack a exigir (L7).

**Onda 5 — consolidação.** A gerente monta o `DATA_LEDGER`, verifica o **gate de saída** (grão ✓ ·
expand/contract com rollback ✓ · índice/partição justificado ✓), reúne as `delegated_dependency`
para Desenvolvimento e Segurança com as restrições anexadas (L6), e emite o `DEPARTMENT_RETURN`.

## Gates locais

| # | Gate | Falha |
|---|---|---|
| G1 | piso de entrada atendido | `DATA_CAPABILITY_GAP` para `requisitos-descoberta` |
| G2 | missão pertence a este Departamento | devolve ao Diretor sem produzir |
| G3 | escolha de motor ancorada em padrão de acesso da onda 1 | retorno rejeitado |
| G4 | grão declarado para **cada** tabela/coleção | entrega INCOMPLETA |
| G5 | plano de evolução com rollback por fase e versão livre | entrega INCOMPLETA |
| G6 | **todo** índice/partição amarrado a um acesso nomeado | entrega INCOMPLETA |
| G7 | `architectural_constraint` respeitada ou conflito escalado | retorno rejeitado |
| G8 | separação de agentes das ondas 2/3 e 3/4 mantida | plano rejeitado |

Os gates G4–G6 são o fechamento RI-04. Nenhum deles admite compensação: dez índices bem
justificados não substituem um grão não declarado.

## Riscos residuais declarados

- **R1 — volumetria é estimativa.** A ordem de grandeza vem de quem pede, e erro de uma ordem muda a
  decisão de partição. Declarada como premissa, não como fato medido.
- **R2 — plano de query não é execução.** Justificar índice lendo plano é projeção; o ganho real só
  aparece com o volume real. O retorno diz "esperado", nunca "medido".
- **R3 — grão declarado não é grão respeitado.** O schema exige a frase; nada aqui impede que a
  implementação a viole. Quem fecha isso é teste do `departamento-desenvolvimento`.
- **R4 — expand/contract exige disciplina de release** que este Departamento não controla. O plano é
  correto; a execução em fases fora de ordem quebra igual.
- **R5 — a fronteira com Arquitetura tem zona cinzenta declarada** (contrato de dados, CDC). Foi
  dividida em duas metades; casos novos vão precisar de decisão do Diretor.
- **R6 — existência das ondas.** Um `DATA_LEDGER` internamente coerente é reproduzível sem que
  nenhuma `DATA_TASK` tenha sido emitida. Exigir o registro de emissão encarece a fabricação; não a
  impede.
- **R7 — lições são do stack conhecido.** L1–L7 vêm de Java/Spring, Supabase e Tauri. Em stack fora
  desses, valem como princípio, e o retorno deve dizer que a transposição não foi verificada.
