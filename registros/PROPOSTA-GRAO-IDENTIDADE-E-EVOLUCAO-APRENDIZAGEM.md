# PROPOSTA — grão, identidade e evolução do registro de aprendizagem

- **Data:** 2026-07-27
- **Status:** **PROPOSTA**, não aceita. Três decisões estão reservadas a Jeremias (D2.2, D3.0 e a
  confirmação de D1); enquanto não houver decisão dele, nada aqui é convenção vigente.
- **Tipo de entrega:** `proposal`
- **Produzido por:** cadeia `ceo-maestro → diretor-de-lentes → departamento-registros` +
  `departamento-arquitetura-dados`, com consulta a `departamento-auditoria-responsabilidades` e
  `departamento-inovacao-melhoria`
- **Escopo:** `Estrutura Final de Skills/registros/relatorios/aprendizagem/`
- **Não decide:** o conteúdo do `LEARNING_REPORT` (já fixado no protocolo, §1.5), a lista de naturezas
  (fechada pelo ADR-005, decisão 4) e os campos do `gem` (do `departamento-evolucao-skills`)

---

## 0. O que já estava decidido, e que esta proposta não toca

Antes de propor qualquer coisa, o levantamento. **Três camadas do formato já existem** e são fonte
vigente — repeti-las aqui seria a cópia local que o próprio pacote proíbe:

| Camada | Onde já está decidido | O que fixa |
|---|---|---|
| Payload do relatório | `departamento-registros/references/protocolo-registros.md`, §1.5 | os 13 campos do `LEARNING_REPORT` e os 15 campos de cada lição |
| Contrato executável | `departamento-registros/schemas/departamento-registros.schema.json`, `$defs/learningReport` | obrigatoriedade, tipos, `const` de `produced_for`, `requested_via` e `return_to` |
| Endereço | ADR-005, decisão 5 | `registros/relatorios/aprendizagem/`, ancorado na raiz da estrutura |
| Natureza e chave durável | `naturezas-e-roteamento.md`, §2 (regra `R6`) | natureza `aprendizagem`; chave durável `projeto + categoria de falha + data da lição` |

**O que continua descoberto, e é o objeto desta proposta:** o grão do arquivo, a identidade do arquivo
e da lição entre rodadas, o índice, e o caminho pelo qual o formato muda sem virar improviso.

---

## D1 — Grão: dois níveis, e nenhum deles é "por projeto"

### Decisão proposta

**O arquivo é a rodada de colheita. A linha é a lição.**

| Nível | Unidade | O que representa | Chave |
|---|---|---|---|
| **Arquivo** | um `LEARNING_REPORT` | **uma rodada de colheita**: uma `DEPARTMENT_MISSION`, uma janela de tempo, uma varredura que saturou | `report_id` |
| **Linha** | um item de `licoes[]` | **uma lição já vivida e destilada** | `projeto + categoria_falha + ocorrido_em` |

### Por que é a rodada, e não a lição nem o projeto

Não é preferência — é o que o schema já obriga:

- `window: {from, to}` e `department_mission_ref` são **obrigatórios e singulares**. Um arquivo por
  lição teria uma janela degenerada; um arquivo por projeto teria uma janela que **nunca fecha**.
- `saturation_declared` e `gaps_de_colheita` são propriedades de uma **varredura**, não de uma lição.
  Um arquivo por lição obrigaria cada lição a declarar a própria saturação — o que não quer dizer nada.
- `licoes` aceita **zero itens** desde que `gaps_de_colheita` traga ao menos um. Uma rodada que não
  colheu nada **ainda é um registro válido** — e isso só faz sentido se o arquivo for a rodada.
  Colheita vazia é informação: é a prova de que se procurou.

### O que isso obriga

- Um relatório **nunca é editado depois de gravado**. Ele é `fonte` (papel do enum de
  `naturezas-e-roteamento.md`, §7), e o papel `fonte` não admite conserto em cima.
- Lição repetida em duas rodadas gera **duas linhas em dois arquivos** — o que é correto, porque cada
  linha prova a sua própria colheita. A ligação entre elas é D2.3, não a fusão dos arquivos.
- A pasta cresce **um arquivo por rodada**, não um por lição. Volume previsível e auditável.

### Quem responde

- **Já respondido:** a natureza `aprendizagem` e sua chave durável são ato de Jeremias, exercido no
  ADR-005, decisão 4. Esta proposta **não** cria natureza nova.
- **Responde por D1:** `departamento-registros` (é decisão de endereço e de grão de registro),
  com `departamento-arquitetura-dados` respondendo pela derivação do grão a partir da cardinalidade do
  schema. Sobe a Jeremias apenas como **confirmação**, porque fixa uma convenção durável.

---

## D2 — Identidade: três identidades, uma existe

### D2.1 — Identidade do arquivo: nome do arquivo **é** o `report_id`

Hoje o `report_id` só tem restrição de charset (`$defs/identifier`: `^[A-Za-z0-9][A-Za-z0-9._:-]+$`,
3 a 128 caracteres). **Convenção de nome de arquivo não existe em lugar nenhum** — nem no protocolo,
nem no schema, nem no README da pasta, que diz apenas "arquivo datado, estável por hash".

**Proposto:**

```text
report_id  = LR-<AAAA-MM-DD>-<NN>          exemplo: LR-2026-07-27-01
nome       = <report_id>.md                exemplo: LR-2026-07-27-01.md
```

- `<AAAA-MM-DD>` é a data de **gravação** (`recorded_at`), não a da lição. A data da lição é campo da
  linha (`ocorrido_em`), e misturar as duas é o erro que a chave durável já separa.
- `<NN>` é o sequencial da rodada **no dia**, dois dígitos, começando em `01`. Duas rodadas no mesmo
  dia são caso real quando a missão vem fatiada.
- **Uma identidade, não duas.** Nome de arquivo e `report_id` são o mesmo texto: isso é o que torna o
  índice de D2.4 biunivocal nos dois sentidos (`REGISTRO_ORFAO` e `INDICE_ADIANTADO`, §8) sem exigir
  uma tabela de tradução que envelheceria sozinha.
- Ordenação lexicográfica = ordenação cronológica. Sem script, sem front-matter, sem parse.

**Compatível com o que já existe:** `LR-2026-07-27-01` passa no `$defs/identifier` sem tocar no schema.

### D2.2 — Nome do índice: **dois precedentes concorrentes, escolha reservada a Jeremias**

`naturezas-e-roteamento.md`, §9, é explícito: *"Escolher entre dois termos concorrentes é ato de
Jeremias; **nomear que os dois existem** é obrigação de quem roteia."* A busca de precedente foi feita
e está registrada:

| Candidato | Precedente encontrado | Contra |
|---|---|---|
| `INDICE.md` | **nenhum** dentro da Estrutura | cunha termo novo numa estrutura que já tem convenção de arquivo-contrato |
| seção de índice dentro do `README.md` existente | `_compartilhado/README.md`, `ceo-maestro/evals/README.md` e o próprio `relatorios/aprendizagem/README.md` — nesta estrutura, `README.md` **é** o arquivo-contrato da pasta | mistura papel `index` com papel de documento no mesmo arquivo, e o §7 pede papel declarado por artefato |

Busca executada em 2026-07-27 sobre `Estrutura Final de Skills/`: nenhum arquivo `*indice*` ou
`*index*` existe na árvore. O único índice-como-prática do cofre é `MEMORY.md`, que está **fora** da
Estrutura e serve a outro dono.

**Não escolhida aqui.** É ato de Jeremias, e cunhar sem escolha é `CONVENCAO_IMPROVISADA`.

### D2.3 — Identidade da lição entre rodadas: a chave durável vira **regra de junção**

O problema, verificável: `licao_id` é declarado como *"id único **no relatório**"*. É identidade
**local**. A mesma lição colhida em duas rodadas recebe dois `licao_id` diferentes, e nada no formato
diz que são a mesma coisa. Consequência prática: o `departamento-evolucao-skills` não consegue
distinguir **reincidência** de **novidade** — e reincidência é justamente o sinal mais forte que uma
lição pode dar sobre o degrau que merece.

**Proposto — e a boa notícia é que não exige campo novo:**

> Duas linhas são **a mesma lição** quando coincidem em `projeto`, `categoria_falha` e `ocorrido_em`.
> A tripla é a chave durável que `naturezas-e-roteamento.md`, §2, já atribui à natureza `aprendizagem`;
> os três campos **já existem** em `learningLesson`. O que falta é a regra que diz que eles, juntos,
> são identidade — e regra não é campo.

- `licao_id` **permanece** local ao relatório. Não vira global, não vira hash, não vira UUID.
- Coincidência da tripla em rodadas diferentes = **reincidência**, e é fato a reportar, não duplicata
  a apagar. Coincidência **dentro do mesmo relatório** é falha de decomposição e reprova a rodada.
- `ocorrido_em` é a data **do fato**, não da colheita — é o que impede que a mesma lição, colhida
  quatro vezes, pareça quatro lições.

### D2.4 — O índice: sem ele, o primeiro relatório nasce órfão

`naturezas-e-roteamento.md`, §8: *"Registro que não se reencontra não existe... A entrada no índice faz
**parte** do registro."* E `REGISTRO_ORFAO` **bloqueia o fechamento**.

Hoje a pasta tem só o `README.md`, que é contrato e declara não ser relatório. **Não há índice.** Logo,
pelo próprio protocolo do Departamento, o primeiro relatório gravado nasce em `REGISTRO_ORFAO` e a
primeira rodada de colheita fecha `PARTIAL` por construção — antes de qualquer erro de execução.

**Proposto:** o arquivo de índice (nome pendente de D2.2) nasce **antes** do primeiro relatório, com
papel declarado `index`, uma linha por relatório:

```markdown
| report_id | janela | licoes | gaps | supersede | gravado em |
|---|---|---|---|---|---|
| LR-2026-07-27-01 | 2026-07-01 → 2026-07-27 | 6 | 1 | — | 2026-07-27 |
```

- Papel `index`: **aponta para registros, não guarda o fato** (§7). Nenhum conteúdo de lição no índice.
- Obrigação por **convenção**, não mecânica — declarado aqui de propósito: §8 diz que só a obrigação
  mecânica pode ser alegada como reprovação objetiva. Se D3 fizer nascer um validador, ela sobe a
  mecânica; até lá, é disciplina, e fingir o contrário seria gate tautológico.

### Quem responde por D2

| Sub-decisão | Dono | Por quê |
|---|---|---|
| D2.1 formato de `report_id` e do nome | `departamento-registros` | é convenção de endereço, e o valor cabe no schema atual |
| D2.2 nome do índice | **Jeremias** | dois precedentes concorrentes nomeados; §9 reserva a escolha |
| D2.3 chave de junção entre rodadas | `departamento-arquitetura-dados` propõe, `departamento-registros` adota | é identidade de registro derivada da chave durável já vigente |
| D2.4 existência e forma do índice | `departamento-registros` | §8 é obrigação dele, e o ato de gravar é do `agente-aprendizados-e-relatorios` |

---

## D3 — Evolução do formato: o schema é **fechado por construção**

### O achado que decide o plano inteiro

`$defs/learningReport` e `$defs/learningLesson` declaram **`additionalProperties: false`**, e **não
existe campo `schema_version`** em nenhum dos dois, nem no `causalHeader` que eles carregam.

Três consequências, todas verificáveis lendo o schema:

1. **Nenhum campo novo pode ser acrescentado a um relatório sem editar o schema.** O validador rejeita.
   Não há caminho aditivo silencioso — o que é uma virtude: o formato não deriva sem que alguém decida.
2. **Um relatório não sabe declarar sua própria versão.** Um leitor futuro não consegue distinguir "não
   tem o campo porque é antigo" de "não tem o campo porque a colheita não achou".
3. **Editar aquele schema é editar um pacote de skill.** Portanto **não é ato do
   `departamento-registros`** — é evolução de skill, e a rota que alcança o
   `departamento-evolucao-skills` é exclusiva do CEO, por `EXECUTIVE_MISSION`.

### D3.0 — `schema_version` no `LEARNING_REPORT`: proposto, e reservado a Jeremias

**Proposto:** acrescentar `schema_version: "<inteiro>"` ao `learningReport`, obrigatório, começando em
`1`, e declarar que **todo relatório gravado antes da adoção é `schema_version: 1` por definição** —
sem reescrever nenhum arquivo, porque relatório é `fonte` e `fonte` não se edita.

Por que sobe a Jeremias e não fica no Departamento: mexer só no `learningReport` é degrau 2; mexer no
`causalHeader` — que é compartilhado por **todos** os envelopes do pacote — é **degrau 3**, e o degrau 3
exige decisão de Jeremias mais prova em ao menos duas skills
(`mineracao-e-proveniencia.md`, §4). A proposta é ficar em **degrau 2**, no `learningReport` apenas,
justamente para não arrastar a estrutura inteira; mas quem confirma o degrau é quem o decide.

### D3.1 — A escada de evolução do formato, mapeada nos degraus que a casa já usa

| Degrau | Que mudança é | Quem executa | Trava de aceitação |
|---:|---|---|---|
| **0–1** | convenção pura: nome de arquivo, formato do `report_id`, forma do índice — **não toca o schema** | `departamento-registros` declara a convenção (§9), com busca de precedente registrada | precedente nomeado; termo concorrente citado; escolha de termo sobe a Jeremias |
| **2** | campo novo, ou restrição mudada, **dentro de** `learningReport`/`learningLesson` | `departamento-evolucao-skills`, sob `EXECUTIVE_MISSION` do CEO | baseline **vermelho→verde executado** no validador do pacote; anti-sedimento: a redação substituída é **apagada**, não empilhada |
| **3** | mudança em `causalHeader` ou em qualquer `$defs` compartilhado — alcança todos os envelopes | **Jeremias decide**; Evolução executa sob missão | prova em ao menos 2 skills; cadeia completa de validadores em regressão |
| **4** | o relatório de aprendizagem deixa de caber nesta natureza e vira outra coisa | **Jeremias**; ADR novo | a fronteira das naturezas foi consultada e não cobre |

Os degraus não são vocabulário inventado aqui: são os de `mineracao-e-proveniencia.md`, §4, aplicados
ao formato em vez de ao material minerado. Usar a escada que já existe é o oposto de cunhar a segunda.

### D3.2 — Como um relatório errado é corrigido: **supersede, nunca edição**

O ciclo de vida (§5) já tem `VIGENTE → SUPERADO → ARQUIVADO`. Mas `learningReport` **não tem campo**
para carregar isso, e `additionalProperties: false` impede acrescentá-lo sem degrau 2.

**Proposto, e honesto sobre a limitação:** enquanto o campo não existir, o ponteiro de supersede vive na
**coluna `supersede` do índice** (D2.4), não dentro do relatório. É uma solução de degrau 0 para um
problema que merece degrau 2 — e fica declarada como tal, com a dívida nomeada, em vez de disfarçada.

Nunca, em nenhum degrau: reescrever um relatório gravado. `fonte` não se conserta em cima; corrige-se
com um registro novo que aponta para o antigo.

### D3.3 — O relatório versionado por hash

O README da pasta promete "estável por hash". Isso só é verdade se ninguém editar o arquivo — o que
D1 e D3.2 já garantem. Nada mais é necessário: o `fonte_digest` de cada lição já prova a origem, e o
digest do próprio arquivo é calculável a qualquer momento porque o arquivo é imutável.

### Quem responde por D3

| Sub-decisão | Dono |
|---|---|
| D3.0 `schema_version` — adotar e em que degrau | **Jeremias** decide; `departamento-evolucao-skills` executa sob `EXECUTIVE_MISSION` do CEO |
| D3.1 a escada de degraus para o formato | `departamento-inovacao-melhoria` propôs; `departamento-registros` opera; CEO autoriza cada degrau ≥ 2 |
| D3.2 supersede por índice, com a dívida declarada | `departamento-registros`, com a limitação registrada |
| D3.3 estabilidade por hash | consequência de D1; nenhum dono novo |

---

## Riscos residuais declarados

1. **O índice é obrigação por convenção, não mecânica.** Enquanto não houver validador que o confira,
   `REGISTRO_ORFAO` depende de disciplina. Declarado, não escondido.
2. **`licoes` aceita colisão de `licao_id` entre relatórios diferentes** — por design, já que a
   unicidade declarada é "no relatório". D2.3 resolve por regra de junção, e regra não é trava: só um
   validador transformaria isso em reprovação objetiva.
3. **Nenhum relatório real foi gravado ainda.** Todo o formato é derivado do schema e do protocolo, não
   da prática. A primeira rodada real pode invalidar D1 ou D2.1 — e o certo é revisitar, não defender.
4. **R6 do protocolo de registros** (risco residual permanente do Departamento) permanece nomeado, como
   toda saída daquele Departamento obriga.

---

## Estado das três decisões

| # | Decisão | Estado |
|---|---|---|
| D1 | grão: arquivo = rodada, linha = lição | **proposta**, aguarda confirmação |
| D2.1 | `report_id` = nome do arquivo = `LR-AAAA-MM-DD-NN` | **proposta**, cabe no schema atual |
| D2.2 | nome do arquivo de índice | **reservada a Jeremias** — dois precedentes nomeados |
| D2.3 | junção por `projeto + categoria_falha + ocorrido_em` | **proposta**, sem campo novo |
| D2.4 | índice nasce antes do primeiro relatório | **proposta** |
| D3.0 | `schema_version` no `learningReport` | **reservada a Jeremias** — degrau 2 proposto |
| D3.1 | escada 0/1/2/3/4 para evolução do formato | **proposta** |
| D3.2 | supersede pelo índice, com dívida declarada | **proposta**, limitação registrada |

**Governada por:** [regras-de-ouro/REGRAS-DE-OURO.md](../regras-de-ouro/REGRAS-DE-OURO.md), fonte
normativa única · posição em [ORGANOGRAMA.md](../ORGANOGRAMA.md) · natureza e endereço em
[ADR-005](../ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-registros/references/adr-005-quatro-agentes-e-relatorios-de-registros.md)
