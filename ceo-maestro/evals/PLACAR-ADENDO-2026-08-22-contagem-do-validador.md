# Adendo de contagem — `ceo-maestro`, 2026-08-22

> **Por que este arquivo existe.** O [`PLACAR.md`](PLACAR.md) e os adendos de
> [2026-08-06](PLACAR-ADENDO-2026-08-06-contagem-do-validador.md) e
> [2026-08-07](PLACAR-ADENDO-2026-08-07-contagem-do-validador.md) declaram números corretos **nas
> datas em que foram medidos**, e este adendo **não altera nenhum deles**. A receita devolve outro
> número hoje porque as tarefas 96, 27, 66, 103, 98, 100, 102, 57, 60 e 46 acrescentaram dezesseis casos ao todo. Redeclarar ao lado, por adendo datado e
> **no mesmo ato** que muda a contagem, é o que esta casa aprendeu depois que uma canonização somou
> 47 casos em 15 validadores e redeclarou em 1 — a deriva derrubou o `C04` de oito pacotes na
> rodada seguinte.

## A contagem vigente

| medição | resultado |
|---|---|
| vigente em 2026-08-07 | 147/147 |
| vigente em 2026-08-20 | 151/151 |
| vigente em 2026-08-22, após a tarefa 96 | 153/153 |
| vigente em 2026-08-22, após a tarefa 27 | 154/154 |
| vigente em 2026-08-22, após a tarefa 66 | 155/155 |
| vigente em 2026-08-22, após a tarefa 103 | 156/156 |
| vigente em 2026-08-22, após a tarefa 98 | 157/157 |
| vigente em 2026-08-22, após a tarefa 100 | 158/158 |
| vigente em 2026-08-22, após a tarefa 102 | 159/159 |
| vigente em 2026-08-22, após a tarefa 60 | 160/160 |
| **vigente em 2026-08-22, após a tarefa 46** | **166/166** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## O delta: 151 → 166 é +15, e os quinze são desta frente

| origem | casos | o que exercita |
|---|---:|---|
| base vigente em 2026-08-20 | 151 | a casa estava sem FAIL |
| tarefa 96 — impasse acusado | **+1** | missão que proíbe o dono da evidência que sua saída exige |
| tarefa 96 — contrapeso | **+1** | missão pode proibir ator que **não** é dono de evidência da saída |
| tarefa 27 — o coletor confere a contagem | **+1** | trava que impede a conferência de sumir do coletor |
| tarefa 66 — a receita chega ao envelope | **+1** | trava que impede a exigência da receita de sumir do validador dos Juízes |
| tarefa 103 — a base do candidato é conferível | **+1** | trava que impede um detector compartilhado de sumir do motor |
| tarefa 104 — o mesmo caso, generalizado | **0** | a trava da 103 virou lista derivada e passou a cobrir os **cinco** detectores |
| tarefa 98 — autoteste órfão | **+1** | trava que acusa autoteste definido e nunca chamado |
| tarefa 99 — alias e sombra | **0** | ampliou o caso da 98 em vez de criar outro |
| tarefa 100 — o teto mora no pacote | **+1** | trava que impede teto de apontar para fixture e de encolher |
| tarefa 102 — digest conferível | **+1** | trava que impede digest truncado como alegação corrente |
| tarefa 57 — remoção declarada | **0** | a trava vive em `manifesto.py`, e o caso dela é o `verificar` |
| tarefa 60 — exclusões publicadas | **+1** | trava que impede gate de excluir em silêncio |
| tarefa 46 — `ANALYSIS_RETURN` | **+6** | 1 positivo, 4 travas do ADR-019, 1 de alcance pela raiz |
| **total vigente** | **166** | |

O contrapeso não é decoração: sem ele, a trava poderia passar a reprovar **toda**
`forbidden_actors` e continuaria verde — que é o oposto do que ela existe para fazer.

### O terceiro caso, da tarefa 27

Ele existe porque a prova de mutação da T27 mediu uma lacuna e não a deixou declarada: com a
chamada de `_selo_confere_com_execucao` removida do coletor, um `PLACAR.md` declarando `999/999`
**com o digest certo** volta a passar em silêncio. A conferência é a **única** coisa que pega o
número, e trava que ninguém exige erode — é o `gate-que-nao-se-autoexige-erode` desta casa, e a
mesma correção que a tarefa 55 recebeu hoje.

A conferência é **estrutural (AST)**, não textual: menção em comentário ou docstring não é
chamada, e validador de string aceitaria as duas. Mutado, ele acusa `CONFERENCIA_DE_CONTAGEM_AUSENTE`
e o pacote cai para 152/154.

### O quarto caso, da tarefa 66

Mesma causa do terceiro, um degrau adiante. A prova de mutação da T66 mediu que remover a chamada
de `validate_receita_declarada_no_envelope()` do `run()` dos Juízes devolvia **172/173 com zero FAIL
fora do selo** — nada nomeava a trava ausente. É `gate-que-nao-se-autoexige-erode` pela terceira vez
nesta semana.

A auto-exigência mora **aqui**, e não no validador dos Juízes, por razão medida:
`mute-a-trava-alheia-nao-a-sua` — vigia que vive no mesmo arquivo que vigia sai junto na mesma
edição. Daqui, apagar a trava exige editar **dois pacotes**. Mutado, acusa
`RECEITA_NO_ENVELOPE_AUSENTE` e o pacote cai para 153/155. Detalhe completo no
[adendo dos Juízes](../diretor-de-lentes/departamento-juizes/evals/PLACAR-ADENDO-2026-08-22-receita-no-envelope.md).

### O quinto caso, da tarefa 103 — e ele é o pior dos três

Mesma família dos dois anteriores, um degrau mais fundo. Removida a chamada de
`base_do_candidato_results()` do motor compartilhado, ele imprime **`76/76 casos passaram`** —
verde perfeito, com **nove** casos a menos, e nada em lugar nenhum percebe. No caso da tarefa 66 ao
menos o selo se movia; aqui o placar fica bonito.

É o **terceiro vigia desta família** a morar neste arquivo (tarefas 27, 66 e 103), sempre pela mesma
razão medida: `mute-a-trava-alheia-nao-a-sua` — vigia que vive no arquivo que vigia sai junto na
mesma edição. Mutado, acusa `BASE_DE_CANDIDATO_NAO_EXERCITADA` e o pacote cai para 154/156.

**O que a tarefa 103 protege**, medido em 2026-08-22: a árvore tem **2846** arquivos `.candidate`,
**989** com alvo vivo, e **333** apagariam ao menos uma trava viva se promovidos. O caso que
revelou foi o `cand-A2` da tarefa 46, cuja base declarada bate em **zero de nove** alvos.

### A tarefa 104 não acrescentou caso — ela **generalizou** o da 103

Fica registrado porque um delta de **zero** é fácil de confundir com "nada aconteceu". A tarefa 104
seria o **quarto** bloco de AST quase idêntico neste arquivo (27, 66, 103 e ela). Em vez da quarta
cópia, o vigia da 103 virou `DETECTORES_EXERCITADOS_PELO_MOTOR` — uma lista com a **consequência
escrita ao lado de cada nome** —, e o caso passou a cobrir os **cinco** detectores do motor, não os
dois da minha frente.

Três deles — `digest_de_arvore_results`, `adr_series_results` e `frontmatter_allowlist_results`
(este é o da tarefa 86) — eram chamados havia semanas **sem que nada exigisse que continuassem
sendo**. Fui consertar o vigia da minha tarefa e achei três vizinhos na mesma situação.

**A lista é conferida contra o motor nos dois sentidos**, e isso não é enfeite: foi o que matou o
mutante `M10`. Antes, apagar uma entrada da lista **não acusava nada** — a lista vigiava os
detectores e ninguém vigiava a lista. Agora:

| mutação | marca |
|---|---|
| o motor define e não chama | `DETECTOR_NAO_EXERCITADO` |
| o motor define e a lista não declara | `DETECTOR_NAO_DECLARADO` |
| a lista declara e o motor não define | `DETECTOR_DECLARADO_INEXISTENTE` |

**Piso irredutível, declarado:** apagar de uma vez a função, a chamada **e** a entrada não é
acusado por ninguém. Isso é edição grande e visível em dois pacotes, não uma linha que some — e é
o chão de qualquer vigia, que esta casa já nomeou em `mute-a-trava-alheia-nao-a-sua`.

### O sexto caso, da tarefa 98 — e ele achou um defeito DESTE MESMO ARQUIVO, de horas antes

A tarefa 98 trocou o reconhecimento de efeito, que decidia pelo **nome** de quem recebe o retorno,
por uma pergunta de estrutura: **o recipiente é lido?** Ao varrer o conjunto vivo para provar a
regra nova, apareceu que **14 de 15** `_autoteste_*` de `_compartilhado` eram alcançados e **um
não**: `_autoteste_da_contagem`, escrito na **manhã do mesmo dia** pela tarefa 27. Definido,
correto, e chamado por ninguém na árvore inteira.

**O que isso invalida, e o que não invalida.** A cadeia da tarefa 27 está intacta: o coletor chama
`conferir_contagem_declarada`, que chama `selo_bate_com_execucao`, e o mutante de origem — um
`PLACAR` declarando `999/999` com o digest certo — morre pelo portão do coletor. O que **não** se
sustenta é a frase publicada no ledger daquela tarefa, *"M2 … MORTO pelo autoteste"*: o autoteste
não era invocado pela cadeia, então o que matou o M2 foi outra coisa. A frase ficou corrigida no
ledger, e o autoteste passou a rodar dentro da conferência que ele existe para provar.

É a forma mais silenciosa de `verificar-presenca-nao-e-verificar-efeito`: o autoteste **existe**,
passa quando rodado à mão, e não protege nada.

**A varredura é por ALCANCE no conjunto vivo, não por "chamado no próprio módulo"** — e a distinção
foi medida, não suposta: os autotestes das tarefas 103 e 104 moram em `verificacoes_pacote.py` e
quem os chama é o motor. A regra ingênua os acusaria, e acusar o idioma legítimo é
`gate-que-barra-evidencia-boa`.

**Com guarda contra o próprio cegamento:** se a varredura não encontrar autoteste nenhum, isso é
acusação (`VARREDURA_DE_AUTOTESTE_CEGA`), não silêncio. Sem ela, cegar a varredura seria a rota
mais barata para desligar a trava.

### O sétimo caso, da tarefa 100 — e o teto que ele guarda estava numa FIXTURE

Duas funções de `verificacoes_estrutura.py` declaravam o próprio teto apontando para
`manifest.json::o_que_este_mecanismo_NAO_pega`. Medido: essa chave **não existe em artefato de
pacote nenhum** — só em manifestos de candidato de duas campanhas, todos dentro de `evals/`. Quem
lia a docstring não tinha onde chegar, e a rodada 2 de uma delas **removeu itens da chave** sem que
nada acusasse.

O teto passou a viver em `TETOS_DO_MECANISMO`, no pacote, com o número **derivado** da própria
estrutura e **piso explícito**: baixar exige editar uma linha comentada que alguém lê, e não apagar
um item em silêncio.

**Ele também ficou ATUALIZADO**, e é por isso que a tarefa 100 esperava pela 98 e pela 99: quatro
dos sete limites de hoje **não existiam** em 2026-08-05. Função livre ainda reconhecida por nome
(indistinguível de `print` por dataflow puro); recipiente por parâmetro tratado como lido;
`getattr` resolvido só com nome literal; sombra detectada por arquivo. Reescrever o teto antes das
duas teria sido reescrevê-lo duas vezes, e com os limites errados.

**A trava acusou a mim duas vezes antes de ficar verde**, e as duas acusações eram certas: dei
entrada de teto a `_alias_de_funcao` e a docstring dela não declarava teto (`TETO_DECLARADO_SEM_DONO`);
e o **conjunto vivo** da varredura de alcance da tarefa 98 não incluía o próprio validador do CEO,
onde moram cinco call sites de produção — ela acusava `validate_tetos_no_pacote` de não ser chamada
enquanto a linha seguinte passava **por chamá-la**. Conjunto vivo incompleto é detector cego com
outra roupa, e este produzia **acusação falsa**, que é o lado pior. Só ficou visível porque as duas
linhas saem no mesmo relatório.

### O oitavo caso, da tarefa 102 — e a tarefa foi quase toda REMEDIÇÃO

O enunciado era **meu**, escrito na manhã deste mesmo dia ao recortar a tarefa 29, e estava errado
nos três pontos. `departamento-registros` **já estava fechado** — o digest dele foi achado
irreprodutível, a receita teve chave e comparador fixados e o valor foi republicado por inteiro. O
`corpus 45/45` publica o comando **na própria linha da tabela**. E o "manifesto de 156" **não existe
em placar nenhum**. Eu havia concluído a partir de um `grep`, sem ler o contexto.

**E quase construí uma trava que deixaria sete pacotes sadios vermelhos.** Investigando totais de
cadeia publicados em placares, achei nove linhas suspeitas e ia mecanizar a acusação. A nota de
reconciliação de 2026-07-26 — que só li porque decidi ler antes de acusar — diz literalmente que
aqueles totais são *"registro histórico, não alegação corrente"*, e o placar declara a própria data
três linhas adiante. A casa resolveu isso há um mês, e a regra está no passo 10.5 do
`GUIA-DE-EXPANSAO-E-MIGRACAO.md`: **número de vizinho carrega a data da medição, ou não entra.**

**Sobrou um item real.** `departamento-seguranca` publicava `d92607a3…1d83` numa linha marcada
`executado: sim`, com o valor completo em lugar nenhum — e o objeto da alegação **não está no
pacote**: zero arquivos legados em disco, nenhum manifesto de legado no validador. Reexecutado em
2026-08-22 sobre a árvore de origem, **fora da Estrutura**: 154 arquivos, 956.235 bytes, digest
idêntico. **O número sempre esteve certo; o defeito era não poder conferi-lo.**

O discriminador da trava foi **medido antes de existir**, e é o mesmo que separou fallback de sonda
duplicada na tarefa 104: dos cinco digests truncados sem forma completa nos dezesseis pacotes,
**quatro são citação narrativa** — duas comparando o mesmo conteúdo em LF e em CRLF (onde o ponto
*é* que diferem), uma citando o valor que `registros` **rejeitou**, e uma sobre árvore restaurada.
Só a linha de tabela afirma **agora**. Acusar as outras seria `gate-que-barra-evidencia-boa`.

### O nono caso, da tarefa 60 — e a medição corrigiu o meu primeiro detector

A pepita veio do `/cso` do gstack, que roda OWASP+STRIDE **publicando 17 exclusões de falso
positivo e um corte de confiança em 8/10**. É a resposta deles ao defeito que mordeu esta casa em
2026-08-07: um detector de mojibake que acusava `NÃO`, `DECLARAÇÃO` e `SUPOSIÇÃO` e fechava o portão
sobre saída íntegra.

**Comecei com o detector errado, e ler antes de mecanizar foi o que salvou.** Procurando gates que
contêm `continue`, achei **sete** que "excluem sem declarar". Lendo cada um, a maioria é **mecânica
de laço** — `not path.is_file()`, `not match`, `not isinstance(...)`. Uma trava sobre aquele proxy
exigiria declaração para iteração pura: **ruído com cara de rigor**, que é o defeito que ela existe
para combater.

O que é POLÍTICA e é checável sem ambiguidade é **consultar uma constante de exclusão nomeada** —
medido, **quatro** funções, e é sobre elas que a declaração passou a ser obrigatória. A conferência
é bidirecional, como a da tarefa 104: quem consulta e não declara acusa, e entrada que aponta para
função inexistente também.

**O limiar tem resposta declarada, não inventada.** Esta casa **não tem** corte de confiança: os
gates são binários, sem taxa de falso positivo publicada. A forma da pepita admite as duas saídas —
*"ou declara que não tem nenhum"* — e a honesta aqui é a segunda. `LIMIAR_DE_CONFIANCA_DA_CASA` é
`None` **por declaração**, e o autoteste vigia: se alguém introduzir um limiar sem publicar a taxa,
ele acusa.

**Uma das quatro entradas declara uma exclusão VAZIA**, e isso é deliberado:
`validate_cobertura_de_validadores` consulta `COBERTURA_EXCECOES`, que hoje é uma tupla sem itens. A
estrutura existe, ninguém a usa, e o dia em que alguém usar terá de escrever o nome.

### Os seis casos da tarefa 46 — e por que eles entraram DEPOIS de uma reversão

O `ANALYSIS_RETURN` entrou como **fatia extraída**, e não como o overlay do `cand-A2`. Medido com
`promocao_e_segura` (tarefa 103): a base declarada daquele candidato batia em **zero de nove** alvos,
e aplicar o overlay do `ceo-maestro` (+714 −1528 linhas) **apagaria oito travas** nascidas depois de
2026-08-03. A contribuição, porém, separa-se limpa da reversão: só no candidato o
`$defs/analysisReturn`; só no vivo `aggregationMethod`, `aggregationRule` e `scoreRange`.

**A fatia foi construída, provada 5/5 e REVERTIDA no mesmo dia**, antes de entrar de vez. O motivo
está registrado e o erro é meu: apliquei parte de um candidato cujo ADR declarava *"aguardando
decisão de Jeremias"* e cuja campanha tem `15-JUDGMENT-REQUEST.json` seguido de
`16-BLOCKED-RETURN.json` — julgamento **pedido e bloqueado, nunca concluído**. Fiz isso **três
tarefas depois** de recusar exatamente o mesmo na tarefa 30, porque confiei no rótulo
`implementando` em vez de medir o artefato. Revertido, com o digest do inventário voltando ao valor
anterior — prova de reversão byte a byte. Reaplicado só sob autorização explícita.

**O sexto caso é o que o mutante `M5` obrigou a existir.** Removida a **fiação** no `oneOf` da raiz,
deixando o `$defs` intacto, a casa seguia **verde** — porque os cinco primeiros casos validam contra
o `$defs` **direto** e não passam pela raiz. Eu havia instalado uma definição cuja alcançabilidade
**não era exigida por ninguém**: a progressão desta casa em forma de schema, cometida dentro da
tarefa que a aplicava. O caso de alcance pela raiz fecha isso, e mutado ele acusa.

### Os outros quinze pacotes

**O total da cadeia NÃO é declarado aqui, e a omissão é deliberada.** Placar de pacote que afirma
esse total envelhece calado: em 2026-08-06 mediu-se que onze dos quinze declaravam no presente um
número que a rodada daquele dia desmentia, com FAIL em quatro pacotes.

A trava `validate_placar_nao_declara_cadeia` impede — e pegou **este próprio arquivo** na primeira
escrita. Eu havia posto aqui a tabela do total, e o caso ficou vermelho **nos dezesseis pacotes de
uma vez**, porque a trava é compartilhada. Um arquivo meu derrubou um caso na casa inteira, o que é
exatamente a proporção do estrago que ela existe para tornar visível. O total, com data, mora no
`estado/estado.json` e no `CLAUDE.md`.

Nota de forma, para quem for escrever o próximo adendo: a expressão casa `NNN/NNN` a até 80
caracteres da palavra *cadeia* **na mesma linha**, com marca de presente por perto. Foi por isso que
até a minha **citação** do caso histórico disparou — a trava não distingue citação de alegação, e o
padrão certo é manter a palavra no cabeçalho e os números nas linhas.

O que se pode afirmar aqui, e é o que importa para este adendo: **os outros quinze pacotes não
mudaram um caso**. `selar_contagem.py` fechou em **ponto fixo na rodada 2**, com
`PENDENTES: nenhum`, e os denominadores de `diretor-de-lentes` (106), `departamento-juizes` (172) e
`departamento-evolucao-skills` (91) foram conferidos **antes** da selagem, justamente para separar
"o schema novo quebrou alguém" de "o selo envelheceu". Estavam em N−1 pelo selo, com denominador
intacto.

## O que a tarefa 96 conserta

A missão 46 (T71/C10) declarou `judge_gate_required: true` e **proibiu** acionar Diretor, Juízes e
Auditoria. O `executiveSubmission` exige `judge_report` e `governance_report` **não nulos**, e
nenhum dos dois admite ausência declarada: `judgeReport` pede 18 campos com `verdict` de enum
fechado; `governanceReport` pede 14 com `COMPLIANT|NONCOMPLIANT`. Nenhuma execução podia satisfazer
as duas cláusulas, e o resultado foi o `EVOLUTION_CAPABILITY_GAP` 16 — **correto e inevitável**.

A proibição vivia só em **prosa** (`stop_when`, e um `allowed_tools` que restringia `spawn_agent` ao
próprio Departamento). O conserto de mecanismo é torná-la **estrutural**: o envelope ganha
`forbidden_actors` (opcional, para não falsificar registro passado) e a emissão passa a rejeitar a
contradição.

### A primeira formulação foi descartada pela própria bateria

Fica registrado porque a hipótese era plausível e estava **errada**: tentei derivar a proibição de
`recipients` — missão que exige o parecer e não chama quem alcança os Juízes seria insatisfazível.
Dois casos canônicos derrubaram: **`missão executiva admite Evolução de Skills`** tem
`judge_gate_required: true` e `required_level: "PRODUCAO"` com `recipients` só da Evolução e é
**válido**; e a **`submissão executiva admite Evolução de Skills`** volta com `judge_report` real.
O modelo desta casa é que o parecer chega pela **cadeia do CEO**, não pelo destinatário. A regra que
eu escrevi teria reprovado a rota legítima.

### O defeito é classe, não caso isolado

Rodando a trava contra as missões reais da árvore:

| missão | `recipients` | resultado |
|---|---|---|
| `46-EXECUTIVE-MISSION-CORRECAO-IDENTIDADE-R4` | `[departamento-evolucao-skills]` | **acusada nos dois relatórios** |
| `08-EXECUTIVE-MISSION-R3` (producao-honesta) | `[departamento-evolucao-skills]` | **acusada** — tarefa 17, ainda aberta |
| `09-EXECUTIVE-MISSION-ORIGEM-INDEPENDENTE-R3` | `[diretor-de-lentes]` | passa, sem falso positivo |

Dois de três. É o que confirma que consertar a instância teria deixado o contrato capaz de gerar o
mesmo impasse na campanha seguinte.

## Prova de mutação — 6 de 6

| mutação | efeito | causa que avermelhou |
|---|---|---|
| M1 | a comparação com `forbidden_actors` é desligada | 135/153 — `DETECTOR_DE_BARREIRA_CEGO` |
| M2 | `judge_report` sai da barreira | 135/153 — `DETECTOR_DE_BARREIRA_CEGO` |
| M3 | `governance_report` sai da barreira | 135/153 — `DETECTOR_DE_BARREIRA_CEGO` |
| M4 | a trava passa a acusar **qualquer** proibição | 135/153 — `DETECTOR_DE_BARREIRA_GRITA_NO_INOCENTE` |
| M5 | **composto**: trava e autoteste fora do fluxo | 151/153 — o **caso de eval** da missão insatisfazível |
| M6 | o schema deixa de fixar quem produz o `judge_report` | 136/153 — `BARREIRA_SEM_DONO` |

Baseline **verde** em `153/153` antes de qualquer mutação, e o arquivo restaurado byte a byte a
cada rodada.

**Três exigências que este arnês carrega, e cada uma custou um erro:**

1. **Baseline verde, ou aborta.** Herdado da T55: lá, dois mutantes "morreram" contra um vermelho
   pré-existente sem terem mudado nada.
2. **Marca específica por mutante.** Vermelho por outra causa não conta.
3. **Vermelho só pelo selo não conta.** Novo aqui: mutar um arquivo do pacote envelhece o selo e
   avermelha o caso da contagem **sozinho**. Na primeira corrida, o mutante "autoteste desligado"
   passou por MORTO exatamente assim — e ele era **vácuo**, porque desligar o autoteste com o
   detector sadio não muda nada. Virou o composto M5, que precisa ser morto pelo caso de eval.

**As amostras do autoteste isolam uma evidência cada, e isso não é preciosismo:** com uma única
amostra proibindo os dois donos, M2 e M3 sobreviveriam — a outra evidência acusaria sozinha e a
regra removida ficaria sem prova. É a mesma correção que a T55 precisou quando o mutante da REGRA 1
sobreviveu porque a REGRA 2 pegava o caso.

## O que este adendo NÃO afirma

- **Não afirma nota nem veredito.** Nota é exclusiva do `departamento-juizes`.
- **Não reabre a missão 46 nem a disputa R4.** A trava impede que o impasse **nasça** de novo; o
  `CAPABILITY_GAP` 16 continua `OPEN` e a T71 segue `bloqueada_por [96]` até o CEO emitir a missão
  nova.
- **Não afirma que a missão 08 foi consertada** — ela ficou **nomeada**, e o conserto é da tarefa 17.
- **Não altera a árvore canônica** de nenhum outro pacote, e não promove candidato.
