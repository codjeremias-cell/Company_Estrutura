# ADR-021 — Identidade de candidato é digest de CONTEÚDO; bytes crus são proveniência

- **Data:** 2026-08-05
- **Status:** **RASCUNHO** — proposta do `departamento-evolucao-skills`, sob
  `MISSION-DIGEST-QUE-NAO-REPROVA-R3-FINAL-20260805` (tarefa 19, rodada 3). Entra na árvore
  como `.candidate`; vigora somente se o candidato for adotado por decisão de Jeremias.
- **Decisores:** `ceo-maestro` propõe a Jeremias; a conformidade da adoção é da Auditoria.
- **Dono pela posição:** `departamento-arquitetura-dados` — identidade de um artefato é
  decisão de modelagem de dados, no mesmo padrão que pôs o ADR-015 em arquitetura-software
  e o ADR-016 nos Juízes.
- **Número conferido contra a árvore em 2026-08-05:** a série global vai de 001 a 018 nos
  `references/` vivos; **019 está reservado** por 37 `adr-019-*.md.candidate` pendentes da
  campanha `contrato-analysis-2026-07-31`; **020 está ocupado** (dois `adr-020-*.md` num lab
  de `producao-honesta-2026-08-04`, FAIL pré-existente de duplicidade) **e reservado** por 4
  `adr-020-*.md.candidate` da mesma campanha. **021 não tem arquivo nem menção na árvore.**
  Receita: `find . -name "adr-*.md" -o -name "adr-*.md.candidate"` sobre a raiz da
  Estrutura, commit `12c0dbe`, mais grep textual por `adr-021|ADR-021` (zero ocorrências).

> **Nota de reprodutibilidade — 2026-08-22 (tarefa 101).** O parágrafo acima descreve o que foi
> medido em **2026-08-05** e **não é alterado**: reescrever a conferência de um registro seria
> alterar o registro. O que esta nota acrescenta é que **a receita publicada nele não reproduz o
> universo que a trava usa**, e a diferença tem tamanho.
>
> **A receita, ao pé da letra, executada em 2026-08-22:** 337 arquivos, 25 números distintos, **9
> números com mais de um arquivo**, maior número visto `025`. **A trava:** 25 arquivos, 23 números,
> **1** grupo repetido. Treze vezes mais arquivos, nove vezes mais colisões aparentes.
>
> **A causa é uma só: a receita declara a RAIZ e não declara a EXCLUSÃO.** Ela conta cópia de
> laboratório, `overlay/` de candidato e backup de campanha como se cunhassem número. A trava
> exclui por partes do caminho — `_PASTAS_QUE_NAO_SAO_PACOTE = ("agentes",
> "fontes-legadas-pinadas", "evals")` —, e a razão está escrita nela: *"cópia de laboratório não
> cunha número… a trava continua pegando colisão real, que por definição mora fora de `evals/`"*.
>
> **Medido de propósito, porque a casa tem dois critérios e eu não quis supor que coincidem:** o
> critério da trava (por nome de parte do caminho) e o critério **estrutural** da tarefa 96
> (`evals/` como ancestral ⇒ cópia) devolvem hoje **exatamente o mesmo conjunto** — 25 e 25, com
> diferença simétrica **zero nos dois sentidos**. Coincidem porque `evals` está nos dois; não
> porque um implique o outro.
>
> **A única repetição que sobra está perdoada, e por caminho exato:** os três `adr-001` de
> `ceo-maestro`, `diretor-de-lentes` e `departamento-negocios`, declarados em
> `ADR_HISTORICAL_EXCEPTIONS`. A isenção é por **caminho**, nunca por número — um quarto `adr-001`
> em qualquer outro lugar reprova o grupo inteiro.
>
> **Duas afirmações do parágrafo acima venceram**, e ficam nomeadas em vez de corrigidas no lugar:
> *"a série vai de 001 a 018"* (hoje o maior é `025`) e *"021 não tem arquivo nem menção na
> árvore"* — este próprio arquivo é o `adr-021`, o que torna a frase verdadeira quando escrita e
> falsa desde o instante seguinte.
>
> **A norma que sai daqui, e ela vale para qualquer ADR futuro:** a autoridade sobre a série é
> `_compartilhado/verificacoes_estrutura.py::validate_adr_series`, e o documento **cita a trava em
> vez de reimplementá-la**. Receita em prosa que reescreve o que um validador faz é uma segunda
> fonte da verdade, e segunda fonte deriva — foi o que aconteceu aqui em dezessete dias. Para
> cunhar o próximo número, execute a cadeia: se o número colidir, `validate_adr_series` reprova
> nos dezesseis pacotes de uma vez.

## Contexto — a medição que obriga a decidir

Duas medições, duas rodadas:

1. **Rodada 1 (T19):** o `candidate_digest` do candidato, computado sobre **bytes crus**,
   deu `4abadd31…` na cópia de trabalho onde foi gerado e `bc429bb4…` num worktree novo do
   **mesmo commit**. Nenhum caractere mudou; o fim de linha do checkout mudou
   (`core.autocrlf=true`, e o `.gitattributes` do cofre não cobre
   `Estrutura Final de Skills/`).
2. **Rodada 2 (T19):** a prova de worktree (`saida-crua-r2/13-prova-worktree.json`) repetiu o
   fenômeno de propósito: checkout novo virou 20 de 20 arquivos para CRLF; a identidade por
   conteúdo não se moveu (`ea3b51cc…` nas três árvores), a de bytes crus deu dois valores.

A lição já estava paga e registrada na memória da casa: **digest de arquivo não é
identidade** — o EOL do checkout muda o SHA-256 e a conferência não sobrevive a um clone.

## Decisão

1. **A identidade de um candidato é o digest do CONTEÚDO normalizado**, pela receita de
   `_compartilhado/verificacoes_pacote.py::digest_de_arvore_normalizado`: para cada arquivo
   do overlay, BOM removido e `CRLF`→`LF` antes do `sha256` (arquivo que não decodifica em
   UTF-8 entra em bytes crus); manifesto de linhas `<sha256>  <chave relativa>` ordenado
   pela chave com comparador ordinal, separador e terminador `\n`, UTF-8 sem BOM; a
   identidade é o `sha256` desse manifesto, com prefixo `sha256:`.
2. **O digest de bytes crus continua sendo computado e publicado — como PROVENIÊNCIA, nunca
   como identidade.** Ele responde «que bytes exatos estavam neste checkout quando o
   candidato foi gerado», que é pergunta de custódia, não de endereço. No `manifest.json`
   ele vive sob nome que nega a identidade (`digest_de_bytes_crus_NAO_E_IDENTIDADE`, e
   `sha256_depois` por arquivo, para o gate de recomputação da Auditoria).
3. **As duas medidas têm nomes distintos e não se substituem.** Empatar os nomes foi o que
   produziu a disputa de identidade de 2026-08-01.

## Consequências

- Identidade passa a sobreviver a clone, worktree e checkout com `autocrlf` — conferível em
  qualquer máquina que leia a receita.
- O gate vivo `conferir_manifesto_do_candidato` (recomputação de `sha256_depois` sobre bytes
  crus) **continua verde**: o manifesto carrega as duas formas, e a conferência de custódia
  não é enfraquecida pela mudança do que significa identidade.
- Custo aceito: dois números por arquivo no manifesto. É o preço de não fingir que uma
  medida serve às duas perguntas.
- **Alcance:** esta decisão nomeia a identidade de CANDIDATO (pacote de overlay entregue a
  julgamento). Digests declarados de artefatos avulsos da árvore seguem a regra local de
  quem os declara; a normalização de EOL da árvore inteira é decisão separada, de Jeremias,
  com `BLOCKED_RETURN` já emitido na rodada 2 e preço medido
  (`saida-crua-r2/12-impacto-eol.json`: 2 522 digests declarados deixam de reproduzir).

## Alternativas recusadas

- **Só bytes crus** (estado da rodada 1): reprova candidato idêntico por causa do checkout —
  vermelho que mente.
- **Só conteúdo, sem proveniência**: quebraria o gate vivo de recomputação da Auditoria e
  apagaria a resposta de custódia — o `FURO 4` de novo, do outro lado.
- **Mudar o gate vivo para aceitar a receita nova**: mover a régua para caber o medido — o
  anti-padrão que esta campanha inteira existe para matar.
