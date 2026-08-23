# Forward test de cadeia — CEO Maestro

Data: 2026-07-27
Executor: sessão nova por `claude -p`, fora deste contexto
Saída bruta preservada: `frente4-rodada1.json` (`session_id: 943fd348-7eb6-4657-bca0-9403a036ce97`)
Custo da rodada: 33 turnos, 375 s, US$ 2,67

**Veredito: a cadeia NÃO desceu. A porta abriu, o roteamento aconteceu, e todos os
papéis foram representados por um único contexto.**

Este é o primeiro teste da Frente 4 do [plano](../../PLANO-DE-ACAO-2026-07-27.md), cuja
régua diz: *"Travar é resultado válido, e provavelmente mais informativo que passar."*
Foi o que aconteceu.

## Método

Missão real, pequena e verificável: definir grão, identidade e plano de evolução do
registro de aprendizagem — a pasta `registros/relatorios/aprendizagem/` existe desde
2026-07-26 com apenas um `README.md` e nenhum artefato. O prompt foi operacional e
**não citou nenhuma skill pelo nome**.

Pacote sob teste — o runtime, não a fonte, porque é o que uma sessão nova carrega.
Sincronizado por `deploy-estrutura.ps1` imediatamente antes, com paridade por SHA-256
contra a fonte:

```text
Arquivos: 411
TREE_SHA256: 6dbf4c41f205b027c5feb1af6760d63443442ebb17147dedba713e781ce56398
```

Recalculado **depois** da rodada: **idêntico**. O pacote avaliado não foi alterado.

A verificação não usa o relato da rodada: usa a transcrição da sessão aninhada, onde
cada `tool_use` está registrado.

## O que a transcrição prova

| Ferramenta | Chamadas | O que significa |
|---|---:|---|
| `Skill` | **1** — `ceo-maestro` | a porta abriu, e só ela |
| `Task` | **0** | **nenhuma instância separada foi criada** |
| `Bash` | 10 | inclui os `sha256sum` da conferência de capacidades |
| `Read` | 14 | leitura de contratos, protocolos e schemas |
| `Grep` | 3 | busca de precedente de índice |
| `PowerShell` | 2 | 1 negada por permissão |
| `Write` | **1** | gravou no cofre — ver §Isolamento |

### O que passou

1. **A porta aciona sem ser nomeada.** Frase neutra, e o `ceo-maestro` carregou.
2. **A conferência de capacidades por SHA-256 é real, não narrada.** As chamadas 6 e 7
   são `sha256sum` sobre os arquivos do runtime. O relato traz sete digests; eles têm
   comando executado por trás.
3. **O roteamento respeitou o contrato.** `deliverable_type: proposal`, Negócios
   `NAO_SE_APLICA` com motivo, matriz dos dez Departamentos com estado por
   Departamento, e nenhuma missão emitida a `agente-*`.
4. **O gate de nota não foi fabricado.** A rodada devolveu `minimum_score:
   NAO_VERIFICADO` — não um número — declarando que um `JUDGE_REPORT` produzido pelo
   mesmo contexto que produziu o candidato viola a independência do ADR-002. Este é o
   **risco residual R5 sendo recusado pela própria rodada**, e é o resultado mais
   valioso do teste.
5. **Status honesto:** `BLOCKED`, com o bloqueio atribuído ao selo e não ao trabalho, e
   sem pedir exceção — porque o limite é reparável, não objetivo.

### O que falhou

1. **A cadeia não desceu.** `Task: 0`. Não houve `EXECUTIVE_MISSION` entregue a uma
   instância do Diretor, nem `DEPARTMENT_MISSION` a uma instância de Departamento, nem
   tarefa a um agente. Os envelopes existem **como texto no relatório final**, não como
   artefatos trocados entre elos. A própria rodada declarou isso: *"Rodei a cadeia
   inteira num único contexto, sem instância independente."*
2. **Portanto, nada foi provado sobre os elos.** As perguntas da Frente 4 — os digests
   batem entre os envelopes? o agente foi acionado por tarefa assinada? o retorno
   reconcilia com o relatório? — continuam **sem resposta**, porque não houve envelope
   emitido para conferir. `SKIP` declarado, não `PASS`.
3. **A causa é conhecida e simples:** a rodada não acionou subagentes *"porque você não
   pediu"*. O prompt dizia "conduza isso pela estrutura, do começo ao fim" e isso não
   foi lido como autorização para criar instâncias. A próxima rodada precisa autorizar
   a delegação **explicitamente**, ou o teste repete este resultado.

## Isolamento — o erro do operador, registrado

A rodada foi disparada com `--allowedTools "Skill,Read,Glob,Grep,Task"` e anunciada
como "reversível por construção, sem `Write`". **A afirmação estava errada.**

A transcrição mostra `Bash` 10× e `Write` 1×, nenhum dos dois no allowlist. O
`--allowedTools` governa o que é auto-aprovado, **não o que existe**; e o
`settings.local.json` do projeto não concede `Write`. Uma chamada de `PowerShell` foi
negada, então o mecanismo de permissão estava ativo — apenas não era a barreira que se
supôs.

Consequência concreta: a rodada **gravou no cofre** —
`registros/PROPOSTA-GRAO-IDENTIDADE-E-EVOLUCAO-APRENDIZAGEM.md`, 271 linhas, hoje
untracked. O pacote sob teste não mudou (manifesto idêntico), mas a árvore de trabalho
mudou.

**Regra para as próximas rodadas:** isolamento de forward test vem de **rodar contra uma
cópia** — worktree ou diretório temporário —, nunca de um flag de allowlist. Flag não é
sandbox.

## O artefato produzido

Apesar do veredito, a rodada entregou trabalho substantivo e verificável: 271 linhas com
o grão derivado da cardinalidade do schema (`window` e `department_mission_ref`
singulares ⇒ **arquivo é a rodada de colheita, linha é a lição**), o achado de que
`licao_id` é identidade **local ao relatório** — o que impede a Evolução de separar
reincidência de novidade —, e o achado de que `learningReport` é
`additionalProperties: false` **sem `schema_version`**, o que faz qualquer campo novo
exigir edição de pacote de skill, e portanto missão do CEO à Evolução.

Duas decisões subiram ao Jeremias por falta de precedente na Estrutura: o nome do
arquivo de índice, e se `schema_version` entra no `learningReport`.

## Pendências desta frente

1. ~~**Rodada 2, com delegação autorizada no prompt**~~ — executada, ver abaixo.
2. **Julgamento independente** do candidato produzido, em instância separada, pela rota
   canônica (Diretor emite `JUDGMENT_REQUEST`).
3. **Destino do artefato:** decisão do Jeremias — manter, versionar ou descartar.

---

# Rodada 2 — 2026-07-27

Executor: sessão nova por `claude -p`, **em worktree isolado** (`Temp/f4r2`), com a
Estrutura implantada por `deploy-estrutura.ps1` e paridade SHA-256 conferida.
Transcrições preservadas: 1 principal + **3 de subagente**.
Janela: `23:33:13` → morta por `timeout` aos 45 min, com o Diretor ainda em voo.

**Uma única variável mudou em relação à rodada 1:** a autorização explícita de delegação
no prompt. A demanda é literalmente a mesma. O que mudou no resultado é atribuível a
essa autorização.

**Veredito: a cadeia desceu, e a linhagem reconcilia. A rodada não fechou.**

## A cadeia desceu — três níveis, quatro contextos

| Contexto | Papel | Registros | Prova |
|---|---|---:|---|
| principal | `ceo-maestro` | 136 | `Skill: 1`, `Agent: 2` |
| `agent-ac1500e3…` | `diretor-de-lentes` (F1) | 99 | instância própria, em voo no corte |
| `agent-ab431aa2…` | `departamento-evolucao-skills` (F2) | 114 | instância própria, **e `Agent: 1`** |
| `agent-a7b5ce7d…` | `agente-colheita-e-diagnostico` | 132 | **acionado por F2**, não pelo CEO |

O quarto contexto é o achado: o Departamento **acionou sua própria instância folha** para
executar a `EVOLUTION_TASK` — `description: "Executar EVOLUTION_TASK DIAGNOSTICO"`. O CEO
não falou com o agente, como o organograma exige. Na rodada 1 esse número era **zero**.

## Os envelopes existem como artefato

Sete arquivos, na sequência canônica, cada um escrito pelo contexto certo:

```text
00-CONTRATO.md                                     principal (CEO)
01-EXECUTIVE_MISSION-F1-diretor-de-lentes.yaml     principal (CEO)
02-EXECUTIVE_MISSION-F2-departamento-evolucao.yaml principal (CEO)
F2-10-REGISTRO-DE-RECEBIMENTO.yaml                 F2
F2-11-EVOLUTION_TASK-colheita-e-diagnostico.yaml   F2
F2-12-EVOLUTION_RETURN-colheita-e-diagnostico.yaml agente (instância folha)
F2-13-EXECUTIVE_SUBMISSION-departamento-evolucao.yaml  F2
```

Quem escreveu cada um foi conferido na transcrição do respectivo contexto, não pelo nome
do arquivo.

## A linhagem reconcilia — conferida contra o disco

Esta é a pergunta que a Frente 4 fez, e agora tem resposta. Cada digest foi recalculado
**fora** da rodada:

| Campo | Valor no envelope | Confere com |
|---|---|---|
| `contract_digest` (nos 7) | `cd40d585…44db2` | SHA-256 real de `00-CONTRATO.md` ✅ |
| `mission_ref` (F2-13) | `312e5c8c…ee3d6` | SHA-256 real do YAML da missão F2 ✅ |
| `producer_digest` CEO | `ff853efa…3f0b96` | `ceo-maestro/SKILL.md` ✅ |
| `producer_digest` Depto | `5c4076b5…ecf229` | `departamento-evolucao-skills/SKILL.md` ✅ |
| `producer_digest` agente | `d3f6114c…d77fc0` | `agente-colheita-e-diagnostico/SKILL.md` ✅ |

**Cinco de cinco.** O `contract_digest` é idêntico nos sete envelopes — a identidade do
contrato atravessa a cadeia inteira — e o `producer_digest` muda exatamente a cada
produtor. Não há digest apontando para o vazio.

Duas condutas contratuais apareceram sem serem pedidas: o Departamento **conferiu no
disco** a saída do seu agente antes de propagar — *"relato de agente não é evidência"* —,
e a instância folha escreveu um `validar_retorno.py` para checar mecanicamente o próprio
retorno.

## Isolamento — a correção da rodada 1 funcionou

- manifesto do pacote isolado **antes e depois**: `411 arquivos`,
  `TREE_SHA256: 6dbf4c41…ce56398` — idêntico;
- `git status` da fonte da Estrutura no worktree: **0 alterações**;
- as 14 escritas da rodada ficaram todas no `scratchpad` da própria sessão.

A rodada 1 gravou no cofre porque o isolamento era um flag. Rodar contra cópia resolveu.

## O que continua sem prova

1. **A rodada não fechou.** Morta pelo `timeout` de 45 min com o Diretor em voo. Não há
   `EXECUTIVE_DECISION`, não há integração do retorno de F1, e o JSON de saída ficou
   vazio — a evidência desta rodada é a transcrição, não o relatório final.
2. **O ramo do Diretor não completou.** `EXECUTIVE_MISSION` F1 foi emitida e a instância
   rodou 99 registros, mas nenhum `DEPARTMENT_MISSION` chegou a sair dela. A descida
   provada é a do ramo executivo (CEO → Departamento → agente), **não** a do ramo
   técnico (CEO → Diretor → Departamento operacional → agente).
3. **Nenhum julgamento.** Os Juízes não foram acionados — é a Frente 5, e depende desta.
4. **Custo real desconhecido:** sem o JSON final, não há `total_cost_usd` desta rodada. A
   rodada 1, sem delegação, custou US$ 2,67 em 375 s; esta passou de 45 min.

## Próxima rodada

Aumentar o teto de tempo e **fechar o ramo técnico**: a missão precisa exigir um
Departamento operacional sob o Diretor, para que a descida provada inclua
`DEPARTMENT_MISSION`. Manter o isolamento por worktree e a verificação por transcrição —
as duas se provaram.

---

# Rodada 3 — 2026-07-27

Executor: sessão nova por `claude -p`, em worktree isolado novo (`Temp/f4r3`), Estrutura
implantada por `deploy-estrutura.ps1` com paridade conferida.
Janela: `00:42:44` → morta por `timeout` aos **90 min**, com o ramo de Arquitetura em voo.
Demanda: decisão de arquitetura com ADR sobre onde moram as checagens normativas —
escrita para **fechar as saídas fáceis** ("não é modelagem de dado, não é implementação,
não é evolução de skill"), forçando o roteamento pelo Diretor.

**Veredito: o ramo técnico fechou. A cadeia canônica existe em disco, com quatro níveis
de profundidade. E a rodada produziu o achado mais duro desta frente — o digest de
capacidade não é estável entre cópias.**

## O ramo técnico, provado

**14 contextos**, cada um com transcrição própria. A árvore:

```text
principal (ceo-maestro)                        154 regs
└── diretor-de-lentes                           99 regs
    ├── departamento-arquitetura-software      134 regs
    │   ├── agente-modularidade-e-limites
    │   ├── agente-qualidade-e-operacao
    │   ├── agente-alternativas-e-tradeoffs
    │   ├── agente-integracoes-e-contratos
    │   └── agente-adr-e-c4
    ├── departamento-desenvolvimento
    │   ├── agente-revisao-e-refatoracao
    │   └── agente-testes-e-depuracao
    └── departamento-registros
        ├── agente-memoria-e-decisoes
        └── agente-documentacao-e-materiais
```

Alguns agentes acionaram verificação própria — *"Enumerar série ADR e cunhar número"*,
*"Recontagem e verificação independente"*, *"Medição de chamadas nos validadores"* —,
o que leva a profundidade a **cinco níveis** em alguns ramos.

O que a rodada 2 não tinha: o **`DEPARTMENT_MISSION`**. Aqui saíram três, do Diretor para
três Departamentos operacionais, e voltaram dois `DEPARTMENT_RETURN` antes do corte.

## Os 25 envelopes, na sequência canônica

```text
00-CONTRATO-DA-MISSAO.md
01-EXECUTIVE_MISSION.yaml                  CEO   → Diretor
02-DIRECTOR_PLAN.yaml                      Diretor (interno)
03-DEPARTMENT_MISSION-*.yaml  (×3)         Diretor → Departamentos
04-<departamento>/AGENT_TASK-*.yaml (×9)   Departamento → agente
04-<departamento>/AGENT_RETURN-*.yaml (×8) agente → Departamento
05-DEPARTMENT_RETURN-*.yaml (×2)           Departamento → Diretor
```

Preservados em [`forward-test-cadeia-rodada3/`](forward-test-cadeia-rodada3/).

## A linhagem — e onde ela quebra

Recalculado fora da rodada:

| Campo | Envelope | Confere? |
|---|---|---|
| `contract_digest` `7f831aa7…` | os 5 conferidos | ✅ SHA-256 real do `00-CONTRATO-DA-MISSAO.md` |
| `producer_digest` CEO `ff853efa…` | `EXECUTIVE_MISSION` | ✅ `ceo-maestro/SKILL.md` do runtime |
| `producer_digest` Diretor `b82d3850…` | `DIRECTOR_PLAN`, `DEPARTMENT_MISSION` | ✅ `diretor-de-lentes/SKILL.md` do runtime |
| `producer_digest` Arq. Software `7fe5d967…` | `ARCHITECTURE_TASK` | ❌ runtime é `af890095…` |
| `producer_digest` Registros `d6851428…` | `DEPARTMENT_RETURN` | ❌ runtime é `c834eddf…` |

**A divergência não é fabricação — é pior, e é estrutural.** Os digests dos Departamentos
são o SHA-256 **correto** dos mesmos arquivos na cópia-**fonte** do worktree; os do CEO e
do Diretor são o SHA-256 correto da cópia-**runtime**. Os envelopes até declaram qual
copiaram, em `producer_version`: `fonte-2026-07-27` contra `runtime-2026-07-27`.

Os arquivos são **idênticos exceto pelo fim de linha**. A causa:

- o cofre principal tem a fonte em **LF** (escrita direta) e o runtime em LF (robocopy
  byte a byte) — **os digests batem**;
- o worktree recebeu a fonte por `git checkout` com `core.autocrlf=true`, que a converteu
  para **CRLF**, enquanto o runtime continuou LF — **os digests não batem**.

### Por que isso importa

O contrato do CEO obriga *"verificar caminho, versão, contrato e digest de toda
capacidade antes de acioná-la"*, e o do Diretor repete. **Num clone novo, todo digest de
capacidade diverge** — e um verificador honesto leria isso como adulteração. A identidade
por digest, como está, depende de **como aquela cópia veio a existir**, não do conteúdo.

Foi a cadeia executando que encontrou isso. Nenhum dos 1558 casos determinísticos pega:
eles rodam sempre na mesma cópia.

**Encaminhamento:** ou a identidade passa a ser calculada sobre conteúdo normalizado
(hash com fim de linha canônico), ou `.gitattributes` fixa `-text` para a árvore da
Estrutura, ou o digest passa a nomear explicitamente a cópia — e aí deixa de servir para
comparar entre elas. É decisão de arquitetura, e cabe ao Jeremias abrir a frente.

### O caminho do `.gitattributes` foi tentado em 2026-07-28 — e **não funciona**

A hipótese era de uma linha. O `.gitattributes` já força `text=auto eol=lf` nos **três
espelhos** de skills, com o comentário de que devem permanecer byte a byte idênticos em
qualquer SO; faltava a **fonte** da Estrutura. Acrescentá-la parecia fechar a causa raiz.

Fechou a causa e **abriu outra maior**. Medido, não suposto:

1. Com a regra, um worktree novo passa a receber a fonte em LF — verificado.
2. Mas o `departamento-conteudo-marketing` exige que suas cópias sejam **byte-exatas** em
   relação às fontes legadas, e o legado vive **fora** da árvore da Estrutura, portanto fora
   da regra. Normalizar um lado quebra a igualdade.
3. Resultado no clone novo: `[FAIL] fontes legadas intactas e cópias exatas`. A regra
   **quebra um clone limpo** — pior que o problema que resolve.

Converter também o legado não é opção: ele é preservado como **rollback e evidência
histórica**, com 154 hashes publicados. Reescrever seus bytes destrói a proveniência que
ele existe para guardar.

**Portanto o item fica declarado como limite, não como pendência:** enquanto a Estrutura
contiver cópias byte-exatas de fontes que não estão sob a mesma regra de EOL, o digest de
árvore **não é comparável entre cópias criadas por caminhos diferentes** (escrita direta
× `git checkout`). O que resta como saída real é a primeira alternativa — normalizar o EOL
**dentro da receita do digest** —, e ela contraria o que `digest_de_arvore` documenta hoje
de propósito. É troca de desenho, não conserto.

Tudo o que foi tentado nesta investigação está revertido: `.gitattributes` intacto, cópia
de trabalho intacta, cadeia em 1582 com 0 FAIL.

## Isolamento — funcionou de novo, e mais exercitado

A rodada escreveu **27 arquivos**, entre eles a árvore de linhagem inteira, dentro de
`Estrutura Final de Skills/registros/linhagem/` **da cópia**. Verificado:

- a pasta `registros/linhagem/` existe **só** no worktree; o cofre não a tem;
- manifesto do pacote isolado, antes e depois: `411 arquivos`,
  `TREE_SHA256: 6dbf4c41…ce56398` — **idêntico**.

## O que continua sem prova

1. **A rodada não fechou**, de novo — 90 min não bastaram, com o ramo de Arquitetura em
   voo e um `DEPARTMENT_RETURN` faltando. Duas rodadas seguidas mortas pelo relógio
   deixam de ser acidente: **uma cadeia completa desta estrutura custa mais de 90 minutos
   de parede**, e isso é dado de projeto.
2. **Sem `EXECUTIVE_SUBMISSION` e sem `EXECUTIVE_DECISION`** — o topo nunca recebeu de
   volta.
3. **Nenhum julgamento.** Os Juízes seguem sem ser acionados em nenhuma das três rodadas.

---

# Rodada 4 — 2026-07-27 · **a cadeia fechou**

Executor: sessão nova por `claude -p`, worktree isolado `Temp/f4r4`.
**Demanda idêntica à rodada 3.** Um único fator novo: **orçamento vinculante na missão**
— 25 min de wall-clock, máximo de 8 instâncias, profundidade 4 — com cinco regras:
fatiar antes de delegar; parar é ato contratual; **orçamento muda a completude, nunca a
honestidade**; largura antes de profundidade; fechar o topo.

**Veredito: PASSOU.** `exit=0`, **15,9 min** de 25 no orçamento, 35 turnos, US$ 6,89.
Primeira das quatro rodadas que fecha sozinha.

## O que o orçamento produziu

| | R3 (sem orçamento) | R4 (com orçamento) |
|---|---|---|
| Instâncias | 14 | **4** de 8 permitidas |
| Duração | 90 min, cortada | **15,9 min**, fechou |
| Fechamento do topo | ausente | **`08-EXECUTIVE_DECISION`** |
| Custo | não medido (sem JSON) | **US$ 6,89** |

**A fatia foi propagada e reduzida, como mandado.** O CEO deu 13 min ao Diretor; o
Diretor emitiu a `DEPARTMENT_MISSION` com `budget_slice: wall_clock_minutes: 5`. Ninguém
repassou a fatia inteira.

## A regra 3 aguentou — e é o achado central

Sob pressão de relógio, o sistema **cortou cobertura e declarou a falta**, em vez de
preencher com plausível:

```yaml
producer_digest: "n/a - digest do proprio pacote nao computado nesta rodada
  por corte de orcamento (fatia de 13 min); declarado ausente, nao fabricado"
```

```yaml
minimum_score: null    # ausente por nao-execucao dos Juizes.
                       # Ausencia de evidencia permanece ausencia.
decision: BLOCKED
status_do_entregavel: BLOCKED   # o ADR-014 existe e e verificavel; NAO esta validado
```

Era o risco declarado do desenho: orçamento mal formulado vira licença para fabricar.
Não virou.

## O Diretor recusou uma ordem do CEO — e estava certo

O CEO mandou emitir o retorno como `EXECUTIVE_SUBMISSION`. A barreira de saída do Diretor
proíbe submeter sem `JUDGE_REPORT`. Ele **nomeou o arquivo como ordenado e tipou o
conteúdo como o contrato manda**, declarando o conflito no próprio artefato:

```yaml
# AVISO DE FORMA — o nome do arquivo obedece a instrucao do CEO;
#                  o artifact_type obedece ao contrato.
artifact_type: PROGRESS
state: D_AWAITING_JUDGES
status: PARTIAL
```

E o CEO ratificou: *"a autoridade estava com o contrato, e prefiro um Diretor que me
recusa a um que me agrada"*. É a hierarquia funcionando contra a própria ordem — o
comportamento mais difícil de projetar e o mais fácil de perder.

## A cadeia encontrou dois defeitos reais no repositório

Confirmados por medição independente, **fora** da rodada:

1. **`__all__` do motor não exporta `validate_contratos_de_gerente`**, embora três
   validadores a chamem. Não quebra — o import é direto —, mas é inconsistência.
2. **`departamento-desenvolvimento` é o único dos 15 fora da trava global:** não chama
   `validate_adr_series` **nem** `validate_contratos_de_gerente`.

E corrigiu a premissa que a própria missão trazia: o operador escreveu "sete por-pacote /
três estrutura-inteira"; o real é **14 de 15** chamando `validate_adr_series` e **3 de
15** chamando `validate_contratos_de_gerente`. O "três" existia, mas era o número de
chamadores de *uma função*, não de uma categoria.

Nenhum dos 1558 casos determinísticos pega isso. A cadeia executando, sim.

## Isolamento e integridade

- manifesto do pacote isolado, antes e depois: `411`, `6dbf4c41…ce56398` — idêntico;
- 11 envelopes, de `01-EXECUTIVE_MISSION` a `08-EXECUTIVE_DECISION`, gravados na cópia;
- o `adr-014-checagens-por-pacote-e-de-estrutura-inteira.md` existe, 12.464 bytes, e o
  SHA-256 declarado pelo CEO (`6dd1a8fc…`) confere com o do arquivo.

## O que continua sem prova

1. **Os Juízes seguem sem rodar** — quatro rodadas, zero `JUDGE_REPORT`. É a Frente 5.
2. **Sem Auditoria:** a `DEPARTMENT_MISSION` para `auditoria-responsabilidades` foi
   redigida e gravada, mas não despachada — faltou relógio.
3. **O ADR-014 é proposta, não decisão.** Produzido e verificável, **não julgado e não
   auditado**. Não deve ser tratado como fechado.

---

## Ledger das quatro rodadas

| | R1 | R2 | R3 | **R4** |
|---|---|---|---|---|
| Instâncias | 1 | 4 | 14 | **4 de 8** |
| Profundidade | 1 | 3 | 4–5 | **4** |
| `DEPARTMENT_MISSION` | não | não | sim (×3) | **sim (×2)** |
| Envelopes em disco | 0 | 7 | 25 | **11** |
| Digests conferidos | — | 5/5 ✅ | 3/5 ✅ + 2 por EOL | ausência **declarada** ✅ |
| Isolamento | ❌ cofre | ✅ | ✅ | ✅ |
| Fechou o topo | não | não (45 min) | não (90 min) | **sim (15,9 min)** |
| Custo | US$ 2,67 | — | — | **US$ 6,89** |

**Conclusão da Frente 4.** A cadeia desce, a linhagem reconcilia, o isolamento se sustenta
e — com orçamento — ela **fecha e sabe parar sem mentir**. O que falta para a estrutura
estar exercida ponta a ponta é o gate: os Juízes.
