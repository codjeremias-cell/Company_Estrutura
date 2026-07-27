# ADR-006 — Arquitetura produz e não julga; seis agentes; fronteira dura com dados e código

- **Data:** 2026-07-26
- **Status:** aceito por decisão de Jeremias
- **Decisores:** Jeremias
- **Contexto normativo:** [ADR-001 hierarquia](../../../../references/adr-001-hierarquia-executiva.md) ·
  [ADR-002 Juízes](../../../departamento-juizes/references/adr-002-nota-absoluta-e-modo-duplo.md) ·
  [ADR-003 Auditoria](../../departamento-auditoria-responsabilidades/references/adr-003-conformidade-sem-nota.md)

## Contexto

A `lente-arquiteto-software` legada é a mais elaborada do pacote antigo. Ela opera em **dois modos
mutuamente exclusivos** — `GERENCIAR` (produz arquitetura por um time) e `JULGAR` (dá nota absoluta
0–10 a arquitetura alheia, com rubrica ponderada, vetos e corte 9,5) — e carrega um aparato pesado
de independência (`responsibility_ledger`, `PRODUCER_IDS`, `JUDGE_EXCLUSION`,
`BLOQUEADO_AUTOJULGAMENTO`) só para impedir que o mesmo agente julgue o que produziu.

Ela também **não tem agentes materializados**: o time existe apenas como um *modelo de papéis* em
`references/modelo-operacional-do-time.md`, com sete funções descritas e nenhuma implementada.

E Jeremias marcou uma fronteira explícita ao pedir a migração: a casa trabalha com **três lentes
vizinhas** — arquiteto de software, arquiteto de dados e desenvolvedor —, e este Departamento não
pode escorregar para as outras duas.

## Decisão

**1. O modo `JULGAR` não migra.** Julgar é do `departamento-juizes` (ADR-002), que já faz isso
melhor: cego, com três óticas independentes, fronteira de Pareto no modo disputa e trava
anti-bypass. Manter um segundo julgador com rubrica própria criaria **duas notas concorrentes** sobre
o mesmo artefato — o mesmo erro que o ADR-003 corrigiu na Auditoria.

Sai junto todo o aparato que existia só para sustentar o julgamento: rubrica ponderada, vetos, corte
9,5, `responsibility_ledger`, `PRODUCER_IDS`, `JUDGE_EXCLUSION`, `NÃO_JULGÁVEL` e
`BLOQUEADO_AUTOJULGAMENTO`. Este Departamento **produz**; quem pontua é outro.

**2. As oito dimensões da rubrica migram — como cobertura, não como nota.** Elas descrevem o que uma
entrega arquitetural precisa **cobrir**, e isso continua valioso. O que sai são os **pesos**, a
**escala 0–10** e o **corte**. Viram [dimensoes-da-entrega.md](dimensoes-da-entrega.md): checklist de
completude do próprio Departamento e insumo para o Diretor compor `applicable_criteria` quando
mandar a entrega aos Juízes. Mesma operação que o ADR-003 fez com as dez dimensões da Auditoria.

**3. Seis agentes, derivados do modelo de papéis legado.** O legado descrevia sete papéis; o sétimo
era "juiz independente", que sai com a decisão 1. Os seis restantes viram agentes reais:

| Agente | Papel legado | Responde |
|---|---|---|
| `agente-drivers-e-restricoes` | drivers | o que o sistema precisa satisfazer, medível |
| `agente-modularidade-e-limites` | domínio e modularidade | onde ficam as fronteiras e quem é **dono** de cada dado |
| `agente-integracoes-e-contratos` | integração e contratos | como as partes conversam e falham |
| `agente-qualidade-e-operacao` | qualidade e operação | como os não funcionais viram cenário medível |
| `agente-alternativas-e-tradeoffs` | alternativas | quais caminhos distintos existem e o que se perde em cada |
| `agente-adr-e-c4` | integrador documental | o que fica registrado, com autoria e divergência preservadas |

**Não são três.** O organograma listava `agente-c4-e-contexto`, `agente-adr-e-tradeoffs` e
`agente-modularidade-e-integracoes` — nomes propostos antes de a fonte legada ser lida. Eles
fundiam pares que o próprio legado separa por boa razão: **modularidade** (fronteiras internas) e
**integração** (contratos entre partes) são perguntas diferentes, e **alternativas** (gerar opções)
e **ADR** (registrar a decisão) têm conflito de interesse quando na mesma mão. O organograma é
atualizado por este ADR.

**4. A fronteira com dados e código é dura, e mecânica.** Regra em uma frase:

> **Quem é dono do dado e como as partes o trocam é arquitetura. Como o dado é modelado e evoluído é
> do Departamento de Arquitetura de Dados. Como qualquer coisa é implementada é do Departamento de
> Desenvolvimento.**

Duas consequências operacionais, ambas obrigatórias:

- **Opção que depende de escolha de banco, modelo, migração, índice ou particionamento sai com
  dependência declarada** para `departamento-arquitetura-dados`. A opção **não fecha aqui**.
- **Opção que depende de spike ou benchmark sai com o spike DESENHADO e a execução delegada** ao
  `departamento-desenvolvimento`. Desenhar o experimento é arquitetura; rodá-lo não é.

O schema do Departamento **não tem** campo para entidade, tabela, índice, migração, DDL, query,
código, patch ou diff — e o validador falha se algum aparecer. A fronteira deixa de depender de
disciplina e passa a depender de contrato.

**5. Opção única exige justificativa verificável.** Regra herdada e mantida: toda recomendação sai
com **2–3 opções realmente distintas**, ou com uma única acompanhada da prova de que as demais foram
eliminadas por restrição real. "Só existe um caminho" sem prova é preferência, não arquitetura.

**6. ADR aceito é contrato vinculante.** Herdado e mantido, agora ancorado na RI-01: proposta que
conflita com ADR aceito **para a parte afetada** e escala ao Diretor. Sem pedido formal de revisão,
divergir é violação; com pedido pendente, a frente fica bloqueada até decisão de Jeremias.

**7. O Departamento não executa nada.** Nem teste, nem benchmark, nem spike, nem prova operacional.
O `test_summary` do seu `DEPARTMENT_RETURN` é sempre `0/0/0` — mesma regra da Auditoria (ADR-003,
decisão 7): prova executada por terceiro entra como evidência, nunca como contagem própria.

## Consequências

- o organograma muda: três agentes propostos viram seis, com nomes novos;
- a estrutura passa a ter **um único** julgador de qualidade, e a arquitetura entra na fila do gate
  como qualquer outra entrega;
- o aparato de independência do legado fica obsoleto **aqui**, mas seu princípio sobrevive intacto
  no `departamento-juizes`, que nasceu com ele;
- a fronteira com dados e código vira caso de teste, não recomendação;
- as oito dimensões dão ao Diretor um vocabulário pronto para compor critérios aplicáveis quando a
  entrega arquitetural for julgada.

## Alternativas consideradas

- **Migrar os dois modos.** Descartada: criaria um segundo julgador com rubrica e corte próprios,
  concorrendo com os Juízes sobre o mesmo artefato. É exatamente a ambiguidade que o ADR-002 e o
  ADR-003 fecharam.
- **Manter os três agentes do organograma.** Descartada: fundem pares que o legado separa. Juntar
  *gerar alternativas* e *registrar a decisão* na mesma mão faz o autor da opção documentar a
  própria escolha, e o registro deixa de preservar divergência.
- **Um agente por dimensão da rubrica (oito).** Descartada: as dimensões são eixos de **avaliação**,
  não de **produção**. "Rastreabilidade" e "simplicidade" são propriedades da entrega inteira, não
  trabalho de alguém.
- **Deixar a fronteira com dados e código só no texto.** Descartada: é a restrição que Jeremias
  nomeou explicitamente, e texto não segura escorregão. Virou ausência de campo no schema e caso
  negativo no validador.
- **Deixar este Departamento escolher o banco quando a opção depender disso.** Descartada: contraria
  a fronteira canônica das três lentes, em que escolha de banco e persistência poliglota são do
  arquiteto de dados. A arquitetura nomeia a **consequência**; a escolha é delegada.
