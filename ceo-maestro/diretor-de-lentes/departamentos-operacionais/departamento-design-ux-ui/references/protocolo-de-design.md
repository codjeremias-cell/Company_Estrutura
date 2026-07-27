# Protocolo do Departamento de Design UX/UI

Como a demanda entra, atravessa os sete agentes e volta ao Diretor. Fonte normativa única:
[`REGRAS-DE-OURO.md`](../../../../../regras-de-ouro/REGRAS-DE-OURO.md).

## Envelopes

| Envelope | De → Para | Papel |
|---|---|---|
| `DEPARTMENT_MISSION` | Diretor → gerente | a demanda |
| `DESIGN_PLAN` | gerente (interno) | modo, Design Read, ondas e agentes acionados |
| `DESIGN_TASK` | gerente → agente | uma capacidade, um agente, com `forbidden_context` |
| `DESIGN_RETURN` | agente → gerente | a resposta daquela ótica, com evidência tipada |
| `DESIGN_LEDGER` | gerente (interno) | cobertura das nove dimensões, gate visual e consolidação |
| `DESIGN_CAPABILITY_GAP` | gerente → Diretor | falha fechada: superfície ausente, fora de escopo, ou executor inexistente |

O `DEPARTMENT_RETURN` entregue ao Diretor **não é definido aqui**: ele pertence ao schema do
`diretor-de-lentes`, e é lá que sua estrutura é validada. O que este Departamento produz é o
`DESIGN_LEDGER`, convertido mecanicamente no envelope que o Diretor consome.

O `causalHeader.producer` é travado por `const` em `departamento-design-ux-ui`.

## Modos

**`PROJETO`** — superfície nova. Exige briefing, fluxo, conteúdo e restrições; hipóteses explícitas
permitem avançar.

**`POLISH`** — superfície que já existe (dimensão 8). Audit → Critique → Polish → Animate → Harden →
Live. **Superfície observável é obrigatória**: sem tela, captura, código de interface ou URL
acessível, o modo não abre e a gerente emite `DESIGN_CAPABILITY_GAP`. Afirmar polish sobre tela
ausente é a falha que o legado nomeou e que aqui é bloqueio de schema.

## Ondas

**Onda 0 — admissão e Design Read.** A gerente confere escopo ([fronteiras](fronteiras-do-departamento.md))
e classifica **cada sinal** do que recebeu:

| Rótulo | Significa |
|---|---|
| `OBSERVADO` | lido ou visto diretamente, com caminho, URL, id ou captura |
| `INFORMADO` | declarado por quem pediu, sem inspeção |
| `HIPOTESE` | inferência rotulada, acompanhada do risco |
| `AUSENTE` | necessário e indisponível |

Declara em uma linha: *"Lendo isto como: {tipo} para {público}, tarefa {tarefa}, linguagem {vibe},
sob {restrições}, rumo a {direção provisória}."* Fundamento de direção que não esteja ligado a um
desses quatro rótulos não entra.

**Onda 1 — direção.** `agente-direcao-e-anti-slop` fixa a direção deliberada, ancorada em heurística,
Lei de UX ou dado — nunca em gosto.

**Onda 2 — fluxo antes da tela.** `agente-fluxo-estados-e-transicoes` entrega ator, gatilho,
pré-condições, caminho principal, desvios, prevenção e recuperação de erro, e o mapa de transições.
**A produção de tela fica bloqueada enquanto o fluxo não fechar.**

**Onda 3 — superfície revisável (mockup-first).** Antes de qualquer implementação, uma superfície
proporcional ao risco: wireframe anotado ou especificação visual inequívoca. Nela agem, em paralelo:
`agente-linguagem-visual`, `agente-design-system-e-tokens`, `agente-nitidez-e-adaptacao` e, quando
houver dado a mostrar, `agente-dataviz`.

**Onda 4 — verificação independente.** Sobre a saída da onda 3, e **por agentes que não a
produziram**: `agente-acessibilidade-medida` mede os valores reais, e `agente-direcao-e-anti-slop`
roda os testes anti-slop de 1ª e 2ª ordem. É a separação por conflito de interesse do ADR-009.

**Onda 5 — gate visual e consolidação.** A gerente monta o `DESIGN_LEDGER`, apura a cobertura das
nove dimensões e trata o `DESIGN_GATE`.

## O gate visual

`DESIGN_GATE` tem três estados: `PENDING`, `APPROVED`, `REJECTED`.

- nasce `PENDING` e **só** vira `APPROVED` com **ator autorizado nomeado** e momento registrado;
- **enquanto estiver `PENDING`, nenhuma `delegated_dependency` de implementação sai** — o schema
  recusa. É o mockup-first virado trava;
- comentário informal, ausência de objeção e "o código já está pronto" **não são aprovação**.

## Gates locais

| # | Gate | Falha |
|---|---|---|
| G1 | missão pertence a este Departamento | devolve ao Diretor sem produzir |
| G2 | modo `POLISH` com superfície observável | `DESIGN_CAPABILITY_GAP` |
| G3 | todo fundamento de direção com sinal rotulado | plano rejeitado |
| G4 | fluxo fechado antes de qualquer tela | onda 3 não abre |
| G5 | dimensão 2 nunca `AUSENTE` — estados não se adiam | entrega bloqueada |
| G6 | nenhum critério atendido sustentado por `REPORTED`/`UNAVAILABLE` | retorno rejeitado |
| G7 | quem produziu a linguagem visual não mede a11y nem roda anti-slop | plano rejeitado |
| G8 | `DESIGN_GATE: APPROVED` antes de dependência de implementação | dependência rejeitada |
| G9 | primitivas do stack nomeadas | dimensão 7 não fecha |

## Taxonomia de evidência

| Tipo | Significa | Pode sustentar "atendido"? |
|---|---|---|
| `OBSERVED` | artefato inspecionado | sim |
| `PRODUCED` | artefato realmente gerado | sim |
| `MEASURED` | valor **e** método registrados | sim |
| `REPORTED` | alegação sem verificação independente | **não** |
| `UNAVAILABLE` | prova não obtida, com motivo | **não** |

Critério sem medição é `UNVERIFIED` e **nunca** é promovido a aprovado. Se a medição exigir execução
fora do escopo, sai como dependência — não se executa aqui.

## Riscos residuais declarados

- **R1 — especificação não é tela.** O que sai daqui é desenho e contrato; a fidelidade real só
  aparece implementada. A dimensão 5 é verificada sobre a especificação, não sobre o build.
- **R2 — `MEASURED` depende de quem mede.** O schema exige valor e método; não recomputa o valor.
  Contraste declarado com método plausível passa. É encarecimento da fabricação, não impedimento.
- **R3 — anti-slop é juízo, não métrica.** Os testes de 1ª e 2ª ordem são adversariais e
  qualitativos. A separação de agentes reduz a autocomplacência; não a elimina.
- **R4 — o gate visual depende de um ator externo.** Se ninguém aprovar, o ramo fica `PENDING` por
  desenho. É falha fechada intencional.
- **R5 — existência das ondas (R6 da casa).** Um `DESIGN_LEDGER` coerente é reproduzível sem que
  nenhuma `DESIGN_TASK` tenha sido emitida. Exigir registro de emissão encarece; não impede.
- **R6 — Impeccable é referência externa.** As leis vêm de `pbakaus/impeccable` (Apache-2.0) via
  catálogo canônico. Se a referência mudar, a direção daqui não é notificada automaticamente.
