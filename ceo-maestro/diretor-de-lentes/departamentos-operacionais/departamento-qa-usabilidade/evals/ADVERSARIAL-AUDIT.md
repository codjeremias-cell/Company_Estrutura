# Auditoria adversarial — Departamento de QA e Usabilidade

**Data:** 2026-07-26  
**Alvo:** pacote isolado anterior à promoção canônica  
**Regra:** registrar também reprovações intermediárias; sucesso simulado é
proibido.

## Resultado final

**APROVADO.** A suíte determinística terminou em **116/116 PASS**. Duas
instâncias independentes, sem editar arquivos, repetiram a suíte e atacaram o
gate composto QA→Diretor:

- auditor A: **9/9 adulterações bloqueadas**;
- auditor B: **10/10 adulterações bloqueadas**;
- nenhum bypass final reproduzível.

## Histórico das rodadas

| Rodada | Achado real | Tratamento | Estado |
|---|---|---|---|
| 1 | sete famílias frágeis: READY sem prova, política ativa frouxa, dimensões de borda incoerentes, perda de incerteza, causal/digests divergentes, julgamento em texto e FAIL sem defeito/pendência | schema e grafo endurecidos | corrigido |
| 2 | cinco contraprovas ainda passavam: `N/A` mascarado, cleanup parcial, causal divergente, julgamento no owner e FAIL ligado a outro caso | regex, enums e correlação por caso/candidato/ambiente | corrigido |
| 3 | cinco contraprovas exatas bloqueadas e regressão das sete famílias em 7/7 | reexecução independente | aprovado no escopo |
| 4 | o schema do Diretor isolado aceitava apagar `UNVERIFIED/MISSING` depois da conversão | gate composto, referência autenticada e reconciliação integral fonte→envelope | corrigido |
| 5 | reataques finais sobre incerteza, digest, causalidade, missão, candidato, evidências, pendências, dissensos e resumo | 9/9 e 10/10 bloqueados | aprovado |

## Brecha final e fechamento

O schema externo valida a forma de `DEPARTMENT_RETURN`, mas não consegue
compará-lo sozinho com `QA_CONSOLIDATED_REPORT`. A mutação abaixo passava na
validação estrutural:

```python
boundary["test_summary"]["skip"] = 0
boundary["test_summary"]["skip_reasons"] = []
boundary["pending_refs"] = []
```

O fechamento aplicado foi:

1. causalidade do retorno herdada da missão e do relatório;
2. `message_id` do relatório como causa direta do retorno;
3. referência `report_id@sha256:<digest-canônico>` em `artifact_refs`;
4. `department_bridge_errors(report, boundary, mission)` recalcula a conversão;
5. igualdade obrigatória de missão, candidato, causalidade, resumo,
   evidências, pendências e dissensos;
6. falha fechada diante de qualquer edição posterior.

O ataque original agora falha por divergência de `test_summary` e
`pending_refs`. Troca ou remoção do digest, adulteração causal e mudanças nos
demais campos reconciliados também falham.

## Limites

- A auditoria prova o contrato e suas contraprovas com fixtures, não a
  eficácia em produto real.
- Dispositivo físico, carga pesada, produção e renderização visual real
  dependem de missão autorizada.
- O schema estrutural do Diretor continua deliberadamente genérico; a
  fidelidade entre documentos é responsabilidade explícita do gate composto.
