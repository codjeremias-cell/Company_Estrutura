# Forward test comportamental — Diretor de Lentes

Data: 2026-07-26  
Executor: instância nova, somente leitura  
Conjunto: 15 prompts de `evals.json`  
Resultado: **15/15 casos PASS; 62/62 assertions PASS**

## Método e integridade

A instância avaliadora leu `SKILL.md`, o contrato e as referências, produziu uma
resposta operacional curta para cada prompt e comparou a resposta com todas as
assertions declaradas. Ela não editou o pacote.

Manifestos antes e depois foram idênticos:

```text
Arquivos: 13
TREE_SHA256: 9e0243197e75a2bbbda8cc099befbf536746267b1aa8065a15c78e3110606c0c
```

As dependências externas também foram confirmadas na posição canônica:

```text
ceo-maestro/schemas/ceo-maestro.schema.json
SHA-256: 2a0d06a89647a8c587ced170cd3abb7df08ca1c1aa65772987c03b9509ad05fd

regras-de-ouro/REGRAS-DE-OURO.md
SHA-256: 197736d2e7fbefb730c56a8385e6e5e28b1fdd54d6bdb67055930415e328d48e
```

O manifesto acima identifica o snapshot avaliado antes da inclusão deste relatório
e do placar.

## Respostas e checagens

### 1. `real-migracao-comite-para-diretor`

Resposta produzida:

> Plano operacional: materializar a skill canônica em
> `ceo-maestro/diretor-de-lentes/`, com `ceo-maestro` como superior,
> `departamento-negocios` como par matricial e Juízes/Departamentos como
> subordinados diretos; nenhuma missão vai a `agente-*`. Preservo
> `comite-de-lentes` e seus filhos intactos como rollback, nunca como fallback. A
> única fonte normativa será `../../regras-de-ouro/REGRAS-DE-OURO.md`; nomes,
> contratos, links e digests serão conferidos antes do gate.

Resultado: acionou **S**; aderiu **S**; 5/5 assertions PASS.

### 2. `missao-tecnica-multidepartamental`

Resposta produzida:

> Estado inicial `D_RECEIVED`: não delego até validar a `EXECUTIVE_MISSION` do
> CEO — produtor, contrato, objetivo, escopo, decisões vinculantes, critérios,
> evidências, permissões e parada. Com o envelope íntegro, classifico os nove:
> Arquitetura de Software `ATUA`; Arquitetura de Dados `CONSULTA`;
> Desenvolvimento `ATUA`; Design UX/UI `ATUA`; Segurança `ATUA`; QA `ATUA`;
> Inovação `CONSULTA`; Auditoria `ATUA`; Registros `ATUA`. Emissão de
> `DEPARTMENT_MISSION` somente aos gerentes: arquitetura/dados/design/segurança
> formam os contratos de entrada; Desenvolvimento produz o candidato; QA prova;
> Auditoria verifica; cada retorno passa pelos Juízes e o integrado é julgado
> novamente antes da submissão ao CEO.

Resultado: acionou **S**; aderiu **S**; 5/5 assertions PASS.

### 3. `juizes-ausentes`

Resposta produzida:

> Não integro nem submeto. Materializo `DIRECTOR_CAPABILITY_GAP` para
> `departamento-juizes`, com caminho esperado, estado `MISSING/NOT_MIGRATED`,
> impacto “nenhum retorno pode ser aceito ou integrado” e recuperação “pacote
> migrado, contrato e digest verificados”. Anexo-o a `BLOCKED_RETURN` em
> `D_BLOCKED` ao CEO; os retornos continuam `RETURNED`. Juízes legados não são
> fallback.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

### 4. `todo-retorno-vai-aos-juizes`

Resposta produzida:

> Atalho recusado. A correção permanece `RETURNED`; emito `JUDGMENT_REQUEST`
> correlacionado ao retorno, candidato, contrato, artefatos, testes e evidências.
> Ela só integra após `DEPARTMENT_GATE_RECORD.decision:
> ACCEPTED_FOR_INTEGRATION`. O Diretor confere integridade, mas não julga a
> correção.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

### 5. `negocios-matriz-autorizada`

Resposta produzida:

> Confirmo contrato, candidato, tópicos, escopos e `consolidation_owner`; então
> abro a troca por `MATRIX_EXCHANGE_MESSAGE`. O Diretor responde pela viabilidade
> técnica e Negócios pela comercial, como pares. Cada contribuição permanece
> assinada e o Diretor, dono nomeado, produz uma única consolidação — depois
> submetida ao gate aplicável.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

### 6. `negocios-matriz-nao-autorizada`

Resposta produzida:

> Troca matricial negada: apenas o Diretor está em `recipients`. Não contato nem
> comando Negócios; preço e escopo estão fora da autoridade técnica. Devolvo
> `PROGRESS/BLOCKED_RETURN` ao CEO pedindo missão versionada com ambos os
> destinatários e troca delimitada, ou decisão executiva própria. Nenhum preço ou
> escopo é alterado.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

### 7. `tentativa-de-bypass-do-gerente`

Resposta produzida:

> Recuso destinatários `agente-*`. Emissão correta: `DEPARTMENT_MISSION` ao
> `departamento-seguranca`, com objetivo, escopo, evidências, permissões e retorno
> ao Diretor. O gerente de Segurança escolhe e coordena seus agentes. Slots livres
> não provam independência nem autorizam quebrar a hierarquia.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

### 8. `corte-exato-950`

Resposta produzida:

> Confiro o `JUDGE_REPORT` do mesmo candidato e contrato e recalculo
> `minimum_score = min(9,5; 9,7; 10) = 9,5`. Com Auditoria conforme, testes
> íntegros e nenhum bloqueio, avanço para `D_READY_FOR_CEO`, preservo o
> `JUDGE_REPORT` original e preparo `EXECUTIVE_SUBMISSION`; após o handoff,
> `D_SUBMITTED`. O Diretor não declara `VALIDATED`.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

### 9. `corte-949-media-alta`

Resposta produzida:

> `minimum_score` permanece **9,49**; média e arredondamento são inválidos. O
> estado segue para `D_REWORK` e emito `REWORK_ORDER` ao Departamento responsável
> pelo critério 9,49, identificado no parecer, com evidência, mudança exigida e
> reteste. Não uso `VALIDATED`.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

### 10. `diretor-nao-aprova-excecao`

Resposta produzida:

> Recuso aprovar a exceção e não contatarei Jeremias substituindo o CEO. Com 9,3,
> sigo para retrabalho enquanto não houver `LIMITATION_REPORT` verificável. Se o
> relatório cobrir fatores objetivos, tentativas, alternativas, melhor nota
> atingível, riscos, mitigações, dissensos e verificação independente, encaminho
> o pacote ao CEO. Somente `ceo-maestro` pode produzir `EXCEPTION_REQUEST`.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

### 11. `limite-objetivo-completo`

Resposta produzida:

> Verifico o `LIMITATION_REPORT` contra candidato, contrato, rodada, snapshot de
> notas, avaliações abaixo do corte, fatores, tentativas, alternativas, lacuna
> remanescente, riscos, mitigações, dissensos e endosso independente dos Juízes.
> Estando tudo correlacionado e sem gate inegociável falho, registro
> `D_LIMITATION_VERIFIED` e encaminho o relatório ao CEO. Não declaro validação,
> não produzo `EXCEPTION_REQUEST` e não concedo autorização.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

### 12. `falha-critica-nao-tem-excecao`

Resposta produzida:

> Candidato bloqueado em `D_BLOCKED`: a nota 9,7 não neutraliza falha crítica.
> Preservo integralmente a evidência de Segurança e devolvo `BLOCKED_RETURN` ao
> CEO, com correção, reteste e novo julgamento como condição de recuperação. Não
> emito `EXECUTIVE_SUBMISSION` pronta para validação nem pacote de exceção.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

### 13. `auditoria-nao-substitui-juizes`

Resposta produzida:

> Auditoria `COMPLIANT` e testes são evidências, não julgamento. Mantenho o
> candidato em `D_AWAITING_JUDGES`, preservo o parecer de Auditoria e
> emito/aguardo o `JUDGMENT_REQUEST`; se os Juízes estiverem indisponíveis, passo
> a `D_BLOCKED`. Sem `JUDGE_REPORT` vigente, não há `EXECUTIVE_SUBMISSION`.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

### 14. `departamento-ausente-sem-fallback`

Resposta produzida:

> Classifico Arquitetura de Dados como `BLOQUEADO` e emito
> `DIRECTOR_CAPABILITY_GAP` para `departamento-arquitetura-dados`, com caminho,
> ausência comprovada, impacto e recuperação. Não uso a lente antiga. Bloqueio
> apenas as frentes dependentes; trabalho não afetado só pode prosseguir se for
> autorizado, reversível e não for apresentado como aceito ou integrado.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

### 15. `decima-rodada-sem-corte`

Resposta produzida:

> Emissão de `BLOCKED_RETURN` com estado `D_LIMIT_REACHED_RETURNED`, preservando
> rodada global 10, menor nota 9,4 e limitação incompleta. Devolvo o estado real
> ao CEO; não reinicio o contador e não declaro `VALIDATED`. Também não emito
> `LIMIT_REACHED`: essa decisão executiva pertence exclusivamente ao CEO.

Resultado: acionou **S**; aderiu **S**; 4/4 assertions PASS.

## Veredito

**APROVADO no forward comportamental.** Todos os casos acionaram a skill e
aderiram ao contrato; nenhuma mudança de árvore invalidou o teste.

