# Origem e fundamentação

Este Departamento **não é migração**: não existe `lente-arquiteto-dados` no pacote legado
`SKILL - Nova formula/maestro/comite-de-lentes/`. O `ORGANOGRAMA.md` já o registrava como
`inexistente → departamento-arquitetura-dados`. Como não há recorte a prestar contas, o que se
presta é **fundamentação**: de onde veio cada decisão.

## Fontes consultadas — estado em 2026-07-26

| Fonte | SHA-256 (16) |
|---|---|
| `Catalogo-Skills-Unificado/skills/arquiteto-dados/SKILL.md` | `df101721b5488c97` |
| `Catalogo-Skills-Unificado/skills/arquiteto-dados/agents/openai.yaml` | `49651895fee8a6d2` |
| `Catalogo-Skills-Unificado/REGRAS-DE-OURO.md` | `06341db894ef2ccc` |
| `Aprendizagem/Gradup.md` | `c12da65013adb13e` |
| `Aprendizagem/Melhorias e Aprendizados.md` | `95c1fab4983fc20a` |
| `Aprendizagem/EscalaOper.md` | `54e264537de239a2` |

As fontes permanecem intactas. Nada foi movido, editado ou removido delas.

## O que veio de onde

**Da lente canônica `arquiteto-dados`** — a substância técnica: a postura (*modelagem a serviço das
perguntas*; *o grão é sagrado*; *schema evolui, nunca recomeça*; *normalize até doer, desnormalize
até funcionar*); as seis áreas de domínio, que viraram os seis agentes; a ordem de operação em seis
passos, que virou as ondas; o **piso** de ≥ 3 perguntas mais volumetria; e o **fechamento checável
RI-04** com os três itens, que aqui deixou de ser checklist em prosa e virou campo obrigatório de
schema com caso negativo no validador.

**Das Regras de Ouro** — RO-04 e RO-10 (acesso parametrizado, JDBC seguro), RO-SB2 (Flyway dono do
schema, `ddl-auto=validate`, engine único dev = prod), RO-SB3 (transação em operação multi-passo),
RO-W2 (RLS como fronteira de segurança) e RO-DT3 (migração versionada em SQLite local, com o *down*
manual). Entraram como **L2, L3, L6 e L7** em
[gates-e-licoes-de-producao.md](gates-e-licoes-de-producao.md).

**Da pasta `Aprendizagem/`** — o material que nenhum manual traz, porque é cicatriz: a migração
Flyway editada que produziu **97 erros em cascata** por *checksum mismatch* (**L1**); o
`catch` de `DataIntegrityViolationException` que precisa ficar fora da `@Transactional`, e o
`clearAutomatically` no `UPDATE` em massa (**L4**); o efeito colateral disparado só em
`AFTER_COMMIT` (**L5**); e a atomicidade do lote de férias com os `ResultSet` padronizados (**L3**,
**L6**). São regras com custo conhecido, não boas práticas genéricas.

**Do `ADR-006`, do Departamento de Arquitetura de Software** — a metade recíproca da fronteira. A
navalha de [fronteiras-do-departamento.md](fronteiras-do-departamento.md) foi escrita para encaixar
exatamente na que já estava aceita do outro lado, e a `architectural_constraint` que a Arquitetura
emite passa a ter aqui um destinatário que a respeita.

## O que deliberadamente **não** entrou

- **Nota, rubrica e veredito.** A lente canônica orienta qualidade; pontuar é do
  `departamento-juizes` (ADR-002). O validador reprova qualquer campo de nota no schema.
- **Código.** A canônica cita ferramentas (Flyway, Liquibase, Atlas) e padrões de implementação;
  aqui elas aparecem como *restrição anexada à dependência*, nunca como artefato produzido.
- **Endurecimento de segurança.** Classificar PII e exigir RLS é daqui; modelar ameaça e desenhar o
  controle é do `departamento-seguranca`.
- **Os geradores de track** (`java-db-foundation`, `springboot-entity`, `java-jdbc-dao`,
  `web-data-layer`). São executores de stack específica e continuam vivos no catálogo — este
  Departamento decide o modelo, e eles implementam. Consultados para extrair as RO aplicáveis;
  não absorvidos.

## Limite desta fundamentação

Fundamentação **não é baseline**. Nenhuma medição comparou este Departamento com a lente canônica
operando sozinha, e nenhum dos comportamentos declarados foi executado contra instância
independente. O que está provado é o que o validador prova — ver
[`evals/PLACAR.md`](../evals/PLACAR.md).
