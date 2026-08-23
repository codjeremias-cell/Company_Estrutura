# Cobertura do domínio e admissibilidade da prova — Departamento de Segurança

Ler antes de recortar o escopo, atribuir área a agente, declarar cobertura ou aceitar qualquer
evidência. **Fonte única** das doze dimensões do domínio, do `coverage_map`, do catálogo de
referencial por área, da dona de cada área e das duas listas de admissibilidade — o que conta como
prova e o que **nunca** conta.

**O que esta página não faz.** Ela não define envelope, gate, onda, autorização, gatilho de
`BLOQUEAR` nem risco residual: isso é do [protocolo-seguranca.md](protocolo-seguranca.md), fonte
única daquilo. Ela também **não pontua**: aqui não há peso, escala 0–10 nem corte. Nota e veredito
são do `departamento-juizes`
([ADR-002](../../../departamento-juizes/references/adr-002-nota-absoluta-e-modo-duplo.md)); o corte
das oito fronteiras internas é o
[ADR-010](adr-010-seguranca-sem-julgamento-e-time-por-funcao.md); a proveniência do recorte migrado
é [origem-migracao.md](origem-migracao.md).

**Relação com o schema.** [`schemas/departamento-seguranca.schema.json`](../schemas/departamento-seguranca.schema.json)
é a forma executável do que esta página descreve: os nomes de área, os estados de cobertura, os
motivos de rejeição de evidência e as identidades de agente são `enum` lá. Divergência entre as duas
é **defeito a corrigir na mesma sessão**, nunca tolerância: a regra vale por esta página, a forma e o
tipo do campo valem pelo schema.

## 1. As doze dimensões e as onze áreas do `coverage_map`

O legado media doze dimensões com peso somando 10,0. O peso, a escala e o corte **não migraram**
(ADR-010, decisão 3): o que resta é **cobertura**. As dimensões 1 a 11 são as **onze áreas** do
`coverage_map` — o mesmo mapa que o legado já mantinha despontuado ao lado da rubrica. A dimensão 12
não é área: ela é a espinha do próprio ledger, e a dona é a gerente.

| # | Dimensão | Área no `coverage_map` | Dona | O que a área exige para ser declarada coberta |
|---:|---|---|---|---|
| 1 | escopo, ativos, dados e fronteiras | `assets_boundaries` | `agente-modelagem-de-ameacas` | inventário de ativos, fluxos, superfície, classificação e as fronteiras de confiança nomeadas |
| 2 | ameaças, STRIDE, abuso e priorização | `threats_stride` | `agente-modelagem-de-ameacas` | ameaça por ativo com pré-condição, impacto e prioridade; casos de abuso enumerados |
| 3 | IAM, autenticação, autorização e sessão | `iam` | `agente-identidade-e-acesso` | matriz sujeito–objeto–ação, sessão, token, privilégio e o comportamento da **negação** |
| 4 | aplicação, API e entradas/saídas | `application_api` | `agente-seguranca-de-aplicacao` | controle por rota/componente, validação, codificação de saída e referencial (§2) |
| 5 | criptografia e segredos | `crypto_secrets` | `agente-seguranca-de-aplicacao` | algoritmo, biblioteca, chave, armazenamento, log e URL; **descoberta** de segredo exposto |
| 6 | cloud, configuração e condições excepcionais | `cloud_config_exceptions` | `agente-configuracao-e-hardening` | baseline, IaC/config, CI/CD como ambiente e o comportamento sob erro, timeout, fallback e estado parcial |
| 7 | cadeia de suprimentos e integridade | `supply_chain` | `agente-cadeia-de-suprimentos` | dependências, SBOM/SCA, proveniência e atestado do builder, assinatura, custódia e rotação de chave |
| 8 | dados, privacidade e LGPD técnica | `data_lgpd` | `agente-privacidade-e-dados-pessoais` | classificação, minimização, retenção, descarte e pendência legal nomeada |
| 9 | detecção, resposta e resiliência | `detection_response` | `agente-deteccao-e-resposta` | evento, alerta, runbook, contenção, recuperação e o ciclo do incidente de segredo |
| 10 | IA/LLM e autonomia | `ai_llm` | **transversal** (§3) | prompt injection, dado não confiável, vazamento, ferramenta/ação e limite de autonomia |
| 11 | testes, reteste e evidência | `testing_evidence` | `agente-prova-e-reteste` | matriz controle–teste–evidência, versão, autorização, cobertura e `SKIP` declarado |
| 12 | rastreabilidade, cobertura, risco e tratamento | **não é área** — é o ledger | **gerente** | `trace_id` ligando ativo → ameaça → controle → evidência → risco → tratamento → reteste |

A décima segunda chave do mapa, `not_assessed`, não é dimensão: é a **lista de exclusão explícita**,
onde entra o que a rodada decidiu não avaliar, com motivo. Área ausente do mapa é defeito de
construção do ledger; área presente em `not_assessed` é decisão declarada.

### Estados de cobertura

| Estado | Significa | Exige |
|---|---|---|
| `COBERTO` | a área foi avaliada e a evidência sustenta a avaliação | ao menos uma evidência admissível (§4) ligada à área |
| `PARCIAL` | parte da área foi avaliada; o resto está nomeado | o que ficou de fora, dito como lacuna, e a evidência do que entrou |
| `NAO_APLICAVEL` | a área não existe neste alvo | justificativa **ligada a ativo ou fluxo** — "não se aplica" solto é lacuna, não cobertura |
| `NAO_AVALIADO` | a área existe e não foi avaliada | motivo, impacto e a condição que a tornaria avaliável; entra em `not_assessed` |

Regra herdada da rubrica, sem o aparato de nota: **não existe redistribuição**. Área não aplicável
não transfere mérito para outra, e área não avaliada não é compensada por profundidade em área
vizinha. Cobertura alta em onze áreas com uma área crítica em `NAO_AVALIADO` continua sendo uma
rodada com lacuna nomeada.

**Concluído quando:** cada uma das onze áreas tem exatamente um estado com dona nomeada, todo
`NAO_APLICAVEL` cita o ativo ou o fluxo que o justifica, e todo `NAO_AVALIADO` aparece em
`not_assessed` com motivo e condição.

## 2. Catálogo de referencial por área

O referencial é **citado**, nunca inventado. Versão, identificador e data não conferidos viram
`PENDING`; memória não é fonte, e severidade sem base fica qualitativa e fundamentada, nunca um CVSS
fabricado.

| Área | Referencial que a rodada cobre quando aplicável |
|---|---|
| `assets_boundaries` | inventário do próprio alvo, diagrama de fluxo, classificação de dados |
| `threats_stride` | **STRIDE** por elemento, casos de abuso, árvore de pré-condições |
| `iam` | OWASP Top 10 (controle de acesso quebrado), OWASP API Top 10 (BOLA, BFLA), ASVS (autenticação, sessão, autorização) |
| `application_api` | OWASP Top 10, OWASP API Security Top 10, CWE Top 25, ASVS (validação, codificação, erro) |
| `crypto_secrets` | ASVS (criptografia, gestão de segredos), CWE de chave e aleatoriedade |
| `cloud_config_exceptions` | baseline do provedor/host, ASVS (configuração), CWE de configuração insegura |
| `supply_chain` | SBOM, SCA, proveniência/atestado do builder, política de assinatura e custódia de chave |
| `data_lgpd` | LGPD **técnica** — minimização, retenção, descarte, base de tratamento como pendência nomeada |
| `detection_response` | ASVS (logging), runbook do alvo, ciclo de incidente de segredo |
| `ai_llm` | prompt injection, dado não confiável como entrada, vazamento, autorização de ferramenta, limite de ação autônoma |
| `testing_evidence` | SAST, DAST, SCA, secret scanning, fuzzing, pentest **autorizado** e reteste |

**Concluído quando:** toda alegação que depende de referencial cita qual, na versão conferida, e toda
citação não conferível está em `claims_unverified` ou `PENDING`.

## 3. IA/LLM é transversal, e ninguém a herda por descuido

A dimensão 10 não tem agente próprio (ADR-010, decisão 6). Ela se aplica **dentro** da fronteira de
cada agente:

- prompt injection e conteúdo não confiável entram como entrada não confiável → `application_api`;
- autorização de ferramenta de agente e escopo de credencial de automação → `iam`;
- vazamento por contexto, log ou saída de modelo → `crypto_secrets` e `data_lgpd`;
- ação autônoma sem trilha, sem limite e sem parada → `detection_response`;
- a **enumeração** dos casos de abuso de IA/LLM é do `agente-modelagem-de-ameacas`, como qualquer
  outra ameaça — enumerar não é controlar, e o controle continua com o irmão dono da área.

O estado de `ai_llm` no mapa é consolidado pela gerente a partir do que cada agente cobriu na própria
fronteira. Alvo sem componente de IA/LLM fecha `NAO_APLICAVEL` **com o ativo ou fluxo citado**, como
qualquer outra área.

**Concluído quando:** `ai_llm` tem estado consolidado, e cada aspecto aplicável aparece dentro do
relatório do irmão dono da área correspondente, sem agente novo e sem dono duplicado.

## 4. Admissibilidade — o que conta como prova

Uma alegação de segurança vale o que a evidência dela sustenta. A evidência que chega ao ledger é
tipada e classificada pelo `agente-prova-e-reteste`, que é o **único** que decide admissibilidade
(ADR-010, decisão 5): quem produziu o achado não certifica a prova de fechamento dele.

### 4.1 Evidência aceita

| Tipo | Só é admissível com |
|---|---|
| fonte ou configuração versionada | versão ou hash do alvo, e o trecho localizável |
| saída bruta de ferramenta | nome **e versão** da ferramenta, escopo, data, hash e limites declarados |
| teste ativo (DAST, fuzz, pentest) | autorização estruturada válida — alvo, ambiente, janela, ações, parada (protocolo, §3) |
| log | redigido, com origem e correlação; nunca o valor do segredo |
| ADR, threat model ou matriz | rastreável até ativo, ameaça e controle |
| reteste | ligado ao `trace_id` do achado que ele fecha |
| atestado de proveniência | verificação sob âncora de confiança **e** custódia da chave declarada |

### 4.2 Evidência rejeitada — nunca conta como prova

Esta é a lista que mais trabalho faz. Cada item é motivo mecânico de rejeição no schema, e evidência
rejeitada **não sustenta** achado confirmado, fechamento de achado nem estado `COBERTO`:

| Motivo | O que é |
|---|---|
| `ALEGACAO_SEM_ARTEFATO` | afirmação sem artefato que a sustente |
| `SCREENSHOT_SEM_ORIGEM` | imagem sem origem, data e alvo verificáveis |
| `FERRAMENTA_SEM_SAIDA` | ferramenta citada sem a saída dela |
| `SCAN_FORA_DA_VERSAO` | varredura feita sobre versão diferente da avaliada |
| `TESTE_ATIVO_SEM_AUTORIZACAO` | atividade ativa sem autorização estruturada válida |
| `EVIDENCIA_DO_PROPRIO_AVALIADOR` | prova produzida por quem avalia a própria alegação |
| `SEGREDO_EM_CLARO` | evidência que carrega o valor do segredo |
| `SKIP_COMO_PASS` | `SKIP`, silêncio de log ou **ausência de achado** apresentados como `PASS` |
| `ATESTADO_SEM_PRIMARIA` | atestado usado como substituto de evidência primária em alegação crítica |

Duas travas herdadas continuam literais: **`skip` não sustenta `pass`** e **atestado não substitui
evidência primária em alegação crítica**. Em cadeia de suprimentos, **assinatura isolada não basta**:
sem proveniência/atestado do builder verificado, custódia, revisão de acesso, rotação e revogação da
chave, a alegação de integridade fica aberta.

**Concluído quando:** toda evidência do ledger tem tipo, origem, versão/hash, escopo e limites; toda
evidência rejeitada carrega o motivo desta tabela; e nenhum achado confirmado ou fechado se apoia em
evidência rejeitada.

## 5. Severidade, confiança e o achado que fecha

- **Severidade** descreve o impacto no alvo: `critical`, `high`, `medium`, `low`, `informational`.
  Sem dado e referência suficientes para CVSS, usar severidade qualitativa fundamentada — nunca um
  número inventado.
- **Confiança** descreve a força da base probatória: `high`, `medium`, `low`. As duas são
  independentes: crítico com confiança baixa continua crítico e continua aberto.
- **Achado fecha** com prova, não com promessa: `status: closed` exige reteste ligado ao `trace_id` e
  evidência admissível de que o controle esperado passou a ser o observado.
- **Segredo confirmado como válido** só fecha com redação, revogação, rotação, contenção e vínculo a
  incidente. Omitir qualquer um desses estados mantém o achado **aberto** — e quem descobre o segredo
  não é quem declara o incidente contido (ADR-010, decisão 5).

**Concluído quando:** cada achado tem severidade e confiança separadas, cada fechamento tem reteste
com evidência admissível, e nenhum incidente de segredo está fechado com estado faltando.

## 6. Vulnerabilidade encontrada não é defeito do trabalho

Regra herdada, e a mais fácil de perder na tradução: **achado crítico corretamente identificado não
reprova a rodada** — ele obriga a recomendação de risco a ser `BLOQUEAR` (protocolo, §5). A entrega
deste Departamento pode ser excelente enquanto o sistema-alvo permanece bloqueado. São planos
diferentes:

| Plano | Dono | Onde vive |
|---|---|---|
| risco do sistema-alvo | este Departamento | `risk_recommendation` do ledger |
| qualidade desta entrega | `departamento-juizes` | nota e veredito, fora deste pacote |
| conformidade com as Regras de Ouro | `departamento-auditoria-responsabilidades` | prova de conformidade, fora deste pacote |
| fechamento executivo | `ceo-maestro`, pelo Diretor | gate executivo |

Confundir os quatro é o erro que o par herdado `REPORT_SELF_APPROVAL: prohibited` e
`GENERAL_AUDIT_GATE: NOT_ISSUED_BY_THIS_DEPARTMENT` existe para impedir — e ambos são `const` no
schema.

**Concluído quando:** o retorno separa risco do alvo, qualidade da entrega e conformidade, e nenhum
campo deste pacote carrega nota, veredito de corte ou gate geral.

---

Relacionado: [SKILL](../SKILL.md) · [CONTRATO](../CONTRATO-DE-COMPROMISSO.md) ·
[protocolo de segurança](protocolo-seguranca.md) ·
[ADR-010](adr-010-seguranca-sem-julgamento-e-time-por-funcao.md) ·
[origem da migração](origem-migracao.md) ·
[schema do pacote](../schemas/departamento-seguranca.schema.json) ·
[Regras de Ouro](../../../../../regras-de-ouro/REGRAS-DE-OURO.md)
