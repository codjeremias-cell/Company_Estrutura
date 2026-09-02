# ADR-022 — o critério que pergunta se o pacote melhora alguma coisa

- **Estado:** **DECIDIDO** por Jeremias em 2026-08-05 · **AINDA NÃO EM VIGOR**
- **Decidido por:** **Jeremias**, em 2026-08-05, ao mandar executar a troca nas duas direções entre
  o Catálogo e a Estrutura — *"vamos executar as trocas… todas elas"*.

  **DECIDIDO NÃO É O MESMO QUE EM VIGOR.** Este ADR altera o conjunto de critérios que os Juízes
  recebem. Só entra em vigor por candidato julgado — `EXECUTIVE_MISSION` à Evolução, ~~alteração no
  schema~~ **declaração na `CRITERIA-MATRIX.json` da campanha e coluna nova no
  [`REGISTRO-DE-VEREDITOS.md`](../../../REGISTRO-DE-VEREDITOS.md)**, julgamento com duas instâncias
  por lente. Até lá, as campanhas seguem com os critérios que seus contratos declararem.

  > **Correção de 2026-08-23 — a receita original apontava um mecanismo que não existe, e o erro é
  > deste ADR.** *"Alteração no schema"* pressupõe que o schema dos Juízes enumere critérios. Ele
  > **não enumera**: medido hoje, `departamento-juizes.schema.json` tem **27 `enum`** e **nenhum**
  > lista `C01`…`C06` ou `CRIT-01`…`CRIT-08`; não existe `$defs/criterion`. O `criteriaMatrix` é
  > **genérico** — `criterion_id` é identificador livre. Os critérios são declarados **por campanha**
  > (21 `CRITERIA-MATRIX.json` na árvore) e consolidados na tabela do `REGISTRO-DE-VEREDITOS.md`.
  > Quem seguisse a receita ao pé da letra procuraria no schema uma lista que nunca esteve lá, e
  > concluiria que o passo estava feito por não achar o que alterar. A frase riscada fica visível
  > porque receita que some não deixa ver que existiu.
- **Origem:** investigação de 2026-08-05 sobre por que o Catálogo alcança 9,3–9,6 e a Estrutura
  trava. Ver `ceo-maestro/evals/` e o `PADRAO-DE-AUTORIA.md` §11 do Catálogo.

> ### ⚠️ `C07` era um nome ambíguo — o critério virou `C-EF` em 2026-08-23
>
> **Este bloco fica.** O renome tirou a ambiguidade do futuro, não do passado: dezoito dias de
> campanhas, ADRs e ledger escrevem `C07` querendo dizer o **pacote**, e quem ler aquilo precisa
> saber por quê. As ocorrências abaixo são as únicas de `C07` neste documento, e todas são
> pacote.
>
> **Como CRITÉRIO** (este ADR): o sétimo critério de julgamento, *Efeito demonstrado*.
> **Como CODINOME DE PACOTE** (`ADR-016`, campanhas T71/T87/T88): o candidato `C07` é o
> `departamento-arquitetura-software`, materializado como **LF** — e `C01`…`C12` ali são pacotes,
> não critérios. Os dois usos convivem **na mesma pasta `references/`**: o `ADR-016` escreve
> *"C01 `ceo-maestro`"* e *"C06 `departamento-arquitetura-dados`"* (pacotes) três parágrafos ao lado
> de onde este ADR escreve *"`C01` contrato · `C06` limites"* (critérios).
>
> **Consequência já observada:** a campanha `ceo-maestro/evals/medida-c07-t88-2026-08-15/` tem nome
> que sugere *"medida do critério C07"* e é **medida do pacote C07** — CRIT-03 e CRIT-05 sobre o
> `departamento-arquitetura-software`. Ela **não** é a remedição que o `A22-03` pede, e foi lida
> como tal na primeira passagem de 2026-08-23.

---

## O achado

**A Estrutura produz medida de efeito e não a consome.**

- **Produz:** `ADR-004` do `departamento-evolucao-skills`, decisão 7 — *"Admissão só com
  vermelho→verde executado. Nenhum candidato é recomendado sem o placar **baseline × pós-skill**
  rodado."* Medido em 2026-08-05: **15 de 15** pacotes têm `PLACAR.md`; **14 de 15** trazem
  baseline; **7 de 15** trazem as colunas de comportamento `acionou` / `aderiu`.
- **Não consome:** dos seis critérios de 2026-08-04 (`C01` contrato · `C02` schema · `C03` trava
  com prova · `C04` evidência · `C05` uso pela cadeia · `C06` limites), e dos oito de 2026-07-29,
  **nenhum pergunta se o pacote melhora o resultado**. O mais próximo, `C05`, mede **integração** —
  se a cadeia atravessa —, não **delta**.

O placar existe como artefato e é julgado pela sua **honestidade** (`CRIT-06` de 2026-07-29:
*"distingue PASS/FAIL/SKIP, não transforma ausência em sucesso"*), **nunca pelo seu resultado**.

> **O gate não tem porta de entrada para *"isso melhorou alguma coisa?"*.**

## A decisão

Passa a existir o critério **`C-EF` — Efeito demonstrado**, dono `robustez-e-evidencia`:

> O pacote demonstra **vermelho → verde executado**: existe caso em que, **sem** o pacote, o
> resultado falha, e **com** o pacote, passa — com a falha do baseline observada, não suposta.
> Contorno é defeito do pacote. Caso em que o baseline **já passa** não conta como efeito: conta
> como **redundância**, e redundância é achado.

| como falha | |
|---|---|
| placar sem baseline executado | o efeito é alegado, não medido |
| baseline que já passa | o pacote é redundante naquele caso |
| `acionou` / `aderiu` ausentes | mede-se o texto, não o comportamento |
| caso não-discriminante não declarado como tal | número que não separa, publicado como se separasse |

**Herdado do `PADRAO-DE-AUTORIA.md` §11 do Catálogo**, item a item — inclusive a trava de
redundância (*"se o baseline já passa sem a skill, a skill é redundante — não crie"*) e as duas
colunas de comportamento.

## O preço, medido e declarado ANTES de decidir

**Este ADR baixa notas. Ele não sobe nenhuma.**

Com agregação por **MENOR**, acrescentar critério só pode **baixar ou empatar** o `minimum_score` —
nunca subir. Medido sobre os nove departamentos em 2026-08-05: mínimo atual **6**; com um sétimo
critério, o mínimo é **6 ou menos**, jamais mais.

E o `ADR-014` é duro com quem não tem material: *"critério sem nota **proíbe** qualquer veredito
positivo e abre lacuna"*. Hoje **1 de 15** (`departamento-qa-usabilidade`) não tem baseline no
placar; **8 de 15** não têm as colunas de comportamento. Sem material, o `C-EF` nasce como lacuna.

**Jeremias foi informado disso antes de decidir**, nestes termos: *"a troca não vai fazer skill
nenhuma subir de nota — o ganho é de verdade, não de número"*. A decisão foi tomada assim mesmo,
e é isso que este parágrafo registra.

## O que este ADR NÃO faz

- **Não muda a agregação.** Continua MENOR entre instâncias e MENOR entre critérios (`ADR-016`).
- **Não muda as bandas nem os níveis** do `ADR-014`.
- **Não torna o `C-EF` obrigatório em toda campanha.** Ele entra no conjunto disponível; cada
  contrato declara os critérios que usa, e critério fecha na origem (protocolo §1).
- **Não retroage.** Julgamento fechado não se reabre por causa dele.

## O que fica aberto

| id | limite | dono | condição de fechamento |
|---|---|---|---|
| `A22-01` | 8 de 15 pacotes sem `acionou`/`aderiu` no placar | `departamento-evolucao-skills` | as duas colunas passam a ser exigidas na produção do placar |
| `A22-02` | `departamento-qa-usabilidade` sem baseline | `diretor-de-lentes` | placar do pacote ganha baseline executado |
| `A22-03` | **piorou ao ser medido no corpus certo.** O piloto de 2026-07-26 mediu 5 de 9 (55%) em skills do **Catálogo**; em 2026-08-23, na **Estrutura**, é **2 de 11 (18%)** e num único pacote | `departamento-evolucao-skills` | medir de novo quando houver ≥ 2 pacotes com material; abaixo de ~55% o `C-EF` mede ruído, e 18% está bem abaixo |
| `A22-04` | quem executa o placar não é quem julga, e a lente `robustez-e-evidencia` **não executa** por contrato | `ceo-maestro` | manter o desenho de executor independente publicando saída crua, como na T19 |
| `A22-05` | a trava que impede preencher `acionou`/`aderiu` sem rodar existe em **1 de 16** validadores (`departamento-seguranca:1427`), e só **4 de 16** pacotes têm os campos — propagá-la sem mais seria vácuo em doze | `departamento-evolucao-skills` | a trava passa a valer onde os campos existem **e** decide-se se os campos passam a ser exigidos (duas metades, ver nota) |

**`A22-03` é o risco real deste ADR:** se o instrumento separa em 55% dos casos, um critério
construído sobre ele carrega essa imprecisão para dentro do veredito. O `ADR-016` já ensinou que
régua com folga maior que o degrau produz `NAO_DISCRIMINADO`, não decisão.


---

## Remedição de 2026-08-23 — não há o que instalar, e o `A22-03` não pôde ser medido como escrito

O `A22-03` manda *"medir de novo depois de `A22-01`"*. **`A22-01` não fechou** — em dezoito dias
nenhum pacote produziu material de efeito novo —, então a remedição foi feita sobre outra pergunta,
mais direta e que decide igual: **quantos pacotes têm hoje o vermelho→verde que o `C-EF` lê?**

### A medição

| o que | quando decidido | hoje, 2026-08-23 |
|---|---|---|
| pacotes na cadeia | 15 | **16** (`especialista-planejador` entrou) |
| sem baseline no placar | 1 de 15 | **2 de 16** |
| sem `acionou`/`aderiu` | 8 de 15 (53%) | **9 de 16 (56%)** |
| **com tabela `baseline` × `pós-skill`** | não medido em 2026-08-05 | **1 de 16** (só o `ceo-maestro`) |
| **casos que SEPARAM**, onde há material | 5 de 9 (55%) — corpus do Catálogo | **2 de 11 (18%)** — corpus da Estrutura |

**As duas últimas linhas são as que mudam a decisão, e a segunda é pior que a primeira.**

**Quinze dos dezesseis não têm o instrumento.** Nove declaram o baseline como *"NÃO — pendente"* no
próprio placar. O décimo sexto, o `ceo-maestro`, **tem** — tabela `| caso | origem | baseline sem
skill | pós-skill | acionou | aderiu |`, com um caso real (*falhou* → *passou*) e uma suíte
sintética de dez com coluna de observação do ganho.

**E nele o poder de separação é 18%, não 55%.** Dos 11 casos: **2 separam** (baseline falha, pós
passa), **6 são redundantes** (o baseline já passava — que o próprio `C-EF` define como achado, não
como efeito) e 3 saem de `parcial` para `passou`. O `A22-03` temia *"se seguir ~55%, o `C-EF` mede
ruído"*. **No corpus onde o `C-EF` vai julgar, não seguiu ~55%: caiu para 18%**, com n = 11 e um
único pacote — amostra pequena demais para concluir, grande demais para ignorar.

> **Correção do método desta própria seção, no mesmo dia.** Esta tabela chegou a dizer **0 de 16**,
> e a seção a interpretava como *"o instrumento não existe neste corpus — não em 56% dele, em
> 100%"*. **Era 1 de 16, e o que escapou era o único que importava.** O detector procurava a forma
> em prosa (`vermelho→verde`, `🔴`/`🟢`); o `ceo-maestro` registra o efeito em **coluna de tabela**.
>
> **O controle positivo não salvou — ele deu falsa segurança, porque veio do corpus errado.** Rodei
> o padrão contra o `PILOTO-2026-07-26.md`, ele casou 6 linhas, e eu li isso como prova de que o
> detector enxergava. Mas o piloto é material derivado do **Catálogo**, e a medição era sobre a
> **Estrutura** — exatamente o defeito que este ADR acusa no `A22-03` três parágrafos abaixo,
> repetido dentro do instrumento que o acusava. **Controle positivo tem de sair do mesmo corpus que
> se vai medir.**

### O que isso faz com o preço — e a correção de uma frase que esta seção chegou a conter

Jeremias foi informado, em 2026-08-05, de que *"8 de 15 não têm as colunas"* e decidiu assim mesmo;
essa proporção **continua exata** (9 de 16 hoje). Mas ela media as **colunas de comportamento**, não
o efeito.

> **Correção, no mesmo dia.** Este parágrafo chegou a afirmar que, com 0 de 16, o `C-EF` *"entrando
> hoje impede veredito positivo em toda a casa"* e que isso era *"preço materialmente maior que o
> aprovado"*. **Está errado, e o próprio ADR desmente três seções acima:** *"não torna o `C-EF`
> obrigatório em toda campanha… cada contrato declara os critérios que usa"*. Critério só proíbe
> veredito positivo **dentro do julgamento que o inclui**. Um critério disponível e não declarado
> não bloqueia ninguém. A frase saiu; o registro de que ela existiu, não.

**O que a medição realmente mostra é mais estranho que um preço alto: não há preço, porque não há
instalação.** Medido em 2026-08-23:

- o schema dos Juízes não enumera critério (27 `enum`, nenhum de critério, sem `$defs/criterion`);
- `rubrica-e-corte.md` define **bandas, níveis, agregação e corte** — e **nenhum critério**;
- o `protocolo-de-julgamento.md` fecha a questão: *"Critério fecha na origem. A gerente **nunca**
  cria, remove, reordena nem reescreve critério… Critério faltante exige novo pedido do Diretor"*;
- as 21 `CRITERIA-MATRIX.json` da árvore mostram critérios **escritos por campanha, com texto
  próprio** — na primeira delas, `C01` é *"o conteúdo normativo é idêntico nos 23"*, que nada tem a
  ver com *"`C01` contrato"*.

**Não existe "conjunto disponível" como artefato.** A frase deste ADR — *"ele entra no conjunto
disponível"* — descreve um lugar que não há. Consequência prática, e ela dissolve a pergunta que
manteve esta decisão parada por dezoito dias: **o `C-EF` não se instala em lugar nenhum; ele entra em
vigor sendo USADO** — no primeiro contrato de campanha que o declarar, emitido pelo Diretor.

Então não há escolha entre *"instalar agora e aceitar lacunas"* e *"fechar o material primeiro"*.
Há um fato: **a primeira campanha que declarar o `C-EF` colherá lacuna em 15 dos 16 pacotes**,
porque só o `ceo-maestro` tem o material — e mesmo nele o critério separa em 2 de 11 casos. O
critério é citável hoje; **utilizável em um pacote só, e ali com poder de separação de 18%** — e o
que muda isso é execução, não redação.

### O `A22-03` foi medido no corpus certo, e piorou

Os **55%** vieram de **9 casos de 3 skills do Catálogo**, sobre placares de **2026-07-19**, lidos
como evidência de segunda mão — o próprio piloto declara *"Li placares, não transcripts"*. **Eles
nunca disseram nada sobre os 16 pacotes da Estrutura**, que é onde o `C-EF` vai julgar.

**Agora há substituto, e ele é pior: 2 de 11 casos separam — 18%.** Medido em 2026-08-23 sobre o
único pacote da Estrutura que tem o instrumento (`ceo-maestro`): dois casos vão de *falhou* a
*passou*, **seis já passavam no baseline** — que o próprio `C-EF` classifica como **redundância, e
redundância é achado** — e três vão de *parcial* a *passou*.

**O `A22-03` previa o teste e o resultado reprova:** *"se seguir ~55%, o `C-EF` mede ruído"*. Não
seguiu 55%; caiu para 18%, com um terço da amostra do piloto e um único pacote. Nem é refutação, nem
é confirmação — é **amostra insuficiente apontando na direção ruim**, e a condição de fechamento
passa a ser *medir de novo quando houver pelo menos dois pacotes com material*.

**A leitura honesta:** se a única evidência de efeito que a Estrutura produziu em um ano de pacotes é
onze casos num só componente, dos quais seis mostram que o pacote não era necessário naquele caso,
então o `C-EF` não está pronto para pesar em veredito — não porque a ideia esteja errada, mas porque
o corpus não tem o que ele lê.

### Renomeado para `C-EF` em 2026-08-23 — a janela estava aberta e foi usada

A colisão descrita no topo estava **documentada em prosa**, e prosa não previne o erro que ela
descreve: foi assim que a campanha `medida-c07-t88` enganou a primeira leitura de 2026-08-23 mesmo
com o `ADR-016` à mão. O reparo por trava seria contorcido — teria de adivinhar quais `cNN` são
pacote e quais são critério, e reprovaria retroativamente campanhas legítimas.

**A saída limpa era o identificador, e a janela fechava sozinha.** Enquanto o ADR não entrava em
vigor, nenhum `JUDGE_REPORT`, `CRITERIA-MATRIX.json` ou linha do `REGISTRO-DE-VEREDITOS.md` citava o
critério — então renomear custava **zero migração**. Depois de em vigor, custaria reescrever
evidência julgada, que é o que esta casa não faz.

**Decidido e executado por Jeremias em 2026-08-23:** o critério passa a se chamar **`C-EF`**
(*efeito*), fora do espaço `C01…C12` que as campanhas usam para pacote e para slot de matriz.

**O tamanho do risco que se evitou, medido antes de renomear:** `C-EF` aparece **17.836 vezes em
3.889 arquivos** da Estrutura, e **todas** são o codinome do pacote — nos onze arquivos fora de
campanha datada, sem exceção (*"`C07` da rodada 7"*, *"`C07-lf`"*, *"sessão T71 C07"*). O critério
vivia em **um único arquivo: este**. Era uma agulha num palheiro de 17.836, e qualquer busca
ingênua por *"onde o C07 é usado"* devolveria o pacote.

**O que NÃO foi renomeado, de propósito:** as quatro ocorrências dentro do bloco de aviso no topo.
Ali `C-EF` é o pacote, e é justamente o que o aviso existe para distinguir.


### A causa raiz, e ela não é preguiça

O material não aparece porque **produzi-lo exige execução que ninguém autorizou**. O piloto já
nomeava isso na §7: a Fase 2 *"não pode rodar por leitura de artefato… exige execução nova… em
termos práticos, exige instâncias independentes — e a autorização para usá-las"*. E o
`departamento-seguranca` tem **trava em código** (`validate_workflow.py:1427`) que **reprova** se
algum caso declarar `acionou`/`aderiu` diferente de `NAO_MEDIDO` — exatamente para impedir que
alguém preencha as colunas sem rodar.

**Tornar a lacuna visível não cria a capacidade de fechá-la.** Essa era a aposta da recomendação
registrada no ledger em 2026-08-22 (*"tornar as 9 lacunas visíveis é o que faz o material
aparecer"*), e a medição de hoje a derruba: a lacuna já é visível em nove placares, escrita pelos
próprios autores, há semanas — e não produziu material nenhum. **O que falta é autorização de
execução, e ela é de Jeremias.**

> **Nota sobre a trava do `NAO_MEDIDO` — e por que propagá-la ingenuamente seria vácuo.** Ela
> existe em **1 de 16** validadores (`departamento-seguranca:1427`), e reprova quando um caso
> declara `acionou`/`aderiu` **diferente** de `NAO_MEDIDO`. Medido em 2026-08-23: só **4 de 16**
> pacotes têm esses campos em `evals/evals.json` — `arquitetura-dados` (16 casos), `desenvolvimento`
> (16), `design-ux-ui` (16) e `seguranca` (15) —, num total de **63 casos, todos `NAO_MEDIDO`**, e
> **nenhum** declarando outra coisa. Um pacote (`especialista-planejador`) nem tem `evals.json`.
>
> Ou seja: copiar a trava para os dezesseis a faria **vincular quatro e não dizer nada sobre doze**,
> porque guarda que só dispara quando o campo existe é inerte onde o campo não existe. `A22-05` tem
> portanto **duas metades**, e a segunda é a que morde: (i) a trava passa a valer onde os campos
> existem; (ii) decide-se se os campos passam a ser **exigidos** — e essa segunda é mudança de
> contrato do placar, não propagação de trava.
