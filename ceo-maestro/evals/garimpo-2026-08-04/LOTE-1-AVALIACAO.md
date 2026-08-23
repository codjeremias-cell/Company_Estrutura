# Garimpo — Lote 1: avaliação e juízes

**Data da coleta:** 2026-08-04
**Ferramenta:** `WebFetch` sobre `raw.githubusercontent.com` (README e arquivos-fonte) e, quando o README
cru não trazia o conteúdo, sobre a documentação publicada do próprio projeto.
**Regra desta nota:** só entra o que foi lido. Cada item traz a URL exata. O que não consegui ler está
declarado na seção final, com o erro.

**Os oito buracos, por número** (referência curta usada no texto todo):

1. Trava que verifica presença, não efeito.
2. Contagem que cai sem `FAIL`.
3. Número sem receita, raiz e critério.
4. Instrumento que só sabe sair verde.
5. Mutação creditada por exceção.
6. Origem independente.
7. Variância entre instâncias do mesmo juiz.
8. Régua que não fecha.

---

## Sumário executivo — o que este lote resolve e o que não resolve

| Buraco | Melhor achado do lote | Força |
|---|---|---|
| 1 | `agentevals` — `create_trajectory_match_evaluator(trajectory_match_mode=...)` compara o **trajeto executado**; `agentevals-dev` pontua a partir de **traço OpenTelemetry gravado** | alta |
| 2 | `lighteval` — `summary_tasks` conta `truncated`/`non_truncated`, `padded`/`non_padded`, `num_truncated_few_shots` como **categorias próprias**; `lm-eval` detecta sumiço por digest agregado | média (ver ressalva) |
| 3 | `lm-eval` (`doc_hash`/`prompt_hash`/`target_hash` + `upper_git_hash` + `--seed` de 4 sementes) e `lighteval` (`hash_examples`/`hash_full_prompts`/`hash_input_tokens`/`hash_cont_tokens` + `lighteval_sha`/`model_sha`) | **alta — o achado mais forte do lote** |
| 4 | `openai/evals` `docs/build-eval.md` — critério de aceite é o **sujeito reprovar**; `openevals` — avaliadores não-LLM (`pyright`/`mypy`/execução em sandbox) | alta |
| 5 | `strands-agents/evals` — injeção de falha (`Timeout`, `CorruptValues`, `RemoveFields`) **pareada** com avaliador que julga a reação | média |
| 6 | `inspect_evals` `CONTRIBUTING.md` — "*Comparable*": exige baseline externo pré-existente para validar a implementação | baixa (processo humano, não gate) |
| 7 | `inspect_ai` — `--epochs N` + `--epochs-reducer` (`mean`, `median`, `mode`, `max`, `at_least_{n}`, `pass_at_{k}`, `pass_k_{k}`) | **alta** |
| 8 | `promptfoo` — `weight` + `threshold` por assertion + `assert-set` com threshold próprio; `inspect_ai` — redutor sobre N épocas | **alta** |

**O buraco 2 é o menos atendido do lote inteiro.** Nenhum dos nove repositórios trata "caso sumiu" como
categoria de primeira classe ao lado de "caso falhou". O que existe são dois substitutos parciais:
digest agregado sobre os samples (`lm-eval`) e contadores de anomalia de processamento (`lighteval`).
Isso é um achado, não uma lacuna da busca — ver §10.

---

## 1. `EleutherAI/lm-evaluation-harness`

### O que existe lá

**Digest por amostra, encadeado.** Em `lm_eval/evaluator.py` o registro por amostra carrega três hashes:

```python
"doc_hash": hash_string(
    json.dumps(
        requests[0].doc,
        indent=2,
        default=handle_non_serializable,
        ensure_ascii=False,
    )
),
"prompt_hash": hash_string(requests[0].arguments[0]),
"target_hash": hash_string(str(target)),
```

Fonte: <https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/evaluator.py>

A primitiva é sha256 hex, em `lm_eval/utils.py`:

```python
def hash_string(string: str) -> str:
    return hashlib.sha256(string.encode("utf-8")).hexdigest()
```

Fonte: <https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/utils.py>
(o mesmo arquivo traz `convert_pil_to_hash` e `convert_bytes_to_hash`, que resolvem o problema de
"objeto não serializável" antes de hashear — detalhe relevante, porque é exatamente onde um digest
costuma virar não determinístico.)

**Digest da rodada inteira, derivado dos digests de amostra.** Em
`lm_eval/loggers/evaluation_tracker.py`, os hashes de amostra são concatenados e re-hasheados:
`s["doc_hash"] + s["prompt_hash"] + s["target_hash"]`, e depois
`hash_string("".join(sample_hashes))`.
Fonte: <https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/loggers/evaluation_tracker.py>

**Proveniência do ambiente.** O mesmo arquivo define `GeneralConfigTracker` com, entre outros:
`model_source`, `model_name`, `model_name_sanitized`, `system_instruction`, **`system_instruction_sha`**,
`fewshot_as_multiturn`, `chat_template`, **`chat_template_sha`**, `start_time`, `end_time`,
`total_evaluation_time_seconds`. E `lm_eval/loggers/utils.py` acrescenta ao dicionário de resultados
`pretty_env_info`, `transformers_version`, `lm_eval_version` e **`upper_git_hash`** — este último vindo de
`get_git_commit_hash()`, que executa `subprocess.check_output(["git", "describe", "--always"])` com
fallback para `get_commit_from_path()`. Também grava `tokenizer_pad_token`, `tokenizer_eos_token`,
`tokenizer_bos_token`, `eot_token_id`, `max_length`.
Fonte: <https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/loggers/utils.py>

**Sementes plurais e declaradas.** `--seed`: *"Random seeds as single integer or comma-separated list for
`python,numpy,torch,fewshot`. Default: `0,1234,1234,1234`"*.
Fonte: <https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/docs/interface.md>

**`--limit` marcado como inválido para reporte.** A própria referência de CLI diz:
*"Limit examples per task. Integer for count, float (0.0-1.0) for percentage. **For testing only.**"*
Mesma URL acima.

**Versão da task no próprio contrato.** `docs/task_guide.md`: o campo `metadata` é
*"An optional field where arbitrary metadata can be passed. Most tasks should include a `version` key in
this field that is used to denote the version of the yaml config."*
Fonte: <https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/docs/task_guide.md>
E `docs/new_task_guide.md` fecha o ciclo: `metadata: version: 0`, e ao atualizar a task, incrementar o
número e documentar no README com data, número do PR, mudança de versão e descrição.
Fonte: <https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/docs/new_task_guide.md>

**Checklist de submissão que exige equivalência externa** (`docs/new_task_guide.md`, verbatim):
- *"Is the task an existing benchmark in the literature?"* → *"Have you referenced the original paper that introduced the task?"* → *"If so, have you checked against the reference implementation and documented how to run such a test?"*
- *"Have you noted which, if any, published evaluation setups are matched by this variant?"*

**Outros flags relevantes** (`docs/interface.md`): `--log_samples` (*"Save all model inputs/outputs for
post-hoc analysis"*, e *"Required with `--log_samples`"* para `--output_path`), `--samples` (*"JSON mapping
task names to sample indices"* — permite reexecutar exatamente o mesmo subconjunto), `--predict_only`
(*"Save predictions only, skip metric computation"* — separa geração de julgamento), `--show_config`,
`--check_integrity` (*"Run task test suite validation before evaluation"*).

### A qual buraco se aplica, e como usaríamos aqui

**Buraco 3 — este é o modelo a copiar.** Nossos quatro leitores tropeçaram no mesmo digest por quatro
eixos: objeto, ordenação, raiz e fim de linha. O `lm-eval` resolve os quatro por construção, e vale
copiar item a item:

- **objeto** → não se hasheia "o arquivo"; hasheia-se o *doc* serializado com
  `json.dumps(..., indent=2, default=handle_non_serializable, ensure_ascii=False)`. A receita de
  serialização faz parte da definição do digest. Nosso erro foi ter digest sem receita.
- **ordenação** → o digest da rodada é `hash_string("".join(sample_hashes))`: a ordem entra no valor de
  propósito. Se queremos digest insensível à ordem, precisamos ordenar *e declarar que ordenamos*; o que
  não pode é ficar implícito.
- **raiz** → `upper_git_hash` vem de `git describe --always` do repositório, não de um caminho de arquivo.
  Isso é o antídoto direto para a lição *"Digest de arquivo não é identidade"* (EOL do checkout muda o
  sha256): a identidade da rodada é *commit + config + sementes*, e o hash de conteúdo é só um dos campos.
- **fim de linha** → parcialmente resolvido: `ensure_ascii=False` e `encode("utf-8")` fixam a codificação,
  mas o `lm-eval` não normaliza EOL. Nosso problema de EOL **não** é resolvido por eles; a lição é fixar a
  normalização na receita, como eles fizeram com `indent` e `ensure_ascii`.

**Buraco 2, parcialmente.** O digest agregado de amostras é a única defesa mecanizada que encontrei em
todo o lote contra "o overlay apagou 29 casos e publicou 64/64 verde": se um caso some, a lista de
`sample_hashes` muda e o digest da rodada muda, mesmo que o placar continue verde. Não é uma categoria de
resultado, é um alarme lateral — mas é barato e nós não temos.

**Buraco 8.** `--limit ... For testing only` é a formulação enxuta do que nos falta: uma rodada reduzida é
executável e **declaradamente não reportável**. Hoje nós não temos essa distinção; toda rodada nossa se
apresenta como se fosse a rodada plena.

**Buraco 6, fraco mas real.** O checklist *"have you checked against the reference implementation"*
transfere a origem do número de referência para fora do autor. Não é independência de autoria do caso —
é independência do *alvo* de comparação.

### O que NÃO serve

- **`--check_integrity` é uma promessa que não consegui abrir.** A flag existe e diz *"Run task test suite
  validation before evaluation"*, mas `run_task_tests()` **não está** em `lm_eval/utils.py` (verificado).
  Não localizei a implementação, então não sei o que ela executa de fato. **Não copiar sem ler o código** —
  esta base já pagou por "trava que existe mas não roda"; adotar uma flag pela descrição seria repetir o
  buraco 1 na própria compra.
- **Nada distingue amostra ausente de amostra reprovada.** Não há categoria `MISSING`. O `--limit` até
  reduz a contagem, mas a saída não marca a rodada como incompleta de forma estrutural.
- **Nada sobre variância de juiz.** `--seed` fixa amostragem few-shot e RNG do processo, não a
  dispersão entre execuções de um julgador. Buraco 7 não é atendido aqui.
- **Não há pinagem de revisão de dataset documentada.** `dataset_kwargs` é descrito como
  *"Auxiliary arguments that `datasets.load_dataset` accepts"* — dá para passar `revision`, mas o guia não
  exige. Buraco 3 fica meio aberto no eixo "dados de entrada".
- **`--verbosity` está deprecado** em favor da variável `LMEVAL_LOG_LEVEL`. Irrelevante para nós; anotado
  só para não copiar flag morta.

---

## 2. `langchain-ai/openevals`

### O que existe lá

**Fábrica de juiz, assinatura completa** (verbatim do README):

```python
create_llm_as_judge(
    prompt,
    model="openai:gpt-5.4",
    judge=None,
    feedback_key="score",
    continuous=False,
    choices=None,
    use_reasoning=True,
    output_schema=None,
    system=None,
    few_shot_examples=None,
)
```

Fonte: <https://raw.githubusercontent.com/langchain-ai/openevals/main/README.md>

Semântica dos parâmetros que importam para nós, verbatim do mesmo README:
- `continuous`: *"sets whether the evaluator should return a float score somewhere between 0 and 1 instead of a binary score."*
- `choices` (lista de floats): *"sets the possible scores for the evaluator"* — **mutuamente exclusivo com `continuous`**.
- `few_shot_examples`: lista de dicts com `inputs`, `outputs`, `reasoning`, `score`; *"appended to the end of the final user message."*
- `use_reasoning`: desligável com `False`.
- `output_schema` (TypedDict / Pydantic / JSON Schema): *"Passing `output_schema` changes the return value"*.
- `feedback_key` (default `"score"`): nomeia a métrica no resultado.
- Variáveis de prompt por convenção: `inputs`, `outputs`, `reference_outputs`.

Retorno padrão: `{'key': 'score', 'score': True, 'comment': '...'}`.

**Avaliadores determinísticos, sem LLM.** `create_json_match_evaluator` com `aggregator`
(`"average"` / `"all"` / `None`), `list_aggregator` (`"average"` / `"all"`) e `exclude_keys`. E os
avaliadores de código: `create_pyright_evaluator()`, `create_mypy_evaluator()` (args default
`"--no-incremental --disallow-untyped-calls --disallow-incomplete-defs --ignore-missing-imports"`),
`create_typescript_evaluator()`, `create_e2b_pyright_evaluator(sandbox=...)`,
`create_e2b_execution_evaluator(sandbox=...)`, com `code_extraction_strategy` (`"llm"` ou
`"markdown_code_blocks"`) e chave de saída no formato `'key': 'pyright_succeeded'`. Mesma URL.

**Prompts prontos em `openevals.prompts`** — constantes nomeadas, entre elas `CORRECTNESS_PROMPT`,
`CONCISENESS_PROMPT`, `HALLUCINATION_PROMPT`, `ANSWER_RELEVANCE_PROMPT`, `PLAN_ADHERENCE_PROMPT`,
`CODE_CORRECTNESS_PROMPT`, `CODE_CORRECTNESS_PROMPT_WITH_REFERENCE_OUTPUTS`, `LAZINESS_PROMPT`,
`RAG_HELPFULNESS_PROMPT`, `RAG_GROUNDEDNESS_PROMPT`, `RAG_RETRIEVAL_RELEVANCE_PROMPT`,
`TRAJECTORY_ACCURACY_PROMPT`, `TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE`, `PII_LEAKAGE_PROMPT`,
`PROMPT_INJECTION_PROMPT`. Mesma URL.

**Cliente de juiz injetável:**

```python
evaluator = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="gpt-5.4",
    judge=OpenAI(),
)
```

### A qual buraco se aplica, e como usaríamos aqui

**Buraco 4 — o achado real deste repo não é o juiz, são os avaliadores de código.**
`create_pyright_evaluator` / `create_mypy_evaluator` / `create_e2b_execution_evaluator` são instrumentos
que **não podem sair verde por opinião**: quem reprova é o `pyright`, um processo externo com código de
saída próprio. Para nós, isso é a forma de sair de "o medidor publicava 100% de discriminadores para
qualquer entrada": todo critério que puder ser reduzido a um comando externo com exit code deve ser, e o
juiz-LLM fica só no resíduo. É o mesmo princípio das nossas lições — "trave em código, não em texto" —,
mas aplicado ao *avaliador*, não ao avaliado.

**Buraco 8.** `choices` versus `continuous` é a distinção que nos falta explicitada: ou a régua tem um
conjunto **finito e declarado** de valores possíveis, ou é contínua — e os dois são mutuamente exclusivos.
Nossa régua atual mistura: pede "10 em todos os critérios" (binário disfarçado) sobre uma escala 0–10
(contínua). O `aggregator` / `list_aggregator` do `create_json_match_evaluator` é o outro lado: a regra de
agregação (`"all"` = conjunção, `"average"` = média) é **parâmetro declarado**, não convenção implícita.
`"all"` é literalmente a nossa régua de hoje; `"average"` é a que provavelmente fecha.

**Buraco 1, de raspão.** `feedback_key` obriga a nomear a métrica na saída. Um resultado sem nome de
métrica não é agregável nem auditável depois — é um detalhe barato de copiar.

### O que NÃO serve

- **Nada sobre calibrar ou testar o juiz.** Confirmado por leitura dirigida do README: não há orientação
  sobre calibração de juiz, teste do próprio avaliador, self-consistency ou controle positivo/negativo.
  Buracos 4 (na parte "teste do avaliador"), 5 e 7 **não** são atendidos.
- **Nada sobre reprodutibilidade.** Sem versionamento, sem hashing, sem especificação de temperatura para
  consistência do juiz. Buraco 3 não é atendido.
- **Nada sobre agregação entre execuções.** Não há `num_repetitions` nem equivalente documentado no README;
  a repetição fica por conta de orquestração externa (pytest/Vitest + LangSmith). Buraco 7 não é atendido.
- **Nada sobre independência autor/avaliador.** Buraco 6 não é atendido.
- **`few_shot_examples` é armadilha para nós.** Exemplos com `score` colados no fim da mensagem do usuário
  ancoram o juiz — reduzem variância *ao custo de* enviesar para os exemplos. Se adotarmos, tem que ser
  medido como redução de variância, não assumido; caso contrário é o buraco 4 outra vez (instrumento
  ajustado até sair a nota desejada).

---

## 3. `langchain-ai/agentevals`

### O que existe lá

**Comparação determinística de trajeto.** `create_trajectory_match_evaluator()` /
`createTrajectoryMatchEvaluator()`, com variante `create_async_trajectory_match_evaluator()`.
O parâmetro `trajectory_match_mode` tem quatro estratégias, verbatim:
- `"strict"`: *"compares two trajectories and ensures that they contain the same messages in the same order with the same tool calls"*
- `"unordered"`: *"compares two trajectories and ensures that they contain the same tool calls in any order"*
- `"subset"`: trajeto real contém subconjunto das chamadas de referência
- `"superset"`: trajeto real contém superconjunto

**Regras de casamento de argumento.** `tool_args_match_mode` (default `"exact"`): `"exact"`,
`"ignore"` (*"treats any two tool calls for same tool as equivalent"*), `"subset"`, `"superset"`.
E o override por ferramenta:

```python
ToolArgsMatchOverrides = dict[str, Union[ToolArgsMatchMode,
  list[str], Callable[[dict, dict], bool]]]
```

— ou seja, por ferramenta se pode passar um modo, uma **lista de campos** que importam, ou uma função
comparadora própria.

**Juiz de trajeto:** `create_trajectory_llm_as_judge()` / `create_async_trajectory_llm_as_judge()`, com
`prompt`, `model`, `continuous`, `choices`, `system`, `few_shot_examples`.
**Grafo:** `create_graph_trajectory_llm_as_judge()`, `graph_trajectory_strict_match()`,
`extract_langgraph_trajectory_from_thread()`.

Fonte: <https://raw.githubusercontent.com/langchain-ai/agentevals/main/README.md>

### A qual buraco se aplica, e como usaríamos aqui

**Buraco 1 — este é o achado.** Nossa trava contava nós `ast.Call` e um `if False:` a satisfazia. O
`trajectory_match_mode` faz a pergunta certa: não "a chamada aparece no código?", mas "**a chamada
aparece no trajeto que de fato aconteceu?**". A transposição direta para nós: a auto-exigência não deve
inspecionar a AST do validador — deve inspecionar o **registro de execução** do validador e conferir se a
trava aparece lá. `"unordered"` é o modo que serviria (não nos importa a ordem em que as travas rodaram,
só que todas as obrigatórias rodaram); `"superset"` é o modo para "rodou pelo menos as obrigatórias, pode
ter rodado mais".

**Buraco 8, de forma indireta.** `tool_args_match_overrides` com **lista de campos** é a resposta elegante
para "quais partes do artefato importam para o veredito". Nossa régua trata tudo como igualmente
obrigatório; aqui, por chamada, se declara quais campos entram na comparação. Isso é o análogo de banda
por critério, só que aplicado ao objeto comparado em vez de à nota.

### O que NÃO serve

- **Sem threshold configurável.** Confirmado no README: o avaliador devolve `score` booleano ou float, e
  não há configuração de limiar documentada. Buraco 8 não é atendido na parte "banda".
- **Sem agregação entre execuções.** Async existe (`create_async_*`), mas *"No built-in aggregation across
  runs documented; requires external orchestration"*. Buraco 7 não é atendido.
- **Sem reprodutibilidade, versionamento ou hash.** Buraco 3 não é atendido.
- **Depende de um formato de mensagem (OpenAI/LangChain) para extrair o trajeto.** Nossa cadeia não emite
  esse formato. Copiar a *ideia* (comparar trajeto executado contra referência, com modo declarado) é
  barato; copiar a *biblioteca* exigiria adaptar nossos registros ao formato de mensagens dela, o que não
  se paga.

### Comparação com `agentevals-dev/agentevals` (§4)

Os dois atacam o buraco 1, por caminhos opostos, e a diferença é o achado:
- **langchain-ai** compara trajeto contra **referência escrita à mão** — precisa de gabarito, e o gabarito
  é escrito por alguém (buraco 6 volta).
- **agentevals-dev** pontua a partir do **traço já gravado**, sem gabarito e sem reexecução.

Para nós: o primeiro serve para travas *obrigatórias* (sabemos quais deveriam rodar → há gabarito); o
segundo serve para *auditar o que aconteceu* quando não há gabarito prévio.

---

## 4. `agentevals-dev/agentevals`

### O que existe lá

Projeto **distinto** do `langchain-ai/agentevals` — o README não menciona o outro repositório. É uma
plataforma agnóstica de framework que pontua comportamento de agente **a partir de traços OpenTelemetry**.

- CLI: `agentevals run` (avalia arquivos de traço contra eval sets, offline), `agentevals serve`
  (UI web + receptor OTLP, portas 8001 / 4317 / 4318), `agentevals evaluator init` (scaffold de avaliador
  próprio), `agentevals evaluator list`.
- SDK:

```python
from agentevals import AgentEvals
app = AgentEvals()
with app.session(eval_set_id="my-eval"):
    agent.invoke("...")
```

- Servidor MCP com as ferramentas `list_metrics`, `evaluate_traces`, `list_sessions`,
  `summarize_session`, `evaluate_sessions`.
- Diferenciais declarados, verbatim: *"score agents from existing traces without replaying expensive LLM
  calls"*; *"no database, no message queue, and no external services"*; interface universal via
  OpenTelemetry, atravessando LangChain, Strands, Google ADK, OpenAI Agents SDK.

Fonte: <https://raw.githubusercontent.com/agentevals-dev/agentevals/main/README.md>

### A qual buraco se aplica, e como usaríamos aqui

**Buraco 1, na formulação mais forte do lote.** *"score agents from existing traces without replaying"* é
exatamente a inversão que nos falta: **a evidência é o registro do que executou**, e a avaliação é uma
função pura sobre esse registro. Aplicado aqui: o validador não deveria *afirmar* que a trava rodou; ele
deveria emitir um traço, e a auditoria deveria pontuar o traço. Isso separa quem executa de quem avalia
sem precisar de dois autores — é independência **por artefato**, não por pessoa.

**Buraco 6, por tabela.** Como o traço é gravado por quem executa e pontuado por um avaliador que só lê o
traço, a independência é estrutural: o avaliador não tem como "consertar" o que já foi gravado. Isso
casa com a nossa lição *"veredito não mora dentro do artefato julgado"*.

**Buraco 5, por tabela.** Um traço registra a exceção *e* o ponto onde ela ocorreu. A distinção que nos
faltou — mutante morto por `ValueError` antes de a trava rodar, versus mutante morto pela asserção da
trava — é visível num traço e invisível num "passou/não passou". Se cada trava emitir um span, o mutante
que morre antes tem span **ausente**, não span **vermelho**. Essa é a diferença que precisamos gravar.

### O que NÃO serve

- **Não li o código, só o README.** Não afirmo assinaturas de API além das listadas.
- **Adotar OpenTelemetry inteiro para uma cadeia de validadores Python é desproporcional.** O que se
  aproveita é o *contrato*: cada trava emite um evento estruturado (nome, resultado, exceção, timestamp) e
  o placar é derivado dos eventos. Não precisa ser OTLP.
- **Nada sobre variância de juiz, thresholds ou reprodutibilidade** aparece no README. Buracos 3, 7 e 8
  não são atendidos.

---

## 5. `huggingface/lighteval`

### O que existe lá

**O README cru é fino** (<https://raw.githubusercontent.com/huggingface/lighteval/main/README.md>): traz
`EvaluationTracker(output_dir="./results")`, a promessa de *"detailed, sample-by-sample results"*, o
exemplo `lighteval eval "hf-inference-providers/openai/gpt-oss-20b" gpqa:diamond` e a versão `0.11.0` na
citação. Não traz o formato pipe `suite|task|num_few_shot|truncate_few_shots`, nem API de métrica
customizada, nem juiz. Fui à fonte da documentação no próprio repo.

**Estrutura do JSON de resultados** — `docs/source/saving-and-reading-results.mdx`:

- Bloco `config_general`: `lighteval_sha`, `model_name`, **`model_sha`**, `model_dtype`, `model_size`,
  `start_time`, `end_time`, `total_evaluation_time_secondes` [sic, no original],
  `num_fewshot_seeds`, `max_samples`, `job_id`.
- Bloco `versions`: versões por task.
- Bloco `results`: métricas agregadas por task.
- Bloco `config_tasks`: função de prompt, dataset, métricas, parâmetros de geração.
- Blocos `summary_general` / `summary_tasks`: **`hash_examples`, `hash_full_prompts`, `hash_input_tokens`,
  `hash_cont_tokens`**, mais `padded`, `non_padded`, `effective_few_shots`, `num_truncated_few_shots`.
- Caminho de saída: *"automatically saved in `{output_dir}/results/{model_name}/results_{timestamp}.json`"*,
  com suporte fsspec (S3, HF Hub).

Fonte: <https://raw.githubusercontent.com/huggingface/lighteval/main/docs/source/saving-and-reading-results.mdx>

**Juiz LLM** — `src/lighteval/metrics/utils/llm_as_judge.py`:

```python
class JudgeLM:
    def __init__(
        self,
        model: str,
        templates: Callable,
        process_judge_response: Callable,
        judge_backend: Literal["litellm", "openai", "transformers", "tgi", "vllm", "inference-providers"],
        url: str | None = None,
        api_key: str | None = None,
        max_tokens: int | None = None,
        response_format: BaseModel = None,
        hf_provider: Optional[...] = None,
        backend_options: dict | None = None,
    ):
```

Docstrings verbatim: `templates` = *"A function taking into account the question, options, answer, and
gold"*; `process_judge_response` = *"A function for processing the judge's response"*;
`response_format` = *"The format of the response from the API"*.
Parsing: `score = self.process_judge_response(response)`.
Retry: `self.API_MAX_RETRY = 3`, `self.API_RETRY_SLEEP = 1`.
Lote: `def evaluate_answer_batch(self, questions, answers, options, golds, **kwargs)`.

Fonte: <https://raw.githubusercontent.com/huggingface/lighteval/main/src/lighteval/metrics/utils/llm_as_judge.py>

### A qual buraco se aplica, e como usaríamos aqui

**Buraco 3 — e aqui está a diferença que vale mais que o `lm-eval`.** Os dois hasheiam, mas em camadas
diferentes, e isso é o achado da comparação:

| | `lm-eval` | `lighteval` |
|---|---|---|
| O que hasheia | `doc_hash`, `prompt_hash`, `target_hash` | `hash_examples`, `hash_full_prompts`, `hash_input_tokens`, `hash_cont_tokens` |
| Camada mais funda | string do prompt | **tokens** de entrada e de continuação |
| Consequência | trocar template/tokenizer sem mudar a string final **não** move o hash | qualquer mudança de tokenização move `hash_input_tokens` |

Para nós, a lição é a que já custou caro: **hasheie na camada onde a discordância acontece**. Nossos
quatro leitores divergiram por objeto, ordenação, raiz e EOL — quatro camadas. A resposta do `lighteval`
é não escolher uma: publicar **um hash por camada**, e então a divergência se localiza sozinha. Se dois
leitores batem em `hash_examples` e divergem em `hash_full_prompts`, o problema está na montagem do
prompt, não nos dados. Isso é diagnóstico, não só detecção.

**Buraco 2 — a melhor aproximação do lote.** `truncated` / `non_truncated`, `padded` / `non_padded`,
`num_truncated_few_shots` são **contadores de anomalia de processamento publicados ao lado do resultado**.
Não é "caso sumiu", mas é a estrutura certa: o placar não é um número, é um número **mais os contadores
de tudo que não entrou nele em condições normais**. Nosso `64/64` verde teria sido impossível de publicar
sob esse formato — a linha "casos esperados: 93, casos executados: 64" estaria ao lado.
**Recomendação concreta:** adicionar ao nosso placar um bloco `summary` com `esperados`, `executados`,
`ausentes`, `quebrados`, `pulados` — e reprovar a publicação se `esperados != executados + ausentes +
quebrados + pulados`.

**Buraco 3, complemento.** `model_sha` e `lighteval_sha` no mesmo bloco: a identidade do resultado inclui
a identidade do *avaliado* e do *avaliador*. Nosso placar hoje identifica só o avaliado.

### O que NÃO serve

- **`JudgeLM` não trata variância.** Tem `API_MAX_RETRY = 3`, mas retry é para **erro de API**, não para
  dispersão de julgamento — não há amostragem múltipla, não há voto, não há temperatura declarada na
  assinatura. Confundir retry com self-consistency seria erro nosso. Buraco 7 não é atendido.
- **`process_judge_response` é um `Callable` livre.** Toda a garantia de que a nota extraída corresponde ao
  que o juiz disse mora numa função que o usuário escreve. É exatamente a superfície onde nosso buraco 4
  mora — o parser pode "sempre achar uma nota". Se copiarmos o padrão, o parser precisa de controle
  negativo próprio (resposta sem nota → tem que falhar, não devolver default).
- **`total_evaluation_time_secondes`** tem erro de grafia no schema publicado. Anotado porque é o tipo de
  detalhe que quebra leitor de terceiro — e é a prova viva de que schema publicado vira contrato.
- **Não consegui ler** `src/lighteval/metrics/llm_as_judge.py` (404) nem a lista de métricas; o que sei do
  juiz vem só de `metrics/utils/llm_as_judge.py`.

---

## 6. `UKGovernmentBEIS/inspect_evals` (+ `inspect_ai`, o runtime)

### O que existe lá

**Redutores de época — o achado mais direto do lote para os buracos 7 e 8.**
`inspect_ai/docs/options.qmd`, verbatim:

- `--epochs`: *"Number of times to repeat each sample (defaults to 1)"*
- `--epochs-reducer`: *"Method for building the reduced score view from per-epoch sample scores. Built in
  reducers include mean, median, mode, max, at_least_{n}, pass_at_{k}, and pass_k_{k}."*

Fonte: <https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_ai/main/docs/options.qmd>

O código dos redutores, em `src/inspect_ai/scorer/_reducer/reducer.py`:

```python
@score_reducer(name="mean")
def mean_score(value_to_float: ValueToFloat = value_to_float()) -> ScoreReducer:
    r"""Take the mean of a list of scores."""

@score_reducer(name="median")
def median_score(value_to_float: ValueToFloat = value_to_float()) -> ScoreReducer:
    r"""Take the median value from a list of scores."""

@score_reducer(name="mode")
def mode_score() -> ScoreReducer:
    r"""Take the mode from a list of scores."""

@score_reducer(name="max")
def max_score(value_to_float: ValueToFloat = value_to_float()) -> ScoreReducer:
    r"""Take the maximum value from a list of scores."""

@score_reducer
def at_least(k: int, value: float = 1.0,
    value_to_float: ValueToFloat = value_to_float()) -> ScoreReducer:
    r"""Score correct if there are at least k score values greater than or equal to the value."""

@score_reducer
def pass_at(k: int, value: float = 1.0,
    value_to_float: ValueToFloat = value_to_float()) -> ScoreReducer:
    r"""Probability of at least 1 correct sample given `k` epochs."""

@score_reducer
def pass_k(k: int, value: float = 1.0,
    value_to_float: ValueToFloat = value_to_float()) -> ScoreReducer:
    r"""Probability that all `k` epoch attempts succeed."""
```

`mode_score` usa `Counter.most_common(1)`; `pass_at` usa o estimador de Chen 2021
(`1.0 - np.prod(1.0 - k / np.arange(...))`); `pass_k` usa `math.comb(correct, k) / math.comb(total, k)`.
Fonte: <https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_ai/main/src/inspect_ai/scorer/_reducer/reducer.py>

**Outros flags relevantes** (`options.qmd`): `--limit` (*"Limit samples to evaluate by specifying a maximum
(e.g. 10) or range (e.g. 10-20)"*), `--sample-id` (*"Evaluate a specific sample (e.g. 44) or list of
samples (e.g. 44,63,91)"*), `--log-format` (*"Values: eval, json"*), `--no-log-samples`, `--seed`
(*"Random seed. OpenAI, Google, Groq, Mistral, HuggingFace, and vLLM only."*), `--temperature`, `--top-p`,
`--max-retries`.

**Requisito de baseline externo** — `inspect_evals/CONTRIBUTING.md`, verbatim:
*"Comparable - we expect baseline results for at least one frontier model to exist, so we can validate
that your implementation produces similar performance."*
E sobre épocas: *"How to calculate the ideal number of epochs for an evaluation: this depends on the size
of the dataset and how performance trends over repeated passes."*
Requisitos de teste, verbatim: *"Add unit tests to cover changes to non-trivial logic or components"*;
*"Check that tests pass (including relevant heavy or end-to-end tests)"*; *"Manually verify that the
evaluation successfully runs e2e by testing it on a few (relevant) samples"*. Variáveis de ambiente de
teste: `RUN_SLOW_TESTS`, `RUN_DATASET_DOWNLOAD_TESTS`.
Fonte: <https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/CONTRIBUTING.md>

**Listagem gerada.** O README traz o marcador `<!-- Eval Listing: Automatically Generated -->` antes das
categorias, com atribuição de contribuidor por eval e comandos como
`uv run inspect eval inspect_evals/arc_easy --model openai/gpt-5-nano`.
Fonte: <https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/README.md>

### A qual buraco se aplica, e como usaríamos aqui

**Buraco 7 — adotar isto.** Nossa medição: duas instâncias da mesma lente, mesmo alvo, mesma rubrica,
divergem até 3 pontos; em 98 pares, 54% divergiram. A resposta do `inspect` é estrutural e barata:
**a unidade de avaliação não é uma execução, é N execuções mais uma regra de redução declarada antes**.
Traduzido para a nossa cadeia:
- `epochs = N` vira campo obrigatório do julgamento (N ≥ 3; com 54% de divergência de pares, N = 1 é
  inaceitável e nós já sabíamos disso empiricamente).
- O redutor vira campo do contrato, escolhido **antes** de ver as notas. `median` é o certo para nota
  contínua com outlier de instância; `mode` para veredito categórico; `at_least_{n}` para "pelo menos n
  dos N juízes aprovaram".
- Nosso `NAO_DISCRIMINADO` (da lição "nota de instância única não decide") ganha definição operacional:
  é o caso em que o redutor não converge — por exemplo, `mode` sem maioria, ou dispersão acima de um
  limite declarado. Hoje é julgamento; passa a ser função.

**Buraco 8 — `at_least_{n}` e `pass_at_{k}` são a régua que fecha.** Nossa régua exigia 10 em todos os
critérios e nunca foi alcançada em 243 notas. `at_least(k, value)` — *"Score correct if there are at least
k score values greater than or equal to the value"* — é a formulação exata do substituto: em vez de
"máximo em tudo", **"pelo menos k de N acima do valor v"**, com `k` e `v` declarados. E note que
`pass_at` e `pass_k` são réguas **opostas** (probabilidade de ao menos 1 acerto × probabilidade de todos
acertarem) — ter as duas nomeadas no mesmo lugar força quem escreve o contrato a dizer qual quer.
Nossa régua atual é `pass_k` disfarçada de meta.

**Buraco 6, e é o único do lote que endereça isso de frente.** *"we expect baseline results for at least
one frontier model to exist, so we can validate that your implementation produces similar performance"*:
o número de referência tem que **preexistir e vir de fora**. Aplicado aqui: nenhum pacote deveria ser
aprovado contra um alvo que a própria frente definiu na mesma rodada — precisa haver um número anterior,
de outra origem, que a implementação reproduza. É a versão institucional da nossa lição
*"canonizar durante medição é alterar evidência"*.

**Buraco 3.** `--sample-id 44,63,91` é o que nos falta para reexecução exata: um terceiro consegue rodar
**os mesmos casos**, não "uma amostra equivalente". Junto com `--log-format eval|json`, o formato do
registro é declarado, não incidental.

### O que NÃO serve

- **`CONTRIBUTING.md` não exige independência entre autor e validador.** Verificado por leitura dirigida:
  diz *"It is your responsibility to address any issues raised by reviewers"* e que tudo deve ser
  *"reviewed and tested by a human prior to submission"* — revisão, não independência de autoria do caso.
  Buraco 6 fica **parcialmente** atendido: independência do *número de referência*, sim; do *autor do
  caso*, não.
- **`--epochs` não é obrigatório.** Default é 1. A ferramenta oferece o mecanismo e não o exige. Se
  copiarmos assim, cairemos no nosso próprio buraco: mecanismo disponível ≠ mecanismo aplicado. **Na nossa
  adoção, `epochs` e `reducer` têm que ser campos obrigatórios do schema, sem default silencioso.**
- **Não há `epochs_reducer` mandatório por eval no `inspect_evals`**, e o `CONTRIBUTING` só *discute* como
  calcular o número ideal de épocas, sem fixar. Confirmado: *"No mandatory epochs or epochs_reducer
  specifications"*.
- **`--seed` só funciona em alguns provedores** (*"OpenAI, Google, Groq, Mistral, HuggingFace, and vLLM
  only"*). Semente não é garantia de reprodutibilidade transversal — e isso vale como aviso para nós: não
  prometer determinismo que o provedor não entrega.
- **Não consegui ler `tools/listing.yaml`** (404 em `main`) — então **não afirmo** quais campos de metadado
  por eval existem (arxiv, group, contributors, human_baseline etc.). O README mostra atribuição de
  contribuidor e o marcador de geração automática; o resto seria invenção.
- **O README não publica resultados de baseline nem score humano por eval** (verificado). O requisito de
  baseline vive no `CONTRIBUTING`, o número não vive no README. Para nós isso é um contra-exemplo: exigir
  a comparação e não publicar o número deixa a exigência não auditável depois.

---

## 7. `openai/evals`

### O que existe lá

**Critério de aceite baseado em o sujeito reprovar** — `docs/build-eval.md`, verbatim:

- *"The eval should be thematically consistent. We'd like to see a number of prompts all revolving around the same use case, subject domain, failure mode, etc."*
- *"The eval should be challenging. If GPT-4 or GPT-3.5-Turbo do well on all of the prompts, this is not as interesting."*
- *"The eval should be directionally clear. The data should include good signal around what is the right behavior."*
- *"The eval should be carefully crafted. Before you submit, you should think through whether you have engineered your prompts for good performance..."*

Formato de dados: JSONL com `"input"` (o prompt, idealmente em formato de chat) e `"ideal"` (string ou
lista de strings com as respostas de referência).

Registro em `evals/registry/evals/<eval_name>.yaml`:

```yaml
<eval_name>:
  id: <eval_name>.dev.v0
  description: <description>
  metrics: [accuracy]

<eval_name>.dev.v0:
  class: evals.elsuite.basic.match:Match
  args:
    samples_jsonl: <eval_name>/samples.jsonl
```

Execução: `oaieval gpt-3.5-turbo <eval_name>`.
Fonte: <https://raw.githubusercontent.com/openai/evals/main/docs/build-eval.md>

**Templates básicos** — `docs/eval-templates.md`, verbatim:
- `"basic/match.py:Match"` implementando `any([a.startswith(b) for b in B])`
- `"basic/includes.py:Includes"` implementando `any([(b in a) for b in B])`
- `"basic/fuzzy_match.py:FuzzyMatch"` implementando `any([(a in b or b in a) for b in B])`

**Template model-graded** — chaves exatas: `prompt`, `input_outputs`, `choice_strings`
(ex.: `"ABCDE"` ou `["Yes", "No", "Unsure"]`), `choice_scores` (opcional, mapeia escolha → nota),
`eval_type` (opcional, três valores: `"cot_classify"`, `"classify_cot"`, `"classify"`),
`output_template` (opcional).
Fonte: <https://raw.githubusercontent.com/openai/evals/main/docs/eval-templates.md>

**Restrição de contribuição** — README: *"Please note that we are currently not accepting evals with
custom code! While we ask you to not submit such evals at the moment, you can still submit model-graded
evals with custom model-graded YAML files."*
Fonte: <https://raw.githubusercontent.com/openai/evals/main/README.md>

### A qual buraco se aplica, e como usaríamos aqui

**Buraco 4 — esta é a formulação mais afiada do lote inteiro.**
*"The eval should be challenging. If GPT-4 or GPT-3.5-Turbo do well on all of the prompts, this is not as
interesting."* Traduzindo para o nosso caso: **um instrumento cujo sujeito passa em tudo não é aceito
como instrumento**. Nosso medidor publicava 100% de discriminadores para qualquer entrada — sob esta
regra, ele seria rejeitado na entrada, antes de qualquer análise de código, só pelo perfil da saída.
Isso é um **controle negativo no nível do conjunto de casos**, não no nível de um caso: se a taxa de
aprovação é 100%, o conjunto é suspeito por construção.

Recomendação concreta para nós: adicionar ao gate de aceitação de qualquer bateria nova uma condição de
**dispersão mínima** — se o placar da bateria contra o baseline atual é 100% PASS, a bateria é
`INCONCLUSIVA` até que se demonstre pelo menos um caso reprovando. Isso é diferente de mutação: mutação
testa a trava; isto testa se o *conjunto de casos* discrimina.

**Buraco 8.** `choice_strings` + `choice_scores` é a régua discreta e explícita: o juiz não devolve
"uma nota", devolve **uma das escolhas nomeadas**, e o mapa escolha→nota é config, não interpretação do
juiz. Isso remove uma fonte inteira de variância (buraco 7) e torna a régua auditável. Comparar com
`openevals` (`choices` como lista de floats): o `openai/evals` é melhor aqui, porque separa **o rótulo que
o juiz emite** da **nota que o rótulo vale** — quem muda a régua não precisa mexer no prompt do juiz.

**Buraco 3, forma mínima.** `id: <eval_name>.dev.v0` — versão no identificador do eval, não num campo
lateral. Nosso placar hoje não versiona a bateria.

**Buraco 1.** `eval_type: cot_classify` versus `classify` é a distinção entre "raciocina e depois
classifica" e "classifica direto". Para auditoria isso importa: com `cot_classify` fica registrado o
raciocínio *que produziu* a classificação — evidência do efeito, não só do resultado.

### O que NÃO serve

- **Não há meta-avaliação de eval model-graded contra rótulo humano.** Verificado por leitura dirigida de
  `docs/eval-templates.md`: nenhum conteúdo sobre validar o juiz contra gabarito humano. E também
  **nenhum aviso** sobre model-graded ser pouco confiável — o texto trata como *"a viable strategy for
  automated evaluation"* e para por aí. Buracos 5 e 7 não são atendidos.
- **Os templates básicos são frágeis e ensinam o erro que já cometemos.**
  `Includes` = `any([(b in a) for b in B])`, `FuzzyMatch` = `any([(a in b or b in a) for b in B])`.
  Isto é literalmente "verificar presença de substring". `FuzzyMatch` aprova se a resposta contém o ideal
  **ou** se o ideal contém a resposta — uma resposta de uma letra passa em quase tudo. **Não copiar.**
  É o nosso buraco 1 encapsulado numa biblioteca de referência.
- **`--record_path`, `/tmp/evallogs`, `oaievalset`:** não estão no README que li. Não afirmo nada sobre o
  formato de log deste projeto.
- **Repositório em modo restritivo** (não aceita evals com código customizado). Como fonte de método
  ainda vale; como ferramenta viva, provavelmente não.

---

## 8. `promptfoo/promptfoo`

### O que existe lá

O README cru (<https://raw.githubusercontent.com/promptfoo/promptfoo/main/README.md>) é página de
divulgação: instalação (`npm install -g promptfoo`, `promptfoo init --example getting-started`,
Node.js >= 22.22.0), menção a *"automated evaluations"* e *"red teaming and vulnerability scanning"*, e
nada de nomes de assertion, threshold ou YAML. Os detalhes vieram da documentação publicada.

**Catálogo de assertions determinísticas** (nomes exatos, `docs/configuration/expected-outputs/`):
`equals`, `contains`, `icontains`, `regex`, `starts-with`, `contains-any`, `contains-all`,
`icontains-any`, `icontains-all`, `is-json`, `contains-json`, `contains-html`, `is-html`, `is-sql`,
`contains-sql`, `is-xml`, `contains-xml`, `is-refusal`, `javascript`, `python`, `ruby`, `webhook`,
`rouge-n`, `bleu`, `gleu`, `levenshtein`, `latency`, `meteor`, `perplexity`, `perplexity-score`, `cost`,
`is-valid-function-call`, `is-valid-openai-function-call`, `is-valid-openai-tools-call`,
`trace-span-count`, `trace-span-duration`, `trace-error-spans`, `skill-used`, `trajectory:tool-used`,
`trajectory:tool-args-match`, `trajectory:tool-sequence`, `trajectory:step-count`, `guardrails`.

**Model-graded:** `similar`, `classifier`, `moderation`, `llm-rubric`, `g-eval`, `answer-relevance`,
`context-faithfulness`, `context-recall`, `context-relevance`, `conversation-relevance`,
`trajectory:goal-success`, `factuality`, `model-graded-closedqa`, `pi`, `select-best`, `max-score`.

Fonte: <https://www.promptfoo.dev/docs/configuration/expected-outputs/>

**Mecânica de nota e corte**, verbatim da mesma página:
- `threshold`: *"The threshold value, applicable only to certain types such as `similar`, `cost`, `javascript`, `python`, `ruby`"*
- `weight`: número que determina *"the relative importance"* (default 1.0); a nota final é *"weighted average of the scores of all assertions"*
- `assert-set` → `threshold`: *"Success threshold for the assert-set. Ex. 1 out of 4 equal weights assertions need to pass."*
- pass/fail do teste: *"If set, the pass/fail status of a test case is determined by whether the combined weighted score of all assertions is greater than or equal to the threshold value."*
- `metric`: permite *"combine related assertions into aggregate metrics"*
- `transform`: *"Process the output before running the assertion."*

**Semântica de threshold em juiz LLM**, verbatim de
<https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/>:
sem threshold, *"PASS depends only on the grader's `pass` field"*; com threshold,
*"PASS requires both `pass === true` AND `score >= threshold`"*.

**Override de juiz, em três níveis** (mesma URL):

```yaml
defaultTest:
  options:
    provider: openai:gpt-5.6
```

```yaml
assert:
  - type: llm-rubric
    value: Is not apologetic
    provider:
      id: openai:gpt-5.6
      config:
        temperature: 0
```

e por CLI: `promptfoo eval --grader openai:gpt-5.6`.

**Rubrica substituível** via `rubricPrompt`, com variáveis `{{output}}` e `{{rubric}}`; o exemplo devolve
JSON `{pass: true, score: number, reason: string}`.

**Repetição e cache** — <https://www.promptfoo.dev/docs/usage/command-line/>:
- `--repeat <number>`: *"Number of times to run each test"*
- `--filter-failing <path or id>`: *"Filter tests that failed in a previous eval"*
- `--filter-sample <number>`: *"Only run a random sample of N tests"*
- `--no-cache`: *"Do not read or write results to disk cache"*
- `--grader <provider>`: *"Model that will grade outputs"*
- `promptfoo cache clear`; env `PROMPTFOO_CACHE_ENABLED` (default **true**), `PROMPTFOO_CACHE_PATH`,
  `PROMPTFOO_CACHE_TTL` (default **1209600** segundos ≈ 14 dias), `PROMPTFOO_CACHE_TYPE` (`disk`|`memory`).

### A qual buraco se aplica, e como usaríamos aqui

**Buraco 8 — a régua ponderada com corte é o que substitui "10 em tudo".** Três níveis, e os três nos
faltam:
1. `threshold` **por assertion** — cada critério tem seu próprio corte, e cortes diferentes por critério
   são legítimos.
2. `weight` **por assertion** — critérios não valem o mesmo. Nossa régua trata todos como iguais e
   obrigatórios; é por isso que ela nunca fechou em 243 notas.
3. `assert-set` com threshold próprio — *"1 out of 4 equal weights assertions need to pass"*. Isto é
   `at_least(k)` aplicado a **critérios** em vez de a **repetições**.

E aqui está a comparação que vale mais que qualquer um dos dois isolados:

> **`promptfoo` faz banda entre critérios; `inspect_ai` faz banda entre repetições. Nossa régua quebrou
> nos dois eixos ao mesmo tempo** — exigia máximo em todos os critérios (eixo `promptfoo`) e decidia com
> uma instância só (eixo `inspect`). Adotar um só resolve metade.

**Buraco 7.** `--repeat <number>` mais `provider: {config: {temperature: 0}}` por assertion é o par
mínimo: repetir e fixar temperatura. Note que a temperatura é configurável **no nível da assertion**, não
global — o que permite juiz determinístico para critério objetivo e juiz amostrado para critério
subjetivo, na mesma bateria.

**Buraco 1.** As assertions `trace-span-count`, `trace-error-spans`, `trajectory:tool-used`,
`trajectory:tool-sequence`, `skill-used` são todas asserções **sobre a execução**, não sobre o texto de
saída. `trajectory:tool-sequence` é exatamente a trava que nos faltou: "estas ferramentas foram chamadas,
nesta ordem" — verificado no traço, não na AST.

**Buraco 4.** `javascript`/`python`/`ruby` como tipos de assertion com `threshold` são a válvula para
critério que precisa ser código executável e não opinião — mesma lógica dos avaliadores de código do
`openevals`, mas embutida no formato de teste.

### O que NÃO serve — e um aviso importante

- **O cache é ligado por default, com TTL de 14 dias.** `PROMPTFOO_CACHE_ENABLED` default `true`,
  `PROMPTFOO_CACHE_TTL` default `1209600`. Isso significa que **uma rodada verde pode ser resposta
  reproduzida do disco, não execução**. Para esta base, isso é o buraco 1 na própria ferramenta de
  medição: o instrumento "passou" sem ter executado. Se adotarmos qualquer coisa daqui, `--no-cache` é
  obrigatório em rodada que vira evidência, e a ausência dele deve reprovar o registro.
  A doc chega a sugerir `--no-cache` para determinismo, mas o default trabalha contra.
- **`--repeat` não vem com regra de redução.** Diferente do `inspect_ai`, roda N vezes mas não declara
  como as N viram uma. Para o buraco 7, `inspect_ai` é estritamente superior: lá o redutor é nomeado e
  faz parte do contrato.
- **Nenhuma orientação documentada sobre confiabilidade de juiz.** Verificado por leitura dirigida da
  página model-graded: não há conselho sobre consistência entre graders nem sobre usar múltiplos.
- **Não consegui confirmar** as categorias A/B/C/D/E e os pesos configuráveis do assertion `factuality` —
  não estavam na página lida. Não afirmo que existem.
- **Sem reprodutibilidade por digest.** Não há hash de dataset, hash de config nem manifesto de execução
  comparável ao do `lm-eval`/`lighteval`. Buraco 3 não é atendido.

---

## 9. `strands-agents/evals`

### O que existe lá

**Injeção de falha pareada com avaliador da reação.** Efeitos disponíveis: `Timeout`, `NetworkError`,
`TruncateFields`, `RemoveFields`, `CorruptValues`, `ExecutionError`, `ValidationError`.
Avaliadores pareados: `FailureCommunicationEvaluator`, `PartialCompletionEvaluator`,
`RecoveryStrategyEvaluator`.

**Diagnóstico de falha como pipeline nomeado:** `detect_failures()`, `analyze_root_cause()`,
`diagnose_session()`, com `DiagnosisConfig(trigger=DiagnosisTrigger.ON_FAILURE,
confidence_threshold=ConfidenceLevel.MEDIUM)` e níveis `LOW`, `MEDIUM`, `HIGH`.

**Estruturas:** `Experiment[InputType, OutputType]`, `Case[InputType, OutputType]`, `EvaluationData` /
`EvaluationOutput`, classe base `Evaluator`. Exemplo verbatim de avaliador próprio:

```python
class PolicyComplianceEvaluator(Evaluator[str, str]):
    def evaluate(self, evaluation_case: EvaluationData[str, str]) -> EvaluationOutput:
```

e o retorno, verbatim:

```python
return EvaluationOutput(
    score=1.0,
    test_pass=True,
    reason="...",
    label="..."
)
```

**Avaliadores prontos** com escalas declaradas no nome: `HelpfulnessEvaluator` (escala de 7 pontos),
`CoherenceEvaluator` (5 pontos), `ConcisenessEvaluator` (3 pontos), além de `FaithfulnessEvaluator`,
`ResponseRelevanceEvaluator`, `HarmfulnessEvaluator`, `RefusalEvaluator`, `StereotypingEvaluator`,
`InstructionFollowingEvaluator`, `ToolSelectionAccuracyEvaluator`, `ToolParameterAccuracyEvaluator`,
`GoalSuccessRateEvaluator`. `OutputEvaluator(rubric=..., include_inputs=True, model=...)`.
Funções de score de trajeto: `exact_match_scorer`, `in_order_match_scorer`, `any_order_match_scorer`.

**CLI `strands-evals`:** `run`, `validate` (*"Schema-check serialized Experiment JSON"*), `report`,
`diagnose`, `generate`. Exemplos:

```bash
strands-evals validate experiments/customer_service.json
strands-evals diagnose session.json --confidence medium
strands-evals generate --context "$(cat tools.txt)" --num-cases 10 \
  --evaluator TrajectoryEvaluator -o experiments/generated.json
```

Fonte: <https://raw.githubusercontent.com/strands-agents/evals/main/README.md>

### A qual buraco se aplica, e como usaríamos aqui

**Buraco 5 — o achado.** `TruncateFields`, `RemoveFields`, `CorruptValues`, `ExecutionError`,
`ValidationError` são **classes de mutação nomeadas**, e cada uma vem pareada com um avaliador que julga a
reação. Isso é precisamente a distinção que nos faltou quando 7 de 11 mutantes foram creditados tendo
morrido por `ValueError` com a trava sem rodar: aqui, `ExecutionError` (o processo quebrou) e
`ValidationError` (a validação recusou) são **efeitos diferentes, injetados de propósito e julgados por
avaliadores diferentes**. Traduzido: nosso relatório de mutação precisa de duas colunas separadas —
`morto_por_assercao` e `morto_por_excecao` — e só a primeira conta como mutante pego. A segunda é
**inconclusiva**, porque a trava não chegou a opinar.

**Buraco 8.** `EvaluationOutput(score=1.0, test_pass=True, ...)`: **`score` e `test_pass` são campos
separados**. A nota não determina o veredito por convenção implícita; o veredito é declarado ao lado. Isso
casa exatamente com a regra da casa (nota é dos Juízes, conformidade é da Auditoria) e é a estrutura de
dado que faltava para expressá-la. E as escalas declaradas no nome do avaliador (7 pontos, 5 pontos,
3 pontos) resolvem outra parte: **nem todo critério precisa da mesma escala** — nossa 0–10 uniforme é uma
escolha, não uma necessidade, e escala de 3 pontos discrimina melhor do que 0–10 em critério grosso.

**Buraco 4.** `strands-evals validate` faz *"Schema-check serialized Experiment JSON"* — o experimento é
validado por schema **antes** de rodar. Nós validamos artefatos por schema; não validamos a *bateria*.

**Buraco 6, com ressalva grande.** `strands-evals generate --context ... --num-cases 10` gera casos por
LLM a partir do contexto. Isso ataca a lição *"caso de eval não nasce do prompt de criação"* pela metade:
separa o autor do caso do autor do código, mas o gerador ainda vê o contexto do sistema. Serve como
**terceira origem** ao lado das que já temos, não como origem independente de verdade.

### O que NÃO serve

- **Correção de leitura minha:** uma primeira passada resumida sugeriu "seeds configuráveis para
  simuladores determinísticos". **Isso é falso** — confirmei numa segunda leitura dirigida do mesmo
  README: não há menção a seeds nem a determinismo de execução; o único uso da palavra é
  *"Deterministic fault injection via Strands plugin hooks"*, que se refere à injeção de falha, não à
  reprodutibilidade da rodada. Registro o erro aqui de propósito: é exatamente o modo de falha que esta
  base já pagou — número/afirmação sem procedência, produzido por resumo automático.
- **Nada sobre execuções repetidas ou agregação entre execuções** — verificado, "não está no README".
  Buraco 7 não é atendido.
- **Como `test_pass` é computado não está documentado no README**; só aparece preenchido à mão no exemplo.
  A separação score/veredito é boa como *forma*; a *regra* teria que ser nossa.
- **A assinatura completa da classe base `Evaluator` e de `OutputEvaluator` não está no README** — só
  `rubric`, `include_inputs`, `model`. Não afirmo mais que isso.
- **Nada sobre reprodutibilidade por digest, versionamento de bateria ou hash.** Buraco 3 não é atendido.

---

## 10. Leitura transversal — o que o lote inteiro ensina

### 10.1 O buraco 2 está essencialmente desatendido, e isso é informação

Nenhum dos nove trata "caso sumiu" como categoria própria ao lado de "caso falhou". Os dois substitutos:

- **Digest agregado** (`lm-eval`): `hash_string("".join(sample_hashes))`. Se um caso some, o digest muda.
  Detecta, não classifica, e só funciona se houver um digest de referência para comparar.
- **Contadores de anomalia publicados ao lado do placar** (`lighteval`): `truncated`/`non_truncated`,
  `padded`/`non_padded`, `num_truncated_few_shots`. Classifica, mas as categorias são de processamento
  (truncamento, padding), não de ausência.

**A síntese para nós, que nenhum dos dois faz sozinho:** o placar deixa de ser `N/N` e passa a ser um
bloco com `esperados`, `executados`, `ausentes`, `quebrados`, `pulados`, mais um digest do conjunto de
casos esperados. Duas travas derivadas, ambas mecanizáveis:
1. `esperados == executados + ausentes + quebrados + pulados`, ou a publicação é recusada.
2. `digest(conjunto_esperado)` da rodada bate com o da referência, ou a rodada é `INCOMPARÁVEL` — não
   reprovada, incomparável. É a mesma distinção que o `--limit ... For testing only` faz.

O `64/64` verde com 29 casos apagados falharia nas duas.

### 10.2 Três respostas diferentes para "presença × efeito" (buraco 1)

| Abordagem | Repo | O que faz | Custo para nós |
|---|---|---|---|
| Comparar trajeto contra gabarito | `langchain-ai/agentevals` | `trajectory_match_mode` em `strict`/`unordered`/`subset`/`superset` | precisa de gabarito — e alguém escreve o gabarito |
| Pontuar traço gravado, sem gabarito | `agentevals-dev/agentevals` | avalia OTel traces sem reexecutar | precisa instrumentar a execução |
| Asserção sobre a execução, no formato de teste | `promptfoo` | `trajectory:tool-sequence`, `trace-span-count`, `trace-error-spans` | precisa de traço, mas a asserção é declarativa |

**A escolha certa aqui:** as travas obrigatórias têm gabarito conhecido (sabemos quais deveriam rodar), então
o modelo `unordered`/`superset` do `agentevals` é o mais barato. O que muda de fato é a **fonte da
verdade**: passa de "a AST do validador contém a chamada" para "o registro de execução contém o evento
da trava". Isso mata `if False:` sem precisar de análise de alcançabilidade.

### 10.3 Duas respostas para "régua que não fecha" (buraco 8), em eixos ortogonais

Já detalhado em §8, mas vale isolado porque é a recomendação mais acionável do garimpo:

- **Eixo critérios** (`promptfoo`): `weight` + `threshold` por critério + `assert-set` com corte de
  conjunto (*"1 out of 4 ... need to pass"*).
- **Eixo repetições** (`inspect_ai`): `--epochs N` + `--epochs-reducer` (`median`, `mode`, `at_least_{n}`,
  `pass_at_{k}`, `pass_k_{k}`).

Nossa régua — 10 em todos os critérios, uma instância — é o pior ponto possível dos dois eixos: `pass_k`
com `k` = todos os critérios, e `N` = 1. Que não tenha fechado em 243 notas não é achado; é aritmética.

### 10.4 Ninguém neste lote testa o próprio juiz de verdade

Buracos 4 (parte "teste do avaliador"), 5 e 7 são atendidos apenas de raspão e por dois caminhos
indiretos:
- `openai/evals`: rejeitar o conjunto de casos se o sujeito passa em tudo (§7) — controle negativo no
  nível do conjunto, não do avaliador.
- `strands-agents/evals`: injeção de falha com avaliador pareado (§9) — mutação do sujeito, não do grader.

**Ninguém muta o grader.** Ninguém publica controle positivo e negativo do avaliador. Ninguém documenta
concordância entre juízes. Isso significa que a nossa medição de 54% de pares divergentes em 98 pares é
mais rigorosa do que a prática publicada por qualquer um destes nove projetos — e que, para o buraco 7, o
que dá para importar é o **mecanismo** (`--epochs` + redutor nomeado), não a **prática**. A prática temos
que escrever.

---

## 11. O que não consegui ler

Declarado para que ninguém tome ausência por inexistência.

| Alvo | URL tentada | Resultado |
|---|---|---|
| `inspect_evals` — listagem de metadados por eval | `https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/tools/listing.yaml` | **HTTP 404**. Não afirmo quais campos (arxiv, group, contributors, human_baseline) existem. |
| `lighteval` — juiz | `https://raw.githubusercontent.com/huggingface/lighteval/main/src/lighteval/metrics/llm_as_judge.py` | **HTTP 404**. Li `src/lighteval/metrics/utils/llm_as_judge.py` no lugar. |
| `inspect_ai` — redutores (primeiro caminho) | `.../src/inspect_ai/scorer/_reducer/reducers.py` | **HTTP 404**. Li `.../reducer.py` no lugar (com sucesso). |
| `inspect_ai` — seção "Reducing Epochs" na doc | `.../docs/scorers.qmd` | A página usa `{{< include _builtin-scorers.md >}}` e não traz a seção. Os redutores saíram do código-fonte e de `docs/options.qmd`. |
| `lm-eval` — implementação de `--check_integrity` | `.../lm_eval/utils.py` | `run_task_tests()` **não está** neste arquivo. Não localizei a implementação; não sei o que a flag executa. |
| `promptfoo` — pesos e categorias A–E do assertion `factuality` | `https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/` | Não constavam na página. Não afirmo que existem. |
| `openai/evals` — `oaievalset`, `--record_path`, formato de log | README | Não constavam. Sem afirmação. |
| Assinatura completa de `Evaluator` / `OutputEvaluator` | `strands-agents/evals` README | Só parcial (`rubric`, `include_inputs`, `model`). |

**Nota de método.** Duas afirmações produzidas por resumo automático na primeira passada não sobreviveram
à releitura dirigida: (a) "seeds configuráveis" em `strands-agents/evals` — **falso**, corrigido em §9;
(b) "listing.yaml gera o README do inspect_evals" — **não verificado**, o README só traz o marcador
`<!-- Eval Listing: Automatically Generated -->` e o arquivo apontado deu 404. Ambas estão registradas
como erro em vez de removidas, porque o padrão de falha (afirmação plausível sem leitura) é o mesmo que
esta base já mediu.
