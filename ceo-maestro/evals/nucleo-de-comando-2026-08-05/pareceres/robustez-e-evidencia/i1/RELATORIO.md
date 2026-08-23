# Parecer — `robustez-e-evidencia`, instância 1 — núcleo de comando

- **Lente:** `robustez-e-evidencia` · **instância:** 1 · **round:** `nucleo-de-comando`
- **Commit julgado:** `412769f31ccb0cb636f85c41f56cf9c6f612b3c1`
- **Contrato selado sobre:** `ee916c6` — confirmei por `git merge-base --is-ancestor` que é ancestral da árvore que julguei.
- **Nível exigido:** `INTERNO` · **Critérios:** `C03`, `C04` · **Pacotes:** três (o `departamento-juizes` não é meu).
- **Não executei nada.** `SKILL.md:132` proíbe. Li a medição do CEO e a critiquei.

## As seis notas

| pacote | C03 trava com prova | C04 evidência e rastreabilidade |
|---|---:|---:|
| `ceo-maestro` | **6** | **5** |
| `diretor-de-lentes` | **7** | **6** |
| `departamento-negocios` | **5** | **4** |

**Mínimo dos meus critérios: 4.**

## Vazamento no contrato — declarado

O `00-CONTRATO.md` traz nas **linhas 10-15** a tabela com as notas de 2026-07-29 dos quatro
pacotes. Eu as vi: estão no segundo parágrafo do primeiro documento que me mandaram ler. O mesmo
arquivo, em `:80-86`, me proíbe de ler os arquivos que contêm exatamente esses números. É
vazamento do próprio CEO. O efeito e o que fiz contra ele estão na seção final.

## O que confirmei da medição do CEO

Os três fatos que me foram passados como publicados por outros juízes — conferi na fonte, não aceitei.

### 1. O `anyOf` do schema do CEO é inerte — confirmado, e por duas causas

`schemas/ceo-maestro.schema.json:1174` põe um `anyOf` dentro do `then` da regra de `REPROVED`.
O motor compartilhado implementa `oneOf` (`_compartilhado/validador_schema.py:300`) e `allOf`
(`:309`) — e mais nada dessa família. O docstring avisa, nomeando `anyOf` na lista do que
"são ignoradas **em silêncio**" (`:14-18`). A regra nunca restringe nada.

O que acrescento: **mesmo se `anyOf` fosse implementado, o bloco continuaria inerte.** Os três
ramos (`schema:1175-1195`) são `properties` puros, sem `required`. Uma instância que não traga
`critical_fail` satisfaz o segundo ramo por vacuidade. Morta por duas causas independentes.

### 2. A sub-execução por `subprocess` — confirmado

`departamento-negocios/evals/validate_workflow.py:2317-2334` roda os validadores do CEO e do
Diretor por `subprocess` e `:2350-2354` converte o exit code deles em `check(False)` próprio.
Daí 2 dos 3 FAIL. Achei ainda o desvio em `:2338-2348`: um rebaixamento para WARN condicionado a
casar três strings, uma delas o literal **`"Resultado: 31/32 casos passaram."`**. O CEO devolve
95/96 hoje; o literal não casa mais; o caso vira FAIL duro. Contagem petrificada governando fluxo.

### 3. A saída de Negócios não é delimitada, e o CEO colheu o sumário errado — confirmado

Rastreei o mecanismo inteiro:

1. `:2350-2354` imprime `combined[-500:]` do vizinho como detalhe do FAIL. O corte de 500 chars
   parte a palavra ao meio — é a origem do ilegível `[FAIL] regressão passa: ceo-maestro: eitado`
   (`stdout:232`), cauda de "rejeitado".
2. A lista de falhas do rodapé **reimprime o mesmo detalhe**. Resultado: `Resultado: 95/96` do CEO
   e `Resultado: 99/100` do Diretor aparecem **duas vezes cada** no stream de Negócios
   (`:233-241`, `:244-252`, `:258-266`, `:269-277`), sem nenhuma marca de dono.
3. O sumário próprio de Negócios está em `:255`, com **outro token**:
   `RESULTADO: 230/233 PASS; 3 FAIL; 0 WARN`.
4. A **última** linha `Resultado:` do arquivo é a do Diretor (`:277`). A receita declarada —
   *"sumario = ULTIMO da saida"* (`00-RESUMO.json:4`) — colheu o número do vizinho.

**`00-RESUMO.json:107` publica `departamento-negocios.sumario_proprio = "99/100"`. É o número do
Diretor.** O verdadeiro é 230/233.

## Furos que achei por conta própria na medição do CEO

**O registro se autocontradiz e ninguém sinalizou.** O mesmo objeto de `00-RESUMO.json` traz
`fails` com **3 itens** e `sumario_proprio: "99/100"` — que implica exatamente 1 falha. As duas
coisas não podem ser verdadeiras juntas. Uma conferência de uma linha (falhas declaradas × diferença
entre numerador e denominador) teria pego: 95/96→1 fail confere; 99/100→1 fail confere; 99/100 com
3 fails não confere. O CEO publicou a contradição sem nomeá-la.

**Deriva de contagem, em tempo presente, no placar do próprio CEO.** `evals/PLACAR.md:10` afirma
*"A cadeia canônica **hoje** soma **1531/1531 PASS**"* — alegação corrente, sem data, tudo-PASS —
enquanto a rodada que o próprio CEO publicou mostra **ao menos um FAIL em cada um dos quatro
pacotes**. A mesma linha dá o número próprio como **33/33 PASS** (2026-07-26); a receita devolve
hoje **95/96 com 1 FAIL**. `adendo_de_contagem: false`.

**Deriva na linha rotulada "ativa" do Diretor.** `diretor-de-lentes/evals/PLACAR.md:10-12`, tabela
intitulada **"Medição ativa"**, declara `79/79 PASS`. A receita devolve `99/100` com 1 FAIL
(`stdout:103`). Número errado e alegação de tudo-PASS onde há FAIL, numa linha que o pacote marca
como corrente. O mesmo arquivo ainda carrega um segundo número próprio, `50/50 PASS` (`:35`).

**Deriva no placar de Negócios.** `PLACAR.md:11` declara `226/226 PASS, 0 FAIL, 0 WARN` e `:37`
declara `Falhas ou advertências abertas | 0`. A receita devolve `230/233` com **3 FAIL**.

## O que sustenta as notas, e não só o que as derruba

Não achei só defeito, e a nota reflete isso.

- **CEO, C03:** as travas são executadas de verdade — `deepcopy` do fixture válido, mutação de um
  campo, re-execução da função real, exigência de lista de erros não vazia (`:3452-3462`). O ataque
  de prefixo é executado contra payload quase-certo (`:2646-2648`), que é o caso difícil. E **morte
  por exceção não é creditada**: não há `except` abrangente no harness, e a ausência do motor
  compartilhado é tratada com `[FAIL]` impresso e um comentário explicando que `ModuleNotFoundError`
  é subclasse de `ImportError` e por isso o segundo braço existe (`:35-45`). O criterio nomeia esse
  defeito; o pacote o tratou de propósito.
- **CEO, C04:** receita literal, raiz (`commit`), critério e stdout cru publicado. **Foi a evidência
  que o próprio CEO publicou que me permitiu convictá-lo.** Pacote que publica o bastante para ser
  condenado pela própria saída não é banda 0-3.
- **Diretor, C03:** cobre as **bordas** da regra de agregação nos **dois sentidos** — aceita o caso
  coerente (`stdout:37`, `:49`) e reprova o incoerente (`:38`, `:39`, `:46`, `:47`, `:48`). Trava que
  só soubesse dizer "não" reprovaria também os válidos, e não reprova. Schema sem `anyOf` (conferi: 0).
- **Negócios, C03:** tem bloco genuíno e forte de trava causal contra forja — colisão de
  `agent_mission_id` com refs coordenadas (`:152`), refs forjadas entre intake/plano/atribuição
  (`:153`), `plan_ref` forjado (`:156`), evidência de scorecard ausente (`:159`). É o que o segura em 5.

## O FAIL da série de ADR

**Descontado.** As duplicatas do `adr-020` estão em
`ceo-maestro/evals/producao-honesta-2026-08-04/origem-independente-R1/lab/mech/{A,B}/` — cópias de
laboratório de outra frente. Não pontuei nenhum dos três pacotes por ele. Onde ele é a única causa
do exit 1 (CEO e Diretor), tratei o exit 1 como alheio; o que cobrei foram os números dos placares
e a inércia do `anyOf`, que independem dele.

## O que declaro contra mim

**Senti a tentação de ser mais duro, não a mais branda.** Fui avisado das duas; foi a de endurecer
que apareceu. O momento foi fechar o `C03` do `ceo-maestro`: eu tinha 96 casos genuinamente
executados por mutação, tratamento deliberado de morte por exceção — e **um** bloco de schema
inerte. Minha primeira inclinação foi 5, pelo simbolismo de reprovar quem me despachou. Corrigi para
6 aplicando a pergunta que aplicaria a qualquer pacote. Registro que a correção foi consciente e
que ela pode ter compensado demais.

**A âncora do vazamento.** As notas que vi eram 1, 1, 2 e 5. As minhas são mais altas. Não consigo
provar que a âncora baixa não me puxou para cima. O que posso dizer é que reconstruí cada achado da
fonte e amarrei cada nota a arquivo e linha que reli.

**Três afirmações minhas são leitura de código, não medida** — porque não pude executar: que nenhum
caso fica vermelho se o bloco `anyOf` for apagado; que o ramo `critical_fail` seria vacuamente
verdadeiro mesmo com `anyOf` implementado; e que o escape hatch de `:2338-2348` não casa mais hoje.
As três se decidem em minutos com uma mutação executada. Quem puder executar, execute antes de
tratar isso como fato medido.

**Cobrei `not errors` com peso desigual.** Nomeei-a risco menor no Diretor (7) e risco adicional no
CEO (6). Se alguém entender que deveria pesar igual, o Diretor cai para 6.

**O mesmo evento aparece em dois pacotes.** Meu `C04` do CEO pune publicar o número errado; meu
`C04` de Negócios pune o stream que o produziu. Sustento que são defeitos distintos — colher sem
conferir × emitir sem marca de dono — mas quem ler as duas razões verá a mesma cena duas vezes.

**Conflito não resolvido, como o contrato admite.** Fui despachado pelo julgado. Nada no que fiz
fecha isso; só a declaração fica.
