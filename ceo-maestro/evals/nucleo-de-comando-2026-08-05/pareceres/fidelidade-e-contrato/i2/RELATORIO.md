# Parecer — `fidelidade-e-contrato`, instância 2 — núcleo de comando

- **Lente:** `fidelidade-e-contrato` (`C01` contrato e fronteira · `C02` schema e envelope)
- **Instância:** 2 — não vi a instância 1, não a procurei e não sei o que ela achou
- **Commit julgado:** `412769f31ccb0cb636f85c41f56cf9c6f612b3c1` (`412769f`, *"sela o rejulgamento do núcleo de comando, com os conflitos declarados"*)
- **Nível exigido:** `INTERNO`
- **Alvos:** `ceo-maestro`, `diretor-de-lentes`, `departamento-negocios`. **Não julguei** o `departamento-juizes` — sou agente dele.
- **Executei alguma coisa?** Não. Todo `PASS`/`FAIL` citado vem de `saida-crua/`.

> **Nota sobre o commit.** O `00-CONTRATO.md:5` sela a árvore `ee916c6`. Julguei `412769f`, que é
> descendente e é o que existe no meu *worktree* — o próprio commit que sela esta rodada.

## Os seis pares

| pacote | critério | nota | razão em uma linha |
|---|---|---:|---|
| `ceo-maestro` | `C01` | **6** | Declaração exemplar; o caso que ocorreu — o CEO operando sobre a própria estrutura — não é coberto por cláusula nenhuma e contraria `SKILL.md:52` na letra. |
| `ceo-maestro` | `C02` | **8** | Schema fechado, `const` em tudo, bateria negativa larga e validado de baixo por quatro pacotes; sobram dois riscos: um `anyOf` que o motor ignora em silêncio e uma saída obrigatória que nenhum envelope carrega. |
| `diretor-de-lentes` | `C01` | **8** | Atende inteiro, sem defeito observado: "não executa, não julga, não autoriza exceções" repetido em quatro lugares e a fronteira polícia até atalhos alheios; sobram dois riscos menores. |
| `diretor-de-lentes` | `C02` | **9** | Supera: o schema valida a aritmética do gate, não só a forma, e o que atravessa é validado contra o schema do outro lado; sobra **um** risco nomeado. |
| `departamento-negocios` | `C01` | **6** | Contrato operacional excelente e régua própria bem cercada, mas o validador do pacote executa os validadores de dois vizinhos e nada no contrato declara essa dependência. |
| `departamento-negocios` | `C02` | **8** | A bateria negativa mais larga dos três e a fronteira validada contra o schema do vizinho; sobram dois riscos: envelope duplicado sem guarda de deriva e saída própria não delimitada. |

**Mínimo dos meus critérios: 6.** É o mínimo dos *meus* dois critérios, não o do pacote — `C03`/`C04`
e `C05`/`C06` são de outras lentes, e a agregação entre instâncias não é minha.

## O que descontei, e disse que descontei

O `FAIL` da **série global de ADR** (número `020` duplicado entre duas cópias de laboratório sob
`ceo-maestro/evals/producao-honesta-2026-08-04/origem-independente-R1/lab/mech/A|B/`) aparece nos
três pacotes que julguei e **não pesou em nenhuma das seis notas**. É alheio: nasce de artefatos de
uma campanha antiga, não de contrato nem de schema destes três.

O que **não** descontei, porque o contrato desta rodada o declara fato do pacote: as **duas cascatas
de sub-execução** do `departamento-negocios`. Cobrei-as **uma vez só**, em `C01`, e não as recobrei em
`C02` — a contabilidade está escrita dentro da razão de `C02` para que possa ser conferida e
contestada.

## Os achados, com caminho e linha

### `ceo-maestro` — a fronteira mais enfática é a que foi atravessada

O pacote proíbe executar em três lugares independentes (`SKILL.md:9`, `SKILL.md:52`,
`CONTRATO-DE-COMPROMISSO.md:86`) e fecha a lista de interlocutores com um "**e mais ninguém**"
(`CONTRATO:20-21`). Nesta rodada, `00-CONTRATO.md:40` registra *"Eu executo os validadores, publico a
saída crua, selo este contrato, despacho os juízes e agrego o resultado"*, e a evidência publicada
carimba `"executado_por": "ceo-maestro no papel de executor"` (`saida-crua/00-RESUMO.json:3`) —
enquanto `SKILL.md:52` diz, na letra: *"Não executar, corrigir, testar, pontuar ou fabricar
evidência."*

Havia rota declarada e não usada — `SKILL.md:42` manda encaminhar toda frente técnica ou de produção
ao `diretor-de-lentes` — e o único desvio previsto no pacote é a `EXCEPTION_AUTHORIZATION` de
Jeremias (`CONTRATO:30-31`), que não é citada para o papel de executor. O contrato da rodada declara
o conflito e o nomeia como teto (`OI-04`); declarar limite é mérito de `C06`, não meu, e eu não
importei esse crédito para cá.

Segundo achado, independente: `saida-crua/00-RESUMO.json:29-34` lista **quatro** `subordinados_diretos`
para o CEO, incluindo `departamento-juizes`, contra os três de `CONTRATO:20-21` e contra a proibição
de acionar os Juízes diretamente (`SKILL.md:49-50`). A receita desse campo não está publicada e eu
não executo: registro a inconsistência, não a causa.

### `ceo-maestro` — uma cláusula do próprio schema não está em vigor

O motor que aplica os schemas cobre um **subconjunto** do draft 2020-12 e documenta que o que não
suporta é *"ignorado em silêncio"* — `_compartilhado/validador_schema.py:14-18`, e `anyOf` está
nomeadamente nessa lista. Varri os três schemas: o único `anyOf` de toda a fronteira está em
`schemas/ceo-maestro.schema.json:1174`, e é justamente a cláusula que exige que um `REPROVED` se
sustente em nota ≤ 6, falha crítica ou pendência bloqueante. Pelo caminho do schema, essa regra não
vale; ela sobrevive porque a camada semântica reconfere o veredito em `evals/validate_workflow.py:650`.
Perda de defesa em profundidade, sem artefato escapando — por isso risco, não defeito.

Segundo risco: `SKILL.md:234-256` torna **obrigatória desde 2026-08-05** a declaração de custo da
rodada (`subagentes`, `tokens_de_subagente`, `rodadas`, `relogio`). Nenhum envelope do schema pode
carregá-los — `executiveDecision` tem 15 propriedades fixas e `additionalProperties: false` — e
nenhum caso da saída crua os menciona. Uma saída declarada obrigatória que circula fora de qualquer
envelope.

### `diretor-de-lentes` — a fronteira policia até o atalho alheio

`SKILL.md:36-37` obriga a **impedir** `CEO → Departamento`, `Diretor → Agente` e
`Negócios → Departamento`: o pacote não se limita a declarar o próprio limite, assume o de terceiros.
O `departamento-evolucao-skills` é declarado **par** e não subordinado, com a razão (evolui as skills
desta camada) e a consequência (o Diretor não o aciona) — `SKILL.md:28-30`. E a troca matricial vem
com a **não**-consequência dita em voz alta: *"Isso não subordina Negócios ao Diretor nem autoriza o
Diretor a editar a proposta comercial"* (`SKILL.md:253-255`).

Os dois riscos que impedem o 9 em `C01`: o único toque autorizado em número — *"recalcula somente a
menor nota aplicável para detectar inconsistência"* (`SKILL.md:193`, `CONTRATO:65` e `:84`) — separa-se
de "pontuar" apenas por texto, sem nada no envelope distinguindo recálculo de atribuição; e o gate
que deveria ser independente é **subordinado direto** de quem lhe manda o trabalho (`CONTRATO:18`).
A fronteira está nomeada — e nisso o critério é atendido —, mas a independência é sustentada por
proibição, não por linha de reporte distinta.

No `C02`, o que faz o pacote superar: o schema valida a **aritmética do gate**, não só a forma —
recusa `REPROVED` com mínimo 9, `ACEITO_USO_INTERNO` com mínimo 10 e `VALIDATED` com mínimo 9
(`saida-crua/diretor-de-lentes.stdout.txt:46-48`), exige `minimum_score_range` e `aggregation_rule`
(`:35-36`) e recusa faixa invertida (`:44-45`). E `SKILL.md:58-62` manda validar os envelopes
executivos contra o schema **do CEO**, com o uso provado em `:10`. Todo objeto materializável é
fechado; os dez objetos sem `additionalProperties: false` são os matchers `contains` da
`department_matrix`, que precisam ser parciais, e o item do array resolve para
`departmentClassification`, fechado, com `minItems`/`maxItems` em 10 e `uniqueItems`.

O risco único: `CONTRATO:46` e `:85` põem **`D_REWORK`** na coluna de saída da tabela de "Saídas
obrigatórias", onde todas as outras linhas nomeiam um `artifact_type`. `D_REWORK` é valor do enum
`directorState` (`schemas/diretor-de-lentes.schema.json:139`); o envelope chama-se `REWORK_ORDER`.
Estado e envelope dividem a mesma célula, e só o `FORWARD-TEST.md:144` desfaz a ambiguidade.

### `departamento-negocios` — o verde depende de dois vizinhos, e o contrato não diz

`evals/validate_workflow.py:2317-2334` roda, por `subprocess`, os validadores do `ceo-maestro` e do
`diretor-de-lentes`, e `:2349-2353` converte o código de saída deles em `FAIL` próprio. Efeito medido:
dois dos três `FAIL` deste pacote são o *status dos vizinhos* — `saida-crua/departamento-negocios.stdout.txt:232`
(`[FAIL] regressão passa: ceo-maestro: eitado`, com o detalhe truncado a 500 caracteres no meio de uma
palavra) e `:243`.

Nenhuma linha do contrato declara essa dependência: as tabelas de "Entradas aceitas" e "Saídas
obrigatórias" (`CONTRATO:42-71`) não a mencionam, e o pacote declara em sentido oposto — *"Não comando
Juízes, Departamentos do CTO nem seus agentes"* (`:33`) — e exige autorização matricial até para falar
com o CTO (`:118`, `:145-152`). Fronteira presumida, não nomeada: é o modo de falha que o próprio
`C01` nomeia.

**A contraleitura, para o registro:** ler isso como *disciplina de regressão* é defensável — o
docstring do validador declara "regressões do CEO/Diretor" (`evals/validate_workflow.py:4`), logo é
deliberado, e um pacote que se recusa a ficar verde enquanto os vizinhos estão vermelhos está fazendo
o que esta casa prega. Se essa leitura prevalecer, a nota sobe para 7 ou 8. Mantenho **6** porque
deliberado-e-não-declarado continua não declarado, e porque o efeito apareceu na medição.

O efeito de envelope, cobrado em `C02`: o fluxo de resultado intercala **38 linhas** dos dois vizinhos
(`:233-252` e `:258-277`) e termina com o sumário do vizinho. A última linha `Resultado:` da saída
deste pacote é o **99/100 do Diretor**, não o próprio `230/233` (`:255`) — e sob a receita publicada
*"sumario = ULTIMO da saida"* (`saida-crua/00-RESUMO.json:4`) foi o número do vizinho que ficou
registrado como `sumario_proprio` deste pacote (`00-RESUMO.json:107`). Uma saída que nenhum schema
governa carregou conteúdo alheio.

O que segura o `C02` em 8 apesar disso: a bateria negativa é a mais larga que li — recusa dois, quatro
e agente duplicado (`:121-123`), plano sem cobrir `BIZ-01..08` (`:124`), `9,49` como pronto (`:129`),
refs forjadas (`:153`) — e **o schema recusa localmente os artefatos que o contrato proíbe o pacote de
produzir**, `JUDGE_REPORT`, `EXECUTIVE_DECISION` e `EXCEPTION_REQUEST` (`:138-140`). A proibição do
contrato virou regra de envelope. Além disso, a fronteira é validada contra o schema **do vizinho**
(`:220-228`, declarado em `SKILL.md:229-231`).

## O que declaro contra mim

**Julgar quem me despachou pesou — e não na direção que a pergunta sugere.** Não senti relutância em
dar nota baixa ao `ceo-maestro`. Senti o viés espelhado: a tentação de provar independência sendo duro
justamente com ele. Foi o único pacote em que escrevi a contraleitura **antes** de fechar a nota, para
conferir se o 6 se sustentava sem plateia. Sustenta-se em dois achados citáveis por caminho e linha;
se fosse um só, eu teria dado 7. E registro que o que me protege não é a minha firmeza: é o contrato
selado antes de eu existir e o *worktree* fora do alcance de edição dele.

Os demais, em resumo — a lista completa está em `PARECER.json`:

1. Usei `python` para **ler e contar** a estrutura dos três schemas (fechadura de objeto, `const` de
   `artifact_type`, varredura de palavras-chave não suportadas, diff das duas definições de
   `MATRIX_EXCHANGE_MESSAGE`). É leitura assistida de arquivo-fonte, não execução de validador, e
   nenhum `PASS`/`FAIL` meu entrou no parecer — mas esses números são derivação **minha** e não
   constam da saída crua. Se a rodada considerar isso execução, três evidências caem.
2. Li `julgamento-nove-departamentos-2026-08-04/00-CONTRATO.md`, que está num diretório listado como
   proibido, porque o despacho o ordenou nominalmente para as definições íntegras de `C01` e `C02`.
   Traz critérios, donos e regra de agregação; **nenhuma nota**. Não abri mais nada ali.
3. Não abri `REGISTRO-DE-VEREDITOS.md`, nenhum `evals/PLACAR.md`, `julgamento-pacotes-2026-07-29/`,
   `recoleta-c03-c05-c06-2026-08-05/` nem os vereditos da T19/T27, e não fiz busca larga. Topei com
   dois **nomes de caminho** — a listagem de diretórios de `ceo-maestro/evals/` ao mapear o pacote, e
   a linha de link `evals\PLACAR.md -> ../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md` na
   saída crua de Negócios. Caminho, sem nota. **Não vi nota anterior de pacote nenhum.**
4. Julguei o `ceo-maestro` em `C01` apoiado também em **conduta observada**, não só em texto de
   contrato. É escolha de escopo minha, discutível, e responde por metade do peso do 6.
5. Duas das seis notas saíram 6, por causas diferentes. Não comparei pacote com pacote em momento
   nenhum, mas percebi a coincidência e reabri as duas derivações antes de escrever.
6. Não executei nada: todo `PASS`/`FAIL` que cito é a palavra de um dos pacotes que julgo, sobre si e
   sobre dois vizinhos, na rodada em que ele é julgado. Não tenho medida independente disso — e o
   contrato me proíbe de fazer uma.
