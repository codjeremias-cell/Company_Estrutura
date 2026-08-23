# ADR-005 — Quatro agentes, registros por natureza e relatório de aprendizagem em pasta própria

- **Data:** 2026-07-26
- **Status:** aceito por decisão de Jeremias
- **Decisores:** Jeremias
- **Escopo:** `ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-registros/`
- **Contexto normativo:** [ADR-001 da hierarquia executiva](../../../../references/adr-001-hierarquia-executiva.md) ·
  [ADR-002 dos Juízes](../../../departamento-juizes/references/adr-002-nota-absoluta-e-modo-duplo.md) ·
  [ADR-003 da Auditoria](../../departamento-auditoria-responsabilidades/references/adr-003-conformidade-sem-nota.md) ·
  [ADR-004 da Evolução de Skills](../../../../departamento-evolucao-skills/references/adr-004-evolucao-no-nivel-do-ceo.md) ·
  [ORGANOGRAMA.md](../../../../../ORGANOGRAMA.md) ·
  [regras-de-ouro/REGRAS-DE-OURO.md](../../../../../regras-de-ouro/REGRAS-DE-OURO.md)
- **Proveniência do recorte:** [origem-migracao.md](origem-migracao.md)

Este ADR é escrito **antes** de o pacote existir, porque contraria o
[ORGANOGRAMA.md](../../../../../ORGANOGRAMA.md) em dois pontos — a contagem de agentes e o nome do
terceiro — e o passo 1 do [guia](../../../../../GUIA-DE-EXPANSAO-E-MIGRACAO.md) proíbe inventar nome
no pacote deixando o organograma mentindo.

## Contexto

O [ORGANOGRAMA.md](../../../../../ORGANOGRAMA.md), item 10, nomeia três agentes mínimos para o
Departamento de Registros:

```text
departamento-registros
├── agente-memoria-e-decisoes
├── agente-estado-e-handoffs
└── agente-documentacao-e-aprendizados
```

O terceiro **acumula duas coisas**: documentação e aprendizado. O passo 8 do guia impõe o teste de
fronteira: *para qualquer critério do domínio, exatamente um agente pode reivindicá-lo; se dois
podem, as fronteiras estão mal cortadas; se nenhum pode, falta agente*. Documentação e relatório de
aprendizagem falham nesse teste por uma razão concreta, não estética: **eles têm consumidores
diferentes**.

- **Documentação** serve **leitores do produto** — quem usa e quem mantém. Ela nasce do comportamento
  real do sistema, envelhece junto com o produto e mora no repositório do projeto-alvo. É a natureza
  `documento-produto` do domínio legado, cujo `DURABLE_KEY` é caminho no repositório mais heading.
- **Relatório de aprendizagem** serve o **método**. Ele é minerado pelo
  [`ceo-maestro/departamento-evolucao-skills/`](../../../../departamento-evolucao-skills/SKILL.md),
  que **já existe** no caminho canônico e já declara, em
  [`references/mineracao-e-proveniencia.md`](../../../../departamento-evolucao-skills/references/mineracao-e-proveniencia.md),
  o formato exato do que consome: cada achado com `gap_alvo`, `fonte_url`, `fonte_titulo`,
  `fonte_versao`, `acessado_em`, `licenca`, `o_que_e`, `limite_declarado`, `degrau_proposto` de **0 a
  4** e `adaptacao`. Ali também está a trava que decide a forma do relatório: *"Nunca afirmar de
  memória. Conceito sem fonte que resolve é suposição declarada, não gem"*, e *"`licenca:
  desconhecida` limita o degrau a 0 ou 1"*.

Do outro lado, o mesmo Departamento de Evolução declara a dependência que ainda não tinha produtor:
o [ADR-004](../../../../departamento-evolucao-skills/references/adr-004-evolucao-no-nivel-do-ceo.md),
decisão 3, fixa que *"aprendizagem chega por relatório, não por leitura direta"* — ele **não** lê
memória de projeto, junction nem transcript bruto, e **requisita o relatório** ao
`departamento-registros` **através do CEO**. Seu
[`references/protocolo-de-evolucao.md`](../../../../departamento-evolucao-skills/references/protocolo-de-evolucao.md)
registra a lacuna com todas as letras: *"a lacuna previsível desta skill: `departamento-registros`
ainda não existe no caminho canônico"*, e toda rodada que dependa de colheita abre bloco.

Ou seja: existe um consumidor **nomeado, já materializado e já bloqueado** esperando um artefato que
só este Departamento pode produzir. Fundir esse artefato com a documentação de produto, dentro de um
agente que também escreve README e manual, faz o consumidor do método disputar dono com o leitor do
produto — e faz o Departamento entregar duas coisas com um único `Concluído quando:`.

Há ainda um dado de precedente na própria estrutura: o `departamento-evolucao-skills` nasceu com
**quatro** agentes — `agente-colheita-e-diagnostico`, `agente-mineracao-externa`,
`agente-curador-de-candidatos` e `agente-prova-de-evolucao` — e seu protocolo declara o time *"fixo
em 4 capacidades nomeadas"*. O "três no nascimento" do guia é piso de partida, não teto.

Por fim, o legado — `SKILL - Nova formula/maestro/comite-de-lentes/orquestrador-registros` — não
resolve nada disso: ele tinha **zero** agentes reais. O "time" eram quinze **papéis por capacidade**
descritos em prosa, sem pasta, sem `SKILL.md` e sem contrato. Papel descrito não é capacidade
descobrível em runtime, e o guia manda enumerar `agentes/` sem presumir caminho.

## Decisão

### 1. Quatro agentes, não três

O Departamento nasce com **quatro** agentes executores:

| Agente | Reivindica |
|---|---|
| `agente-memoria-e-decisoes` | memória durável e decisões/ADR |
| `agente-estado-e-handoffs` | pendências, estado e handoffs |
| `agente-documentacao-e-materiais` | documentos, entregas e materiais |
| `agente-aprendizados-e-relatorios` | os relatórios de aprendizagem |

O quarto existe porque o teste de fronteira do passo 8 exige dono único por critério, e documentação
e relatório de aprendizagem **não podem** ter o mesmo dono sem que um dos dois consumidores fique sem
resposta.

### 2. O corte das quatro fronteiras, por natureza de registro

O domínio herdado tem **sete naturezas** de registro mais a saída de não-registro
([origem-migracao.md](origem-migracao.md), lista 1). Cada natureza recebe **exatamente um** dono:

| Natureza herdada | Regra de roteamento | Agente dono |
|---|---|---|
| `memoria-duravel` (somente leitura; escrita entregue ao dono) | `R5` | `agente-memoria-e-decisoes` |
| `decisao-adr` | `R3` | `agente-memoria-e-decisoes` |
| `estado` / pendência | `R4` | `agente-estado-e-handoffs` |
| `documento-produto` | `R2` | `agente-documentacao-e-materiais` |
| `guia-playbook` | `R7` | `agente-documentacao-e-materiais` |
| `ideia-backlog` | `R8` | `agente-documentacao-e-materiais` |
| `aprendizagem` colhida | `R6` | `agente-aprendizados-e-relatorios` |
| `nao-registro` | `R1` | **nenhum agente**: a recusa de fronteira é ato que a gerente não delega |

Três recortes finos, para que o teste de fronteira feche sem sobreposição:

- **Handoff de memória é da memória, não do handoff.** Memória durável é somente leitura para o
  Departamento, e sua escrita sai como handoff ao dono. Esse handoff é **inseparável da natureza** e
  fica com `agente-memoria-e-decisoes`. O "handoffs" do nome de `agente-estado-e-handoffs` é o
  **handoff de sessão**: o que a próxima sessão retoma, com pendência, bloqueio e próximo passo.
- **Transição emparelhada tem duas pontas e dois donos.** Uma decisão que gera trabalho fecha em
  `agente-memoria-e-decisoes` na ponta da decisão e em `agente-estado-e-handoffs` na ponta da tarefa
  derivada. Cada **ponta** tem dono único; nenhuma ponta fecha sozinha.
- **Relatório de integridade não é aprendizagem.** A execução dos catorze gates de integridade é
  verificação, e a regra herdada de que **quem age não verifica o próprio ato** vale acima do corte
  por natureza: o verificador de um ato é sempre distinto do seu autor, qualquer que seja o agente
  que o praticou.

### 3. `agente-documentacao-e-aprendizados` passa a `agente-documentacao-e-materiais`

O nome do organograma descreve o acúmulo que a decisão 1 desfaz. Com o aprendizado saindo para o
quarto agente, o terceiro fica com **documentos, entregas e materiais** — e o nome precisa dizer isso,
porque `name` do frontmatter, nome da pasta e nome no organograma são o mesmo texto, e divergência aí
quebra descoberta em runtime.

### 4. Os registros são separados por natureza

Decisão de Jeremias: registro **não** se guarda por rodada, por autor nem por data — se guarda por
**natureza**: memória, projeto, pendências, entregas, materiais e outras. É a mesma lei que o domínio
legado já enunciava — *"a natureza determina o destino"* — promovida aqui a decisão do Departamento.

Consequências diretas: um registro tem **um** destino e **uma** regra que o decidiu; o mesmo fato não
é escrito como verdade em dois lugares; e a lista de naturezas é **fechada** — criar categoria nova é
ato reservado a Jeremias, nunca do agente que está roteando.

### 5. Os relatórios de aprendizagem ficam em pasta própria, e o caminho canônico é este

Caminho canônico, ancorado na **raiz da estrutura**:

```text
Estrutura Final de Skills/
└── registros/
    └── relatorios/
        └── aprendizagem/
```

- Do Departamento (profundidade 4): `../../../../registros/relatorios/aprendizagem/`
- Do `departamento-evolucao-skills` (profundidade 2): `../../registros/relatorios/aprendizagem/`

**Por que fora do pacote da skill.** `departamento-registros/` é **fonte de método versionada**: seu
conteúdo é `SKILL.md`, contratos, protocolo, schema, evals e agentes. Relatório é **saída de
runtime**. Escrever saída dentro do pacote faria a skill guardar os próprios registros, contaminaria
as verificações estruturais do validador — que conferem arquivos obrigatórios e a pasta `agentes/`
com exatamente os nomes canônicos — e criaria um diretório que cresce sem contrato.

**Por que na raiz da estrutura, e não dentro de `ceo-maestro/`.** O produtor está na profundidade 4,
sob o Diretor; o consumidor está na profundidade 2, sob o CEO. Ancorar na raiz dá aos dois um caminho
relativo **fixo**, e nenhum deles passa a depender da árvore interna do outro. Se a pasta morasse
dentro de `departamento-evolucao-skills/`, o produtor escreveria dentro do pacote do consumidor — a
inversão exata que o contrato de autoridade proíbe.

**Por que fora do projeto-alvo.** O domínio legado separa `method_root` de `target_root`. Documento de
produto, estado e memória são do **projeto** e ficam nele. O relatório de aprendizagem é artefato
**cross-projeto do método**: ele existe para que uma lição de um projeto melhore uma skill que serve a
todos. Guardá-lo no projeto-alvo o tornaria inencontrável para o método e faria o consumidor
varrer projetos — exatamente o que o ADR-004 do consumidor proíbe.

**Por que a pasta é `relatorios/` com `aprendizagem/` dentro, e não `relatorios-de-aprendizagem/`.**
Porque a decisão 4 vale também aqui: o Departamento produz mais de uma natureza de relatório —
integridade e conservação, entre outras. Cada uma ganha uma irmã sob `registros/relatorios/` sem
renomear nada.

**O que esta pasta NÃO é.** Ela **não** cria canal de leitura direta. O
[ADR-004](../../../../departamento-evolucao-skills/references/adr-004-evolucao-no-nivel-do-ceo.md) e o
[CONTRATO-DE-COMPROMISSO.md](../../../../departamento-evolucao-skills/CONTRATO-DE-COMPROMISSO.md) do
Departamento de Evolução mandam **requisitar o relatório através do CEO**. Isso continua valendo: a
pasta torna o artefato **localizável, datado e estável por hash**, satisfazendo RI-04; o **acesso**
segue pelo canal hierárquico, e a referência viaja no envelope. Departamento que vai buscar arquivo
na pasta de outro, sem missão, é bypass.

### 6. O organograma é corrigido na fase final da migração

Este ADR precede o pacote; o [ORGANOGRAMA.md](../../../../../ORGANOGRAMA.md) é atualizado no passo 10
— item 10 da lista de Departamentos (quatro agentes, com o terceiro renomeado), árvore canônica e
`## Estado desta etapa`. Até lá, o organograma está **conhecidamente desatualizado neste ponto**, e
este arquivo é a razão registrada.

### 7. A série de ADR desta estrutura é **global**, e este arquivo é o `adr-005`

Decisão de Jeremias, tomada sobre o conflito que a versão anterior deste ADR declarou em aberto.

A disciplina que o Departamento cobra dos outros — *procurar a série antes de escrever, e continuá-la
exatamente* — vale primeiro sobre ele mesmo. A busca no escopo achou uma série viva e única:
**`adr-001` (CEO, hierarquia executiva) → `adr-002` (Juízes, nota absoluta e modo duplo) →
`adr-003` (Auditoria, conformidade sem nota) → `adr-004` (Evolução, no nível do CEO)**, cada arquivo
na pasta do dono da decisão, com a mesma grafia `adr-00N-<slug>.md`. A numeração é **da estrutura**,
não do pacote: o que a pasta diz é **quem decide**, não quem conta.

Consequências da convenção, agora confirmada e não mais concorrente:

- este arquivo é `adr-005-quatro-agentes-e-relatorios-de-registros.md`, e o próximo ADR de **qualquer**
  pacote desta estrutura é `adr-006`, onde quer que ele nasça;
- não existe série por pacote; um segundo `adr-001` em outra pasta seria a cicatriz nº 2 do legado —
  seis ADRs, quatro diretórios, três grafias — reencenada dentro da estrutura nova;
- quem for escrever um ADR procura o **maior número em uso na estrutura inteira** antes de cunhar o
  seu, e registra o ato da busca; cunhar sem procurar é `CONVENCAO_IMPROVISADA`.

## Consequências

- O Departamento nasce com **quatro** agentes, e o teste de fronteira do passo 8 fecha: cada uma das
  sete naturezas tem exatamente um dono, e o não-registro é ato indelegável da gerente.
- O `departamento-evolucao-skills` **deixa de estar bloqueado na entrada de aprendizagem**: passa a
  existir produtor para o relatório que ele requisita ao CEO. A lacuna declarada no
  `protocolo-de-evolucao.md` fica pronta para ser fechada — e a menção a *"ainda não existe no caminho
  canônico"* vira dívida da cascata do passo 10, não fato consumado por este ADR.
- O relatório de aprendizagem passa a ter **forma definida pelo consumidor**: os campos de
  proveniência e o degrau de 0 a 4 vêm do `mineracao-e-proveniencia.md`, e este Departamento os
  **consome**, sem redefini-los localmente.
- A estrutura ganha uma pasta na raiz — `registros/` — que não existe no
  [ORGANOGRAMA.md](../../../../../ORGANOGRAMA.md). Isso é dívida explícita da cascata: árvore canônica
  e `## Estado desta etapa` precisam registrá-la.
- Um agente a mais é um contrato, uma `SKILL.md` e um `openai.yaml` a mais para manter, e o validador
  do pacote passa a exigir **quatro** nomes canônicos em `agentes/` — o que quebra por construção
  qualquer cópia que tenha ficado com três.
- O nome `agente-documentacao-e-aprendizados` deixa de existir; qualquer referência a ele em texto
  futuro é erro de leitura deste ADR.
- O Departamento **não** ganha capacidade de julgar nem de pontuar: continua valendo o ADR-002 (a nota
  é dos Juízes) e o ADR-003 (a prova de conformidade é da Auditoria). Este ADR só reparte trabalho de
  registro.

## Alternativas consideradas

- **Manter os três agentes do organograma.** Descartada: o terceiro acumularia dois consumidores com
  critérios de pronto diferentes — leitor do produto e método —, e o teste de fronteira do passo 8
  falharia no primeiro critério de aprendizagem, que tanto "documentação" quanto "aprendizados"
  poderiam reivindicar. Fronteira que só se resolve por bom senso não é fronteira.
- **Manter três e tratar o relatório de aprendizagem como subproduto da documentação.** Descartada:
  o consumidor do relatório já publicou o formato que exige — `gap_alvo`, fonte, versão, licença,
  limite declarado e degrau. Um subproduto de documentação não nasce com esses campos, e o resultado
  previsível é relatório recusado por proveniência incompleta, ou pior, gem afirmado de memória, que
  a RO-01 proíbe.
- **Criar um quinto agente só para índices e curadoria de hub.** Descartada por ora: indexação é
  **parte do registro**, não natureza separada — o registro só chega a `VERIFICADO` com o índice em
  dia. Um dono separado de índice criaria o `REGISTRO_ORFAO` institucionalizado, com um agente achando
  que gravou e outro que ainda não indexou. Se a prática mostrar volume que justifique, o caso é de
  **expansão** (passos 8, 9 e 10 do guia), com ADR próprio.
- **Deixar a documentação de produto fora deste Departamento.** Descartada: `documento-produto` é uma
  das sete naturezas do teste de roteamento herdado, e `R2` precede `R3..R8`. Tirá-la do Departamento
  deixaria a regra `R2` sem destino e reabriria a pergunta "para onde vai o manual?" a cada missão.
- **Guardar o relatório de aprendizagem dentro de `departamento-registros/references/`.** Descartada:
  `references/` é material normativo do pacote, lido por carregamento progressivo. Encher de saída de
  runtime datada faria o pacote crescer sem limite e transformaria leitura obrigatória em arquivo
  morto — a versão de método da cicatriz nº 8 do legado, a segunda cópia parada no tempo.
- **Guardar o relatório dentro de `ceo-maestro/departamento-evolucao-skills/`.** Descartada: o
  produtor passaria a escrever dentro do pacote do consumidor, invertendo a autoridade e dando ao
  Departamento de Registros escrita num pacote que não é dele.
- **Guardar o relatório no projeto-alvo, junto da memória.** Descartada: o relatório é artefato do
  **método**, não do projeto. Ficaria fora do alcance do consumidor, e a alternativa para alcançá-lo
  seria o Departamento de Evolução varrer projetos — leitura direta que o ADR-004 dele proíbe
  justamente para não haver duas destilações divergentes da mesma lição.
- **Dar ao `departamento-evolucao-skills` leitura direta da pasta, sem passar pelo CEO.** Descartada:
  economizaria um salto e quebraria a cadeia de comando. Departamento que lê artefato de outro sem
  missão é bypass, e o ganho é nenhum — a referência já viaja no envelope.
- **Deixar a decisão dos quatro agentes implícita, sem ADR, e só corrigir o organograma depois.**
  Descartada: contrariar o organograma sem registro é exatamente o que o passo 1 do guia proíbe, e
  seis meses depois ninguém saberia se o quarto agente foi decisão ou descuido.
