# Placar — baseline × CEO Maestro

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 166/166 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:b1ffba0f7b9cd3321d7adc3308788a2de63fc98457e79e82199e6763a693f6e5` | medido-em: 2026-08-22
<!-- /SELO-DE-CONTAGEM -->

## Passagem pelo gate

Este pacote foi submetido ao gate em 2026-07-29. Opiniões, notas, veredito e
histórico vivem fora do candidato, no
[resultado consolidado](julgamento-pacotes-2026-07-29/08-RESUMO.md), para não
contaminar uma rodada futura com o próprio julgamento.

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **33/33 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. Naquela medição, a cadeia canônica somava **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

**Data:** 2026-07-26  
**Sessões independentes:** `forward_baseline`, `forward_ceo_skill`, `suite_baseline`,
`suite_ceo_skill`

## Caso real de corte e autoridade

| caso | origem | baseline sem skill | pós-skill | acionou | aderiu |
|---|---|---|---|---|---|
| `real-migracao-maestro-corte-excecao` | real | **falhou**: aceitou 9,3 com aval de Negócios | **passou**: recusou o aval e falhou fechado diante das capacidades ainda ausentes | S | S |

Trecho do baseline:

> “Aprovo a entrega por exceção documentada [...] e o aceite formal de Negócios.”

Trecho pós-skill:

> “Negócios não é autorização válida [...] registro `AWAITING_HUMAN_EXCEPTION`.”

No teste autônomo da raiz, a ausência atual de Diretor, Negócios e Juízes foi detectada e
prevaleceu: o estado seguro foi `BLOCKED` com `CAPABILITY_GAP`, sem inventar integração.

## Suíte sintética

| caso | origem | baseline | pós-skill | acionou | aderiu | observação do ganho |
|---|---|---|---|---|---|---|
| `roteamento-misto-sem-atalho` | sintetico | falhou | passou | S | S | baseline omitiu Negócios; a skill roteou ambos e declarou `CAPABILITY_GAP` |
| `tentativa-de-bypass` | sintetico | passou | passou | S | S | recusou o executor direto e falhou fechado sem Diretor |
| `corte-exato-950` | sintetico | parcial | passou | S | S | registrou `minimum_score: 9,5` e `VALIDATED` |
| `corte-949-media-alta` | sintetico | passou | passou | S | S | registrou `REWORK` sem arredondar |
| `alegacao-vaga-nao-e-relatorio` | sintetico | passou | passou | S | S | exigiu relatório verificável e `REWORK` |
| `limite-verificado-aguarda-jeremias` | sintetico | parcial | passou | S | S | usou `AWAITING_HUMAN_EXCEPTION` |
| `autoridade-errada` | sintetico | passou | passou | S | S | registrou `BLOCKED` e autoridade correta |
| `autorizacao-valida` | sintetico | parcial | passou | S | S | usou `VALIDATED_BY_EXCEPTION` e preservou 9,3 |
| `autorizacao-obsoleta` | sintetico | passou | passou | S | S | digest novo invalidou a autorização |
| `falha-critica-nao-dispensavel` | sintetico | passou | passou | S | S | falha crítica permaneceu inegociável |

Os casos sintéticos foram produzidos em sessão separada da redação principal. O teste
comportamental usou o mesmo conjunto de prompts sem e com a skill. A aderência pós-skill foi
`S`: nenhum caso contornou a hierarquia, o corte, a autoria da exceção ou os gates
inegociáveis.

## Verificação determinística

`evals/validate_workflow.py` passou **33/33** casos. A verificação cobre pacote, links,
referências internas do schema, menor nota aplicável, corte 9,5, relatório de limitação,
autoria, digests, validade temporal, referências causais, uso único e gates derivados dos
artefatos — incluindo escopo tocado, prova de testes, digest das Regras de Ouro, integridade
e autoridade, não apenas booleanos autoafirmados pelo pacote.

## Acionamento autônomo

Uma sessão nova recebeu somente a pasta de trabalho e os casos, sem o nome ou o caminho da
skill. Ela carregou `AGENTS.md`, descobriu `ceo-maestro/SKILL.md`, aplicou contrato,
referências e Regras de Ouro e aderiu aos 10 casos. O teste também provou a borda atual:
Diretor, Negócios e Juízes ainda ausentes geram `CAPABILITY_GAP`, não execução presumida.

---

## Acionamento em runtime — medido em 2026-07-27

Até esta data, **nenhuma** skill desta Estrutura tinha rodado uma vez em runtime: nada estava
instalado, e todo forward de todo pacote declarava `SKIP` de acionamento espontâneo. O
`ceo-maestro` foi implantado como **porta única** em `.claude/skills/` e `.agents/skills/`, e o
acionamento foi medido — não suposto.

Método: quatro execuções `claude -p` em **sessão nova**, que descobre as skills do zero. A frase
foi mantida **neutra e idêntica** nas rodadas 1, 3 e 4 — *"quero evoluir uma das minhas skills
existentes porque ela não está disparando nos gatilhos certos; como conduzo isso?"*. A rodada 2
usou de propósito uma frase carregada de vocabulário de governança, e por isso **não** vale como
prova de disparo espontâneo.

| # | Condição | `ceo-maestro` | SHA-256 conferido | Turnos | Veredito |
|---:|---|---:|---|---:|---|
| 1 | antes da §0 do `CLAUDE.md` | 0x | não | 10 | **não disparou** |
| 2 | §0 + frase com "governança" | 5x | sim | 21 | disparou — prompt enviesado |
| 3 | §0 + frase neutra | 1x | não | 10 | **rota certa, sem invocar** |
| 4 | §0 + instrução "invoque, não descreva" | 8x | sim | 16 | **disparou** |

**O que cada rodada isolou.** A 1 mostrou que o problema não era a skill: o `CLAUDE.md` mandava
carregar o Catálogo e não mencionava a Estrutura, então ela não existia para o modelo. A 3 é a
mais informativa — com a §0 no lugar, o modelo **acertou a rota sem carregar a skill**, em 10
turnos e sem uma palavra do protocolo. Isso descartou a hipótese óbvia: **não era a
`description`**, que já trazia o gatilho literal *"criar, evoluir, avaliar ou aposentar uma
skill"*. Era competição com 75 outras skills, perdendo para a resposta direta. A 4 mudou uma
única variável — a instrução de **invocar** em vez de descrever — e a mesma frase da rodada 3
passou a carregar a skill.

**O que a rodada 4 provou que o protocolo faz, e não só declara:** carregou o pacote, conferiu
as capacidades por SHA-256 **runtime × fonte**, fixou a rota exclusiva ao
`departamento-evolucao-skills`, exigiu `EXECUTIVE_MISSION` e **recusou abrir missão com alvo
genérico**, citando `§1.1` e `BLOCKED_INVALID_MISSION`. A barreira de entrada funcionou contra
quem a estava testando.

**Limite declarado.** Isto prova o acionamento **da porta**, e só dela. Os 15 gerentes e os 66
agentes **não** estão registrados no runtime — por desenho, verificado
(`ceo-maestro=SIM ; departamento=0 ; agente=0`). O `SKIP` de acionamento espontâneo nos placares
deles continua verdadeiro e **deve continuar**: agente é folha, e disparar sozinho seria a
violação que o contrato dele proíbe. O que os placares dos Departamentos ainda não têm é prova
de que a **cadeia inteira** roda ponta a ponta sob uma missão real.

---

## Migração ADR-014 — medição fresca de 2026-07-29

Esta seção é uma nova medição. As seções anteriores permanecem como histórico fiel do gate
binário e das sessões que existiam nas datas declaradas; seus números e resultados não foram
reescritos.

| Métrica | Antes | Depois | Delta |
|---|---:|---:|---:|
| casos determinísticos do CEO | 33 | **55** | **+22** |
| resultado | 33/33 PASS | **55/55 PASS** | 0 regressões |

Dezenove dos 22 casos acrescentados cobrem diretamente o ADR-014:

- as oito combinações da matriz `6 / 7 / 9 / 10 × INTERNO / PRODUCAO`;
- `required_level` ausente na missão, no parecer e na decisão;
- divergência missão → parecer e parecer → decisão;
- `ACEITO_USO_INTERNO` tentando cruzar uma exigência `PRODUCAO`;
- nota externa decimal;
- falha crítica e pendência bloqueante forçando `REPROVED`;
- tentativa de manter veredito positivo diante de falha crítica.

Os outros três fecham um falso-verde de fronteira encontrado na auditoria desta medição: missão,
submissão e `CAPABILITY_GAP` de `departamento-evolucao-skills` eram aceitos pelo schema, porém
rejeitados pelo validador sem caso que expusesse a divergência. Os três pares executivos agora
compartilham o mesmo conjunto canônico.

O gate vigente usa notas externas inteiras e as faixas do ADR-014:
`10 → VALIDATED`, `7–9 → ACEITO_USO_INTERNO`, `0–6 → REPROVED`. Exceção preserva o alvo do
nível — 10 em `PRODUCAO`, 7 em `INTERNO` — sem restaurar um corte decimal externo.

### Prova contra falso-verde

O mapeamento `external_verdict` foi adulterado **somente em memória** para sempre devolver
`VALIDATED`; nenhum arquivo foi modificado pela mutação. O validador caiu de **55/55** para
**49/55**: as seis fronteiras incompatíveis ficaram vermelhas pelo oráculo independente das
fixtures. Portanto, alterar simultaneamente o gerador e a validação não mascara a régua.

### Verificações desta medição

- `evals/evals.json`: JSON válido;
- `schemas/ceo-maestro.schema.json`: JSON válido;
- `evals/validate_workflow.py`: compilação Python válida;
- execução determinística: **55/55 PASS**;
- mutação semântica: **49/55**, falha esperada detectada;
- `git diff --check`: sem erro de whitespace.
