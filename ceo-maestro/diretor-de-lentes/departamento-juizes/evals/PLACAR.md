# Placar de migração — Departamento de Juízes

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **62/62 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. A cadeia canônica hoje soma **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

Data: 2026-07-26
Versão avaliada: 1.0.0
Escopo: migração de `SKILL - Nova formula/maestro/comite-de-lentes/lente-juizes` para
`Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/departamento-juizes`

## Resultado

| Verificação | Resultado | Executado? |
|---|---:|---|
| Validador determinístico do Departamento | 62/62 PASS | **sim** |
| Regressão do validador do `diretor-de-lentes` | 49/49 PASS | **sim** |
| Regressão do validador do `ceo-maestro` | 32/32 PASS | **sim** |
| Total mecânico Departamento + Diretor + CEO | **142/142 PASS** | **sim** |
| Forward comportamental (16 prompts de `evals.json`) | **15/16 casos · 60/60 assertions · 0 contorno** | **sim** — [FORWARD-TEST.md](FORWARD-TEST.md) |
| Acionamento por roteamento cego (2 × 16) | **13/16 unânime** | **sim** — idem |
| Baseline comportamental do pacote legado | — | **NÃO — pendente** |
| Auditoria independente do contrato | — | **NÃO — bloqueada** |

Comando executado, a partir da raiz do pacote:

```bash
python evals/validate_workflow.py
```

## O que o validador prova

O validador **não** confere apenas a presença de strings. Cada bloco abaixo foi executado contra
artefatos montados em memória e contra os arquivos reais do pacote.

**Pacote e vínculos (7 casos).** Arquivos obrigatórios da gerente e dos três agentes; `agentes/`
contendo exatamente os três nomes canônicos, cada um com `SKILL.md`, contrato e `openai.yaml`;
frontmatter com apenas `name`/`description`, nome igual ao da pasta, descrição ≤ 1024 caracteres e
`SKILL.md` ≤ 500 linhas; `short_description` entre 25 e 64 caracteres; fonte normativa única citada
na gerente e em cada agente, no caminho relativo correto de cada nível; **todos** os links
markdown internos do pacote resolvendo em arquivo existente; `$ref` do schema resolvendo; e o
`enum` de `judgeId` batendo com as pastas reais de `agentes/`.

**Autoridades herdadas (1 caso, 7 asserções).** Lê os schemas do Diretor e do CEO e confirma que
eles continuam atribuindo aos Juízes o `JUDGE_REPORT`, o `DEPARTMENT_JUDGE_REPORT` e a verificação
independente; que o pedido de julgamento é autoria do Diretor e retorna a ele; e que só Jeremias
autoriza exceção. Se um desses contratos mudar do outro lado, este caso quebra aqui.

**Artefatos internos aceitos (8 casos).** `CRITERIA_MATRIX`, duas `JUDGE_ASSIGNMENT` de óticas
diferentes, `JUDGE_OPINION`, `JUDGE_CAPABILITY_GAP`, `PANEL_RECORD`, `PANEL_HANDOFF` e
`INDEPENDENT_VERIFICATION`.

**Casos negativos — cegueira e trava (4).** Ótica trocada para o agente; retorno fora da gerente;
`forbidden_context` sem a proibição explícita de autoria; juiz de fora de `agentes/`.

**Casos negativos — rubrica e escala (7).** Nota fracionária `9,5`; nota `11`; `n/a` sem motivo;
`n/a` com motivo verificável (aceito); parecer `BLOCKED` sem abstenção; parecer `BLOCKED` com
abstenção (aceito); parecer `COMPLETED` sem nenhuma nota.

**Casos negativos — consolidação e veredito (9).** `VALIDATED` com menor nota `9`; a mesma rodada
como `REPROVED` (aceita); reprovação sem crítica e sem mudança exigida; `VALIDATED` com lacuna
aberta; `VALIDATED` com critério sem dona; `VALIDATED` sem registro de emissão das atribuições
(condição de R6); `pending` sem R6 nomeado; `VALIDATED` com falha crítica; retorno endereçado fora
do Diretor.

**Casos negativos — modo DISPUTA (5).** Consenso com `leadership_reason` preenchido; decisão de
liderança com motivo (aceita); decisão de liderança sem motivo; `COMPLETED` com lacuna aberta;
`COMPLETED` com menos de dois pareceres válidos.

**Verificação de limitação (2).** Impossibilidade atestada sem tentativa executada é rejeitada;
`NOT_VERIFIED` com conferência parcial é aceito.

**Fronteira com os consumidores (6).** O `PANEL_RECORD` interno é convertido mecanicamente em
`DEPARTMENT_JUDGE_REPORT` e em `JUDGE_REPORT`, e cada um é validado **contra o schema do
consumidor** — não contra o próprio. Os dois consumidores rejeitam `VALIDATED` com `9,49`; o
Diretor rejeita parecer com produtor forjado por outro Departamento; aceita reprovação com crítica
e mudança; e rejeita reprovação muda. É o que prova que o Departamento produz o envelope que o
resto da estrutura de fato consome.

**Aritmética da consolidação (12).** Recalculada em código, sem consultar o campo declarado:
critério com dois avaliadores vale a **menor** nota; `minimum_score` é o mínimo do `scorecard`;
média `9,0` sobre `10/10/6/10` não substitui o mínimo `6`; `n/a` declarado não entra no mínimo;
`10` em tudo valida; `9` em um único critério reprova; e critério sem dona, ótica ausente, falha
crítica, pendência bloqueante ou ausência de registro de emissão reprovam **mesmo com 10 em todos
os critérios**.

## O que ainda não foi provado

Declarado como `SKIP` com motivo, conforme a regra da casa — prova executada > checklist, e
sucesso simulado é violação:

1. **Forward comportamental — EXECUTADO em 2026-07-26.** 18 instâncias independentes,
   [FORWARD-TEST.md](FORWARD-TEST.md): **15/16 casos, 60/60 assertions, zero contorno**, e
   acionamento **13/16 unânime** em roteamento cego. Nenhum defeito sistêmico. Dois defeitos
   localizados ficaram **abertos**: (a) o caso 1 do `evals.json` é mal especificado — pede trabalho
   de migração, que este Departamento recusa por contrato, então o catálogo tem 15 casos válidos e
   não 16; (b) a description do `diretor-de-lentes` reivindica "pular gerente", colidindo com a
   fronteira dos Juízes nos casos 7 e 8. **Não medido:** disparo orgânico — o pacote não está
   instalado como skill de runtime, e a aderência foi medida sob carga.
2. **Baseline do pacote legado.** A `lente-juizes` não foi avaliada contra os mesmos cenários. Sem
   esse baseline, a afirmação "a migração melhora o comportamento" permanece **não medida** — o que
   está provado é apenas que o legado não produz os envelopes que o Diretor e o CEO exigem, o que é
   verificável por leitura dos schemas.
3. **Auditoria independente.** O `departamento-auditoria-responsabilidades` foi migrado em
   2026-07-26 e já existe no caminho canônico, então o gate deixou de estar bloqueado por
   **ausência de capacidade**. Mas a auditoria deste pacote **não foi executada**: nenhuma missão de
   auditoria correu sobre os Juízes. Continua valendo que ela não pode ser substituída por
   auto-avaliação deste pacote, que não julga a si próprio.
4. **Existência do painel em runtime (R6).** O validador confere a **aritmética** e a **estrutura**,
   nunca a **execução**: um `PANEL_RECORD` internamente coerente é reproduzível mesmo que nenhuma
   `JUDGE_ASSIGNMENT` tenha sido emitida de verdade. A condição de `VALIDATED` exigir registro de
   emissão encarece a fabricação; não a impede. Limite declarado, não fechado.
5. **Reexecução dos prompts comportamentais do CEO.** O `ceo-maestro/evals/README.md` declara que os
   casos de `ceo-maestro/evals/evals.json` **devem ser reexecutados** quando o Diretor, Negócios ou
   os Juízes forem migrados. Os Juízes acabaram de ser migrados e essa reexecução **não** ocorreu.
   A regressão determinística do CEO rodou (32/32) e cobre os contratos; os prompts, não.

## Estado da migração

O pacote está **completo e mecanicamente válido**, e **não está declarado pronto**: faltam as
provas comportamentais dos itens 1 e 2 e o gate da Auditoria do item 3. Até lá, o
`departamento-juizes` existe no caminho canônico, o `diretor-de-lentes` deixa de falhar fechado por
ausência de Juízes, e o pacote legado permanece intacto como rollback manual — nunca como fallback
automático.
