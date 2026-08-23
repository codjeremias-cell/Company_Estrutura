# Contrato — rejulgamento do núcleo de comando

- **Selado por:** `ceo-maestro`, em 2026-08-05, **antes** de qualquer parecer.
- **Decidido por:** **Jeremias**, em 2026-08-05.
- **Árvore julgada:** commit **`ee916c6`**.
- **Nível exigido:** `INTERNO` (7–9 → `ACEITO_USO_INTERNO`).

## Os quatro alvos, e por que agora

| pacote | nota vigente | medida em |
|---|---:|---|
| `ceo-maestro` | **1** (com crítica) | 2026-07-29 |
| `diretor-de-lentes` | **1** (com crítica) | 2026-07-29 |
| `departamento-juizes` | **2** (com crítica) | 2026-07-29 |
| `departamento-negocios` | **5** (com crítica) | 2026-07-29 |

**As quatro piores notas da casa, e as mais velhas.** Foram medidas **antes** do `ADR-016`
(agregação entre instâncias), **antes** das canonizações das tarefas 14, 15, 16, 19 e dos adendos de
contagem, e antes de tudo que se aprendeu nas dez rodadas de julgamento desde então.

Os dez departamentos operacionais foram rejulgados — sete deles duas vezes. **Estes quatro, nenhuma.**
Enquanto isso não mudar, **quem julga carrega as piores notas da árvore, medidas com a régua mais
velha, e nunca se submeteu ao que aplica nos outros.**

## ⚠️ Dois conflitos de interesse, declarados e tratados

### 1. O `departamento-juizes` não pode ser julgado pelas próprias lentes

As três lentes (`fidelidade-e-contrato`, `robustez-e-evidencia`, `experiencia-e-risco`) são
**agentes dele**. Julgá-lo com elas é autojulgamento.

**Precedente da casa, seguido aqui:** em 2026-07-29, `00-CONTRATO-E-MANIFESTO.md` estabeleceu —
*"`departamento-juizes` recebe painel externo, porque não pode julgar a si"*.

**Tratamento:** o `departamento-juizes` recebe **painel externo**, com juízes que não pertencem à
sua estrutura e que recebem os critérios sem herdar o protocolo dele.

### 2. O `ceo-maestro` é o objeto e o operador

**Eu executo os validadores, publico a saída crua, selo este contrato, despacho os juízes e agrego o
resultado — e sou um dos quatro julgados.** É o conflito máximo desta casa, e ele **não tem solução
completa no runtime atual**.

O que **é** feito para reduzi-lo:

- este contrato está **selado antes** de qualquer parecer existir, com critérios e agregação fixos;
- a saída crua foi publicada **antes** do despacho, e é a mesma para os quatro;
- **os juízes são avisados de que estão julgando quem os despachou** — e instruídos a dizer se isso
  os constrangeu;
- a agregação é **derivada por regra**, não escolhida: MENOR entre instâncias, MENOR entre critérios;
- os pareceres são gravados em **worktrees isolados**, fora do meu alcance de edição.

O que **não** é resolvido, e fica declarado como limite: **quem pede o julgamento é o julgado.**
Fechar isso exige um despachante fora do `ceo-maestro`, que não existe no runtime atual — é o mesmo
teto `OI-04` já nomeado nesta casa: *forjar a evidência é chamar as mesmas funções que a verificam*.

## Os seis critérios, inalterados

`C01` contrato e fronteira · `C02` schema e envelope · `C03` trava com prova · `C04` evidência e
rastreabilidade · `C05` uso pela cadeia · `C06` limites declarados.

Definições íntegras em
[`../julgamento-nove-departamentos-2026-08-04/00-CONTRATO.md`](../julgamento-nove-departamentos-2026-08-04/00-CONTRATO.md).
**Todos os seis são remedidos** — nada é herdado de 2026-07-29.

Agregação: MENOR entre as duas instâncias, MENOR entre critérios, `NAO_DISCRIMINADO` quando qualquer
faixa cruza o corte 7 (`ADR-016`). Nota inteira, sem média nem compensação.

## Execução

Saída crua dos quatro em [`saida-crua/`](saida-crua/), com `00-RESUMO.json` e **inventário por
pacote**. **As lentes não executam.** Número que não existe ali vira `n/a` com motivo verificável.

O `departamento-negocios` sai com **3 FAIL** — um é a série de ADR (alheia) e dois são cascatas de
sub-execução do próprio validador dele, que executa outros validadores e ecoa a saída. Isso é fato do
pacote e entra na avaliação; a série de ADR **não**.

## Contexto proibido

- `../../REGISTRO-DE-VEREDITOS.md` e `../julgamento-pacotes-2026-07-29/08-RESUMO.md` — **contêm as
  notas de 2026-07-29 destes mesmos quatro pacotes**, que é exatamente o que se vai remedir.
- `../julgamento-nove-departamentos-2026-08-04/` e `../recoleta-c03-c05-c06-2026-08-05/` em todos os
  níveis, e os vereditos da T19/T27.
- **Proibida busca larga sobre `julgamento*`, `pareceres*`, `rejulgamento*`, `recoleta*` ou
  `REGISTRO-DE-VEREDITOS`.** Quatro juízes já se contaminaram por fragmentos de `grep`. Se topar com
  nota, **pare e declare**.

## Schema do parecer — estrito

```json
{"artifact_type":"JUDGE_OPINION","judge_id":"<id>","lens":"<lente ou painel-externo>",
 "instancia":1,"round":"nucleo-de-comando",
 "created_at":"<ISO-8601 com fuso>","commit_julgado":"<hash completo>","required_level":"INTERNO",
 "scores":[{"package_id":"ceo-maestro","criterion_id":"C01","score":7,
            "razao":"...","evidencia":["caminho:linha"]}],
 "minimo_dos_meus_criterios":7,
 "confidence":"alta|media|baixa","por_que_essa_confianca":"...",
 "o_que_declaro_contra_mim":["..."]}
```

Uma entrada por par (pacote, critério) que lhe cabe. Chave divergente volta para reemissão (uma vez).

## Regras

Nota **inteira** · `10` exige declarar que procurou o risco e não achou · evidência = caminho com
linha · `n/a` só com motivo verificável · **nunca comparar um pacote com outro** · o juiz não
conserta nada · o **FAIL da série de ADR não é defeito destes quatro** — desconte e diga que
descontou.

> **Ao juiz, e leia com atenção:** você foi despachado pelo `ceo-maestro`, e o `ceo-maestro` é um dos
> quatro que você vai julgar. Se isso o constrangeu de alguma forma — se você hesitou em dar nota
> baixa a quem o despachou —, **diga na seção contra si**. Um parecer que declara o constrangimento
> vale mais que um que finge não tê-lo sentido.
