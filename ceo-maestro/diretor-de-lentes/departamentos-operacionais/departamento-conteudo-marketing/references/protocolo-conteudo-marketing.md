# Protocolo único — Departamento de Conteúdo e Marketing

Fonte única dos envelopes internos, capacidades, integração, gates, ações externas e riscos.
`SKILL.md` resume; em conflito, este protocolo vence e o resumo é corrigido.

Envelopes de fronteira pertencem ao
[schema do Diretor](../../../schemas/diretor-de-lentes.schema.json). Este pacote consome
`DEPARTMENT_MISSION` e produz `DEPARTMENT_RETURN`; não os redefine.

## Identidade

Todo envelope interno preserva:

`contract_id` + `contract_version` + `contract_digest` + `department_mission_ref` +
`brief_id` + `round`.

Entregas e manifestos acrescentam `candidate_digest`. Divergência bloqueia como
`BLOCKED_IDENTITY_MISMATCH`. Digest é calculado sobre os bytes/estrutura reais, nunca copiado de
texto sem conferência.

## 1. `CONTENT_MARKETING_BRIEF`

Criado pela gerente antes de delegar. Materializa:

- objetivo e métricas de negócio referenciados;
- audiência e jornada, com fonte;
- produto, proposta de valor, posicionamento e oferta assinados por Negócios;
- mensagem-mãe, canais e ativos requeridos;
- fatos permitidos e claims que exigem prova;
- política de marca, direitos, privacidade, acessibilidade e restrições;
- modo `PRODUCTION_ONLY` ou `AUTHORIZED_ACTIVATION`;
- fontes atuais de especificação e política.

Fato, hipótese e decisão são listas separadas. Campo comercial ausente não é preenchido pela
gerente.

## 2. `MARKETING_ASSIGNMENT`

Gerente → agente. Uma capacidade e um agente dono. Contém identidade, briefing, objetivo,
entradas, saída, evidência, modo, proibições, autorização e retorno.

| Capacidade | Agente |
|---|---|
| `STRATEGY` | `agente-estrategia-conteudo-campanhas` |
| `NARRATIVE` | `agente-narrativa-redacao` |
| `VISUAL` | `agente-direcao-arte-imagem` |
| `VIDEO` | `agente-roteiro-producao-video` |
| `ADVERTISING` | `agente-publicidade-conversao` |
| `EMAIL` | `agente-email-ciclo-de-vida` |
| `INTELLIGENCE` | `agente-inteligencia-relatoria-marketing` |
| `COMPLIANCE` | `agente-governanca-marca-conformidade` |

Agente só opera com assignment válido e `return_to: departamento-conteudo-marketing`. Pedido
direto é `BLOCKED_BYPASS_ATTEMPT`.

## 3. `MARKETING_DELIVERABLE`

Agente → gerente. Deve conter exatamente a capacidade recebida, artefatos reais, evidências,
fontes, assunções, riscos, direitos/proveniência e estado.

`external_action: EXECUTED` exige referências de autorização e recibo. Sem ambas, a entrega é
inválida e a ação é reportada como quebra crítica. `COMPLETED` exige ao menos um artefato e uma
evidência. `BLOCKED` exige motivo e condição de recuperação.

## 4. `CAMPAIGN_ASSET_MANIFEST`

Integra os ativos sem apagar o produtor:

- id, tipo, canal, variante, versão, artifact ref e digest;
- specification ref oficial e data da consulta;
- claim refs e destino;
- alt, legenda, transcrição ou razão de não aplicabilidade;
- titular/licença/território/prazo/canal;
- ingredientes, modificações, uso de IA e Content Credentials quando disponíveis;
- UTM e evento de mensuração sem PII;
- autorização/recibo de ação externa, quando houver.

Ativo sem direito comprovado, claim sem fonte ou especificação volátil não conferida fica
`BLOCKED`; não entra em candidato pronto.

## 5. `CAMPAIGN_READINESS_RECORD`

Oito dimensões, exatamente uma vez:

| Dimensão | Pergunta | Dona primária |
|---|---|---|
| `BUSINESS_ALIGNMENT` | público, valor, oferta e objetivo vieram de Negócios? | estratégia |
| `CLAIMS_EVIDENCE` | cada alegação é verdadeira, delimitada e provada? | conformidade |
| `BRAND` | voz, identidade e experiência são coerentes? | conformidade |
| `ACCESSIBILITY` | alternativas, legendas e leitura inclusiva foram tratadas? | conformidade |
| `RIGHTS_PROVENANCE` | uso, licença, ingredientes e IA estão registrados? | conformidade |
| `PRIVACY_CONSENT` | dados, cookies, lista e segmentação têm base e minimização? | conformidade |
| `CHANNEL_POLICY` | formato, conteúdo, destino e restrição atual passam? | especialista do canal + conformidade |
| `MEASUREMENT` | objetivo, eventos, UTM, hipótese e limites estão definidos? | inteligência |

Estados: `PASS`, `FAIL`, `NOT_APPLICABLE`, `NOT_PROVEN`.

- `PASS` exige evidência.
- `NOT_APPLICABLE` exige razão específica.
- `FAIL` e `NOT_PROVEN` tornam `ready: false`.
- dimensão ausente ou duplicada torna o registro inválido.
- `ready` é recalculado; não é opinião da gerente.

## 6. `MARKETING_CAPABILITY_GAP`

Sete campos obrigatórios: capacidade, agente esperado, causa observada, impacto, estado `OPEN`,
dono de recuperação e condição de recuperação. Uma lacuna por bloco. A gerente não fecha lacuna
que ela abriu nem assume a capacidade.

## 7. Ações externas

| Ação | Padrão | Condição mínima para executar |
|---|---|---|
| gerar arquivo local reversível | permitido na missão | ferramenta e escopo autorizados |
| publicar/postar | negado | canal, conta, ativo, janela, rollback e autorização |
| disparar e-mail | negado | lista lícita, volume, remetente, autenticação, descadastro e autorização |
| comprar/impulsionar mídia | negado | conta, orçamento, teto, período, público e autorização |
| subir lista/segmento | negado | finalidade, base, minimização, segurança e autorização |
| contratar terceiro/licença | negado | valor, fornecedor, direito, prazo e autorização |

Autorização ampla como “pode fazer o marketing” não satisfaz. Expiração, escopo ou conta
divergente bloqueia. Agente registra recibo do resultado e do custo; gerente não infere sucesso.

## 8. Fronteira com o Departamento de Registros

`MARKETING_DELIVERABLE` e `CAMPAIGN_ASSET_MANIFEST` podem conter relatório de desempenho, plano de
mensuração e referência reproduzível. Isso é **produção analítica**, não custódia institucional.

Se a missão exigir memória durável, estado, documentação de produto, material institucional ou
relatório de aprendizagem:

1. manter o artefato e seu digest no candidato;
2. registrar no `DEPARTMENT_RETURN` a necessidade, natureza provável e evidência;
3. devolver ao Diretor;
4. aguardar missão separada do Diretor para `departamento-registros`.

A gerente e seus agentes não escolhem destino canônico, não escrevem na pasta de Registros e não
acionam agente de Registros. O Departamento produtor continua dono do conteúdo e da evidência; o
Departamento de Registros é dono da classificação, persistência, índice e recibo de custódia.

## 9. Consolidação e retorno

1. validar cada deliverable;
2. montar manifesto e calcular digest;
3. executar lint/checks aplicáveis;
4. emitir e recalcular readiness;
5. preservar pendências e dissensos;
6. derivar `DEPARTMENT_RETURN`;
7. validar contra o schema do Diretor;
8. devolver ao Diretor.

O Departamento não envia diretamente aos Juízes. Retrabalho só inicia por `REWORK_ORDER` do
Diretor, mantendo contrato e candidato da rodada.

## Riscos residuais declarados

| Id | Vetor | Consequência | Mitigação | Teto |
|---|---|---|---|---|
| R1 | política de plataforma muda | ativo aprovado internamente pode ser recusado | fonte oficial datada por execução | mudança entre consulta e publicação continua possível |
| R2 | ferramenta não expõe proveniência | uso de IA/ingredientes fica incompleto | manifesto + C2PA quando disponível | autodeclaração não prova toda a cadeia |
| R3 | atribuição observacional | relatório pode confundir correlação com causa | declarar modelo/janela e usar experimento | nem todo canal permite teste causal |
| R4 | autorização textual forjada | ação externa aparenta estar permitida | correlacionar contrato, recurso e expiração | runtime sem canal autenticado não elimina falsificação |
| R5 | licença autodeclarada | ativo pode infringir direito de terceiro | exigir documento e escopo de licença | documento falso requer verificação externa |
| R6 | julgamento reconhece estilo/autoria | cegueira dos Juízes pode ser parcial | higienização do protocolo dos Juízes | fingerprint do conteúdo pode sobreviver |
| R7 | dado de plataforma agregado | segmento pequeno pode reidentificar pessoa | minimização, limiares e revisão | anonimização absoluta não é garantida |
| R8 | execução fora das ferramentas observadas | publicação ou gasto pode não deixar recibo no pacote | negar aceite sem recibo | ação externa fora do runtime só é auditável por evidência posterior |

Todo retorno nomeia os riscos aplicáveis. Risco residual não vira permissão nem resultado
positivo.
