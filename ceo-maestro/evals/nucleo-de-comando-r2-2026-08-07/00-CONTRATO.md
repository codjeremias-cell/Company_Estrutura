# Contrato — rejulgamento do núcleo de comando, rodada 2

- **Selado em:** 2026-08-07, **antes** de qualquer parecer existir.
- **Nível exigido:** `INTERNO` (7–9 → `ACEITO_USO_INTERNO`).
- **Alvos:** `ceo-maestro`, `diretor-de-lentes`, `departamento-juizes`, `departamento-negocios`.
- **Critérios:** os **seis**, todos remedidos. Nada é herdado.

## Por que remedir os seis, e não só os que mudaram

As tarefas 32, 33 e 34 endereçaram `C03`, `C04` e `C05`. A tentação era remedir só esses três.

**Não funcionaria**, e a aritmética diz por quê: o veredito é o **MENOR** dos seis. O `ceo-maestro`
trava em `C01` = 6, então melhorar três critérios não muda o veredito dele se o `C01` ficar de pé.

E o `C01` **também** foi endereçado — os juízes o baixaram citando duas coisas que já não existem:
o inventário que listava quatro subordinados diretos onde o contrato diz três (consertado na tarefa
33) e o despacho fora do protocolo (travado na tarefa 32).

Régua única, uma data, sem mistura.

## O que mudou na árvore desde a rodada 1

| tarefa | o que entrou | critério que ela endereça |
|---|---|---|
| **32** | trava: rodada de julgamento sem `JUDGE_ASSIGNMENT` **reprova**, derivada do disco, com 4 mutações | `C05`, `C01` |
| **33** | coletor de saída crua virou artefato versionado, com os 4 defeitos virando regra e gate de coerência | `C04`, `C01` |
| **34** | trava por forma: placar de pacote não declara total de cadeia no presente, ligada nos 15 | `C04` |
| **24** | as duas cópias de `adr-020` do laboratório ganharam sufixo `.candidate` | ruído de fundo |

**Cadeia: 1934 casos com 18 FAIL → 1951 casos com 1 FAIL.** Os quatro alvos fecham em **100%**.

## ⚠️ Esta rodada corre PELO PROTOCOLO — e a rodada 1 não correu

A rodada 1 foi despachada direto às lentes, sem `JUDGMENT_REQUEST`, `CRITERIA_MATRIX`,
`JUDGE_ASSIGNMENT`, `write_path` nem `custody_copy`. O protocolo chama isso de
`BLOCKED_BYPASS_ATTEMPT`, *"mesmo vindo do CEO ou de Jeremias"*. Três juízes acharam o desvio, e ele
era **reincidência** de um achado de 2026-07-28 ao qual nenhuma trava havia sido acrescentada.

Nesta rodada os envelopes existem, em `01-JUDGMENT-REQUEST.json`, `02-CRITERIA-MATRIX.json` e
`03-JUDGE-ASSIGNMENTS/`. **A trava da tarefa 32 reprova o pacote se eles faltarem** — não é
disciplina, é condição de o validador ficar verde.

## Os dois conflitos, de novo declarados

### 1. O `departamento-juizes` não pode ser julgado pelas próprias lentes

Recebe **painel externo**, como em 2026-07-29 e na rodada 1.

### 2. O `ceo-maestro` é o objeto e o operador — e o limite **não fechou**

Continuo executando os validadores e despachando, e sou um dos julgados. O que mudou desde a
rodada 1:

- os envelopes de protocolo existem e são **verificáveis por terceiro**;
- a saída crua passou por um **gate de coerência** que a rodada 1 não tinha — e que **fechou** na
  primeira tentativa desta rodada, por um falso positivo do meu próprio nome de caso, corrigido e
  reconferido por mutação;
- a `custody_copy` é tomada **antes** do despacho, com digest.

O que **não** mudou: há **um só ator de runtime**. `SKILL.md:52` proíbe o CEO de executar e
`SKILL.md:42` diz que ele não chama Juízes diretamente — e no runtime atual não existe um
despachante fora do CEO. **Isso fica declarado como limite, não resolvido.** É o mesmo teto `OI-04`.

> **Decisão de Jeremias, 2026-08-06:** as notas da rodada 1 valem, com fronteira declarada. Isso
> **não** autoriza repetir o bypass — e desde 06/ago a trava impede que ele passe em silêncio.

## Agregação — selada agora

MENOR entre as duas instâncias · MENOR entre critérios · nota **inteira**, sem média nem
compensação · `NAO_DISCRIMINADO` **apenas quando a faixa cruzada pode decidir**: havendo critério
acordado abaixo do corte, há **dominância** e o veredito é o da banda (`ADR-016` + precedente
`qa-usabilidade` de 05/ago, codificado no agregador).

## Contexto proibido

- `../nucleo-de-comando-2026-08-05/` **em todos os níveis** — contém as notas da rodada 1 destes
  mesmos quatro pacotes, que é exatamente o que se vai remedir.
- `../../REGISTRO-DE-VEREDITOS.md`, `../julgamento-pacotes-2026-07-29/08-RESUMO.md`,
  `../julgamento-nove-departamentos-2026-08-04/` (exceto o `00-CONTRATO.md`, pelas definições),
  `../recoleta-c03-c05-c06-2026-08-05/`.
- **Proibida busca larga** sobre `julgamento*`, `pareceres*`, `rejulgamento*`, `recoleta*`,
  `nucleo-de-comando-2026-08-05`. Se topar com nota, **pare e declare**.

> **Lição da rodada 1, corrigida aqui:** aquele contrato trazia as notas de 29/jul nas linhas 10-15
> — no primeiro arquivo que o despacho mandava abrir. Quatro juízes se contaminaram. **Este contrato
> não contém nota nenhuma**, e essa ausência é proposital.

## Ao juiz

Você foi designado por `JUDGE_ASSIGNMENT`, e o `ceo-maestro` — um dos julgados — participou da
cadeia que a emitiu. Se isso o constrangeu **em qualquer direção**, diga na seção contra si.

**Não presuma a direção do viés.** Na rodada 1, seis de seis instâncias relataram a tentação de ser
**mais duras** com quem as despachou, não mais brandas — o oposto do que o despacho previa. Não
tome isso como expectativa: é evidência de que a direção não é óbvia, e de que nomeá-la de antemão
atrapalha. Descreva o que sentiu, não o que se espera que sinta.
