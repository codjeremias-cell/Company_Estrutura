# Forward comportamental — Departamento de Arquitetura de Dados

Data: 2026-07-26
Versão avaliada: 1.0.0
Instâncias: **16 independentes**, uma por caso

> **Reconciliação de 2026-07-29.** A medição original classificou como fabricada a atribuição do
> teto de 1000 linhas à RO-W8. Essa classificação estava errada: a frase já constava literalmente
> da fonte normativa na revisão da Estrutura criada pelo commit `36027a2b` e continua presente.
> O registro abaixo foi corrigido sem apagar o erro de avaliação; a prova estruturada e as mutações
> estão em [`forward-proveniencia.json`](forward-proveniencia.json).

## Método

Uma instância por caso — agrupar prompts no mesmo agente ensina o padrão de recusa e enviesa o
resultado *para passar*. Cada instância recebeu apenas o caminho do `SKILL.md` e o prompt.

O relatório original afirma que cada instância gravou a resposta completa em
`scratchpad/forward/dados-NN.md` e devolveu um resumo do que **recusou**, do que **entregou** e de
**toda afirmação numérica, de API ou de regra**. Esses arquivos brutos não existem no worktree nem
na revisão-base, e o `evals.json` mantém `acionou` e `aderiu` como `NAO_MEDIDO`. Portanto, o método
e as contagens abaixo são **relato histórico não reproduzível**, não prova vigente.

O resumo preservado ainda permite reconciliar as duas citações normativas relatadas no caso 15,
mas não permite reconstituir nem promover o resultado comportamental das 16 respostas.

## Resultado

| Medida | Resultado |
|---|---|
| Casos reportados | **16 de 16** — histórico; respostas brutas ausentes |
| Asserções reportadas | **49/49 PASS** — histórico; não reproduzível |
| Contorno de contrato reportado | **zero** — não reproduzível |
| Defeitos encontrados | **1** no schema; a suposta falha de citação era erro da avaliação |
| Procedência normativa inventariada | **2/2 citações verificadas** |
| Estado vigente do forward | **NOT_PROVEN** |

## Defeito 1 — a L5 existia só em prosa (corrigido)

O caso 14 (efeito colateral dentro da transação) devolveu, sem ser perguntado:

> *"Notei que o schema aceita `IN_TRANSACTION` — quem recusa é a L5, não o validador."*

Correto. O `commit_relative_trigger` admitia `IN_TRANSACTION` exigindo apenas o fluxo de erro
declarado. A regra que proíbe **efeito externo** dentro da transação vivia só no texto.

**Correção aplicada.** O valor `IN_TRANSACTION` não foi removido — escrever na tabela de outbox
*é* legitimamente dentro da transação, e é o ponto do padrão. A trava é condicional:

```
IN_TRANSACTION  ⇒  anti_dual_write == OUTBOX
```

Efeito externo (e-mail, HTTP) só com `AFTER_COMMIT`. Três casos negativos entraram no validador
(`110 → 114`), incluindo o de `CDC`, que não basta: CDC lê o log depois do commit, não escreve
dentro dele.

É a lição do dia aplicada a mim mesmo: **regra que importa vira trava, não parágrafo.**

## Erro de avaliação 2 — citação existente foi classificada como inventada (corrigido)

O caso 15 (Supabase) citou duas regras da governança:

| Citação | Verificação |
|---|---|
| **RO-W1** — *anon key pública por design* | ✅ exata |
| **RO-W8** — *consulta sem limite corta em 1000 linhas no Supabase* | ✅ **exata** |

Na medição original, a segunda linha foi marcada como falsa sob a alegação de que RO-W8 tratava
somente de erro e data. A conferência da fonte mostra o contrário. A própria linha da
[RO-W8](../../../../../regras-de-ouro/REGRAS-DE-OURO.md) termina com:

> *"Consulta sem limite corta em 1000 linhas no Supabase — sinalizar o teto ao usuário."*

O Git remonta essa linha ao commit `36027a2b`, de 2026-07-26; no Catálogo, a mesma redação já
existia desde a ratificação das RO-W1…W8. O fato técnico também é corroborado pela
[referência oficial do Supabase para `select()`](https://supabase.com/docs/reference/javascript/v1/select),
que registra o máximo padrão de 1000 linhas e a configuração nas API Settings. Essa fonte externa
corrobora o fato; a autoridade normativa continua sendo exclusivamente a RO-W8 local.

**Correção aplicada.** A **procedência normativa** do caso 15 fica `PASS`; o forward comportamental
geral fica `NOT_PROVEN`. O inventário estrutura cada citação com `rule_id`, âncora e digest da
linha normativa. O validador exige que a âncora esteja **na mesma regra citada**, preserva a
ausência dos brutos e executa quatro mutações: âncora fabricada, citação não verificada conservando
`PASS`, placar adulterado e omissão da RO-W8. As quatro precisam ficar vermelhas internamente para
o pacote passar.

## Verificação independente das afirmações

Conferidas na fonte, além das duas acima:

- **`MODE=PostgreSQL` e `SKIP LOCKED`** (caso 6) — modo de compatibilidade real do H2 e uma de suas
  lacunas reais. Exemplo correto para o argumento do engine único.
- **NULL em constraint de unicidade** (caso 13) — múltiplos NULLs em PostgreSQL, MySQL e SQLite; um
  só no SQL Server. Correto, e é a pegadinha que morde em migração entre engines.
- **Fan-out de grão misto** (caso 16) — *3 itens × 2 pagamentos = 6 linhas, soma 6×*. Aritmética
  correta, e é a demonstração concreta da dupla contagem.
- **Volumetria derivada** (caso 2) — 1M dobrando por ano → 32M em 5 anos; parcelas na ordem de 10⁸.
  Ordem de grandeza correta, que é exatamente o que o piso pede.

## Comportamentos notáveis, não exigidos pelos checks

- **Caso 5:** o prompt disse "V23", que *parece* convenção Flyway mas nunca nomeou a ferramenta. A
  instância inferiu e **rotulou a inferência como suposição** em vez de afirmar.
- **Caso 13:** **aceitou** a constraint proposta — *"só o banco fecha a corrida do clique duplo"* —
  e recusou apenas o "e pronto". A proposta estava certa; o fechamento é que não estava.
- **Caso 10:** recusou também as **versões suavizadas** da nota — chute informal, semáforo, adjetivo
  comparativo. Defendeu o zero-contorno ativamente.
- **Caso 8:** *"rollback de `DROP` devolve estrutura, não dado"* — a ressalva que decide se a
  reversão vale algo.
- **Caso 9:** marcou `constraint_conflict: false` corretamente — a restrição não inviabiliza o
  modelo (há três alternativas), então escalar seria errado.
- **Caso 11:** entregou o achado de PII **apesar** do piso bloquear a modelagem. O gate certo travou
  a coisa certa.

## O que este forward NÃO prova

1. **O resultado comportamental relatado.** As respostas brutas
   `scratchpad/forward/dados-NN.md` estão ausentes; por isso 16/16, 49/49 e zero contorno não são
   prova vigente. O catálogo continua corretamente em `NAO_MEDIDO`.
2. **Disparo orgânico.** O pacote não está instalado como skill de runtime; o caminho do `SKILL.md`
   foi entregue à instância.
3. **Acionamento por roteamento cego.** Não foi medido para este pacote. No forward do Design, dois
   roteadores independentes cobriram os 16 prompts de lá; aqui não houve equivalente.
4. **Baseline.** Não existe pacote legado — este Departamento é skill nova. A comparação com a
   lente canônica `arquiteto-dados` nos mesmos cenários não foi feita.
5. **Auditoria independente e parecer dos Juízes.** Pendentes.
6. **R1/R2 permanecem.** O relatório histórico diz que as instâncias produziram projeções, não
   medições em banco real; sem os brutos, essa aderência também não é reproduzível.

