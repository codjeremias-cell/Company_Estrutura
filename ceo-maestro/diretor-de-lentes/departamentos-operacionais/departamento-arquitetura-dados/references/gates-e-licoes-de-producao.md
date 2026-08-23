# Gates de entrada e saída, e as lições que já custaram caro

Duas travas objetivas e um conjunto de regras que **não** são teoria: cada uma abaixo tem origem em
regra de ouro vigente ou em incidente registrado em projeto real do Jeremias. É o que diferencia
este Departamento de um manual de modelagem genérico.

## Gate de entrada — o piso

Nenhuma frente de modelagem abre sem os dois:

1. **≥ 3 perguntas do negócio** que o dado precisa responder, escritas;
2. **volumetria em ordem de grandeza** — linhas hoje, crescimento, leitura por segundo no pico.

Faltando qualquer um, o Departamento **não modela**: devolve ao Diretor com
`DATA_CAPABILITY_GAP` apontando `requisitos-descoberta`. Modelar sem pergunta é modelar por
reflexo, e o resultado é um schema que responde bem a perguntas que ninguém fez.

Também decide-se aqui, com evidência e não por hábito: **OLTP ou OLAP**. A mesma modelagem não
serve às duas cargas.

## Gate de saída — o fechamento checável (RI-04)

A entrega só fecha com os três, e cada um é campo obrigatório do schema:

| Item | Provado por |
|---|---|
| **Grão declarado** | frase explícita do que **uma linha** representa, por tabela/coleção do modelo |
| **Plano expand/contract com rollback** | as fases nomeadas e o ponto de reversão de cada uma |
| **Índice ou partição justificado por padrão de acesso** | o acesso real que o motiva, não "por garantia" |

> **Faltou um = entrega incompleta.** Não é recomendação: o validador reprova.

## Lições com procedência — regras duras

### L1 · Migração que já pisou em banco é imutável

Migração aplicada em **qualquer** banco — dev e Neon inclusive — **nunca** é editada: vira versão
nova. *"Não commitada" não é critério.*

**Custo real:** editar uma já aplicada gerou **97 erros em cascata** por `checksum mismatch`
(`Aprendizagem/Gradup.md`, épico banco de questões; também em `Melhorias e Aprendizados.md` e
SIGO-SIGCOT). Todo plano de migração emitido aqui declara a próxima versão livre.

### L2 · Um engine só, dev = prod

**RO-SB2.** Migrações versionadas (`V1__`, `V2__`…) com `ddl-auto=validate` — o ORM **nunca** cria
ou altera schema; quem manda é a migração. E **o mesmo engine em dev e produção**: desenvolver em
SQLite/H2 para "subir depois" quebra a premissa de que basta migrar. Toda escolha de persistência
emitida aqui declara o engine único de ponta a ponta.

Em desktop (**RO-DT3**), o mesmo princípio com uma ressalva que precisa estar no plano: o
`tauri-plugin-sql` aplica o **up** no boot, mas o **down** é artefato manual de dev — ou seja, o
rollback existe como arquivo, não como automatismo. Declarar isso é obrigação, não detalhe.

### L3 · Operação multi-passo é transação atômica

**RO-SB3** e a lição do lote de férias (`EscalaOper`): multi-passo usa `@Transactional` ou
`setAutoCommit(false)` + `commit`/`rollback`. **Nunca gravação parcial.** Todo modelo que exija
escrita em mais de uma tabela declara a fronteira transacional junto — quem desenha o modelo é quem
sabe onde a atomicidade é obrigatória.

### L4 · O tratamento do erro de integridade fica fora da transação

Capturar `DataIntegrityViolationException` **dentro** da `@Transactional` não funciona: a transação
já está `rollback-only` e a query do próprio `catch` falha. E `UPDATE` em massa via `@Modifying`
precisa de `clearAutomatically=true`, senão o cache de primeiro nível serve dado obsoleto na mesma
transação. (`Aprendizagem/Gradup.md`, frente PP/QA visual.)

Consequência para o desenho: **constraint de unicidade não é só integridade, é fluxo de erro.** Ao
declarar uma constraint, este Departamento declara também o que o consumidor deve fazer quando ela
disparar — isso segue na dependência para o `departamento-desenvolvimento`.

### L5 · Efeito colateral só depois do commit

Efeito externo disparado dentro da transação vaza estado que pode não existir. O padrão validado é
`@TransactionalEventListener(AFTER_COMMIT)` (`Aprendizagem/Gradup.md`) — que, além de correto,
fechou uma enumeração por *timing* (CWE-208). Modelo que dispara integração declara o ponto de
disparo relativo ao commit.

### L6 · Acesso sempre parametrizado

**RO-04** e **RO-10.** Acesso parametrizado (`?`), nunca concatenação de entrada; em JDBC,
`try-with-resources` em `Connection`/`Statement`/`ResultSet` (a padronização do `EscalaBD` nasceu de
13 `ResultSet` corrigidos). Aqui isso vira **restrição anexada à dependência** que vai para o
Desenvolvimento — este Departamento não escreve o acesso, mas não entrega modelo sem a regra junto.

### L7 · Quando o banco é a fronteira de segurança, diga

**RO-W2.** Em stack Supabase, **RLS é a fronteira de segurança**: checklist de RLS em todas as
tabelas e bucket privado antes de expor. Modelo emitido para essa stack **declara a política de RLS
por tabela** — e a dependência vai para o `departamento-seguranca`, que endurece. Modelar tabela
exposta sem dizer isso é entregar furo por omissão.

## Como isso entra na entrega

Cada lição acima que se aplicar ao caso vira **restrição declarada** no retorno, com a origem
citada. O que não se aplicar fica de fora — anexar regra irrelevante é sedimento, e sedimento é
falha de autoria pelo `PADRAO-DE-AUTORIA.md`.
