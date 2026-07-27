# Fronteiras — o que é arquitetura, o que é dados, o que é código

Fonte única do escopo deste Departamento. Ler antes de abrir frente, e sempre que um agente sentir
vontade de resolver um problema que não é dele.

## A régua, em uma frase

> **Quem é dono do dado e como as partes o trocam é arquitetura.
> Como o dado é modelado e evoluído é do `departamento-arquitetura-dados`.
> Como qualquer coisa é implementada é do `departamento-desenvolvimento`.**

As três lentes canônicas dizem a mesma coisa, cada uma do seu lado: a estrutura macro não-dados é
desta; o modelo e a evolução do dado é de dados; a implementação e o microdesign é de
desenvolvimento. Esta referência só torna a régua operável.

## Tabela de corte

| Pergunta | De quem | Por quê |
|---|---|---|
| Que módulos existem e onde ficam as fronteiras? | **arquitetura** | limites são estrutura |
| Qual módulo é **dono** de qual capacidade e dos dados dela? | **arquitetura** | ownership é decisão de fronteira |
| Quais entidades existem, com que atributos e relacionamentos? | **dados** | é o modelo |
| Normalizar ou desnormalizar? Qual grão? | **dados** | é o modelo |
| Que banco usar? Persistência poliglota? | **dados** | é escolha de tecnologia de dados |
| Como migrar o schema sem downtime? | **dados** | é evolução do dado |
| Que índice criar? Como está o plano de query? | **dados** (modelo) / **desenvolvimento** (tuning) | nunca arquitetura |
| Os serviços conversam por API síncrona ou por evento? | **arquitetura** | é topologia de integração |
| Qual o contrato da API/evento: campos, versionamento, idempotência? | **arquitetura** | é contrato entre partes |
| Como o contrato é implementado no código? | **desenvolvimento** | é implementação |
| Como o DAO/repositório acessa o banco? | **desenvolvimento** | é implementação |
| Que padrão GoF usar nesta classe? | **desenvolvimento** | é microdesign |
| Que atributos de qualidade importam e em que cenário medível? | **arquitetura** | é NFR virando driver |
| O sistema atende ao SLO? | **testador** | é prova executada |
| Monolito modular ou microsserviços? | **arquitetura** | é estilo estrutural |
| Vale a pena este spike? Como ele seria montado? | **arquitetura** desenha | experimento é decisão estrutural |
| Rodar o spike e reportar o número | **desenvolvimento** executa | execução não é arquitetura |
| Onde ficam as fronteiras de confiança? | **arquitetura** aponta · **segurança** modela ameaça | limite é estrutura, ameaça é especialidade |

## As duas regras de saída obrigatória

Quando a frente esbarra na fronteira, o trabalho **não para e não invade**: sai com dependência
declarada. Sem isso, a entrega está incompleta.

**Regra D — dependência de dados.** Toda opção, módulo ou contrato cuja viabilidade dependa de
escolha de banco, modelo de dados, migração, índice, particionamento ou grão sai com:

```yaml
delegated_dependency:
  target: "departamento-arquitetura-dados"
  question: "<a pergunta de dados, literal>"
  blocks: "<a opção/decisão que não fecha sem a resposta>"
  architectural_constraint: "<o que a arquitetura JÁ fixou e que a resposta precisa respeitar>"
  decision_rule: "<qual resposta leva a qual decisão arquitetural>"
```

A arquitetura **fixa a restrição** (ex.: "este contexto é dono destes dados e não expõe leitura
direta a outro"), e a resposta de modelagem tem de caber nela. O que a arquitetura **não** faz é
responder a pergunta.

**Regra S — dependência de spike.** Toda opção cuja escolha dependa de um número que ninguém tem sai
com o experimento **desenhado** e a execução delegada:

```yaml
delegated_dependency:
  target: "departamento-desenvolvimento"
  question: "<o que o spike precisa medir — montagem, entradas, o que decide>"
  blocks: "<a opção que não fecha sem o número>"
  architectural_constraint: "<o que a arquitetura JÁ fixou e o spike precisa respeitar>"
  decision_rule: "<qual resultado escolhe qual opção>"
```

Desenhar o experimento é arquitetura — é ela que sabe qual número decide o quê. Rodá-lo não é.
Spike sem `decision_rule` é curiosidade cara: se nenhum resultado muda a escolha, o spike não é
necessário.

## Red flags — PARE

Frases que o próprio agente reconhece em si quando já saiu do escopo:

- "aproveitando, já deixo o schema esboçado"
- "a tabela ficaria mais ou menos assim"
- "só um índice em `cliente_id` resolve"
- "escrevi um exemplo de como ficaria o repositório"
- "usa Postgres" — sem que a missão já traga a decisão de banco como restrição dada
- "esse `for` aninhado vai ficar lento" — micro-otimização é microdesign
- "rodei um teste rápido para confirmar"

Nenhuma delas é proibida por ser errada — várias podem estar certas. São proibidas porque **fecham,
sem autoridade, uma decisão de outro dono**, e depois a outra lente herda uma escolha que não fez.

## O caso que confunde: "donos de dados"

A dimensão `integração, contratos e donos de dados` é arquitetural, e isso costuma soar como
modelagem. Não é. O corte:

| Arquitetura decide | Dados decide |
|---|---|
| o contexto `Cobrança` é dono de faturas | quais campos uma fatura tem |
| ninguém lê a base de `Cobrança` direto; só pelo contrato | se fatura e item ficam em uma ou duas tabelas |
| a leitura de faturas por `Relatórios` é assíncrona, por evento | como o dado de relatório é modelado dimensionalmente |
| o dado replicado tolera atraso de até 5 min | como a replicação é feita e versionada |

A arquitetura escreve a **restrição** e o **contrato**; dados escreve a **forma**.

## Quando a fronteira estiver genuinamente ambígua

Não resolver por conta própria e não paralisar a frente inteira. Registrar como
`ARCHITECTURE_CAPABILITY_GAP` com a pergunta literal, marcar a decisão dependente como `PENDING` com
dono, seguir no trecho reversível e devolver ao `diretor-de-lentes` — quem roteia entre Departamentos
é ele. Chutar a resposta da lente vizinha é pior que declarar a dúvida.

**Concluído quando:** nenhuma entrega deste Departamento contém entidade, schema, índice, migração,
query, código ou patch; toda dependência de dados ou de spike saiu declarada com alvo, pergunta e —
no spike — regra de decisão.
