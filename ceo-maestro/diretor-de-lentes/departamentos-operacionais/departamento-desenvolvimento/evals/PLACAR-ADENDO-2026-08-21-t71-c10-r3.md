## Adendo 2026-08-21 — T71 C10 r3 (linhagem B)

`mission_verdict` distingue const ausente (`BLOCKED_CONST_AUSENTE`) de
producer forjado (`BLOCKED_BYPASS_ATTEMPT`). Ausência de `$defs` ou de
`departmentMissionAdmission` fecha `BLOCKED_BYPASS_ATTEMPT`, nunca exceção.
`$def` com `additionalProperties` false e os 18 `required` do envelope do
Diretor. Title/description não chamam `DEPARTMENT_MISSION` de envelope interno.
`oneOf` e `mission_verdict` são a mesma autoridade.

Tabela Resultado vigente: sem 105/105, sem Juízes/Auditoria pendentes.
CRIT-06 em seção própria, inconfundível do catálogo estrutural de 16 casos.
FAIL ambiental T87/T88 leva o rótulo `ENV-T87/T88` no stdout.
Receita de rollback em `evals/ROLLBACK.md` com hash de origem.
Sem `FORWARD-TEST.md`.
