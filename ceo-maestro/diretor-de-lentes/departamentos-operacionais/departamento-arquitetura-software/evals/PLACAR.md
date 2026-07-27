# Placar de migração — Departamento de Arquitetura de Software

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **72/72 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. A cadeia canônica hoje soma **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../../../ORGANOGRAMA.md).
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

`SKIP` declarado com motivo:

1. **Forward comportamental — EXECUTADO; esta seção estava vencida.** Corrigido em 2026-07-26: o
   texto anterior dizia "os 16 prompts não foram executados", mas o
   [FORWARD-TEST.md](FORWARD-TEST.md) registra **16/16 casos e 60/65 asserções PASS**, e a tabela
   mecânica desta mesma página já declarava a execução. A seção criada para não esconder ausência de
   prova estava negando prova existente — o erro simétrico ao que produziu a rodada 2 do
   `departamento-inovacao-melhoria`, e igualmente corrosivo para a confiança nesta seção.

   O que **de fato** continua aberto: **5 asserções falharam** (60 de 65) e não estavam inventariadas
   em lugar nenhum — precisam ser nomeadas uma a uma, com o caso de origem, antes de este item
   fechar. O acionamento espontâneo segue sem medição (os prompts rodaram sob carga explícita). E
   **este pacote tem uma fronteira nova**, com dois Departamentos que não existiam na data desta
   página (ver item 4: os dois passaram a existir em 2026-07-26).
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
