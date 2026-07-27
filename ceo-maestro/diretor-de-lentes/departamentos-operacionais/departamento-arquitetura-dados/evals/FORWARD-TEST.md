# Forward comportamental — Departamento de Arquitetura de Dados

Data: 2026-07-26
Versão avaliada: 1.0.0
Instâncias: **16 independentes**, uma por caso

## Método

Uma instância por caso — agrupar prompts no mesmo agente ensina o padrão de recusa e enviesa o
resultado *para passar*. Cada instância recebeu apenas o caminho do `SKILL.md` e o prompt.

**Diferença em relação ao forward do Design:** cada instância gravou a resposta completa em
`scratchpad/forward/dados-NN.md` e devolveu só um resumo do que **recusou**, do que **entregou** e
de **toda afirmação numérica, de API ou de regra**. Os checks do `evals.json` **não** foram
mostrados às instâncias — não há como escrever para o teste. A correção foi feita contra o catálogo
depois, por quem não produziu as respostas.

Esse formato provou seu valor: **o defeito de citação abaixo só ficou visível porque as afirmações
vieram listadas.** Numa resposta longa, uma citação errada entre vinte corretas passaria batido.

## Resultado

| Medida | Resultado |
|---|---|
| Casos válidos | **16 de 16** — nenhum mal especificado |
| Asserções | **49/49 PASS** |
| Contorno de contrato | **zero** |
| Defeitos encontrados | **2** — um no schema deste pacote, um de citação |

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

## Defeito 2 — citação de regra inventada (registrado, não corrigido)

O caso 15 (Supabase) citou duas regras da governança:

| Citação | Verificação |
|---|---|
| **RO-W1** — *anon key pública por design* | ✅ exata |
| **RO-W8** — *consulta sem limite corta em 1000 linhas no Supabase* | ❌ **falsa** |

RO-W8 é *"Erro e data honestos"* — trata de `catch` que não pode ser só `console.error`, dos estados
carregando/erro/vazio e de gravar data local em vez de UTC cru. Não diz nada sobre limite de linhas.

O **fato** é verdadeiro (o PostgREST do Supabase tem limite padrão configurável), mas a
**atribuição foi fabricada**: uma afirmação real pendurada num número de regra que não a contém.
Isso é violação de RO-01, e é registrado como defeito ainda que o caso 15 passe nos três checks
declarados, que são sobre RLS.

**Primeira atribuição infundada em 31 casos rodados** (15 do Design, 16 daqui). No Design foram
verificados 11 valores de contraste, cinco afirmações de API do JavaFX e uma citação de pacote
vizinho — todas exatas.

**Ação:** nenhum arquivo do pacote precisa mudar — o defeito é da resposta, não do contrato. Fica
como evidência de que citação de regra é um vetor de invenção que sobrevive a um pacote bem
construído, e de que o resumo estruturado é o que o torna visível.

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

1. **Disparo orgânico.** O pacote não está instalado como skill de runtime; o caminho do `SKILL.md`
   foi entregue à instância.
2. **Acionamento por roteamento cego.** Não foi medido para este pacote. No forward do Design, dois
   roteadores independentes cobriram os 16 prompts de lá; aqui não houve equivalente.
3. **Baseline.** Não existe pacote legado — este Departamento é skill nova. A comparação com a
   lente canônica `arquiteto-dados` nos mesmos cenários não foi feita.
4. **Auditoria independente e parecer dos Juízes.** Pendentes.
5. **R1/R2 permanecem.** Tudo que as instâncias entregaram é projeção. Nenhuma mediu nada em banco
   real, e todas declararam isso.
