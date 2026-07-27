# ADR-008 — Dados nasce sem legado, com seis agentes e dois gates checáveis

- **Data:** 2026-07-26
- **Status:** aceito por decisão de Jeremias
- **Decisores:** Jeremias
- **Contexto normativo:** [ADR-001 hierarquia](../../../../references/adr-001-hierarquia-executiva.md) ·
  [ADR-002 Juízes](../../../departamento-juizes/references/adr-002-nota-absoluta-e-modo-duplo.md) ·
  [ADR-006 Arquitetura](../../departamento-arquitetura-software/references/adr-006-arquitetura-sem-julgamento-e-com-seis-agentes.md)

## Contexto

O `ORGANOGRAMA.md` registra este Departamento no mapeamento como **"inexistente →
`departamento-arquitetura-dados`"**, e a verificação confirmou: **não há `lente-arquiteto-dados` no
pacote legado**. Este Departamento não é migração — é skill nova, como foi o
`departamento-evolucao-skills`.

A fonte é a lente canônica `Catalogo-Skills-Unificado/skills/arquiteto-dados/`, que já é madura:
tem domínio dividido em seis áreas, um piso explícito para começar a modelar e um **fechamento
checável (RI-04)** com três itens.

E há um contexto novo que não existia nas migrações anteriores: o
`departamento-arquitetura-software` foi migrado horas antes e **já produz `delegated_dependency`
apontando para cá**, carregando uma `architectural_constraint`. Este Departamento nasce com um
consumidor esperando por ele e com uma restrição para respeitar.

## Decisão

**1. Skill nova, fundamentada na canônica.** Não há recorte de legado a prestar contas — há
fundamentação. O que entra vem de `arquiteto-dados`: postura, domínio, ordem de operação, bordas
com dono e o fechamento checável. O que muda é a forma: lente vira Departamento com gerente e
agentes, sob o `diretor-de-lentes`.

**2. Seis agentes, um por decisão de dados que tem dono distinto.**

| Agente | Responde |
|---|---|
| `agente-perguntas-e-volumetria` | quais perguntas o dado responde, em que volume e latência, OLTP ou OLAP |
| `agente-escolha-de-persistencia` | qual banco, por qual evidência, e onde a persistência poliglota tem fronteira |
| `agente-modelo-e-grao` | entidades, chaves, normalização e **o grão** — o que uma linha representa |
| `agente-evolucao-e-migracao` | como o schema evolui sem downtime, com expand/contract e rollback |
| `agente-escala-e-acesso` | índices por padrão de acesso real, particionamento, replicação, CAP/PACELC |
| `agente-contratos-e-integridade` | contrato de dados entre produtor e consumidor, CDC/outbox, transação e linhagem |

**3. Duas separações por conflito de interesse**, no mesmo espírito da Arquitetura:

- quem faz `ESCOLHA_PERSISTENCIA` **não** faz `MODELO_GRAO` na mesma frente — quem escolhe o motor
  tende a modelar de um jeito que justifica a escolha, e a contraprova morre;
- quem faz `MODELO_GRAO` **não** faz `EVOLUCAO_MIGRACAO` na mesma frente — quem desenhou o modelo
  subestima o custo de migrar para longe dele.

**4. Dois gates mecânicos, herdados da canônica e agora verificáveis.**

- **Piso de entrada:** modelar exige **≥ 3 perguntas do negócio** respondidas pelo dado **e**
  volumetria em ordem de grandeza. Sem isso, a frente não abre e a lacuna volta ao Diretor —
  modelar sem pergunta é modelagem por reflexo.
- **Fechamento checável (RI-04):** a entrega fecha com **grão declarado** ✓, **plano expand/contract
  com rollback** ✓ e **índice/partição justificado por padrão de acesso** ✓. **Faltou um =
  incompleta.** Os três viram campo obrigatório no schema e caso negativo no validador.

**5. A fronteira com Arquitetura é recíproca e a restrição dela é vinculante.** O ADR-006 fixou:
*quem é dono do dado e como as partes o trocam é arquitetura; como o dado é modelado e evoluído é
daqui*. Este Departamento **respeita a `architectural_constraint`** que vem na dependência
delegada: se o ownership diz que ninguém lê a base do dono direto, nenhum modelo daqui pode propor
leitura direta. Restrição arquitetural que inviabiliza o modelo **escala ao Diretor** — não se
contorna e não se ignora.

**6. Este Departamento não implementa, não julga e não endurece segurança.** Ler o plano de query
para justificar um índice é daqui; **tuning de uma query específica e o código do DAO** são do
`departamento-desenvolvimento`. Declarar que um campo é PII, com necessidade de retenção e
mascaramento, é daqui; **modelar ameaça e endurecer o controle** é do `departamento-seguranca`.
Pontuar é do `departamento-juizes`.

**7. Nunca migração destrutiva sem plano de reversão.** Herdado da canônica como salvaguarda dura:
em produção, expand/contract; `ALTER` destrutivo direto não é entregável, é incidente.

## Consequências

- o consumidor já existe: as dependências que a Arquitetura emitiu passam a ter destinatário real;
- os dois gates deixam de ser conselho e viram rejeição de schema;
- o `departamento-desenvolvimento` e o `departamento-seguranca` ganham mais um emissor de
  dependências apontando para eles — ambos ainda ausentes;
- a fronteira das três lentes irmãs fica coberta dos dois lados: Arquitetura declara o que não é
  dela, e Dados declara o recíproco.

## Alternativas consideradas

- **Fundir dados dentro do `departamento-arquitetura-software`.** Descartada: contraria a fronteira
  canônica das três lentes, o organograma, e concentraria em um Departamento duas decisões que a
  casa separa desde sempre — a estrutura macro e o modelo do dado.
- **Três agentes, como o organograma propunha para os outros.** Descartada: a canônica divide o
  domínio em seis áreas com riscos muito diferentes. Fundir *evolução de schema* com *modelagem*
  apaga justamente a separação que impede o modelador a subestimar a migração.
- **Deixar o fechamento RI-04 como checklist em prosa.** Descartada: os três itens são objetivos e
  a canônica já diz "faltou um = incompleta". Vira campo obrigatório.
- **Permitir que este Departamento sobreponha a restrição arquitetural quando o modelo pedir.**
  Descartada: seria o mesmo escorregão que o ADR-006 impede do outro lado. Conflito escala ao
  Diretor, que roteia entre os dois.
