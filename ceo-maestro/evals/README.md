# Testes do CEO Maestro

Execute:

```powershell
python evals/validate_workflow.py
```

O validador usa somente a biblioteca padrão do Python. Ele verifica:

- integridade JSON e referências internas do schema;
- causalidade de `CAPABILITY_GAP` e correlação da missão;
- contenção de `scope_touched` no escopo autorizado;
- `required_level` obrigatório e idêntico da missão ao parecer, à exceção e à decisão;
- cálculo da menor nota externa aplicável, sempre inteira e sem média ou arredondamento;
- faixas fixas do ADR-014: `10 → VALIDATED`, `7–9 → ACEITO_USO_INTERNO` e
  `0–6 → REPROVED`;
- matriz de fronteira `6 / 7 / 9 / 10` em `INTERNO` e `PRODUCAO`;
- `PRODUCAO` alcançado somente por `VALIDATED`; `INTERNO` alcançado também por
  `ACEITO_USO_INTERNO`;
- autoria, proveniência e digests;
- completude do relatório de limitação e alvo de exceção coerente com o nível: 10 para
  `PRODUCAO`, 7 para `INTERNO`;
- gates que nenhuma exceção pode dispensar;
- autorização exclusiva, explícita, vigente e de uso único de Jeremias;
- derivação de conclusão, regras, integridade e autoridade a partir das provas;
- rejeição de nível ausente ou divergente, nota decimal, falha crítica, bloqueio e
  `ACEITO_USO_INTERNO` usado como produção;
- oráculo independente das fixtures para impedir falso-verde no mapeamento de vereditos.

Os prompts comportamentais em `evals.json` complementam os testes determinísticos e devem ser
reexecutados quando o Diretor, Negócios ou Juízes forem migrados. A medição determinística
vigente em 2026-07-29 é **55/55 PASS**; o histórico permanece em `PLACAR.md`.
