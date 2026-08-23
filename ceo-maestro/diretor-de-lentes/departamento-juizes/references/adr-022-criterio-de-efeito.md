# ADR-022 — o critério que pergunta se o pacote melhora alguma coisa

- **Estado:** **DECIDIDO** por Jeremias em 2026-08-05 · **AINDA NÃO EM VIGOR**
- **Decidido por:** **Jeremias**, em 2026-08-05, ao mandar executar a troca nas duas direções entre
  o Catálogo e a Estrutura — *"vamos executar as trocas… todas elas"*.

  **DECIDIDO NÃO É O MESMO QUE EM VIGOR.** Este ADR altera o conjunto de critérios que os Juízes
  recebem. Só entra em vigor por candidato julgado — `EXECUTIVE_MISSION` à Evolução, alteração no
  schema, julgamento com duas instâncias por lente. Até lá, as campanhas seguem com os critérios
  que seus contratos declararem.
- **Origem:** investigação de 2026-08-05 sobre por que o Catálogo alcança 9,3–9,6 e a Estrutura
  trava. Ver `ceo-maestro/evals/` e o `PADRAO-DE-AUTORIA.md` §11 do Catálogo.

---

## O achado

**A Estrutura produz medida de efeito e não a consome.**

- **Produz:** `ADR-004` do `departamento-evolucao-skills`, decisão 7 — *"Admissão só com
  vermelho→verde executado. Nenhum candidato é recomendado sem o placar **baseline × pós-skill**
  rodado."* Medido em 2026-08-05: **15 de 15** pacotes têm `PLACAR.md`; **14 de 15** trazem
  baseline; **7 de 15** trazem as colunas de comportamento `acionou` / `aderiu`.
- **Não consome:** dos seis critérios de 2026-08-04 (`C01` contrato · `C02` schema · `C03` trava
  com prova · `C04` evidência · `C05` uso pela cadeia · `C06` limites), e dos oito de 2026-07-29,
  **nenhum pergunta se o pacote melhora o resultado**. O mais próximo, `C05`, mede **integração** —
  se a cadeia atravessa —, não **delta**.

O placar existe como artefato e é julgado pela sua **honestidade** (`CRIT-06` de 2026-07-29:
*"distingue PASS/FAIL/SKIP, não transforma ausência em sucesso"*), **nunca pelo seu resultado**.

> **O gate não tem porta de entrada para *"isso melhorou alguma coisa?"*.**

## A decisão

Passa a existir o critério **`C07` — Efeito demonstrado**, dono `robustez-e-evidencia`:

> O pacote demonstra **vermelho → verde executado**: existe caso em que, **sem** o pacote, o
> resultado falha, e **com** o pacote, passa — com a falha do baseline observada, não suposta.
> Contorno é defeito do pacote. Caso em que o baseline **já passa** não conta como efeito: conta
> como **redundância**, e redundância é achado.

| como falha | |
|---|---|
| placar sem baseline executado | o efeito é alegado, não medido |
| baseline que já passa | o pacote é redundante naquele caso |
| `acionou` / `aderiu` ausentes | mede-se o texto, não o comportamento |
| caso não-discriminante não declarado como tal | número que não separa, publicado como se separasse |

**Herdado do `PADRAO-DE-AUTORIA.md` §11 do Catálogo**, item a item — inclusive a trava de
redundância (*"se o baseline já passa sem a skill, a skill é redundante — não crie"*) e as duas
colunas de comportamento.

## O preço, medido e declarado ANTES de decidir

**Este ADR baixa notas. Ele não sobe nenhuma.**

Com agregação por **MENOR**, acrescentar critério só pode **baixar ou empatar** o `minimum_score` —
nunca subir. Medido sobre os nove departamentos em 2026-08-05: mínimo atual **6**; com um sétimo
critério, o mínimo é **6 ou menos**, jamais mais.

E o `ADR-014` é duro com quem não tem material: *"critério sem nota **proíbe** qualquer veredito
positivo e abre lacuna"*. Hoje **1 de 15** (`departamento-qa-usabilidade`) não tem baseline no
placar; **8 de 15** não têm as colunas de comportamento. Sem material, o `C07` nasce como lacuna.

**Jeremias foi informado disso antes de decidir**, nestes termos: *"a troca não vai fazer skill
nenhuma subir de nota — o ganho é de verdade, não de número"*. A decisão foi tomada assim mesmo,
e é isso que este parágrafo registra.

## O que este ADR NÃO faz

- **Não muda a agregação.** Continua MENOR entre instâncias e MENOR entre critérios (`ADR-016`).
- **Não muda as bandas nem os níveis** do `ADR-014`.
- **Não torna o `C07` obrigatório em toda campanha.** Ele entra no conjunto disponível; cada
  contrato declara os critérios que usa, e critério fecha na origem (protocolo §1).
- **Não retroage.** Julgamento fechado não se reabre por causa dele.

## O que fica aberto

| id | limite | dono | condição de fechamento |
|---|---|---|---|
| `A22-01` | 8 de 15 pacotes sem `acionou`/`aderiu` no placar | `departamento-evolucao-skills` | as duas colunas passam a ser exigidas na produção do placar |
| `A22-02` | `departamento-qa-usabilidade` sem baseline | `diretor-de-lentes` | placar do pacote ganha baseline executado |
| `A22-03` | o poder de separação do instrumento é baixo — o piloto de 2026-07-26 mediu **5 de 9 casos separando (55%)** | `departamento-evolucao-skills` | medir de novo depois de `A22-01`; se seguir ~55%, o `C07` mede ruído |
| `A22-04` | quem executa o placar não é quem julga, e a lente `robustez-e-evidencia` **não executa** por contrato | `ceo-maestro` | manter o desenho de executor independente publicando saída crua, como na T19 |

**`A22-03` é o risco real deste ADR:** se o instrumento separa em 55% dos casos, um critério
construído sobre ele carrega essa imprecisão para dentro do veredito. O `ADR-016` já ensinou que
régua com folga maior que o degrau produz `NAO_DISCRIMINADO`, não decisão.
