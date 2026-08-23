# ADR-015 — Checagem por pacote e checagem de estrutura inteira: onde moram, quem chama, e como pacote novo entra sozinho

- **Data:** 2026-07-27
- **Status:** aceito — aprovado por Jeremias em 2026-07-29
- **Decidido em:** 2026-07-29
- **Proponente:** `departamento-arquitetura-software`, sob `DEPARTMENT_MISSION` DM-2026-07-27-ARQ-001 do `diretor-de-lentes`
- **Decisor:** Jeremias
- **Candidato aplicado:** `_compartilhado/verificacoes_pacote.py`, sha256 `9ad640071443ceec11552b97d8bbb83ecab8db8d119bdcf517261815e695ab3a` ·
  `_compartilhado/verificacoes_estrutura.py`, sha256 `bcbd7daf09c61e2f628ba2b34c9648dfc56920cd1b157bd9d68f7079cf843e01`
- **Contexto normativo:** [ADR-006 arquitetura sem julgamento](adr-006-arquitetura-sem-julgamento-e-com-seis-agentes.md) ·
  [ADR-001 hierarquia](../../../../references/adr-001-hierarquia-executiva.md) ·
  [ADR-003 conformidade sem nota](../../departamento-auditoria-responsabilidades/references/adr-003-conformidade-sem-nota.md)

## Contexto

O motor compartilhado `_compartilhado/verificacoes_pacote.py` (373 linhas, lido integralmente)
carregava **dois tipos de checagem com contratos de entrada incompatíveis**, sob um nome de arquivo
que anunciava só o primeiro.

**Tipo A — POR PACOTE.** Recebe um arquivo ou o diretório de **um** pacote e não sai dele:

| Função | Entrada |
|---|---|
| `read_frontmatter` | um arquivo |
| `validate_frontmatter` | um `SKILL.md` |
| `validate_openai_yaml` | um `agents/openai.yaml` |
| `validate_required_files` | lista de caminhos dada pelo chamador |
| `validate_agents_folder` | `agentes/` do próprio pacote |
| `validate_contract_sections` | um `CONTRATO-DE-COMPROMISSO.md` |
| `validate_skill_tokens` | um `SKILL.md` |
| `validate_links` | `package_root.rglob("*.md")` — varre, mas dentro do pacote recebido |

**Tipo B — ESTRUTURA INTEIRA.** Recebe `structure_root`, a raiz da árvore, e atravessa tudo:

| Função | Travessia | O que trava |
|---|---|---|
| `validate_adr_series` | `root.rglob("adr-*.md")` | unicidade **global** da série `adr-<NNN>` |
| `validate_contratos_de_gerente` | `root.rglob("SKILL.md")` | as 12 seções de `SECOES_CONTRATO_GERENTE` em todo pacote gerente |

A série de ADR é **global, não por escopo**: `validate_adr_series` agrega tudo num único
`by_number: dict[int, list[str]]` sem filtro de Departamento, e reprova qualquer número com dois
arquivos fora da isenção histórica por caminho exato `ADR_HISTORICAL_EXCEPTIONS`. É por isso que
este ADR é **015** e não `adr-001` local.

O módulo **não resolve a raiz sozinho**: não há `raiz_estrutura` nem cadeia de `.parent`;
`structure_root` chega sempre por parâmetro do chamador.

### A premissa foi medida, e está corrigida

Jeremias afirmou: *"sete validadores chamam por-pacote / três chamam estrutura-inteira"*.

**Medição de 2026-07-27**, método: Glob `Estrutura Final de Skills/**/evals/validate_workflow.py`
(15 arquivos, universo fechado), depois inspeção do bloco de import e da chamada real
`validate_adr_series(` / `validate_contratos_de_gerente(` para separar import de uso:

- **universo: 15** validadores, não 10;
- **14 chamavam pelo menos uma checagem de estrutura inteira**;
- **1 chamava somente checagens por pacote** — `departamento-desenvolvimento`;
- **0 não usavam o motor**;
- desdobrando o tipo B: `validate_adr_series` era chamada por **14**;
  `validate_contratos_de_gerente`, por **3** (`ceo-maestro`, `diretor-de-lentes`,
  `departamento-design-ux-ui`).

**A premissa está corrigida.** O "três" existe, mas é o número de chamadores de **uma** função
(`validate_contratos_de_gerente`), não de uma categoria; e o "sete por-pacote" não tem lastro — só
existia **um** validador exclusivamente por pacote. A missão exigia citar 2 exemplos
só-por-pacote: **não era satisfazível**, porque só havia 1. Fica declarado como evidência
insuficiente por escassez do universo, não por corte de orçamento.

## Decisão proposta

**1. A fronteira é o tipo do parâmetro, e vira fronteira de módulo.**
Checagem que recebe **um pacote** fica em `_compartilhado/verificacoes_pacote.py`. Checagem que
recebe `structure_root` sai para `_compartilhado/verificacoes_estrutura.py` — hoje, exatamente
`validate_adr_series` e `validate_contratos_de_gerente`. O critério não é temático nem estilístico:
é **verificável em uma linha de assinatura**, e por isso um validador não pode errar de lado por
descuido. `validate_links` fica no lado do pacote apesar de usar `rglob`, porque o `package_root`
que ela varre **é** o pacote — o parâmetro decide, não o verbo.

**2. Quem chama: todo validador de pacote chama os dois lados. A checagem de estrutura inteira é
replicada de propósito, nunca centralizada.**
É a decisão contraintuitiva, e era a que já predominava no código: 14 dos 15 validadores rodavam o
tipo B. A redundância é o mecanismo — qualquer validador pega a colisão do vizinho, mesmo que o
pacote do vizinho ainda não tenha validador próprio. Com N frentes paralelas, N validadores checam
a árvore inteira; basta **um** rodar para a colisão aparecer. Centralizar num único validador de
raiz mataria isso. Consequência imediata: `departamento-desenvolvimento` estava **fora da trava** e
precisava entrar.

**3. Pacote novo entra por descoberta no filesystem, e a lacuna de cobertura é fechada por um gate
derivado — não por linha de documentação.**
Três camadas, todas executáveis, todas com precedente no código medido:

- **Descoberta por posição na árvore.** `validate_contratos_de_gerente` define quem é gerente por
  `root.rglob("SKILL.md")` + o teste `pacote.parent.name == "agentes"` — sem lista de nomes.
  Pacote novo entra na trava por existir, sem ninguém precisar lembrar de o cadastrar. Idem
  `validate_adr_series` com `rglob("adr-*.md")`.
- **Gate de cobertura, derivado da mesma varredura.** Para cada `SKILL.md` fora de `agentes/`
  descoberto por `rglob`, exigir `evals/validate_workflow.py` no pacote, import do módulo de
  estrutura inteira e chamadas reais das funções exigidas. Pacote sem validador, ou com validador
  que não exercita o tipo B, vira FAIL — do mesmo jeito que contrato sem seção vira FAIL hoje. O
  gate **deriva a lista de pacotes da árvore**, não de um registro; não há onde esquecer de
  cadastrar porque não há cadastro.
- **Isenção só por caminho exato e fechada.** Padrão de `ADR_HISTORICAL_EXCEPTIONS`: exceção nomeia
  o arquivo, não o número, e um arquivo novo entrando no grupo reprova o grupo inteiro. Qualquer
  isenção do gate de cobertura segue essa forma.

**4. Nenhuma lista de pacotes é introduzida.** O único hardcode de identidade no motor é
`ADR_HISTORICAL_EXCEPTIONS`, que é isenção fechada e histórica. `expected_names` de
`validate_agents_folder` continua vindo do validador do pacote — é o pacote declarando o próprio
time, não a estrutura mantendo um registro central.

**5. A decisão de arquitetura não executa a especialidade de Desenvolvimento.** Mover funções,
criar `verificacoes_estrutura.py`, escrever o gate de cobertura e corrigir `__all__` pertencem à
frente de implementação. O ADR registra a fronteira e os trade-offs; a aplicação é rastreada no
adendo abaixo.

## Consequências

**O que melhora**

- a fronteira deixa de depender de leitura de docstring e passa a ser legível na assinatura;
- pacote novo é coberto por existir na árvore, e a ausência de validador próprio vira FAIL visível;
- a colisão de ADR e a divergência de anatomia de contrato continuam sendo pegas por qualquer
  frente paralela, inclusive por quem não conhece o pacote vizinho.

**O que fica PIOR — e é o preço proposto**

- **Custo quadrático assumido.** Quinze validadores × `rglob` da árvore inteira, e cada pacote novo
  soma mais uma varredura completa. A suíte fica mais lenta a cada crescimento, por decisão, não por
  descuido.
- **Raio de explosão maior.** Um ADR duplicado ou um contrato de gerente fora de ordem reprova os
  quinze validadores de uma vez, não só o pacote culpado. A mensagem aponta o arquivo certo, mas é
  repetida; a contagem agregada de FAIL mede replicação, não número de defeitos distintos.
- **Nasce um FAIL novo por criar pacote.** Com o gate de cobertura, criar a pasta de um pacote
  **antes** de escrever seu `evals/validate_workflow.py` reprova a suíte inteira. O trabalho em
  progresso deixa de ser silencioso — é o objetivo, e é também um atrito real no meio de uma
  migração.
- **Dois módulos onde havia um.** Todo validador passa a ter dois imports do compartilhado, e
  `departamento-desenvolvimento` ganha uma dependência que não tinha — mais superfície de import
  quebrado, o tipo de falha que a memória da casa registra como *contagem que cai sem FAIL*.
- **A correção da premissa reabre uma pergunta de governança:** se todos os 15 rodam a trava
  global, a próxima colisão de ADR será reportada 15 vezes antes de alguém a corrigir.

## Alternativas consideradas

- **Centralizar o tipo B num único `evals/validate_estrutura.py` na raiz.** Descartada. É a opção
  mais limpa no papel — uma varredura, uma mensagem, custo linear — e cai por uma razão medida:
  com um só executor, frente paralela que roda apenas o validador do próprio pacote **não** pega a
  colisão do vizinho. Troca custo de CPU por dependência de disciplina humana — exatamente o que a
  memória da casa proíbe (*trave em código, não em texto*).
- **Manter tudo num arquivo só e resolver com comentário/seção "checagens de estrutura inteira".**
  Descartada. Custo zero, e era o estado anterior: o arquivo já avisava em prosa qual função era de
  qual tipo, e mesmo assim `departamento-desenvolvimento` ficou fora da trava e
  `validate_contratos_de_gerente` ficou fora do `__all__`. Aviso em prosa não previne erro — já
  falhou, aqui, de forma verificável.
- **Registrar os pacotes cobertos numa lista/`packages.toml` e iterar sobre ela.** Descartada.
  Daria mensagem de erro ótima e custo linear, mas reintroduz o cadastro manual: pacote novo só é
  coberto se alguém lembrar de o inscrever. Transforma o gate derivado em gate declarado.
- **Escopar a série de ADR por Departamento, deixando cada pacote com sua numeração local.**
  Descartada. Resolveria o raio de explosão e o `adr-001` triplicado, mas contraria o passo 4 do
  guia e o comportamento vigente. Mudar a série é pedido formal de revisão, não efeito colateral
  deste ADR.

## Adendo de aplicação — 2026-07-29

A proposta nasceu como `ADR-014`, mas esse número foi ocupado em 2026-07-28 pelo
[ADR-014 dos Juízes](../../../departamento-juizes/references/adr-014-dois-niveis-de-veredito.md).
Como a série é global, esta decisão foi renumerada para **ADR-015**. O próximo número livre foi
conferido na árvore antes da criação.

Três diferenças entre a proposta de 2026-07-27 e o candidato aplicado:

1. A correção do `__all__` e a entrada de `departamento-desenvolvimento` na trava global já estavam
   materializadas antes desta sessão; deixaram de ser pendência.
2. O gate ficou **mais rígido** do que a proposta pedia: a proposta exigia import do módulo; a
   implementação exige import **e chamada real**, por AST, porque import sem chamada é dependência
   morta.
3. A primeira implementação ainda aceitava "qualquer função de estrutura". A mutação A removeu
   somente a chamada de `validate_cobertura_de_validadores` de Registros e passou verde porque o
   arquivo ainda chamava `validate_adr_series`. O conserto tornou
   `FUNCOES_OBRIGATORIAS = ("validate_cobertura_de_validadores",)` autorreferente e exige, além
   dela, ao menos uma função complementar de estrutura.

Prova executada no checkout fiel aos bytes do repositório principal:

| Prova | Resultado |
|---|---|
| cadeia saudável, 15 validadores | **1531/1531 PASS**, 0 FAIL, 0 quebrado |
| mutação A: Registros importa, mas apaga só a chamada do gate | **184/185**, `exit=1`; Segurança nomeia Registros e `validate_cobertura_de_validadores` ausente |

O candidato está implementado e provado. O aceite arquitetural foi registrado somente depois da
decisão humana explícita abaixo; a aplicação técnica anterior não fabricou essa autoridade.

## Registro da decisão — 2026-07-29

Jeremias decidiu explicitamente, no canal ativo: **“sobre o ADR-015 - aprovado”**.

A partir dessa decisão, este ADR é contrato vinculante. Alterar a fronteira entre checagens por
pacote e checagens de estrutura inteira, retirar a replicação deliberada do gate ou enfraquecer a
chamada obrigatória exige conflito declarado e nova decisão de Jeremias.

## Fechamento das pendências desta decisão

- **R6 fechado** — o código aplicado agora possui decisão de arquitetura aceita.
- `PENDING` de Jeremias fechado — o ADR foi aprovado em 2026-07-29.
- deploy e paridade dos runtimes concluídos após a prova da fonte; a árvore fonte e os dois
  runtimes foram conferidos mecanicamente.
- O `1558` citado no plano veio de outro checkout e de outro método; não foi herdado. O par
  comparável desta aplicação é **1516→1531**, medido no mesmo método e na mesma árvore.
