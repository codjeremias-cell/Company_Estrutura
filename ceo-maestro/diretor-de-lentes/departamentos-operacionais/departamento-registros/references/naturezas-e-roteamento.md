# Naturezas, roteamento e ciclo de vida — Departamento de Registros

Fonte única do **domínio**: o que é um registro, qual é a natureza dele, como se decide o destino, como
ele percorre o ciclo de vida e o que faz um destino ser confiável. Ler antes de decompor, rotear ou
declarar um registro verificado.

Os **envelopes**, a aritmética do ledger, a custódia, a trava anti-bypass, os catorze gates de
integridade e os riscos residuais vivem em [protocolo-registros.md](protocolo-registros.md), fonte
única daquilo — nunca relistados aqui. Os campos e enums são do
[schema do pacote](../schemas/departamento-registros.schema.json); esta página diz o que cada valor
**obriga**, não o que ele é.

**Regra de citação: glosa + ponteiro + digest, nunca cópia.** Norma vigente não é recopiada para
dentro deste pacote — cópia local apodrece em silêncio, e foi assim que uma regra recopiada divergiu
da fonte sem ninguém notar. A forma que não apodrece tem três partes: **glosa curta** do que a fonte
decide, **ponteiro** para o arquivo e **digest** conferido na leitura. É a mesma disciplina que obriga
este pacote a **referenciar**
[regras-de-ouro/REGRAS-DE-OURO.md](../../../../../regras-de-ouro/REGRAS-DE-OURO.md) em vez de copiar
qualquer RI ou RO para dentro dele.

## 1. As leis do domínio

- **A natureza determina o destino** — não a pasta mais próxima, não o arquivo aberto na sessão, não o
  destino usado da última vez.
- **Conservação:** registro identificado ou pousa, ou fica pendente visível, ou é recusado com destino
  nomeado. Nunca some.
- **Registro que não se reencontra não existe.** Gravar sem indexar produz nota órfã; indexar sem
  verificar produz índice que mente. A entrada no índice faz **parte** do registro.
- **Um fato, uma fonte.** O segundo lugar é view derivada, ponteiro ou snapshot — nunca um segundo
  original.
- **Decidir o destino não é ter a caneta.** Onde o ato de gravar pertence a outro dono, este
  Departamento decide, nomeia o dono e entrega o handoff; não escreve.
- **Caminho não conferido é alegação, e caminho conferido não é caminho autorizado.** Existir e estar
  dentro da raiz confiável são duas provas distintas, e as duas antecedem a escrita.
- **Ausência de erro observado não é aprovação.** Gate sem método e evidência é `NAO_VERIFICADO`.

**Concluído quando:** toda decisão de destino da rodada pode ser justificada por uma destas leis, e
nenhuma foi substituída por conveniência de execução.

## 2. As naturezas de registro — lista fechada

**A lista é fechada.** Criar, fundir ou aposentar natureza é **ato de Jeremias**, escalado pelo canal
do Diretor; o agente que estiver roteando **nunca** cunha categoria nova. É a decisão 4 do
[ADR-005](adr-005-quatro-agentes-e-relatorios-de-registros.md): registro não se guarda por rodada, por
autor nem por data — se guarda por **natureza**.

| Natureza | Pergunta que ela responde | Leitor | Envelhece? | Chave durável | Agente dono |
|---|---|---|---|---|---|
| `memoria-duravel` *(somente leitura)* | "como trabalhamos e por quê" | a próxima sessão | não, por definição | caminho do arquivo de memória + âncora do heading | `agente-memoria-e-decisoes` |
| `decisao-adr` | "por que é assim e o que perdemos ao mudar" | quem for reverter | não | escopo + prefixo + número da série | `agente-memoria-e-decisoes` |
| `estado` *(inclui pendência)* | "onde a tarefa está" | quem retoma o trabalho | sim, rápido | id da tarefa na fonte de estado | `agente-estado-e-handoffs` |
| `documento-produto` | "o que este sistema faz e como se usa" | quem usa ou mantém o produto | com o produto | caminho no repositório + heading | `agente-documentacao-e-materiais` |
| `guia-playbook` | "como se faz isto, de novo, em qualquer projeto" | qualquer executor | com a receita | caminho do guia + título da receita | `agente-documentacao-e-materiais` |
| `ideia-backlog` | "o que talvez valha a pena um dia" | o próprio autor, depois | fica ou morre | slug do tema + título da entrada | `agente-documentacao-e-materiais` |
| `aprendizagem` | "o que já aprendemos e não queremos reaprender" | o conjunto dos projetos | não | projeto + categoria de falha + data da lição | `agente-aprendizados-e-relatorios` |
| `nao-registro` | — é saída de fronteira, não natureza | — | — | — | **nenhum**: a recusa é ato indelegável da gerente |

As palavras que Jeremias usa mapeiam sem tradução: **memória** é `memoria-duravel`; **projeto** e
**pendências** são `estado`; **entregas** e **materiais** são `documento-produto`, `guia-playbook` e
`ideia-backlog`; **aprendizados** é `aprendizagem`; **decisões** é `decisao-adr`.

**Esta tabela é a forma operante**, e é a que se lê em execução. O
[ADR-005](adr-005-quatro-agentes-e-relatorios-de-registros.md), §2 e §4, é o **registro da decisão**
que criou a lista e o corte das fronteiras; [origem-migracao.md](origem-migracao.md) é o **inventário
de proveniência** do que veio do legado. Em divergência, vale a decisão do ADR e esta tabela se
corrige na mesma sessão — e a mesma precedência vale para o ciclo de vida e os gates de transição da
§5. Três recortes finos que o teste de fronteira exige:

- **Handoff de memória é da memória.** `memoria-duravel` é somente leitura para este Departamento, e a
  escrita sai como handoff ao dono — handoff inseparável da natureza, logo de `agente-memoria-e-decisoes`.
  O "handoffs" do nome de `agente-estado-e-handoffs` é o **handoff de sessão**: pendência, bloqueio e
  próximo passo.
- **Transição emparelhada tem duas pontas e dois donos** (§6). Cada ponta tem dono único; nenhuma ponta
  fecha sozinha.
- **Verificar não é da natureza, é da independência.** Quem verifica um ato nunca é quem o praticou,
  qualquer que seja o agente — [protocolo](protocolo-registros.md), §2, regra 7.

**Erros típicos de fronteira**, na ordem da tabela: memória absorvendo status e painel de tarefas;
decisão gravada em local e numeração improvisados; estado virando prosa fora da fonte estruturada;
documento descrevendo comportamento que o código não tem; guia virando documentação de um único
produto; ideia virando tarefa antes de amadurecer; aprendizagem copiada bruta em vez de destilada.

**Escopo antes de caminho.** Registro que só faz sentido num projeto permanece nele; registro que
atravessa projetos sobe ao acervo; registro que descreve o método mora com o método. Escopo errado
produz duas patologias simétricas: conhecimento cross-projeto preso num repositório, e detalhe de um
projeto poluindo o acervo comum.

**Concluído quando:** cada registro da rodada tem exatamente uma natureza desta lista, com a chave
durável declarada, e nenhuma categoria nova foi cunhada.

## 3. O teste de roteamento `R1..R8`

Aplicar a tabela **na ordem**, a cada registro atômico, sobre o **texto original preservado** — nunca
sobre o resumo.

| # | Pergunta discriminante | Se sim → natureza | Destino |
|---|---|---|---|
| R1 | pede construir, analisar, executar ou opinar, em vez de guardar um fato? | `nao-registro` | recusa de fronteira (§4) |
| R2 | explica o produto a quem vai usá-lo ou mantê-lo, a partir do comportamento real? | `documento-produto` | repositório do projeto-alvo |
| R3 | fixa escolha estrutural cara de reverter, com alternativas e consequências? | `decisao-adr` | série de ADR do escopo (§8) |
| R4 | descreve algo fazendo, pendente, bloqueado, concluído ou "próximo" — **inclusive defeito conhecido e ainda não corrigido**? | `estado` | fonte de estado do projeto |
| R5 | continua válido daqui a sete dias, mesmo terminando a sprint? | `memoria-duravel` | memória do projeto — **somente leitura**: destino decidido aqui, escrita entregue ao dono |
| R6 | é lição já vivida, destilada para consolidação entre projetos? | `aprendizagem` | camada de aprendizagem do alvo |
| R7 | é receita repetível entre projetos? | `guia-playbook` | guias/playbooks |
| R8 | é desejo ainda imaturo, sem dono, prazo nem decisão? | `ideia-backlog` | captura de ideias |

**O invariante de atomicidade — o coração do teste.**

- Casou com **uma** linha: rotear, registrando-a como regra decisora.
- Casou com **duas ou mais em fatias separáveis**: o registro **não é atômico** — voltar à decomposição
  e dividir. O envelope de decomposição fica sem destino e só aponta as fatias geradas.
- Casou com **duas ou mais na mesma proposição indivisível**: aplicar o desempate nomeado da tabela
  abaixo e registrar **a regra e o desempate**.
- **Zero linhas casadas, ou nenhum desempate aplicável:** `PENDING_DESTINO`, com uma pergunta única ao
  Diretor. **Nunca escolher o destino "mais parecido".**

**Reprodutibilidade:** duas aplicações independentes ao mesmo texto produzem a mesma contagem e os
mesmos destinos. Divergência em que só um lado nomeia a regra resolve-se por ela; divergência em que
**os dois** nomeiam é material e sobe ao Diretor — [protocolo](protocolo-registros.md), §1.4.

| Parece | Mas | Decisão |
|---|---|---|
| convenção com prazo ("vale até a migração acabar") | a convenção é durável enquanto vale; a migração é trabalho | dois registros: convenção na memória **com a condição de expiração escrita**; migração no estado |
| decisão que também vira convenção de trabalho | R3 e R5 casam | dois registros: o ADR guarda a decisão; a memória guarda a convenção apontando para o ADR |
| receita nova que também é preferência | R5 e R7 casam | dois registros: a receita no guia; a memória registra só a convenção adotada |
| ideia que já tem dono, prazo e aprovação | R8 e R4 casam | ideia madura — transição emparelhada (§6) |
| desejo imaturo que também soa durável | R8 e R5 casam na mesma proposição | desempate pela coluna "envelhece": ideia "fica ou morre", memória "não envelhece" — registrar o desempate |
| lição colhida | vive na memória **e** é destilada na camada de aprendizagem | um registro, com destino derivado por link — não duas cópias |
| **relato de defeito encontrado** | parece natureza nova, e **não é** | veio como **motivo da missão** → é envelope, entra no recorte excluído com o motivo escrito; veio **solto** → **R4**, porque defeito conhecido e não corrigido é pendência, e a chave durável é o artefato defeituoso + a discrepância medida |

**O que continua descoberto, e fica dito:** um defeito relatado que **não** vai virar tarefa nem lição,
porque o dono decidiu conviver com ele, não tem destino nesta taxonomia — e o desfecho honesto é
`PENDING_DESTINO` com a pergunta ao Diretor. **Lacuna nomeada é melhor que natureza inventada.**

**Concluído quando:** cada registro casa com uma linha, ou traz desempate nomeado, ou está em
`PENDING_DESTINO` com a pergunta aberta — e nenhum foi roteado por semelhança.

## 4. Fronteira do domínio e a forma da recusa

Não é registro — é trabalho de outra especialidade: escrever, revisar ou depurar código; projetar tela,
fluxo ou componente; executar bateria de teste ou produzir a prova; modelar dados, arquitetar sistema
ou avaliar segurança; auditar governança, dar gate ou comparar candidatos; opinar sobre negócio,
viabilidade ou prioridade executiva.

A recusa tem forma fixa e **quatro obrigações**:

1. dizer **por que não é registro**, citando o que o pedido pede;
2. **nomear a capacidade adequada**, conferida no organograma, ou declarar que não foi possível
   conferir — inventar o nome de uma capacidade para parecer prestativo não vale;
3. **provar que nada foi escrito**, por método independente, com o par antes × depois — "não escrevi
   nada" é autorrelato e não prova a negativa;
4. **redigir** credencial que apareça no trecho literal reproduzido.

Um pedido fora do domínio pode conter, dentro dele, um registro legítimo: a fatia de registro é roteada
e o restante é recusado. **A fronteira separa fatias, não conversas.**

**Concluído quando:** cada fatia recusada tem motivo, capacidade nomeada, prova de ausência de efeito
colateral e trecho redigido — e nenhuma nota foi criada "só para não perder o contexto".

## 5. Ciclo de vida e os seis gates de transição

Cada registro está em exatamente um estado da espinha da rodada:

```text
CAPTURADO → ROTEADO → GRAVADO → INDEXADO → VERIFICADO
```

Depois de `VERIFICADO`, o registro vive: `VIGENTE`, até ser `SUPERADO` (apontando quem o substitui) ou
`ARQUIVADO` (com rótulo de snapshot). Os estados de exceção e o mapa `state → contador` estão no
[protocolo](protocolo-registros.md), §1.4. **Transição sem o gate correspondente comprovado é
inválida**, e estado não deriva de urgência nem de plausibilidade.

| De → Para | Gate de transição | Método (o ato) | Evidência que sustenta |
|---|---|---|---|
| `CAPTURADO → ROTEADO` | `GATE_DECOMPOSICAO` | reaplicar `R1..R8` ao texto original preservado até cada fatia casar com uma única linha | um envelope de roteamento por registro, com o trecho literal; total identificado aberto no ledger |
| `ROTEADO → GRAVADO` | `GATE_DESTINO_UNICO` | conferir regra decisora não vazia, um destino por registro, dono e convenção declarada; abrir ou listar o caminho | evidência do próprio ato de listar, abrir ou testar; convenção com fonte e método de busca |
| `ROTEADO → GRAVADO` | `GATE_CUSTODIA` **(pré-escrita)** | resolver o caminho canônico, inspecionar reparse point e confinamento; varrer o conteúdo candidato antes de existir byte; conferir o nível de canal de quem decidiu destino, convenção e classificação; conferir autorização de ato irreversível | caminho resolvido + confinamento provado; varredura com método e categoria (nunca o valor); item de autorização correspondente |
| `GRAVADO → INDEXADO` | `GATE_FONTE_UNICA` | comparar o hash em disco com o baseline **antes** de escrever; depois reler o artefato no caminho real e confirmar que a escrita foi na fonte, sem view editada | baseline + hash pós-escrita; artefato real; view marcada como regenerada, nunca como atualizada |
| `INDEXADO → VERIFICADO` | `GATE_INDICE` | executar a verificação mecânica quando existir; senão conferir um a um os índices exigidos | saída do script anexada, ou trecho do índice citando o registro, com entrada de histórico datada |
| `INDEXADO → VERIFICADO` | `GATE_INTEGRIDADE` | rodar os catorze gates de integridade **por quem não é autor do ato verificado** | um resultado por gate, com método, reprodução e evidência; `NAO_APLICAVEL` só com justificativa concreta |

**Quem produz `VERIFICADO` são os dois últimos, juntos.** Um registro indexado cuja suíte de
integridade não rodou **não** está `VERIFICADO` e não conta como pousado. `GATE_CUSTODIA` é o **veto de
entrada**: roda entre o roteamento e a emissão da tarefa de escrita, e `FAIL` ou `NAO_VERIFICADO`
impede a emissão.

**Concluído quando:** todo registro que a rodada afirma ter pousado tem, por transição alcançada, o
gate nomeado com método e evidência — e nenhum estado foi atribuído sem eles.

## 6. Transições emparelhadas

Algumas transições **só valem em par**: as duas pontas nascem juntas, ficam em dependência mútua e
nenhuma pode ser dada por concluída sozinha. É a forçante para "uma frase gera dois registros": sem
ela, a metade menos óbvia fecha sozinha e some.

| Transição | Ponta A | Ponta B |
|---|---|---|
| ideia madura vira trabalho | status da ideia muda para aprovada, com data e motivo | tarefa rastreável criada na fonte de estado |
| decisão que gera trabalho | decisão registrada com motivo | tarefa derivada no estado |
| projeto novo entra | memória do projeto (**handoff ao dono**) | linha em **cada** índice que a natureza obriga |
| índice de memória misturado migra | snapshot datado preservado | memória com ponteiro único (**handoff ao dono**) |

Par declarado impede fechamento isolado: as duas pontas fecham juntas ou nenhuma fecha. **Meia
transição declarada concluída é falha, não observação.** Ponta cujo destino é a memória fecha em
`HANDOFF_DECLARADO`, com dono nomeado — o par se dá por fechado quando a **entrega ao dono** está
registrada, não quando o byte apareceu; alegar `VERIFICADO` sobre escrita que este Departamento não fez
é evidência inventada.

**Concluído quando:** nenhuma transição emparelhada da rodada tem uma ponta só, e cada ponta de memória
fechou como handoff com dono resolvido.

## 7. Fonte única, view derivada, snapshot e destilação

Antes de gravar, declarar o **papel do artefato**. Os valores do enum são do
[schema](../schemas/departamento-registros.schema.json); o que cada um obriga é isto — e cada um tem
método próprio de detecção, porque declarar "é derivado" sem dizer **de que tipo** deixa o gate sem ato
a executar:

| Papel | Regra | Como se detecta divergência |
|---|---|---|
| `fonte` | único artefato gravável do fato; toda escrita vai aqui | comparação do baseline antes da escrita |
| `view_regeneravel` | derivada por regeneração determinística; **nunca** editada | regenerar da fonte e comparar (diff ou hash) |
| `view_manual` | deriva de uma fonte, mas **nenhum gerador a regenera**: alguém a mantém à mão e por isso ela diverge em silêncio | comparar **fato a fato** o valor anunciado com o valor medido na fonte; não há regeneração a executar, e fingir que há é gate tautológico. É a **única** categoria derivada que recebe escrita direta como conserto legítimo |
| `destilacao` | consolidação curada que linka de volta; não é recalculável | conferir presença, ponteiro à fonte e data — **não** o conteúdo; a limitação é declarada, não escondida |
| `runtime_gerado` | sobrescrito pelo deploy; nunca editado à mão | paridade por digest contra a fonte |
| `snapshot` | cópia congelada, datada e rotulada; nunca lida como atual | conferir rótulo e data; apresentá-lo como atual é falha nomeada |
| `index` | aponta para registros; não guarda o fato | biunivocidade índice ↔ artefato, nos dois sentidos (§8) |

Em alvo desconhecido, **nenhum par fonte × view é presumido**: descobrir e declarar antes de gravar,
com o ato que confirmou cada ponta. Perfil de outro projeto não vale por analogia, e perfil descoberto
uma vez não vira caminho chumbado — toda linha herdada é **hipótese a reconfirmar em runtime**.

**Concluído quando:** todo destino tocado tem papel declarado e, quando não for `fonte`, a fonte
correspondente resolvida — e nenhuma view foi editada onde havia de onde regenerá-la.

## 8. Indexação e orfandade

Para cada registro gravado, responder antes de fechar: **que índices, hubs e mapas precisam citá-lo**;
se algum é verificado **mecanicamente** e se a verificação foi executada; e se a entrada de histórico do
índice tocado está datada.

Um alvo costuma ter os dois regimes, e a diferença importa porque só um reprova sozinho: obrigação
**mecânica** é a que um script existente valida e cuja saída se anexa; obrigação por **convenção** é a
que só a disciplina cobra — e é exatamente onde a orfandade acontece. As duas **obrigam igual**; só a
primeira pode ser alegada como reprovação objetiva.

Dois estados de defeito, simétricos e com métodos distintos:

- **`REGISTRO_ORFAO`** — o registro existe e o índice não o cita. Parar no índice mais óbvio é
  orfandade adiada: o hub anda e o secundário não, e ninguém detecta.
- **`INDICE_ADIANTADO`** — o índice cita e o registro não existe. Sentido inverso da mesma
  biunivocidade, e por isso **método próprio**: testar em disco o artefato que cada linha cita.
  Reaproveitar a evidência do outro sentido deixa este sem ato.

Os dois **bloqueiam o fechamento** e são reportados como gates de integridade —
[protocolo](protocolo-registros.md), §3.

**Concluído quando:** todos os índices exigidos foram listados e conferidos um a um (ou pelo script,
com a saída anexada), cada entrada tocada está datada, e nenhum registro está órfão nem adiantado.

## 9. Convenção declarada e ADR por escopo

Convenção **nunca se improvisa em silêncio**: declarar antes de gravar, com a fonte de onde veio e o
nível de canal dessa fonte, e registrar a declaração quando for a primeira do escopo.

**Procurar o precedente vale para o endereço e para o valor.** Antes de cunhar um valor de campo — um
rótulo de status, um termo de frontmatter, uma categoria —, buscar precedente no histórico do destino e
**nomear no próprio ato os valores concorrentes encontrados**, ou declarar que a busca não achou
nenhum. Escolher entre dois termos concorrentes é ato de Jeremias; **nomear que os dois existem** é
obrigação de quem roteia, custa uma linha, e é o que separa uma escolha declarada de uma convenção
improvisada.

**Frontmatter** é medido **no destino**, antes do primeiro registro de uma família nova — a mesma
exigência que o ADR tem para local e numeração. Famílias com esquema próprio são respeitadas, não
uniformizadas por reflexo.

**Histórico e links:** o gate é a **data**, não o estilo. Entrada sem data reprova; divergência de
estilo entre famílias se reporta como achado, e não se "conserta" de passagem em nota alheia. Registro
novo entra na malha **por link**, na forma que o destino usa.

**ADR por escopo.** O conteúdo do ADR pertence à lente de arquitetura; o **local e a numeração**
pertencem a este Departamento:

1. procurar, no escopo-alvo, uma série já existente **antes** de escrever, e registrar o ato da busca;
2. existindo, continuar exatamente o padrão encontrado — pasta, prefixo, largura do número,
   capitalização, campos — sem "corrigir" a série alheia de ofício;
3. não existindo, **declarar a convenção antes** do primeiro ADR e registrar a declaração como
   convenção durável;
4. não misturar séries de escopos diferentes no mesmo diretório; divergência entre séries é fato
   registrado, não conflito a unificar sem decisão de Jeremias.

**A série desta estrutura é global**, e é o precedente que este Departamento aplica a si mesmo:
`adr-001` (CEO) → `adr-002` (Juízes) → `adr-003` (Auditoria) → `adr-004` (Evolução) →
[`adr-005`](adr-005-quatro-agentes-e-relatorios-de-registros.md) (Registros), cada arquivo na pasta do
dono da decisão. Quem escrever o próximo procura o **maior número em uso na estrutura inteira**, não no
próprio pacote.

**Concluído quando:** toda convenção usada na rodada tem fonte declarada e ato de busca registrado, e
nenhum valor, local ou número foi cunhado sem procurar precedente.

---

Relacionado: [SKILL](../SKILL.md) · [CONTRATO](../CONTRATO-DE-COMPROMISSO.md) ·
[protocolo de registros](protocolo-registros.md) ·
[ADR-005](adr-005-quatro-agentes-e-relatorios-de-registros.md) ·
[origem da migração](origem-migracao.md)
