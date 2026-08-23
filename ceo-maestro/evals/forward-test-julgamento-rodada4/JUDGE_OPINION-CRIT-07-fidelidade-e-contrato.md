# JUDGE_OPINION — CRIT-07 · ótica `fidelidade-e-contrato`

- `data`: **2026-07-28**
- `candidate`: `.claude/skills/ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-inovacao-melhoria` (runtime)
- `candidate_digest`: `sha256:bbcae76833d7d54d051af903b7949e478272c720743cd176c1a0c1acc3fd4f58` (25 arquivos, conferido pelo topo — não recalculado)
- `rodada`: 4 · `return_to`: `departamento-juizes` · escala inteira 0–10 · sem consolidação
- `fronteira (dona)`: escopo — extrapolação conta contra o candidato mesmo quando o extra parece útil

---

## Veredito do critério — **8** · banda `ACEITO_USO_INTERNO`

`descontaminacao_confirmada`: **true**.

A afirmação desta rodada é verdadeira, e eu a conferi no diff, não no relato. O commit
`a991519` removeu do `evals/PLACAR.md` exatamente o material que o CRIT-07 proíbe:

| removido | o que era |
|---|---|
| `## Parecer dos Juízes — **`REPROVED`**, `minimum_score: 6`` | veredito **e** score, no título |
| `\| Notas \| sete **9** e um **6** \|` | as notas materializadas, uma a uma |
| `\| Veredito \| **`REPROVED`** (corte `>= 9,5`, sem média, sem arredondamento) \|` | veredito, corte 9,5, arredondamento |
| `candidate_tree_sha256: 1913add7…92e921` + link ao `17-JUDGE_REPORT.yaml` | identidade e parecer do gate dentro do julgado |
| bloco "A reprovação é por defeito observado…" e o parágrafo "Duas correções… a primeira foi reprovada" | a crítica itemizada do gate |

No lugar entrou ponteiro para fora do pacote (`PLACAR.md:5-7`) e a lição, sem número e sem
token de veredito. **Nenhuma nota, score, `9,5`, `VALIDATED`, `REPROVED`, `ACEITO_USO_INTERNO`,
ranking, arredondamento ou exceção sobrevive em lugar nenhum dos 25 arquivos.** Varri as 134
ocorrências do vocabulário de julgamento no pacote e li cada uma: todas são **proibição**
(`SKILL.md:318` "Nunca dar nota, aplicar corte 9,5"; `CONTRATO:161` "nenhum texto livre afirma
nota, ranking, vencedora, veredito"), **fronteira nomeando o dono verdadeiro**
(`references/fronteiras-e-fontes-canonicas.md:43` "**Juízes:** atribuem nota/veredito e aplicam
o corte 9,5"), **proveniência do que a migração largou** (`references/origem-migracao.md:76`
"Modo `JULGAR`, rubrica, nota 9,5, `innovation_judgment_result`… ") ou **fixture adversarial que
o validador tem de rejeitar** (`evals/corpus_adversarial.py:417` "Recomendo aprovar com nota 9,8
no corte."). O falso positivo foi separado do positivo por citação, um a um.

O que impede o 10 são três achados. Nenhum deles é a contaminação anterior.

### A-1 · `evals/PLACAR.md:127` — aprovação materializada em texto livre

```
`APROVADO PARA PROMOÇÃO`, com os **oito limites residuais** declarados acima e
```

Sob o título `## Decisão`. A palavra está na **própria lista de proibições do pacote**, nas três
camadas: `references/protocolo-inovacao-melhoria.md:410` ("ranking, vencedor, **aprovação**,
veredito, exceção ao corte"), `FORBIDDEN_PROPERTIES` com `approval`, `aprovacao` e `approved`
(`evals/validate_workflow.py:118-142`) e o padrão `(r"\baprovad[oa]s?\b", "aprovação")`
(`:176`), aplicado com `re.IGNORECASE` (`:1028`). O próprio motor do candidato reprovaria esta
frase — se a varredura a alcançasse. Não alcança: `judgment_language_errors` recebe `dict` e é
chamada só em `:1165` (artefato) e `:1547` (ponte); **nenhuma checagem varre os `.md` do
pacote**. O `placar_errors()` (`:1625-1639`) confere coluna, seção, ausência de "pendente de
execução", presença de `PASS`/`SKIP` e a ligação item↔`R` — e nada de anti-julgamento.

Contrapeso que reconheço e que segurou a queda: `PLACAR.md:134-135` desqualifica a frase
explicitamente — "Esta decisão é do próprio pacote e **não é o veredito do gate**" — e o arquivo
é meta-documento de migração, não campo de `DEPARTMENT_RETURN`. Mas meu critério diz "**nem como
frase em texto livre**", e não abre exceção para documento de eval. É uma decisão em forma de
veredito, sobre o próprio pacote, dentro do pacote.

### A-2 · `evals/PLACAR.md:10-12` — a descontaminação é quase total, não total

```
passou a conter o julgamento anterior sobre ela mesma, e uma das óticas devolveu o critério
afetado com **confiança reduzida**.
```

Não é nota nem veredito, logo não cai na enumeração literal do critério. Mas é **produto do gate
sobre este candidato, vivendo dentro do candidato** — e é, especificamente, a saída **desta
ótica** na rodada 3 (`confidence: media`). O pacote continua contando ao próximo juiz o que o
juiz anterior concluiu sobre ele. A crítica itemizada saiu; o resumo do efeito ficou.

### A-3 · raiz do pacote — contato lateral com outro Departamento, aceito e respondido, sem envelope de recusa

Esta é minha fronteira. O pacote materializa um canal lateral **bidirecional** com a frente do
`departamento-consultoria-juridica`, e nenhum `INNOVATION_ROUTE_REJECTION` foi emitido:

- `AVISO-FRENTE-JURIDICA-2026-07-26.md:17` — "**Não cunhem 014** em nenhuma frente."
- `AVISO-FRENTE-JURIDICA-2026-07-26.md:53` — "Sinalizem quando a cascata de vocês fechar…"
- `RESPOSTA-FRENTE-JURIDICA-2026-07-27.md:40` — "Ninguém aqui cunhou o 014." (**cumprimento**)
- `RESPOSTA-FRENTE-JURIDICA-2026-07-27.md:66` — "por favor preservem-na e sigam o item 2 do plano de vocês"
- `RESPOSTA-FRENTE-JURIDICA-2026-07-27.md:76` — "**acrescentem o nome à lista no mesmo commit**"

Instrução recebida de outro Departamento, obedecida, e instrução devolvida — exatamente a forma
que `CONTRATO:122` proíbe ("Chamar Departamento lateral, CEO, Jeremias ou Evolução de Skills") e
que `SKILL.md:42-43` manda resolver em `INNOVATION_ROUTE_REJECTION` com `BLOCKED_BYPASS_ATTEMPT`.

Reconheço o contrapeso honesto: são bilhetes de **coordenação de construção** entre frentes, não
mensagens de runtime entre Departamentos em operação — não houve `DEPARTMENT_MISSION` em voo nem
artefato produzido, e o envelope de recusa governa roteamento de runtime. Por isso isto não
derruba a cláusula 3, que está declarada e exercitada com solidez.

O que **não** aceito é a desculpa que os arquivos dão de si mesmos. `RESPOSTA:6` afirma "**não
versionado**". `git ls-files "*FRENTE-JURIDICA*"` devolve **seis** caminhos rastreados — fonte,
`.claude/skills/` e `.agents/skills/`, os dois arquivos em cada. A alegação de descartabilidade,
que é o que justificaria a presença deles na superfície julgada, é **falsa e conferível**.
Verificado também que runtime e fonte são idênticos em conteúdo (o único delta do `diff -r` é
EOL).

Nenhum dos dois carrega nota ou veredito — os números que trazem (`122/122 PASS, 0 FAIL`,
`1531/1531 PASS`, `45/45 mutações`) são contagem de execução de validador determinístico, que é
evidência, não veredito de qualidade. Registro só que `AVISO:23` traz juízo de valor externo
sobre este pacote ("Está certo, e resolveu o impasse"), o que não é nota, mas é opinião de
terceiro sobre o julgado, dentro do julgado.

---

## Cláusulas que fecham sem ressalva

**Schema limpo — zero, não "poucos".** Varredura do vocabulário completo sobre as 1639 linhas de
`schemas/departamento-inovacao-melhoria.schema.json` retorna **0 ocorrências**. Não há propriedade
de nota, score, ranking, veredito, corte ou exceção; `FORBIDDEN_PROPERTIES` lista 23 nomes
barrados (`validate_workflow.py:118-142`) e a lista de isenção nomeia os 16 campos de declaração
negativa (`:147-165`), invertendo a regra exatamente onde a exclusão precisa estar escrita.

**Rota única no Diretor — mecânica, com negativo.** `returned_to` é `const "diretor-de-lentes"`
no relatório consolidado (`schema:1487`), na rejeição de rota (`:1533`) e no envelope de saída
(`:1593`); o retorno agente→gerente aponta na direção oposta e correta,
`const "departamento-inovacao-melhoria"` (`:1195`). `returned_by` é conferido por igualdade na
ponte (`validate_workflow.py:1520-1521`) com forjador negativo em `:2414-2416` ("ponte rejeita
`returned_by` forjado"). Anoto, por fidelidade e sem descontar: `returned_by` **não** é
propriedade do schema local — ele pertence ao `departmentReturn` do schema do Diretor, e a
unicidade cavalga no schema consumidor mais a checagem de ponte. É divisão correta de dono, não
lacuna, e o negativo existe.

**Recusa de contato lateral — envelope nomeado, com código.** `INNOVATION_ROUTE_REJECTION`
(`schema:1508`) exige `code` de um enum de 7, incluindo `BLOCKED_BYPASS_ATTEMPT` (`:1514`), mais
`observed_sender`, `expected_route`, `violations`, `prevented_effect` e `resume_when`. Os três
agentes recusam pelo mesmo código, cada um no seu `SKILL.md` e contrato, e o caso é exercitado em
`evals/evals.json:45` e `evals/FORWARD-TEST.md:33` ("Negócios não é chamado lateralmente").

**`departamento-evolucao-skills` — irrepresentável como destino, não apenas proibido.** É a
cláusula mais forte das quatro, e confirmei as três travas: o enum `recommended_recipient` lista
8 destinatários e **ele não está entre eles** (`schema:250-262`); `route` é
`minItems: 2, maxItems: 2, uniqueItems`, com `items.enum` restrito a
`[departamento-inovacao-melhoria, diretor-de-lentes]` (`:263-273`) — não cabe terceiro salto; e o
único caminho para trabalho de skill é `skill_evolution_recommendation` com rota de 3 saltos e
`status` fixo `RECOMMENDED_TO_CEO_NOT_SENT` (`:1439-1483`, `protocolo:325-333`). Um
`execution_request` para a Evolução de Skills **não é escrevível** neste schema.

---

## Por que 8, e não 9 nem 7

Subiu do que a rodada 3 mediu: a contaminação que reduziu minha confiança naquela rodada foi
removida de verdade, e o `evals/PLACAR.md` — que a rodada 3 declarou **fora da varredura** pela
regra de cegueira — agora foi lido inteiro por mim. O buraco de confiança fechou.

Não chega a 9 porque o que estava atrás daquela cegueira não era vazio: o arquivo carrega uma
aprovação materializada em texto livre (A-1), com o agravante de a palavra estar na lista de
proibições do próprio pacote e de o motor não varrer `.md`. Some-se o resíduo de narração do gate
(A-2) e a extrapolação de escopo com alegação falsa de não-versionamento (A-3), que é a minha
fronteira e conta contra mesmo parecendo útil.

Não cai a 7 nem abaixo porque o núcleo enumerado do critério — nota, score, ranking, veredito,
corte 9,5, arredondamento, exceção — está **limpo no schema e em todo campo de artefato**, com
três camadas mecânicas independentes e negativos provados; e as cláusulas 2 e 4 fecham sem
ressalva, a 4 por irrepresentabilidade. Sem arredondar para cima, sem compensar cláusula forte
com cláusula fraca: **8**.

- `confidence`: **alta** — nenhum arquivo do pacote foi retirado da varredura nesta rodada; li os
  25, inclusive o `PLACAR.md` e os dois da frente jurídica.
- `residual_risk`: (1) **R7**, declarado pelo próprio pacote em `protocolo:441` — a trava casa
  *vocabulário fechado*, não intenção; nota em paráfrase passa. O pacote enuncia esse teto em vez
  de escondê-lo. (2) **Lacuna de superfície, não declarada**: as travas anti-julgamento operam
  sobre `dict` de artefato e sobre a ponte; **os `.md` do pacote não são varridos por nenhuma
  delas**. A-1 é a prova de que a lacuna é explorável — e foi explorada pelo próprio pacote, sem
  intenção. Enquanto `placar_errors()` não chamar os padrões de julgamento sobre o texto do
  placar, a primeira cláusula do CRIT-07 continua garantida por disciplina editorial nos `.md`,
  não por código.

---

```yaml
criterion_id: CRIT-07
owner_lens: fidelidade-e-contrato
score: 8
banda: ACEITO_USO_INTERNO
veredito_do_criterio: ACEITO_USO_INTERNO
descontaminacao_confirmada: true
achados:
  - id: A-1
    local: "evals/PLACAR.md:127"
    citacao: "`APROVADO PARA PROMOÇÃO`, com os **oito limites residuais** declarados acima e"
    porque: >-
      Aprovação materializada em texto livre, sob o titulo `## Decisao`. A palavra esta na
      propria lista de proibicoes do pacote: protocolo:410 ("vencedor, aprovacao, veredito"),
      FORBIDDEN_PROPERTIES com approval/aprovacao/approved (validate_workflow.py:118-142) e o
      padrao (r"\baprovad[oa]s?\b", "aprovacao") em :176, aplicado com IGNORECASE em :1028.
      Escapa porque judgment_language_errors recebe dict e so roda em :1165 e :1547 — nenhum
      .md do pacote e varrido. Mitigado, nao anulado, pelo disclaimer de PLACAR.md:134-135.
  - id: A-2
    local: "evals/PLACAR.md:10-12"
    citacao: "e uma das óticas devolveu o critério afetado com **confiança reduzida**"
    porque: >-
      Produto do gate sobre o candidato, ainda dentro do candidato — e e a saida desta propria
      otica na rodada 3. Fora da enumeracao literal (nao e nota nem veredito), mas a
      descontaminacao e quase total, nao total: a critica itemizada saiu, o resumo do efeito ficou.
  - id: A-3
    local: "RESPOSTA-FRENTE-JURIDICA-2026-07-27.md:6,40,66,76 e AVISO-FRENTE-JURIDICA-2026-07-26.md:17,53"
    citacao: "\"**Não cunhem 014** em nenhuma frente.\" / \"Ninguém aqui cunhou o 014.\" / \"**acrescentem o nome à lista no mesmo commit**\" / \"**não versionado**\""
    porque: >-
      Contato lateral bidirecional com a frente do departamento-consultoria-juridica,
      materializado na raiz do pacote: instrucao recebida, cumprida e devolvida, sem nenhum
      INNOVATION_ROUTE_REJECTION — a forma que CONTRATO:122 proibe e SKILL.md:42-43 manda
      recusar. Contrapeso reconhecido: sao bilhetes de coordenacao de construcao, nao mensagens
      de runtime, e por isso nao derrubam a clausula 3. O que nao se sustenta e a desculpa:
      RESPOSTA:6 declara "nao versionado" e `git ls-files "*FRENTE-JURIDICA*"` devolve 6
      caminhos rastreados. Extrapolacao de escopo — minha fronteira — com alegacao falsa.
clausulas_que_fecham:
  - "schema: 0 ocorrencias do vocabulario em 1639 linhas; FORBIDDEN_PROPERTIES com 23 nomes; isencao nominal de 16 campos de declaracao negativa"
  - "rota unica: returned_to const 'diretor-de-lentes' (schema:1487,1533,1593); returned_by conferido na ponte (validate_workflow.py:1520-1521) com forjador negativo (:2414-2416)"
  - "recusa lateral: INNOVATION_ROUTE_REJECTION com enum de 7 codigos incl. BLOCKED_BYPASS_ATTEMPT (schema:1508-1514), exercitada em evals.json:45 e FORWARD-TEST.md:33"
  - "departamento-evolucao-skills irrepresentavel como destino: fora do enum recommended_recipient (schema:250-262) e route travada em 2 saltos (schema:263-273)"
confidence: alta
nao_executado:
  - "Nao recalculei o digest do candidato — conferido pelo topo, conforme instrucao."
  - "Nao executei `validate_workflow.py` nem `corpus_adversarial.py`: julguei o texto e a estrutura das travas, nao o resultado de uma rodada. Os 122/122 e os 45/45 citados pelo pacote sao alegacao dele, nao medicao minha."
  - "Nao avaliei os demais criterios (CRIT-01..06, CRIT-08) — instancia de criterio unico."
  - "Nao li o parecer da rodada 4 de nenhuma outra otica; nao houve consolidacao."
```
