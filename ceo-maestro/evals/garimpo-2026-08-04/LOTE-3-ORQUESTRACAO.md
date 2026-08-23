# LOTE 3 — Orquestração, memória e infraestrutura

**Data do garimpo:** 2026-08-04
**Método:** leitura de READMEs e docs por rota crua (`raw.githubusercontent.com`) e, quando o README apontava, das páginas de documentação citadas. Não houve listagem de diretório — só caminhos citados por documento lido.
**Escopo:** 17 repositórios. Todos foram lidos; os casos em que a leitura veio vazia ou insuficiente estão declarados como tal.

## Os sete buracos, por número (referência do relatório)

1. Despacha-e-espera quebra a cadeia
2. Trabalho perdido na queda
3. Concorrência sobre a mesma árvore
4. Identidade que não sobrevive
5. Memória entre sessões
6. Envelope entre agentes
7. Segurança e adversarial

---

## 1. `SWE-agent/mini-swe-agent`

**Fontes lidas:**
- https://raw.githubusercontent.com/SWE-agent/mini-swe-agent/main/README.md
- https://raw.githubusercontent.com/SWE-agent/mini-swe-agent/main/mkdocs.yml
- https://raw.githubusercontent.com/SWE-agent/mini-swe-agent/main/docs/usage/output_files.md
- https://raw.githubusercontent.com/SWE-agent/mini-swe-agent/main/docs/usage/swebench.md

### O que existe lá

**Histórico linear como única fonte de estado.** O README declara que "every step of the agent just appends to the messages and that's it". Não há sessão de shell viva: cada ação roda por `subprocess.run` isolada, o que o README aponta como o que permite trocar por `docker exec` sem mudar o agente. Classe do agente em `src/minisweagent/agents/default.py` (~100 linhas), ambiente em `src/minisweagent/environments/local.py`.

**Trajetória como artefato tipado e versionado.** `docs/usage/output_files.md`: os resultados saem em arquivos `.traj.json` que carregam um campo `trajectory_format: mini-swe-agent-1.1`. Dentro há um objeto `info` com `instance_cost`, `api_calls`, a configuração completa, `mini_version`, `exit_status` e `submission` opcional; e um array `messages` no formato de chat da OpenAI **com um campo extra `extra`** para metadado por mensagem.

**Agregado por chave de instância.** O `preds.json` é "keyed by instance_id", com os campos `model_name_or_path`, `instance_id` e `model_patch`.

**Retomada em lote — e a confissão do limite.** `docs/usage/swebench.md`, comando `mini-extra swebench --model ... --subset verified --split test --workers 4`; flags `-w/--workers` (padrão `1`), `-o/--output`, `--redo-existing` (padrão `False`). E a frase que interessa: **"Trajectories are only saved upon completion, so most likely, you can just rerun the script to complete the tasks next time."**

### A qual buraco se aplica, e como

- **Buraco 2 (trabalho perdido na queda) — achado negativo de alto valor.** Este projeto tem exatamente a nossa doença, admitida por escrito: trajetória só é gravada ao concluir, e a "retomada" é rodar tudo de novo e deixar o que não terminou refazer do zero. A retomada é por **presença de chave no `preds.json`**, não por checkpoint. Serve aqui como **contraexemplo citável**: a nossa regra "grave antes de devolver" é mais forte que a do mini-swe-agent, e o custo do modelo deles é refazer a rodada inteira. Se algum dia alguém propuser "só grava no fim, é mais simples", este é o precedente medido do que se paga.
- **Buraco 6 (envelope).** O campo `extra` **por mensagem** dentro de um array em formato padrão é o padrão a copiar: em vez de inventar um envelope novo, eles mantêm o formato canônico e penduram metadado num slot nomeado. Nosso `causal` (quem pediu, sob qual contrato, em que rodada) cabe nesse formato — mensagem canônica + `extra` com a proveniência —, o que mantém o transcript legível por ferramenta genérica sem perder a custódia. E o `trajectory_format` versionado é a trava que falta em vários dos nossos artefatos: o consumidor sabe contra qual versão está lendo.
- **Buraco 1 (despacha-e-espera).** O modelo "linear, sem shell viva, cada ação é `subprocess.run`" elimina a classe inteira do problema por construção: não existe filho vivo para acordar. É o oposto arquitetural do nosso despacho e vale como referência de trade-off — perde-se paralelismo, ganha-se que nenhum passo depende de um processo que possa ter morrido.

### O que NÃO serve

O `--redo-existing` não é retomada, é o contrário (refazer o que já existe). Não há watchdog, callback, fila nem polling em lugar nenhum do que foi lido — `--workers` é pool de threads, não coordenação entre agentes. As camadas de sandbox citadas (Docker, Podman, Singularity/Apptainer, Bubblewrap, Contree) resolvem isolamento de **execução**, não isolamento de **árvore de arquivos sob auditoria concorrente** (buraco 3): rodar em container não impede duas frentes de escrever no mesmo repositório montado.

---

## 2. `agent37-platform/minions`

**Fontes lidas:**
- https://raw.githubusercontent.com/agent37-platform/minions/main/README.md
- https://raw.githubusercontent.com/agent37-platform/minions/main/CLAUDE.md — **contém só `# CLAUDE.md` e `@AGENTS.md`**, ou seja, é um ponteiro
- https://raw.githubusercontent.com/agent37-platform/minions/main/AGENTS.md — este sim, substantivo

### O que existe lá

**Máquina de estados de três posições, com dono declarado por transição.** Do `AGENTS.md`: `IN_PROGRESS` → `IN_REVIEW` → `DONE`, e a regra de quem move o quê — "System moves to: `in_review` (after successful agent runs); Human moves to: `in_progress`, `done`". A transição de sistema é feita por uma função nomeada, `recordCompletedAgentRun()`.

**Separação dura entre metadado de tarefa e transcript.** Dois bancos, de propósito: o SQLite do Minions (`minions.db`, modo WAL) guarda tarefa, status e configuração por tarefa; os transcritos vivem no **SessionDB do Hermes**. O `AGENTS.md` é explícito: Minions tem **"no message table"**, e o histórico de chat é **projetado do SessionDB sob demanda**.

**Identidade da tarefa ancorada na sessão do agente.** "Each task.id equals the Hermes root session ID". Colunas citadas da tabela de tarefas: `id`, `status`, `agent_model`, `reasoning_effort`, `last_agent_response_at`; timestamps em milissegundos de época.

**Protocolo entre processos em JSONL por stdin/stdout.** Tipos de requisição citados: `chat`, `session.messages.get`, `settings.set`, `scheduledTasks.list`. Eventos de stream: `text_delta`, `thinking_delta`, `tool_progress` (com ciclo running/completed/error), `done` (com sessionId e usage), `error`.

**Sobrevivência do despacho — o achado central.** Três mecanismos citados: (a) o worker Python é subprocesso do `HermesWorkerAdapter` e **"auto-restarts on crash"**; (b) concorrência de runs por **semáforo, padrão 10**; (c) e a frase que responde ao nosso buraco 1 diretamente — **quando o browser desconecta, "the server continues draining the worker stream to completion"**, e só então `last_agent_response_at` é gravado. Há ainda um `Map<taskId, LiveChatRun>` em memória (`server/live-chat.ts`) com TTL de 30 segundos normal e **5 minutos em caso de erro**.

**Layout de estado:** `MINIONS_HOME`, padrão `~/.minions/`, com `data/minions.db`, `logs/`, `workspace/` e `skills/` (registrado em `~/.hermes/config.yaml`). Comandos: `npx minionsai`, UI em `http://localhost:6969`; scripts `npm run dev|build|start|prod|test`.

### A qual buraco se aplica, e como

- **Buraco 1 (despacha-e-espera) — o achado mais forte do lote.** "O servidor continua drenando o stream do worker até a conclusão mesmo com o cliente desconectado" é precisamente a inversão que nos falta. Nos nossos sete agentes travados, quem esperava era o **pai**, e o **filho** não existia mais. Aqui a responsabilidade de drenar não é do observador: é do **plano de controle**, que não é o mesmo processo do consumidor. Aplicação nossa: o gerente que despacha não pode ser o mesmo componente que consome o resultado. Quem drena tem que ser um processo que sobrevive à desconexão do requerente, e a conclusão se registra por escrita (`last_agent_response_at`), não por retorno de chamada.
- **Buraco 2 (trabalho perdido).** O TTL diferenciado — **5 minutos quando houve erro, contra 30 segundos no caminho feliz** — é uma ideia barata e diretamente aplicável: o estado efêmero de uma rodada que falhou vive mais tempo justamente porque é dele que se precisa para diagnosticar e retomar. Nós descartamos igual nos dois casos.
- **Buraco 5 (memória entre sessões).** A separação deles é exatamente a nossa fronteira `memoria` × `estado`, com um detalhe que nós não temos: **eles não copiam o transcript, projetam-no sob demanda de outro banco**. "No message table" é uma trava de duplicação. Nosso equivalente seria: `estado.json` referencia o transcript por identidade, nunca o embute.
- **Buraco 6 (envelope).** O ciclo `tool_progress` com running/completed/error e o `done` carregando `sessionId` + `usage` é um envelope de progresso mínimo e suficiente. O ponto forte é `task.id == root session ID`: a identidade da unidade de trabalho **é** a identidade da sessão, sem tradução no meio.

### O que NÃO serve

O `auto-restarts on crash` é do **subprocesso worker**, não da tarefa: nada no que foi lido diz que a tarefa retoma de onde parou após o restart — o worker volta, o trabalho perdido não é descrito como recuperado. Não copiar isso como se fosse retomada. O semáforo de 10 é limite de concorrência, não isolamento de árvore (buraco 3 não é tocado). E a filosofia declarada — "keep things simple. We handle ONLY the most important cases" — é honesta, mas significa que não há tratamento de borda: não há nada aqui sobre digest, normalização ou identidade de artefato (buraco 4 intocado).

---

## 3. `coder/mux`

**Fontes lidas:**
- https://raw.githubusercontent.com/coder/mux/main/README.md (raso, remete à documentação)
- https://mux.coder.com/llms.txt
- https://mux.coder.com/runtime/worktree
- https://mux.coder.com/reference/cli.md

### O que existe lá

**Runtime de worktree com caminho previsível.** A doc de worktree: cada workspace vira um git worktree em `~/.mux/src/<project-name>/<workspace-name>`, com o exemplo literal
```
~/.mux/src/
  mux-main/
    improved-auth-ux/
    fix-ci-flakes/
```
O `.git` é compartilhado, e a consequência é declarada: "commits created in any worktree are immediately visible to your other worktrees (including your main checkout)". O agente é livre para trocar de branch, entrar em detached HEAD ou criar branch.

**A flag que importa.** `mux run` aceita `--runtime` / `-r` com os valores `local`, `worktree`, `ssh <host>` ou `docker <image>`. Exemplo lido: `mux run --dir /path/to/project "Add authentication"`.

**Execução com limite e código de saída semântico.** Flags de `mux run`: `--dir`/`-d`, `--model`/`-m` (ex.: `anthropic:claude-sonnet-4-5`), `--thinking`/`-t` (`OFF`, `LOW`, `MED`, `HIGH`, `MAX` ou `0`–`9`), `--budget`/`-b` em USD, `--json` (saída **NDJSON**), `--quiet`/`-q`.
Modo de objetivo: `mux run --goal "Ship the migration safely" --goal-budget 5.00 --goal-turns 10`, com **continuações automáticas**. Os códigos de saída são o achado: **`0` completo, `1` erro, `2` orçamento estourado, `3` incompleto** — "incompleto" é um estado próprio, distinto de erro.

**Workflows duráveis.** `mux workflow run ./workflows/research.js --args-json '{"topic":"..."}'` (alias `mux wf run`), com modos de argumento `--arg key=value`, `--args-json`, `--args-file`, `--args-stdin`.

**Confiança explícita por repositório.** `mux trust`, `mux trust --dir /path/to/repo`, `mux trust --revoke` — autoriza automação controlada pelo próprio repositório.

### A qual buraco se aplica, e como

- **Buraco 3 (concorrência sobre a mesma árvore) — o achado mais forte do lote para este buraco.** É a resposta direta ao nosso incidente de canonização durante auditoria: cada frente recebe **um worktree próprio, em caminho determinístico e nomeado pelo workspace**. Aplicação nossa: uma rodada de auditoria abre `~/.mux/src/<projeto>/<rodada>`-equivalente e audita ali; quem canoniza trabalha em outro. A regra que extraímos e que precisa virar trava nossa: **o nome do workspace tem que estar no caminho**, porque é isso que torna a colisão impossível de acontecer por acidente e visível quando acontece.
- **Buraco 4 (identidade que não sobrevive) — atenção, é ressalva, não solução.** O `.git` compartilhado significa que **commit feito em qualquer worktree é imediatamente visível nos outros**. Worktree isola *working tree*, **não isola histórico**. Para o nosso caso — em que um `git merge` converteu fim de linha em 10 358 arquivos e invalidou digest — worktree **não teria evitado nada**: a conversão viaja pelo `.git` compartilhado. Isolamento de árvore e ancoragem de identidade são problemas separados, e este repositório só resolve o primeiro.
- **Buraco 1 (despacha-e-espera).** O código de saída **`3` = incompleto**, separado de `1` = erro, é exatamente a distinção que nos faltou: nossos sete agentes travados não estavam em erro, estavam **incompletos**, e o pai não tinha como saber a diferença. Adotar um estado terminal "incompleto" distinto de "falhou" no envelope de retorno é barato e diagnostica a classe inteira. O `--goal-turns 10` como teto explícito de continuações também é o padrão certo: continuação automática **com teto declarado**, não laço aberto.
- **Buraco 6 (envelope).** `--json` emitindo **NDJSON** (uma linha, um evento) é o formato certo para stream auditável: cada linha é um registro fechado, e um processo que morre no meio deixa as linhas anteriores íntegras. Isso ataca também o buraco 2 — arquivo append-only não perde o que já foi escrito.

### O que NÃO serve

O README do repositório é vitrine e **não** entrega nada técnico — quem quiser reproduzir precisa ir na doc hospedada. A doc de worktree lida **não** especifica os comandos git usados, nem nomes de campo de configuração, nem procedimento de limpeza dos worktrees, nem persistência de sessão; declaro isso como não lido, não como inexistente. O `llms.txt` confirma que **não há seção dedicada a sessões nem a fila de tarefas**. `mux trust` é autorização, não contenção — mesmo problema já registrado na nossa lição "`--allowedTools` não é sandbox".

---

## 4. `OndrejDrapalik/gmux`

**Fonte lida:** https://raw.githubusercontent.com/OndrejDrapalik/gmux/main/README.md

### O que existe lá

Camada de integração tmux/Ghostty para rodar agentes ao lado de dev servers. O que é concreto e relevante:

- **Detecção de agente vivo por inspeção da árvore de processos:** `tmux-agent-detect.sh` identifica quando um processo Claude, Codex ou opencode está de fato trabalhando; `tmux-agent-spinner.sh` é o indicador visual disso.
- **Refresh que não mata quem está trabalhando:** `prefix r` limpa painéis **pulando** processos de agente e de servidor.
- **Detecção de porta viva:** `tmux-live-port-watcher.sh` marca janelas com listener TCP local.
- **Persistência de sessão via `tmux-resurrect`:** `prefix C-s` salva, `prefix C-r` restaura; `prefix O` restaura grupos nomeados via `tmux-cohort.sh`.
- Instalação: `ln -sf "$(pwd)/dotfiles/tmux.conf" ~/.tmux.conf`, `cp -R dotfiles/tmux/scripts ~/.tmux/scripts`; templates JSON de workspace em `~/.config/gmux/templates/`, lançados por `prefix G`.

### A qual buraco se aplica, e como

- **Buraco 1 (despacha-e-espera).** O `tmux-agent-detect.sh` é a peça conceitual: **liveness verificada por introspecção da árvore de processos, não por promessa de quem despachou.** Nossos sete agentes ficaram esperando porque ninguém perguntou ao sistema operacional se o filho existia. A pergunta "esse PID/processo ainda está aí?" é respondível em qualquer plataforma e é a checagem mais barata que temos disponível antes de declarar "aguardando retorno". O `prefix r` que pula processos de agente é a mesma ideia aplicada à destruição: **não limpe o que ainda está vivo** — nossa versão seria não redespachar nem sobrescrever custódia de uma rodada cujo processo ainda respira.

### O que NÃO serve

O README **não documenta nenhuma integração com git worktree** — apesar do nome sugerir, buraco 3 não é tocado. `tmux-resurrect` restaura **painéis e layout**, não estado semântico de trabalho: é restauração de terminal, não retomada de tarefa; não confundir com buraco 2. Nada sobre envelope, memória ou identidade de artefato. É o repositório de menor rendimento do lote, mas o `agent-detect` justifica a leitura.

---

## 5. `DeusData/codebase-memory-mcp`

**Fonte lida:** https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/README.md

### O que existe lá

**O modelo de memória é grafo de código, não prosa.** Extrai via ASTs tree-sitter (158 linguagens) funções, classes, métodos, interfaces, enums, tipos, rotas e recursos; e as **relações**: cadeias de chamada, imports, herança, roteamento HTTP, padrões async, canais (Socket.IO, EventEmitter, pub-sub) e fluxos de dados. Inclui infraestrutura como nó de grafo: Dockerfile, manifests Kubernetes, overlays Kustomize. Resolução semântica de tipo por LSP híbrido para 11 linguagens.

**A resposta ao "como evitar que a memória minta quando o código muda" — o achado central deste repositório.** Não é revalidação sob demanda: são **watchers em segundo plano com detecção de mudança baseada em git**. Configuração nomeada:
- `auto_watch` (padrão `true`) — registra o projeto no watcher de fundo;
- `auto_index` — reindexação automática ao início da sessão MCP para projetos novos.

E a gradação de custo que vale copiar: os watchers exportam **dois níveis de artefato** — snapshot de melhor qualidade com `zstd -9` na indexação explícita, e atualização incremental rápida com `zstd -3` pelos watchers.

**Ferramentas MCP (15), por grupo:**
- indexação: `index_repository`, `list_projects`, `delete_project`, `index_status`
- consulta: `search_graph`, `trace_path` (alias `trace_call_path`), `detect_changes`, `query_graph`, `get_graph_schema`, `get_code_snippet`, `get_architecture`, `search_code`
- gestão: **`manage_adr`** (Architecture Decision Records) e `ingest_traces`

**Armazenamento:** padrão `~/.cache/codebase-memory-mcp/`, SQLite em **modo WAL**. Artefato comprimido opcional `.codebase-memory/graph.db.zst`, descrito como "snapshot comprimido do grafo de conhecimento que vive ao lado do seu código". Logs em `${CBM_CACHE_DIR}/logs/`: `cbm-daemon.log`, `daemon-conflicts.ndjson`, `activation-events.ndjson`.

**Comandos:** `codebase-memory-mcp config list|set|reset` (ex.: `config set auto_index true`, `config set auto_index_limit 50000`); `install|update|uninstall`; modo CLI de um tiro sem daemon — `codebase-memory-mcp cli index_repository --repo-path /absolute/path`, `cli search_graph --project X --name-pattern '.*Handler.*'`, `cli trace_path --project X --function-name Search --direction both`, `cli query_graph --project X --query 'MATCH (f:Function) RETURN f.name LIMIT 5'`; UI de grafo com `--ui=true --port=9749`.

**Variáveis de ambiente:** `CBM_CACHE_DIR`, `CBM_DIAGNOSTICS`, `CBM_LOG_LEVEL`, `CBM_WORKERS`, `CBM_MEM_BUDGET_MB`, **`CBM_ALLOWED_ROOT`** (restringe `index_repository` a caminhos dentro do diretório).

### A qual buraco se aplica, e como

- **Buraco 5 (memória entre sessões) — o achado mais forte do lote para este buraco.** A memória deles **não guarda conclusões, guarda estrutura derivável**, e por isso pode ser invalidada mecanicamente quando o git muda. É a diferença que nos falta: a nossa memória guarda lição (não derivável, não invalidável por diff) e o estado guarda tarefa. Falta o terceiro tipo — **o índice derivado, que tem que ter data de validade amarrada ao commit**. A ferramenta `detect_changes` é exatamente o gancho: perguntar "o que mudou desde a última indexação" antes de confiar no índice.
- **Buraco 5, segundo ângulo — `manage_adr` dentro do mesmo grafo.** Decisão de arquitetura vive junto com o código que ela governa, consultável pela mesma interface. Nossa Estrutura tem ADRs em `references/` de cada pacote, soltos do artefato que governam. Este é o padrão para amarrar.
- **Buraco 3 (concorrência).** `daemon-conflicts.ndjson` é um **log dedicado a conflito de daemon**, em NDJSON. Nós não temos artefato equivalente: quando duas frentes colidiram sobre a mesma árvore, não havia onde a colisão ficasse registrada — foi descoberta pelo estrago. Um log append-only só de colisões é barato e teria datado o nosso incidente.
- **Buraco 4 (identidade).** O par `zstd -9` (snapshot canônico) × `zstd -3` (incremental) separa **o artefato que serve de âncora** do **artefato que serve de cache**. Nossa confusão no incidente de EOL foi tratar todo arquivo como âncora. Aqui há dois níveis declarados, com custo diferente.
- **Buraco 7, tangencialmente.** `CBM_ALLOWED_ROOT` é contenção real de escopo de leitura — restringe por caminho, não por permissão de ferramenta. É o tipo de trava que a nossa lição "`--allowedTools` não é sandbox" pedia.

### O que NÃO serve

O índice é de **código-fonte**, não de artefatos de governança: ele não vai indexar envelope JSON, contrato ou parecer — nossa cadeia de 81 skills não é o alvo dele. O `auto_index` só dispara para **projetos novos** no início da sessão, não é revalidação universal. E o modelo de invalidação é por **mudança de arquivo detectada pelo git**: nada garante que a *conclusão* derivada continue válida — só que a *estrutura* foi reindexada. Para memória de lição (a nossa), esse mecanismo não se aplica: lição não é invalidada por diff.

---

## 6. `Forward-Future/loopy`

**Fonte lida:** https://raw.githubusercontent.com/Forward-Future/loopy/main/README.md

### O que existe lá

**Laço com condição de parada declarada antes de agir.** Um loop precisa responder quatro perguntas — objetivo, critério de sucesso, o que fazer com os resultados, condições de parada — e **exige fronteira finita de execução antes de agir**. A mecânica de execução: relê o estado corrente antes de cada passagem, faz **uma ação limitada por iteração**, aplica a checagem de aceitação depois de cada passagem.

**As seis condições de parada, nomeadas:** sucesso, no-op, bloqueador, fronteira de aprovação, limite esgotado, ou **ausência de progresso mensurável**.

**O recibo — o achado central.** Cada execução devolve um recibo com a definição do loop (ou referência imutável a ela) **mais as condições de aceitação**, ações, evidência e **motivo da parada**, preservado "so a later debrief can reproduce what ran".

**Sem efeito colateral automático:** o sistema "does not quietly start schedules, change production, publish content, or send messages on your behalf".

**Persistência:** loops de projeto salvos em `LOOPS.md` na raiz, com nome, explicação de uma frase, o prompt exato, data de gravação e URL de origem se adaptado. **Se a fonte publicada mudar, o Loopy avisa e oferece comparação antes de reusar.** O catálogo usa Durable Object com SQLite e mantém **revisão append-only a cada publicação**; exportação em `catalog-backup.ndjson`.

**Comandos:** instalação `npx skills add Forward-Future/loopy --skill loopy --agent codex -g -y`; publicação (mantenedor) `LOOP_PUBLISH_TOKEN=... npm --prefix loop-library/worker run loop:publish -- /path/to/loop.json`; invocação `/loopy [request]` (Claude Code, Cursor) ou `$loopy [request]` (Codex). Template de registro em `loop-library/worker/examples/loop.json`.

### A qual buraco se aplica, e como

- **Buraco 1 (despacha-e-espera).** "Motivo da parada" como **campo obrigatório do recibo**, escolhido de uma lista fechada de seis, é a trava que nos falta. Nossos agentes pararam sem motivo declarado — e "parei porque esperava alguém" nem sequer é um dos seis, o que já denuncia o estado como ilegítimo. Adotar uma enumeração fechada de motivos de parada, validada por schema, torna o travamento **impossível de registrar como conclusão**.
- **Buraco 1, segunda peça.** "Ausência de progresso mensurável" como condição de parada de primeira classe ataca diretamente a nossa lição "objetivo com teto prende o destravável": cinco rodadas reprovando o mesmo pacote é exatamente um laço sem essa condição.
- **Buraco 4 (identidade).** "definição do loop **ou referência imutável** a ela" — o recibo carrega o contrato ou um ponteiro imutável para ele, nunca uma cópia mutável. E o alerta quando a fonte publicada muda é a versão comportamental do nosso problema de digest: **detectar que a âncora mudou e recusar reuso silencioso**. É o que faltou quando o EOL virou.
- **Buraco 2 (trabalho perdido).** Revisão **append-only** a cada publicação, com export em `catalog-backup.ndjson`: nada é sobrescrito, então uma queda no meio da escrita não destrói a versão anterior.
- **Buraco 6 (envelope).** O recibo é praticamente o nosso envelope de retorno bem-feito: definição + critérios de aceitação + ações + evidência + motivo de parada, tudo num artefato só, projetado para reprodução posterior.

### O que NÃO serve

`LOOPS.md` é markdown de prosa na raiz do projeto — não é estado validado por schema, e não substitui `estado.json`. O catálogo é hospedado (Cloudflare Durable Object), o que não replica aqui. E o "recibo" descrito é contrato de comportamento, não formato: **o README não publica o schema do recibo**, então a estrutura acima é a enumeração dos campos citados, não uma especificação lida.

---

## 7. `witt3rd/oh-my-hermes`

**Fonte lida:** https://raw.githubusercontent.com/witt3rd/oh-my-hermes/master/README.md
**Nota:** a rota `/main/README.md` retornou **HTTP 404**; o repositório usa `master`.

### O que existe lá

Coleção de oito skills para o Hermes Agent, com "consensus planning, requirements interviewing, and verified execution". Skills nomeadas: `omh-deep-research`, `omh-ralplan` (planejamento por consenso), **`omh-ralplan-driver`** (despacha as execuções), `omh-ralph` (execução verificada), **`omh-ralph-driver`** e `omh-ralph-task`, `omh-deep-interview`, `omh-triage` (consenso multi-papel, v0.1), `omh-autopilot` (encadeia tudo).

**Estado local ao projeto, autossemeado.** "OMH self-seeds a `.omh/` directory in the project on first use (with the plugin installed)". Artefatos de pesquisa em `.omh/research/{slug}-report.md` **com marcadores de status**. Inicialização manual por `omh_state(action="init")`.

**A fronteira declarada — o achado.** "**No persistent memory across projects**" — e o que atravessa entre skills é **o relatório confirmado**, descrito como "the durable handoff between skills".

**Disciplina de despacho quantificada.** Uma sessão típica de pesquisa usa "5-8 `delegate_task` calls", com **teto de três tentativas** antes de expor status `BLOCKED`.

O plugin opcional em Python (3.10+, pyyaml) adiciona "hook-based role injection, **atomic state management**, and evidence gathering", documentado em `docs/plugin.md`. Instalação: `hermes skills tap add witt3rd/oh-my-hermes`.

### A qual buraco se aplica, e como

- **Buraco 1 (despacha-e-espera) — o padrão do "driver".** Há um componente separado e nomeado cujo único papel é **despachar** (`omh-ralplan-driver`, `omh-ralph-driver`), distinto de quem planeja e de quem executa. Nossa cadeia funde gerente-que-decide com gerente-que-despacha; separar dá um lugar onde a disciplina de retomada pode morar sem contaminar a especialidade.
- **Buraco 1, segunda peça — `BLOCKED` com teto de 3.** Estado terminal explícito para "não consegui", alcançado por contagem, não por julgamento. É a mesma família do `exit 3` do mux: **travamento tem que ter nome e ser alcançável por regra**, não por o agente perceber que travou (que é exatamente o que não acontece).
- **Buraco 2 (trabalho perdido).** "Atomic state management" citado como função do plugin, e artefatos de pesquisa gravados em arquivo **com marcador de status** — ou seja, o artefato intermediário existe em disco antes da conclusão, e carrega em si o quanto já está pronto. É a forma do nosso "grave antes de devolver".
- **Buraco 6 (envelope).** "O relatório confirmado é o handoff durável entre skills": o envelope entre etapas é um **artefato revisado e confirmado**, não uma mensagem em memória. Combina com a nossa custódia.
- **Buraco 5 (memória).** A escolha deliberada de **não ter memória entre projetos** é uma fronteira mais dura que a nossa, e vale como referência: o que atravessa sessão é artefato em `.omh/`, não memória do agente.

### O que NÃO serve

Não há detalhe de formato: nenhum schema, nenhum nome de campo, nenhum exemplo de `delegate_task`. "Atomic state management" é afirmação do README, sem mecanismo lido — `docs/plugin.md` não foi buscado. Nada sobre isolamento de árvore, digest ou concorrência (buracos 3 e 4 intocados). Os números "5-8 chamadas" e "3 strikes" são disciplina de uso, não trava verificável.

---

## 8. `modelcontextprotocol/servers`

**Fontes lidas:**
- https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md (índice de topo)
- https://raw.githubusercontent.com/modelcontextprotocol/servers/main/src/memory/README.md

**Escopo declarado (o que ficou de fora):** o repositório é um catálogo grande, com dezenas de servidores de referência e centenas de integrações de terceiros. Fui **só** ao servidor de memória, por ser o único que toca um buraco nomeado (5 e 6). **Não** li `src/filesystem`, `src/git`, `src/sequentialthinking`, `src/time`, nem qualquer servidor de terceiro — apenas registrei os caminhos de referência abaixo. Não afirmo nada sobre o conteúdo deles.

### O que existe lá

Servidores de referência e seus caminhos, do README de topo: `src/memory` ("Knowledge graph-based persistent memory system"), `src/filesystem` ("Secure file operations with configurable access controls"), `src/git` ("Tools to read, search, and manipulate Git repositories"), `src/sequentialthinking` ("Dynamic and reflective problem-solving through thought sequences"), `src/time`.

**O modelo de memória de `src/memory`, lido em detalhe.** Três primitivas, e só três:
- **Entity** — `name` (identificador único), `entityType` (ex.: "person", "organization"), `observations` (array de fatos discretos).
- **Relation** — `from` (nome da entidade origem), `to` (nome da entidade destino), `relationType`, com a regra de estilo declarada: **descrição em voz ativa**.
- **Observation** — unidade atômica de informação, string, presa a uma entidade e **gerenciável independentemente**.

**Ferramentas:** `create_entities`, `create_relations`, `add_observations`, `delete_entities` (remove nós **e relações em cascata**), `delete_observations`, `delete_relations`, `read_graph`, `search_nodes` (por nome, tipo ou conteúdo de observação), `open_nodes` (por nome).

**Armazenamento:** arquivo padrão **`memory.jsonl`**, caminho customizável por `MEMORY_FILE_PATH`. Exposto também como recurso `memory://knowledge-graph` (MIME `application/json`). Setup por `npx -y @modelcontextprotocol/server-memory` ou Docker com volume `claude-memory:/app/dist`.

### A qual buraco se aplica, e como

- **Buraco 5 (memória).** A granularidade é o achado: **observação atômica, deletável isoladamente**. Nossa memória é markdown por tema — quando uma lição envelhece, não há operação de remover *aquele fato* sem reescrever a nota. `delete_observations` existe justamente porque memória que só cresce apodrece. E o formato **`.jsonl`** (uma linha por registro) é append-friendly: escrita que morre no meio perde a última linha, não o arquivo — o que também serve ao **buraco 2**.
- **Buraco 6 (envelope).** `from` / `to` / `relationType` em voz ativa é o mínimo viável de um registro causal, e o nosso `causal` (quem pediu, sob qual contrato, em que rodada) é um superconjunto disso. Vale como sanidade: se o nosso envelope não consegue responder "quem → quem, que relação", ele é mais fraco que o exemplo canônico do MCP.
- **Buraco 5, ressalva de projeto.** `delete_entities` com **cascata sobre relações** é a política que evita relação órfã apontando para nó inexistente. Nossa cadeia de custódia tem o risco simétrico: apagar um artefato sem apagar as referências a ele.

### O que NÃO serve

O grafo é de **fatos declarados pelo agente**, sem qualquer verificação contra a realidade — nada aqui impede a memória de mentir; ao contrário do `codebase-memory-mcp`, não há watcher, não há detecção de mudança, não há invalidação. É armazenamento, não verdade. Também não há versionamento, digest, nem proveniência: uma observação não carrega quem a escreveu nem quando. Para a nossa cadeia, isso é insuficiente como está — serve o **modelo de dados**, não a implementação.

---

## 9. `microsoft/ai-agents-for-beginners`

**Fonte lida:** https://raw.githubusercontent.com/microsoft/ai-agents-for-beginners/main/README.md

**Escopo declarado (o que ficou de fora):** curso com muitas lições; li **só o README de topo** para mapear quais lições tocam os buracos. **Não abri nenhuma lição.** Portanto os itens abaixo são **ponteiros verificados de nome e pasta**, não conteúdo lido. Ficaram fora todas as lições de introdução, frameworks, uso de ferramentas e as demais não listadas.

### O que existe lá (ponteiros, por buraco)

| Lição | Pasta | Buraco que promete tocar |
|---|---|---|
| Multi-Agent Design Pattern | `08-multi-agent` | 1, 6 |
| Planning Design Pattern | `07-planning-design` | 1 |
| Metacognition Design Pattern | `09-metacognition` | 1 (autoavaliação de progresso) |
| Agentic RAG | `05-agentic-rag` | 5 |
| Context Engineering for AI Agents | `12-context-engineering` | 5, 6 |
| Managing Agentic Memory | `13-agent-memory` | 5 |
| Building Trustworthy AI Agents | `06-building-trustworthy-agents` | 7 |
| AI Agents in Production | `10-ai-agents-production` | 2 |
| Securing AI Agents | `18-securing-ai-agents` | 7 |

### A qual buraco se aplica, e como

Como **rota de leitura futura**, não como achado. Se houver uma segunda passada, a ordem que rende para esta base é `13-agent-memory` → `12-context-engineering` (buraco 5, onde nossa fronteira memória×estado precisa de contraste) e `08-multi-agent` (buraco 6, envelope). `09-metacognition` interessa porque autoavaliação de progresso é o que faltou aos sete agentes travados.

### O que NÃO serve

É material didático, não implementação de referência: não espere schema, comando ou trava executável. Nada aqui é evidência de nada — e, por regra desta base, **ponteiro não é achado**. Registrado como mapa, com a leitura declarada como não feita.

---

## 10. `openclaw/openclaw`

**Fonte lida:** https://raw.githubusercontent.com/openclaw/openclaw/main/README.md

### O que existe lá

Assistente pessoal que roda nos dispositivos do usuário e o encontra nos canais que ele já usa. A peça arquitetural: **o Gateway**, descrito como "the local control plane for sessions, tools, events, and channel connections", conectando modelos, ferramentas, canais de mensagem e apps companheiros **através de um único ponto**. Interfaces coordenadas pelo Gateway: Control UI, CLI e TUI. Canais integrados: WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage.

**Comandos lidos:** `openclaw onboard --install-daemon`, `openclaw gateway status`, `openclaw dashboard`, `openclaw pairing approve <channel> <code>`.

Extensibilidade por ferramentas, skills e plugins, com SDK de plugin e o marketplace ClawHub.

### A qual buraco se aplica, e como

- **Buraco 1 (despacha-e-espera).** Duas ideias transferíveis. Primeira: **o plano de controle é um daemon** (`--install-daemon`), não um processo de sessão — ele sobrevive ao cliente que o invocou, que é a propriedade que faltou aos nossos sete agentes. Segunda: **existe um comando de saúde do próprio plano de controle**, `openclaw gateway status`. Nós não temos o equivalente: não há como perguntar à cadeia "você está viva e o que está em voo?". Um `status` que enumere despachos em aberto teria transformado sete travamentos silenciosos em uma pergunta de um comando.
- **Buraco 6 (envelope), por analogia.** Um Gateway único que normaliza sete canais heterogêneos num só plano de sessões/eventos é o mesmo papel que o `ceo-maestro` exerce como porta única. Vale como confirmação de desenho, não como técnica.

### O que NÃO serve

O README é de produto e **não** documenta formato de sessão, esquema de evento, fila, persistência, nem nome de arquivo de configuração — declaro isso como não lido. `pairing approve` é controle de acesso a canal, não custódia de trabalho. Nada sobre worktree, digest ou memória. Rendimento baixo para esta base: o valor é o par daemon + `status`.

---

## 11. `garrytan/gstack`

**Fonte lida:** https://raw.githubusercontent.com/garrytan/gstack/main/README.md

### O que existe lá

Toolkit que transforma o Claude Code num time de engenharia: 23+ especialistas acionados por slash commands, num sprint Think → Plan → Build → Review → Test → Ship → Reflect.

**Encadeamento por artefato — o achado central.** A descrição é literal: `/office-hours` gera documentos de design que alimentam `/plan-ceo-review`, que produz planos estruturados que `/plan-eng-review` consome. **"Each stage writes artifacts the next stage reads, preventing gaps."**

**Comandos nomeados:** `/office-hours` (interrogatório de produto, 6 perguntas forçantes), `/autoplan` (encadeia CEO → design → eng review automaticamente), `/review` (auditoria de staff engineer com correções automáticas), `/qa`, `/ship`, `/land-and-deploy`, `/cso` (auditoria de segurança OWASP + STRIDE), `/learn`, e **`/freeze`**.

**Estado e configuração:** config global em `~/.gstack/config.yaml`; estado por projeto no diretório `.gstack/`; `CLAUDE.md` lista as skills disponíveis por projeto; `.claude/` para setup local do repositório. Variáveis `GSTACK_ANTHROPIC_API_KEY`, `GSTACK_OPENAI_API_KEY`. Telemetria desligada por padrão, `gstack-config set telemetry off`. Setup: `git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack` e `./setup`; `setup --team` para gstack compartilhado.

**Isolamento e checkpoint:** sessões independentes de Claude Code; o Conductor permite 10-15 sprints paralelos, cada um em workspace isolado. **`/freeze` restringe edições a diretórios específicos durante depuração.** E: "Optional checkpoint mode with `WIP:` commits (crash-safe)". `/pair-agent` coordena múltiplos agentes por sessões de browser isoladas por aba, com tokens escopados.

### A qual buraco se aplica, e como

- **Buraco 3 (concorrência sobre a mesma árvore) — `/freeze` é o achado.** É a trava mais barata do lote inteiro: **restringir edição a um conjunto de diretórios enquanto uma operação corre**. Exatamente o que faltou quando uma frente canonizou arquivos durante a auditoria de outra. Não exige worktree, não exige lock de sistema de arquivos, não exige processo novo: é uma declaração de escopo de escrita, verificável. Nossa versão: durante inspeção, a raiz auditada entra congelada, e qualquer escrita fora do escopo declarado é recusada pelo próprio gate.
- **Buraco 2 (trabalho perdido) — commits `WIP:` como checkpoint.** Descrito literalmente como "crash-safe". A análise pronta em memória que perdemos três vezes teria sobrevivido como commit `WIP:` num worktree próprio. É retomada por git, sem infraestrutura nova, e o prefixo torna trivial distinguir checkpoint de entrega.
- **Buraco 6 (envelope) e buraco 1.** "Cada etapa escreve artefatos que a próxima lê, prevenindo lacunas" é a nossa cadeia de custódia dita em uma frase — e a consequência é que **nenhuma etapa espera outra viva**: espera-se por **arquivo em disco**, não por processo. Isso é a resposta estrutural ao despacha-e-espera: se o handoff é sempre artefato, o filho pode morrer que o pai lê o que ficou.

### O que NÃO serve

As métricas de produtividade citadas (810×, 11 417 linhas/dia) são autorrelato do autor, sem metodologia auditável — irrelevantes aqui e não devem ser citadas como evidência de nada. "Workspaces isolados" para sprints paralelos é afirmado, mas o README **não** diz que são worktrees git nem descreve o mecanismo; não confundir com o mux, que documenta o caminho. `/pair-agent` depende de sessões de browser, fora do nosso contexto. Nada sobre digest ou identidade de artefato.

---

## 12. `DietrichGebert/ponytail`

**Fonte lida:** https://raw.githubusercontent.com/DietrichGebert/ponytail/main/README.md

### O que existe lá

Skill que impõe disciplina de código mínimo por uma **escada de decisão de sete degraus**, aplicada depois de entender o problema: (1) isto precisa existir? → pula (YAGNI); (2) já existe nesta base? → reusa; (3) a stdlib faz? → usa stdlib; (4) recurso nativo da plataforma? → usa nativo; (5) dependência já instalada? → usa; (6) cabe em uma linha? → uma linha; (7) só então: implementação mínima viável. Restrições de segurança declaradas fora da escada: "trust-boundary validation, data-loss handling, security, and accessibility are never on the chopping block".

**Comandos:** `/ponytail [lite|full|ultra|off]`, `/ponytail-review` (aponta over-engineering no diff atual), `/ponytail-audit` (varre o repositório), **`/ponytail-debt`** (extrai anotações `ponytail:` adiadas), `/ponytail-gain`, `/ponytail-help`.

**Configuração e estado:** `PONYTAIL_DEFAULT_MODE` (`lite`, `full`, `ultra`, `off`); `~/.config/ponytail/config.json` (Windows: `%APPDATA%\ponytail\config.json`); entrada opcional de statusLine em `~/.claude/settings.json`; **`PONYTAIL_SUBAGENT_MATCHER`**, regex que escopa em quais subagentes o ruleset é injetado (ex.: `explore|general`). Regras always-on em `AGENTS.md`; hooks de ciclo de vida em `hooks/`; desinstalação por `node scripts/uninstall.js`.

### A qual buraco se aplica, e como

- **Buraco 1, obliquamente — `PONYTAIL_SUBAGENT_MATCHER`.** É o mecanismo mais interessante para nós: **regra injetada seletivamente por tipo de subagente, por regex.** Nossa cadeia injeta contrato uniformemente; poder escopar "esta disciplina vale para agentes-folha, não para gerentes" é a diferença entre regra aplicável e regra ignorada. Aplicação direta: a disciplina de "grave antes de devolver" precisa valer para **todo** despachado, e um matcher explícito torna isso verificável em vez de esperado.
- **Buraco 2, por analogia — `/ponytail-debt`.** Anotação inline (`ponytail:`) que um comando depois **coleta e materializa**. O padrão é: o trabalho adiado fica marcado **no lugar onde aconteceu**, e é colhido por varredura, não por memória de quem adiou. Nossa versão: o que a rodada não conseguiu concluir fica marcado no artefato, e um comando de colheita produz a lista de pendências — imune à morte da instância.
- **Buraco 6.** Modo com quatro níveis (`lite|full|ultra|off`) e variável de ambiente que fixa o padrão é o modelo de "intensidade declarada" que o nosso `required_level` (PRODUCAO / INTERNO) já exerce. Confirmação de desenho.

### O que NÃO serve

O núcleo — a escada de sete degraus contra over-engineering — é disciplina de **código**, não de orquestração, e não toca nenhum dos sete buracos. Os ganhos citados (redução de ~54%, "100% safety compliance") são autorrelato sem metodologia lida. `AGENTS.md` como "regra always-on auto-carregada" é exatamente a armadilha que esta base já mediu: **aviso em prosa não previne erro**. Não replicar. Rendimento: baixo, salvo o matcher.

---

## 13. `Panniantong/Agent-Reach`

**Fonte lida:** https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/README.md

### O que existe lá

Camada de capacidade que abstrai acesso a plataformas para agentes — "handles selection, installation, health checks, and routing".

**Roteamento por lista ordenada de backends com fallback automático — o achado.** As cadeias são publicadas literalmente:
- Twitter: `twitter-cli` → `OpenCLI` → `bird`
- B站: `bili-cli` → `OpenCLI` → Search API (com `yt-dlp` marcado como **deprecado após 2026-06**)
- YouTube: `yt-dlp` (primário); Web: Jina Reader; RSS: feedparser

**Diagnóstico como comando de primeira classe:** `agent-reach doctor` revela quais backends estão ativos e o estado da configuração. Outros: `agent-reach install` com `--safe`, `--dry-run`, `--env=auto`; `agent-reach uninstall`.

**Configuração:** `~/.agent-reach/config.yaml`, **permissão 600, local-only**. O instalador cria um `SKILL.md` no diretório de skills do agente, o que habilita a seleção autônoma de ferramenta. Requer permissão de exec habilitada — usuários de OpenClaw precisam de `tools.profile: "coding"`.

### A qual buraco se aplica, e como

- **Buraco 1 (despacha-e-espera) — `doctor` + fallback ordenado.** Duas peças. A primeira: **um comando cuja única função é dizer o que está vivo agora.** Nossa cadeia não tem `doctor`; se tivesse, os sete travamentos seriam uma linha de saída. A segunda: **cadeia de fallback declarada e ordenada** — quando o backend primário não responde, o próximo assume por regra publicada, não por improviso do agente. Aplicado aqui: um despacho que não retorna deveria cair para um caminho alternativo **declarado no contrato**, não deixar o pai esperando.
- **Buraco 4, tangencialmente.** `yt-dlp` marcado como deprecado **com data** (`após 2026-06`) na própria tabela de roteamento é a prática que nós já exigimos ("número de vizinho carrega a data da medição, ou não entra"), aplicada a capacidade em vez de medição. Confirma o padrão.

### O que NÃO serve

O domínio — acesso a Twitter, B站, YouTube, RSS — é irrelevante para esta base. A instalação por prompt em linguagem natural apontando para um `install.md` remoto, com o agente executando `pip install` autonomamente, é **exatamente o vetor de ataque** que o item 7 deste lote nos manda procurar: código não auditado executado por instrução vinda de URL. Registrar como antipadrão, não como técnica. Nada sobre memória, envelope, worktree ou checkpoint.

---

## 14. `gadievron/raptor`

**Fonte lida:** https://raw.githubusercontent.com/gadievron/raptor/main/README.md

### O que existe lá

RAPTOR (Recursive Autonomous Penetration Testing and Observation Robot) encadeia análise estática, análise de binário, validação de vulnerabilidade por LLM, geração de exploit e escrita de patch num fluxo só.

**Pipeline validador de seis estágios, cada um com uma pergunta própria:**
- **A** — validação de padrão: separar vulnerabilidade genuína de ruído de ferramenta
- **B** — pré-requisitos do atacante e barreiras defensivas
- **C** — existência do caminho de código e alcançabilidade externa
- **D** — checagem final de viabilidade (código de teste, precondições irreais)
- **E** — viabilidade de exploit binário, quando há artefato compilado
- **F** — **auto-revisão contra hedging e contradições**

**Três motores de varredura complementares:** Semgrep (123 regras próprias, taint tracking para SQLi, XSS, SSRF, desserialização, cripto fraca); Coccinelle (54 regras, casamento estrutural C/C++ para segurança de memória e bugs de inteiro); CodeQL (8 queries, taint interprocedural com **solver SMT Z3**).

**Comandos:** `/scan /path/to/code`, `/agentic /path/to/code`, `/validate` (validação isolada de achados anteriores), `/project create myapp --target /path`, `/binary investigate /path/to/binary`.

**Configuração:** `~/.config/raptor/models.json`; contexto de ameaça por projeto em `threat-model.json` e `THREAT_MODEL.md`; scorecard de modelos em `out/llm_scorecard.json`.

**A trava estatística — o achado mais forte deste repositório.** O acordo entre modelos é medido por **intervalo de confiança de Wilson a 95%, no nível da célula `(model, decision_class)`**, e o sistema "only short-circuits once the Wilson 95% upper-bound on the cell's miss-rate falls at or below 5%". Teto de custo por execução: `--max-cost-usd`, padrão `$10`.

### A qual buraco se aplica, e como

- **Buraco 7 (adversarial) — e diretamente a nossa lição "nota de instância única não decide".** Nós medimos que a mesma lente em duas instâncias variava até 3 pontos e que 3 de 8 vereditos eram sorte de instância; a resposta que demos foi `NAO_DISCRIMINADO` perto do corte. O RAPTOR responde a mesma pergunta **com estatística nomeada**: só para de consultar quando o limite superior de Wilson a 95% sobre a taxa de erro **daquela célula** cai a ≤5%. Isto é adotável quase literalmente: célula = (instância de lente, classe de veredito); enquanto o limite superior da taxa de erro estiver acima do corte, **exija mais uma opinião**. Substitui nosso critério qualitativo por um gatilho calculável.
- **Buraco 7, segunda peça — estágio F.** Um estágio dedicado a **auto-revisão contra hedging e contradição** é o que falta aos nossos pareceres: o verificador tem que ser obrigado a reler a própria conclusão procurando linguagem evasiva. Casa com a nossa lição "reclassificar não é consertar" — hedging é a forma textual da evasão.
- **Buraco 7, terceira peça — estágio C.** "Existência do caminho de código e alcançabilidade externa" é o teste que separa achado teórico de achado explorável. Nossa auditoria tem o equivalente por fazer: uma trava declarada sem call site é o análogo exato de uma vulnerabilidade sem caminho alcançável — e a nossa lição "verificar presença não é verificar efeito" é a mesma descoberta, chegada por outro caminho.
- **Buraco 4, obliquamente.** `out/llm_scorecard.json` acumula desempenho de modelo **entre projetos** — a métrica de confiabilidade do juiz é artefato persistido, não impressão. Nós não temos histórico de acurácia por lente.

### O que NÃO serve

O alvo é vulnerabilidade em código-fonte e binário; **nada aqui ataca um verificador de auditoria**, que é o que o item 7 do briefing pede em sentido estrito. As 123 + 54 + 8 regras são de classes de bug (SQLi, XSS, memória), sem tradução para conformidade de processo. `--max-cost-usd` é controle de orçamento, não de qualidade. O que se leva é **método de decisão sob incerteza**, não conteúdo de regra.

---

## 15. `dinosn/raptor-loop-hunt`

**Fonte lida:** https://raw.githubusercontent.com/dinosn/raptor-loop-hunt/main/README.md

### O que existe lá

Skill de Claude Code que faz varredura iterativa de vulnerabilidade por metodologia multifase, em vez de passada única.

**O ciclo de três tempos:** **Generate** (candidatos em várias granularidades, de sistema a função) → **Judge** (avaliação adversarial que tenta **refutar** falsos positivos) → **Verify** (validação **direto do código-fonte cru**).

**Os três componentes arquiteturais nomeados — o achado central:**
- **`raptor-loop-kb`** — base de conhecimento **monotônica**: "scrutiny levels only increase across runs". O nível de escrutínio **nunca desce** entre execuções.
- **`raptor-loop-ledger`** — **livro-razão de disposição**: máquina de estados que certifica **toda transição de achado com evidência**.
- **`raptor-loop-exec`** — corretor de execução: PoC roda em sandbox de menor privilégio, com portão de capacidade.

**Arquivos:** `SKILL.md` (metodologia e rubrica de severidade), `references/vuln-class-discovery.md` (procedimentos de busca por classe), `scripts/raptor-loop-kb`, `scripts/raptor-loop-exec`.

**Invocação:** `/plugin marketplace add dinosn/raptor-loop-hunt`, `/plugin install raptor-loop-hunt@raptor`, `/raptor-loop-hunt`; ou implicitamente por "audit this", "find every bug", "security-review it". Resultado reivindicado: 200+ vulnerabilidades verificadas em 40+ bases reais (Kafka, Redis, memcached, Samba).

### A qual buraco se aplica, e como

- **Buraco 7 — monotonicidade do escrutínio é o achado transferível do lote inteiro para auditoria.** "Níveis de escrutínio só aumentam entre execuções" é a trava contra a evasão mais fácil que existe numa cadeia como a nossa: **rebaixar a exigência para fazer o candidato passar**. Nossa lição "reclassificar não é consertar" descreve exatamente uma tentativa disso, pega pelo gate. A generalização deles é mais forte que a nossa: em vez de proibir uma manobra específica, tornam **matematicamente impossível** a categoria — o escrutínio é monotônico crescente, por construção da base de conhecimento. Aplicação: o nível de exigência aplicado a um pacote entra no `estado` como valor que só sobe; uma rodada que tente aplicar critério mais frouxo que a anterior é recusada pelo próprio validador, sem julgamento humano.
- **Buraco 7, segunda peça — o ledger.** Máquina de estados que exige **evidência em toda transição** de disposição do achado. É a nossa cadeia de custódia aplicada ao veredito: não é possível mover um achado de "aberto" para "descartado" sem depositar o porquê. Nossa lição "ausência de evidência permanece ausência" é o mesmo princípio; o ledger é a **implementação** dele.
- **Buraco 7, terceira peça — "Verify direto do código-fonte cru".** A verificação **não** consulta a análise que gerou o candidato: volta à fonte. É a nossa "origem independente", que aqui tem taxa de acerto perto de 100%, encontrada por outro time e nomeada como estágio obrigatório do ciclo. Confirmação externa forte de que o método é o certo.
- **Buraco 1, obliquamente.** O ciclo Generate → Judge → Verify tem **papéis separados por adversarialidade**: quem gera não julga, quem julga não verifica. Nossa separação juiz × auditoria × gerente é a mesma família.

### O que NÃO serve

`raptor-loop-exec` (sandbox de PoC com portão de capacidade) é para executar exploit, sem uso aqui. A rubrica de severidade e o `vuln-class-discovery.md` são de classes de vulnerabilidade de código. Os números reivindicados (200+ em 40+ bases) são autorrelato sem metodologia lida — não citar como evidência. E, importante: nada em nenhum destes dois repositórios de segurança descreve **como plantar um caso que o verificador deveria pegar e não pega**; o que se lê é como *não deixar passar*, não como *fabricar a armadilha*. Nossa "origem independente" continua sem par externo lido.

---

## 16. `scadastrangelove/awesome-ai-security-tools`

**Fonte lida:** https://raw.githubusercontent.com/scadastrangelove/awesome-ai-security-tools/main/README.md

### O que existe lá

Catálogo curado. Extraí só o que toca teste adversarial, verificação de agente e integridade de cadeia de suprimentos.

**Red-teaming e avaliação de LLM:**
- `garak` — https://github.com/NVIDIA/garak — "The LLM vulnerability scanner", sonda injeção de prompt, jailbreak e vazamento
- `PyRIT` — https://github.com/microsoft/PyRIT — Python Risk Identification Tool, usado em 100+ operações de red-team
- `promptfoo` — https://github.com/promptfoo/promptfoo — CLI de avaliação e red-teaming com 50+ plugins de ataque
- `HarmBench` — https://github.com/centerforaisafety/HarmBench — framework padronizado (ICML 2024) de red-teaming automatizado
- `wallbreaker` — https://github.com/JailbreakAI/wallbreaker

**Detecção de injeção de prompt:**
- `spikee` — https://github.com/ReversecLabs/spikee — kit de avaliação e exploração de injeção **com geração de dataset** e integração com Burp
- `promptmap` — https://github.com/utkusen/promptmap — scanner em modo white-box e black-box
- DeBERTa v3 Prompt Injection v2 (protectai) e Prompt Guard 86M (Meta), ambos no Hugging Face

**Auditoria e verificação de agente — o grupo que mais interessa:**
- `agent-audit` — https://github.com/scadastrangelove/agent-audit — "Forensic auditor for local AI coding agents", **296 regras embutidas**
- `SkillSpector` — https://github.com/NVIDIA/SkillSpector — "Security scanner for AI-agent **skills**", combina análise estática, checagens AST/YARA e revisão opcional por LLM
- `Snyk Agent Scan` — https://github.com/snyk/agent-scan — scanner para agentes, servidores MCP e **agent skills**
- `Ramparts` — https://github.com/highflame-ai/ramparts — scanner em Rust para servidores MCP e bundles de skill, com regras YARA

**Integridade de cadeia de suprimentos:**
- `modelscan` — https://github.com/protectai/modelscan
- `Fickling` — https://github.com/trailofbits/fickling — decompilador/reescritor/analisador estático de pickle Python
- `GuardDog` — https://github.com/DataDog/guarddog — detecção de pacote malicioso em PyPI, npm, Go, RubyGems
- `AIsbom` — https://github.com/Lab700xOrg/aisbom` — SBOM para IA/ML

### A qual buraco se aplica, e como

- **Buraco 7 — `SkillSpector`, `Ramparts` e `Snyk Agent Scan` varrem exatamente o nosso artefato: skills.** Esta base tem 81 pacotes de skill com scripts Python dentro (`emitir_governanca.py`, `inspecao_executada.py`, `validate_workflow.py` e afins). Nenhum deles nunca passou por um scanner de skill. É a aplicação mais direta e imediata do lote: rodar um scanner de bundle de skill sobre `Estrutura Final de Skills/` e sobre os runtimes `.claude/skills/` e `.agents/skills/`. `Ramparts` usa YARA e é Rust (roda em Windows); `SkillSpector` combina AST e YARA.
- **Buraco 7 — `spikee` gera dataset de ataque.** É a peça mais próxima do que o briefing pede: **fabricar casos que o verificador deveria pegar**. Geração de dataset de injeção é a mecânica de "plantar o caso"; adaptá-la de injeção de prompt para plantio de não-conformidade é o passo que falta, e é nosso, não deles.
- **Buraco 7 — `promptfoo` com 50+ plugins de ataque e `garak`** são o caminho para transformar "origem independente" em bateria repetível, em vez de exercício manual.
- **Buraco 4, obliquamente — `GuardDog`, `modelscan`, `Fickling`, `AIsbom`.** Todos atacam a mesma pergunta que o nosso incidente de EOL: **este artefato é o que ele diz ser?** O padrão SBOM (`AIsbom`) é o mais transferível: inventário declarado do que compõe a entrega, conferível contra o que está lá.

### O que NÃO serve

É catálogo — **nenhuma ferramenta foi lida além do nome e da descrição de uma linha**. Nada aqui é achado verificado; são ponteiros com URL, e a própria página avisa que cada ferramenta mantém a licença original e deve ser verificada antes do uso. Os classificadores do Hugging Face são modelos hospedados, fora do nosso regime offline. E a maioria do catálogo (guardrails de runtime, scanners de modelo, defesa de inferência) trata de proteger LLM em produção, o que não é o problema desta base.

---

## 17. `calesthio/OpenMontage`

**Fonte lida:** https://raw.githubusercontent.com/calesthio/OpenMontage/main/README.md

### O que existe lá

Sistema agêntico de produção de vídeo. O domínio é irrelevante aqui; **a mecânica de pipeline é o achado**, e é substancial.

**Pipeline declarado em manifesto, com skill por estágio.** 12 pipelines como manifestos YAML em `pipeline_defs/`; a sequência de estágios é literal: `research -> proposal -> script -> scene_plan -> assets -> edit -> compose`. Cada estágio tem uma **skill diretora** — arquivo Markdown em `skills/pipelines/` — que instrui o agente. O ciclo por estágio: o agente lê o manifesto, consulta a skill do estágio, invoca ferramentas Python, **auto-revisa contra critérios** e **faz checkpoint do estado antes de prosseguir**.

**Checkpoint com trilha de decisão — o achado central.** Estado de produção persistido como checkpoints JSON, registrando conclusão de estágio com timestamp, decisões criativas **e alternativas consideradas**, snapshots de custo, provedor escolhido, portões de aprovação humana e suas transições, com trilha de auditoria que sobrevive a revisões. A frase que importa: **"Every major creative and technical choice — provider selection, style/playbook choice, music track, voice selection, renderer family, any fallback or downgrade — is logged with alternatives considered, confidence scores, and reasoning."** Checkpoints são **retomáveis**, e versões superadas são **arquivadas**, não apagadas.

**Portões não negociáveis:** "Human approval gates are enforced, not suggested". Pausam em proposta, roteiro, plano de cena, assets gerados e publicação. Validação pré-composição bloqueia render que viole as promessas de entrega; auto-revisão pós-render (ffprobe, amostragem de frames, análise de áudio) **rejeita saída ruim antes de apresentá-la**.

**Comandos e estrutura:** `make setup`; `python -m backlot open` (biblioteca) e `python -m backlot open <project-id>` (quadro ao vivo); `python scripts/backlot_simulate_run.py` (execução simulada). Diretórios: `pipeline_defs/`, `skills/`, `tools/` (auto-descoberto), `remotion-composer/`, `projects/<project-name>/`. Registro de ferramentas inspecionável por
`python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.support_envelope(), indent=2))"`.

### A qual buraco se aplica, e como

- **Buraco 2 (trabalho perdido na queda) — o achado mais forte do lote para este buraco.** "Checkpoint do estado **antes de prosseguir**" é a nossa regra "grave antes de devolver", já implementada e com granularidade de estágio. Nossas três instâncias morreram no ato de escrever o resultado final; aqui o resultado final nunca é o primeiro momento de escrita, porque cada estágio já depositou o seu. E **versão superada é arquivada, não sobrescrita** — a escrita nunca destrói o que existia.
- **Buraco 6 (envelope) — "alternativas consideradas" como campo obrigatório.** O checkpoint não guarda só a decisão: guarda **o que mais estava na mesa, o score de confiança e o raciocínio**. Nosso `causal` responde quem pediu, sob qual contrato, em que rodada — mas **não responde o que foi descartado**. Sem isso, uma auditoria posterior não distingue "escolheu bem" de "só havia uma opção visível". É a adição de campo mais valiosa que este lote sugere.
- **Buraco 6, segunda peça — `support_envelope()`.** Existe um método nomeado que devolve, em JSON, o que o registro de ferramentas suporta. É **capacidade declarada por interrogação do runtime**, exatamente o que o `ceo-maestro` faz ao conferir capacidades por SHA-256 — só que consultável por comando. Nosso equivalente não é interrogável de fora.
- **Buraco 1 (despacha-e-espera).** Duas peças. O portão de aprovação é **um estado do pipeline com transição registrada**, não uma espera por alguém: o pipeline **pausa e persiste**, e a aprovação é um evento que o retoma. Nossos agentes esperavam sem pausar nem persistir. E `backlot_simulate_run.py` é uma execução simulada — a capacidade de **ensaiar o pipeline sem efeito** é o que permitiria reproduzir o travamento sem gastar rodada real.
- **Buraco 4, obliquamente.** A validação pré-composição bloqueia render que viole "delivery promises": a promessa de entrega é declarada antes e conferida contra o artefato produzido. É a forma de identidade que mais nos falta — não hash do arquivo, mas **conformidade do artefato com o que foi prometido**.

### O que NÃO serve

Todo o domínio de vídeo — provedores, música, voz, Remotion, ffprobe — é inaplicável. Os portões de aprovação humana são de gosto criativo, não de conformidade. `python -m backlot open` é UI. E o README **não** publica o schema dos checkpoints JSON: os campos listados acima são os citados em prosa, não uma especificação lida.

---

## Síntese — as travas mais adotáveis, por buraco

| Buraco | Trava concreta | Origem |
|---|---|---|
| 1 | Servidor continua drenando o stream do worker mesmo com o cliente desconectado; conclusão registrada por escrita (`last_agent_response_at`), não por retorno | minions, `AGENTS.md` |
| 1 | Estado terminal "incompleto" (`exit 3`) distinto de "erro" (`exit 1`); `--goal-turns` como teto de continuações | mux, `reference/cli.md` |
| 1 | Motivo de parada obrigatório, de lista fechada de seis — inclusive "sem progresso mensurável" | loopy |
| 1 | Liveness por introspecção da árvore de processos (`tmux-agent-detect.sh`); comando `status` do plano de controle | gmux; openclaw |
| 2 | Checkpoint de estado **antes de prosseguir** a cada estágio; versão superada arquivada, não sobrescrita | OpenMontage |
| 2 | Commits `WIP:` como checkpoint declarado crash-safe | gstack |
| 2 | Formato append-only por linha (NDJSON / `.jsonl`): queda perde a última linha, não o arquivo | mux; MCP memory |
| 3 | `/freeze` — restringir escrita a diretórios declarados durante uma operação | gstack |
| 3 | Worktree por workspace em caminho determinístico `~/.mux/src/<projeto>/<workspace>` | mux |
| 3 | Log dedicado a colisão, append-only (`daemon-conflicts.ndjson`) | codebase-memory-mcp |
| 4 | Recibo carrega a definição **ou referência imutável** a ela; alerta e comparação quando a fonte muda | loopy |
| 4 | Dois níveis de artefato: snapshot âncora (`zstd -9`) × incremental (`zstd -3`) | codebase-memory-mcp |
| 5 | Índice derivado com invalidação por git (`auto_watch`, `detect_changes`) — o terceiro tipo, além de memória e estado | codebase-memory-mcp |
| 5 | Observação **atômica e deletável isoladamente**; entidade/relação/observação como únicas primitivas | MCP `src/memory` |
| 5 | Transcript **projetado** de outro banco, nunca copiado ("no message table") | minions |
| 6 | Formato canônico + campo `extra` por mensagem; `trajectory_format` versionado | mini-swe-agent |
| 6 | Decisão registrada **com alternativas consideradas, confiança e raciocínio** | OpenMontage |
| 6 | Handoff sempre por artefato em disco, nunca por processo vivo | gstack |
| 7 | Escrutínio **monotônico crescente** entre execuções (`raptor-loop-kb`) | raptor-loop-hunt |
| 7 | Ledger que exige evidência em toda transição de disposição de achado | raptor-loop-hunt |
| 7 | Wilson 95% sobre taxa de erro da célula (modelo, classe de decisão) como critério de parar de consultar | raptor |
| 7 | Estágio dedicado a auto-revisão contra hedging e contradição | raptor |
| 7 | Varrer as próprias 81 skills com `SkillSpector` / `Ramparts` / `agent-scan` | awesome-ai-security-tools |

## Declarações de limite desta leitura

- **`microsoft/ai-agents-for-beginners`:** só o README de topo. Nenhuma lição aberta. Os itens da tabela são ponteiros de nome e pasta, não conteúdo.
- **`modelcontextprotocol/servers`:** só o README de topo e `src/memory/README.md`. Não li `src/filesystem`, `src/git`, `src/sequentialthinking`, `src/time`, nem servidores de terceiros.
- **`coder/mux`:** o README do repositório é vitrine; o técnico veio de `mux.coder.com`. Limpeza de worktree, persistência de sessão e formato de configuração **não foram lidos** — declarados como desconhecidos, não como inexistentes.
- **`agent37-platform/minions`:** o `CLAUDE.md` é só um ponteiro (`@AGENTS.md`); o conteúdo veio do `AGENTS.md`.
- **`witt3rd/oh-my-hermes`:** `/main/README.md` deu **404**; lido em `/master/README.md`. `docs/plugin.md` não foi buscado.
- **`awesome-ai-security-tools`:** nenhuma das ferramentas listadas foi lida — só nome, URL e descrição de uma linha do catálogo.
- **Nenhum comando deste documento foi executado.** Tudo é citação de documentação lida.
