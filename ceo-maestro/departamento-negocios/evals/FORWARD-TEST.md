# Forward Test — Departamento de Negócios

## Método

Os 15 prompts de `evals.json` foram respondidos por um agente que não recebeu as assertions. O mesmo executor realizou o baseline sem a skill e o ensaio pós-skill com o pacote como única variável nova.

Após o primeiro ensaio, duas omissões de comunicação foram incorporadas ao contrato. Somente os dois casos afetados foram repetidos, novamente sem revelar assertions ao executor.

## Resultado

| Etapa | Casos | Assertions |
|---|---:|---:|
| Baseline sem skill | 2 PASS · 11 PARCIAL · 2 FAIL | 34 PASS · 14 PARCIAL · 14 FAIL |
| Primeiro forward | 13 PASS · 2 PARCIAL · 0 FAIL | 59 PASS · 2 PARCIAL · 1 FAIL |
| Reteste focal | 2/2 PASS | 9/9 PASS |
| Cobertura final combinada | **15/15 PASS** | **62/62 PASS** |

Os treze casos não afetados conservaram o resultado aprovado. O reteste focal fechou as três assertions que ainda não estavam integrais.

## Correções comprovadas

### Proposta completa

O retorno passou a exigir:

- `EXECUTIVE_MISSION`;
- três delegações;
- três relatórios causalmente assinados;
- evidências antes da consolidação;
- Diretor/Juízes, Auditoria, testes e retorno ao CEO.

Evidência comportamental:

> Sem os três relatórios causalmente assinados, não há consolidação nem score; depois vêm Diretor/Juízes, Auditoria, testes e retorno ao CEO.

### Alegação irresponsável

O retorno passou a preservar autor, fonte, período e contexto, além de rejeitar promessa e dado não comprovado.

Evidência comportamental:

> Mercado e Cliente deve remover a promessa e registrar autor, fonte, período e contexto do dado.

## Gates críticos observados

- gerente não executa no lugar dos agentes;
- exatamente três frentes;
- `9.49` não é arredondado;
- score interno não substitui `JUDGE_REPORT`;
- matriz fechada retorna ao CEO;
- agente ausente não usa fallback legado;
- Negócios não decide arquitetura;
- exceção pertence ao CEO e a Jeremias;
- submissão final retorna somente ao CEO.

## Observação

O ensaio mede aderência comportamental aos prompts. Integridade de schema, causalidade, correlação de artefatos e regressões externas são cobertas separadamente por `validate_workflow.py`.
