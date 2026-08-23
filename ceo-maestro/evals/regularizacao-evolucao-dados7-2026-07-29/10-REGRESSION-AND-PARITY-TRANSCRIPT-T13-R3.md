# Tarefa 13 — regressão, deploy e paridade R3

Data: 2026-07-30
Exceção: `EXREQ-T13-R6-R3`
Autorização: `EXAUTH-T13-R6-R3` (`CONSUMED`)
Candidata: `cand-G`
Digest agregado: `sha256:f3f8bdd0a284c349cb77488909b14e67ace8f2912e914d89f4e17a28987c73c5`

## Promoção canônica

Os cinco arquivos autorizados foram copiados de `cand-G/evals` para o pacote
canônico de Arquitetura de Dados. A comparação SHA-256 pós-overlay fechou 5/5;
os hashes individuais e o digest agregado constam em
`09-PROMOTION-RECEIPT-T13-R3.json`.

## Regressão do pacote promovido

Comando executado:

```powershell
python -X utf8 evals/validate_workflow.py
```

Resultado final: **122/122 PASS**, zero FAIL e zero caso quebrado. As quatro
mutações obrigatórias (`ANCHOR_FABRICATED`, `CITATION_UNVERIFIED`,
`SUMMARY_TAMPERED`, `CLAIM_OMITTED`) foram rejeitadas.

## Pré-deploy integral

O deploy inicialmente bloqueou, sem copiar arquivos, porque a busca recursiva
incluía validadores preservados em dossiês históricos. A descoberta foi
restringida aos 15 pacotes gerentes canônicos, com guard que falha se qualquer
gerente perder seu `evals/validate_workflow.py`. As varreduras de links do
Diretor e de Evolução passaram a excluir somente o dossiê histórico desta
regularização. A medição byte a byte dos legados foi feita com os bytes LF do
repositório principal, conforme a limitação de EOL já registrada no projeto.
As tentativas do `robocopy` também foram limitadas a duas, com espera de um
segundo, para que um arquivo bloqueado reprove o deploy de forma visível em vez
de repetir silenciosamente por tempo indefinido.

Resultado final do pré-deploy: **16 executáveis, 0 falhas**.

## Correção referencial não material

Após a aprovação, `06-EXCEPTION-REQUEST-T13-R3.json` teve somente os campos
`judge_report_ref` e `limitation_report_ref` normalizados de caminhos de arquivo
para os IDs semânticos exigidos pelo validador do CEO. O SHA-256 mudou de
`8a6b66cad717f7cca52e11e928f65e0b835426885480fdb72ccdaa3712b3360c` para
`261ed052a1780651d51bfda6a67a2efb4eb8f99d6992bd9092d2d75150b645db`.
Escopo autorizado, digest da candidata, digest do snapshot, nota, riscos
residuais e gates inegociáveis permaneceram inalterados.

## Deploy e paridade

O script oficial `Estrutura Final de Skills/deploy-estrutura.ps1` implantou os
componentes nos runtimes Claude e Codex. A comparação final SHA-256 retornou:

- Claude: **OK — estrutura idêntica**.
- Codex: **OK — estrutura idêntica**.

Nenhum gate inegociável foi dispensado. R6 permanece visível como risco
residual aceito exclusivamente para esta promoção de uso único.
