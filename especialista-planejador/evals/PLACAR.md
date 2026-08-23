# Placar — `especialista-planejador`, variante Estrutura

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 17/17 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:22b442c8f8d7df0227cfb982b93a62800ab0ccf6615f0bb672ba486465ded39b` | medido-em: 2026-08-22
<!-- /SELO-DE-CONTAGEM -->

**Data da medição: 2026-08-08.** Todo número abaixo carrega a data em que foi medido; nenhum número
de vizinho entra sem ela.

## O que foi executado

| Verificação | Executado? | Resultado |
|---|---|---|
| `python evals/validate_workflow.py` deste pacote, a partir da raiz do pacote | sim | **14/14 casos**, exit 0 |
| As sete travas de estrutura inteira, chamadas por este validador | sim | sem erro |
| Suítes dos 15 pacotes gerentes, **antes** de instalar este pacote | sim | 15/15 com exit 0 |
| Suítes dos 15 pacotes gerentes, **depois** de instalar este pacote | sim | comparadas caso a caso com a rodada anterior |
| Integridade do `ceo-maestro` (SHA-256 de cada arquivo, antes e depois) | sim | nenhum arquivo alterado |

O registro completo da instalação — as duas rodadas, o diff entre elas e os digests do `ceo-maestro`
— está fora deste pacote, em `.tmp-especialista-planejador/governance/estrutura/INSTALACAO-ESTRUTURA.md`,
porque é evidência de uma migração e não do funcionamento corrente da skill.

## O que este validador prova

1. O pacote está completo e **não tem** pasta de nó de cadeia (`agentes/`, `schemas/`, `references/`).
2. O frontmatter é canônico (só `name` e `description`), dentro dos limites de tamanho.
3. A interface de runtime declara nome, resumo de 25–64 caracteres e o token da skill.
4. O contrato tem as **doze** seções canônicas, na ordem, e as contáveis de fato contam itens.
5. Todo link markdown interno resolve em arquivo existente.
6. A posição **fora da cadeia** está declarada na `SKILL.md` e no contrato, com a fonte normativa
   citada por caminho relativo nos dois.
7. A região de doutrina está delimitada **uma única vez**, com `INICIO` antes de `FIM`.
8. As sete travas de estrutura inteira do `_compartilhado` passam com este pacote na árvore.

## O que ainda NÃO foi provado

### Dono e condição de fechamento, item a item

> Exigido pelos achados `CA-01` e `GR-01`/`GR-02` da remedição de 2026-08-03: pendência declarada sem dono é pendência de ninguém. "O próprio Departamento" significa o pacote que este placar mede — ele responde pela própria evidência.

| item | dono | fecha quando |
|---:|---|---|
| 1 | o próprio Departamento | uma sessão independente rodar os prompts contra ESTA variante — a medição do Catálogo mede a doutrina, que aqui é idêntica byte a byte, e não o envelope |
| 2 | o próprio Departamento | houver medição de acionamento em sessão nova com frase neutra, no molde da §1b do `CLAUDE.md` do cofre |
| 3 | o próprio Departamento | a paridade da região de doutrina virar trava que reprove divergência, em vez de receita executada por quem edita |
| 4 | Jeremias | o pacote for publicado em `.claude/skills/` ou `.agents/skills/` — ato separado, e deliberadamente fora deste placar |


- **SKIP — comportamento da skill nesta vertente.** Nenhuma sessão independente rodou os prompts
  contra esta variante. A medição comportamental que existe é a do Catálogo, sobre a `cand-lean`, e
  ela mede a **doutrina** — que aqui é idêntica byte a byte —, não o envelope. O envelope desta
  variante (identidade, canal, recusa de rota) **não tem medição comportamental nenhuma**. Transferir
  o número do Catálogo para cá seria creditar alcance por nome.
- **SKIP — acionamento em sessão nova.** Não foi medido se, com frase neutra, o runtime carrega esta
  skill em vez de responder direto. O `CLAUDE.md` do cofre documenta que descrição não vence resposta
  direta; sem instrução explícita, o acionamento é hipótese.
- **SKIP — paridade automática da doutrina.** A identidade de bytes com o Catálogo é conferida pela
  receita publicada na `SKILL.md`, executada por quem edita. Não há trava que reprove a divergência:
  ela é **detectável**, não impedida. Congelar o digest neste validador foi recusado de propósito —
  número congelado em validador envelhece calado, e o aparato de prova deste pacote foi removido por
  medição.
- **SKIP — deploy para runtime.** Este pacote existe na fonte da verdade. Publicá-lo em
  `.claude/skills/` ou `.agents/skills/` é ato separado, e não foi executado aqui.

## Fronteira que este placar não atravessa

Este documento mede **um pacote**. Ele não afirma total de cadeia como estado corrente, porque nenhum
pacote consegue rodar sozinho os validadores de todos os outros e saber o número do dia.
