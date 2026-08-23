# ADR-018 — Uma trava só está provada em três eixos, e o terceiro é a documentação

- **Estado:** **aceito** — vinculante
- **Data:** 2026-08-01 · **decidido em:** 2026-08-03
- **Decidido por:** **Jeremias**, em 2026-08-03, ao autorizar a canonização do
  `cand-K-extracao-terminada-por-recomputacao` sob a **regra de parada** que ele fixou, ciente do
  veredito **`REPROVED`, `minimum_score 4`, `critical_fail: false`** da rodada 9 e dos limites
  declarados. Registro em
  `ceo-maestro/evals/compliant-porta-unica-2026-08-01/179-FECHAMENTO-DA-TAREFA-15.md`.

  **Limite deste ADR, medido e declarado:** o terceiro eixo — a documentação — foi provado
  redutível. A rodada 9 mediu que **o eixo E é tipado**: uma promessa reescrita com outras
  palavras atravessa a varredura, e o caso `B2` executou isso. O ADR permanece vinculante no que
  exige; não permanece suficiente no que promete.
- **Contexto normativo:** [../../../../../regras-de-ouro/REGRAS-DE-OURO.md](../../../../../regras-de-ouro/REGRAS-DE-OURO.md)
- **Substitui:** nada. **Complementa:** [ADR-017](adr-017-inspecao-em-papel-sob-porta-unica.md).

## Contexto — o mesmo defeito, descido três níveis

Esta base mediu, em três frentes seguidas, a mesma pergunta mal respondida: **a verificação
conferia a presença do mecanismo, não o efeito dele.** E cada correção herdou a forma do defeito
que veio corrigir, um nível abaixo.

| frente | a trava existia | o que a verificação conferia | o que escapou |
|---|---|---|---|
| tarefa 14 | sim | que a função existia e ficava vermelha sob mutação | **nenhum call site no fluxo real** — protegia o eval, não a operação |
| tarefa 15, rodada 1 (`A2`) | sim, com call site | que o **nome** da trava aparecia entre as chamadas do emissor | manter a chamada e **descartar o retorno**: `COMPLIANT` com zero âncoras, validador 118/118 verde |
| tarefa 15, rodada 1 (`A1`) | sim, chamada corretamente | que a chamada estava no fonte | a **instrução de uso publicada** ensinava a invocação que passava por fora dela |

O `A1` é o que obriga este ADR. Não houve defeito de código: a conferência de identidade existia,
tinha call site e ficava vermelha sob mutação. O `SKILL.md:215` publicava
`emitir_governanca.py <pasta-da-rodada> <raiz-auditada>` — dois argumentos — e a conferência morava
atrás de `if raiz_do_candidato is not None`, com a raiz vindo de um **quarto** argumento que
nenhuma prosa do pacote mencionava. Medido pelos Juízes, com `candidate_digest` falso: quatro
argumentos → `NAO_EMITIU` exit 2; **três, os documentados → `COMPLIANT` exit 0, gravando
`sha256:ffff…`**.

A trava estava certa. O caminho que o operador percorre é que passava ao lado dela.

## Decisão

**Uma trava só é dada por provada quando os três eixos abaixo têm saída executada. Os três, não
dois.**

### Eixo 1 — mutar a trava fica vermelho

O que a base já exigia. Desligar a trava, ou desligar o encadeamento que a liga à decisão, tem de
produzir vermelho na prova de mutação, **e pela razão que a mutação declara mirar**. Cada mutação
declara a razão esperada, e o harness só marca vermelho quando ela aparece na saída — vermelho pela
razão errada é verde disfarçado.

### Eixo 2 — o RESULTADO da trava é consumido por quem decide

Ser invocada não basta. O valor devolvido pela trava tem de ser o que alimenta a decisão, e isso é
conferido por **fluxo de dados**, ligando atribuição a uso — não por presença de nome na AST. Uma
sonda que mantenha a chamada e descarte o retorno fica vermelha, e essa sonda entra nos casos
obrigatórios do validador.

### Eixo 3 — o caminho DOCUMENTADO passa por ela

**A documentação de uso faz parte da trava**, porque é o caminho que o operador de fato percorre.
Em consequência:

1. toda invocação publicada — `SKILL.md`, protocolo, ADR, docstring do próprio programa — tem de
   ser uma invocação que o programa aceita **e** que aciona as travas;
2. o validador do pacote **extrai** as invocações publicadas e as confere;
3. o validador **executa** a invocação documentada contra uma entrada que ela deve barrar, e exige
   que barre — com o par de controle, mesma entrada e um campo trocado, exigindo que **não** barre;
4. nenhuma fonte publicada pode afirmar garantia que a medição desmente.

O item 4 é conferência de texto, e texto é instrumento fraco para provar comportamento. Aqui o
objeto medido **é** o texto publicado — usar AST para isso seria medir a coisa errada.

## Regra de leitura das mutações verdes

**Mutação verde não é aprovação: é pergunta em aberto.** Toda mutação que sair verde é investigada
até a causa, e o desfecho é registrado como um destes três:

- **trava morta** — a mutação deveria ter sido pega e não foi; é defeito, e vira correção;
- **caso errado** — a mutação não exercita o que declara exercitar; é defeito do instrumento;
- **defesa em profundidade declarada** — a mutação é pega por outra camada, e isso é registrado com
  o nome da camada que pegou.

Nenhum dos três é "passou". Na rodada 1 desta frente, investigar as verdes rendeu mais achado que
investigar as vermelhas.

## Alternativas consideradas

**Manter dois eixos e revisar a documentação à mão.** Recusada: é a forma de aviso em prosa que já
falhou nesta base — a armadilha documentada repetiu quatro vezes antes de virar código. Documentação
revisada por atenção humana volta a divergir do código na primeira pressa.

**Gerar a documentação a partir do código.** Recusada por ora: resolveria o `A1`, mas a `SKILL.md`
tem função didática que geração automática não cumpre, e a troca não estava em escopo. O que se
adota é o inverso barato — o código **lê** a documentação e reprova a divergência.

## Consequências

**Positivas.**

1. A invocação publicada e a invocação protegida deixam de poder divergir em silêncio.
2. O verde do validador passa a significar "a trava decide", e não "a trava foi mencionada".
3. Cada vermelho carrega a razão que a mutação mirava, o que fecha "teste que passa pela razão
   errada" dentro da própria prova de mutação.

**Negativas, declaradas.**

1. **O eixo 3 não alcança o que não está publicado.** Se alguém operar por um caminho que nenhuma
   fonte do pacote documenta, nada aqui pega.
2. **O eixo 2 confere fluxo dentro deste emissor.** Quem editar o emissor e o validador na mesma
   passada derruba os dois. O que se ganha é que a queda deixa de ser silenciosa: exige uma segunda
   edição, no laço principal do validador, e a prova de mutação a exibe. **Não é prova de
   impossibilidade.**
3. **Custo de manutenção.** Mudar a linha de comando publicada passa a ser mudança que reprova o
   validador até a documentação acompanhar. É o efeito desejado, e é atrito real.

## Verificação

- `evals/validate_workflow.py::validate_call_site` — eixo 2, por fluxo de dados.
- `evals/validate_workflow.py::validate_identidade_nao_opcional` — a conferência de identidade não
  pode voltar a depender da aridade de `argv`.
- `evals/validate_workflow.py::validate_documented_usage` — eixo 3, extração das invocações
  publicadas.
- `evals/validate_workflow.py::validate_caminho_documentado_executado` — eixo 3, **executado**: o
  comando publicado, com `candidate_digest` falso, tem de barrar; com o correto, não pode barrar.
- Prova de mutação da rodada 2:
  `ceo-maestro/evals/compliant-porta-unica-2026-08-01/16-PROVA-DE-MUTACAO-R2.md`.
- Matriz dos três eixos, trava a trava:
  `ceo-maestro/evals/compliant-porta-unica-2026-08-01/18-TRES-EIXOS-POR-TRAVA.md`.

## Fronteiras que esta decisão NÃO cruza

- **A porta única fica.** Nada aqui transforma os 81 `SKILL.md` aninhados em skills invocáveis.
- **A nota continua dos Juízes** (ADR-003 intacto), e a faixa do ADR-014 não foi tocada.
- **Nenhuma exigência existente foi afrouxada.** As travas da rodada 1 permanecem, e as do ramo
  `COMPLIANT` só cresceram.
- **A análise de fluxo de dados marca por MENÇÃO, e este é o limite nomeado.** `validate_call_site`
  prova que o valor decisivo **não está desligado** da origem — que o nome que decide descende, por
  alguma cadeia, do retorno da trava. Ela **não** prova que o valor seja *função* daquele retorno:
  um nome que mencione a origem e a ignore no conteúdo satisfaz a marcação. A sonda
  `S02-ALIAS-ESTADOS` preserva a cadeia e troca o conteúdo.

  **Correção da rodada 4, e ela retira uma frase.** Até a rodada 3 este item terminava com
  *"quem a barra é o gate de schema `anchors_total`, não o fluxo. Defesa em profundidade existe"*.
  **Três medições independentes desmentiram isso**: os Juízes mostraram que o gate `anchors_total`
  **não** barra a forma interprocedural, porque os números fabricados pelo intermediário são
  internamente consistentes — `anchors_total: 12` passa em `minimum: 10`. A defesa alegada não
  existia; o limite de marcação estava bem declarado, e foi só ele que sobreviveu à medição.

  **O que existe agora, e é outra coisa.** A defesa não é mais o gate de schema, e não é mais
  vigilância de caminho — é `auditar_ledger_contra_evidencia`, que confronta o **artefato pronto**
  com os recibos em disco e refaz a conta. Vigiar caminho sempre admite mais uma função no meio;
  confrontar artefato com evidência não depende de por onde o valor passou. Provado pela mutação
  `M22-CONTAGEM-LAVADA` e pelo caso executado
  `o ledger emitido é confrontado com os recibos em disco`.

  **E há um limite novo, medido, que substitui a frase retirada.** A auditoria contra a evidência
  pega **número que diverge da evidência**, não a lavagem em si. Uma lavagem que fabrique o número
  *correto* atravessa — e escreve o valor verdadeiro, que é o desfecho inofensivo. Isso não é
  teoria: a primeira versão da `M22` plantava `anchors_total: 12` numa rodada com exatamente 12
  âncoras reais e **saiu verde**. Mutação verde é pergunta em aberto, e esta é a resposta.
- **O eixo 3 pode ficar NAO_CONFERIDO, e isso é um estado, não uma falha.** Uma trava cujo caminho
  documentado nenhum caso executado exercita declara `NAO_CONFERIDO` com razão, e o sumário imprime
  `NAO_MEDIDO` naquela posição. **Nunca `OK`.** Ausência de evidência permanece ausência, inclusive
  quando a ausência é do próprio conferidor.
- **Todo instrumento de prova precisa de um caso que o faça REPROVAR.** A matriz dos três eixos, a
  bateria de sondas, a prova de mutação e a varredura de afrouxamento têm, cada uma, pelo menos um
  caso executado que as faz acusar — e o instrumento que confere isso tem o seu. Instrumento que não
  pode acusar não sustenta alegação.
