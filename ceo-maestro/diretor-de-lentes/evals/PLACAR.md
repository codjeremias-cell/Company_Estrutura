# Placar de migração — Diretor de Lentes

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **50/50 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. A cadeia canônica hoje soma **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

Data: 2026-07-26  
Versão avaliada: 1.0.0  
Escopo: migração seletiva de `comite-de-lentes` para `ceo-maestro/diretor-de-lentes`

## Resultado

| Verificação | Resultado |
|---|---:|
| Baseline comportamental do pacote legado | 0 PASS, 2 PARCIAL, 3 FAIL |
| Forward comportamental da nova skill | 15/15 casos PASS |
| Critérios do forward | 62/62 assertions PASS |
| Validador determinístico do Diretor | 50/50 PASS |
| Regressão do contrato do CEO | 32/32 PASS |
| Total mecânico Diretor + CEO | 81/81 PASS |
| Auditoria independente do contrato | APROVADO TECNICAMENTE |

## Baseline do legado

Uma instância nova avaliou cinco cenários centrais contra a skill antiga, antes de usar
o contrato migrado:

| Cenário | Resultado |
|---|---|
| Missão técnica multidepartamental | PARCIAL |
| Negócios como relação matricial | FAIL |
| Juízes ausentes | FAIL |
| Corte 9,49 sem arredondamento | PARCIAL |
| Exceção somente pelo CEO | FAIL |

O baseline comprova que renomear a pasta sem reconstruir o contrato não seria
suficiente. As lacunas estavam na hierarquia, na relação matricial, no fail-closed,
no corte individual de 9,5 e na autoridade de exceção.

## Forward comportamental

Uma instância nova leu a skill e seus contratos e respondeu aos 15 prompts do
conjunto `evals.json`, sem editar o pacote. Todos os casos acionaram a skill e
aderiram integralmente ao contrato:

- 15/15 casos PASS;
- 62/62 assertions PASS;
- Juízes obrigatórios para todo retorno departamental;
- Auditoria preservada como evidência, nunca como substituta dos Juízes;
- `minimum_score` calculado sem média ou arredondamento;
- exceção recusada pelo Diretor e reservada ao fluxo CEO → Jeremias;
- comunicação com Negócios mantida como relação matricial;
- agentes nunca receberam missão direta do Diretor;
- ausência de capacidade gerou gap explícito e bloqueio delimitado;
- décima rodada não foi convertida em validação.

As respostas operacionais, os trechos verificáveis e a integridade do snapshot
estão em [FORWARD-TEST.md](FORWARD-TEST.md).

## Validação mecânica

O validador do Diretor verificou schemas, produtores, destinatários, correlação de
contrato/candidato/rodada/digest, a cadeia completa Departamento → Juízes, matriz
com Negócios, dez Departamentos operacionais exatos — incluindo Conteúdo e Marketing — e os
casos negativos.

O validador do CEO foi executado como regressão para garantir que:

- `CAPABILITY_GAP`, `EXCEPTION_REQUEST` e `EXECUTIVE_DECISION` continuam sendo
  produzidos pelo CEO;
- apenas Jeremias pode autorizar a exceção;
- o relatório dos Juízes continua produzido pelos Juízes.

## Histórico da auditoria

A primeira auditoria reprovou a prontidão por falta de evidência comportamental e
por contratos mecânicos insuficientes para produtores, correlação, gate
departamental e troca matricial. Foram adicionados:

- produtor causal exato em cada envelope;
- correlação obrigatória de contrato, candidato, rodada e digest;
- `DEPARTMENT_GATE_RECORD` com missão, retorno, pedido e parecer completos;
- `MATRIX_EXCHANGE_MESSAGE` validado nos dois sentidos;
- testes negativos para tentativas de bypass;
- este placar e a evidência do forward comportamental.

Após as correções, a reaudição declarou o contrato tecnicamente aprovado. A
prontidão final depende ainda da presença física dos filhos canônicos; enquanto
eles não forem migrados, o Diretor falha fechado com `DIRECTOR_CAPABILITY_GAP` e
`BLOCKED_RETURN`, sem recorrer silenciosamente ao legado.
