# Guia de Expansão e Migração

> Manual único para **migrar uma lente legada** ou **criar um Departamento novo** nesta estrutura,
> do início ao fim. Destilado dos três pacotes já materializados — `ceo-maestro`,
> `diretor-de-lentes` e `departamento-juizes` — e do que cada um custou a acertar.
>
> **Fonte normativa:** [regras-de-ouro/REGRAS-DE-OURO.md](regras-de-ouro/REGRAS-DE-OURO.md).
> **Hierarquia e contrato estrutural:** [ORGANOGRAMA.md](ORGANOGRAMA.md).
> **Regras operacionais:** [AGENTS.md](AGENTS.md).
> Este guia **não cria regra nova**: organiza a aplicação das que já existem. Conflito entre este
> guia e as três fontes acima é resolvido a favor delas, e o guia se corrige.

---

## 0. Qual é o seu caso

| Situação | Caminho | Onde começa |
|---|---|---|
| Existe pacote legado em `SKILL - Nova formula/` fazendo o trabalho | **Migração** | passo 1 |
| A capacidade não existe em lugar nenhum | **Criação** | passo 1, pulando o passo 3 |
| Duas ou mais skills legadas cobrem parte do domínio, mas faltam capacidades | **Consolidação híbrida** | passos 1 a 10; proveniência por fonte + ADR do novo recorte |
| Já existe o Departamento e você vai acrescentar ou retirar um agente | **Expansão** | passos 4, 8, 9 e 10 |
| Você quer mudar o contrato de um pacote já migrado | **Evolução** | passo 4 (ADR) e depois 9 e 10 |

Migração, consolidação híbrida e criação convergem a partir do passo 4. A diferença real é o passo
3: quem migra **deve prestar contas do recorte**; quem consolida presta contas de **cada** fonte e
separa o que foi criado por pesquisa; quem cria parte do zero e só declara a fronteira.

**Regra que vale em todos os casos:** o pacote legado permanece **intacto**. Ele é rollback manual e
evidência histórica — nunca fallback automático em runtime, nunca editado, nunca movido.

---

## 1. Antes de escrever qualquer arquivo — as cinco leituras

1. **[ORGANOGRAMA.md](ORGANOGRAMA.md)** — posição do pacote na hierarquia, o time executor mínimo
   e o contrato estrutural obrigatório.
2. **[AGENTS.md](AGENTS.md)** — entrada operacional, níveis do ADR-014 e regra de exceção.
3. **[regras-de-ouro/REGRAS-DE-OURO.md](regras-de-ouro/REGRAS-DE-OURO.md)** — RI-01 a RI-06 e as RO
   aplicáveis. Você vai **referenciar** este arquivo, nunca copiar trecho dele.
4. **O pacote do superior** — `SKILL.md`, `CONTRATO-DE-COMPROMISSO.md` e, principalmente, o
   **schema**: é ele que define o envelope que o seu pacote vai receber e o que ele precisa
   devolver. Um Departamento operacional lê
   `ceo-maestro/diretor-de-lentes/schemas/diretor-de-lentes.schema.json`.
5. **Um pacote modelo** — para Departamento, use
   `ceo-maestro/diretor-de-lentes/departamento-juizes/`; é o mais completo e o único com validador
   que testa contra o schema do consumidor.

**Concluído quando:** você sabe dizer, sem consultar, quem é o seu superior, qual envelope você
recebe, qual você devolve e quais campos desse envelope o schema do superior torna obrigatórios.

---

## 2. Anatomia canônica de um pacote

### Departamento

```text
departamento-<nome>/
├── SKILL.md                      # OBRIGATÓRIO — o gerente-orquestrador
├── CONTRATO-DE-COMPROMISSO.md    # OBRIGATÓRIO — papel, autoridade, obrigações, proibições
├── agents/
│   └── openai.yaml               # OBRIGATÓRIO — interface do runtime
├── references/                   # OBRIGATÓRIO — pelo menos protocolo + origem-migracao
│   ├── protocolo-<dominio>.md
│   ├── origem-migracao.md        # só migração; obrigatório nela
│   └── adr-00N-<decisao>.md      # quando houver decisão que contraria legado ou organograma
├── schemas/
│   └── departamento-<nome>.schema.json    # OBRIGATÓRIO se o pacote materializa envelope próprio
├── evals/
│   ├── evals.json                # OBRIGATÓRIO — catálogo de casos, ≥ 12, ≥ 1 de origem real
│   ├── validate_workflow.py      # OBRIGATÓRIO — validador determinístico
│   └── PLACAR.md                 # OBRIGATÓRIO — o que rodou e o que NÃO rodou
└── agentes/                      # OBRIGATÓRIO — mínimo 3; quantidade justificada pela cobertura
    └── agente-<ótica>/
        ├── SKILL.md
        ├── CONTRATO-DE-COMPROMISSO.md
        └── agents/openai.yaml
```

Opcionais que valem quando existirem: `references/bootstrap.md` (posição esperada, verificação de
capacidade e ordem de autoridade), `references/workflow-*.md`, `evals/FORWARD-TEST.md` (**só depois
de executado de verdade** — ver passo 9) e `evals/README.md`.

### Agente

Três arquivos, sempre. Agente **não** tem `references/`, `schemas/` nem `evals/`: ele obedece ao
protocolo e ao schema do Departamento. Agente que precisa de protocolo próprio é sinal de que a
fronteira dele está errada, ou de que ele deveria ser um Departamento.

### Ferramentas compartilhadas — importe, não copie

O `validate_workflow.py` de um pacote **não implementa** motor de schema nem verificação
estrutural: ele importa de `_compartilhado/` na raiz da estrutura.

```text
Estrutura Final de Skills/
└── _compartilhado/
    ├── validador_schema.py        # motor JSON Schema + find_const + collect_property_names
    ├── verificacoes_pacote.py     # frontmatter, openai.yaml, arquivos, agentes/, links
    ├── teste_validador_schema.py  # teste do motor
    └── README.md                  # como importar, limites do motor e regra de manutenção
```

Copiar essas funções para dentro do pacote é regressão: elas já divergiram uma vez, e a cópia mais
antiga ficou sem `exclusiveMaximum` sem que nenhum teste acusasse. O contrato de uso, a guarda de
import e os limites declarados do motor estão em
[_compartilhado/README.md](_compartilhado/README.md).

---

## 3. A tabela de caminhos relativos — leia antes de escrever links

**A armadilha nº 1 desta estrutura.** A profundidade muda por papel, e Departamentos operacionais
ficam **um nível mais fundo** que `departamento-juizes` e `departamento-negocios`, por causa da
pasta `departamentos-operacionais/`.

| Pacote | Profundidade | → `regras-de-ouro/REGRAS-DE-OURO.md` | → schema do Diretor | → schema do CEO |
|---|---:|---|---|---|
| `ceo-maestro/` | 1 | `../regras-de-ouro/…` | — | `schemas/…` |
| `ceo-maestro/departamento-negocios/` | 2 | `../../regras-de-ouro/…` | — | `../schemas/…` |
| `ceo-maestro/diretor-de-lentes/` | 2 | `../../regras-de-ouro/…` | `schemas/…` | `../schemas/…` |
| `…/diretor-de-lentes/departamento-juizes/` | 3 | `../../../regras-de-ouro/…` | `../schemas/…` | `../../schemas/…` |
| `…/departamento-juizes/agentes/agente-X/` | 5 | `../../../../../regras-de-ouro/…` | — | — |
| `…/departamentos-operacionais/departamento-X/` | **4** | `../../../../regras-de-ouro/…` | `../../schemas/…` | `../../../schemas/…` |
| `…/departamentos-operacionais/departamento-X/agentes/agente-Y/` | **6** | `../../../../../../regras-de-ouro/…` | — | — |
| `ceo-maestro/departamento-negocios/agentes/agente-X/` | 4 | `../../../../regras-de-ouro/…` | — | — |

Do **agente**, aponte só para o protocolo do próprio Departamento (`../../references/…`) e para as
Regras de Ouro. Agente não referencia schema de superior: ele não emite envelope de fronteira.

**Não confie nesta tabela sozinha.** O validador do seu pacote deve conferir que **todo link
markdown interno resolve em arquivo existente** — é um caso de teste, não uma revisão a olho
(modelo: `validate_links()` em `departamento-juizes/evals/validate_workflow.py`).

---

## 4. O passo a passo

### Passo 1 — Fixar identidade e posição

Nome em `kebab-case`, prefixado por papel: `departamento-<domínio>` e `agente-<ótica>`. O nome do
**arquivo `name:` do frontmatter, o nome da pasta e o nome citado no `ORGANOGRAMA.md` são o mesmo
texto** — divergência aqui quebra descoberta em runtime e é caso de teste no validador.

Confira no `ORGANOGRAMA.md` a linha do seu Departamento: os agentes necessários já estão nomeados
lá. O piso é três; não existe teto artificial. A quantidade nasce da cobertura exclusiva do
domínio, e qualquer mudança de composição exige atualizar o organograma e registrar a decisão em
ADR — não invente nome novo no pacote e deixe o organograma mentindo.

**Concluído quando:** nome, pasta, entrada no organograma e superior estão fixados e coincidem.

### Passo 2 — Levantar a proveniência *(só migração)*

Antes de tocar em qualquer coisa, congele a fonte por hash:

```bash
cd "SKILL - Nova formula/maestro/comite-de-lentes/<pasta-legada>"
sha256sum $(find . -type f) && find . -type f | wc -l && du -sb .
```

Guarde a tabela de hashes — ela vai para `references/origem-migracao.md`. Em consolidação híbrida,
faça uma tabela e um total separados para **cada raiz de origem**; nunca misture dois legados em
uma contagem que não permita reconstruir de onde veio cada decisão. Contagem de arquivos e bytes
entram como **contexto de escala**, não como identidade: os filhos legados podem evoluir em
paralelo, e o que fixa a proveniência são os hashes.

Ao terminar tudo (passo 10), **recalcule os mesmos hashes** e prove que a fonte não mudou. Migração
que altera o legado não é migração, é mudança disfarçada.

**Concluído quando:** existe uma tabela `fonte → arquivo → SHA-256`, tirada antes de qualquer
escrita, e capacidades criadas por pesquisa estão separadas das capacidades migradas.

### Passo 3 — Decidir o recorte, em três listas *(só migração)*

`references/origem-migracao.md` precisa de **três** seções, e a do meio é a que ninguém quer
escrever:

1. **Recorte preservado** — o que migrou com adaptação de nome e cadeia. É o valor que justifica a
   migração existir.
2. **Recorte reescrito** — tabela `legado → novo → por quê`, uma linha por mudança de contrato.
   Aqui entram as inversões: gatilho que mudou, saída que mudou, regra que o legado proibia e agora
   é obrigatória. **Se esta tabela está vazia, ou você não leu o legado, ou você só renomeou pasta.**
3. **Recorte não copiado** — o que ficou para trás e por quê. Evals, placares e backtests do legado
   medem outro gatilho e outra saída: **eles quase nunca migram**, e promovê-los é fabricar
   evidência.

**Concluído quando:** cada arquivo de cada fonte aparece em exatamente uma das três listas e toda
capacidade sem fonte legada aparece numa quarta seção, **recorte criado**, com origem de pesquisa e
critério de adoção.

### Passo 4 — Escrever o ADR *(quando houver decisão)*

ADR é obrigatório quando a migração **contraria** o legado, o organograma ou um ADR anterior. Formato
já praticado na estrutura: contexto → decisão numerada → consequências → **alternativas
consideradas com o motivo do descarte**.

A série `adr-00N` é **global para toda decisão nova da estrutura**, não reinicia por pacote. Antes
de cunhar um número, procure todos os `adr-*.md`, identifique o maior número vigente e use o
seguinte. O arquivo continua na pasta do dono da decisão; a numeração global preserva a ordem entre
Departamentos diferentes. Os três `ADR-001` históricos, criados antes desta convenção em camadas
distintas, permanecem intactos como proveniência e **não** autorizam reuso.

**A unicidade não é mais conferida por lista escrita à mão.** Ela é mecânica, em
`validate_adr_series()` de [_compartilhado/verificacoes_pacote.py](_compartilhado/verificacoes_pacote.py):
a função varre `adr-*.md` na **estrutura inteira**, agrupa por número e reprova qualquer número com
dois donos, isentando apenas o grupo dos `adr-001` históricos — e um arquivo novo entrando nesse
grupo reprova o grupo inteiro. **Todos** os validadores da cadeia chamam essa verificação sobre a raiz
da estrutura, então a colisão do vizinho é pega mesmo por um pacote que não a criou e mesmo quando o
pacote do vizinho ainda não tem validador próprio — foi assim que os dois `adr-005` simultâneos de
Registros e QA apareceram. Para descobrir o próximo número livre, leia a árvore, não este guia:

```bash
find "Estrutura Final de Skills" -name "adr-*.md" | sort
```

Lista manual de "qual número é de quem" **não é mantida aqui**: ela defasa a cada frente paralela, e
já defasou. A fonte é a árvore; a trava é o validador.

A seção de alternativas não é enfeite. Ela é o que impede a próxima sessão de refazer a discussão —
e é o primeiro lugar que o auditor lê. Modelo:
`departamento-juizes/references/adr-002-nota-absoluta-e-modo-duplo.md`.

**Concluído quando:** toda decisão que alguém poderia questionar em seis meses tem número, data,
motivo e alternativa descartada.

### Passo 5 — Escrever o protocolo e as referências

O protocolo é a **fonte única** dos envelopes internos, das travas e dos riscos. Três regras:

- **Não duplicar schema.** A `SKILL.md` e os agentes **referenciam** a seção do protocolo; nunca
  relistam campos. Onde a duplicação for inevitável (um "caminho comum" resumido), declare
  explicitamente que **em conflito o protocolo vence e o resumo se corrige**.
- **Não redefinir envelope do consumidor.** `JUDGMENT_REQUEST`, `DEPARTMENT_MISSION`,
  `JUDGE_REPORT` e afins pertencem aos schemas do Diretor e do CEO. Seu protocolo os **consome e
  valida**; recriá-los localmente produz divergência silenciosa no dia em que o superior mudar.
- **Riscos residuais em um único lugar.** Uma seção `## Riscos residuais declarados`, em tabela
  `Id | Vetor | Consequência | Mitigação | Teto`. A coluna **Teto** é obrigatória e diz o que a
  mitigação **não** resolve. O resto do documento aponta para lá; nada é declarado duas vezes.

Toda seção fecha com **`Concluído quando:`** — critério observável, não sensação.

**Concluído quando:** um leitor novo consegue executar o fluxo lendo só o protocolo, e nenhum campo
de schema aparece definido em dois lugares.

### Passo 6 — Escrever o schema interno

Só os envelopes que **o seu pacote materializa**. Convenções já estabelecidas na estrutura:

- `$schema` draft 2020-12, `$id` em `https://skill-crowd.local/schemas/<nome>.schema.json`;
- `oneOf` no topo listando cada `$defs` de artefato;
- `additionalProperties: false` em **todo** objeto — chave extra é erro, não tolerância;
- `causalHeader` completo, com `producer` travado em `const` no **seu** nome: é o que rejeita
  envelope forjado por outro pacote;
- `if/then` para as condições de contrato (ex.: `VALIDATED` exige mínimo 10, ausência de falha
  crítica e lacuna vazia; `ACEITO_USO_INTERNO` exige mínimo 7 e não satisfaz `PRODUCAO`;
  reprovação exige crítica e mudança);
- `enum` de identidades derivado das **pastas reais** — e um caso de teste conferindo isso.

**Concluído quando:** o schema aceita todos os artefatos legítimos do fluxo e rejeita, por
construção, cada atalho que o contrato proíbe.

### Passo 7 — Escrever `SKILL.md` e `CONTRATO-DE-COMPROMISSO.md`

**Limites mecânicos da `SKILL.md`** (todos verificados pelo validador):

- frontmatter com **exatamente** `name` e `description`, nessa ordem, e nada mais;
- `name` idêntico ao nome da pasta;
- `description` entre aspas, **≤ 1024 caracteres**;
- arquivo **≤ 500 linhas**.

A `description` é o que dispara a skill. Ela precisa de: papel em uma frase; **gatilhos em
linguagem de usuário** ("passou no gate?", "isso pode ir para produção?"), inclusive sem citar o
nome da skill; os **anti-gatilhos** ("pediram para tratar nota 9 como produção → deve recusar e
devolver"); e um `NÃO acione para…`
que nomeie as skills vizinhas.

**Seções obrigatórias da `SKILL.md` de Departamento:**

```text
# <Nome>                          → papel em 2–3 linhas + "orquestra e não executa"
## Lei de Ferro — cadeia de comando   → diagrama + com quem fala e com quem não fala
## Compromisso obrigatório        → link para o CONTRATO
## Carregamento progressivo       → quando ler cada reference e cada schema
## Entradas aceitas               → envelope + aponta a tabela de rejeição do protocolo
## Descobrir o time real          → enumerar agentes/ em runtime, sem presumir path
## Workflow obrigatório           → passos numerados, cada um com "Concluído quando:"
## Guardrails                     → "Nunca …", um por linha
## Portão de saída                → checklist de conferência antes de emitir
## Formato de devolução           → o que o superior lê antes do YAML
## Exemplo — entra → sai          → um caso concreto, de preferência um que REPROVA
## Evidência de conclusão da própria skill
## 🔗 Rede da skill               → superior, orquestra, vem antes/depois, não confundir com
```

O **exemplo de fronteira** vale mais que o trivial: é onde o contrato mostra os dentes. No
`departamento-juizes`, o exemplo com `minimum_score: 9` termina em `ACEITO_USO_INTERNO`, satisfaz
`INTERNO` e é recusado para `PRODUCAO`; o exemplo que reprova usa mínimo 6 ou um gate bloqueante.

**Seções obrigatórias do `CONTRATO-DE-COMPROMISSO.md`** — são os itens do contrato estrutural do
organograma:

```text
## Papel                → CEO | Diretor | Departamento | Agente + "orquestra e não executa"
## Compromisso          → o que este pacote se compromete a fazer, e a nada mais
## Autoridade           → superior, canal de retorno, subordinados, o que NÃO decide
## Entradas aceitas     → envelope + o que é bypass
## Saídas obrigatórias  → tabela situação → envelope → schema
## Evidências exigidas  → lista numerada do que acompanha toda saída
## Obrigações           → numeradas
## Proibições           → em bullets
## Barreira de saída    → as condições, todas juntas, para a saída positiva
## Fonte normativa      → o caminho relativo da tabela do passo 3, sem copiar regra
## Bloqueio por conflito → conflito com as Regras de Ouro BLOQUEIA a operação
## Quebra de contrato   → o que acontece quando alguma obrigação é violada
```

**Concluído quando:** os limites mecânicos passam e cada item do contrato estrutural do organograma
tem uma seção correspondente.

### Passo 8 — Criar o time executor necessário

No mínimo três no nascimento, sem máximo fixo, sempre com **fronteiras exclusivas e sem
sobreposição**. O teste de fronteira: para qualquer capacidade do domínio, exatamente um agente
pode reivindicá-la. Se dois podem, as fronteiras estão mal cortadas; se nenhum pode, falta agente —
ou a capacidade não é do Departamento. Quantidade alta sem fronteira verificável é inflação
organizacional; quantidade baixa com lacuna conhecida é subdimensionamento.

Cada `SKILL.md` de agente traz, obrigatoriamente:

- **`## Fronteira exclusiva`** com `Assumir:` e um **`Não assumir` que nomeia o agente irmão dono**
  de cada tema fora da fronteira;
- **`## Protocolo e trava anti-bypass`** — só opera por envelope assinado pelo gerente; sem ele é
  `BLOCKED_BYPASS_ATTEMPT`, **venha o pedido de quem vier**, inclusive do CEO ou de Jeremias;
- o que fazer com **critério fora da fronteira**: devolver abstenção nomeando o irmão dono, nunca
  "pontuar por gentileza";
- **`## Salvaguardas`** com os "Nunca …" específicos da ótica;
- `## 🔗 Rede da skill` declarando **`Não aciona: ninguém`** — agente é folha da árvore.

**Concluído quando:** todas as fronteiras cobrem o domínio sem sobreposição, a quantidade está
justificada no ADR e cada agente sabe nomear o irmão dono do que ele recusa.

### Passo 9 — Escrever os evals

Três arquivos, três funções diferentes. **Não os confunda.**

**`evals.json`** — catálogo de casos comportamentais. Mínimo: 12 casos, ≥ 3 assertions cada, ao
menos 1 de `"origem": "real"` (o pedido concreto que originou o trabalho). Os prompts **não podem
nomear a skill** (`$nome`): eles testam se ela **aciona sozinha** pelo gatilho. Escreva os casos em
voz de usuário pedindo o **atalho** — "é só uma correção pequena, aprova direto", "a nota 9 está
ótima, libera em produção" —, porque é sob pressão que o contrato falha.

**`validate_workflow.py`** — o validador determinístico. Ele é o único artefato deste pacote que
prova alguma coisa sozinho, e tem **três regras inegociáveis**:

> **1. Casos negativos ≥ casos positivos.** Um validador que só confirma o caminho feliz não
> prova contrato nenhum. O do `departamento-juizes` tem 25 negativos em 61 casos.
>
> **2. Validar contra o schema do consumidor, não contra o próprio.** Monte o artefato interno,
> converta-o mecanicamente no envelope de fronteira e valide-o contra o schema do **superior**. É
> a única prova de que o pacote produz o que o resto da estrutura consome. Sem isso, o gate é
> **tautológico**: você provou que o seu schema aceita o que o seu código escreveu.
>
> **3. Recalcular em código, sem ler o campo declarado.** Se o contrato diz "menor nota, nunca
> média", o teste calcula o mínimo a partir do scorecard e compara com o campo — e um caso prova
> que a média **daria outro número**. Conferir se o campo existe não é conferir se a regra vale.

Blocos que todo validador precisa ter. As quatro primeiras linhas da tabela vêm **prontas** de
`_compartilhado/verificacoes_pacote.py` — você passa nomes, caminhos e limites, não reimplementa.
Modelo de uso: `departamento-auditoria-responsabilidades/evals/validate_workflow.py`.

| Bloco | Prova |
|---|---|
| `validate_structure()` | arquivos obrigatórios, `agentes/` com os nomes canônicos, mínimo 3 e sem teto artificial, vínculos externos existem |
| `validate_metadata()` | frontmatter, ≤ 1024 chars, ≤ 500 linhas, `short_description` de 25–64 chars |
| `validate_normative_source()` | fonte única citada no caminho relativo correto **de cada nível**, tokens de contrato presentes |
| `validate_links()` | **todo** link markdown interno resolve em arquivo existente |
| `validate_schema_shape()` | `$defs` esperadas, `$ref` resolvem, `enum` de identidades = pastas reais |
| `validate_inherited_authority()` | os schemas do superior **ainda** atribuem a você o que você produz — quebra aqui se o outro lado mudar |
| fixtures positivas | cada envelope legítimo é aceito |
| fixtures negativas | cada atalho proibido pelo contrato é rejeitado |
| fronteira | envelope derivado validado contra o schema do consumidor |
| aritmética | as regras de cálculo recalculadas em código |

**`PLACAR.md`** — o relato honesto. Tabela com coluna **"Executado?"** e uma seção
**"O que ainda não foi provado"**, com `SKIP` declarado e motivo. Regra da casa: *prova executada >
checklist*, e **sucesso simulado é violação** (RI-04).

> **Nunca escreva um `FORWARD-TEST.md` com respostas que ninguém produziu.** Um relatório de teste
> comportamental só existe depois que uma instância independente respondeu aos prompts de verdade e
> as respostas foram conferidas. Inventar as respostas para "fechar o pacote" é fabricar resultado —
> a violação mais grave desta estrutura, e a mais difícil de detectar depois.

**Concluído quando:** o validador roda e passa, e o `PLACAR.md` diz com todas as letras o que **não**
foi provado.

### Passo 10 — Fechar os vínculos e provar que nada quebrou

Um pacote novo não termina em si mesmo. Percorra a cascata:

1. **`ORGANOGRAMA.md`** — marque `[x]` no estado da migração com o número real do validador; atualize
   a árvore canônica se o pacote tiver pastas além do mínimo; complemente a seção do Departamento com
   o que ele decidiu; atualize **`## Estado desta etapa`**.
2. **References do superior** — procure e corrija toda menção a "**futuro** `<seu-pacote>`". Elas
   existem: o superior foi escrito quando você ainda não existia.
   ```bash
   grep -rn "futuro\|ainda não\|quando for migrado" --include="*.md" "Estrutura Final de Skills"
   ```
3. **Evals do superior** — o `evals/README.md` do CEO declara que os prompts comportamentais **devem
   ser reexecutados** quando Diretor, Negócios ou Juízes forem migrados. Registre essa dívida no seu
   `PLACAR.md` se não executar agora.
4. **Regressão completa** — o motor compartilhado **e todos** os validadores da árvore,
   descobertos por varredura, sem lista fixa. Lista fixa envelhece: a versão anterior deste passo
   nomeava cinco comandos e deixava **onze pacotes de fora**, chamando o resultado de "completa".
   ```bash
   cd "Estrutura Final de Skills"
   PYTHONIOENCODING=utf-8 python "_compartilhado/teste_validador_schema.py"
   for f in $(find . -name validate_workflow.py | sort); do
     d=$(dirname $(dirname "$f"))
     printf "%-42s " "$(basename "$d")"
     (cd "$d" && PYTHONIOENCODING=utf-8 python evals/validate_workflow.py 2>&1 | grep -ioE '[0-9]+/[0-9]+' | tail -1)
   done
   ```
   O terminal do Jeremias é cp1252 e os validadores imprimem seta: **sempre**
   `PYTHONIOENCODING=utf-8`. Cada validador roda a partir da **própria pasta do pacote** — ele
   infere a raiz da estrutura pelo caminho do próprio arquivo.

   Contagem que muda sem mudança de contrato é regressão, não melhoria — anote a contagem de cada
   pacote **antes** de mexer no motor compartilhado.
5. **Número de vizinho carrega data, ou não entra.** A patologia medida em 2026-07-26 foi o
   inverso da fraude: **onze de quinze** placares declaravam para si um número **menor** que o
   real, porque cada frente congelou o número do vizinho no instante em que rodou e o vizinho
   cresceu depois. Seis congelaram o motor compartilhado em 55 quando ele já estava em 61. Ao citar
   um pacote que não é seu, escreva o valor **e a data da medição**; ao citar um total de cadeia,
   escreva **quais** validadores ele soma. "Cadeia integrada: 377/377" sem denominador vira, dois
   meses depois, um número órfão que ninguém consegue reproduzir.
6. **Integridade do legado** — recalcule os hashes do passo 2 e prove que a fonte não mudou.
7. **Git** — commite antes de abrir frentes paralelas: enquanto um arquivo estiver untracked, uma
   sessão em worktree **não o enxerga** e o trabalho parece ter sumido. (Em 2026-07-26,
   `Estrutura Final de Skills/` já tinha 252 arquivos rastreados e 157 ainda não — inclusive o
   `departamento-desenvolvimento/` inteiro. Confira com `git status`, não com memória.)

**Concluído quando:** todo validador da cadeia passa, o organograma conta o estado verdadeiro e o
legado tem os mesmos hashes do passo 2.

---

## 5. Armadilhas conhecidas

Cada uma custou uma correção real em pelo menos um dos três pacotes:

1. **Profundidade de caminho.** Departamento operacional está **um nível mais fundo** que
   `departamento-juizes` — a pasta `departamentos-operacionais/` no meio. Copiar os `../../../` do
   modelo sem recontar quebra a fonte normativa em silêncio. Use a tabela do passo 3 **e** o teste de
   links.
2. **Redefinir o envelope do consumidor** no schema local. Funciona hoje e diverge no dia em que o
   superior mudar, sem nenhum teste acusando. Consuma o schema do superior.
3. **Gate tautológico.** Validador que confere apenas presença de string, ou que valida o artefato
   contra o próprio schema que o gerou, prova só coerência interna. Ver as três regras do passo 9.
4. **Nota estimada para cobrir ótica ausente.** Qualquer forma de "assume neutro e segue" converte
   lacuna em aprovação. Lacuna abre bloco, proíbe a saída positiva e é **nomeada como lacuna** — não
   como defeito de quem entregou.
5. **Promover evals do legado.** Eles medem o gatilho e a saída antigos. Reescreva.
6. **Frontmatter com chave extra** (`version`, `tipo`, `tags`). O validador rejeita: só `name` e
   `description`.
7. **`short_description` fora de 25–64 caracteres.** Erro silencioso e chato de achar sem teste.
8. **Deixar "futuro X" no texto do superior** depois que X existe. O leitor seguinte acredita.
9. **Usar o legado como fallback** "só enquanto não migra". Ausência de capacidade é lacuna
   declarada e bloqueio, nunca substituição silenciosa.
10. **Declarar pronto sem prova comportamental.** Mecânica verde ≠ skill que aciona e adere.
    Complete e diga o que falta — o organograma tem coluna para isso.
11. **Copiar o motor de schema para dentro do pacote.** Já aconteceu: a cópia do
    `diretor-de-lentes` ficou sem `exclusiveMaximum` e nenhum teste acusou, porque cada validador
    só testava a si próprio. Importe de `_compartilhado/` e, ao mexer no motor, rode o teste dele
    **antes** dos validadores.

---

## 6. Checklist de aceite — copie para a sua frente

```markdown
### Identidade e posição
- [ ] name do frontmatter = nome da pasta = nome no ORGANOGRAMA.md
- [ ] superior e canal de retorno declarados e coerentes com o organograma
- [ ] posição na árvore canônica confere com a do organograma

### Proveniência (migração)
- [ ] tabela arquivo → SHA-256 da fonte, tirada ANTES de escrever
- [ ] recorte preservado / reescrito / não copiado, cobrindo todos os arquivos da fonte
- [ ] legado intacto: hashes recalculados ao final batem com os do início

### Contrato estrutural (ORGANOGRAMA.md)
- [ ] papel declarado: CEO | Diretor | Departamento | Agente
- [ ] superior responsável e canal de retorno
- [ ] responsabilidades próprias
- [ ] proibições e limites de atuação
- [ ] entradas aceitas e saídas obrigatórias
- [ ] evidências exigidas
- [ ] regra explícita de que orquestra e NÃO executa (CEO, Diretor, Departamento)
- [ ] regra de que toda entrega passa pelo departamento-juizes antes do fechamento
- [ ] referência à fonte única regras-de-ouro/REGRAS-DE-OURO.md, no caminho relativo do nível
- [ ] compromisso de bloquear a operação em conflito com as Regras de Ouro

### Arquivos
- [ ] SKILL.md, CONTRATO-DE-COMPROMISSO.md, agents/openai.yaml
- [ ] references/ com protocolo e (migração) origem-migracao.md
- [ ] ADR para cada decisão que contraria legado, organograma ou ADR anterior
- [ ] schemas/ quando o pacote materializa envelope próprio
- [ ] agentes/ com mínimo 3 e quantidade justificada, cada um com os 3 arquivos

### Limites mecânicos
- [ ] frontmatter só com name e description
- [ ] description <= 1024 caracteres, entre aspas
- [ ] SKILL.md <= 500 linhas
- [ ] short_description entre 25 e 64 caracteres
- [ ] todo link markdown interno resolve

### Evals
- [ ] evals.json com >= 12 casos, >= 1 real, >= 3 assertions por caso
- [ ] nenhum prompt nomeia a skill
- [ ] validate_workflow.py com casos negativos >= positivos
- [ ] motor e verificações IMPORTADOS de _compartilhado/, nunca copiados
- [ ] validação contra o schema do CONSUMIDOR, não só contra o próprio
- [ ] aritmética do contrato recalculada em código
- [ ] PLACAR.md com coluna "Executado?" e seção do que NÃO foi provado
- [ ] nenhum relatório de teste com resposta que ninguém produziu

### Cascata
- [ ] ORGANOGRAMA.md: estado, árvore, seção do Departamento, estado da etapa
- [ ] nenhuma menção a "futuro <este pacote>" sobrou no superior
- [ ] validadores de toda a cadeia rodados e passando
- [ ] dívida de reexecução dos evals do superior registrada
- [ ] pastas commitadas (senão o worktree não as enxerga)
```

---

## 7. Ordem recomendada das próximas frentes

| # | Pacote | Por que nesta posição |
|---:|---|---|
| ~~1~~ | ~~`departamento-auditoria-responsabilidades`~~ | ✅ **Migrado em 2026-07-26.** Nasceu sem scorecard próprio, pelo ADR-002; a decisão completa está no ADR-003. Com ele e os Juízes no lugar, os dois insumos da `EXECUTIVE_SUBMISSION` passaram a ter produtor. |
| ~~2~~ | ~~`departamento-conteudo-marketing`~~ | ✅ **Criado por consolidação híbrida em 2026-07-26.** Migra seletivamente `redator-tecnologia-ia` e `email-marketing-html`, acrescenta imagem, vídeo, publicidade, estratégia, relatoria e conformidade a partir de pesquisa oficial e documenta o recorte no ADR-007. |
| ~~3~~ | ~~`departamento-registros`~~ | ✅ **Migrado em 2026-07-26.** Quatro agentes separam memória/decisões, estado/handoffs, documentação/materiais e aprendizados/relatórios; ADR-005. |
| 4 | `departamento-desenvolvimento` | Primeiro Departamento de software que **produz candidato** — fecha o circuito produzir → julgar → integrar para código. |
| 5 | `departamento-qa-usabilidade` | Fecha o par prova executada + veredito junto com Desenvolvimento. |
| ~~6a~~ | ~~`departamento-arquitetura-software`~~ | ✅ **Migrado em 2026-07-26.** Seis agentes, cobertura sem autojulgamento e fronteiras com Dados/Desenvolvimento; ADR-006. |
| 6b | `departamento-arquitetura-dados` | Contrato de dados da frente de construção. |
| 7 | `departamento-seguranca` · `departamento-design-ux-ui` | Gates especializados sobre o candidato já circulando. |
| 8 | `departamento-inovacao-melhoria` | Depende de haver histórico para melhorar. |
| — | `departamento-negocios` | **Em paralelo a qualquer um.** Responde ao CEO, não ao Diretor: não bloqueia nem é bloqueado pela fila acima. |

Regra de sequenciamento: um Departamento novo só é útil quando **alguém consome o que ele produz**
ou **ele consome algo que já existe**. Migrar na ordem errada gera pacote válido e ocioso — e pacote
ocioso não recebe prova comportamental, que é justamente o que falta em todos.

---

## 8. Fronteira deste guia

Este guia cobre **como materializar** um pacote. Ele **não** decide quais Departamentos existem
(organograma), o que cada um faz (o contrato dele), nem se uma entrega passa (Departamento de
Juízes). Conflito entre este guia e `ORGANOGRAMA.md`, `AGENTS.md` ou `REGRAS-DE-OURO.md` se resolve
a favor deles, e o guia é corrigido na mesma sessão em que o conflito aparecer.
