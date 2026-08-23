# Plano de ação — as cinco pendências abertas

**Data:** 2026-07-27 · **Base:** cadeia em 1531/1531 PASS, runtime com a porta única acionando,
cofre e repositório publicado em paridade.

Este plano existe porque a estrutura chegou num ponto incomum: ela **valida** por completo e
quase nada nela foi **exercido**. As cinco frentes abaixo são o caminho de uma coisa para a
outra. Não são bugs — são provas que faltam e uma dívida de padrão que a própria casa prescreveu.

## Definição de pronto — a régua deste plano

Nenhuma frente aqui fecha com "nota ≥ 9,5 em todas as lentes". Essa régua já saturou nesta base:
revisão adversarial em spec grande estabiliza perto de 8,5 e mais rodadas de leitura não movem o
número. A régua deste plano é outra, em duas partes:

1. **Bloqueante zerado** — nenhum P0/P1 aberto na frente.
2. **Prova de uso** — a frente foi *executada* contra algo real, e a evidência está no `PLACAR.md`
   do pacote dono, com PASS/FAIL/SKIP honesto.

Contagem que muda sem mudança de contrato é regressão. Número de vizinho carrega a data da
medição, ou não entra.

---

## Ordem recomendada, e por quê

```text
1. Sinal à frente jurídica     → destrava OUTRA pessoa. Horas de espera, minutos de trabalho.
2. As 10 asserções falhadas    → barato, e hoje três placares carregam pendência sem inventário.
3. Dívida normativa            → precisa vir ANTES do julgamento (ver frente 5).
4. Cadeia ponta a ponta        → o degrau que converte "valida" em "funciona".
5. Parecer dos Juízes          → só faz sentido depois de 3 e 4.
```

A dependência que decide a ordem: **julgar antes de padronizar é queimar o gate**. Os Juízes
reprovariam 51 de 66 contratos por violarem o `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, e o veredito não
ensinaria nada que a frente 3 já não saiba. Pior: gastaria a primeira rodada de julgamento — a
mais informativa — num achado conhecido.

---

## Frente 1 — Sinal à frente jurídica

**O que é.** A frente da Consultoria Jurídica deixou um arquivo de coordenação em
`departamento-inovacao-melhoria/AVISO-FRENTE-JURIDICA-2026-07-26.md` pedindo aviso de quando
nossa cascata fechasse e os dois arquivos compartilhados parassem de mudar. Fechou.

**Por que importa.** Sem o sinal, vira espera mútua: eles esperando por nós, nós supondo que
seguem sozinhos. E há um erro no plano deles que só nós podemos corrigir a tempo.

**O que fazer.**
1. Escrever a resposta na mesma pasta de coordenação, informando: cascata fechada; número final
   da cadeia (**1531/1531**, motor 61 + 15 validadores); `ORGANOGRAMA.md` e
   `diretor-de-lentes/references/origem-migracao.md` estáveis desde 2026-07-27.
2. **Corrigir a contagem no plano deles.** O aviso diz que vão "corrigir de onze para doze
   Departamentos operacionais". Está errado nas duas pontas: hoje são **dez**, e com o jurídico
   serão **onze**. Os Juízes ocupam camada paralela e nunca foram operacionais. A nota "Como
   contar" que ficou no `ORGANOGRAMA.md` explica a causa raiz — o item 10 numerado no meio da
   lista — e existe para o merge deles pegar isso.
3. Informar que **ADR-014 continua reservado** para eles e que ninguém aqui o cunhou.

**Pronto quando:** o arquivo de resposta existe na pasta de coordenação e nomeia os três pontos.

**Custo:** minutos. **Risco:** nenhum. **Faz sozinha:** sim.

---

## Frente 2 — O instrumento de eval, não as asserções

> **Esta frente foi reescrita em 2026-07-27, na segunda passada.** A primeira redação dizia que as
> 10 asserções falhadas "nunca foram inventariadas". **Falso** — os três `FORWARD-TEST.md` as
> inventariam e classificam em detalhe. O erro foi meu: corrigi a contradição dos placares sem
> reler os forwards, e o plano herdou a suposição. A investigação que eu propunha **já estava
> feita**; o que ela revela é um problema maior.

**O que é.** As 10 asserções estão nomeadas e classificadas. Abrindo a classificação:

| Pacote | Falhas | Diagnóstico já registrado |
|---|---:|---|
| `arquitetura-software` | 5 | **4 defeito do catálogo** (casos 1, 10, 11, 15) + **1 lacuna real** (caso 7) |
| `auditoria-responsabilidades` | 2 | **2 defeito do instrumento** — "não é falha da skill, é o contrato funcionando" |
| `evolucao-skills` | 3 | **3 lacuna real** (casos 2, 3, 5) |

**Seis das dez são o mesmo defeito**, e ele não está nas skills: os prompts do catálogo são
**pedidos crus do usuário**, mas os contratos exigem envelope (`DEPARTMENT_MISSION`, os nove
drivers). A skill bloqueia corretamente no portão — e a asserção, que descreve comportamento
*depois* do portão, fica inalcançável por construção. O forward da Auditoria diz com todas as
letras: *"o catálogo mede a recusa com precisão e mede a execução por hipótese"*.

**O padrão é sistêmico, não local.** Além das 6 asserções, há **4 casos inválidos por
especificação** em quatro pacotes diferentes: caso 1 da Auditoria, caso 1 da Evolução, caso 3 do
Design e caso 1 dos Juízes. Cinco pacotes, mesma causa.

**Por que importa.** Um instrumento que mede recusa com precisão e execução por hipótese produz
um número que parece resultado e não é. Foi assim que 60/65 e 58/60 conviveram com placares
dizendo "não executado": ninguém confiava no número o bastante para defendê-lo.

**O que fazer.**
1. **Consertar o instrumento, não o placar.** Separar cada `evals.json` em dois blocos declarados:
   **casos de portão** (pedido cru — mede se a skill recusa e roteia) e **casos de operação**
   (com o envelope completo no prompt — mede o que ela faz depois de autorizada). A ação já está
   escrita no forward da Auditoria; falta executá-la nos cinco pacotes.
2. **Aposentar os 4 casos inválidos por especificação**, ou reescrevê-los como caso de portão.
   Caso irrodável não pode continuar contando no denominador.
3. **As 4 lacunas reais viram fixture negativa permanente** no validador do pacote dono — caso 7
   de Arquitetura e casos 2, 3 e 5 da Evolução. Cada uma descreve comportamento que o contrato
   exige e a skill não entregou; é exatamente o material de uma fixture.

**Pronto quando:** os cinco `evals.json` declaram portão × operação; nenhum caso irrodável conta
no denominador; e as 4 lacunas reais são casos negativos no validador, com o número subindo por
cobertura nova.

### Estado — parcialmente executada em 2026-07-27

**Feito.** Os cinco `evals.json` passaram a declarar `tipo` em cada caso, e os quatro casos
irrodáveis viraram `status: APOSENTADO` com `motivo` escrito. A trava entrou **dentro dos cinco
validadores**, não em prosa: caso sem `tipo` válido reprova, aposentado sem motivo reprova, e o
mínimo de 12 passou a contar **só os não aposentados**. Provado por mutação nos dois harnesses
diferentes — o validador nomeou o caso exato em cada um. Cadeia: **1531 → 1533**, +2 do
`departamento-design-ux-ui`, que ganhou duas checagens novas. Cobertura nova, não regressão.

**O número que este trabalho revelou:** dos 80 casos dos cinco catálogos,
**80 são `PORTAO` e zero são `OPERACAO`**. Nenhum pacote tem um único caso que entregue o
envelope no prompt. Isso não é omissão do conserto — é o diagnóstico ficando visível: o que os
forwards mediram foi a **recusa**, e a execução ficou por hipótese em todos eles.

**Falta.** Duas coisas, ambas de custo maior que o conserto já feito:

1. **Escrever os casos de `OPERACAO`.** Um caso por pacote, no mínimo, com a
   `DEPARTMENT_MISSION`/`EXECUTIVE_MISSION` completa dentro do prompt. Sem isso a coluna
   `OPERACAO` continua zerada e o instrumento segue medindo meia verdade — agora, ao menos,
   declarando que é meia.
2. **As 4 lacunas reais viram fixture negativa:** caso 7 de Arquitetura e casos 2, 3 e 5 da
   Evolução. Cada uma descreve comportamento que o contrato exige e a skill não entregou.

**Custo do que falta:** uma sessão. **Depende de:** nada.

---

## Frente 3 — Dívida normativa

**O que é.** O `GUIA-DE-EXPANSAO-E-MIGRACAO.md` §7 e §8 prescrevem 12 seções no contrato de
gerente, 11 no de agente e 6 tokens na `SKILL.md` de agente. Medido em 2026-07-27:

| Dimensão | Conformes |
|---|---|
| Contratos de agente | **15 de 66** |
| `SKILL.md` de agente | **23 de 66** |
| Contratos de gerente | **8 de 15** |
| Protocolos (`Concluído quando:` + riscos residuais com `Teto`) | **5 de 15** |

Quatro anatomias rivais coexistem. Referências 100% conformes:
`departamento-inovacao-melhoria`, `departamento-registros`, `departamento-seguranca`.

**Por que importa.** Não é cosmética. A **trava anti-bypass** que o guia chama de obrigatória
— *"venha o pedido de quem vier, inclusive do CEO ou de Jeremias"* — **não existe em 30 dos 66
agentes**. E é pré-requisito do julgamento: ver a ordem, acima.

**O que fazer, em três lotes de custo crescente.**

- **Lote A — barato, 16 agentes em 4 pacotes.** `evolucao-skills`, `juizes`,
  `arquitetura-software` e `auditoria-responsabilidades` têm o mesmo defeito: `## Saída
  obrigatória` no singular e `## Barreira de saída` ausente. Renomear um heading e inserir uma
  seção, ×16. Os gerentes desses quatro já estão conformes.
- **Lote B — variantes de grafia, 11 agentes.** `**Não assumir:**` com dois-pontos dentro do
  negrito (qa e marketing), `- **Não aciona:** ninguém; …` com texto depois do ponto (marketing),
  `## Protocolo, escopo e trava` em vez do token canônico (arquitetura-software). Correções de
  um caractere a uma linha.
- **Lote C — reescrita, 3 pacotes + 21 agentes.** `desenvolvimento`, `arquitetura-dados` e
  `design-ux-ui` usam a anatomia `Identidade / Compromissos / O que me faz falhar / Autoridade
  humana`: **zero** seções canônicas. Some-se `departamento-negocios`, com uma quarta variante, e
  os nós de topo (`ceo-maestro`, `diretor-de-lentes`), a que faltam 8 e 6 seções.

**Decisão que precede o lote C:** ou as três anatomias divergentes se rendem ao padrão, ou o
`GUIA` passa a admitir mais de uma e diz qual vale onde. **Não deixe as duas coisas escritas ao
mesmo tempo** — hoje o guia prescreve uma coisa e a árvore faz quatro, e é isso que torna a
conformidade não verificável.

**Pronto quando:** o validador de cada pacote passa a checar as seções e os tokens do próprio
pacote — como o de `inovacao-melhoria` faz — e a checagem passa. **Trave em código, não em
prosa:** enquanto a estrutura obrigatória não estiver dentro do validador, ela não está provada.

**Custo:** A e B em uma sessão; C é frente própria, provavelmente várias.
**Depende de:** a decisão acima, que é do Jeremias.

### Estado — **executada** em 2026-07-27

**Feito.** Os três lotes fecharam, e as três dimensões de anatomia estão conformes:

| Dimensão | Antes | Agora |
|---|---:|---:|
| Contratos de agente | 15/66 | **66/66** |
| `SKILL.md` de agente (6 tokens) | 23/66 | **66/66** |
| Contratos de gerente | 8/15 | **15/15** |

Os 24 `SKILL.md` restantes eram os quatro pacotes de anatomia divergente — `negocios` 3,
`arquitetura-dados` 6, `desenvolvimento` 8, `design-ux-ui` 7 —, e nenhum deles tinha **nenhum** dos
seis tokens: não foi renomear heading, foi escrever `## Protocolo e trava anti-bypass`,
`## Fronteira exclusiva` com `Assumir:`/`**Não assumir**` e `## Salvaguardas` por agente, com o
vocabulário real de cada pacote — `DEV_TASK`, `DESIGN_TASK`, `DATA_TASK`,
`BUSINESS_AGENT_MISSION` — e o estado de bloqueio que o **schema daquele pacote** admite. O
trabalho foi aditivo: +1.602 linhas contra 174 removidas, e as removidas são os headings
convertidos e as Redes reescritas em bullet.

**A trava entrou em código, não em prosa.** O motor `_compartilhado` já tinha
`validate_contract_sections`, `validate_skill_tokens`, `SECOES_CONTRATO_AGENTE` e
`TOKENS_SKILL_AGENTE` — mas só **sete** pacotes os chamavam, e nenhum era um dos quatro
divergentes. Arquivo conforme sem validador que o cubra regride na edição seguinte. Os quatro
validadores passaram a conferir os próprios agentes; a cadeia foi de **1546 para 1555**, e os +9
são exatamente os gates novos (negócios +6, os outros +1 cada). Cobertura nova, não regressão.

**Provado por mutação, não por contagem.** Em cada um dos quatro pacotes, um agente teve o
`## Salvaguardas` renomeado e o validador reprovou com `exit=1`, nomeando o caso — e o arquivo foi
restaurado em seguida. Gate que nunca reprovou não é gate.

**Os 7 contratos de gerente, na mesma sessão.** `negocios`, `arquitetura-dados`, `desenvolvimento`
e `design-ux-ui` (12 seções ausentes cada), `conteudo-marketing` (5) e os dois nós de topo —
`ceo-maestro` (8) e `diretor-de-lentes` (6). Nenhuma palavra existente foi descartada: as anatomias
rivais — `Identidade / Compromissos / O que me faz falhar / Autoridade humana / Verificação`, e as
dez seções numeradas de Negócios — foram **preservadas como seções próprias** ao lado das
canônicas, e o que entrou foi o que não existia: `Papel`, `Entradas aceitas`, `Saídas obrigatórias`
com a tabela situação → envelope → schema, `Evidências exigidas`, `Barreira de saída` e
`Bloqueio por conflito`. Cada envelope citado é o do schema daquele pacote, conferido antes de
escrever — `BUSINESS_RETURN` e `B_BLOCKED` em Negócios, `EXECUTIVE_SUBMISSION` e `CAPABILITY_GAP`
no CEO, `DIRECTOR_CAPABILITY_GAP` no Diretor.

**A trava de gerente também entrou em código, e é estrutura-inteira.** Em vez de repetir a
checagem em quinze validadores de idiomas diferentes, `validate_contratos_de_gerente` nasceu no
`_compartilhado`, no mesmo molde de `validate_adr_series`: varre a árvore, e **quem é gerente é
definido pela posição** — pacote novo entra na trava por existir, sem ninguém precisar cadastrá-lo.
Chamada por `ceo-maestro`, `diretor-de-lentes` e `departamento-design-ux-ui`, os mesmos três que já
rodavam a série global de ADR. Cadeia: **1555 → 1558**, os +3 sendo exatamente esses gates.

**Provado por mutação:** com `## Barreira de saída` renomeado no contrato do CEO, os três
validadores saíram com `exit=1`; restaurado, `exit=0`. E um erro do caminho vale registro — na
primeira instalação o `import` do `design-ux-ui` falhou e o validador passou a **quebrar** em vez
de reprovar, o que o meu agregador contou como "0 FAIL". Contagem que cai sem FAIL é validador que
parou de rodar: o laço passou a contar validador quebrado como categoria própria.

---

## Frente 4 — A cadeia ponta a ponta

**O que é.** Está provado que a **porta** aciona: em sessão nova, com frase neutra, o
`ceo-maestro` carrega, confere as capacidades por SHA-256 contra o runtime, fixa a rota e recusa
missão com alvo genérico. O que nunca aconteceu é uma missão **descer e voltar**: CEO →
`EXECUTIVE_MISSION` → Diretor → `DEPARTMENT_MISSION` → Departamento → tarefa ao agente →
retorno → `DEPARTMENT_RETURN` → CEO.

**Por que importa.** É o degrau que converte "estrutura que valida" em "estrutura que funciona".
Tudo o que os 15 validadores provam é que os **artefatos** são bem formados; nenhum prova que a
cadeia produz um deles em operação. E é a frente que dá material real para as Juízes julgarem.

**O que fazer.**
1. Escolher um alvo **pequeno, real e reversível**. Sugestão: uma das 10 asserções da frente 2 —
   a demanda já existe, é verificável e o resultado é útil de qualquer forma.
2. Rodar por `claude -p` em sessão nova, chamando o `ceo-maestro`, e **preservar a saída bruta**.
3. Conferir a linhagem no que voltou: os digests batem entre os envelopes? O agente foi acionado
   por tarefa assinada? O retorno reconcilia com o relatório? Alguma coisa foi afirmada sem
   evidência?
4. Registrar como `FORWARD-TEST` de cadeia no `PLACAR.md` do `ceo-maestro`, com o mesmo rigor da
   medição de acionamento: método, contagem, o que ficou `SKIP`.

**Pronto quando:** existe uma rodada real, com saída bruta preservada, em que cada elo da cadeia
tem envelope rastreável — ou uma lista honesta de onde ela travou e por quê. **Travar é
resultado válido**, e provavelmente mais informativo que passar.

**Custo:** uma sessão. **Depende de:** nada — pode começar hoje.
**Risco declarado:** a rodada pode ser fabricada pela própria gerente (risco residual **R5** do
protocolo de Inovação). Reconciliação por digest encarece, não impede.

### Estado — **executada** em 2026-07-27, em quatro rodadas

Relatório completo em
[`ceo-maestro/evals/FORWARD-TEST-CADEIA.md`](ceo-maestro/evals/FORWARD-TEST-CADEIA.md).

| | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Instâncias | 1 | 4 | 14 | 4 de 8 |
| `DEPARTMENT_MISSION` | não | não | sim | sim |
| Fechou o topo | não | não (45 min) | não (90 min) | **sim (15,9 min)** |

**A cadeia desce, a linhagem reconcilia, o isolamento se sustenta e — com orçamento — ela
fecha e sabe parar sem mentir.** O R5 foi recusado pela própria rodada: sob corte de tempo,
o sistema declarou `producer_digest` **ausente** em vez de fabricá-lo.

**Achados que só a execução produziu:** o digest de capacidade não é estável entre cópias
(EOL de checkout); o `__all__` do motor não exportava `validate_contratos_de_gerente`; e
`departamento-desenvolvimento` era o único dos 15 fora da trava global — os dois últimos
já corrigidos.

**Aberto:** o `adr-014` que a rodada 4 produziu é **proposta não julgada** — versionado,
não aplicado.

---

## Frente 5 — Parecer dos Juízes

**O que é.** Os 15 pacotes têm prova mecânica e **zero notas**. O `departamento-juizes` existe,
tem três agentes, protocolo, rubrica e validador — e **nunca foi acionado**. É por isso que a
planilha `CHAMADAS-E-NOTAS-DAS-SKILLS.xlsx` tem 81 linhas em amarelo.

**Por que importa.** Nesta casa, nota e veredito são exclusivos dos Juízes, e nenhuma entrega é
"validada" sem eles. Hoje toda a Estrutura está estruturalmente pronta e formalmente não julgada
— o que é o estado honesto, e não pode virar permanente.

**O que fazer.**
1. **Depois** das frentes 3 e 4. Julgar antes de padronizar queima a primeira rodada num achado
   já conhecido.
2. Começar por **um** pacote, não pelos 15. Sugestão: `departamento-inovacao-melhoria` — é o mais
   recente, 100% conforme, com corpus adversarial reexecutável e placar honesto. Se ele não
   passar, o problema é a régua, não o pacote.
3. A rota é a canônica: Diretor emite `JUDGMENT_REQUEST`; nenhum Departamento fala com os Juízes.
4. Registrar o parecer no `PLACAR.md` do pacote julgado **e** na planilha, trocando o amarelo
   pela nota.

**Pronto quando:** ao menos um pacote tem parecer emitido pela rota canônica, com nota
registrada; e o placar dele deixa de dizer "nunca passou pelo gate".

**Custo:** uma sessão por pacote. **Depende de:** frentes 3 e 4.

### Estado — **em curso**, rodada 1 executada em 2026-07-27

Relatório em
[`ceo-maestro/evals/FORWARD-TEST-JULGAMENTO.md`](ceo-maestro/evals/FORWARD-TEST-JULGAMENTO.md).

**A rota canônica passou inteira:** CEO → `EXECUTIVE_MISSION` → Diretor →
`JUDGMENT_REQUEST` → Juízes, sem o CEO pontuar e sem canal lateral. Os Juízes conferiram a
identidade do candidato **antes** de abri-lo e devolveram `BLOCKED_CANDIDATE_MISMATCH` —
nenhuma nota inventada para preencher relatório.

**Ainda não há `JUDGE_REPORT`,** e a causa foi erro do operador: a missão fixou um
`candidate_tree_sha256` por receita ad-hoc, não publicada. Fechado na origem —
`digest_de_arvore()` entrou no `_compartilhado` com a receita na docstring, provada por
duas implementações independentes e travada por mutação.

### Fechamento — 2026-07-28, em quatro rodadas

**O critério de pronto foi atingido:** o `departamento-inovacao-melhoria` tem parecer
formal pela rota canônica, e o placar dele não diz mais que nunca passou pelo gate.

| | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| `JUDGE_REPORT` | ❌ | ❌ | ✅ | ✅ |
| `minimum_score` | — | 6 | 6 | **8** |
| Veredito | — | — | `REPROVED` | **`ACEITO_USO_INTERNO`** |
| Alcança o `required_level` | — | — | não | **sim (`INTERNO`)** |

No caminho, o gate **reprovou o operador duas vezes** — evasão na primeira correção,
vocabulário de julgamento na segunda —, e a régua ganhou dois níveis
([ADR-014](ceo-maestro/diretor-de-lentes/departamento-juizes/references/adr-014-dois-niveis-de-veredito.md)),
porque o corte único de 9,5 numa escala inteira exigia 10 em tudo e nenhum pacote passaria.

**Os seis defeitos do parecer estão fechados** — cinco corrigidos com trava em código e
prova por mutação; o de EOL provado **impossível** de corrigir pelo caminho óbvio, e
declarado como limite com o motivo medido (ver `FORWARD-TEST-CADEIA.md`).

### Rodada dos 14 pacotes restantes — concluída em 2026-07-29

Relatório completo em
[`ceo-maestro/evals/julgamento-pacotes-2026-07-29/08-RESUMO.md`](ceo-maestro/evals/julgamento-pacotes-2026-07-29/08-RESUMO.md).

As três óticas emitiram 39 pareceres formais para os 13 candidatos não
reflexivos; o `departamento-juizes` recebeu três pareceres externos e um
`EXTERNAL_JUDGE_REPORT`, sem autojulgamento.

| resultado | quantidade |
|---|---:|
| `VALIDATED` | 0 |
| `ACEITO_USO_INTERNO` | 7 |
| `REPROVED` | 7 |

**Achados que bloqueiam nova rodada:** migração incompleta do ADR-014 em CEO,
Negócios, Diretor e Juízes; uma citação normativa fabricada em Arquitetura de
Dados; conformidade sem proveniência externa no placar de Conteúdo e Marketing;
e prova contraditória no placar de QA e Usabilidade.

> **RETOMAR AQUI.** A tarefa de julgamento está fechada; a próxima frente é
> retrabalho, não uma nova nota. Corrigir primeiro os quatro grupos acima,
> reexecutar as provas afetadas e só então abrir rodada 2 sobre novos digests.
> Continuam separadas: a planilha `CHAMADAS-E-NOTAS-DAS-SKILLS.xlsx`, bloqueada
> por Excel via COM, e a explicação medida do achatamento de cadeia da Frente 5 R2.
>
> Receita para qualquer rodada nova: snapshot isolado + capacidades conferidas
> por SHA-256 + critérios congelados + verificação pelos artefatos emitidos,
> nunca pelo relato do orquestrador.

---

## O que este plano NÃO resolve

- **Prova comportamental dos 66 agentes.** Eles não estão no runtime, por desenho — agente é
  folha e disparar sozinho violaria o contrato dele. A única prova possível é indireta, pela
  cadeia da frente 4.
- **O corpus adversarial compartilha o motor do validador.** Ele mede as mutações conhecidas, não
  a que ninguém escreveu.
- **Anti-julgamento é por vocabulário.** Nota afirmada em paráfrase, fora da lista de padrões,
  continua passando.
- **`mode`, permissões e alvo são conferidos como declaração**, não como canal. Se a ferramenta
  mentir sobre o alvo atingido, a conferência mente junto.

Estes quatro são **tetos**, não tarefas: nenhuma das cinco frentes os fecha, e é por isso que
estão declarados aqui em vez de virarem uma sexta linha do plano.

---

Relacionado: [ORGANOGRAMA](ORGANOGRAMA.md) ·
[GUIA de expansão e migração](GUIA-DE-EXPANSAO-E-MIGRACAO.md) ·
[AGENTS](AGENTS.md) · [Regras de Ouro](regras-de-ouro/REGRAS-DE-OURO.md)
