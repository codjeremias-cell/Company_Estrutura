# Rodada 3 — recebimento e reconciliação §1.1

- **judgment_request_id:** `jrq-2026-07-28-frente5-r3-inovacao`
- **candidato:** `departamento-inovacao-melhoria`
- **modo:** VALIDACAO (um único candidato — protocolo §1.0). Fixado no recebimento.
- **required_level declarado na missão:** `INTERNO`
- **régua:** ADR-014, faixa fixa. `10 → VALIDATED` · `7–9 → ACEITO_USO_INTERNO` · `≤6 → REPROVED`.

## 1. Digest do candidato — reproduzido, não aceito

O pedido fixou `candidate_tree_sha256 = e50aa56606b9e62be7159ab504fbdcdf70add43ef62fccd104db87a8ec740346`.

Recalculado nesta rodada pela receita de `_compartilhado/verificacoes_pacote.py::digest_de_arvore`
(manifesto de 25 linhas, 2649 bytes, chave POSIX, comparador ordinal, linha
`sha256␣␣chave`, terminador `\n`, UTF-8 sem BOM). **Bate — mas só contra uma das duas árvores.**

| árvore | tree sha256 | confere com o pedido |
|---|---|---|
| runtime `.claude/skills/…/departamento-inovacao-melhoria` | `e50aa566…0346` | **SIM** |
| fonte `Estrutura Final de Skills/…/departamento-inovacao-melhoria` | `36789934b7e31313b8c53241f736926f9d59baf1f5a379033d3d50495530609f` | não |

**Árvore julgada nesta rodada: a do runtime**, por ser a que o digest do pedido fixa. Registrado
como `PEND-DUAS-ARVORES-UM-DIGEST` (ver §3).

Origem da divergência, medida: dos 25 arquivos, **24 são byte a byte idênticos** nas duas árvores.
O único divergente é `RESPOSTA-FRENTE-JURIDICA-2026-07-27.md`
(`cf8c6eb3…` na fonte, `562eda4d…` no runtime); `diff` acusa `1,94c1,94` — todas as linhas —
assinatura de fim de linha, não de conteúdo. Nenhum arquivo do contrato julgado está no delta:
`SKILL.md`, `CONTRATO-DE-COMPROMISSO.md`, `evals/PLACAR.md`, `references/`, `schemas/` e os três
agentes são idênticos nas duas árvores. **A divergência não toca a superfície julgada.**

`SKILL.md` = `fa95dfdf…944c5` e `evals/PLACAR.md` = `993aaa51…e7bc`, ambos conferidos e batendo
com o pedido, nas duas árvores.

**Pendência da rodada 2 fechada:** `PEND-DIGEST-NAO-RECOMPUTADO-PELA-GERENTE` — nesta rodada a
gerente recomputou o digest por si, sem depender de reprodução de terceiro.

## 2. Reuso da `CRITERIA_MATRIX` — permitido, com rebind

Foi determinado reusar a matriz da rodada 2
(`forward-test-julgamento-rodada2/03-CRITERIA_MATRIX.yaml`,
sha256 `939695fb834bbf25890cb9bc96adbb02e1f3ffe0be396226bdc8328136983e2a`, **conferido e batendo**),
com um fator só mudando.

Varri os contratos dos Juízes atrás de regra que proíba reusar matriz de outra rodada.
**Nenhuma proíbe.** A matriz é partição interna da gerente e não carrega nota — o próprio artefato
declara `consolidacao_antecipada: PROIBIDA — nenhuma nota, banda ou veredito existe neste artefato`.
O contrato exige (§1.2) que ela cubra todo `criterion_id` do pedido, seja montada antes da
delegação e vá íntegra ao relatório: os três requisitos são satisfeitos pelo reuso, já que o
contrato do candidato não mudou e os 8 critérios continuam válidos.

O que **existe** e foi respeitado é outra regra, vizinha e mais forte — protocolo §2,
`forbidden_context`: nenhuma atribuição pode citar **rodada anterior**, nota anterior, veredito
anterior ou histórico de retrabalho. O histórico que Jeremias forneceu (REPROVED, `minimum_score` 6,
o 6 no CRIT-06) **não foi repassado a nenhuma ótica**. As três julgaram cegas, contra o candidato
como ele está. Foi por isso que a pergunta sobre o §12 chegou à ótica dona como pergunta aberta
("legítimo ou evasão?"), sem dizer que havia parecer anterior.

Rebind aplicado: a matriz reusada é literal no conteúdo — 8 critérios, mesmos textos, mesmas donas,
mesmas razões — e re-endereçada na identidade (`judgment_request_ref` → `…-r3-…`), porque o §1
manda o quarteto viajar idêntico em todo envelope **desta** rodada. Reusar o conteúdo é permitido;
reusar o endereço de outra rodada quebraria a correlação. Ver `03-CRITERIA_MATRIX.yaml`.

## 3. Pendências declaradas desta rodada

- **`PEND-DUAS-ARVORES-UM-DIGEST`** — fonte e runtime não têm o mesmo digest de árvore. O pedido
  fixou o do runtime. Julgar o runtime é julgar o artefato implantado, não a fonte da verdade que o
  cofre declara canônica. Não bloqueia (o delta não toca a superfície julgada), mas quem promover
  esta nota para a fonte está promovendo por correlação, não por identidade.
- **`PEND-CONTAMINACAO-PLACAR`** — o candidato **publica dentro de si** o parecer do gate anterior
  (`evals/PLACAR.md:3-25` e `:95-107`, inclusive o caminho `…/forward-test-julgamento-rodada2/…`).
  Duas óticas o encontraram e pararam de lê-lo como insumo. Custo medido nesta rodada: a ótica
  `fidelidade-e-contrato` **excluiu `evals/PLACAR.md` da varredura do CRIT-07** e baixou a confiança
  daquele critério para `media`. A cegueira do §2 deixou de ser sustentável por construção — não por
  falha de quem julga, mas porque o artefato julgado carrega o julgamento anterior.
- **`PEND-BATERIA-NAO-EXECUTADA`** — `python` não executa neste ambiente por falta de permissão.
  Nenhuma ótica rodou `validate_workflow.py` nem `corpus_adversarial.py`. Os `122/122 PASS` e
  `45/45` são registro do candidato, não resultado reproduzido aqui. As notas vêm de leitura de
  código, schema e corpus — não de execução. Ausência de evidência permanece ausência.
