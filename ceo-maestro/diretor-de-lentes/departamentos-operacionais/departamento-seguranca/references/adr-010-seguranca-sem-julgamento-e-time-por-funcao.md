# ADR-010 — Segurança migra sem julgar, com o time cortado por função verificável

- **Data:** 2026-07-26
- **Status:** **ACEITO — confirmado por Jeremias em 2026-07-26.** O conjunto de agentes é decisão
  dele, e ele confirmou os **oito** da decisão 4, nos nomes exatos ali fixados. A partir desta
  confirmação, o passo 8 do guia está liberado e as fases seguintes consomem este conjunto como
  fechado; mudá-lo exige novo ADR.
- **Decisores:** Jeremias (confirmado em 2026-07-26)
- **Série global:** sucede o
  [ADR-009 de Design](../../departamento-design-ux-ui/references/adr-009-design-sem-painel-cego-e-com-time-fixo.md).
  Confirmado por varredura de todos os `adr-*.md` da estrutura antes de cunhar o número: existem três
  `adr-001` históricos (CEO, Diretor e Negócios, anteriores à convenção em camadas) e a série contínua
  002 → 009. **009 é o maior vigente; este é o 010.**
- **Contexto normativo:**
  [ADR-001 hierarquia](../../../../references/adr-001-hierarquia-executiva.md) ·
  [ADR-002 Juízes](../../../departamento-juizes/references/adr-002-nota-absoluta-e-modo-duplo.md) ·
  [ADR-003 Auditoria](../../departamento-auditoria-responsabilidades/references/adr-003-conformidade-sem-nota.md) ·
  [ADR-005 Registros](../../departamento-registros/references/adr-005-quatro-agentes-e-relatorios-de-registros.md) ·
  [ADR-006 Arquitetura](../../departamento-arquitetura-software/references/adr-006-arquitetura-sem-julgamento-e-com-seis-agentes.md) ·
  [ADR-007 time elástico](../../departamento-conteudo-marketing/references/adr-007-departamento-e-time-elastico.md) ·
  [ADR-008 Dados](../../departamento-arquitetura-dados/references/adr-008-dados-skill-nova-e-seis-agentes.md) ·
  [ADR-009 Design](../../departamento-design-ux-ui/references/adr-009-design-sem-painel-cego-e-com-time-fixo.md)
- **Proveniência do recorte:** [origem-migracao.md](origem-migracao.md)

## Contexto

A fonte é a `lente-especialista-seguranca`: 154 arquivos, `SKILL.md` de 290 linhas, três JSON Schemas
próprios, um registro canônico de funções versionado (`ROLE_REGISTRY_VERSION: 1.1`), uma rubrica
ponderada de doze dimensões e nove rodadas de transcripts executados. Como a `lente-designer`, não é
esboço — é skill que já rodou. E, como ela, resolve à sua maneira coisas que a nova estrutura resolve
de outra.

Três fatos moldam esta decisão.

**Primeiro: a lente legada julga.** Ela opera em modo duplo `GERENCIAR | JULGAR`, com escala 0–10,
pesos somando 10,0, corte 9,5, piso de 9,0 por dimensão crítica, vetos e `REPORT_VERDICT`. Na nova
estrutura, nota e corte pertencem ao `departamento-juizes` desde o
[ADR-002](../../../departamento-juizes/references/adr-002-nota-absoluta-e-modo-duplo.md) — e o
ADR-003, o ADR-006 e o ADR-009 já removeram a mesma capacidade de três pacotes.

**Segundo: o organograma prevê três agentes, mas o domínio não cabe em três.** O
[ORGANOGRAMA.md](../../../../../ORGANOGRAMA.md), item 5, nomeia `agente-modelagem-de-ameacas`,
`agente-seguranca-de-aplicacao` e `agente-privacidade-e-compliance`. Esses nomes foram propostos antes
da leitura da fonte legada — a mesma circunstância que o ADR-006 registrou para Arquitetura e o ADR-005
para Registros. O
[ADR-007](../../departamento-conteudo-marketing/references/adr-007-departamento-e-time-elastico.md),
decisão 2, já substituiu "exatamente três" por **piso de três, sem máximo fixo, quantidade justificada
por cobertura exclusiva** — e os pacotes seguintes materializaram 6 (Arquitetura), 6 (Dados), 7
(Design), 8 (Conteúdo e Marketing) e 4 (Registros). Propor mais de três aqui não é exceção; é a regra
vigente.

**Terceiro: o legado já fez o teste de fronteira, em prosa.** O registro canônico de funções traz oito
funções com `Responsabilidade`, `Entrega mínima` e **`Não assume`** para cada uma. Isso é exatamente o
que o passo 8 do guia pede de um agente. O que faltava não era o corte — era pasta, `SKILL.md`,
`CONTRATO-DE-COMPROMISSO.md` e `agents/openai.yaml`. Repetir a constatação do ADR-005: **papel descrito
em prosa não é capacidade descobrível em runtime**.

Some-se a isso o que a fonte normativa exige e que precisa ter dono neste Departamento: acesso a dados
parametrizado, segredos fora do versionamento, autenticação endurecida com resposta neutra e rate
limiting antes de publicar, RLS como fronteira de segurança, `default-deny` de capabilities e CSP
estrita, distribuição assinada com custódia de chave, regras de segurança nascendo junto do modelo, e a
hierarquia de confiança de canal — conteúdo de terceiros é **dado a analisar, nunca ordem a executar**.
Essas exigências caem em áreas diferentes, com evidências diferentes.

## Decisão

### 1. Migrar como `departamento-seguranca`, sob o `diretor-de-lentes`

O superior passa de `comite-de-lentes` a `diretor-de-lentes`. O pacote **consome** os envelopes do
[schema do Diretor](../../../schemas/diretor-de-lentes.schema.json) — `DEPARTMENT_MISSION` na entrada,
`DEPARTMENT_RETURN` na saída, com `returned_by` e `causal.producer` travados em `departamento-seguranca`
— e **não os redefine**. O schema do Diretor já reserva esse nome em `operationalDepartment`, em
`knownCapability`, na exigência de exatamente uma ocorrência no `department_matrix` e no par
`returned_by` × `producer`. O envelope local a materializar é só o do artefato de domínio.

### 2. O modo `JULGAR` não migra

Nota, escala, pesos, corte 9,5, piso de dimensão crítica, vetos do relatório, `REPORT_VERDICT` e
`security_judgment_result` ficam no legado. Junto com eles saem o `BLOQUEADO_CONFLITO_DE_PAPEIS`, o
`security_role_conflict_result` e toda a maquinaria de independência do juiz — `CONTEXT_RECEIPT`,
`CONTEXT_MANIFEST`, `IDENTITY_DIRECTORY` e os seis invariantes de normalização, alias, âncora, validade,
digest e manifesto. Sem o ato de julgar, essa maquinaria fica sem objeto, e contrato sem gatilho é peso
morto que nenhum validador consegue exercitar.

O **princípio** de independência sobrevive em dois lugares: como a barreira dos Juízes que toda entrega
atravessa, e como as separações internas da decisão 5.

### 3. As doze dimensões viram cobertura, não nota

Estados de cobertura por área, sem peso e sem número entre 0 e 10. É a terceira aplicação da mesma
conversão — ADR-006 (oito dimensões de Arquitetura) e ADR-009 (nove dimensões de Design) —, e aqui ela
tem apoio adicional na própria fonte: o `COVERAGE_MAP` do `security_management_result` já lista as onze
áreas de cobertura **sem peso**, ao lado de `not_assessed`. A rubrica era a versão pontuada de um mapa
que já existia despontuado.

Área declarada não aplicável exige justificativa ligada a ativo ou fluxo; "não se aplica" solto é
lacuna, não cobertura — regra herdada da rubrica.

### 4. Oito agentes, um por função do registro canônico do legado *(confirmada)*

> **Confirmada por Jeremias em 2026-07-26.** O conjunto abaixo é o resultado de aplicar o teste de
> fronteira do passo 8 ao domínio real; a palavra final era de Jeremias, e ele fixou estes oito
> nomes. O `enum` de identidades do
> [schema do pacote](../schemas/departamento-seguranca.schema.json) é exatamente esta coluna.

| # | Agente | Função legada | Dimensões | Recorte exclusivo — a pergunta que só ele responde |
|---:|---|---|---|---|
| 1 | `agente-modelagem-de-ameacas` | `THREATS` | 1, 2 | *O que pode ser atacado, por quem e sob qual pré-condição?* Ativos, dados, fluxos, superfície, fronteiras de confiança, STRIDE, casos de abuso e priorização. É o único que **produz o espaço de ameaças**; todos os outros verificam controles dentro dele. |
| 2 | `agente-identidade-e-acesso` | `IAM` | 3 | *Quem pode fazer o quê, sobre qual objeto, e o que acontece quando a resposta é não?* Matriz sujeito–objeto–ação, autenticação, sessão, token, privilégio, negações e RLS. |
| 3 | `agente-seguranca-de-aplicacao` | `CODE_APPSEC` | 4, 5 | *O que o código faz com entrada não confiável e com material criptográfico?* Rota e componente, OWASP/CWE/ASVS, validação, codificação de saída, algoritmos, chaves e **descoberta** de segredo exposto. |
| 4 | `agente-configuracao-e-hardening` | `CLOUD_CONFIG` | 6 | *A plataforma onde isso roda está no baseline, e o que ela faz quando algo falha?* Cloud, host, container, rede, CI/CD como ambiente, exceções e o comportamento sob erro, timeout, fallback e estado parcial. |
| 5 | `agente-cadeia-de-suprimentos` | `SUPPLY_CHAIN` | 7 | *O que executa é o que foi construído a partir do que foi revisado?* Dependências, SBOM, SCA, proveniência e atestado do builder, assinatura, custódia e rotação das chaves. |
| 6 | `agente-privacidade-e-dados-pessoais` | `DATA_LGPD` | 8 | *Este dado pessoal pode existir aqui, com que mínimo, por quanto tempo e com qual descarte?* Classificação, minimização, retenção, descarte e LGPD técnica. |
| 7 | `agente-deteccao-e-resposta` | `DETECTION_RESPONSE` | 9 | *Quando o controle falha ou a violação já ocorreu, o sistema percebe, contém e volta?* Eventos, alertas, runbooks, contenção, recuperação e o ciclo do incidente de segredo — revogação, rotação, `close_when`. |
| 8 | `agente-prova-e-reteste` | `EVIDENCE` | 11 | *A alegação tem prova admissível, e o fechamento tem reteste?* SAST, DAST, SCA, secret scanning, fuzz, pentest autorizado, reteste, matriz controle–teste–evidência, cobertura e `SKIP` declarado. É o único que decide **admissibilidade de evidência**. |

**A fronteira que cada um recusa, com o irmão dono nomeado:**

| Agente | Não assume → dono |
|---|---|
| `agente-modelagem-de-ameacas` | o **controle** de cada ameaça enumerada → o irmão dono da classe de controle; arquitetura macro → `departamento-arquitetura-software` |
| `agente-identidade-e-acesso` | validação de entrada e codificação de saída → `agente-seguranca-de-aplicacao`; **implementar** IAM → `departamento-desenvolvimento` |
| `agente-seguranca-de-aplicacao` | a matriz de permissão → `agente-identidade-e-acesso`; a resposta ao segredo achado → `agente-deteccao-e-resposta`; **corrigir o código** → `departamento-desenvolvimento` |
| `agente-configuracao-e-hardening` | o que é construído e assinado no pipeline → `agente-cadeia-de-suprimentos`; alertar e conter → `agente-deteccao-e-resposta`; **alterar o ambiente** → `departamento-desenvolvimento` |
| `agente-cadeia-de-suprimentos` | o hardening do ambiente que executa → `agente-configuracao-e-hardening`; **atualizar a dependência** → `departamento-desenvolvimento` |
| `agente-privacidade-e-dados-pessoais` | criptografia e chave → `agente-seguranca-de-aplicacao`; **parecer jurídico** → fora do domínio: vira `PENDING` com dono nomeado ao Diretor |
| `agente-deteccao-e-resposta` | descobrir o segredo exposto → `agente-seguranca-de-aplicacao`; **operar o incidente** de verdade → fora do domínio, exige capacidade e autorização próprias |
| `agente-prova-e-reteste` | produzir achado ou desenhar controle → os sete irmãos; ele **prova, não descobre** |

**As duas dimensões restantes têm dono declarado e não geram agente:**

- **dimensão 10, IA/LLM** — transversal (decisão 6);
- **dimensão 12, rastreabilidade, cobertura, risco e tratamento** — **da gerente**: é consolidação, não
  especialidade. Mesma forma do ADR-009, que deixou as dimensões 8 e 9 com a gerente de Design.

**Prova do teste de fronteira:** doze dimensões, oito donos exclusivos, uma transversal e uma da
gerente. Nenhuma dimensão com dois donos; nenhuma sem dono.

**Por que três não bastam.** Com o conjunto do organograma, `agente-seguranca-de-aplicacao` teria de
reivindicar as dimensões 3, 4, 5, 6, 7, 9 e 11 — **sete das doze** —, e o registro do legado dá a cada
uma delas `Entrega mínima` e `Não assume` diferentes. Os critérios que ficariam órfãos, nomeados:

| Critério órfão | Por que nenhum dos três nomes o reivindica sem esticar o significado |
|---|---|
| `EVIDENCE` / dim. 11 — admissibilidade de evidência e reteste | ficaria com quem produziu o achado, que é autocertificação — e o próprio legado lista "`SKIP`, silêncio ou ausência de achado apresentados como `PASS`" como evidência **rejeitada** |
| `SUPPLY_CHAIN` / dim. 7 — proveniência do builder, atestado, custódia de chave | não é "aplicação" nem "ameaça" nem "privacidade": é integridade do que se distribui |
| `CLOUD_CONFIG` / dim. 6 — baseline, IaC, CI/CD, fail-open de plataforma | "segurança de aplicação" não cobre o ambiente que a executa |
| `DETECTION_RESPONSE` / dim. 9 — o que acontece **depois** da falha | nem modelagem de ameaças nem segurança de aplicação respondem por percepção, contenção e recuperação |
| `IAM` / dim. 3 — matriz sujeito–objeto–ação | tecnicamente cabe em "aplicação", mas o legado o separa com peso próprio e entrega própria, e é a classe de achado mais frequente do domínio |

### 5. Duas separações por conflito de interesse

No mesmo espírito do ADR-006, do ADR-008 e do ADR-009:

- **quem produz o achado não certifica a prova de fechamento.** `agente-prova-e-reteste` não produz
  achado nem desenha controle na mesma frente. É a forma de domínio de *autor não é adversário de si
  mesmo* (ADR-009, decisão 6) e de *quem verifica integridade não é o autor do ato verificado*
  (ADR-005). O legado já dizia, em prosa: `EVIDENCE` "não assume executar sem capacidade/autorização ou
  declarar `PASS`", e "o juiz não integra o time produtor";
- **quem descobre o segredo exposto não declara o incidente contido.** A descoberta é do
  `agente-seguranca-de-aplicacao`; o ciclo revogação → rotação → contenção → `close_when` é do
  `agente-deteccao-e-resposta`. É o corte que o próprio legado já fazia entre `CODE_APPSEC` e
  `DETECTION_RESPONSE`, e ele impede que quem achou feche o próprio achado.

### 6. IA/LLM é transversal e obrigatório, não é agente

Prompt injection é entrada não confiável (dimensão 4); autorização de ferramenta de agente é IAM
(dimensão 3); vazamento é cripto e privacidade (dimensões 5 e 8); ação autônoma sem trilha é detecção
(dimensão 9). Um agente de IA/LLM disputaria **cada** um desses recortes com o irmão dono — que é
exatamente o defeito que o teste de fronteira existe para evitar.

A dimensão 10 vira, portanto, **critério transversal obrigatório**: cada agente a aplica dentro da
própria fronteira, e a **enumeração** dos casos de abuso de IA/LLM é do `agente-modelagem-de-ameacas`,
que já enumera todas as ameaças. Isso não cria dois donos: é o mesmo repasse ameaça → controle que vale
para qualquer outra ameaça. Mesma forma da decisão 9 do ADR-009 para adaptação nativa.

### 7. A recomendação de risco do sistema permanece — e vira gate mecânico

O enum herdado continua: `LIBERAR | LIBERAR_COM_RESSALVAS | BLOQUEAR | INDETERMINADO`, com motivo em
campo próprio. **Ele não é nota e não é o gate geral.** O par herdado
`REPORT_SELF_APPROVAL: prohibited` e `GENERAL_AUDIT_GATE: NOT_ISSUED_BY_THIS_LENS` permanece, com os
destinatários atualizados: a **nota** é do `departamento-juizes`, a **conformidade** é do
`departamento-auditoria-responsabilidades`, e recomendação `LIBERAR` **nunca** significa entrega
validada.

Os cinco gatilhos que o legado descrevia em prosa viram **condição de schema** — presente qualquer um,
`BLOQUEAR` é obrigatório e a saída positiva é recusada:

1. achado crítico confirmado e aberto;
2. alto explorável sem controle compensatório provado **e** sem risco formalmente aceito por autoridade
   competente;
3. fail-open de autenticação, autorização ou fronteira de confiança;
4. segredo válido exposto;
5. controle obrigatório material ausente.

É a mesma conversão que o ADR-008 fez com o fechamento de três itens de Dados e o ADR-009 com o
`DESIGN_GATE`: gate que depende de disciplina é o primeiro a cair.

### 8. Atividade ativa continua fail-closed sob autorização estruturada

DAST, fuzzing e pentest só ocorrem com alvo, ambiente, janela, dados, contas, ações permitidas,
proibidas, limites de taxa, condições de parada e contato de emergência — todos simultaneamente
válidos. Ausência ou divergência bloqueia **somente a atividade afetada**; análise estática segura
prossegue. O que não puder ser executado vira **`SKIP` declarado com motivo**, nunca `PASS` — e falta
de capacidade vira lacuna escalada ao Diretor como `DIRECTOR_CAPABILITY_GAP` com
`safe_state: "D_BLOCKED"`, nunca uso silencioso do pacote legado.

### 9. O desvio do organograma é dívida da cascata, registrada aqui

| [ORGANOGRAMA.md](../../../../../ORGANOGRAMA.md), item 5 | Proposta | Natureza do desvio |
|---|---|---|
| `agente-modelagem-de-ameacas` | `agente-modelagem-de-ameacas` | **mantido**, nome e escopo |
| `agente-seguranca-de-aplicacao` | `agente-seguranca-de-aplicacao` | **mantido no nome, reduzido no escopo**: perde IAM, configuração, cadeia de suprimentos, detecção e prova para irmãos próprios |
| `agente-privacidade-e-compliance` | `agente-privacidade-e-dados-pessoais` | **renomeado** — ver alternativas |
| — | `agente-identidade-e-acesso`, `agente-configuracao-e-hardening`, `agente-cadeia-de-suprimentos`, `agente-deteccao-e-resposta`, `agente-prova-e-reteste` | **cinco acrescentados** |

Atualizar o item 5, a árvore canônica, a linha do mapeamento de nomes e o estado da migração no
`ORGANOGRAMA.md` é trabalho da **fase de cascata** (passo 10 do guia), fora do escopo desta etapa.
Enquanto não for feito, o organograma está desatualizado em relação a esta decisão — e, com a
confirmação de Jeremias, **a fonte vigente do conjunto é este ADR**; o organograma é a fonte
desatualizada, a ser corrigida na cascata.

## Consequências

- o `departamento-juizes` ganha mais um cliente: a nota do domínio de segurança passa a sair de lá, e a
  reprovação volta pelo Diretor como retrabalho;
- o `departamento-desenvolvimento` — ainda ausente — ganha mais um emissor de dependências: correção de
  código, atualização de dependência e alteração de ambiente saem daqui como dependência delegada, não
  como execução;
- a dependência que o `departamento-arquitetura-dados` já emite para cá
  ([ADR-008](../../departamento-arquitetura-dados/references/adr-008-dados-skill-nova-e-seis-agentes.md),
  decisão 6: *modelar ameaça e endurecer o controle é do `departamento-seguranca`*) passa a ter
  destinatário real — e o mesmo vale para a regra herdada pelo Design de acionar segurança antes do
  aceite visual em fluxo de risco;
- oito agentes é o segundo maior time operacional da estrutura, atrás só de Conteúdo e Marketing: mais
  custo de coordenação, e cada fronteira precisará provar que não gera fila;
- a maquinaria de independência do juiz sai inteira do domínio; se a estrutura voltar a precisar dela, o
  lugar é o `departamento-juizes`, não aqui;
- o legado permanece **intacto** — 154 arquivos, digest de manifesto
  `d92607a3fa32f80c44b9a9b18bfce20b16a7c8b69bc5d0756b24754fc3ad1d83` —, como rollback manual e história
  citável, nunca como fallback de runtime;
- **com a confirmação de 2026-07-26, o passo 8 está liberado**: as oito pastas de agente podem ser
  criadas na fase própria, e as fases já materializadas — protocolo, schema, `SKILL.md` e contrato —
  consomem este conjunto como fechado. O `enum` de identidades do schema e as pastas de `agentes/`
  são o **mesmo texto**; divergência entre eles é defeito a corrigir na mesma sessão.

## Alternativas consideradas

| Alternativa | Motivo do descarte |
|---|---|
| Manter os três agentes do organograma | `agente-seguranca-de-aplicacao` teria de reivindicar sete das doze dimensões, e `EVIDENCE`, `SUPPLY_CHAIN`, `CLOUD_CONFIG` e `DETECTION_RESPONSE` ficariam órfãs ou espremidas. O registro de funções do legado já dá a cada uma `Entrega mínima` e `Não assume` distintos: o teste de fronteira já falhava lá, em prosa |
| Migrar o modo `JULGAR` "porque já funciona" | Dois donos da nota sobre o mesmo candidato. Mesmo descarte do ADR-006 (modo `JULGAR` de Arquitetura), do ADR-009 (painel cego de Design) e do ADR-003 (conformidade sem nota) |
| Fundir `agente-configuracao-e-hardening` com `agente-cadeia-de-suprimentos` — sete agentes | **O corte mais próximo de cair, e o candidato número um a revisão.** Descartado porque são perguntas diferentes, com evidência diferente — baseline e IaC de um lado; SBOM, atestado e custódia de chave do outro — e o registro do legado as separa desde a versão 1.1. Se a operação real mostrar uma fila só, esta é a primeira fusão a reavaliar |
| Criar `agente-ia-e-autonomia` — nove agentes | Prompt injection é dimensão 4, autorização de ferramenta é dimensão 3, vazamento é 5 e 8, ação autônoma sem trilha é 9. O agente disputaria cada recorte com o irmão dono. Vira critério transversal obrigatório (decisão 6) |
| Separar `criptografia e segredos` de `código e API` — nono ou décimo agente | O legado mantém os dois na mesma função (`CODE_APPSEC`), e a separação útil já existe e é outra: **descobrir** o segredo × **responder** ao incidente (decisão 5). Um agente só de cripto disputaria chave com privacidade, com cadeia de suprimentos e com o próprio código |
| Dar a evidência ao produtor do achado | Autocertificação: quem achou declara o próprio fechamento. É literalmente o último item da lista de evidência **rejeitada** do próprio legado |
| Manter o nome `agente-privacidade-e-compliance` | "Compliance" alcança a conformidade com as Regras de Ouro, que é do `departamento-auditoria-responsabilidades`, e sugere parecer jurídico, que o próprio legado exclui (`DATA_LGPD` "não assume parecer jurídico"). O nome novo diz o que o agente realmente cobre |
| Manter os pesos como "cobertura ponderada, só para uso interno" | Número entre 0 e 10 num pacote de segurança é lido como nota e reapareceria no retorno ao Diretor. ADR-006 e ADR-009 converteram rubrica em cobertura sem deixar resíduo numérico; repetir |
| Deixar os cinco gatilhos de `BLOQUEAR` em prosa, como no legado | Gate que depende de disciplina foi exatamente o que o ADR-008 e o ADR-009 converteram em condição de schema. Aqui o custo de errar é liberar um sistema com crítico aberto |
| Manter a descoberta de capacidades em runtime, com `AVAILABILITY: available \| unavailable \| unknown` | Time que muda a cada execução é inauditável pelo `departamento-auditoria-responsabilidades` e não travável por `enum` (ADR-009, decisão 1). A flexibilidade volta como `DIRECTOR_CAPABILITY_GAP`, que é explícita e rastreável |
| Usar `lente-especialista-seguranca` como fallback enquanto o pacote não existir | Armadilha nº 9 do guia. Ausência de capacidade é lacuna declarada e bloqueio, nunca substituição silenciosa |

## Critério de revisão

Revisar quando duas fronteiras disputarem o mesmo achado, quando uma fronteira gerar fila recorrente que
não caiba em seu contrato — a candidata declarada é configuração × cadeia de suprimentos —, ou quando o
runtime passar a oferecer capacidade autorizada de teste ativo, hoje a função com maior probabilidade de
virar `CAPABILITY_GAP` recorrente. **Oito é composição inicial, não teto permanente**
([ADR-007](../../departamento-conteudo-marketing/references/adr-007-departamento-e-time-elastico.md),
decisão 2).
