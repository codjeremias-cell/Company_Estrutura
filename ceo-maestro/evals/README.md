# Testes do CEO Maestro

Execute:

```powershell
python evals/validate_workflow.py
```

O validador usa somente a biblioteca padrão do Python. Ele verifica:

- integridade JSON e referências internas do schema;
- causalidade de `CAPABILITY_GAP` e correlação da missão;
- contenção de `scope_touched` no escopo autorizado;
- cálculo da menor nota aplicável;
- corte exato de 9,5 sem média nem arredondamento;
- autoria, proveniência e digests;
- completude do relatório de limitação;
- gates que nenhuma exceção pode dispensar;
- autorização exclusiva, explícita, vigente e de uso único de Jeremias;
- derivação de conclusão, regras, integridade e autoridade a partir das provas;
- separação entre `VALIDATED` e `VALIDATED_BY_EXCEPTION`.

Os prompts comportamentais em `evals.json` complementam os testes determinísticos e devem ser
reexecutados quando o Diretor, Negócios ou Juízes forem migrados.
