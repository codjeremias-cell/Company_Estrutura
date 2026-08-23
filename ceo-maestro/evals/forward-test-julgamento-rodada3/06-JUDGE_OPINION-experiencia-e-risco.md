# JUDGE_OPINION — `agente-julgar-experiencia-e-risco`

- `judgment_request_ref`: `jrq-2026-07-28-frente5-r3-inovacao`
- `candidate_digest`: `sha256:e50aa56606b9e62be7159ab504fbdcdf70add43ef62fccd104db87a8ec740346`
- `return_to`: `departamento-juizes` · escala inteira 0–10 · **quatro notas secundárias, que entram
  na consolidação pela menor** (matriz §`reducao_declarada`: redução declarada, não lacuna)

**Consumidor nomeado:** quem herda o pacote — precisa rodar `evals/validate_workflow.py` depois de
uma mudança em `_compartilhado/`, decidir num comando se o pacote continua são, e depois movê-lo ou
reimplantá-lo. Consumidor secundário: o `diretor-de-lentes`, que lê o relatório consolidado e nunca
pode receber em silêncio um gate fabricado ou uma nota lavada.
**Dia ruim:** tarde da noite, o motor compartilhado acabou de mudar, o pacote já foi espelhado para
`.claude/skills/`, o autor está inalcançável.

> *Método:* `python` não executa neste ambiente (permissão). As quatro notas vêm de leitura dos
> caminhos de código, do schema e do corpus — **nunca** das contagens que o pacote alega.

## CRIT-05 (secundária — "não apenas frase em prosa") — **9** · banda `excelente`

A trava existe em três camadas de código. `derive_gate_checks()` recomputa as onze chaves a partir
dos retornos reais (`validate_workflow.py:1317-1362`), `chain_errors()` compara declarado contra
derivado (`:1467-1476`), e o schema fecha `gateChecks` com `additionalProperties: false`, as onze
chaves `required` e booleanas, mais um `allOf` que torna BLOCKED ↔ banda ↔ `blocking_pending_refs`
estruturalmente conjuntivo (`schemas/…json:1243-1272`, `:1323-1341`). Nada aqui pede ao operador que
confie num booleano autoafirmado: o valor declarado só sobrevive coincidindo com o recomputado.

Fora de 10: **oito das onze chaves derivadas são pura veracidade-de-presença** —
`bool(e.get("rollback"))`, `bool(e.get("owner"))`, `bool(e.get("smallest_test"))`,
`bool(e.get("pdca_check"))` — de modo que um placeholder como "a definir" passa em `text`
(minLength 3) e vira o gate `True`. Só `baseline` (`status == "MEASURED"`) e `two_alternatives`
(distinção) testam substância.

- `failure_mode`: **barulhenta + localizada** — quando o booleano mente, o operador recebe
  `portfólio initiative-001: gate declarado diverge do derivado em ['baseline']` e saída não-zero:
  a iniciativa nomeada e a chave nomeada, não um "inválido" difuso. A única costura silenciosa é a
  derivação por presença, que o próprio pacote nomeia como **R4** ("a derivação encarece a
  fabricação, não a impede", `protocolo:438`).
- `confidence`: alta · `residual_risk`: oito das onze chaves passam por presença, não por
  substância — um placeholder promove iniciativa a `READY_FOR_EXPERIMENT` sem aviso. E o gate só é
  exigido quando **alguém roda** o validador; o pipeline em runtime ainda depende da instrução na
  SKILL.md, então rodada não-rodada não tem gate nenhum.

## CRIT-06 (secundária — motor compartilhado × cópia) — **9** · banda `excelente`

O validador importa o motor e **não vendoriza nada**: `sys.path.insert(0, STRUCTURE_ROOT)` seguido
de `from _compartilhado.validador_schema import …` e `from _compartilhado.verificacoes_pacote
import …` (`:80-95`); não existe `validador_schema.py` nem `verificacoes_pacote.py` em lugar nenhum
da árvore do pacote, e `corpus_adversarial.py` reusa `import validate_workflow as V` (`:29-31`) em
vez de derivar uma segunda camada semântica. O import resolve a partir da profundidade real **nas
duas árvores** que confiri: `STRUCTURE_ROOT = PACKAGE_ROOT.parents[3]` cai em
`Estrutura Final de Skills\` na fonte e em `.claude\skills\` na cópia implantada, e `_compartilhado\`
com seu `__init__.py` está presente nas duas. A cópia divergente que o mantenedor paga depois
simplesmente não existe aqui — que é o ponto inteiro do critério.

- `failure_mode`: **barulhenta + localizada** — motor ausente vira
  `[FAIL] motor compartilhado ausente em {STRUCTURE_ROOT}: {exc}`, nomeando o diretório exato
  procurado, e `SystemExit(1)`. O operador aprende onde se procurou e tem o override
  `SKILL_STRUCTURE_ROOT` documentado; nunca recebe um PASS meio-validado.
- `confidence`: alta · `residual_risk`: a mesma inferência de `STRUCTURE_ROOT` que faz o import
  resolver também dirige `LEGACY_ROOT = STRUCTURE_ROOT.parent / "SKILL - Nova formula" / …`. Na
  cópia implantada isso resolve para `.claude\SKILL - Nova formula`, que **não existe** (verificado)
  — então operador rodando o validador **a partir da árvore de runtime** recebe FAIL num pacote
  íntegro, enquanto o docstring promete "depois da promoção, a raiz é inferida automaticamente".
  Custa um diagnóstico, não uma crença falsa, e `INNOVATION_LEGACY_ROOT` existe como escape.
  Costura menor: o handler pega só `ModuleNotFoundError`, então motor presente-mas-quebrado sai como
  traceback cru.

## CRIT-07 (secundária — recusa nomeada e risco de nota) — **9** · banda `excelente`

A recusa é **tipada e nomeada**, não narrada: `innovationRouteRejection` é objeto fechado exigindo
`code` de enum de sete valores incluindo `BLOCKED_BYPASS_ATTEMPT`, mais `observed_sender`,
`expected_route`, `violations` (minItems 1), `prevented_effect` e `resume_when`
(`schemas/…json:1491-1536`) — e `returned_to` é `const: "diretor-de-lentes"`, de modo que a própria
rejeição não pode vazar de lado. Contato lateral de saída é fechado do mesmo jeito: toda rota de
`execution_request` fixada em exatamente `[departamento-inovacao-melhoria, diretor-de-lentes]`,
`status` forçado a `RECOMMENDED_NOT_SENT` para que nenhum artefato possa alegar que o contato
aconteceu, Negócios exigindo `matrix_authorization.granted_by == "ceo-maestro"`, e Evolução de
Skills barrada como destino. Sobre a nota: fechada em dois eixos — 22 nomes de propriedade proibidos
via `collect_property_names` e varredura de padrão em texto livre aplicada ao relatório **e** ao
`DEPARTMENT_RETURN` de saída — com `zeroTestSummary` fixando pass/fail/skip em `const: 0`
(`:1343-1357`), de modo que contagem de QA também não pode ser lavada para dentro do envelope.

- `failure_mode`: **barulhenta + localizada, com uma costura silenciosa.** Rota ruim gera envelope
  endereçado nomeando remetente, violação e efeito impedido. A costura:
  `NEGATIVE_DECLARATION_FIELDS` faz `walk_strings` **pular dezessete subárvores inteiras**
  (`:144-165`), inclusive `risks`, `limitations`, `trade_offs` e `claims_unverified` — então
  "alternativa vencedora, nota 9,8" escrito em `report["risks"]` nunca é varrido e viaja silencioso
  para o relatório que o Diretor lê. A isenção tem justificativa escrita e o pacote nomeia a classe
  como **R7** ("a trava segura o vocabulário, não o sentido"), o que faz disto risco menor nomeado e
  não lacuna.
- `confidence`: alta · `residual_risk`: nota ou veredito redigido dentro de `risks`, `limitations`
  ou `trade_offs` é invisível à varredura anti-julgamento e chega ao Diretor sem sinalização.
  Estruturalmente, R1 e R8 são honestos que o runtime não tem controle de canal algum — a recusa é
  contratual e auditável só depois do fato, então quem adotar **não pode** ler "recusado com
  envelope nomeado" como contenção técnica.

## CRIT-08 (secundária — fonte referenciada, não copiada) — **9** · banda `excelente`

Resolvi cada citação a partir da profundidade real, em vez de ler a string. **Dez citações**, todas
apontando para fora do pacote, todas caindo no mesmo arquivo: raiz usa `../../../../` (quatro acima
= raiz da estrutura), `references/` usa cinco, os três `SKILL.md` e os três contratos de agente usam
seis — cada uma aritmeticamente correta contra a árvore-fonte **e** contra a cópia implantada, onde
`regras-de-ouro\REGRAS-DE-OURO.md` existe. Busca por `*REGRA*` dentro do pacote não retorna nada:
sem cópia paralela, sem reenunciado parcial das RI/RO, e o contrato o diz nas palavras do próprio
critério — "Este contrato referencia a fonte; não copia nem cria versão paralela." `RULES_PATH`
também está na lista de arquivos exigidos do validador, então ausência da fonte externa é FAIL e não
encolher de ombros.

- `failure_mode`: **barulhenta + localizada para seis das dez, silenciosa para quatro.**
  `link_errors()` (`:1655-1671`) resolve todo link markdown, então `SKILL.md:407`,
  `protocolo:456` e os três `SKILL.md` de agente quebram alto numa profundidade errada. Mas as
  **quatro citações de contrato são code spans, não links**, então `link_errors()` nunca as vê — um
  erro de profundidade ali seria silencioso. Raio de dano pequeno na prática: cada citação não
  checada fica no mesmo diretório de uma gêmea checada carregando a string idêntica.
- `confidence`: alta · `residual_risk`: as quatro citações de contrato são strings não verificadas.
  Se o pacote mover um nível de diretório, o ponteiro normativo que esses contratos chamam de "a
  fonte normativa única" quebra enquanto só as gêmeas linkadas falham — exatamente a divergência
  silenciosa que este critério existe para prevenir, fechada para o caso **cópia** e só parcialmente
  fechada para o caso **caminho**.
