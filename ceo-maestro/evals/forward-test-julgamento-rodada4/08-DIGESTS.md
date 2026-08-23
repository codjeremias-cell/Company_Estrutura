# Digests — rodada 4 de julgamento, `departamento-inovacao-melhoria`

Data: **2026-07-28**. Receita: `_compartilhado/verificacoes_pacote.py`, `digest_de_arvore`.

## Como foi recalculado

Python **não roda nesta sessão** (permissão negada — a mesma limitação que a gerente
registrou na rodada 2 como `PEND-DIGEST-NAO-RECOMPUTADO-PELA-GERENTE`). O digest foi
recalculado por **reimplementação independente** da receita, o que é evidência mais forte
que rodar o próprio código do pacote: dois caminhos distintos chegando ao mesmo número.

Receita aplicada, passo a passo, como a docstring fixa:
chave = caminho relativo POSIX · ordenação **ordinal** sobre a chave · linha =
`<sha256hex>` + **dois espaços** + chave · separador `\n` · terminador `\n` ·
manifesto UTF-8 sem BOM · digest = SHA-256 do manifesto · conteúdo em **bytes crus**,
sem normalizar fim de linha.

## Resultado — os três declarados batem

| Alvo | Declarado por Jeremias | Recalculado | Confere |
|---|---|---|---|
| árvore runtime | `bbcae768…c3fd4f58` | `bbcae76833d7d54d051af903b7949e478272c720743cd176c1a0c1acc3fd4f58` | ✅ |
| árvore fonte | `08e5c79c…9b7a02e512a` | `08e5c79c5c0d616d062a535918d1bce27595cfda0f313e6a689f79b7a02e512a` | ✅ |
| `evals/PLACAR.md` (runtime) | `b4d60fe6…60c160f1bf8` | `b4d60fe694a4e83b03a2f64c16fc96e2143129ca97d40c3ea3960dc6160f1bf8` | ✅ |

Os três batem **caractere a caractere**, 64 dígitos hex cada. Nenhuma ressalva de
transcrição: o que Jeremias declarou é exatamente o que a receita produz.

Ambos os manifestos têm **2649 bytes** e **25 linhas** — o mesmo tamanho do manifesto da
rodada 2 (`1913add7…`), confirmando que o conjunto de caminhos não mudou: o que mudou foi
conteúdo.

## O achado das duas árvores

Comparação arquivo a arquivo, os 25 de cada lado:

- **24 de 25 são byte-idênticos** entre runtime e fonte (CRLF nos dois lados);
- **1 diverge**: `RESPOSTA-FRENTE-JURIDICA-2026-07-27.md`
  - runtime `562eda4df7ae053cf22d46a4176375641c0a65baa1f0d6dd233342ed6bc881e7` — **LF**
  - fonte   `cf8c6eb310b952b21162ee11417ca5e05d588c7b35596e0a695c73558828c882` — **CRLF**

Portanto a afirmação "a divergência entre as duas é de fim de linha" está **imprecisa como
enunciada**. Não existe regime de EOL distinto entre as árvores — existe **um único arquivo**
cujo fim de linha foi normalizado para LF só no runtime. Anomalia pontual de espelhamento.

**Não invalida o julgamento.** O arquivo divergente não é evidência de nenhum dos 8
critérios; para tudo que os critérios examinam, julgar o runtime é julgar a fonte, byte a
byte. O veredito vale para as duas cópias.

**Achado derivado:** enquanto o deploy não fixar EOL, todo `candidate_tree_sha256` vale para
uma cópia só e precisa dizer qual — a receita é deliberadamente sensível a EOL, e um único
arquivo normalizado já basta para produzir dois números para o mesmo conteúdo lógico.

## Insumos conferidos

| Artefato | SHA-256 |
|---|---|
| `…/forward-test-julgamento-rodada2/03-CRITERIA_MATRIX.yaml` | `939695fb834bbf25890cb9bc96adbb02e1f3ffe0be396226bdc8328136983e2a` ✅ igual ao declarado |

## Envelopes emitidos nesta rodada

| Arquivo | SHA-256 |
|---|---|
| `JUDGE_OPINION-CRIT-04-robustez-e-evidencia.md` | `ee508ca8c39e4029d136d80297fc60e87b396935cb5c5d4e73ab1dc5e63194aa` |
| `JUDGE_OPINION-CRIT-05-robustez-e-evidencia.md` | `1c12e3287bc9ad2f75e9c43b5573a8bd404588894edc22b4aa1455e5864af6e2` |
| `JUDGE_OPINION-CRIT-06-robustez-e-evidencia.md` | `6bb68917f9573901cedb471eba7d19fbe39f984665df95060ed8f3dfb5ed031b` |
| `JUDGE_OPINION-CRIT-07-fidelidade-e-contrato.md` | `e201eb637f0d06c036a58f8175c2d9252adc45ccbc63f0230e6ec41e1e19abb8` |
| `JUDGE_OPINION-CRIT-08-robustez-e-evidencia.md` | `0ee008e8847f24c79f40d9a82db82f473e0a12d903e03e49ef5e2ff98da4c538` |
| `07-JUDGE_REPORT.yaml` | `d5b2f5168015e344266c0a28eac9bf6c51c5f0a3d37bda11555dc29272c51192` |

O `08-DIGESTS.md` não se auto-hasheia: quem quiser conferir roda `sha256sum` sobre ele.

## Escopo do que os digests provam

Provam **identidade da cópia julgada**. Não provam que as baterias do candidato passam:
nenhum juiz executou `validate_workflow.py` nem `corpus_adversarial.py` — Python está
negado nesta sessão. Os `122/122 PASS` e `45/45` que o pacote exibe permanecem **alegação
do candidato**, não medição dos Juízes. Ausência de evidência permanece ausência.
