## Adendo 2026-08-16 — T71 C10 entrada (cand-B)

O selo de 2026-08-08 (116/116) é registro daquela data. Esta overlay acrescenta
o `$defs/departmentMissionAdmission` e sete casos: o literal no validador, o
`find_const` do producer de entrada, três chamadas de `mission_verdict` que
leem o const do schema, e dois casos de schema (rejeita producer forjado /
aceita o do Diretor).

O caso de saída (`plano com produtor forjado` no `DEV_PLAN`) permanece. CRIT-06
não entra neste adendo.
