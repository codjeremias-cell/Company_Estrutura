# Placar de migração — Departamento de Desenvolvimento

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 131/131 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:7964131d36f8d5be163b527beaf82346f844cd044c25b729cbcda4d28eda84f4` | medido-em: 2026-09-02
<!-- /SELO-DE-CONTAGEM -->

## Passagem pelo gate

Este pacote foi submetido ao gate em 2026-07-29. Opiniões, notas, veredito e
histórico vivem fora do candidato, no
[resultado consolidado](../../../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md),
para não contaminar uma rodada futura com o próprio julgamento.

> **Reconciliação de 2026-07-26 (histórico, não vigente).** O número próprio **nessa data** foi 105/105 PASS. **Não republicar 105/105 como resultado corrente.** O vigente do validador é a linha `CONTAGEM-VIGENTE` do selo. Totais de cadeia daquela medição ficam no retrato datado, não nesta tabela.
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

Data: 2026-07-26
Versão avaliada: 1.0.0
Escopo: migração de `SKILL - Nova formula/maestro/comite-de-lentes/lente-dev-senior` (37 arquivos)
para `…/departamentos-operacionais/departamento-desenvolvimento`, fundamentada na canônica
`dev-senior` e nos **31 geradores de desenvolvimento** do catálogo

## Resultado vigente

> Esta tabela **não** publica 105/105. Esse número é retrato de 2026-07-26
> (parágrafo histórico acima). O vigente do validador é o selo `CONTAGEM-VIGENTE`.

| Verificação | Resultado | Executado? |
|---|---:|---|
| Validador determinístico do Departamento | ver selo CONTAGEM-VIGENTE | **sim** |
| Cadeia integrada da estrutura | ver regressão final | **sim** |
| Baseline do pacote legado | — | **NÃO — existe no legado, não reproduzido** |
| Auditoria independente | EXECUTADA 2026-08-03 · NONCOMPLIANT · 4 achados | **sim — ver estado vigente 2026-08-08** |
| Parecer dos Juízes | EMITIDO 2026-08-03 · REPROVED · min 6 faixa 6–7 | **sim — ver estado vigente 2026-08-08** |

## CRIT-06 — TETO_HONESTO (nao e o catalogo estrutural de 16 casos)

O catalogo em `evals.json` (16 casos PORTAO/OPERACAO, exercitado pelo validador
na secao "O que o validador prova / Catalogo") **nao** e esta prova.

A prova comportamental dos 16 forwards contra instancia nova e independente:
**TETO_HONESTO**. Nao rodou. Nao e PASS. Nao fabricar `FORWARD-TEST.md`.

```bash
python evals/validate_workflow.py
```

## A trava que distingue este Departamento

Todos os outros travam `test_summary` em `0/0/0` por `const`. **Aqui o validador prova o
contrário:** existe um caso que falha se `pass` estiver travado em zero. É a verificação mecânica do
ADR-012 §1 — o Departamento que escreve o código é exatamente o que precisa provar que ele roda.

## O que o validador prova

**Pacote e vínculos (9).** Arquivos da gerente e as **seis** referências; `agentes/` com exatamente
os oito nomes; frontmatter com `description` entre aspas e ≤ 1024; `short_description` de 25–64;
posição na hierarquia em runtime; fonte normativa no caminho relativo de cada nível; links internos
resolvendo; `workerId` batendo com as pastas reais.

**Travas do ADR-012 (6).** Nenhum campo de **nota** e nenhum campo de **decisão alheia** (`modulo`,
`c4`, `topologia`, `ownership`, `grao`, `one_row_means`, `expand_contract`, `token_semantico`,
`paleta`) em qualquer profundidade do schema. `producer` travado; `executed_by` travado no agente de
testes; `falha_explicita` do `ponytail` travada em `true`; e **`pass` deliberadamente não travado**.

**Artefatos aceitos (19).** `DEV_PLAN` com e sem upstream, as oito `DEV_TASK` e os oito `DEV_RETURN`,
`DEV_CAPABILITY_GAP` e `DEV_LEDGER` com o gate fechado.

**Casos negativos — plano (3).** Upstream ausente com atribuição emitida; upstream ausente sem
nomear o que falta; produtor forjado.

**Casos negativos — tarefa (4).** Capacidade trocada; verificação independente fora da onda 3;
`forbidden_context` sem a proibição de decidir ou inventar; agente de outro Departamento.

**Casos negativos — retorno (24).** Implementação sem degrau da escada e sem artefato; **os cinco
inegociáveis marcados como simplificados**, um a um; inegociável não simplificado (aceito); **quem
implementa produzindo a própria evidência**; **revisor revisando a si mesmo**; testes sem evidência e
sem borda; evidência produzida por quem não é o agente de testes; `SKIP` sem e com motivo; borda
ausente sem e com justificativa; `ponytail` sem teto e completo; `SUPOSIÇÃO` sem e com motivo de não
confirmação; **quarta tentativa de correção**; terceira sem causa raiz; terceira com causa raiz e
pendência (aceita); `BLOCKED` sem motivo.

**Casos negativos — livro-razão (10).** `ENTREGUE` com cada uma das três bordas descoberta; com
`FAIL`; sem revisão independente; sem registro de emissão; com pendência; lacuna aberta sem e com
bloqueio; `INCOMPLETA` legítima; retorno fora do Diretor.

**Fronteira com o consumidor (6).** O `DEV_LEDGER` vira `DEPARTMENT_RETURN` **com número real de
teste** e é validado contra o schema do `diretor-de-lentes`. Mais: o Diretor reconhece este
Departamento em `operationalDepartment` e `knownCapability`, e **Arquitetura e Dados delegam para
cá** — as dependências que elas emitiam para o vazio agora têm destinatário.

**Recalculado em código (17).** Sem consultar campo declarado: o gate fecha com bordas cobertas,
bateria verde, revisão feita e emissão registrada; **não fecha** com qualquer borda descoberta, com
`FAIL`, sem revisão, sem emissão, com lacuna, **com prova de outra versão** ou com evidência
produzida por quem implementou. Mais a aritmética das partes: seis capacidades implementam e duas
verificam; os cinco inegociáveis e os cinco tracks batem com os enums.

**Catálogo (6).** 16 casos, todos com `acionou`/`aderiu`, **separados em `PORTAO` e `OPERACAO`** —
com ao menos quatro de operação. A separação é resposta direta ao defeito de instrumento encontrado
no forward de 2026-07-26: catálogo que só traz pedido cru mede bem a recusa e mede a execução por
hipótese.

## Defeito encontrado e corrigido

**A armadilha de profundidade, pela quinta vez.** Os links do ADR-012 para os ADR-006, 008 e 009
saíram com `../` em vez de `../../`. Quinta ocorrência com o aviso escrito como armadilha nº 1 do
guia. O `validate_links` pegou, como nas quatro anteriores. Já não é descuido isolado: é dado de que
o aviso em prosa não previne, e de que a única defesa que funciona é a mecânica.

## O que ainda não foi provado

### Estado vigente das obrigações — conferido em 2026-08-08

> **Duas obrigações desta seção estavam declaradas como pendentes e não estão.** A campanha [`remedicao-dos-sete-2026-08-03`](../../../../evals/remedicao-dos-sete-2026-08-03/PLACAR.md) executou as duas sobre este pacote. O texto dos itens abaixo é registro da rodada em que foi escrito e fica como está; o estado corrente é este.

| obrigação | estado em 2026-08-08 | quem emitiu |
|---|---|---|
| Auditoria independente | **EXECUTADA** em 2026-08-03 · `governance_report` **NONCOMPLIANT** · **4 achados** nomeados, com dono e condição de correção | `departamento-auditoria-responsabilidades` |
| Parecer dos Juízes | **EMITIDO** em 2026-08-03 · veredito **REPROVED** · `minimum_score` **6**, faixa **6–7** · **5 de 8** critérios `NAO_DISCRIMINADO` | `departamento-juizes` |

> **A faixa atravessa o corte, e isso é o achado — não um detalhe.** Duas instâncias da mesma lente, sobre os mesmos bytes e com a mesma rubrica, divergiram em 54% dos pares na campanha. Onde a faixa cruza o 6/7, consertar "até passar" seria mirar num número que a régua não distingue. O aceite interno deste pacote **nunca esteve estabelecido**, e continua não estando.

### Dono e condição de fechamento, item a item

> Exigido pelos achados `CA-01` e `GR-01`/`GR-02` da mesma campanha: pendência declarada sem dono é pendência de ninguém. "O próprio Departamento" significa o pacote que este placar mede — ele responde pela própria evidência.

| item | dono | fecha quando |
|---:|---|---|
| 1 | o próprio Departamento | os 16 casos forem executados contra instância nova e independente, com `FORWARD-TEST.md` registrando `acionou` e `aderiu` MEDIDOS |
| 2 | o próprio Departamento | a `lente-dev-senior` for reproduzida com instrumento comparável, ou este item registrar a decisão de não comparar, com motivo |
| 3 | `departamento-auditoria-responsabilidades` e `departamento-juizes` | os dois emitirem sobre este pacote sem achado bloqueante e sem `REPROVED`. Ver o estado vigente acima — nenhum dos dois está pendente |
| 4 | o próprio Departamento | houver medida de cobertura de REQUISITO, e não só de execução |
| 5 | o próprio Departamento | o schema recomputar se o teste exercita a borda que declara exercitar |
| 6 | o próprio Departamento | o uso do gerador for DERIVADO da evidência em vez de autodeclarado, no molde de `contar_ancoras_declaradas` |
| 7 | `diretor-de-lentes` | o Diretor ampliar o acervo de tracks ou registrar o corte atual como definitivo, com data |


1. **Forward comportamental.** Os 16 casos não foram executados. Não há evidência de que a skill
   dispara nos gatilhos, nem de que segura a RO-01 sob o pedido direto de usar uma assinatura
   inventada. O catálogo já nasce com a separação portão/operação, mas nenhum dos dois foi rodado.
2. **Baseline.** A `lente-dev-senior` tem `placar-baseline.md` e duas rodadas de evals. **Não foram
   reproduzidos**, e os instrumentos não são comparáveis: o legado media orquestração com time
   descoberto em runtime, que este pacote deliberadamente não tem.
3. **Auditoria independente e parecer dos Juízes.** Não pendentes. Estado vigente em 2026-08-08: Auditoria EXECUTADA NONCOMPLIANT; Juízes EMITIDO REPROVED. Ver a tabela de Resultado vigente.
4. **R1 — verde não é correto.** A bateria prova que o que foi testado passa, não que o requisito
   foi atendido.
5. **R2 — cobertura de borda é declarada, não medida.** O schema exige os três estados; não
   recomputa se o teste exercita a borda que diz exercitar.
6. **R3 — `generator_used` é autodeclarado.** Nada aqui prova que o gerador foi invocado.
7. **R7 — a cobertura do Departamento é a do catálogo, não a do mercado.** Cinco tracks porque o
   acervo tem cinco. Go, Python, .NET e React Native falham fechados — o que é correto, e é também
   uma limitação a declarar.

## Adendo 2026-08-16 — T71 C10 entrada (histórico)

Registro da primeira overlay de entrada. **Não descreve o estado vigente**
desta overlay r3 e **não rotula este candidato**. Substituído pelo adendo r3.

## Adendo 2026-08-21 — T71 C10 r3 (linhagem B)

`mission_verdict` distingue const ausente (`BLOCKED_CONST_AUSENTE`) de
producer forjado (`BLOCKED_BYPASS_ATTEMPT`). Ausência de `$defs` ou de
`departmentMissionAdmission` fecha `BLOCKED_BYPASS_ATTEMPT`, nunca exceção.
`$def` com `additionalProperties` false e os 18 `required` do envelope do
Diretor. Title/description não chamam `DEPARTMENT_MISSION` de envelope interno.
`oneOf` e `mission_verdict` são a mesma autoridade.

Tabela Resultado vigente: sem 105/105, sem Juízes/Auditoria pendentes.
CRIT-06 em seção própria, inconfundível do catálogo estrutural de 16 casos.
FAIL ambiental T87/T88 leva o rótulo `ENV-T87/T88` no stdout.
Receita de rollback em `evals/ROLLBACK.md` com hash de origem.
Sem `FORWARD-TEST.md`.

## Adendo 2026-08-21 — T71 C10 r4 (conserto)

O caso `FAIL ambiental T87/T88 tem rotulo ENV no validador` deixou de
grep o proprio fonte pelo literal contiguo — o mutador trocava esse
literal no caso junto com a producao e o caso seguia verde. A assercao
reconstrói o token em partes e exige o texto de emissao na producao
(o print). O selo `CONTAGEM-VIGENTE` e a contagem medida desta custodia,
com o digest normalizado do instrumento, nao a contagem narrada.
