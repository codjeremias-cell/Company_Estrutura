# Resultado e auditoria — migração integral para o ADR-014

- **work_item_id:** `estado-tarefa-6`
- **missão:** `mission-adr014-2026-07-29`
- **fechamento:** `2026-07-29T17:11:17-03:00`
- **escopo auditado:** CEO, Negócios, Diretor, Juízes e suas fronteiras de julgamento
- **resultado de conformidade:** `COMPLIANT` no escopo do ADR-014
- **pontuação:** não se aplica — Auditoria prova conformidade e não atribui nota

## Resultado executivo

A cadeia vigente aplica uma única régua externa:

| `minimum_score` inteiro | Veredito | Alcança `INTERNO` | Alcança `PRODUCAO` |
|---:|---|:---:|:---:|
| 10 | `VALIDATED` | sim | sim |
| 7–9 | `ACEITO_USO_INTERNO` | sim | não |
| 0–6 | `REPROVED` | não | não |

`required_level` é obrigatório, nasce na `EXECUTIVE_MISSION`, atravessa os envelopes sem
alteração e volta ao fechamento. Ausência ou divergência é recusada antes do julgamento; o nível
não é inferido. Falha crítica, cobertura ausente, critério sem dona, emissão não registrada ou
pendência bloqueante força `REPROVED`, mesmo com nota 10.

A régua decimal `9,5` de Negócios foi preservada somente como instrumento interno. Nenhuma nota
fracionária cruza a fronteira dos Juízes. Negócios não chama os Juízes diretamente: entrega ao
Diretor, único emissor do `JUDGMENT_REQUEST` e único destinatário do parecer.

## Medição reproduzível

| Pacote | Baseline comparável | Final | Delta |
|---|---:|---:|---:|
| `ceo-maestro` | 33/33 | **55/55** | +22 |
| `departamento-negocios` | 170/170 | **226/226** | +56 |
| `diretor-de-lentes` | 53/53 | **79/79** | +26 |
| `departamento-juizes` | 70/70 | **88/88** | +18 |
| **Cadeia completa** | **1575/1575** | **1697/1697** | **+122** |

O plano herdou `1532/1532` de outro checkout. Esse número não é baseline comparável desta frente:
o HEAD `868f1a3` já continha cobertura posterior. A reconciliação usa o mesmo conjunto atual de
instrumentos e o delta final é exatamente `22 + 56 + 26 + 18 = 122`.

Medição final dos 16 instrumentos:

| Instrumento | Resultado |
|---|---:|
| motor compartilhado | 66/66 |
| Evolução de Skills | 58/58 |
| Negócios | 226/226 |
| Juízes | 88/88 |
| Arquitetura de Dados | 116/116 |
| Arquitetura de Software | 73/73 |
| Auditoria e Responsabilidades | 66/66 |
| Conteúdo e Marketing | 40/40 |
| Desenvolvimento | 109/109 |
| Design UX/UI | 114/114 |
| Inovação e Melhoria | 132/132 |
| QA e Usabilidade | 119/119 |
| Registros | 171/171 |
| Segurança | 185/185 |
| Diretor | 79/79 |
| CEO | 55/55 |
| **Total** | **1697/1697** |

Não houve `FAIL` nem validador quebrado. Os oito JSON de schema/fixtures foram parseados, os
quatro validadores alterados compilaram sem gerar artefato e `git diff --check` passou.

### Fidelidade de bytes legados

Três pacotes possuem manifestos históricos sensíveis aos bytes originais. Um checkout inteiramente
normalizado para LF ou CRLF produz falsos negativos em Conteúdo, Inovação e QA. A suíte final foi
executada num checkout de índice com a política EOL do repositório e recebeu os 137 arquivos
legados imutáveis, byte a byte, do checkout principal limpo. Com isso, os três gates passaram em
40/40, 132/132 e 119/119, respectivamente, e a cadeia fechou em 1697/1697.

## Testes adversariais

1. No CEO, uma mutação que fazia todo `external_verdict` virar `VALIDATED` derrubou a suíte para
   **49/55**: seis fronteiras incompatíveis foram rejeitadas.
2. Nos Juízes, uma mutação do exemplo vigente de `rubrica-corte-v2` para
   `rubrica-corte-v1` derrubou a suíte para **87/88**. A nova trava
   `ADR-014, rubrica, exemplos e SKILL são coerentes` ficou vermelha.

Esses resultados demonstram que o verde depende da semântica adotada, e não apenas da presença de
alguma função de estrutura ou de fixtures autorreferentes.

## Achados da auditoria e tratamento

| Achado | Tratamento | Estado |
|---|---|---|
| CEO não reconhecia Evolução como terceiro par executivo em todos os gates | conjunto de executivos, gap de capacidade, retorno e casos atualizados | fechado |
| ADR/rubrica inferiam `PRODUCAO` quando `required_level` faltava | ausência agora é recusada; nenhum default silencioso | fechado |
| exemplo de disputa ainda emitia `rubrica-corte-v1` | exemplo migrado para v2 e protegido por teste adversarial | fechado |
| algumas frases protegiam só `VALIDATED` | lacunas agora proíbem todo veredito positivo; críticas cobrem também uso interno | fechado |
| `analysis` de Evolução é aceito pelo schema, mas rejeitado pelo validador semântico do CEO | separado como tarefa 12; requer decisão sobre gates de análise | aberto, fora do escopo |

O último achado é anterior e independente da régua do ADR-014. Corrigi-lo aqui misturaria a
decisão sobre julgamento externo com outra decisão: se uma análise informativa exige
`JUDGE_REPORT` e `governance_report`. Ele foi preservado como pendência explícita, não tratado como
sucesso nem usado para bloquear a migração concluída.

## Publicação

`deploy-estrutura.ps1` espelhou a fonte para:

- `.claude/skills`
- `.agents/skills`

A verificação SHA-256 em modo `-SomenteVerificar -Runtime Ambos -SemValidacao` retornou `[OK]`
para Claude e Codex: ambos os runtimes estão idênticos à `Estrutura Final de Skills`.

## Limites declarados

- Esta frente não rejulgou os sete pacotes reprovados e não produziu evidência de produção para os
  sete aceitos apenas para uso interno.
- Provas comportamentais de runtime pendentes em outros pacotes continuam pendentes.
- Os registros históricos anteriores ao ADR-014 foram preservados como história, não como regra
  operacional vigente.
