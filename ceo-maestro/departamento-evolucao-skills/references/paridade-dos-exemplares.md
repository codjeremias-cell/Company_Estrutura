# Paridade dos três exemplares — a norma, e como conferir

> Fecha a segunda metade do achado `FIND-REMED7-C02-EA-02` (remedição de 2026-08-03, `HIGH`,
> bloqueante). A primeira metade — *"fazer os três exemplares voltarem a bater"* — **já está
> satisfeita**, medida em 2026-08-08 e transcrita abaixo. A segunda dizia, literalmente, que *"a
> raiz auditada não menciona `.claude/skills` nem `.agents/skills` em nenhum `.md` fora de
> `evals/`, então não há norma publicada contra a qual medir"*. Este documento é essa norma.

## Os três exemplares

| exemplar | caminho | papel |
|---|---|---|
| **fonte** | `Estrutura Final de Skills/ceo-maestro/departamento-evolucao-skills/` | a única que se edita |
| runtime Claude | `.claude/skills/ceo-maestro/departamento-evolucao-skills/` | cópia gerada |
| runtime Codex | `.agents/skills/ceo-maestro/departamento-evolucao-skills/` | cópia gerada |

A Estrutura é implantada como **porta única**: só o `ceo-maestro` é skill invocável, e este
Departamento viaja aninhado dentro dele. Por isso o exemplar de runtime não fica em
`.claude/skills/departamento-evolucao-skills/`, e procurá-lo ali dá falso negativo.

## A norma

**A paridade é por BYTES, não por conteúdo normalizado.** As duas cópias de runtime têm de
reproduzir o `digest_de_arvore` da fonte, exatamente.

- **Receita:** `_compartilhado/verificacoes_pacote.py::digest_de_arvore`, e em nenhum outro lugar.
  Ela percorre só arquivos, exclui qualquer caminho com componente `__pycache__`, usa o caminho
  relativo com `/`, ordena por comparador **ordinal**, monta linhas `sha256  caminho` no formato do
  `sha256sum` e tira o SHA-256 desse manifesto.
- **O conteúdo entra em bytes crus**, sem normalizar fim de linha. Isso é deliberado: a mesma
  árvore em CRLF e em LF dá digests diferentes, e quem precisa comparar cópias com EOL distinto tem
  um problema de normalização a resolver antes, não um digest a afrouxar. O `.gitattributes` do
  cofre é que garante o LF nos três caminhos.
- **`__pycache__` fica de fora**, e é a única exclusão. Não é conveniência: `.pyc` é artefato de
  execução, muda com a versão do interpretador e não é conteúdo entregue.

## Como conferir, literal

```
cd "Estrutura Final de Skills"
PYTHONIOENCODING=utf-8 python -c "import sys; sys.path.insert(0,'.'); from _compartilhado.verificacoes_pacote import digest_de_arvore; from pathlib import Path; [print(r, digest_de_arvore(Path(p))) for r, p in (('fonte','ceo-maestro/departamento-evolucao-skills'), ('claude','../.claude/skills/ceo-maestro/departamento-evolucao-skills'), ('agents','../.agents/skills/ceo-maestro/departamento-evolucao-skills'))]"
```

Os três números têm de ser iguais. Diferença é **defeito**, e agora existe norma que diz isso.

## A medição de 2026-08-08

| exemplar | `digest_de_arvore` |
|---|---|
| fonte | `e20358cc120c94472912c0adba143c9d999c47986e9f347372975ef80aac79ad` |
| runtime Claude | `e20358cc120c94472912c0adba143c9d999c47986e9f347372975ef80aac79ad` |
| runtime Codex | `e20358cc120c94472912c0adba143c9d999c47986e9f347372975ef80aac79ad` |

Conferido também arquivo a arquivo: **462 arquivos comuns, ZERO diferindo em bytes**. Os 4 que
existem só na fonte são `__pycache__/*.pyc`, que a receita exclui — e é por isso que o digest bate
mesmo com a contagem bruta de arquivos diferindo (466 contra 462). **Contar arquivos não é conferir
paridade**; quem comparar pelo número vai achar divergência onde não há.

## O que esta norma NÃO garante

Não garante que os exemplares continuem batendo. Os runtimes são **gerados** por
`deploy-skills.ps1`, que não é executado por este Departamento nem por esta frente, e um espelho
que rode sem preservar o runtime da Estrutura desfaz a paridade sem que nada aqui fique vermelho.
Nenhuma trava deste pacote confere os três exemplares — a conferência é a receita acima, executada
por quem edita.

Fechar isso exigiria a trava rodar sobre caminhos **fora** da raiz auditada, o que é decisão de
fronteira entre esta frente e a do Catálogo, dona dos dois runtimes e do script de deploy. Está
registrado em `estado/FRENTES-ATIVAS.md` e no `estado.json`, e é ato de acordo, não de conserto
unilateral.
