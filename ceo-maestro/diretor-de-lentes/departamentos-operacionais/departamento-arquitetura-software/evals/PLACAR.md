# Placar de migração — Departamento de Arquitetura de Software

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 82/82 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:248749b384ee4edd23688874828d7ccb5d4ec254eb3cc3373cce7ff18530fe51` | medido-em: 2026-09-02
<!-- /SELO-DE-CONTAGEM -->

## Passagem pelo gate

Este pacote foi submetido ao gate em 2026-07-29. Opiniões, notas, veredito e
histórico vivem fora do candidato, no
[resultado consolidado](../../../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md),
para não contaminar uma rodada futura com o próprio julgamento.

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **72/72 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. Naquela medição, a cadeia canônica somava **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

Data: 2026-07-26
Versão avaliada: 1.0.0
Escopo: migração de `SKILL - Nova formula/maestro/comite-de-lentes/lente-arquiteto-software` para
`.../departamentos-operacionais/departamento-arquitetura-software`

## Resultado

| Verificação | Resultado | Executado? |
|---|---:|---|
| Validador determinístico da Arquitetura | 72/72 PASS | **sim** |
| Regressões (Diretor, CEO, Juízes, Auditoria, Evolução, Negócios, motor) | inalteradas | **sim** |
| Forward comportamental (16 casos) | **16/16 casos · 60/65 asserções · 0 contorno** | **sim** — [FORWARD-TEST.md](FORWARD-TEST.md) |
| Baseline do pacote legado | — | **NÃO — pendente** |
| Gate dos Juízes sobre esta entrega | — | **NÃO — pendente** |

```bash
python evals/validate_workflow.py
```

## O que muda em relação ao legado

Três recortes, todos no [ADR-006](../references/adr-006-arquitetura-sem-julgamento-e-com-seis-agentes.md):

1. **O modo `JULGAR` não migrou.** Sai a rubrica ponderada 0–10, o corte 9,5, os vetos e todo o
   aparato de independência (`responsibility_ledger`, `PRODUCER_IDS`, `BLOQUEADO_AUTOJULGAMENTO`).
   Julgar é do `departamento-juizes`; dois julgadores seriam duas notas concorrentes.
2. **As oito dimensões viraram cobertura, não nota.** Continuam dizendo o que a entrega precisa
   conter; deixaram de dizer quanto ela vale.
3. **Seis agentes, não três.** O legado descrevia sete papéis e não materializava nenhum. O sétimo
   era o juiz, que saiu. Os três nomes do organograma fundiam pares que o próprio legado separa —
   modularidade × integração, e alternativas × ADR — e foram substituídos.

## O que o validador prova

**Pacote e vínculos (9 casos).** Arquivos obrigatórios; `agentes/` com exatamente os seis nomes;
posição sob `departamentos-operacionais/` conferida em runtime; frontmatter, limites e
`short_description` de 25–64 nos sete pacotes; fonte normativa no caminho relativo de cada nível;
todos os links markdown resolvendo; `workerId` e as oito dimensões batendo com as referências.

**As duas travas do ADR-006, mecânicas (2 casos).** O validador percorre o schema inteiro e falha
se encontrar:

- **campo de julgamento** — `score`, `nota`, `veredito`, `rubrica`, `peso`, `corte`, `aprovado`;
- **campo de outra lente** — `entidade`, `tabela`, `coluna`, `indice`, `migracao`, `ddl`,
  `normalizacao`, `particionamento`, `grao`, `sharding`, `banco`; ou `codigo`, `patch`, `diff`,
  `query`, `sql`, `implementacao`.

É a fronteira que Jeremias marcou, deixando de depender de disciplina e passando a depender de
contrato: **não há onde escrever um schema aqui**.

**Contrato do Diretor (1 caso).** Confirma que ele reconhece este Departamento e os dois vizinhos
como operacionais, que a missão retorna ao Diretor, e que pontuar continua sendo dos Juízes.

**Artefatos aceitos (12).** Plano, duas tarefas, os seis retornos (um por ótica), conjunto de
opções, lacuna e livro-razão.

**Casos negativos — tarefa (5).** Ótica trocada para o `kind`; `scope_out` vazio; ADR/C4 rodando
antes da onda 4; `forbidden_context` sem a proibição de conclusão esperada; retorno fora da gerente.

**Casos negativos — retorno (10).** Alternativas com uma opção só; opção sem o que **perde**;
contrato só com caminho feliz; módulo sem dono de dado; driver sem `como_se_mede`; ADR marcado como
aceito; ADR sem alternativa descartada com motivo; `BLOCKED` com e sem motivo.

**Casos negativos — fronteira (3).** Spike delegado sem regra de decisão; dependência delegada aos
Juízes (alvo inválido); dependência de dados sem a restrição arquitetural junto.

**Casos negativos — conjunto de opções (4).** Opção única com justificativa verificável (aceita) e
sem (rejeitada); justificativa pendurada em conjunto de duas; recomendação sem perda declarada.

**Casos negativos — livro-razão (8).** Sete dimensões em vez de oito; entrega com dimensão
`AUSENTE`; `NAO_APLICAVEL` genérico; lacuna aberta; sem registro de emissão (R6); sem conjunto de
opções; gate de fronteira vermelho; produtor forjado.

**Fronteira com o consumidor (2).** O livro-razão vira `DEPARTMENT_RETURN` e é validado **contra o
schema do Diretor**; produtor forjado é rejeitado lá.

**Regras recalculadas em código (17).** Sem consultar campo declarado: 2–3 opções formam conjunto e
4 não; opção única exige justificativa longa; recomendação sem perda é inválida; spike exige regra
de decisão e dependência de dados não; dimensão `AUSENTE`, gate de fronteira vermelho ou lacuna
aberta impedem a entrega; os dois acúmulos proibidos são detectados e o permitido não; o
`test_summary` é `0/0/0`; e as seis óticas cobrem exatamente as seis primeiras dimensões.

## O que ainda não foi provado

### Estado vigente das obrigações — conferido em 2026-08-08

> **Duas obrigações desta seção estavam declaradas como pendentes e não estão.** A campanha [`remedicao-dos-sete-2026-08-03`](../../../../evals/remedicao-dos-sete-2026-08-03/PLACAR.md) executou as duas sobre este pacote. O texto dos itens abaixo é registro da rodada em que foi escrito e fica como está; o estado corrente é este.

| obrigação | estado em 2026-08-08 | quem emitiu |
|---|---|---|
| Auditoria independente | **EXECUTADA** em 2026-08-03 · `governance_report` **NONCOMPLIANT** · **3 achados** nomeados, com dono e condição de correção | `departamento-auditoria-responsabilidades` |
| Parecer dos Juízes | **EMITIDO** em 2026-08-03 · veredito **REPROVED** · `minimum_score` **6**, faixa **6–8** · **1 de 8** critérios `NAO_DISCRIMINADO` | `departamento-juizes` |

> **A faixa atravessa o corte, e isso é o achado — não um detalhe.** Duas instâncias da mesma lente, sobre os mesmos bytes e com a mesma rubrica, divergiram em 54% dos pares na campanha. Onde a faixa cruza o 6/7, consertar "até passar" seria mirar num número que a régua não distingue. O aceite interno deste pacote **nunca esteve estabelecido**, e continua não estando.

### Dono e condição de fechamento, item a item

> Exigido pelos achados `CA-01` e `GR-01`/`GR-02` da mesma campanha: pendência declarada sem dono é pendência de ninguém. "O próprio Departamento" significa o pacote que este placar mede — ele responde pela própria evidência.

| item | dono | fecha quando |
|---:|---|---|
| 1 | — | já fechado no próprio texto, com data |
| 2 | o próprio Departamento | a lente legada for avaliada nos mesmos cenários com instrumento comum, ou este item registrar a decisão de não comparar, com o motivo e o dono da decisão |
| 3 | `departamento-juizes` | um veredito novo dos Juízes suceder o de 2026-08-03. Ver o estado vigente acima |
| 4 | — | já fechado no próprio texto, com data |
| 5 | o próprio Departamento | houver âncora externa ao pacote que prove a emissão — runtime separado, assinatura fora da árvore ou terceiro que não compartilhe o processo. Depende das tarefas 50 e 57; nenhuma trava de dentro fecha isto |


`SKIP` declarado com motivo:

1. **Forward comportamental — EXECUTADO; esta seção estava vencida.** Corrigido em 2026-07-26: o
   texto anterior dizia "os 16 prompts não foram executados", mas o
   [FORWARD-TEST.md](FORWARD-TEST.md) registra **16/16 casos e 60/65 asserções PASS**, e a tabela
   mecânica desta mesma página já declarava a execução. A seção criada para não esconder ausência de
   prova estava negando prova existente — o erro simétrico ao que produziu a rodada 2 do
   `departamento-inovacao-melhoria`, e igualmente corrosivo para a confiança nesta seção.

   *Correção de 2026-07-27, segunda passada:* a primeira redação desta linha dizia que as 5
   asserções falhadas "não estavam inventariadas em lugar nenhum". **Estavam** — o
   [FORWARD-TEST.md](FORWARD-TEST.md) tem a seção "As cinco asserções que não fecharam", com caso
   de origem e classificação. O erro foi meu, ao corrigir a contradição anterior sem reler o
   forward.

   O que **de fato** continua aberto, já classificado no forward: **4 das 5 são defeito do
   catálogo** (casos 1, 10, 11 e 15 pedem "fixa a restrição arquitetural", mas os prompts são
   pedidos crus, sem missão e sem os nove drivers — a restrição não existe para ser fixada, e as
   instâncias marcaram `PENDING` em vez de inventar, que é o que o caso 2 do mesmo catálogo exige
   delas). **Uma é lacuna real de cobertura**: o caso 7 (*"a trava vale mesmo vindo de Jeremias"*)
   não foi tratado pela instância, embora o caso 8 do mesmo pacote tenha tratado.

   Ação, portanto, não é "nomear": é **consertar o instrumento** (ver o achado sistêmico no
   `PLANO-DE-ACAO-2026-07-27.md`, frente 2) e cobrir a lacuna do caso 7. O acionamento espontâneo
   segue sem medição — os prompts rodaram sob carga explícita. E **este pacote tem uma fronteira
   nova**, com dois Departamentos que não existiam na data desta página (ver item 4).
2. **Baseline do legado.** A `lente-arquiteto-software` não foi avaliada nos mesmos cenários. O que
   está provado por leitura é que ela tem um modo julgador que o organograma não comporta.
3. **Gate dos Juízes.** Esta entrega não passou pelo gate — e, ao contrário dos pacotes anteriores,
   agora há um `departamento-juizes` migrado que poderia julgá-la.
4. ~~**Os dois vizinhos não existem.**~~ **VENCIDO em 2026-07-26.** Era verdade quando esta página foi
   escrita: `departamento-arquitetura-dados` e `departamento-desenvolvimento` não existiam, e toda
   `delegated_dependency` apontava para capacidade ausente. Os dois foram materializados no mesmo dia,
   por frentes próprias, e agora têm destinatário real no caminho canônico. O que **continua** não
   provado é o handoff em execução: nenhuma `delegated_dependency` foi emitida, recebida e honrada
   ponta a ponta.
5. **R6.** Um livro-razão coerente é reproduzível sem nenhuma `ARCHITECTURE_TASK` emitida. A
   condição de registro de emissão encarece a fabricação; não a impede.

## Achado de processo

O verificador de links pegou **três** links quebrados no ADR-006, todos por profundidade de
caminho — o **mesmo erro** que eu já tinha cometido no ADR-003 e que a armadilha nº 1 do
`GUIA-DE-EXPANSAO-E-MIGRACAO.md` descreve.

A armadilha estar documentada não impediu a repetição. O que impediu o erro de sair foi o **teste**,
não o aviso. Vale como evidência a favor de manter o `validate_links` obrigatório em todo pacote — e
como sinal de que aviso em guia não substitui verificação automática.
