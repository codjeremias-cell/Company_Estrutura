# Contrato executivo e bootstrap — tarefa 13

Data: 2026-07-29  
`contract_id`: `CONTRACT-T13-EVOL-DADOS7-20260729`  
Versão: `1`  
Autoridade humana: Jeremias  
Estado inicial: `CONTRACTED`

## INTENT

Regularizar o candidato técnico da tarefa 7 pela rota canônica de Evolução de
Skills, preservando a correção já provada sem atribuir retroativamente autoria,
execução, nota ou conformidade a quem não as produziu.

## SCOPE_IN

- o pacote
  `ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-arquitetura-dados`;
- os cinco artefatos técnicos alterados na tarefa 7:
  `evals/FORWARD-TEST.md`, `evals/PLACAR.md`, `evals/evals.json`,
  `evals/forward-proveniencia.json` e `evals/validate_workflow.py`;
- os artefatos de evidência da tarefa 7;
- área isolada de candidatos da rodada;
- eventual promoção do candidato escolhido somente depois de prova independente,
  Auditoria conforme e `JUDGE_REPORT` que alcance `PRODUCAO`.

## SCOPE_OUT

- fabricar os 16 outputs brutos ausentes;
- converter `NOT_PROVEN` em evidência comportamental positiva;
- alterar ADR-014, ADR-015 ou a RO-W8;
- mexer nas tarefas 8 ou 9;
- publicar, fazer push ou entregar a terceiros;
- atribuir a alteração anterior a qualquer agente.

## DONE

1. `EXECUTIVE_MISSION` válida emitida pelo CEO ao
   `departamento-evolucao-skills`;
2. quatro capacidades do Departamento resolvidas e pinadas;
3. gap observado nomeado com trecho de evidência e alcance medido;
4. ao menos dois candidatos distintos, em área isolada, com anti-sedimento;
5. baseline vermelho→verde executado por agente diferente do curador;
6. fronteira de Pareto recalculável e `EVOLUTION_LEDGER` completo;
7. Auditoria e Juízes independentes sobre o candidato vigente;
8. promoção somente se `minimum_score: 10`, sem `critical_fail`, sem pendência
   bloqueante e com governança `COMPLIANT`;
9. regressões e paridade dos runtimes comprovadas;
10. tarefa 13 concluída no estado retomável apenas depois dos gates.

## Restrições e decisões vinculantes

- `required_level: PRODUCAO`;
- o Departamento de Evolução orquestra, mas não edita a skill viva, não pontua,
  não escolhe vencedor e não promove;
- candidatos ficam fora do canônico até a decisão executiva;
- o agente que produzir candidato fica `CONFLICTED` para provar aquele
  candidato;
- a prova preserva `NOT_PROVEN` enquanto os outputs brutos não existirem;
- o relatório de aprendizagem ainda não existe: a rodada registra
  `TETO_PROVAVEL` e a lacuna correspondente, mas pode usar os artefatos frescos
  da tarefa 7 enviados pelo CEO como material da missão;
- R6 permanece `pending` em todo retorno de Evolução.

## Evidências de entrada

| Evidência | SHA-256 |
|---|---|
| `02-RESULTADO-E-AUDITORIA.md` | `c4ae6f7d94ee38cdd7c1949ee2d97cde5a1ce020ca7f233031c8631709f29cee` |
| `03-DEV-TEST-RETURN.md` | `e702924ff5761d572a7fa0e0fff8b3febc7607cbd040577ba286d98b6dcd648b` |
| `05-AUDIT-RECEIPTS.md` | `11b176fe32df5c110de8043a2f048f31e9aea64e6a6fe1293c5fe05e3361f561` |
| candidato técnico da tarefa 7 | `6745d7b423d1275a1f059a3c3ae247a8771eb063a0bc6152b4601ca06da2c3f4` |

## Bootstrap e capacidades pinadas

| Capacidade | Caminho | SHA-256 |
|---|---|---|
| instrução hierárquica | `Estrutura Final de Skills/AGENTS.md` | `12116eb34b6c9099145f79122a70b5eba7a9c6e975833ff8082e191efb40e608` |
| CEO Maestro | `ceo-maestro/SKILL.md` | `5fe11a01b225690c56c87a7fd617425d087c86f74c7693f141c7dfc9877076ff` |
| contrato do CEO | `ceo-maestro/CONTRATO-DE-COMPROMISSO.md` | `2c50843760c075ca84280ee142ef6616aeb1708f014823b47ef15cbf9e0c0eca` |
| Evolução de Skills | `ceo-maestro/departamento-evolucao-skills/SKILL.md` | `da40d932d9dcb5e34903d082a630e1175d65127226958ef4e9807608617e041a` |
| contrato de Evolução | `ceo-maestro/departamento-evolucao-skills/CONTRATO-DE-COMPROMISSO.md` | `b07d06d393d908c7285b95e4fbeb42a950d803c657cac09b9c1d483c58705574` |
| Diretor de Lentes | `ceo-maestro/diretor-de-lentes/SKILL.md` | `cc762abce8efb77f8e3db44b8ce1b69c804a9c5637e77f3f57a759bb73beb4c3` |
| Departamento de Negócios | `ceo-maestro/departamento-negocios/SKILL.md` | `7bfff1cd0c8f59bd6cb6030090a2733d54435d58a0e012ddf1c09dc85542307f` |
| Departamento de Juízes | `ceo-maestro/diretor-de-lentes/departamento-juizes/SKILL.md` | `a63511167a86d36fa240f124a8e23824fc868597c49af1be33157d72a5660b7a` |
| Regras de Ouro | `regras-de-ouro/REGRAS-DE-OURO.md` | `e307c4e784cfa29525b038504bc7ea6c598087e2527c07e33d3897958197eff6` |

### Time de Evolução

| Capacidade | `SKILL.md` | `agents/openai.yaml` | Estado |
|---|---|---|---|
| `agente-colheita-e-diagnostico` | `53da4bf04dc5c135f1b0b657b61706200fde0860a430b97da6c507c48fe3dd42` | `b28b87cbdbd98efa2e5a2e436b99daa30d055f3419e183c1fd1dfefdd754928e` | `AVAILABLE` |
| `agente-curador-de-candidatos` | `902ee66e8dbc38f830a2d67172643af83faed63d04282547a5ea5c8d4274ced5` | `3714f431f56b8c81afa3303f4b7fc4926681788fb8160bcb18d653d633df34ee` | `AVAILABLE` |
| `agente-mineracao-externa` | `ac6f696ee927a322fb0509fef7afffe5eda61fd52830a460c6218e444909f70b` | `0b069bc9e7a5736e2de4c4c9b9f2e84228ee4e34ee337a86b6f6fe3b6b0905fd` | `AVAILABLE` |
| `agente-prova-de-evolucao` | `45e8c7000ecb0d6fd4f8007a7e84c101713523fdcf992da44a14493a5ac71f84` | `ce8e1d6408dd5fc550effffffe292ae6d68b116049b7907f80e79426dae025e7` | `AVAILABLE` |

O bootstrap está `active`: a raiz e todas as capacidades resolvem sem
junction/reparse point no caminho observado. A capacidade de aprendizagem
existe, mas nenhum relatório materializado foi encontrado; o `README.md` local
declara expressamente que não conta como relatório.
