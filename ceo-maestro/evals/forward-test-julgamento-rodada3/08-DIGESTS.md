# Digests da rodada 3

## Entradas conferidas (recalculadas, não aceitas)

| artefato | sha256 declarado no pedido | recalculado | confere |
|---|---|---|---|
| árvore do candidato (runtime) | `e50aa56606b9e62be7159ab504fbdcdf70add43ef62fccd104db87a8ec740346` | idem | **SIM** |
| árvore do candidato (fonte) | — | `36789934b7e31313b8c53241f736926f9d59baf1f5a379033d3d50495530609f` | **diverge do pedido** |
| `SKILL.md` | `fa95dfdf523c8da06822fe1be3a2b2298fb207b55a5498034039f8edabd944c5` | idem | **SIM** |
| `evals/PLACAR.md` | `993aaa51214319a1c1c8413c385d8d91f0bfdf66a61e4b6d861c8cd9f49ae7bc` | idem | **SIM** |
| `03-CRITERIA_MATRIX.yaml` da rodada 2 | `939695fb834bbf25890cb9bc96adbb02e1f3ffe0be396226bdc8328136983e2a` | idem | **SIM** |

Receita da árvore: `_compartilhado/verificacoes_pacote.py::digest_de_arvore` — 25 arquivos,
manifesto de **2649 bytes**, chave POSIX relativa, comparador ordinal, linha `sha256␣␣chave`,
terminador `\n`, UTF-8 sem BOM, conteúdo em bytes crus. Reproduzido linha a linha, não estimado.

## Envelopes emitidos nesta rodada

| arquivo | sha256 |
|---|---|
| `00-RECEBIMENTO.md` | `d84df35c01f82366887953b1d5f18593a7aff2ec2622a9cda46896411d5b918f` |
| `03-CRITERIA_MATRIX.yaml` | `a5363b28181e92610e0956fa8aff042fbe2c2634667ec7fdf2b14e3cbdc78563` |
| `04-JUDGE_OPINION-robustez-e-evidencia.md` | `206e3db661a2f36611c6b12bdacda7bc734d26a030ada3bd40f7393017b029eb` |
| `05-JUDGE_OPINION-fidelidade-e-contrato.md` | `6838c22e81ca803309321514ac54bb070267c7fd952e5a429b762800480b0718` |
| `06-JUDGE_OPINION-experiencia-e-risco.md` | `3aafef1e40bc3342228d3356656666a8aa99789c011ccd2bc2282400cea07b73` |
| `07-JUDGE_REPORT.yaml` | `526a0808f84fa61c0378aae4337dc87d2c9c5eb1d3cf4af5541d6648c7f7a5c3` |

Este arquivo não se autodigere. Para conferir:
`Get-FileHash -Algorithm SHA256 <arquivo>` — os seis acima foram medidos assim, nesta ordem.

## Veredito, em uma linha

`minimum_score: 6` (CRIT-06, ótica `robustez-e-evidencia`) → faixa `≤6` do ADR-014 → **`REPROVED`**.
**Não alcança** o `required_level: INTERNO`.
