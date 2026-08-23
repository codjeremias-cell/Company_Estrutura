# Auditoria de responsabilidades e evidências

- **Missão auditada:** `msn-2026-07-29-t3-julgamento-14`
- **Snapshot julgado:** `f938386eb3a7c0eeafa3a97797f8f13afdbd5715`
- **Data:** 2026-07-29
- **Função:** provar conformidade e rastreabilidade; esta auditoria não atribui
  nota, não altera veredito e não corrige candidato.
- **Resultado:** **CONFORME**, com R2, R4 e R6 preservados como limites.

## Matriz de verificação

| controle | evidência observada | resultado |
|---|---|---|
| autoridade | Jeremias autorizou continuar a tarefa 3; o manifesto exclui publicação, promoção e correção silenciosa | conforme |
| identidade | 14 `candidate_digest` e 14 `contract_digest` congelados no manifesto | conforme |
| emissão independente | 39 `JUDGE_OPINION` formais para 13 candidatos e 3 opiniões externas para C05 | conforme |
| trava reflexiva | C05 não possui `JUDGE_REPORT`; recebeu `EXTERNAL_JUDGE_REPORT` de painel externo | conforme |
| schemas | 39 opiniões formais, 13 `DEPARTMENT_JUDGE_REPORT` e 13 `JUDGE_REPORT` validados pelo motor compartilhado | conforme |
| consolidação | o menor score por critério e o menor dos oito critérios foram recomputados; 7 aceites internos e 7 reprovações | conforme |
| artefato real | cada score aponta às opiniões, e cada opinião aponta a arquivo versionado do snapshot | conforme |
| placares | 14 placares registram somente a passagem pelo gate e resolvem para o resumo externo | conforme |
| estado | tarefa 3 concluída; retrabalhos 6–10 registrados; tarefa 11 bloqueada até novos digests | conforme |
| fonte | motor 66/66; 15 validadores 1532/1532; zero FAIL e zero quebrado | conforme |
| runtimes | deploy em ambos os runtimes; fonte, Claude e Codex idênticos por SHA-256 | conforme |

## Reconciliação das contagens

O baseline anterior era **1531/1531** nos 15 validadores. A rodada terminou em
**1532/1532**. O delta `+1` é inteiramente explicado: o novo link para
`08-RESUMO.md`, inserido no placar de `departamento-negocios`, gera uma
checagem dinâmica adicional de link resolvido naquele validador.

O teste do motor compartilhado inicialmente nem executava: ainda importava
`validate_adr_series` de `verificacoes_pacote.py`, embora a função tivesse sido
movida para `verificacoes_estrutura.py`. O import foi corrigido, e a bateria
fechou em **66/66**. O defeito não estava em candidato e não alterou nenhuma
nota; foi corrigido depois da consolidação.

## Imutabilidade da rodada

As opiniões e os relatórios usam o snapshot e os digests congelados antes da
abertura. Nenhum achado foi corrigido dentro dos candidatos durante a
pontuação. As seções “Passagem pelo gate” foram adicionadas aos placares
**depois** dos relatórios, apenas para apontar ao histórico externo; por isso
não fazem parte do `candidate_digest` julgado e exigem novos digests numa
rodada futura.

## Limites preservados

- **R2:** o runtime não expõe substrato e tier verificáveis das instâncias.
- **R4:** fingerprints do conteúdo sobreviveram à anonimização; foram
  predeclarados e não pesaram na nota.
- **R6:** IDs, horários e destinos tornam a emissão auditável, mas não criam
  canal autenticado nem tornam fabricação tecnicamente impossível.
- Os validadores provam estrutura e contratos; não substituem as operações
  reais ainda pedidas nos relatórios.

## Índice de evidências

- [Contrato e manifesto](00-CONTRATO-E-MANIFESTO.md)
- [Registro de emissão](01-REGISTRO-DE-EMISSAO.md)
- [Opiniões de fidelidade](02-JUDGE-OPINIONS-FID.ndjson)
- [Opiniões de robustez](03-JUDGE-OPINIONS-ROB.ndjson)
- [Opiniões de experiência](04-JUDGE-OPINIONS-EXP.ndjson)
- [Relatórios ao Diretor](05-DEPARTMENT_JUDGE_REPORTS.ndjson)
- [Relatórios ao CEO](06-JUDGE_REPORTS.ndjson)
- [Painel externo de C05](07-EXTERNAL-JUDGE-REPORT-C05.json)
- [Resumo consolidado](08-RESUMO.md)
